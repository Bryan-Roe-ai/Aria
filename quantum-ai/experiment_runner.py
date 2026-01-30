#!/usr/bin/env python3
"""
Quantum Circuit Experiment Runner
Automatically tests multiple combinations and compares results
"""
import pennylane as qml
import numpy as np
import matplotlib.pyplot as plt
import subprocess
import json
from pathlib import Path

print("=" * 70)
print("  QUANTUM CIRCUIT EXPERIMENT SUITE")
print("=" * 70)

# Define experiment configurations
experiments = [
    {
        'name': 'Minimal Entanglement',
        'n_qubits': 3,
        'type': 'custom',
        'params': {'rotation_angles': [0, 0, 0], 'coupling_strength': 0.1, 'layer_depth': 1, 'entanglement_type': 'linear'}
    },
    {
        'name': 'Maximum Entanglement',
        'n_qubits': 3,
        'type': 'custom',
        'params': {'rotation_angles': [np.pi/2, np.pi/2, np.pi/2], 'coupling_strength': 1.0, 'layer_depth': 3, 'entanglement_type': 'all-to-all'}
    },
    {
        'name': 'Symmetric Pattern',
        'n_qubits': 4,
        'type': 'symmetric',
        'params': {}
    },
    {
        'name': 'Information Cascade',
        'n_qubits': 4,
        'type': 'cascade',
        'params': {}
    },
    {
        'name': 'Circular vs Linear',
        'n_qubits': 3,
        'type': 'custom',
        'params': {'rotation_angles': [np.pi/4, np.pi/4, np.pi/4], 'coupling_strength': 0.7, 'layer_depth': 2, 'entanglement_type': 'circular'}
    },
    {
        'name': 'Deep Circuit',
        'n_qubits': 3,
        'type': 'custom',
        'params': {'rotation_angles': [np.pi/3, np.pi/4, np.pi/6], 'coupling_strength': 0.5, 'layer_depth': 5, 'entanglement_type': 'pyramid'}
    },
]

# Storage for results
results = []

print("\n📊 Running experiments...")
print(f"Total experiments: {len(experiments)}\n")

for i, exp in enumerate(experiments, 1):
    print(f"[{i}/{len(experiments)}] {exp['name']}")
    print(f"  Config: {exp['n_qubits']} qubits, {exp['type']} circuit")
    
    n_qubits = exp['n_qubits']
    circuit_type = exp['type']
    shots = 1000
    
    dev = qml.device('lightning.qubit', wires=n_qubits, shots=shots)
    
    # Build circuit based on type
    if circuit_type == 'custom':
        params_config = exp['params']
        
        @qml.qnode(dev)
        def circuit(params):
            layer_depth = params_config['layer_depth']
            entanglement = params_config['entanglement_type']
            coupling = params_config['coupling_strength']
            
            # Initial superposition
            for j in range(n_qubits):
                qml.Hadamard(wires=j)
            
            # Layers
            for layer in range(layer_depth):
                for j in range(n_qubits):
                    idx = (layer * n_qubits + j) % len(params)
                    qml.RY(params[idx] * coupling, wires=j)
                    qml.RZ(params[idx] * 0.5, wires=j)
                
                # Entanglement
                if entanglement == 'linear':
                    for j in range(n_qubits - 1):
                        qml.CNOT(wires=[j, j+1])
                elif entanglement == 'circular':
                    for j in range(n_qubits):
                        qml.CNOT(wires=[j, (j+1) % n_qubits])
                elif entanglement == 'all-to-all':
                    for j in range(n_qubits):
                        for k in range(j+1, n_qubits):
                            qml.CNOT(wires=[j, k])
                elif entanglement == 'pyramid':
                    step = 1
                    while step < n_qubits:
                        for j in range(0, n_qubits - step, step * 2):
                            qml.CNOT(wires=[j, j + step])
                        step *= 2
            
            return qml.probs(wires=range(n_qubits))
        
        test_params = np.array(params_config['rotation_angles'])
        probs = circuit(test_params)
    
    elif circuit_type == 'symmetric':
        @qml.qnode(dev)
        def circuit(theta):
            for j in range(n_qubits):
                qml.RY(theta, wires=j)
            for j in range(n_qubits - 1):
                qml.CNOT(wires=[j, j+1])
            for j in range(n_qubits):
                qml.RZ(theta * 0.5, wires=j)
            return qml.probs(wires=range(n_qubits))
        
        probs = circuit(np.pi/3)
    
    elif circuit_type == 'cascade':
        @qml.qnode(dev)
        def circuit(angles):
            qml.RY(angles[0], wires=0)
            for j in range(n_qubits - 1):
                qml.CNOT(wires=[j, j+1])
                if j+1 < len(angles):
                    qml.RY(angles[j+1], wires=j+1)
                qml.RZ(angles[j] * 0.3, wires=j+1)
            for j in range(n_qubits):
                qml.Hadamard(wires=j)
            return qml.probs(wires=range(n_qubits))
        
        angles = np.linspace(0, np.pi, n_qubits)
        probs = circuit(angles)
    
    # Analyze results
    max_prob = np.max(probs)
    max_state = format(np.argmax(probs), f'0{n_qubits}b')
    entropy = -np.sum(probs * np.log2(probs + 1e-10))
    max_entropy = n_qubits
    uniformity = entropy / max_entropy
    
    # Count significant states
    significant_states = np.sum(probs > 0.05)
    
    result = {
        'name': exp['name'],
        'n_qubits': n_qubits,
        'type': circuit_type,
        'max_state': max_state,
        'max_prob': max_prob,
        'entropy': entropy,
        'uniformity': uniformity,
        'significant_states': significant_states,
        'probs': probs
    }
    results.append(result)
    
    print(f"  ✓ Max state: |{max_state}⟩ ({max_prob:.1%})")
    print(f"  ✓ Uniformity: {uniformity:.1%}")
    print(f"  ✓ Significant states: {significant_states}/{2**n_qubits}")
    print()

# ========== COMPARATIVE ANALYSIS ==========
print("=" * 70)
print("  COMPARATIVE ANALYSIS")
print("=" * 70)

print("\n📊 All Experiments Summary:\n")
print(f"{'Experiment':<25} {'Qubits':<8} {'Max State':<12} {'Prob':<8} {'Uniformity':<12}")
print("-" * 70)
for r in results:
    print(f"{r['name']:<25} {r['n_qubits']:<8} |{r['max_state']}⟩{'':<5} {r['max_prob']:<8.1%} {r['uniformity']:<12.1%}")

# Find extremes
max_uniform = max(results, key=lambda x: x['uniformity'])
min_uniform = min(results, key=lambda x: x['uniformity'])
max_concentrated = max(results, key=lambda x: x['max_prob'])

print(f"\n🏆 Key Findings:")
print(f"  Most uniform: {max_uniform['name']} ({max_uniform['uniformity']:.1%})")
print(f"  Most concentrated: {max_concentrated['name']} ({max_concentrated['max_prob']:.1%} in |{max_concentrated['max_state']}⟩)")
print(f"  Least uniform: {min_uniform['name']} ({min_uniform['uniformity']:.1%})")

# ========== VISUALIZATIONS ==========
print(f"\n{'='*70}")
print("  CREATING COMPARISON VISUALIZATIONS")
print(f"{'='*70}")

fig = plt.figure(figsize=(16, 10))
gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

# Plot 1: Uniformity comparison
ax1 = fig.add_subplot(gs[0, :])
names = [r['name'] for r in results]
uniformities = [r['uniformity'] for r in results]
colors = plt.cm.viridis(np.linspace(0, 1, len(results)))
bars = ax1.barh(names, uniformities, color=colors, edgecolor='black', linewidth=1.5)
ax1.set_xlabel('Uniformity (Entropy / Max Entropy)', fontsize=11, fontweight='bold')
ax1.set_title('Experiment Uniformity Comparison', fontsize=13, fontweight='bold')
ax1.set_xlim(0, 1)
ax1.grid(axis='x', alpha=0.3)
for i, bar in enumerate(bars):
    width = bar.get_width()
    ax1.text(width + 0.02, bar.get_y() + bar.get_height()/2, 
             f'{uniformities[i]:.1%}', va='center', fontweight='bold')

# Plot 2-4: Top 3 experiments probability distributions
for idx, r in enumerate(results[:3]):
    ax = fig.add_subplot(gs[1, idx])
    states = range(len(r['probs']))
    ax.bar(states, r['probs'], color='steelblue', edgecolor='black', linewidth=0.5)
    ax.set_xlabel('State', fontsize=9)
    ax.set_ylabel('Probability', fontsize=9)
    ax.set_title(f"{r['name']}\n({r['n_qubits']} qubits)", fontsize=10, fontweight='bold')
    ax.set_ylim(0, max(r['probs']) * 1.1)
    ax.grid(axis='y', alpha=0.3)

# Plot 5-7: Bottom 3 experiments probability distributions
for idx, r in enumerate(results[3:]):
    ax = fig.add_subplot(gs[2, idx])
    states = range(len(r['probs']))
    ax.bar(states, r['probs'], color='coral', edgecolor='black', linewidth=0.5)
    ax.set_xlabel('State', fontsize=9)
    ax.set_ylabel('Probability', fontsize=9)
    ax.set_title(f"{r['name']}\n({r['n_qubits']} qubits)", fontsize=10, fontweight='bold')
    ax.set_ylim(0, max(r['probs']) * 1.1)
    ax.grid(axis='y', alpha=0.3)

plt.savefig('experiment_comparison.png', dpi=150, bbox_inches='tight')
print("✓ Saved: experiment_comparison.png")

# Side-by-side entropy comparison
fig2, ax = plt.subplots(figsize=(12, 6))
x = np.arange(len(results))
width = 0.35

entropy_vals = [r['entropy'] for r in results]
max_entropy_vals = [r['n_qubits'] for r in results]

bars1 = ax.bar(x - width/2, entropy_vals, width, label='Actual Entropy', color='steelblue', edgecolor='black', linewidth=1.5)
bars2 = ax.bar(x + width/2, max_entropy_vals, width, label='Max Possible', color='lightcoral', edgecolor='black', linewidth=1.5)

ax.set_xlabel('Experiment', fontsize=12, fontweight='bold')
ax.set_ylabel('Entropy (bits)', fontsize=12, fontweight='bold')
ax.set_title('Entropy Comparison Across Experiments', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels([r['name'] for r in results], rotation=45, ha='right')
ax.legend(fontsize=11)
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('entropy_comparison.png', dpi=150, bbox_inches='tight')
print("✓ Saved: entropy_comparison.png")

# ========== RECOMMENDATIONS ==========
print(f"\n{'='*70}")
print("  🎯 RECOMMENDATIONS FOR FURTHER EXPLORATION")
print(f"{'='*70}")

print("\n1. For Maximum Superposition:")
print(f"   → Try: {max_uniform['name']} configuration")
print(f"   → Why: Highest uniformity ({max_uniform['uniformity']:.1%}), most quantum-like")

print("\n2. For Targeted State Preparation:")
print(f"   → Try: {max_concentrated['name']} configuration")
print(f"   → Why: Can achieve {max_concentrated['max_prob']:.1%} in single state")

print("\n3. For Learning Entanglement:")
print(f"   → Compare: 'Circular vs Linear' and 'Maximum Entanglement'")
print(f"   → Why: See how entanglement patterns affect distribution")

print("\n4. For Quantum Algorithms:")
print(f"   → Start with: 'Deep Circuit' configuration")
print(f"   → Why: Good balance of layers and expressivity")

print(f"\n{'='*70}")
print("  ✓ EXPERIMENT SUITE COMPLETE!")
print(f"{'='*70}")
print("\n📁 Generated Files:")
print("  • experiment_comparison.png - All experiments side-by-side")
print("  • entropy_comparison.png - Entropy analysis")
print("\n💡 Next Steps:")
print("  • Edit custom_circuits.py with configurations above")
print("  • Try intermediate values between extremes")
print("  • Increase qubits to 5-6 for more complex behavior")
print(f"{'='*70}")
