"""
Training Hook for Quantum-LLM Bridge Integration
Monkey-patches existing training scripts to add quantum enhancement.
"""
import sys
from pathlib import Path
from typing import Optional

import torch

# Add quantum-ai to path
quantum_ai_path = Path(__file__).resolve().parents[2] / "quantum-ai"
if str(quantum_ai_path) not in sys.path:
    sys.path.insert(0, str(quantum_ai_path))

from src.quantum_llm_bridge import (
    create_default_bridge,
    QuantumTrainingCallback,
    QuantumTokenEnhancer,
)


class QuantumTrainingHook:
    """
    Global hook for quantum-enhanced training.
    Can be injected into any training script.
    """
    
    _instance: Optional["QuantumTrainingHook"] = None
    
    def __init__(
        self,
        n_training_qubits: int = 4,
        n_token_qubits: int = 4,
        n_layers: int = 4,
        entanglement_pattern: str = "full",
        enhancement_strength: float = 0.1,
        enable: bool = True,
    ):
        self.enable = enable
        if not enable:
            self.quantum_bridge = None
            self.quantum_callback = None
            self.quantum_enhancer = None
            return
        
        # Create bridge
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.quantum_bridge = create_default_bridge(
            n_training_qubits=n_training_qubits,
            n_token_qubits=n_token_qubits,
            device=device,
        )
        
        # Override circuit parameters
        self.quantum_bridge.n_layers = n_layers
        self.quantum_bridge.entanglement_pattern = entanglement_pattern
        
        # Create callback and enhancer
        self.quantum_callback = QuantumTrainingCallback(
            self.quantum_bridge,
            enable_logging=True,
        )
        
        self.quantum_enhancer = QuantumTokenEnhancer(
            self.quantum_bridge,
            enhancement_strength=enhancement_strength,
            enable_logging=False,
        )
        
        print("[QuantumHook] ✓ Quantum-LLM bridge initialized")
        print(f"  Training qubits: {n_training_qubits}")
        print(f"  Token qubits: {n_token_qubits}")
        print(f"  Layers: {n_layers}")
        print(f"  Entanglement: {entanglement_pattern}")
    
    @classmethod
    def get_instance(cls) -> "QuantumTrainingHook":
        """Get global instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def initialize(
        cls,
        n_training_qubits: int = 4,
        n_token_qubits: int = 4,
        enable: bool = True,
        **kwargs
    ) -> "QuantumTrainingHook":
        """Initialize global instance with config."""
        cls._instance = cls(
            n_training_qubits=n_training_qubits,
            n_token_qubits=n_token_qubits,
            enable=enable,
            **kwargs
        )
        return cls._instance
    
    def on_training_step(
        self,
        loss: float,
        step: int,
        epoch: int = 0,
        grad_norm: float = 0.0,
        learning_rate: float = 5e-5,
        **kwargs
    ) -> Optional[torch.Tensor]:
        """
        Call this at each training step to feed state to quantum circuit.
        
        Args:
            loss: Current step loss
            step: Global step number
            epoch: Current epoch
            grad_norm: Gradient norm
            learning_rate: Current learning rate
            
        Returns:
            Quantum adjustment tensor or None if disabled
        """
        if not self.enable or self.quantum_callback is None:
            return None
        
        return self.quantum_callback.on_step_end(
            loss=loss,
            grad_norm=grad_norm,
            learning_rate=learning_rate,
            epoch=epoch,
            step=step,
            **kwargs
        )
    
    def enhance_generation_logits(
        self,
        logits: torch.Tensor,
        training_state: Optional[dict] = None,
    ) -> torch.Tensor:
        """
        Enhance logits with quantum circuit.
        
        Args:
            logits: Raw logits [batch, vocab_size]
            training_state: Optional training state dict
            
        Returns:
            Enhanced logits
        """
        if not self.enable or self.quantum_enhancer is None:
            return logits
        
        return self.quantum_enhancer.enhance_logits(logits, training_state)
    
    def save_history(self, output_path: Path) -> None:
        """Save quantum training history."""
        if self.enable and self.quantum_callback:
            self.quantum_callback.save_history(output_path)


# Global initialization function
def init_quantum_training(
    enabled: bool = True,
    n_training_qubits: int = 4,
    n_token_qubits: int = 4,
    n_layers: int = 4,
    entanglement_pattern: str = "full",
    enhancement_strength: float = 0.1,
) -> QuantumTrainingHook:
    """
    Initialize quantum training globally.
    Call this at the start of any training script.
    
    Args:
        enabled: Whether to enable quantum enhancement
        n_training_qubits: Number of qubits for training state
        n_token_qubits: Number of qubits for token generation
        n_layers: Quantum circuit depth
        entanglement_pattern: Entanglement strategy
        enhancement_strength: How much quantum affects generation
        
    Returns:
        QuantumTrainingHook instance
    """
    return QuantumTrainingHook.initialize(
        enable=enabled,
        n_training_qubits=n_training_qubits,
        n_token_qubits=n_token_qubits,
        n_layers=n_layers,
        entanglement_pattern=entanglement_pattern,
        enhancement_strength=enhancement_strength,
    )


# Convenience function for training loops
def quantum_training_step(
    loss: float,
    step: int,
    **kwargs
) -> Optional[torch.Tensor]:
    """
    Convenience function to call from training loop.
    
    Example:
        from quantum_ai.quantum_training_hook import quantum_training_step
        
        for step, batch in enumerate(dataloader):
            outputs = model(**batch)
            loss = outputs.loss
            
            # Feed to quantum circuit
            quantum_adj = quantum_training_step(loss=loss.item(), step=step)
            
            # Optionally use adjustment (e.g., modulate learning rate)
            if quantum_adj is not None:
                loss = loss * (1 + quantum_adj * 0.1)
    """
    hook = QuantumTrainingHook.get_instance()
    return hook.on_training_step(loss=loss, step=step, **kwargs)


# Convenience function for generation
def quantum_enhance_logits(
    logits: torch.Tensor,
    training_state: Optional[dict] = None,
) -> torch.Tensor:
    """
    Convenience function to enhance logits during generation.
    
    Example:
        from quantum_ai.quantum_training_hook import quantum_enhance_logits
        
        outputs = model(input_ids)
        logits = outputs.logits[:, -1, :]
        
        # Apply quantum enhancement
        enhanced_logits = quantum_enhance_logits(logits)
        
        # Sample
        probs = torch.softmax(enhanced_logits / temperature, dim=-1)
        next_token = torch.multinomial(probs, num_samples=1)
    """
    hook = QuantumTrainingHook.get_instance()
    return hook.enhance_generation_logits(logits, training_state)


if __name__ == "__main__":
    # Demo
    print("=" * 70)
    print("Quantum Training Hook Demo")
    print("=" * 70)
    
    # Initialize
    hook = init_quantum_training(
        enabled=True,
        n_training_qubits=4,
        n_token_qubits=4,
    )
    
    # Simulate training
    print("\nSimulating training steps...")
    for step in range(10):
        loss = 2.5 - step * 0.1
        adj = hook.on_training_step(
            loss=loss,
            step=step,
            epoch=0,
            grad_norm=1.0,
        )
        if step % 2 == 0:
            print(f"  Step {step}: loss={loss:.2f}, quantum_adj={adj.item():.6f}")
    
    # Simulate generation
    print("\nSimulating generation...")
    mock_logits = torch.randn(1, 1000)
    enhanced = hook.enhance_generation_logits(mock_logits)
    print(f"  Original mean: {mock_logits.mean():.6f}")
    print(f"  Enhanced mean: {enhanced.mean():.6f}")
    print(f"  Change: {(enhanced - mock_logits).abs().mean():.6f}")
    
    print("\n" + "=" * 70)
    print("Demo complete!")
    print("=" * 70)
