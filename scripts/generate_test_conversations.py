"""Generate test conversations for self-learning system"""

import json
from datetime import datetime
from pathlib import Path

# Create logs directory
logs_dir = Path(__file__).resolve().parents[1] / "talk-to-ai" / "logs"
logs_dir.mkdir(parents=True, exist_ok=True)

# Test conversation pairs
conversations = [
    ("What is quantum computing?", "Quantum computing is a type of computation that harnesses quantum mechanical phenomena like superposition and entanglement to process information in ways that classical computers cannot."),
    ("Explain machine learning", "Machine learning is a branch of artificial intelligence where systems learn from data to improve their performance on tasks without being explicitly programmed."),
    ("How do neural networks work?", "Neural networks are computing systems inspired by biological neural networks. They consist of interconnected nodes (neurons) organized in layers that process and transform input data to produce outputs."),
    ("What is reinforcement learning?", "Reinforcement learning is a machine learning paradigm where an agent learns to make decisions by interacting with an environment and receiving rewards or penalties for its actions."),
    ("Tell me about transformers", "Transformers are a neural network architecture that uses self-attention mechanisms to process sequential data. They're the foundation of modern language models like GPT and BERT."),
    ("What is deep learning?", "Deep learning is a subset of machine learning that uses neural networks with multiple layers (deep neural networks) to learn hierarchical representations of data."),
    ("Explain gradient descent", "Gradient descent is an optimization algorithm used to minimize a loss function by iteratively moving in the direction of steepest decrease, determined by the negative gradient."),
    ("What are LSTMs?", "LSTMs (Long Short-Term Memory networks) are a type of recurrent neural network designed to learn long-term dependencies by using gates to control information flow."),
    ("What is overfitting?", "Overfitting occurs when a model learns the training data too well, including noise and outliers, resulting in poor generalization to new data."),
    ("Explain backpropagation", "Backpropagation is an algorithm for training neural networks that computes gradients of the loss function with respect to network parameters by applying the chain rule backwards through the network."),
]

# Generate log files
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = logs_dir / f"chat_{timestamp}_training_data.jsonl"

print(f"Generating {len(conversations)} conversation pairs...")
print(f"Output: {log_file}")

with open(log_file, "w", encoding="utf-8") as f:
    for user_msg, assistant_msg in conversations:
        # Write user message
        f.write(json.dumps({
            "role": "user",
            "content": user_msg,
            "timestamp": datetime.now().isoformat(),
            "provider": "lmstudio",
            "model": "local-model"
        }) + "\n")
        
        # Write assistant response
        f.write(json.dumps({
            "role": "assistant",
            "content": assistant_msg,
            "timestamp": datetime.now().isoformat(),
            "provider": "lmstudio",
            "model": "local-model"
        }) + "\n")

print(f"\n✅ Generated {len(conversations)} conversation pairs")
print(f"📁 Saved to: {log_file}")
print("\nNow run the self-learning system to train on these conversations:")
print("  python .\\scripts\\self_learning_chat.py --min-conversations 5")
