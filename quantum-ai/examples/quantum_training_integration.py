"""
Example: Quantum-Enhanced LLM Training
Demonstrates how to integrate QuantumLLMBridge with Hugging Face training.
"""
import sys
from pathlib import Path

# Add quantum-ai to path
quantum_ai_path = Path(__file__).resolve().parents[2]
if str(quantum_ai_path) not in sys.path:
    sys.path.insert(0, str(quantum_ai_path))

import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    Trainer,
    TrainingArguments,
    TrainerCallback,
)
from datasets import load_dataset
from src.quantum_llm_bridge import (
    create_default_bridge,
    QuantumTrainingCallback,
    QuantumTokenEnhancer,
)


class HFQuantumCallback(TrainerCallback):
    """
    Hugging Face Trainer callback that integrates quantum bridge.
    """
    
    def __init__(self, quantum_callback: QuantumTrainingCallback):
        self.quantum_callback = quantum_callback
    
    def on_step_end(self, args, state, control, **kwargs):
        """Called at end of each training step."""
        if state.global_step > 0:
            # Get training metrics
            loss = kwargs.get('loss', 0.0)
            
            # Compute gradient norm from model
            grad_norm = 0.0
            model = kwargs.get('model')
            if model is not None:
                total_norm = 0.0
                for p in model.parameters():
                    if p.grad is not None:
                        param_norm = p.grad.data.norm(2)
                        total_norm += param_norm.item() ** 2
                grad_norm = total_norm ** 0.5
            
            # Feed to quantum circuit
            self.quantum_callback.on_step_end(
                loss=loss,
                grad_norm=grad_norm,
                learning_rate=state.learning_rate if hasattr(state, 'learning_rate') else 5e-5,
                epoch=state.epoch,
                step=state.global_step,
            )


def quantum_enhanced_generation(
    model,
    tokenizer,
    quantum_enhancer: QuantumTokenEnhancer,
    prompt: str,
    max_length: int = 100,
    temperature: float = 0.7,
) -> str:
    """
    Generate text with quantum-enhanced logits.
    
    Args:
        model: HuggingFace model
        tokenizer: HuggingFace tokenizer
        quantum_enhancer: QuantumTokenEnhancer instance
        prompt: Input prompt
        max_length: Max tokens to generate
        temperature: Sampling temperature
        
    Returns:
        Generated text
    """
    quantum_enhancer.reset()
    
    inputs = tokenizer(prompt, return_tensors="pt")
    input_ids = inputs['input_ids'].to(model.device)
    
    generated = input_ids
    
    for _ in range(max_length):
        with torch.no_grad():
            outputs = model(generated)
            logits = outputs.logits[:, -1, :]  # Get last token logits
            
            # Apply quantum enhancement
            enhanced_logits = quantum_enhancer.enhance_logits(logits)
            
            # Sample with temperature
            probs = torch.softmax(enhanced_logits / temperature, dim=-1)
            next_token = torch.multinomial(probs, num_samples=1)
            
            generated = torch.cat([generated, next_token], dim=1)
            
            # Check for EOS
            if next_token.item() == tokenizer.eos_token_id:
                break
    
    return tokenizer.decode(generated[0], skip_special_tokens=True)


def main():
    print("=" * 70)
    print("Quantum-Enhanced LLM Training Example")
    print("=" * 70)
    
    # Configuration
    model_name = "microsoft/phi-2"  # Small model for demo
    dataset_name = "wikitext"
    dataset_config = "wikitext-2-raw-v1"
    output_dir = Path("data_out/quantum_training_demo")
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\nUsing device: {device}")
    
    # Step 1: Create quantum bridge
    print("\n[1/5] Creating quantum bridge...")
    quantum_bridge = create_default_bridge(
        n_training_qubits=4,
        n_token_qubits=4,
        device=device
    )
    print("✓ Quantum bridge created")
    info = quantum_bridge.get_quantum_state_info()
    print(f"  - Training qubits: {info['training_qubits']}")
    print(f"  - Token qubits: {info['token_qubits']}")
    print(f"  - Entanglement: {info['entanglement_pattern']}")
    print(f"  - Total parameters: {info['parameters']}")
    
    # Step 2: Load model and tokenizer
    print("\n[2/5] Loading model and tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16 if device.type == "cuda" else torch.float32,
        trust_remote_code=True,
    ).to(device)
    print(f"✓ Loaded {model_name}")
    
    # Step 3: Load dataset
    print("\n[3/5] Loading dataset...")
    dataset = load_dataset(dataset_name, dataset_config)
    
    def tokenize_function(examples):
        return tokenizer(
            examples["text"],
            truncation=True,
            max_length=256,
            padding="max_length",
        )
    
    tokenized_dataset = dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=dataset["train"].column_names,
    )
    
    # Use small subset for demo
    train_dataset = tokenized_dataset["train"].select(range(100))
    eval_dataset = tokenized_dataset["validation"].select(range(20))
    print(f"✓ Loaded {len(train_dataset)} train, {len(eval_dataset)} eval samples")
    
    # Step 4: Setup quantum callbacks
    print("\n[4/5] Setting up quantum training callbacks...")
    quantum_train_callback = QuantumTrainingCallback(
        quantum_bridge,
        enable_logging=True
    )
    hf_quantum_callback = HFQuantumCallback(quantum_train_callback)
    print("✓ Quantum callbacks configured")
    
    # Step 5: Train with quantum enhancement
    print("\n[5/5] Starting quantum-enhanced training...")
    training_args = TrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=1,
        per_device_train_batch_size=2,
        per_device_eval_batch_size=2,
        learning_rate=5e-5,
        warmup_steps=10,
        logging_steps=5,
        eval_strategy="steps",
        eval_steps=20,
        save_steps=50,
        save_total_limit=1,
        report_to="none",
        remove_unused_columns=False,
    )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        callbacks=[hf_quantum_callback],  # Add quantum callback!
    )
    
    print("\nTraining...")
    trainer.train()
    print("✓ Training complete")
    
    # Save quantum history
    history_path = output_dir / "quantum_history.json"
    quantum_train_callback.save_history(history_path)
    print(f"✓ Quantum history saved to {history_path}")
    
    # Demo: Quantum-enhanced generation
    print("\n" + "=" * 70)
    print("Quantum-Enhanced Generation Demo")
    print("=" * 70)
    
    quantum_enhancer = QuantumTokenEnhancer(
        quantum_bridge,
        enhancement_strength=0.1,
        enable_logging=True
    )
    
    prompts = [
        "The future of artificial intelligence",
        "Quantum computing will",
        "Machine learning algorithms",
    ]
    
    for prompt in prompts:
        print(f"\nPrompt: {prompt}")
        print("-" * 70)
        
        # Standard generation
        inputs = tokenizer(prompt, return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=30,
                temperature=0.7,
                do_sample=True,
            )
        standard_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"Standard: {standard_text}")
        
        # Quantum-enhanced generation
        quantum_text = quantum_enhanced_generation(
            model,
            tokenizer,
            quantum_enhancer,
            prompt,
            max_length=30,
            temperature=0.7,
        )
        print(f"Quantum:  {quantum_text}")
    
    print("\n" + "=" * 70)
    print("Example complete!")
    print("=" * 70)
    print(f"\nOutputs saved to: {output_dir}")
    print(f"Quantum history: {history_path}")


if __name__ == "__main__":
    main()
