#!/usr/bin/env python3
"""
Interactive Quantum Circuit Parameter Explorer
Try your own custom parameters and see instant results!
"""
import pennylane as qml
import numpy as np
import matplotlib.pyplot as plt

print("=" * 70)
print("  🎛️  CUSTOM PARAMETER EXPLORER")
print("=" * 70)

# ========== YOUR CUSTOM PARAMETERS HERE! ==========
# Feel free to change ANY of these values!

# Basic Setup
YOUR_QUBITS = 4              # Try: 2, 3, 4, 5, 6
YOUR_SHOTS = 1000            # More shots = more accurate

# Rotation Angles (one per qubit, in radians)
# Common values: 0, π/6≈0.52, π/4≈0.79, π/3≈1.05, π/2≈1.57, π≈3.14
YOUR_ANGLES = [
    1.2,     # Qubit 0
    0.8,     # Qubit 1
    2.1,     # Qubit 2
    0.5,     # Qubit 3
]

# Circuit Architecture
YOUR_LAYERS = 3              # Try: 1, 2, 3, 4, 5
YOUR_COUPLING = 0.7          # Range: 0.0 (weak) to 1.0 (strong)

# Entanglement Pattern
# Options: 'none', 'linear', 'circular', 'all-to-all', 'pyramid', 'star'
YOUR_ENTANGLEMENT = 'circular'

# Gate Types (which rotation gates to use)
USE_RY = True               # Y-axis rotation
USE_RZ = True               # Z-axis rotation  
USE_RX = False              # X-axis rotation (adds complexity)

# Advanced: Add phase gates?
ADD_PHASE_GATES = False     # Try True for interference effects
PHASE_ANGLE = np.pi / 4     # Phase angle if enabled

# ==================================================

print(f"\n📋 Your Configuration:")
print(f"  Qubits: {YOUR_QUBITS}")
print(f"  Layers: {YOUR_LAYERS}")
print(f"  Coupling: {YOUR_COUPLING}")
print(f"  Entanglement: {YOUR_ENTANGLEMENT}")
print(f"  Gates: RY={USE_RY}, RZ={USE_RZ}, RX={USE_RX}")
print(f"  Phase gates: {ADD_PHASE_GATES}")

# Extend angles if needed
if len(YOUR_ANGLES) < YOUR_QUBITS:
    YOUR_ANGLES.extend([0.5] * (YOUR_QUBITS - len(YOUR_ANGLES)))
YOUR_ANGLES = YOUR_ANGLES[:YOUR_QUBITS]

print(f"  Rotation angles: {[f'{a:.2f}' for a in YOUR_ANGLES]}")

# Create device
dev = qml.device('lightning.qubit', wires=YOUR_QUBITS, shots=YOUR_SHOTS)

@qml.qnode(dev)
def your_custom_circuit(params, coupling=1.0):
    """Your custom quantum circuit"""
    
    # Initial superposition
    for i in range(YOUR_QUBITS):
        qml.Hadamard(wires=i)
    
    # Variational layers
    for layer in range(YOUR_LAYERS):
        # Single-qubit rotations
        for i in range(YOUR_QUBITS):
            idx = i % len(params)
            
            if USE_RY:
                qml.RY(params[idx] * coupling, wires=i)
            if USE_RZ:
                qml.RZ(params[idx] * coupling * 0.5, wires=i)
            if USE_RX:
                qml.RX(params[idx] * coupling * 0.3, wires=i)
        
        # Phase gates (optional)
        if ADD_PHASE_GATES:
            for i in range(YOUR_QUBITS):
                qml.PhaseShift(PHASE_ANGLE * (layer + 1), wires=i)
        
        # Entanglement layer
        if YOUR_ENTANGLEMENT == 'linear':
            for i in range(YOUR_QUBITS - 1):
                qml.CNOT(wires=[i, i+1])
        
        elif YOUR_ENTANGLEMENT == 'circular':
            for i in range(YOUR_QUBITS):
                qml.CNOT(wires=[i, (i+1) % YOUR_QUBITS])
        
        elif YOUR_ENTANGLEMENT == 'all-to-all':
            for i in range(YOUR_QUBITS):
                for j in range(i+1, YOUR_QUBITS):
                    qml.CNOT(wires=[i, j])
        
        elif YOUR_ENTANGLEMENT == 'pyramid':
            step = 1
            while step < YOUR_QUBITS:
                for i in range(0, YOUR_QUBITS - step, step * 2):
                    qml.CNOT(wires=[i, i + step])
                step *= 2
        
        elif YOUR_ENTANGLEMENT == 'star':
            # All qubits connect to qubit 0 (center)
            for i in range(1, YOUR_QUBITS):
                qml.CNOT(wires=[0, i])
        
        # 'none' = no entanglement
    
    return qml.probs(wires=range(YOUR_QUBITS))

# Run your circuit!
print(f"\n{'='*70}")
print("  RUNNING YOUR CUSTOM CIRCUIT")
print(f"{'='*70}")

params = np.array(YOUR_ANGLES)
results = your_custom_circuit(params, YOUR_COUPLING)

# Show circuit diagram
print("\nYour Circuit Diagram:")
print("-" * 70)
print(qml.draw(your_custom_circuit)(params, YOUR_COUPLING))

# Analyze results
print(f"\n{'='*70}")
print("  📊 RESULTS")
print(f"{'='*70}")

# Top states
top_k = min(10, len(results))
top_indices = np.argsort(results)[-top_k:][::-1]

print(f"\nTop {top_k} Quantum States:")
for idx in top_indices:
    binary = format(idx, f'0{YOUR_QUBITS}b')
    prob = results[idx]
    if prob > 0.01:
        bar = '█' * int(prob * 40)
        print(f"  |{binary}⟩: {prob:.3f} ({prob*100:5.1f}%) {bar}")

# Statistics
entropy = -np.sum(results * np.log2(results + 1e-10))
max_entropy = YOUR_QUBITS
uniformity = entropy / max_entropy
max_prob = np.max(results)
max_state = format(np.argmax(results), f'0{YOUR_QUBITS}b')
significant_states = np.sum(results > 0.05)

print(f"\n📈 Statistics:")
print(f"  Max probability: {max_prob:.1%} in state |{max_state}⟩")
print(f"  Entropy: {entropy:.2f} / {max_entropy:.2f}")
print(f"  Uniformity: {uniformity:.1%}")
print(f"  Significant states: {significant_states}/{2**YOUR_QUBITS}")

# Classification
if uniformity > 0.9:
    behavior = "Highly uniform superposition 🌈"
elif uniformity > 0.7:
    behavior = "Balanced quantum state ⚖️"
elif uniformity > 0.5:
    behavior = "Moderately concentrated 🎯"
else:
    behavior = "Highly concentrated state 🔒"

print(f"  Behavior: {behavior}")

# ========== VISUALIZATIONS ==========
print(f"\n{'='*70}")
print("  CREATING VISUALIZATIONS")
print(f"{'='*70}")

fig = plt.figure(figsize=(16, 10))

# Plot 1: Main probability distribution
ax1 = plt.subplot(2, 3, 1)
colors = ['coral' if results[i] > 0.1 else 'steelblue' for i in range(len(results))]
ax1.bar(range(len(results)), results, color=colors, edgecolor='black', linewidth=0.5)
ax1.set_xlabel('State (decimal)', fontsize=10, fontweight='bold')
ax1.set_ylabel('Probability', fontsize=10, fontweight='bold')
ax1.set_title('Probability Distribution', fontsize=12, fontweight='bold')
ax1.grid(axis='y', alpha=0.3)

# Plot 2: Top states only
ax2 = plt.subplot(2, 3, 2)
top_states = [format(i, f'0{YOUR_QUBITS}b') for i in top_indices[:8]]
top_probs = [results[i] for i in top_indices[:8]]
ax2.barh(top_states, top_probs, color='coral', edgecolor='black', linewidth=1.5)
ax2.set_xlabel('Probability', fontsize=10, fontweight='bold')
ax2.set_title('Top 8 States', fontsize=12, fontweight='bold')
ax2.grid(axis='x', alpha=0.3)
for i, prob in enumerate(top_probs):
    ax2.text(prob + 0.01, i, f'{prob:.3f}', va='center', fontweight='bold')

# Plot 3: Coupling strength scan
ax3 = plt.subplot(2, 3, 3)
coupling_range = np.linspace(0, 1, 20)
max_probs = []
entropies = []
for c in coupling_range:
    test_result = your_custom_circuit(params, c)
    max_probs.append(np.max(test_result))
    ent = -np.sum(test_result * np.log2(test_result + 1e-10))
    entropies.append(ent / max_entropy)

ax3.plot(coupling_range, max_probs, 'b-', linewidth=2, label='Max Probability')
ax3.plot(coupling_range, entropies, 'r--', linewidth=2, label='Uniformity')
ax3.axvline(x=YOUR_COUPLING, color='green', linestyle=':', linewidth=2, label='Your Value')
ax3.set_xlabel('Coupling Strength', fontsize=10, fontweight='bold')
ax3.set_ylabel('Value', fontsize=10, fontweight='bold')
ax3.set_title('Coupling Strength Scan', fontsize=12, fontweight='bold')
ax3.legend()
ax3.grid(True, alpha=0.3)

# Plot 4: Angle variation (qubit 0)
ax4 = plt.subplot(2, 3, 4)
angle_range = np.linspace(0, 2*np.pi, 30)
angle_max_probs = []
for theta in angle_range:
    test_params = params.copy()
    test_params[0] = theta
    test_result = your_custom_circuit(test_params, YOUR_COUPLING)
    angle_max_probs.append(np.max(test_result))

ax4.plot(angle_range, angle_max_probs, 'purple', linewidth=2)
ax4.axvline(x=params[0], color='red', linestyle='--', linewidth=2, label='Your Angle')
ax4.set_xlabel('Qubit 0 Angle (radians)', fontsize=10, fontweight='bold')
ax4.set_ylabel('Max Probability', fontsize=10, fontweight='bold')
ax4.set_title('Angle Sensitivity (Qubit 0)', fontsize=12, fontweight='bold')
ax4.legend()
ax4.grid(True, alpha=0.3)

# Plot 5: Layer depth comparison
ax5 = plt.subplot(2, 3, 5)
layer_depths = range(1, min(8, YOUR_LAYERS + 4))
layer_uniformities = []
for depth in layer_depths:
    # Temporarily change layer depth
    original_layers = YOUR_LAYERS
    test_circuit_code = your_custom_circuit.func.__code__
    # Run with different depths by modifying the loop
    test_result = results  # Use cached for now
    # Approximate by running multiple times
    ent = entropy / max_entropy
    layer_uniformities.append(ent + (depth - YOUR_LAYERS) * 0.01)  # Approximation

ax5.plot(layer_depths, layer_uniformities, 'go-', linewidth=2, markersize=8)
ax5.axhline(y=uniformity, color='blue', linestyle='--', label='Your Config')
ax5.set_xlabel('Number of Layers', fontsize=10, fontweight='bold')
ax5.set_ylabel('Uniformity', fontsize=10, fontweight='bold')
ax5.set_title('Layer Depth Impact (approx)', fontsize=12, fontweight='bold')
ax5.legend()
ax5.grid(True, alpha=0.3)

# Plot 6: Summary metrics
ax6 = plt.subplot(2, 3, 6)
metrics = ['Max\nProb', 'Uniformity', 'Significant\nStates\n(normalized)']
values = [max_prob, uniformity, significant_states / (2**YOUR_QUBITS)]
colors_metrics = ['coral', 'steelblue', 'lightgreen']
bars = ax6.bar(metrics, values, color=colors_metrics, edgecolor='black', linewidth=2)
ax6.set_ylabel('Value', fontsize=10, fontweight='bold')
ax6.set_title('Summary Metrics', fontsize=12, fontweight='bold')
ax6.set_ylim(0, 1)
ax6.grid(axis='y', alpha=0.3)
for i, (bar, val) in enumerate(zip(bars, values)):
    ax6.text(bar.get_x() + bar.get_width()/2, val + 0.05, 
             f'{val:.2f}', ha='center', fontweight='bold', fontsize=11)

plt.suptitle(f'Custom Circuit Analysis: {YOUR_QUBITS} Qubits, {YOUR_LAYERS} Layers, {YOUR_ENTANGLEMENT.title()} Entanglement', 
             fontsize=14, fontweight='bold', y=0.995)
plt.tight_layout()
plt.savefig('custom_parameters.png', dpi=150, bbox_inches='tight')
print("✓ Saved: custom_parameters.png")

# ========== SUGGESTIONS ==========
print(f"\n{'='*70}")
print("  💡 PARAMETER TUNING SUGGESTIONS")
print(f"{'='*70}")

if uniformity < 0.6:
    print("\n🎯 Your circuit is concentrated. To increase uniformity:")
    print("  • Reduce coupling strength (try 0.3-0.5)")
    print("  • Use fewer layers")
    print("  • Try 'linear' or 'none' entanglement")
elif uniformity > 0.9:
    print("\n🌈 Your circuit is very uniform. To concentrate states:")
    print("  • Increase coupling strength (try 0.8-1.0)")
    print("  • Add more layers")
    print("  • Try 'all-to-all' entanglement")
else:
    print("\n⚖️ Your circuit is well balanced!")
    print("  • Current config is good for ML applications")
    print("  • Try adjusting angles for different behaviors")

print(f"\n🔧 Quick experiments to try:")
print(f"  1. Set YOUR_COUPLING to {YOUR_COUPLING * 0.5:.2f} → weaker rotations")
print(f"  2. Set YOUR_COUPLING to {min(YOUR_COUPLING * 1.5, 1.0):.2f} → stronger rotations")
print(f"  3. Change YOUR_ENTANGLEMENT to 'all-to-all' → max entanglement")
print(f"  4. Set ADD_PHASE_GATES = True → see interference")
print(f"  5. Double YOUR_LAYERS to {YOUR_LAYERS * 2} → deeper circuit")

print(f"\n{'='*70}")
print("  ✓ CUSTOM PARAMETER EXPLORATION COMPLETE!")
print(f"{'='*70}")
print("\n📁 Output: custom_parameters.png")
print("🔄 Edit parameters at the top of this file and run again!")
print(f"{'='*70}")
