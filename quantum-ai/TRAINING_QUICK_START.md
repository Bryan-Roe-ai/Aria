# 🚀 QAI Training Quick Start Guide

**Status:** ✅ Models Setup Complete
**Date:** January 31, 2026
**Location:** `quantum-ai/`

---

## One-Command Start

### Option 1: Run Full Training Suite
```bash
python examples/train_models.py
```
**What it does:**
- Trains 3 hybrid quantum-classical models
- Tests on Moons, Iris, and Circles datasets
- Generates accuracy plots and comparisons
- Saves results to `results/`
- Duration: ~2-5 minutes

**Expected Output:**
```
========================================
QUANTUM MACHINE LEARNING TRAINING EXAMPLES
========================================
1. BINARY CLASSIFICATION: MOONS DATASET
✅ Training on 160 samples...
   Epoch 1/100: Loss = 0.48, Accuracy = 52%
   Epoch 50/100: Loss = 0.12, Accuracy = 82%
   Epoch 100/100: Loss = 0.06, Accuracy = 92%
✅ Final Accuracy: 85% (on validation set)
```

---

### Option 2: Launch Interactive Dashboard
```bash
# Windows
start_dashboard.bat

# Linux/Mac
./start_dashboard.sh
```

**Dashboard Features:**
- 🎨 Real-time training visualization
- 📊 Live loss/accuracy curves (updated every second)
- 🎛️ Interactive hyperparameter controls
- 💾 Training session management
- 📈 Model comparison charts

**Access:** http://localhost:5000

---

### Option 3: Run Quick Simulations (No Training)
```bash
python examples/run_simulations.py
```
**What it does:**
- Creates Bell states
- Demonstrates superposition
- Shows gradient computation
- Visualizes quantum state evolution
- Duration: ~30 seconds

---

## Training Configuration

### Available Configurations (in `checkpoints/training_config.json`)

**1. DEFAULT (Moons Dataset)**
```json
{
  "epochs": 100,
  "learning_rate": 0.01,
  "batch_size": 8,
  "backend": "lightning.qubit"
}
```
- Best for: Quick training demo
- Expected accuracy: ~85%
- Training time: ~2 minutes

**2. INTENSIVE (Iris Dataset)**
```json
{
  "epochs": 200,
  "learning_rate": 0.001,
  "batch_size": 4,
  "backend": "default.qubit"
}
```
- Best for: Higher accuracy
- Expected accuracy: ~90%
- Training time: ~5 minutes

**3. QUICK (Fast Testing)**
```json
{
  "epochs": 10,
  "learning_rate": 0.01,
  "batch_size": 16,
  "backend": "lightning.qubit"
}
```
- Best for: Rapid testing
- Expected accuracy: ~60%
- Training time: ~20 seconds

---

## Model Registry

Located in: `checkpoints/registry.json`

### Available Models

1. **Quantum Classifier** (Hybrid Quantum-Classical)
   - Framework: PennyLane
   - Qubits: 4
   - Layers: 2
   - Backend: lightning.qubit
   - Best for: Binary/multiclass classification

2. **Variational Circuit** (Parametrized VQC)
   - Framework: PennyLane
   - Qubits: 4
   - Layers: 3
   - Backend: default.qubit
   - Best for: Feature extraction

3. **Grover Algorithm** (Quantum Search)
   - Framework: Qiskit
   - Qubits: 3
   - Shots: 1000
   - Backend: qasm_simulator
   - Best for: Unstructured search

---

## Checkpoint Structure

```
quantum-ai/
├── checkpoints/
│   ├── quantum_classifier/        # Hybrid model checkpoints
│   ├── variational_circuits/      # VQC saved states
│   ├── grover_algorithms/         # Search results
│   ├── ensemble_models/           # Multi-model voting
│   ├── best_models/               # Top performers
│   ├── experiments/               # Experimental runs
│   ├── backups/                   # Backup checkpoints
│   ├── registry.json              # Model registry
│   ├── training_config.json       # Training templates
│   ├── metrics.json               # Performance tracking
│   └── setup_report.json          # Setup verification
├── results/
│   ├── training_demo.png          # Training progress plots
│   ├── accuracy_comparison.png    # Model comparison
│   ├── loss_curves.png            # Loss evolution
│   └── *.png                      # Generated visualizations
└── logs/
    └── training_*.log              # Training logs
```

---

## Performance Targets

| Metric | Target | Status |
|--------|--------|--------|
| Quantum Classifier Accuracy | ≥85% | 🎯 |
| Variational Circuit Loss | ≤0.05 | 🎯 |
| Training Time | ≤300 seconds | ✅ |
| Inference Time | ≤100ms | ✅ |

---

## GPU Optimization

### Check GPU Status
```python
import torch
print(f"CUDA Available: {torch.cuda.is_available()}")
print(f"Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")
```

### Optimize Backend Selection
```python
# Fastest (recommended for development)
backend = "lightning.qubit"

# More accurate but slower
backend = "default.qubit"

# CPU-only fallback
backend = "default.qubit.legacy"
```

### Memory Optimization
```python
# Reduce batch size if OOM
batch_size = 4  # Instead of 8

# Reduce data samples
n_samples = 100  # Instead of 200

# Use mixed precision
torch.set_float32_matmul_precision('medium')
```

---

## Azure Quantum Integration

### Step 1: Verify Configuration
```bash
python examples/azure_integration.py
```

### Step 2: Submit to Azure
```bash
python azure_quantum_deploy.py
```

### Workflow
1. **Local simulation** → `backend: qiskit_aer`
2. **Azure simulator** → `backend: azure_ionq_simulator`
3. **Real QPU** → `backend: azure_ionq_hvn` (after cost review)

---

## Troubleshooting

### Problem: Import Errors
```bash
pip install -r requirements.txt
```

### Problem: Port 5000 Already in Use (Dashboard)
```bash
# Windows
netstat -ano | findstr 5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :5000
kill -9 <PID>
```

### Problem: CUDA Out of Memory
```python
# Reduce batch size
batch_size = 4

# Use CPU backend
backend = "lightning.qubit"  # CPU-friendly

# Clear cache
torch.cuda.empty_cache()
```

### Problem: Training Very Slow
```python
# Use lightning backend (fastest)
dev = qml.device("lightning.qubit", wires=4)

# Reduce qubits if possible
n_qubits = 2  # Instead of 4

# Reduce data samples
X_train = X_train[:100]  # Instead of 200
```

---

## Next Steps After Training

1. **Evaluate Results**
   - Check `results/` for plots
   - Review accuracy metrics
   - Compare models

2. **Save Best Model**
   - Checkpoint automatically saved to `checkpoints/best_models/`
   - Registry updated in `registry.json`

3. **Deploy to Azure**
   - Run `python azure_quantum_deploy.py`
   - Submit to Azure Quantum
   - Monitor job status

4. **Fine-tune Hyperparameters**
   - Adjust learning rate
   - Increase epochs
   - Change architecture

---

## Monitoring Training

### Real-time Monitoring
```bash
# Watch training logs
tail -f logs/training_*.log

# Monitor resources
python scripts/resource_monitor.py --stream
```

### Dashboard Metrics
- Loss curve (updating live)
- Accuracy curve (updating live)
- Training time elapsed
- Epochs completed
- Batches processed

---

## File Locations

| File | Purpose |
|------|---------|
| `examples/train_models.py` | Main training script |
| `examples/run_simulations.py` | Quantum simulations |
| `examples/azure_integration.py` | Azure setup test |
| `start_dashboard.bat` | Dashboard launcher (Windows) |
| `start_dashboard.sh` | Dashboard launcher (Linux/Mac) |
| `checkpoints/registry.json` | Model registry |
| `checkpoints/training_config.json` | Training templates |
| `results/` | Generated plots and results |

---

## Quick Reference

```bash
# Train models
python examples/train_models.py

# Start dashboard
start_dashboard.bat  # or ./start_dashboard.sh

# Run simulations
python examples/run_simulations.py

# Test Azure
python examples/azure_integration.py

# Deploy to Azure
python azure_quantum_deploy.py

# Monitor resources
python scripts/resource_monitor.py --stream
```

---

**🎉 Ready to Train! Pick an option above and get started.** 🚀

For detailed documentation, see:
- `README.md` - Full documentation
- `QUICK_REFERENCE.md` - Command reference
- `MCP_SERVER_README.md` - MCP server setup
- `config/quantum_config.yaml` - Configuration details
