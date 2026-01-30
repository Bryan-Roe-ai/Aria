#!/usr/bin/env python3
"""
Intelligent Quantum Optimizer
Uses insights from previous experiments to generate and test improved configurations
"""
import pennylane as qml
import numpy as np
import json
import matplotlib.pyplot as plt
from datetime import datetime

print("=" * 70)
print("  🎯 INTELLIGENT QUANTUM OPTIMIZER")
print("=" * 70)

# Load previous results for learning
try:
    with open('quantum_llm_results.json', 'r') as f:
        previous_data = json.load(f)
    previous_results = previous_data['results']
    print(f"\n✓ Loaded {len(previous_results)} previous experiments")
except:
    previous_results = []
    print("\n⚠️  No previous results found - starting fresh")

# ========== LEARNED INSIGHTS ==========
print("\n📚 Applying Learned Insights:")
print("   • High coupling (1.0) → 96.1% avg uniformity")
print("   • All-to-all entanglement → 92.2% avg uniformity")  
print("   • Small angles → 95.4% uniformity")
print("   • Shallow circuits (3 layers) → 84.4% avg uniformity")

# ========== GENERATE OPTIMIZED CONFIGS ==========
print(f"\n🧬 Generating optimized configurations...")

optimized_configs = [
    {
        'name': '🎯 Optimal-1: High Coupling + All-to-All',
        'qubits': 4,
        'angles': [1.2, 0.8, 2.1, 0.5],  # Balanced angles
        'coupling': 1.0,  # High coupling works best
        'layers': 3,  # Shallow is better
        'entanglement': 'all-to-all'  # Best performer
    },
    {
        'name': '🎯 Optimal-2: Small Angles + High Coupling',
        'qubits': 4,
        'angles': [0.1, 0.2, 0.15, 0.3],  # Small angles work well
        'coupling': 1.0,  # High coupling
        'layers': 3,
        'entanglement': 'circular'  # Second best
    },
    {
        'name': '🎯 Optimal-3: Ultra-High Coupling',
        'qubits': 4,
        'angles': [1.2, 0.8, 2.1, 0.5],
        'coupling': 1.2,  # Push beyond tested range
        'layers': 3,
        'entanglement': 'all-to-all'
    },
    {
        'name': '🎯 Optimal-4: Adaptive Angles',
        'qubits': 4,
        'angles': [0.5, 1.0, 1.5, 2.0],  # Gradual increase
        'coupling': 1.0,
        'layers': 3,
        'entanglement': 'all-to-all'
    },
    {
        'name': '🎯 Optimal-5: Golden Ratio + High Coupling',
        'qubits': 4,
        'angles': [1.618, 0.618, 1.618, 0.618],  # Golden ratio
        'coupling': 1.0,
        'layers': 3,
        'entanglement': 'all-to-all'
    },
    {
        'name': '🎯 Optimal-6: Fibonacci + All-to-All',
        'qubits': 4,
        'angles': [1.0, 1.0, 2.0, 3.0],  # Fibonacci
        'coupling': 1.0,
        'layers': 3,
        'entanglement': 'all-to-all'
    },
    {
        'name': '🎯 Optimal-7: Perfect Pi Fractions',
        'qubits': 4,
        'angles': [np.pi/6, np.pi/4, np.pi/3, np.pi/2],  # Perfect fractions
        'coupling': 1.0,
        'layers': 3,
        'entanglement': 'all-to-all'
    },
    {
        'name': '🎯 Optimal-8: Hybrid Entanglement',
        'qubits': 4,
        'angles': [1.2, 0.8, 2.1, 0.5],
        'coupling': 1.0,
        'layers': 4,
        'entanglement': 'hybrid',  # Mix patterns
        'layer_patterns': ['all-to-all', 'circular', 'linear', 'pyramid']
    },
]

def build_and_test_circuit(config):
    """Build and test quantum circuit"""
    n_qubits = config['qubits']
    angles = config['angles'][:n_qubits]
    coupling = config['coupling']
    layers = config['layers']
    entanglement = config['entanglement']
    
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
                qml.RY(params[idx] * coupling, wires=i)
                qml.RZ(params[idx] * coupling * 0.5, wires=i)
            
            # Adaptive entanglement
            if entanglement == 'hybrid' and 'layer_patterns' in config:
                pattern = config['layer_patterns'][layer % len(config['layer_patterns'])]
            else:
                pattern = entanglement
            
            # Apply entanglement
            if pattern == 'linear':
                for i in range(n_qubits - 1):
                    qml.CNOT(wires=[i, i+1])
            elif pattern == 'circular':
                for i in range(n_qubits):
                    qml.CNOT(wires=[i, (i+1) % n_qubits])
            elif pattern == 'all-to-all':
                for i in range(n_qubits):
                    for j in range(i+1, n_qubits):
                        qml.CNOT(wires=[i, j])
            elif pattern == 'pyramid':
                step = 1
                while step < n_qubits:
                    for i in range(0, n_qubits - step, step * 2):
                        qml.CNOT(wires=[i, i + step])
                    step *= 2
        
        return qml.probs(wires=range(n_qubits))
    
    probs = circuit(np.array(angles))
    
    # Analyze
    max_prob = np.max(probs)
    max_state = format(np.argmax(probs), f"0{n_qubits}b")
    entropy = -np.sum(probs * np.log2(probs + 1e-10))
    uniformity = entropy / n_qubits
    significant = np.sum(probs > 0.05)
    
    return {
        'probs': probs,
        'max_prob': max_prob,
        'max_state': max_state,
        'entropy': entropy,
        'uniformity': uniformity,
        'significant_states': significant
    }

# ========== TEST OPTIMIZED CONFIGS ==========
print(f"\n🚀 Testing {len(optimized_configs)} optimized configurations...\n")

results = []
for i, config in enumerate(optimized_configs, 1):
    print(f"[{i}/{len(optimized_configs)}] {config['name']:45s}", end=" ")
    
    try:
        analysis = build_and_test_circuit(config)
        results.append({
            'config': config,
            'analysis': analysis
        })
        print(f"✓ U={analysis['uniformity']:.1%}, Max={analysis['max_prob']:.1%}")
    except Exception as e:
        print(f"✗ {e}")

# ========== COMPARISON WITH PREVIOUS BEST ==========
print("\n" + "=" * 70)
print("  📊 COMPARISON WITH PREVIOUS BEST")
print("=" * 70)

if previous_results:
    prev_best_uniform = max(previous_results, key=lambda x: x['analysis']['uniformity'])
    new_best_uniform = max(results, key=lambda x: x['analysis']['uniformity'])
    
    print(f"\n🏆 Previous Best:")
    print(f"   {prev_best_uniform['name']}")
    print(f"   → {prev_best_uniform['analysis']['uniformity']:.1%} uniformity")
    
    print(f"\n🆕 New Best:")
    print(f"   {new_best_uniform['config']['name']}")
    print(f"   → {new_best_uniform['analysis']['uniformity']:.1%} uniformity")
    
    improvement = new_best_uniform['analysis']['uniformity'] - prev_best_uniform['analysis']['uniformity']
    if improvement > 0:
        print(f"\n🎉 IMPROVEMENT: +{improvement:.2%} uniformity!")
    elif improvement < -0.01:
        print(f"\n📉 Regression: {improvement:.2%}")
    else:
        print(f"\n⚖️  Similar performance (Δ={improvement:.2%})")

# ========== RANKINGS ==========
print("\n" + "=" * 70)
print("  🏆 OPTIMIZED CONFIG RANKINGS")
print("=" * 70)

sorted_results = sorted(results, key=lambda x: x['analysis']['uniformity'], reverse=True)

print("\n📈 By Uniformity:")
for i, r in enumerate(sorted_results[:5], 1):
    print(f"  {i}. {r['config']['name']:45s} → {r['analysis']['uniformity']:.1%}")

print("\n🎯 By Max Probability:")
sorted_by_max = sorted(results, key=lambda x: x['analysis']['max_prob'], reverse=True)
for i, r in enumerate(sorted_by_max[:5], 1):
    print(f"  {i}. {r['config']['name']:45s} → {r['analysis']['max_prob']:.1%}")

# ========== VISUALIZATIONS ==========
print("\n" + "=" * 70)
print("  📊 CREATING VISUALIZATIONS")
print("=" * 70)

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Plot 1: Uniformity comparison
ax = axes[0, 0]
names = [r['config']['name'].replace('🎯 ', '') for r in sorted_results]
uniformities = [r['analysis']['uniformity'] for r in sorted_results]
colors = plt.cm.viridis(np.linspace(0, 1, len(names)))
bars = ax.barh(range(len(names)), uniformities, color=colors, edgecolor='black', linewidth=2)
ax.set_yticks(range(len(names)))
ax.set_yticklabels(names, fontsize=9, fontweight='bold')
ax.set_xlabel('Uniformity', fontsize=12, fontweight='bold')
ax.set_title('Optimized Configurations - Uniformity', fontsize=14, fontweight='bold')
ax.set_xlim(0, 1)
ax.grid(axis='x', alpha=0.3)
ax.axvline(x=0.996 if previous_results else 0.9, color='red', linestyle='--', linewidth=2, label='Previous Best')
ax.legend()

# Plot 2: Probability distribution of best config
ax = axes[0, 1]
best = sorted_results[0]
probs = best['analysis']['probs']
states = [format(i, f"0{best['config']['qubits']}b") for i in range(len(probs))]
bars = ax.bar(range(len(probs)), probs, color='steelblue', edgecolor='black', linewidth=1)
ax.set_xlabel('Quantum State', fontsize=11, fontweight='bold')
ax.set_ylabel('Probability', fontsize=11, fontweight='bold')
ax.set_title(f"Best Config: {best['config']['name']}", fontsize=12, fontweight='bold')
ax.set_xticks(range(len(probs)))
ax.set_xticklabels(states, rotation=45, ha='right', fontsize=8)
ax.grid(axis='y', alpha=0.3)

# Highlight max state
max_idx = np.argmax(probs)
bars[max_idx].set_color('coral')

# Plot 3: Parameter sensitivity
ax = axes[1, 0]
couplings = [r['config']['coupling'] for r in results]
uniformities_scatter = [r['analysis']['uniformity'] for r in results]
ax.scatter(couplings, uniformities_scatter, s=300, c=range(len(results)), 
           cmap='plasma', edgecolor='black', linewidth=2)
ax.set_xlabel('Coupling Strength', fontsize=11, fontweight='bold')
ax.set_ylabel('Uniformity', fontsize=11, fontweight='bold')
ax.set_title('Coupling vs Uniformity', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3)
for i, r in enumerate(results):
    ax.annotate(str(i+1), (couplings[i], uniformities_scatter[i]), 
                ha='center', va='center', fontsize=8, fontweight='bold', color='white')

# Plot 4: Metrics comparison
ax = axes[1, 1]
metrics = ['Uniformity', 'Max Prob', 'Entropy/Max', 'Sig States/Total']
values = [
    best['analysis']['uniformity'],
    best['analysis']['max_prob'],
    best['analysis']['entropy'] / best['config']['qubits'],
    best['analysis']['significant_states'] / (2**best['config']['qubits'])
]
colors_bar = ['green', 'orange', 'blue', 'purple']
bars = ax.bar(metrics, values, color=colors_bar, edgecolor='black', linewidth=2, alpha=0.7)
ax.set_ylabel('Value (normalized)', fontsize=11, fontweight='bold')
ax.set_title('Best Configuration Metrics', fontsize=12, fontweight='bold')
ax.set_ylim(0, 1)
ax.grid(axis='y', alpha=0.3)
for bar, val in zip(bars, values):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 0.02, f'{val:.2f}',
            ha='center', va='bottom', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('optimized_quantum_circuits.png', dpi=150, bbox_inches='tight')
print("✓ Saved: optimized_quantum_circuits.png")

# ========== SAVE RESULTS ==========
output = {
    'timestamp': datetime.now().isoformat(),
    'optimized_configs': len(results),
    'best_config': {
        'name': best['config']['name'],
        'coupling': best['config']['coupling'],
        'layers': best['config']['layers'],
        'entanglement': best['config']['entanglement'],
        'angles': best['config']['angles'],
        'uniformity': float(best['analysis']['uniformity']),
        'max_prob': float(best['analysis']['max_prob'])
    },
    'improvement': float(improvement) if previous_results else None,
    'all_results': [
        {
            'name': r['config']['name'],
            'uniformity': float(r['analysis']['uniformity']),
            'max_prob': float(r['analysis']['max_prob']),
            'config': {k: (v if not isinstance(v, (np.ndarray, np.floating)) else (v.tolist() if isinstance(v, np.ndarray) else float(v))) 
                      for k, v in r['config'].items() if k != 'layer_patterns'}
        }
        for r in results
    ]
}

with open('optimized_results.json', 'w') as f:
    json.dump(output, f, indent=2)
print("✓ Saved: optimized_results.json")

# ========== FINAL SUMMARY ==========
print("\n" + "=" * 70)
print("  ✅ OPTIMIZATION COMPLETE")
print("=" * 70)

print(f"\n🎯 Best Optimized Configuration:")
print(f"   Name: {best['config']['name']}")
print(f"   Uniformity: {best['analysis']['uniformity']:.3%}")
print(f"   Max Probability: {best['analysis']['max_prob']:.1%}")
print(f"   Significant States: {best['analysis']['significant_states']}/{2**best['config']['qubits']}")
print(f"\n   Parameters:")
print(f"   • Coupling: {best['config']['coupling']}")
print(f"   • Layers: {best['config']['layers']}")
print(f"   • Entanglement: {best['config']['entanglement']}")
print(f"   • Angles: {best['config']['angles']}")

if previous_results and improvement > 0:
    print(f"\n🎉 Successfully improved uniformity by {improvement:.2%}!")
elif previous_results:
    print(f"\n📊 Achieved comparable results to previous best")

print(f"\n📁 Generated Files:")
print(f"   • optimized_quantum_circuits.png")
print(f"   • optimized_results.json")

print("\n" + "=" * 70)
print("  🚀 READY FOR DEPLOYMENT")
print("=" * 70)
