#!/bin/bash
# Massive Dataset Expansion Script
# Collects datasets from all sources in parallel

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
WORKSPACE_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
LOG_DIR="$WORKSPACE_ROOT/data_out/logs"

mkdir -p "$LOG_DIR"

echo "================================================================================"
echo "🚀 MASSIVE DATASET EXPANSION"
echo "================================================================================"
echo "Starting parallel collection from all sources..."
echo ""

# Function to run collector in background
run_collector() {
    local name=$1
    local script=$2
    local args=$3
    local log_file="$LOG_DIR/${name}_$(date +%Y%m%d_%H%M%S).log"
    
    echo "📦 Starting: $name"
    python "$script" $args > "$log_file" 2>&1 &
    local pid=$!
    echo "   PID: $pid"
    echo "   Log: $log_file"
    echo ""
}

# 1. sklearn + UCI + OpenML (fast sources)
run_collector "aggressive" \
    "$SCRIPT_DIR/aggressive_collector.py" \
    ""

# 2. HuggingFace bulk collection
run_collector "huggingface" \
    "$SCRIPT_DIR/huggingface_bulk_collector.py" \
    ""

# 3. Standard automation for additional coverage
run_collector "standard" \
    "$WORKSPACE_ROOT/scripts/dataset_automation.py" \
    "--sources sklearn openml uci --limit 100"

echo "================================================================================"
echo "✅ All collectors launched in background"
echo "================================================================================"
echo ""
echo "Monitor progress:"
echo "  tail -f $LOG_DIR/aggressive_*.log"
echo "  tail -f $LOG_DIR/huggingface_*.log"
echo "  tail -f $LOG_DIR/standard_*.log"
echo ""
echo "Check running processes:"
echo "  ps aux | grep 'dataset.*collector'"
echo ""
echo "View all logs:"
echo "  ls -lh $LOG_DIR/"
echo ""
