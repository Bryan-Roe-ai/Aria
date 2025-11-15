"""
Automatic Evaluation Framework for Fine-tuned Models
Supports multiple evaluation metrics and automated benchmarking
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import numpy as np
from dataclasses import dataclass, asdict
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import load_dataset
import yaml


@dataclass
class EvaluationMetrics:
    """Container for evaluation metrics"""
    perplexity: float
    accuracy: Optional[float] = None
    bleu_score: Optional[float] = None
    rouge_scores: Optional[Dict[str, float]] = None
    inference_time_ms: float = 0.0
    tokens_per_second: float = 0.0
    memory_usage_mb: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AutomaticEvaluator:
    """Automatic evaluation system for fine-tuned models"""
    
    def __init__(self, config_path: str = "lora/lora.yaml"):
        """Initialize evaluator with config"""
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.results_dir = Path("data_out/evaluation_results")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
    def _load_config(self) -> Dict[str, Any]:
        """Load evaluation config"""
        with open(self.config_path) as f:
            return yaml.safe_load(f)
    
    def evaluate_model(
        self,
        model_path: str,
        test_dataset: str,
        metrics: List[str] = ["perplexity", "inference_time"],
        num_samples: int = 100
    ) -> EvaluationMetrics:
        """
        Evaluate model on test dataset
        
        Args:
            model_path: Path to fine-tuned model
            test_dataset: Path or name of test dataset
            metrics: List of metrics to compute
            num_samples: Number of samples to evaluate
            
        Returns:
            EvaluationMetrics object with results
        """
        print(f"Loading model from {model_path}...")
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            device_map="auto" if self.device == "cuda" else None
        )
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        
        print(f"Loading test dataset: {test_dataset}...")
        dataset = self._load_test_data(test_dataset, num_samples)
        
        results = {
            "perplexity": 0.0,
            "inference_time_ms": 0.0,
            "tokens_per_second": 0.0,
            "memory_usage_mb": 0.0
        }
        
        # Compute perplexity
        if "perplexity" in metrics:
            results["perplexity"] = self._compute_perplexity(model, tokenizer, dataset)
        
        # Compute inference metrics
        if "inference_time" in metrics:
            inference_metrics = self._compute_inference_metrics(model, tokenizer, dataset)
            results.update(inference_metrics)
        
        # Compute generation quality metrics
        if "bleu" in metrics or "rouge" in metrics:
            quality_metrics = self._compute_quality_metrics(
                model, tokenizer, dataset, metrics
            )
            results.update(quality_metrics)
        
        return EvaluationMetrics(**results)
    
    def _load_test_data(self, dataset_path: str, num_samples: int) -> List[Dict[str, Any]]:
        """Load test dataset"""
        dataset_path = Path(dataset_path)
        
        if dataset_path.suffix == ".jsonl":
            # Load JSONL file
            data = []
            with open(dataset_path) as f:
                for i, line in enumerate(f):
                    if i >= num_samples:
                        break
                    data.append(json.loads(line))
            return data
        else:
            # Try loading as HuggingFace dataset
            try:
                dataset = load_dataset(str(dataset_path), split=f"test[:{num_samples}]")
                return list(dataset)
            except:
                raise ValueError(f"Unsupported dataset format: {dataset_path}")
    
    def _compute_perplexity(
        self,
        model: AutoModelForCausalLM,
        tokenizer: AutoTokenizer,
        dataset: List[Dict[str, Any]]
    ) -> float:
        """Compute perplexity on test set"""
        model.eval()
        total_loss = 0.0
        total_tokens = 0
        
        with torch.no_grad():
            for example in dataset:
                text = self._extract_text(example)
                inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                outputs = model(**inputs, labels=inputs["input_ids"])
                total_loss += outputs.loss.item() * inputs["input_ids"].size(1)
                total_tokens += inputs["input_ids"].size(1)
        
        perplexity = np.exp(total_loss / total_tokens)
        return float(perplexity)
    
    def _compute_inference_metrics(
        self,
        model: AutoModelForCausalLM,
        tokenizer: AutoTokenizer,
        dataset: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Compute inference speed metrics"""
        model.eval()
        total_time = 0.0
        total_tokens = 0
        
        if self.device == "cuda":
            torch.cuda.reset_peak_memory_stats()
        
        with torch.no_grad():
            for example in dataset[:10]:  # Use subset for timing
                text = self._extract_text(example)
                inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                start = time.perf_counter()
                outputs = model.generate(**inputs, max_new_tokens=50)
                end = time.perf_counter()
                
                total_time += (end - start)
                total_tokens += outputs.size(1)
        
        avg_time_ms = (total_time / 10) * 1000
        tokens_per_sec = total_tokens / total_time if total_time > 0 else 0.0
        
        memory_mb = 0.0
        if self.device == "cuda":
            memory_mb = torch.cuda.max_memory_allocated() / (1024 ** 2)
        
        return {
            "inference_time_ms": avg_time_ms,
            "tokens_per_second": tokens_per_sec,
            "memory_usage_mb": memory_mb
        }
    
    def _compute_quality_metrics(
        self,
        model: AutoModelForCausalLM,
        tokenizer: AutoTokenizer,
        dataset: List[Dict[str, Any]],
        metrics: List[str]
    ) -> Dict[str, Any]:
        """Compute generation quality metrics (BLEU, ROUGE)"""
        # Placeholder for quality metrics
        # Would require rouge-score and sacrebleu packages
        return {
            "bleu_score": None,
            "rouge_scores": None
        }
    
    def _extract_text(self, example: Dict[str, Any]) -> str:
        """Extract text from dataset example"""
        if "text" in example:
            return example["text"]
        elif "messages" in example:
            # Chat format
            return "\n".join([f"{m['role']}: {m['content']}" for m in example["messages"]])
        elif "instruction" in example:
            return f"Instruction: {example['instruction']}\nResponse: {example.get('response', '')}"
        else:
            return str(example)
    
    def save_results(self, metrics: EvaluationMetrics, experiment_name: str):
        """Save evaluation results to file"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_file = self.results_dir / f"{experiment_name}_{timestamp}.json"
        
        with open(output_file, "w") as f:
            json.dump(metrics.to_dict(), f, indent=2)
        
        print(f"✓ Results saved to {output_file}")
    
    def compare_models(
        self,
        model_paths: List[str],
        test_dataset: str,
        num_samples: int = 100
    ) -> Dict[str, EvaluationMetrics]:
        """Compare multiple models on same dataset"""
        results = {}
        
        for model_path in model_paths:
            model_name = Path(model_path).name
            print(f"\nEvaluating {model_name}...")
            metrics = self.evaluate_model(model_path, test_dataset, num_samples=num_samples)
            results[model_name] = metrics
            
            print(f"  Perplexity: {metrics.perplexity:.2f}")
            print(f"  Inference Time: {metrics.inference_time_ms:.2f}ms")
            print(f"  Tokens/sec: {metrics.tokens_per_second:.2f}")
        
        return results


def main():
    """CLI for automatic evaluation"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Automatic Model Evaluation")
    parser.add_argument("--model", type=str, required=True, help="Path to model")
    parser.add_argument("--dataset", type=str, required=True, help="Path to test dataset")
    parser.add_argument("--config", type=str, default="lora/lora.yaml", help="Config file")
    parser.add_argument("--num-samples", type=int, default=100, help="Number of test samples")
    parser.add_argument("--metrics", nargs="+", default=["perplexity", "inference_time"],
                        help="Metrics to compute")
    parser.add_argument("--output-name", type=str, default="evaluation", help="Output name")
    
    args = parser.parse_args()
    
    evaluator = AutomaticEvaluator(config_path=args.config)
    metrics = evaluator.evaluate_model(
        args.model,
        args.dataset,
        metrics=args.metrics,
        num_samples=args.num_samples
    )
    
    print("\n=== Evaluation Results ===")
    print(f"Perplexity: {metrics.perplexity:.2f}")
    print(f"Inference Time: {metrics.inference_time_ms:.2f}ms")
    print(f"Tokens/sec: {metrics.tokens_per_second:.2f}")
    print(f"Memory Usage: {metrics.memory_usage_mb:.2f}MB")
    
    evaluator.save_results(metrics, args.output_name)


if __name__ == "__main__":
    main()
