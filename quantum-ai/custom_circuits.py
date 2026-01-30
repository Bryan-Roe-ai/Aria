#!/usr/bin/env python3
"""
Custom Quantum Circuit Variations
Easy-to-modify circuits for experimentation
"""
import pennylane as qml
import numpy as np
import matplotlib.pyplot as plt

print("=" * 70)
print("  CUSTOM QUANTUM CIRCUIT VARIATIONS")
print("=" * 70)

# ========== CONFIGURATION (EDIT THESE!) ==========
N_QUBITS = 4  # Change to 2, 3, 4, 5, etc.
SHOTS = 1000  # Number of measurements
CIRCUIT_TYPE = "custom"  # Options: "custom", "symmetric", "cascade", "random_walk"

# Custom parameters (feel free to modify!)
CUSTOM_PARAMS = {
    'rotation_angles': [np.pi/4, np.pi/3, np.pi/6, np.pi/2],  # One per qubit
    'coupling_strength': 0.5,  # 0 to 1
    'layer_depth': 3,  # Number of variational layers
    'entanglement_type': 'circular',  # 'linear', 'circular', 'all-to-all', 'pyramid'
}
# ==================================================

dev = qml.device('lightning.qubit', wires=N_QUBITS, shots=SHOTS)

print(f"\n[Configuration]")
print(f"  Qubits: {N_QUBITS}")
print(f"  Shots: {SHOTS}")
print(f"  Circuit Type: {CIRCUIT_TYPE}")
print(f"  Entanglement: {CUSTOM_PARAMS['entanglement_type']}")
print(f"  Layers: {CUSTOM_PARAMS['layer_depth']}")

# ========== VARIATION 1: CUSTOM PARAMETERIZED CIRCUIT ==========
@qml.qnode(dev)
def custom_circuit(params):
    """Fully customizable variational circuit"""
    n_layers = CUSTOM_PARAMS['layer_depth']
    
    # Initial state preparation
    for i in range(N_QUBITS):
        qml.Hadamard(wires=i)
    
    # Variational layers
    for layer in range(n_layers):
        # Single-qubit rotations
        for i in range(N_QUBITS):
            idx = (layer * N_QUBITS + i) % len(params)
            qml.RY(params[idx] * CUSTOM_PARAMS['coupling_strength'], wires=i)
            qml.RZ(params[idx] * 0.5, wires=i)
        
        # Entanglement
        if CUSTOM_PARAMS['entanglement_type'] == 'linear':
            for i in range(N_QUBITS - 1):
                qml.CNOT(wires=[i, i+1])
        
        elif CUSTOM_PARAMS['entanglement_type'] == 'circular':
            for i in range(N_QUBITS):
                qml.CNOT(wires=[i, (i+1) % N_QUBITS])
        
        elif CUSTOM_PARAMS['entanglement_type'] == 'all-to-all':
            for i in range(N_QUBITS):
                for j in range(i+1, N_QUBITS):
                    qml.CNOT(wires=[i, j])
        
        elif CUSTOM_PARAMS['entanglement_type'] == 'pyramid':
            step = 1
            while step < N_QUBITS:
                for i in range(0, N_QUBITS - step, step * 2):
                    qml.CNOT(wires=[i, i + step])
                step *= 2
    
    return qml.probs(wires=range(N_QUBITS))

# ========== VARIATION 2: SYMMETRIC CIRCUIT ==========
@qml.qnode(dev)
def symmetric_circuit(theta):
    """All qubits treated identically"""
    for i in range(N_QUBITS):
        qml.RY(theta, wires=i)
    
    for i in range(N_QUBITS - 1):
        qml.CNOT(wires=[i, i+1])
    
    for i in range(N_QUBITS):
        qml.RZ(theta * 0.5, wires=i)
    
    return qml.probs(wires=range(N_QUBITS))

# ========== VARIATION 3: CASCADE CIRCUIT ==========
@qml.qnode(dev)
def cascade_circuit(angles):
    """Information cascades through qubits"""
    # Initialize first qubit
    qml.RY(angles[0], wires=0)
    
    # Cascade through qubits
    for i in range(N_QUBITS - 1):
        qml.CNOT(wires=[i, i+1])
        if i+1 < len(angles):
            qml.RY(angles[i+1], wires=i+1)
        qml.RZ(angles[i] * 0.3, wires=i+1)
    
    # Final layer
    for i in range(N_QUBITS):
        qml.Hadamard(wires=i)
    
    return qml.probs(wires=range(N_QUBITS))

# ========== VARIATION 4: QUANTUM RANDOM WALK ==========
@qml.qnode(dev)
def random_walk_circuit(steps):
    """Simulate quantum random walk"""
    # Initial superposition
    qml.Hadamard(wires=0)
    
    for step in range(steps):
        # Coin operator
        qml.Hadamard(wires=0)
        
        # Shift operator (use available qubits as position)
        for i in range(min(N_QUBITS-1, step+1)):
            qml.CNOT(wires=[0, i+1])
        
        # Phase
        qml.RZ(np.pi * 0.1 * step, wires=0)
    
    return qml.probs(wires=range(N_QUBITS))

# ========== RUN SELECTED CIRCUIT ==========
print(f"\n{'='*70}")
print(f"  RUNNING: {CIRCUIT_TYPE.upper()} CIRCUIT")
print(f"{'='*70}")

if CIRCUIT_TYPE == "custom":
    params = np.array(CUSTOM_PARAMS['rotation_angles'])
    results = custom_circuit(params)
    print(f"\nParameters: {params}")
    print(qml.draw(custom_circuit)(params))

elif CIRCUIT_TYPE == "symmetric":
    theta = np.pi / 3
    results = symmetric_circuit(theta)
    print(f"\nSymmetric angle: {theta:.3f}")
    print(qml.draw(symmetric_circuit)(theta))

elif CIRCUIT_TYPE == "cascade":
    angles = np.linspace(0, np.pi, N_QUBITS)
    results = cascade_circuit(angles)
    print(f"\nCascade angles: {angles}")
    print(qml.draw(cascade_circuit)(angles))

elif CIRCUIT_TYPE == "random_walk":
    steps = 4
    results = random_walk_circuit(steps)
    print(f"\nRandom walk steps: {steps}")
    print(qml.draw(random_walk_circuit)(steps))

# ========== ANALYZE RESULTS ==========
print(f"\n{'='*70}")
print("  RESULTS ANALYSIS")
print(f"{'='*70}")

# Find top states
top_k = min(8, len(results))
top_indices = np.argsort(results)[-top_k:][::-1]

print(f"\nTop {top_k} Quantum States:")
for idx in top_indices:
    binary = format(idx, f'0{N_QUBITS}b')
    prob = results[idx]
    if prob > 0.001:  # Only show non-negligible probabilities
        bar = '█' * int(prob * 50)
        print(f"  |{binary}⟩: {prob:.3f} {bar}")

# Statistics
entropy = -np.sum(results * np.log2(results + 1e-10))
max_entropy = N_QUBITS  # log2(2^N_QUBITS)
print(f"\nEntropy: {entropy:.2f} / {max_entropy:.2f} (max)")
print(f"Uniformity: {entropy/max_entropy:.1%}")

# ========== VISUALIZATIONS ==========
print(f"\n{'='*70}")
print("  CREATING VISUALIZATIONS")
print(f"{'='*70}")

# Main probability distribution
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Probability bar chart
ax1 = axes[0, 0]
states = [format(i, f'0{N_QUBITS}b') for i in range(len(results))]
colors = ['coral' if results[i] > 0.1 else 'steelblue' for i in range(len(results))]
ax1.bar(range(len(results)), results, color=colors, edgecolor='black', linewidth=0.5)
ax1.set_xlabel('State (decimal)', fontsize=10, fontweight='bold')
ax1.set_ylabel('Probability', fontsize=10, fontweight='bold')
ax1.set_title(f'{CIRCUIT_TYPE.title()} Circuit - Probability Distribution', fontsize=12, fontweight='bold')
ax1.grid(axis='y', alpha=0.3)

# Plot 2: Top states pie chart
ax2 = axes[0, 1]
threshold = 0.05
significant_probs = []
significant_labels = []
for i, prob in enumerate(results):
    if prob > threshold:
        significant_probs.append(prob)
        significant_labels.append(f"|{format(i, f'0{N_QUBITS}b')}⟩")
if sum(significant_probs) < 1.0:
    significant_probs.append(1.0 - sum(significant_probs))
    significant_labels.append('Others')
ax2.pie(significant_probs, labels=significant_labels, autopct='%1.1f%%', startangle=90)
ax2.set_title('Major States Distribution', fontsize=12, fontweight='bold')

# Plot 3: Parameter scan (if custom circuit)
ax3 = axes[1, 0]
if CIRCUIT_TYPE == "custom":
    scan_range = np.linspace(0, 2*np.pi, 30)
    max_probs = []
    for theta in scan_range:
        test_params = np.array([theta] * len(CUSTOM_PARAMS['rotation_angles']))
        test_result = custom_circuit(test_params)
        max_probs.append(np.max(test_result))
    ax3.plot(scan_range, max_probs, 'b-', linewidth=2)
    ax3.set_xlabel('Parameter Value', fontsize=10, fontweight='bold')
    ax3.set_ylabel('Max State Probability', fontsize=10, fontweight='bold')
    ax3.set_title('Parameter Sensitivity', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3)
else:
    ax3.text(0.5, 0.5, 'Parameter scan\navailable for\ncustom circuit only', 
             ha='center', va='center', fontsize=12, transform=ax3.transAxes)
    ax3.axis('off')

# Plot 4: Cumulative probability
ax4 = axes[1, 1]
sorted_probs = np.sort(results)[::-1]
cumulative = np.cumsum(sorted_probs)
ax4.plot(range(len(cumulative)), cumulative, 'g-', linewidth=2, marker='o', markersize=3)
ax4.axhline(y=0.5, color='r', linestyle='--', label='50% threshold')
ax4.axhline(y=0.9, color='orange', linestyle='--', label='90% threshold')
ax4.set_xlabel('Number of States', fontsize=10, fontweight='bold')
ax4.set_ylabel('Cumulative Probability', fontsize=10, fontweight='bold')
ax4.set_title('Cumulative Distribution', fontsize=12, fontweight='bold')
ax4.legend()
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(f'{CIRCUIT_TYPE}_variation.png', dpi=150, bbox_inches='tight')
print(f"✓ Saved: {CIRCUIT_TYPE}_variation.png")

# ========== COMPARISON WITH DIFFERENT PARAMETERS ==========
print(f"\n{'='*70}")
print("  PARAMETER COMPARISON")
print(f"{'='*70}")

if CIRCUIT_TYPE == "custom":
    print("\nTesting different parameter sets:")
    
    test_sets = [
        ("Zero", np.zeros(len(CUSTOM_PARAMS['rotation_angles']))),
        ("π/4", np.ones(len(CUSTOM_PARAMS['rotation_angles'])) * np.pi/4),
        ("π/2", np.ones(len(CUSTOM_PARAMS['rotation_angles'])) * np.pi/2),
        ("Random", np.random.uniform(0, 2*np.pi, len(CUSTOM_PARAMS['rotation_angles'])))
    ]
    
    for name, test_params in test_sets:
        test_result = custom_circuit(test_params)
        max_prob = np.max(test_result)
        max_state = format(np.argmax(test_result), f'0{N_QUBITS}b')
        entropy_test = -np.sum(test_result * np.log2(test_result + 1e-10))
        print(f"  {name:8} → max_state=|{max_state}⟩ prob={max_prob:.3f} entropy={entropy_test:.2f}")

print(f"\n{'='*70}")
print("  ✓ CUSTOM VARIATIONS COMPLETE!")
print(f"{'='*70}")
print("\n🎛️  To experiment, edit these variables at the top:")
print("  • N_QUBITS - Number of qubits (2-6)")
print("  • CIRCUIT_TYPE - 'custom', 'symmetric', 'cascade', 'random_walk'")
print("  • CUSTOM_PARAMS - Rotation angles, layers, entanglement")
print("  • SHOTS - Number of measurements")
print(f"\n📊 Generated: {CIRCUIT_TYPE}_variation.png")
print(f"{'='*70}")
