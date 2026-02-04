# 🎯 QAI MODELS - QUICK REFERENCE CARD

## One-Liner Commands

```bash
# Train all models
python examples/train_models.py

# Run simulations only (no training)
python examples/run_simulations.py

# Launch web dashboard
start_dashboard.bat              # Windows
./start_dashboard.sh             # Linux/Mac

# Test Azure integration
python examples/azure_integration.py

# Deploy to Azure Quantum
python azure_quantum_deploy.py
```

---

## Notebook Sections (QAI_Models_Setup.ipynb)

| Cell | Section | Purpose |
|------|---------|---------|
| 1 | 📘 Intro | Project overview |
| 2 | 📦 Imports | Load libraries |
| 3 | 🔗 Imports Cont. | Verify packages |
| 4 | 📦 Dependencies | Install missing |
| 5 | 🔧 Environment | Init QAI setup |
| 6 | 📁 Checkpoints | Create dirs |
| 7 | ⚙️ Configuration | Set parameters |
| 8 | 📊 Data | Load datasets |
| 9 | 🔄 Training | Quick demo |
| 10 | 📚 Resources | Docs & next steps |

---

## Model Quick Stats

| Model | Framework | Qubits | Layers | Backend | Best For |
|-------|-----------|--------|--------|---------|----------|
| Classifier | PennyLane | 4 | 2 | lightning | Classification |
| VQC | PennyLane | 4 | 3 | default | Feature extract |
| Grover | Qiskit | 3 | - | qasm_sim | Search |
| Ensemble | Hybrid | - | - | - | Accuracy |

---

## Training Profiles

**QUICK:** 10 epochs → 20s → 60% accuracy
```json
{"epochs": 10, "learning_rate": 0.01, "batch_size": 16}
```

**DEFAULT:** 100 epochs → 2min → 85% accuracy
```json
{"epochs": 100, "learning_rate": 0.01, "batch_size": 8}
```

**INTENSIVE:** 200 epochs → 5min → 90% accuracy
```json
{"epochs": 200, "learning_rate": 0.001, "batch_size": 4}
```

---

## File Locations

```
quantum-ai/
├── QAI_Models_Setup.ipynb ............ Interactive notebook ✨
├── TRAINING_QUICK_START.md .......... Training guide 📖
├── SETUP_README.txt ................. This file 📋
├── examples/
│   ├── train_models.py ............. Main training script
│   └── run_simulations.py .......... Quantum sims
├── checkpoints/
│   ├── registry.json ............... Model list
│   ├── training_config.json ........ Configs
│   └── *.npz ....................... Saved models
└── results/
    └── *.png ....................... Plots
```

---

## Environment Variables

```bash
# GPU/Device
CUDA_VISIBLE_DEVICES=0              # Use first GPU

# PennyLane
PL_BACKEND=lightning.qubit          # Fastest backend

# Azure (optional)
AZURE_SUBSCRIPTION_ID=...
AZURE_RESOURCE_GROUP=rg-quantum-ai
```

---

## Python API Quick Start

```python
# 1. Import
import pennylane as qml
import torch
import numpy as np

# 2. Create device
dev = qml.device('lightning.qubit', wires=4)

# 3. Define circuit
@qml.qnode(dev)
def circuit(params, x):
    for i in range(4):
        qml.RY(x[i], wires=i)
    for i, p in enumerate(params):
        qml.RX(p, wires=i)
    return qml.expval(qml.PauliZ(0))

# 4. Get result
params = np.random.randn(4)
x = np.random.randn(4)
result = circuit(params, x)  # → number between -1 and 1
```

---

## Dashboard Features

| Feature | URL | Port |
|---------|-----|------|
| Training Viz | http://localhost:5000 | 5000 |
| Loss Curves | Auto-updating | - |
| Accuracy Curves | Auto-updating | - |
| Hyperparameter Tuning | Interactive | - |
| Session Management | Save/Load | - |

---

## Troubleshooting Quick Fixes

**Error: Module not found**
→ `pip install -r requirements.txt`

**Error: Port 5000 in use**
→ `netstat -ano | findstr 5000` (Windows)

**Error: CUDA out of memory**
→ Reduce batch_size or use lightning backend

**Error: Training too slow**
→ Switch to `lightning.qubit` backend

---

## Performance Tips

✅ **Fast:** `lightning.qubit` backend
✅ **Accurate:** `default.qubit` backend
✅ **Development:** Use small n_qubits (2-4)
✅ **GPU:** Use PyTorch for data preprocessing
✅ **Production:** Test locally first, then Azure

---

## Data Formats

**Training Data:**
```python
X_train.shape = (n_samples, 4)      # Padded to 4 features
y_train.shape = (n_samples,)        # Labels: 0/1 (binary)
```

**Checkpoints:**
```python
# Saved as numpy
model_state = np.load('checkpoint.npz')
params = model_state['params']
```

---

## Monitoring

```bash
# Watch training logs (Linux/Mac)
tail -f logs/training_*.log

# Monitor GPU
watch -n 1 nvidia-smi

# Check resource usage
python scripts/resource_monitor.py --snapshot
```

---

## Common Workflows

### Workflow 1: Quick Test
```bash
1. Run notebook cell 9 (5 epoch demo)
2. Check training_demo.png
3. Done! (~1 minute)
```

### Workflow 2: Full Training
```bash
1. python examples/train_models.py
2. Wait 2-5 minutes
3. Check results/*.png
4. Review metrics in registry.json
```

### Workflow 3: Interactive Training
```bash
1. start_dashboard.bat
2. Visit http://localhost:5000
3. Adjust parameters live
4. Watch curves update in real-time
```

---

## Config Reference

`config/quantum_config.yaml`:
```yaml
ml:
  model:
    n_qubits: 4              # Change to 2/3/4/5
    n_layers: 2              # Change to 1-5
  training:
    epochs: 100              # Change for quick/intensive
    learning_rate: 0.01      # Change to 0.001-0.1
    batch_size: 8            # Change to 4/8/16
```

---

## Success Indicators

✅ Notebook runs without errors
✅ Models load from registry
✅ Training loss decreases
✅ Accuracy improves over epochs
✅ Dashboard shows live updates
✅ Results saved to output directories

---

## Next Level

After training works:
1. **Fine-tune:** Adjust hyperparameters
2. **Deploy:** Push to Azure Quantum
3. **Scale:** Use multiple GPUs
4. **Optimize:** Profile & benchmark

---

**🚀 Ready? Pick a command above and go!**

For detailed guide: See `TRAINING_QUICK_START.md`
