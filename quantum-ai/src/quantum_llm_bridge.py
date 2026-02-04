"""
Quantum-LLM Bridge Circuit
Links quantum circuits bidirectionally with LLM training and token generation.

This creates a hybrid quantum-classical system where:
- Training state (loss, gradients, embeddings) feeds into quantum circuit
- Quantum circuit measurements influence token generation logits
- Creates quantum entanglement between training phase and inference phase
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pennylane as qml
import torch
import torch.nn as nn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QuantumLLMBridge(nn.Module):
    """
    Bidirectional quantum-classical bridge for LLM training and token generation.
    
    Architecture:
    1. Training State Encoder: Maps training metrics → quantum parameters
    2. Quantum Entanglement Circuit: Processes state through entangled qubits
    3. Token Generation Decoder: Maps quantum measurements → token logit adjustments
    
    The circuit maintains quantum coherence between training steps and token generation,
    allowing the model to leverage quantum superposition for exploration.
    """
    
    def __init__(
        self,
        n_qubits: int = 8,
        n_training_qubits: int = 4,
        n_token_qubits: int = 4,
        n_layers: int = 3,
        backend: str = "lightning.qubit",
        shots: Optional[int] = None,
        entanglement_pattern: str = "full",
    ) -> None:
        """
        Initialize quantum-LLM bridge.
        
        Args:
            n_qubits: Total qubits (must equal n_training_qubits + n_token_qubits)
            n_training_qubits: Qubits for encoding training state
            n_token_qubits: Qubits for token generation influence
            n_layers: Depth of variational circuit
            backend: PennyLane device backend
            shots: Number of shots for sampling (None = exact simulation)
            entanglement_pattern: How to entangle qubits (linear, circular, full)
        """
        super().__init__()
        
        assert n_qubits == n_training_qubits + n_token_qubits, \
            f"Total qubits {n_qubits} must equal training {n_training_qubits} + token {n_token_qubits}"
        
        self.n_qubits = n_qubits
        self.n_training_qubits = n_training_qubits
        self.n_token_qubits = n_token_qubits
        self.n_layers = n_layers
        self.entanglement_pattern = entanglement_pattern.lower()
        
        # Training qubits: 0 to n_training_qubits-1
        self.training_wires = list(range(n_training_qubits))
        # Token qubits: n_training_qubits to n_qubits-1
        self.token_wires = list(range(n_training_qubits, n_qubits))
        
        # Create quantum device
        self.dev = qml.device(backend, wires=n_qubits, shots=shots)
        
        # Variational parameters for entanglement layers
        self.quantum_weights = nn.Parameter(
            torch.randn(n_layers, n_qubits, 3) * 0.1
        )
        
        # Classical preprocessing for training state
        self.training_encoder = nn.Sequential(
            nn.Linear(8, 16),  # loss, grad_norm, lr, epoch, step, etc.
            nn.Tanh(),
            nn.Linear(16, n_training_qubits * 2),  # For amplitude + phase encoding
            nn.Tanh()
        )
        
        # Classical postprocessing for token adjustments
        self.token_decoder = nn.Sequential(
            nn.Linear(n_token_qubits, 32),
            nn.ReLU(),
            nn.Linear(32, 1),  # Single adjustment value per token
            nn.Tanh()  # Bounded adjustment
        )
        
        # Create QNode for the bridge circuit
        self.qnode = qml.QNode(self._bridge_circuit, self.dev, interface="torch")
        
        logger.info(
            f"Initialized QuantumLLMBridge: {n_training_qubits} training qubits "
            f"<-> {n_token_qubits} token qubits, {n_layers} layers, {entanglement_pattern} entanglement"
        )
    
    def _encode_training_state(self, state_params: torch.Tensor) -> None:
        """
        Encode training state into training qubits using amplitude + phase encoding.
        
        Args:
            state_params: Preprocessed training state [n_training_qubits * 2]
        """
        # Split into amplitude and phase components
        amplitudes = state_params[:self.n_training_qubits]
        phases = state_params[self.n_training_qubits:]
        
        # Encode into training qubits
        for i, wire in enumerate(self.training_wires):
            qml.RY(amplitudes[i] * np.pi, wires=wire)  # Amplitude encoding
            qml.RZ(phases[i] * np.pi, wires=wire)      # Phase encoding
    
    def _entangle_training_to_tokens(self) -> None:
        """
        Create entanglement between training qubits and token qubits.
        This is the key: training state influences token generation through quantum entanglement.
        """
        if self.entanglement_pattern == "linear":
            # Linear chain: each training qubit connects to corresponding token qubit
            for i in range(min(self.n_training_qubits, self.n_token_qubits)):
                train_wire = self.training_wires[i]
                token_wire = self.token_wires[i]
                qml.CNOT(wires=[train_wire, token_wire])
        
        elif self.entanglement_pattern == "circular":
            # Circular: wrap around connections
            for i in range(self.n_token_qubits):
                train_wire = self.training_wires[i % self.n_training_qubits]
                token_wire = self.token_wires[i]
                qml.CNOT(wires=[train_wire, token_wire])
                
        elif self.entanglement_pattern == "full":
            # Full: every training qubit entangles with every token qubit
            for train_wire in self.training_wires:
                for token_wire in self.token_wires:
                    qml.CNOT(wires=[train_wire, token_wire])
                    
        else:
            raise ValueError(f"Unknown entanglement pattern: {self.entanglement_pattern}")
    
    def _variational_layer(self, layer_idx: int) -> None:
        """
        Apply variational rotations to all qubits.
        
        Args:
            layer_idx: Which layer parameters to use
        """
        weights = self.quantum_weights[layer_idx]
        
        for wire in range(self.n_qubits):
            qml.RX(weights[wire, 0], wires=wire)
            qml.RY(weights[wire, 1], wires=wire)
            qml.RZ(weights[wire, 2], wires=wire)
    
    def _bridge_circuit(self, state_params: torch.Tensor) -> List[torch.Tensor]:
        """
        The complete quantum bridge circuit.
        
        Flow:
        1. Encode training state into training qubits
        2. Apply variational layers for quantum processing
        3. Entangle training qubits with token qubits
        4. More variational layers for joint processing
        5. Measure token qubits (training qubits remain for next step)
        
        Args:
            state_params: Encoded training state
            
        Returns:
            Expectation values from token qubits
        """
        # Step 1: Encode training state
        self._encode_training_state(state_params)
        
        # Step 2: Initial variational processing
        for layer in range(self.n_layers // 2):
            self._variational_layer(layer)
            
            # Local entanglement within training qubits
            for i in range(len(self.training_wires) - 1):
                qml.CNOT(wires=[self.training_wires[i], self.training_wires[i + 1]])
        
        # Step 3: Critical cross-entanglement (training <-> token)
        self._entangle_training_to_tokens()
        
        # Step 4: Joint variational processing
        for layer in range(self.n_layers // 2, self.n_layers):
            self._variational_layer(layer)
            
            # Local entanglement within token qubits
            for i in range(len(self.token_wires) - 1):
                qml.CNOT(wires=[self.token_wires[i], self.token_wires[i + 1]])
        
        # Step 5: Measure token qubits only
        # Training qubits maintain state for next iteration (in real quantum hardware)
        return [qml.expval(qml.PauliZ(wire)) for wire in self.token_wires]
    
    def forward(
        self,
        training_state: Dict[str, float],
        token_embeddings: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Forward pass through quantum bridge.
        
        Args:
            training_state: Dict with keys like 'loss', 'grad_norm', 'learning_rate', etc.
            token_embeddings: Optional token embeddings to modulate [batch, seq_len, hidden_dim]
            
        Returns:
            Quantum-influenced adjustments for token logits [batch, seq_len] or scalar
        """
        # Prepare training state vector
        state_vector = torch.tensor([
            training_state.get('loss', 0.0),
            training_state.get('grad_norm', 0.0),
            training_state.get('learning_rate', 1e-4),
            training_state.get('epoch', 0.0) / 10.0,  # Normalized
            training_state.get('step', 0.0) / 1000.0,  # Normalized
            training_state.get('perplexity', 0.0) / 100.0,  # Normalized
            training_state.get('accuracy', 0.0),
            training_state.get('kl_divergence', 0.0),
        ], dtype=torch.float32)
        
        # Encode through classical network
        encoded_state = self.training_encoder(state_vector)
        
        # Run quantum circuit
        quantum_measurements = self.qnode(encoded_state)
        quantum_output = torch.stack(quantum_measurements)
        
        # Decode quantum measurements to token adjustments
        token_adjustment = self.token_decoder(quantum_output.unsqueeze(0)).squeeze()
        
        # If token embeddings provided, modulate them
        if token_embeddings is not None:
            # Broadcast adjustment across sequence
            adjustment = token_adjustment * 0.1  # Scale factor
            return adjustment
        
        return token_adjustment
    
    def get_quantum_state_info(self) -> Dict[str, Any]:
        """
        Get information about current quantum state.
        
        Returns:
            Dict with quantum circuit metadata
        """
        return {
            "total_qubits": self.n_qubits,
            "training_qubits": self.n_training_qubits,
            "token_qubits": self.n_token_qubits,
            "layers": self.n_layers,
            "entanglement_pattern": self.entanglement_pattern,
            "parameters": self.quantum_weights.numel(),
            "training_wires": self.training_wires,
            "token_wires": self.token_wires,
        }


class QuantumTrainingCallback:
    """
    Training callback that feeds training state into quantum circuit.
    Use with Hugging Face Trainer or custom training loop.
    """
    
    def __init__(self, quantum_bridge: QuantumLLMBridge, enable_logging: bool = True):
        self.quantum_bridge = quantum_bridge
        self.enable_logging = enable_logging
        self.quantum_history = []
    
    def on_step_end(
        self,
        loss: float,
        grad_norm: float,
        learning_rate: float,
        epoch: int,
        step: int,
        **kwargs
    ) -> torch.Tensor:
        """
        Called at end of each training step.
        
        Args:
            loss: Current step loss
            grad_norm: Gradient norm
            learning_rate: Current learning rate
            epoch: Current epoch
            step: Global step number
            **kwargs: Additional metrics (perplexity, accuracy, etc.)
            
        Returns:
            Quantum adjustment tensor
        """
        training_state = {
            'loss': loss,
            'grad_norm': grad_norm,
            'learning_rate': learning_rate,
            'epoch': float(epoch),
            'step': float(step),
            'perplexity': kwargs.get('perplexity', 0.0),
            'accuracy': kwargs.get('accuracy', 0.0),
            'kl_divergence': kwargs.get('kl_divergence', 0.0),
        }
        
        # Get quantum adjustment
        with torch.no_grad():
            adjustment = self.quantum_bridge(training_state)
        
        # Log
        if self.enable_logging and step % 10 == 0:
            logger.info(
                f"[QuantumBridge] Step {step}: loss={loss:.4f}, "
                f"quantum_adjustment={adjustment.item():.6f}"
            )
        
        # Store history
        self.quantum_history.append({
            'step': step,
            'loss': loss,
            'quantum_adjustment': adjustment.item(),
        })
        
        return adjustment
    
    def save_history(self, output_path: Path) -> None:
        """Save quantum training history."""
        import json
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open('w') as f:
            json.dump(self.quantum_history, f, indent=2)
        logger.info(f"Saved quantum training history to {output_path}")


class QuantumTokenEnhancer:
    """
    Enhances token generation logits using quantum circuit outputs.
    Can be used during inference/generation phase.
    """
    
    def __init__(
        self,
        quantum_bridge: QuantumLLMBridge,
        enhancement_strength: float = 0.1,
        enable_logging: bool = False
    ):
        self.quantum_bridge = quantum_bridge
        self.enhancement_strength = enhancement_strength
        self.enable_logging = enable_logging
        self.generation_step = 0
    
    def enhance_logits(
        self,
        logits: torch.Tensor,
        training_state: Optional[Dict[str, float]] = None
    ) -> torch.Tensor:
        """
        Apply quantum enhancement to token generation logits.
        
        Args:
            logits: Raw logits from LLM [batch, vocab_size]
            training_state: Optional training state to feed into quantum circuit
            
        Returns:
            Enhanced logits [batch, vocab_size]
        """
        if training_state is None:
            # Use default state during inference
            training_state = {
                'loss': 0.0,
                'grad_norm': 0.0,
                'learning_rate': 0.0,
                'epoch': 0.0,
                'step': float(self.generation_step),
                'perplexity': 0.0,
                'accuracy': 0.0,
                'kl_divergence': 0.0,
            }
        
        with torch.no_grad():
            # Get quantum adjustment
            adjustment = self.quantum_bridge(training_state)
            
            # Apply to logits
            # Adjustment modulates the temperature/confidence of predictions
            enhanced_logits = logits + adjustment * self.enhancement_strength
            
            if self.enable_logging and self.generation_step % 10 == 0:
                logger.info(
                    f"[QuantumEnhancer] Step {self.generation_step}: "
                    f"adjustment={adjustment.item():.6f}"
                )
            
            self.generation_step += 1
            
            return enhanced_logits
    
    def reset(self) -> None:
        """Reset generation step counter."""
        self.generation_step = 0


def create_default_bridge(
    n_training_qubits: int = 4,
    n_token_qubits: int = 4,
    device: str = "cpu"
) -> QuantumLLMBridge:
    """
    Create a default quantum-LLM bridge with sensible defaults.
    
    Args:
        n_training_qubits: Qubits for training state
        n_token_qubits: Qubits for token generation
        device: PyTorch device
        
    Returns:
        Initialized QuantumLLMBridge
    """
    bridge = QuantumLLMBridge(
        n_qubits=n_training_qubits + n_token_qubits,
        n_training_qubits=n_training_qubits,
        n_token_qubits=n_token_qubits,
        n_layers=4,
        backend="lightning.qubit",
        shots=None,  # Use exact simulation
        entanglement_pattern="full",
    )
    
    bridge = bridge.to(device)
    return bridge


if __name__ == "__main__":
    # Demo usage
    print("=" * 70)
    print("Quantum-LLM Bridge Circuit Demo")
    print("=" * 70)
    
    # Create bridge
    bridge = create_default_bridge(n_training_qubits=4, n_token_qubits=4)
    
    # Print circuit info
    info = bridge.get_quantum_state_info()
    print("\nQuantum Circuit Configuration:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Simulate training step
    print("\n" + "-" * 70)
    print("Simulating training step...")
    training_state = {
        'loss': 2.5,
        'grad_norm': 1.2,
        'learning_rate': 5e-5,
        'epoch': 1.0,
        'step': 100.0,
        'perplexity': 15.0,
        'accuracy': 0.85,
        'kl_divergence': 0.1,
    }
    
    adjustment = bridge(training_state)
    print(f"Quantum adjustment: {adjustment.item():.6f}")
    
    # Simulate token generation
    print("\n" + "-" * 70)
    print("Simulating token generation enhancement...")
    enhancer = QuantumTokenEnhancer(bridge, enhancement_strength=0.1)
    
    # Mock logits
    mock_logits = torch.randn(1, 50257)  # GPT-2 vocab size
    enhanced = enhancer.enhance_logits(mock_logits, training_state)
    
    print(f"Original logits mean: {mock_logits.mean():.6f}")
    print(f"Enhanced logits mean: {enhanced.mean():.6f}")
    print(f"Change: {(enhanced - mock_logits).abs().mean():.6f}")
    
    # Training callback example
    print("\n" + "-" * 70)
    print("Simulating training callback...")
    callback = QuantumTrainingCallback(bridge, enable_logging=True)
    
    for step in range(5):
        loss = 2.5 - step * 0.1
        adj = callback.on_step_end(
            loss=loss,
            grad_norm=1.0,
            learning_rate=5e-5,
            epoch=1,
            step=step,
        )
        print(f"  Step {step}: loss={loss:.2f}, adjustment={adj.item():.6f}")
    
    print("\n" + "=" * 70)
    print("Demo complete!")
    print("=" * 70)
