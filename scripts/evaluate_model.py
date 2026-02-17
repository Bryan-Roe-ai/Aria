"""
Model Evaluation Script

This is a wrapper/convenience script that delegates to evaluate_lora_model.py
for actual model evaluation. It provides a simplified interface while maintaining
backward compatibility.

For LoRA models, use evaluate_lora_model.py directly for full functionality.
"""
import sys
from pathlib import Path

# Import the real evaluation logic from evaluate_lora_model
sys.path.insert(0, str(Path(__file__).parent))

try:
    from evaluate_lora_model import main as lora_main
    
    def main():
        """Delegate to evaluate_lora_model for actual implementation."""
        print("Note: Delegating to evaluate_lora_model.py for evaluation")
        print("For full control, use evaluate_lora_model.py directly\n")
        lora_main()
    
except ImportError:
    # Fallback if evaluate_lora_model is not available
    import argparse
    import json
    
    def evaluate(model_path, dataset_path, metrics):
        """Placeholder evaluation logic."""
        print(f"Warning: Using stub evaluation. Install transformers for real evaluation.")
        results = {m: 0.0 for m in metrics}
        results['note'] = 'Stub evaluation - install dependencies for real metrics'
        return results
    
    def main():
        ap = argparse.ArgumentParser(description="Evaluate a trained model.")
        ap.add_argument("--model", required=True, help="Path to trained model")
        ap.add_argument("--dataset", required=True, help="Path to evaluation dataset")
        ap.add_argument("--metrics", nargs="+", default=["accuracy"], help="Metrics to compute")
        ap.add_argument("--output", help="Path to write results JSON")
        args = ap.parse_args()

        results = evaluate(args.model, args.dataset, args.metrics)
        print(json.dumps(results, indent=2))
        if args.output:
            Path(args.output).write_text(json.dumps(results, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
