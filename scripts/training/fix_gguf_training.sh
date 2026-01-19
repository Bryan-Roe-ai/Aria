#!/bin/bash
# Quick fix script for GGUF training "No model path" issues

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

echo "🔧 GGUF Training Fix Script"
echo "=============================="
echo ""

# Function to list available LoRA models
list_models() {
    echo "📦 Available LoRA Models:"
    echo ""
    
    for dir in data_out/lora_training/* data_out/autotrain/* data_out/train_and_promote/*; do
        if [ -d "$dir" ]; then
            for checkpoint in "$dir"/checkpoint-*; do
                if [ -d "$checkpoint" ]; then
                    if [ -f "$checkpoint/adapter_config.json" ] && [ -f "$checkpoint/adapter_model.safetensors" ]; then
                        name=$(basename "$(dirname "$checkpoint")")
                        echo "  ✓ $name"
                        echo "    Path: $checkpoint"
                        echo ""
                    fi
                fi
            done
        fi
    done
}

# Function to run GGUF conversion with existing model
convert_existing() {
    local model_path="$1"
    local model_name=$(basename "$(dirname "$model_path")")
    
    echo "🔄 Converting: $model_name"
    echo "   From: $model_path"
    echo ""
    
    python scripts/training/quantum_gguf_complete_pipeline.py \
        --model-path "$model_path" \
        --no-deploy
}

# Main menu
echo "Options:"
echo "  1. List available LoRA models"
echo "  2. Convert most recent model to GGUF"
echo "  3. Quick quantum-enhanced GGUF pipeline"
echo "  4. Dry-run test"
echo ""

read -p "Select option (1-4): " choice

case $choice in
    1)
        list_models
        ;;
    2)
        echo ""
        python scripts/training/quantum_gguf_complete_pipeline.py --quick-quantum
        ;;
    3)
        echo ""
        python scripts/training/quantum_gguf_complete_pipeline.py --quick-quantum
        ;;
    4)
        echo ""
        python scripts/training/gguf_training_automation.py --dry-run --quick
        ;;
    *)
        echo "Invalid option"
        exit 1
        ;;
esac

echo ""
echo "✅ Done!"
