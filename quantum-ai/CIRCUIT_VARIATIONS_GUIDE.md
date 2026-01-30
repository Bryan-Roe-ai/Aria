# Quantum Circuit Variations - Quick Guide

## 🚀 Quick Start

```bash
cd /workspaces/AI/quantum-ai
python custom_circuits.py
```

## 🎛️ Easy Customization

Edit the top of `custom_circuits.py` to experiment:

### **Option 1: Change Circuit Type**
```python
CIRCUIT_TYPE = "custom"        # Fully customizable
CIRCUIT_TYPE = "symmetric"     # All qubits identical
CIRCUIT_TYPE = "cascade"       # Information flows through qubits
CIRCUIT_TYPE = "random_walk"   # Quantum random walk
```

### **Option 2: Adjust Qubits**
```python
N_QUBITS = 2   # Simple 2-qubit system
N_QUBITS = 3   # Medium complexity
N_QUBITS = 4   # Default (current)
N_QUBITS = 5   # More complex (32 states)
N_QUBITS = 6   # Very complex (64 states)
```

### **Option 3: Tune Parameters**
```python
CUSTOM_PARAMS = {
    'rotation_angles': [π/4, π/3, π/6, π/2],  # Change these!
    'coupling_strength': 0.5,   # 0 (weak) to 1 (strong)
    'layer_depth': 3,           # 1, 2, 3, 4, 5...
    'entanglement_type': 'circular'  # See options below
}
```

### **Entanglement Types:**
- `'linear'` - Nearest neighbors only (simple)
- `'circular'` - Ring topology (current)
- `'all-to-all'` - Every qubit connects (complex)
- `'pyramid'` - Hierarchical (efficient)

## 📊 What Gets Generated

**4 visualizations in one image:**
1. **Probability bar chart** - All quantum states
2. **Pie chart** - Major states distribution  
3. **Parameter sensitivity** - How results change
4. **Cumulative distribution** - State concentration

**Plus analysis:**
- Top quantum states with probabilities
- Entropy measure (uniformity)
- Parameter comparison tests

## 🎯 Example Experiments

### Experiment 1: Maximum Entanglement
```python
N_QUBITS = 3
CIRCUIT_TYPE = "custom"
CUSTOM_PARAMS = {
    'rotation_angles': [0, 0, 0],
    'coupling_strength': 1.0,
    'layer_depth': 1,
    'entanglement_type': 'circular'
}
```

### Experiment 2: Quantum Interference
```python
N_QUBITS = 4
CIRCUIT_TYPE = "symmetric"
# All qubits get same rotation → interference patterns
```

### Experiment 3: Information Cascade
```python
N_QUBITS = 5
CIRCUIT_TYPE = "cascade"
# Watch information flow from qubit 0 to qubit 4
```

### Experiment 4: Complex Entanglement
```python
N_QUBITS = 4
CUSTOM_PARAMS = {
    'rotation_angles': [π/2, π/3, π/4, π/6],
    'coupling_strength': 0.8,
    'layer_depth': 5,
    'entanglement_type': 'all-to-all'
}
```

## 📈 Current Results

**Circuit:** Custom with 4 qubits, circular entanglement, 3 layers

**Top states:**
- |0001⟩: 21.9% ⭐
- |0010⟩: 12.3%
- |0111⟩: 11.2%

**Entropy:** 88.4% uniformity (high superposition!)

## 🔬 Tips for Exploration

1. **Start simple:** 2-3 qubits, 1-2 layers
2. **One change at a time:** See what each parameter does
3. **Watch entropy:** Higher = more uniform distribution
4. **Compare types:** Run all 4 circuit types with same qubit count
5. **Parameter scan:** Use plot #3 to find interesting values

## 🎨 Files Generated

- `custom_variation.png` - Main analysis (current)
- `symmetric_variation.png` - If you use symmetric circuit
- `cascade_variation.png` - If you use cascade circuit
- `random_walk_variation.png` - If you use random walk

## ⚡ Quick Tests

```bash
# Test all circuit types quickly
for type in custom symmetric cascade random_walk; do
    python custom_circuits.py  # Edit CIRCUIT_TYPE first
done
```

Happy experimenting! 🚀
