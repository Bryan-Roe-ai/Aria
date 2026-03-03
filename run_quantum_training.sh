#!/bin/bash

# Quantum AI Training Workflow - Sequential Execution
# =================================================

VENV_PYTHON="/home/bryan/Aria/Aria/.venv/bin/python"
WORK_DIR="/home/bryan/Aria/Aria"
OUTPUT_LOG="/home/bryan/Aria/Aria/data_out/quantum_training_execution.log"

cd "$WORK_DIR"

# Create output directory if needed
mkdir -p data_out/quantum

# Function to run a training job and capture metrics
run_training_job() {
    local job_name=$1
    local preset=$2
    local epochs=$3
    local batch_size=$4
    local n_qubits=$5
    
    echo ""
    echo "=========================================="
    echo "Job: $job_name"
    echo "Preset: $preset | Epochs: $epochs | Batch Size: $batch_size | QBits: $n_qubits"
    echo "=========================================="
    
    local start_time=$(date +"%Y-%m-%d %H:%M:%S")
    local start_epoch=$(date +%s)
    
    echo "START TIME: $start_time"
    
    # Run the training
    "$VENV_PYTHON" quantum/train_custom_dataset.py \
        --preset "$preset" \
        --epochs "$epochs" \
        --batch-size "$batch_size" \
        --n-qubits "$n_qubits" \
        2>&1 | tee "/tmp/${job_name}_output.log"
    
    local exit_code=${PIPESTATUS[0]}
    local end_epoch=$(date +%s)
    local end_time=$(date +"%Y-%m-%d %H:%M:%S")
    local duration=$((end_epoch - start_epoch))
    
    echo ""
    echo "END TIME: $end_time"
    echo "DURATION: ${duration}s"
    echo "EXIT CODE: $exit_code"
    
    if [ $exit_code -ne 0 ]; then
        echo "❌ FAILED: $job_name"
        return 1
    else
        echo "✅ SUCCESS: $job_name"
        # Extract final metrics from output
        if grep -q "Final Accuracy" "/tmp/${job_name}_output.log"; then
            echo "Final Accuracy:" $(grep "Final Accuracy" "/tmp/${job_name}_output.log" | tail -1)
        fi
        if grep -q "Final Loss" "/tmp/${job_name}_output.log"; then
            echo "Final Loss:" $(grep "Final Loss" "/tmp/${job_name}_output.log" | tail -1)
        fi
        return 0
    fi
}

echo "Starting Quantum Training Workflow..."
echo "Workspace: $WORK_DIR"
echo "Python: $VENV_PYTHON"
echo "Timestamp: $(date)"
echo "" | tee "$OUTPUT_LOG"

# Step 1: Quick Sanity Test (2 epochs)
echo "="
echo "STEP 1/3: Quick Sanity Test (Heart, 2 epochs)"
echo "="
run_training_job "sanity_test" "heart" "2" "16" "4" | tee -a "$OUTPUT_LOG"
sanity_result=$?

if [ $sanity_result -ne 0 ]; then
    echo "❌ Sanity test failed. Aborting remaining jobs."
    exit 1
fi

# Step 2: Heart Quick (50 epochs)
echo ""
echo "="
echo "STEP 2/3: Heart Quick Job (50 epochs)"
echo "="
run_training_job "heart_quick" "heart" "50" "16" "4" | tee -a "$OUTPUT_LOG"
heart_result=$?

# Step 3: Ionosphere Quick (100 epochs)
echo ""
echo "="
echo "STEP 3/3: Ionosphere Quick Job (100 epochs)"
echo "="
run_training_job "ionosphere_quick" "ionosphere" "100" "16" "4" | tee -a "$OUTPUT_LOG"
ionosphere_result=$?

# Summary
echo ""
echo "=========================================="
echo "TRAINING SUMMARY"
echo "=========================================="
echo "Sanity Test (heart, 2 epochs): $([ $sanity_result -eq 0 ] && echo '✅ PASS' || echo '❌ FAIL')"
echo "Heart Quick (50 epochs): $([ $heart_result -eq 0 ] && echo '✅ PASS' || echo '❌ FAIL')"
echo "Ionosphere Quick (100 epochs): $([ $ionosphere_result -eq 0 ] && echo '✅ PASS' || echo '❌ FAIL')"
echo ""
echo "Output log: $OUTPUT_LOG"
echo "Model artifacts: data_out/quantum/"
echo "=========================================="

# Verify outputs
echo ""
echo "Checking output directory..."
if [ -d "data_out/quantum" ]; then
    echo "Contents of data_out/quantum/:"
    ls -lhR data_out/quantum/ | head -50
else
    echo "⚠️  data_out/quantum/ is empty"
fi

# Exit with appropriate code
if [ $sanity_result -eq 0 ] && [ $heart_result -eq 0 ] && [ $ionosphere_result -eq 0 ]; then
    echo ""
    echo "✅ ALL JOBS COMPLETED SUCCESSFULLY"
    exit 0
else
    echo ""
    echo "❌ SOME JOBS FAILED"
    exit 1
fi
