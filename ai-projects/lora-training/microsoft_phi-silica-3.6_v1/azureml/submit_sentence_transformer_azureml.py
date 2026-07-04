#!/usr/bin/env python3
"""Submit the 50k SentenceTransformer Azure ML job via `az ml job create`."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
JOB_YAML = SCRIPT_DIR / "job-sentence-transformer-train.yml"
REPO_ROOT = SCRIPT_DIR.parents[3]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compute", default=os.environ.get("COMPUTE", "azureml:gpu-cluster"))
    parser.add_argument("--train-size", type=int, default=int(os.environ.get("TRAIN_SIZE", "50000")))
    parser.add_argument(
        "--hub-model-id",
        default=os.environ.get("HUB_MODEL_ID", "Bryan-Roe-ai/aria-minilm-all-nli-50k"),
    )
    parser.add_argument("--no-stream", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    subscription = os.environ.get("AZURE_ML_SUBSCRIPTION_ID", "").strip()
    resource_group = os.environ.get("AZURE_ML_RESOURCE_GROUP", "rg-phi36-ml").strip()
    workspace = os.environ.get("AZURE_ML_WORKSPACE", "phi36-ml-workspace").strip()
    if not subscription or subscription == "__REPLACE__":
        sys.exit("Set AZURE_ML_SUBSCRIPTION_ID")

    az = shutil.which("az") or ("/tmp/az-venv/bin/az" if Path("/tmp/az-venv/bin/az").exists() else None)
    if not az:
        sys.exit("Azure CLI not found; install azure-cli or use submit_sentence_transformer.sh")

    subprocess.run([az, "account", "set", "--subscription", subscription], check=True)
    subprocess.run(
        [az, "configure", "--defaults", f"group={resource_group}", f"workspace={workspace}"],
        check=True,
    )
    cmd = [
        az,
        "ml",
        "job",
        "create",
        "-f",
        str(JOB_YAML),
        "--set",
        f"compute={args.compute}",
        f"inputs.train_size={args.train_size}",
        f"inputs.hub_model_id={args.hub_model_id}",
    ]
    if os.environ.get("HF_TOKEN"):
        cmd.extend(["--set", f"environment_variables.HF_TOKEN={os.environ['HF_TOKEN']}"])
    if not args.no_stream:
        cmd.append("--stream")
    sys.exit(subprocess.run(cmd, cwd=REPO_ROOT).returncode)


if __name__ == "__main__":
    main()
