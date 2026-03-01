#!/usr/bin/env python
"""
Batch Model Evaluation Script

Evaluates models listed in a YAML config, outputs metrics to JSON/CSV.
Uses evaluate_lora_model.py for actual evaluation.

Usage:
  python scripts/evaluation_script.py --config batch_eval_config.yaml --output data_out/evaluation_results.json
"""
import argparse
import yaml
import json
import csv
import subprocess
import sys
from pathlib import Path
from datetime import datetime


def evaluate_model(model_path, dataset_path):
    """
    Evaluate a model using evaluate_lora_model.py.
    Falls back to stub metrics if evaluation fails.
    """
    try:
        # Use evaluate_lora_model.py for real evaluation
        script_path = Path(__file__).parent / "evaluate_lora_model.py"
        result = subprocess.run(
            [
                sys.executable,
                str(script_path),
                "--model", model_path,
                "--dataset", dataset_path,
                "--max-samples", "100",
                "--output-format", "json"
            ],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            # Parse JSON output from evaluate_lora_model.py
            output_lines = result.stdout.strip().split('\n')
            for line in reversed(output_lines):
                try:
                    metrics = json.loads(line)
                    return metrics
                except json.JSONDecodeError:
                    continue
        
        # If subprocess failed, return error metrics
        return {
            "error": "Evaluation failed",
            "stderr": result.stderr[:200] if result.stderr else "",
            "eval_time": str(datetime.now()),
        }
        
    except Exception as e:
        # Fallback to stub metrics if evaluation fails
        return {
            "error": str(e),
            "note": "Stub evaluation used due to error",
            "eval_time": str(datetime.now()),
        }


def main():
    ap = argparse.ArgumentParser(description="Batch Model Evaluation")
    ap.add_argument("--config", required=True, help="YAML config file")
    ap.add_argument("--output", required=True, help="Output file (json/csv)")
    args = ap.parse_args()

    with open(args.config) as f:
        config = yaml.safe_load(f)

    results = []
    for job in config.get("jobs", []):
        model_path = job.get("model_path")
        dataset_path = job.get("dataset_path")
        print(f"Evaluating {model_path} on {dataset_path}...")
        metrics = evaluate_model(model_path, dataset_path)
        results.append({
            "model": model_path,
            "dataset": dataset_path,
            **metrics
        })

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    if out_path.suffix == ".json":
        with out_path.open("w") as f:
            json.dump(results, f, indent=2)
    elif out_path.suffix == ".csv":
        if results:
            with out_path.open("w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)
    else:
        print("Unsupported output format. Use .json or .csv")
    
    print(f"\nResults written to {out_path}")


if __name__ == "__main__":
    main()
