# Datasets Quick Start Guide

Complete reference for using datasets in Aria training, quantum ML, and chat applications.

## 📊 What's Available Now

**Total: 1,109 datasets** organized into 2 main categories:

### Quantum ML Datasets (38 curated CSVs)
Ready for quantum circuit training and variational algorithms.

**Small, hand-picked** (good for quick experiments):
- `ionosphere.csv` (351 samples, 34 features)
- `sonar.csv` (208 samples, 60 features)
- `banknote.csv` (1,372 samples, 5 features)
- `heart_disease.csv` (302 samples, 14 features)

**Quantum-friendly synthetic** (designed for quantum kernels):
- `quantum_xor.csv` (500 samples, 2D XOR pattern)
- `concentric_rings.csv` (600 samples, 2D non-linear)
- `crescent_moons.csv` (600 samples, 2D moons)
- `entangled_features.csv` (800 samples, 10D entangled)

**Larger datasets** (for production training):
- `digits.csv` (1,797 samples, 64 features - handwritten digits)
- `california_housing.csv` (20,640 samples, 8 features - regression)
- `letter_recognition.csv` (20,000 samples, 16 features)
- `optical_digits.csv` (3,823 samples, 64 features)
- `mushroom.csv` (8,124 samples, 22 features)

📍 Location: `datasets/quantum/*.csv`

### Massive Quantum Corpus (1,071 CSVs, organized by type)

**Synthetic datasets** (497 CSVs):
- `massive_quantum/synthetic/blobs/` (107 CSVs)
- `massive_quantum/synthetic/circles/` (82 CSVs)
- `massive_quantum/synthetic/classification/` (100 CSVs)
- `massive_quantum/synthetic/gaussian/` (91 CSVs)
- `massive_quantum/synthetic/moons/` (117 CSVs)

**Real-world data** (271 CSVs):
- `massive_quantum/medical/` (26 medical/health datasets)
- `massive_quantum/financial/` (47 credit/banking datasets)
- `massive_quantum/forex/` (98 currency pair time-series)

**Benchmarks** (156 CSVs):
- `massive_quantum/benchmarks/seeded/` (OpenML benchmarks with different random seeds)

**Misc & OpenML** (247 CSVs):
- `massive_quantum/misc/` (uncategorized)
- `massive_quantum/openml/` (explicit OpenML downloads)

📍 Location: `datasets/massive_quantum/` (recursive auto-discovery)

### Chat Training Datasets

**Aria personality** (curated, training-ready):
- `chat/aria_persona/` (15 core identity examples)
- `chat/aria_expanded/` (63 extended conversations)
- `chat/aria_simple/` (28 basic responses)
- `chat/aria_movement/` (40 character movement examples)

**Task-specific**:
- `chat/coding_instructions/` (8 code generation examples)

**Community datasets** (if present):
- `chat/dolly/` (Databricks Dolly 15k)
- `chat/openassistant/` (OpenAssistant conversations)
- `chat/mixed_chat/` (combined sources)

📍 Location: `datasets/chat/<subdirectory>/train.json`

---

## 🚀 Quick Start Examples

### Load a small quantum dataset (fast experiments)
\`\`\`python
from quantum.src.dataset_loader import load_dataset

X, y, _ = load_dataset('quantum_xor')  # 500 samples, 2D
print(f"Shape: {X.shape}, Classes: {set(y)}")
\`\`\`

### Load any quantum dataset and preprocess for N qubits
\`\`\`python
from scripts.dataset_helper import quick_load_for_qubits

# Returns properly scaled/dimensioned data
X_train, X_val, y_train, y_val = quick_load_for_qubits('sonar', n_qubits=8)
print(f"Training shape: {X_train.shape}")  # (280, 8) - exactly 8 features
\`\`\`

### Discover all available datasets
\`\`\`bash
python scripts/dataset_discovery.py           # List all 1,109 datasets
python scripts/dataset_discovery.py validate  # Check all are readable
python scripts/dataset_discovery.py quantum   # Show quantum datasets only
\`\`\`

### Find a dataset by name (recursive search)
\`\`\`python
from quantum.src.dataset_loader import load_dataset

# Searches datasets/quantum/, datasets/massive_quantum/ recursively
X, y, _ = load_dataset('synthetic_blobs_0_seed_42')  # Finds it!
\`\`\`

### Load chat training data
\`\`\`python
import json
from pathlib import Path

chat_data = json.load(open('datasets/chat/aria_persona/train.json'))
print(f"Loaded {len(chat_data)} training examples")
for example in chat_data[:2]:
    print(f"  Q: {example['instruction']}")
    print(f"  A: {example['output']}\
")
\`\`\`

---

## 📁 Directory Structure (At a Glance)

\`\`\`
datasets/
├── quantum/                 (38 curated CSVs ready to use)
│   ├── heart_disease.csv
│   ├── quantum_xor.csv
│   ├── digits.csv
│   └── ... (35 more)
│
├── massive_quantum/         (1,071 CSVs, organized into subfolders)
│   ├── synthetic/
│   │   ├── blobs/ (107)
│   │   ├── circles/ (82)
│   │   ├── classification/ (100)
│   │   ├── moons/ (117)
│   │   └── gaussian/ (91)
│   ├── medical/ (26)
│   ├── financial/ (47)
│   ├── forex/ (98)
│   ├── benchmarks/
│   │   └── seeded/ (156)
│   ├── openml/ (30)
│   └── misc/ (217)
│
├── chat/                    (16 subdirectories with .json files)
│   ├── aria_persona/
│   ├── aria_expanded/
│   ├── coding_instructions/
│   ├── dolly/
│   └── ... (12 more)
│
├── raw/                     (empty placeholder for future raw data)
└── dataset_index.json       (metadata for all 54+ indexed datasets)
\`\`\`

---

## 🛠️ Helper Tools

### dataset_discovery.py
Lists and validates all available datasets.
\`\`\`bash
python scripts/dataset_discovery.py          # List all
python scripts/dataset_discovery.py validate # Validate all readable
python scripts/dataset_discovery.py quantum  # List quantum only
\`\`\`

### dataset_helper.py
Convenience functions for training scripts.
\`\`\`python
from scripts.dataset_helper import quick_load_quantum, quick_load_for_qubits

# Quick split into train/val
X_train, X_val, y_train, y_val = quick_load_quantum('sonar')

# Auto-dimension to match qubits
X_train, X_val, y_train, y_val = quick_load_for_qubits('banknote', n_qubits=4)
\`\`\`

### dataset_loader.py (core module)
Advanced dataset loading with preprocessing.
\`\`\`python
from quantum.src.dataset_loader import load_dataset, preprocess_for_qubits

# Load with feature names
X, y, feature_names = load_dataset('sonar', return_feature_names=True)

# Preprocess for quantum circuits
X_train, X_val, scaler, pca = preprocess_for_qubits(X_train, X_val, n_qubits=8)
\`\`\`

---

## 📊 Using in Training Scripts

### Example: Quantum ML with new datasets
\`\`\`python
#!/usr/bin/env python3
from scripts.dataset_helper import quick_load_for_qubits

# Load and prepare data
X_train, X_val, y_train, y_val = quick_load_for_qubits('quantum_xor', n_qubits=4)

# Use in your quantum circuit...
import pennylane as qml
dev = qml.device('default.qubit', wires=4)

@qml.qnode(dev)
def circuit(x):
    # Encode and process...
    return qml.expval(qml.PauliZ(0))

# Training loop
for x, y in zip(X_train, y_train):
    pred = circuit(x)
    # ... compute loss, update ...
\`\`\`

### Example: Experiment with different datasets
\`\`\`python
# Quick benchmark across multiple quantum datasets
from scripts.dataset_discovery import get_datasets_by_category
from scripts.dataset_helper import quick_load_quantum

quantum_datasets = get_datasets_by_category('quantum')
for ds_name in quantum_datasets:
    try:
        X_train, X_val, y_train, y_val = quick_load_quantum(ds_name)
        print(f"{ds_name}: train={X_train.shape}, val={X_val.shape}")
    except Exception as e:
        print(f"{ds_name}: ERROR - {e}")
\`\`\`

### Example: Loading chat data for fine-tuning
\`\`\`python
import json
from pathlib import Path

# Load Aria persona training data
chat_dir = Path('datasets/chat')
aria_data = json.load(open(chat_dir / 'aria_persona' / 'train.json'))

# Prepare for LoRA fine-tuning
train_examples = [
    {"prompt": ex["instruction"], "completion": ex["output"]}
    for ex in aria_data
]

# Use with transformers/HuggingFace LoRA...
\`\`\`

---

## 💡 Dataset Usage Tips

1. **Start small**: Use `quantum/` datasets first (fast feedback loops)
2. **Experiment freely**: `massive_quantum/synthetic/` has clean, controlled datasets
3. **Scale up**: Real datasets in `massive_quantum/medical/` and `massive_quantum/financial/`
4. **Know your data**: Run `python scripts/dataset_discovery.py validate` before production
5. **Organize runs**: Different datasets often need different hyperparameters

---

## 📝 Dataset Index Metadata

Full metadata available in `datasets/dataset_index.json`:
- Path to each dataset
- Sample counts
- Feature dimensions
- Category tags
- Data types
- Descriptions

\`\`\`bash
python -m json.tool datasets/dataset_index.json | head -50
\`\`\`

---

## ❓ FAQ

**Q: Can I add my own datasets?**  
A: Yes! Add CSVs to `datasets/quantum/` or `datasets/massive_quantum/<category>/`, then run `python scripts/dataset_discovery.py` to refresh.

**Q: How do I load a dataset by full name?**  
A: `load_dataset('synthetic_blobs_0_seed_42')` searches recursively.

**Q: What if a dataset is corrupted?**  
A: Run `python scripts/dataset_discovery.py validate` to identify bad files.

**Q: Can I use datasets for commercial projects?**  
A: Most are public + high-quality. Check licenses in dataset_index.json metadata.

---

*Last updated: March 2, 2026*  
*Total datasets: 1,109 | Categories: 8 | Scripts: 3 helper utilities*
