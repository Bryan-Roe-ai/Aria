#!/usr/bin/env python3
"""
Try All Parameter Combinations
Automatically test multiple configurations and compare results
"""
import pennylane as qml
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

print("=" * 70)
print("  🚀 TRYING ALL PARAMETER COMBINATIONS")
print("=" * 70)

# Define all configurations to test
configurations = [
    {
        'name': '1. Original (Balanced)',
        'qubits': 4,
        'angles': [1.2, 0.8, 2.1, 0.5],
        'coupling': 0.7,
        'layers': 3,
        'entanglement': 'circular',
        'phase_gates': False,
        'gates': {'RY': True, 'RZ': True, 'RX': False}
    },
    {
        'name': '2. Weak Coupling',
        'qubits': 4,
        'angles': [1.2, 0.8, 2.1, 0.5],
        'coupling': 0.35,
        'layers': 3,
        'entanglement': 'circular',
        'phase_gates': False,
        'gates': {'RY': True, 'RZ': True, 'RX': False}
    },
    {
        'name': '3. Strong Coupling',
        'qubits': 4,
        'angles': [1.2, 0.8, 2.1, 0.5],
        'coupling': 1.0,
        'layers': 3,
        'entanglement': 'circular',
        'phase_gates': False,
        'gates': {'RY': True, 'RZ': True, 'RX': False}
    },
    {
        'name': '4. All-to-All Entanglement',
        'qubits': 4,
        'angles': [1.2, 0.8, 2.1, 0.5],
        'coupling': 0.7,
        'layers': 3,
        'entanglement': 'all-to-all',
        'phase_gates': False,
        'gates': {'RY': True, 'RZ': True, 'RX': False}
    },
    {
        'name': '5. With Phase Gates',
        'qubits': 4,
        'angles': [1.2, 0.8, 2.1, 0.5],
        'coupling': 0.7,
        'layers': 3,
        'entanglement': 'circular',
        'phase_gates': True,
        'gates': {'RY': True, 'RZ': True, 'RX': False}
    },
    {
        'name': '6. Deep Circuit (6 layers)',
        'qubits': 4,
        'angles': [1.2, 0.8, 2.1, 0.5],
        'coupling': 0.7,
        'layers': 6,
        'entanglement': 'circular',
        'phase_gates': False,
        'gates': {'RY': True, 'RZ': True, 'RX': False}
    },
    {
        'name': '7. Standard Angles',
        'qubits': 4,
        'angles': [np.pi/2, np.pi/4, np.pi/3, np.pi/6],
        'coupling': 0.7,
        'layers': 3,
        'entanglement': 'circular',
        'phase_gates': False,
        'gates': {'RY': True, 'RZ': True, 'RX': False}
    },
    {
        'name': '8. All Gates Enabled',
        'qubits': 4,
        'angles': [1.2, 0.8, 2.1, 0.5],
        'coupling': 0.7,
        'layers': 3,
        'entanglement': 'circular',
        'phase_gates': False,
        'gates': {'RY': True, 'RZ': True, 'RX': True}
    },
    {
        'name': '9. Linear Entanglement',
        'qubits': 4,
        'angles': [1.2, 0.8, 2.1, 0.5],
        'coupling': 0.7,
        'layers': 3,
        'entanglement': 'linear',
        'phase_gates': False,
        'gates': {'RY': True, 'RZ': True, 'RX': False}
    },
    {
        'name': '10. Maximum Everything',
        'qubits': 4,
        'angles': [np.pi, np.pi, np.pi, np.pi],
        'coupling': 1.0,
        'layers': 5,
        'entanglement': 'all-to-all',
        'phase_gates': True,
        'gates': {'RY': True, 'RZ': True, 'RX': True}
    },
]

results = []

print(f"\nTesting {len(configurations)} configurations...\n")

def build_and_run_circuit(config):
    """Build and execute a circuit with given configuration"""
    n_qubits = config['qubits']
    angles = config['angles'][:n_qubits]
    coupling = config['coupling']
    layers = config['layers']
    entanglement = config['entanglement']
    phase_gates = config['phase_gates']
    gates = config['gates']
    
    dev = qml.device('lightning.qubit', wires=n_qubits, shots=1000)
    
    @qml.qnode(dev)
    def circuit(params):
        # Initial superposition
        for i in range(n_qubits):
            qml.Hadamard(wires=i)
        
        # Variational layers
        for layer in range(layers):
            # Rotations
            for i in range(n_qubits):
                idx = i % len(params)
                if gates['RY']:
                    qml.RY(params[idx] * coupling, wires=i)
                if gates['RZ']:
                    qml.RZ(params[idx] * coupling * 0.5, wires=i)
                if gates['RX']:
                    qml.RX(params[idx] * coupling * 0.3, wires=i)
            
            # Phase gates
            if phase_gates:
                for i in range(n_qubits):
                    qml.PhaseShift(np.pi/4 * (layer + 1), wires=i)
            
            # Entanglement
            if entanglement == 'linear':
                for i in range(n_qubits - 1):
                    qml.CNOT(wires=[i, i+1])
            elif entanglement == 'circular':
                for i in range(n_qubits):
                    qml.CNOT(wires=[i, (i+1) % n_qubits])
            elif entanglement == 'all-to-all':
                for i in range(n_qubits):
                    for j in range(i+1, n_qubits):
                        qml.CNOT(wires=[i, j])
            elif entanglement == 'pyramid':
                step = 1
                while step < n_qubits:
                    for i in range(0, n_qubits - step, step * 2):
                        qml.CNOT(wires=[i, i + step])
                    step *= 2
        
        return qml.probs(wires=range(n_qubits))
    
    return circuit(np.array(angles))

# Run all configurations
for i, config in enumerate(configurations, 1):
    print(f"[{i}/{len(configurations)}] {config['name']}")
    
    try:
        probs = build_and_run_circuit(config)
        
        # Analyze
        max_prob = np.max(probs)
        max_state = format(np.argmax(probs), f"0{config['qubits']}b")
        entropy = -np.sum(probs * np.log2(probs + 1e-10))
        max_entropy = config['qubits']
        uniformity = entropy / max_entropy
        significant = np.sum(probs > 0.05)
        
        result = {
            'config': config,
            'probs': probs,
            'max_prob': max_prob,
            'max_state': max_state,
            'entropy': entropy,
            'uniformity': uniformity,
            'significant_states': significant
        }
        results.append(result)
        
        print(f"  ✓ Max: |{max_state}⟩ ({max_prob:.1%}), Uniformity: {uniformity:.1%}, Significant: {significant}/{2**config['qubits']}")
    
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    print()

# ========== COMPARATIVE ANALYSIS ==========
print("=" * 70)
print("  📊 COMPARATIVE ANALYSIS")
print("=" * 70)

print(f"\n{'Configuration':<30} {'Max Prob':<12} {'Uniformity':<12} {'Significant':<12}")
print("-" * 70)
for r in results:
    name = r['config']['name']
    print(f"{name:<30} {r['max_prob']:<12.1%} {r['uniformity']:<12.1%} {r['significant_states']}/{2**r['config']['qubits']:<10}")

# Rankings
print(f"\n🏆 Rankings:")
most_uniform = max(results, key=lambda x: x['uniformity'])
most_concentrated = max(results, key=lambda x: x['max_prob'])
most_distributed = max(results, key=lambda x: x['significant_states'])

print(f"\n  Most Uniform: {most_uniform['config']['name']}")
print(f"    → {most_uniform['uniformity']:.1%} uniformity")

print(f"\n  Most Concentrated: {most_concentrated['config']['name']}")
print(f"    → {most_concentrated['max_prob']:.1%} in state |{most_concentrated['max_state']}⟩")

print(f"\n  Most Distributed: {most_distributed['config']['name']}")
print(f"    → {most_distributed['significant_states']} significant states")

# ========== VISUALIZATIONS ==========
print(f"\n{'='*70}")
print("  CREATING COMPREHENSIVE VISUALIZATIONS")
print(f"{'='*70}")

# Figure 1: Comparison dashboard
fig1 = plt.figure(figsize=(20, 12))
gs = GridSpec(4, 3, figure=fig1, hspace=0.4, wspace=0.3)

# Plot 1: Uniformity comparison
ax1 = fig1.add_subplot(gs[0, :])
names = [r['config']['name'] for r in results]
uniformities = [r['uniformity'] for r in results]
colors = plt.cm.plasma(np.linspace(0, 1, len(results)))
bars = ax1.barh(range(len(names)), uniformities, color=colors, edgecolor='black', linewidth=1.5)
ax1.set_yticks(range(len(names)))
ax1.set_yticklabels(names)
ax1.set_xlabel('Uniformity', fontsize=12, fontweight='bold')
ax1.set_title('Uniformity Comparison Across All Configurations', fontsize=14, fontweight='bold')
ax1.set_xlim(0, 1)
ax1.grid(axis='x', alpha=0.3)
for i, (bar, val) in enumerate(zip(bars, uniformities)):
    ax1.text(val + 0.02, bar.get_y() + bar.get_height()/2, f'{val:.1%}', va='center', fontweight='bold')

# Plots 2-10: Individual probability distributions
for idx, r in enumerate(results[:9]):  # Only first 9 fit in grid
    row = (idx + 3) // 3
    col = (idx + 3) % 3
    ax = fig1.add_subplot(gs[row, col])
    
    probs = r['probs']
    ax.bar(range(len(probs)), probs, color='steelblue', edgecolor='black', linewidth=0.5, alpha=0.7)
    ax.set_xlabel('State', fontsize=8)
    ax.set_ylabel('Prob', fontsize=8)
    ax.set_title(f"{r['config']['name']}\nU={r['uniformity']:.1%}", fontsize=9, fontweight='bold')
    ax.tick_params(labelsize=7)
    ax.set_ylim(0, max(probs) * 1.1)

plt.savefig('all_configurations_comparison.png', dpi=150, bbox_inches='tight')
print("✓ Saved: all_configurations_comparison.png")

# Figure 2: Metrics comparison
fig2, axes = plt.subplots(2, 2, figsize=(14, 10))

# Max probability comparison
ax = axes[0, 0]
max_probs = [r['max_prob'] for r in results]
ax.plot(range(len(results)), max_probs, 'o-', linewidth=2, markersize=10, color='coral')
ax.set_xticks(range(len(results)))
ax.set_xticklabels(range(1, len(results)+1))
ax.set_xlabel('Configuration #', fontsize=11, fontweight='bold')
ax.set_ylabel('Max Probability', fontsize=11, fontweight='bold')
ax.set_title('Maximum State Probability', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3)

# Entropy comparison
ax = axes[0, 1]
entropies = [r['entropy'] for r in results]
max_entropies = [r['config']['qubits'] for r in results]
x = np.arange(len(results))
width = 0.35
ax.bar(x - width/2, entropies, width, label='Actual', color='steelblue', edgecolor='black')
ax.bar(x + width/2, max_entropies, width, label='Maximum', color='lightcoral', edgecolor='black')
ax.set_xlabel('Configuration #', fontsize=11, fontweight='bold')
ax.set_ylabel('Entropy (bits)', fontsize=11, fontweight='bold')
ax.set_title('Entropy Comparison', fontsize=12, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(range(1, len(results)+1))
ax.legend()
ax.grid(axis='y', alpha=0.3)

# Significant states
ax = axes[1, 0]
significant = [r['significant_states'] for r in results]
ax.bar(range(len(results)), significant, color='lightgreen', edgecolor='black', linewidth=1.5)
ax.set_xlabel('Configuration #', fontsize=11, fontweight='bold')
ax.set_ylabel('Number of States > 5%', fontsize=11, fontweight='bold')
ax.set_title('Significant States Count', fontsize=12, fontweight='bold')
ax.set_xticks(range(len(results)))
ax.set_xticklabels(range(1, len(results)+1))
ax.grid(axis='y', alpha=0.3)

# Parameter impact (coupling strength)
ax = axes[1, 1]
couplings = [r['config']['coupling'] for r in results]
ax.scatter(couplings, uniformities, s=200, c=range(len(results)), cmap='viridis', edgecolor='black', linewidth=2)
ax.set_xlabel('Coupling Strength', fontsize=11, fontweight='bold')
ax.set_ylabel('Uniformity', fontsize=11, fontweight='bold')
ax.set_title('Coupling vs Uniformity', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3)
for i, (c, u) in enumerate(zip(couplings, uniformities)):
    ax.annotate(str(i+1), (c, u), fontsize=8, fontweight='bold', ha='center', va='center')

plt.tight_layout()
plt.savefig('metrics_comparison.png', dpi=150, bbox_inches='tight')
print("✓ Saved: metrics_comparison.png")

# Figure 3: Configuration feature heatmap
fig3, ax = plt.subplots(figsize=(14, 8))

# Create feature matrix
features = []
feature_names = ['Coupling', 'Layers', 'Uniformity', 'Max Prob', 'Entropy', 'Significant']
for r in results:
    features.append([
        r['config']['coupling'],
        r['config']['layers'] / 6,  # Normalize
        r['uniformity'],
        r['max_prob'],
        r['entropy'] / r['config']['qubits'],  # Normalize
        r['significant_states'] / 16  # Normalize
    ])

im = ax.imshow(features, cmap='RdYlGn', aspect='auto')
ax.set_xticks(range(len(feature_names)))
ax.set_xticklabels(feature_names, fontsize=11, fontweight='bold')
ax.set_yticks(range(len(results)))
ax.set_yticklabels([r['config']['name'] for r in results], fontsize=10)
ax.set_title('Configuration Feature Heatmap (Normalized)', fontsize=14, fontweight='bold')

# Add colorbar
cbar = plt.colorbar(im, ax=ax)
cbar.set_label('Normalized Value', fontsize=11, fontweight='bold')

# Add values
for i in range(len(results)):
    for j in range(len(feature_names)):
        text = ax.text(j, i, f'{features[i][j]:.2f}', ha='center', va='center', 
                      color='white' if features[i][j] < 0.5 else 'black', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig('feature_heatmap.png', dpi=150, bbox_inches='tight')
print("✓ Saved: feature_heatmap.png")

# ========== RECOMMENDATIONS ==========
print(f"\n{'='*70}")
print("  🎯 KEY INSIGHTS & RECOMMENDATIONS")
print(f"{'='*70}")

print("\n📈 What We Learned:\n")

# Group by behavior
high_uniform = [r for r in results if r['uniformity'] > 0.85]
high_concentrated = [r for r in results if r['max_prob'] > 0.25]
balanced = [r for r in results if 0.7 <= r['uniformity'] <= 0.85]

print(f"High Uniformity Configs ({len(high_uniform)}):")
for r in high_uniform[:3]:
    print(f"  • {r['config']['name']}: {r['uniformity']:.1%}")

print(f"\nHigh Concentration Configs ({len(high_concentrated)}):")
for r in high_concentrated[:3]:
    print(f"  • {r['config']['name']}: {r['max_prob']:.1%} in |{r['max_state']}⟩")

print(f"\nBalanced Configs ({len(balanced)}):")
for r in balanced[:3]:
    print(f"  • {r['config']['name']}: {r['uniformity']:.1%} uniformity")

print("\n💡 Best Use Cases:")
print(f"\n  For Quantum ML:")
print(f"    → {balanced[0]['config']['name'] if balanced else results[0]['config']['name']}")
print(f"    → Good expressivity without over-concentration")

print(f"\n  For State Preparation:")
print(f"    → {most_concentrated['config']['name']}")
print(f"    → Can target specific quantum states")

print(f"\n  For Quantum Randomness:")
print(f"    → {most_uniform['config']['name']}")
print(f"    → Maximum superposition")

print(f"\n{'='*70}")
print("  ✓ ALL CONFIGURATIONS TESTED!")
print(f"{'='*70}")
print("\n📁 Generated Files:")
print("  • all_configurations_comparison.png - Complete overview")
print("  • metrics_comparison.png - Detailed metrics")
print("  • feature_heatmap.png - Configuration features")
print(f"\n🎉 Tested {len(results)} configurations successfully!")
print(f"{'='*70}")
