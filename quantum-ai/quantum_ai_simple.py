#!/usr/bin/env python3
"""
Quantum-LLM Integration (Simplified Working Version)
Uses local echo provider for AI-powered analysis
"""
import sys
import os
import json
import pennylane as qml
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Add paths for LLM integration
sys.path.insert(0, str(Path(__file__).parent.parent / "AI" / "http_chat" / "talk-to-ai" / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "shared"))

try:
    from chat_providers import detect_provider, LocalEchoProvider
    LLM_AVAILABLE = True
    print(f"✓ LLM Provider framework loaded")
except Exception as e:
    LLM_AVAILABLE = False
    print(f"⚠️  LLM not available: {e}")

print("=" * 70)
print("  🧠 QUANTUM-LLM INTEGRATION (AI-POWERED ANALYSIS)")
print("=" * 70)

# ========== QUANTUM CONFIGURATIONS ==========
configurations = [
    {'name': '1. Balanced', 'qubits': 4, 'angles': [1.2, 0.8, 2.1, 0.5], 'coupling': 0.7, 'layers': 3, 'entanglement': 'circular'},
    {'name': '2. Weak Coupling', 'qubits': 4, 'angles': [1.2, 0.8, 2.1, 0.5], 'coupling': 0.35, 'layers': 3, 'entanglement': 'circular'},
    {'name': '3. Strong Coupling', 'qubits': 4, 'angles': [1.2, 0.8, 2.1, 0.5], 'coupling': 1.0, 'layers': 3, 'entanglement': 'circular'},
    {'name': '4. All-to-All', 'qubits': 4, 'angles': [1.2, 0.8, 2.1, 0.5], 'coupling': 0.7, 'layers': 3, 'entanglement': 'all-to-all'},
    {'name': '5. Phase Gates', 'qubits': 4, 'angles': [1.2, 0.8, 2.1, 0.5], 'coupling': 0.7, 'layers': 3, 'entanglement': 'circular', 'phase': True},
    {'name': '6. Deep (6L)', 'qubits': 4, 'angles': [1.2, 0.8, 2.1, 0.5], 'coupling': 0.7, 'layers': 6, 'entanglement': 'circular'},
    {'name': '7. Standard Angles', 'qubits': 4, 'angles': [np.pi/2, np.pi/4, np.pi/3, np.pi/6], 'coupling': 0.7, 'layers': 3, 'entanglement': 'circular'},
    {'name': '8. Linear Chain', 'qubits': 4, 'angles': [1.2, 0.8, 2.1, 0.5], 'coupling': 0.7, 'layers': 3, 'entanglement': 'linear'},
]

def build_and_test_circuit(config):
    """Build and test quantum circuit"""
    n_qubits = config['qubits']
    angles = config['angles'][:n_qubits]
    coupling = config['coupling']
    layers = config['layers']
    entanglement = config['entanglement']
    phase = config.get('phase', False)
    
    dev = qml.device('lightning.qubit', wires=n_qubits, shots=1000)
    
    @qml.qnode(dev)
    def circuit(params):
        for i in range(n_qubits):
            qml.Hadamard(wires=i)
        
        for layer in range(layers):
            for i in range(n_qubits):
                idx = i % len(params)
                qml.RY(params[idx] * coupling, wires=i)
                qml.RZ(params[idx] * coupling * 0.5, wires=i)
            
            if phase:
                for i in range(n_qubits):
                    qml.PhaseShift(np.pi/4 * (layer + 1), wires=i)
            
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
        
        return qml.probs(wires=range(n_qubits))
    
    probs = circuit(np.array(angles))
    
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

# ========== RUN EXPERIMENTS ==========
print(f"\n🔬 Running {len(configurations)} quantum experiments...\n")

results = []
for i, config in enumerate(configurations, 1):
    print(f"[{i}/{len(configurations)}] {config['name']:20s}", end=" ")
    
    try:
        analysis = build_and_test_circuit(config)
        results.append({'config': config, 'analysis': analysis})
        print(f"✓ U={analysis['uniformity']:.1%}, Max={analysis['max_prob']:.1%}")
    except Exception as e:
        print(f"✗ {e}")

print(f"\n✓ Completed {len(results)} experiments")

# ========== AI ANALYSIS ==========
if LLM_AVAILABLE:
    print("\n" + "=" * 70)
    print("  🤖 AI-POWERED ANALYSIS")
    print("=" * 70)
    
    # Create summary for AI
    summary = "Quantum circuit experiments:\n\n"
    for r in results:
        a = r['analysis']
        summary += f"{r['config']['name']}: Uniformity={a['uniformity']:.1%}, Max={a['max_prob']:.1%}\n"
    
    # Use LocalEchoProvider for deterministic responses
    provider = LocalEchoProvider()
    
    # Analysis 1: Identify best configs
    print("\n1️⃣  AI Analysis: Identifying best configurations...\n")
    
    prompt1 = f"""Based on these quantum circuit results:

{summary}

Provide analysis:
1. Which 3 configs are best for quantum ML training? Why?
2. Which config is best for quantum randomness? Why?
3. Key patterns you notice?"""
    
    messages = [{"role": "user", "content": prompt1}]
    response1 = provider.complete(messages=messages, stream=False)
    print(response1)
    
    # Analysis 2: Pattern detection
    print("\n2️⃣  AI Analysis: Pattern Detection...\n")
    
    best = max(results, key=lambda x: x['analysis']['uniformity'])
    worst = min(results, key=lambda x: x['analysis']['uniformity'])
    
    prompt2 = f"""Compare these quantum circuits:

BEST: {best['config']['name']}
- Uniformity: {best['analysis']['uniformity']:.1%}
- Coupling: {best['config']['coupling']}, Layers: {best['config']['layers']}, Entanglement: {best['config']['entanglement']}

WORST: {worst['config']['name']}
- Uniformity: {worst['analysis']['uniformity']:.1%}
- Coupling: {worst['config']['coupling']}, Layers: {worst['config']['layers']}, Entanglement: {worst['config']['entanglement']}

What quantum phenomena explain these differences?"""
    
    messages = [{"role": "user", "content": prompt2}]
    response2 = provider.complete(messages=messages, stream=False)
    print(response2)
    
    # Analysis 3: Recommendations
    print("\n3️⃣  AI Analysis: Optimization Recommendations...\n")
    
    prompt3 = """Based on the quantum circuit analysis above, design an OPTIMAL configuration:

Return in format: coupling=X, layers=Y, entanglement=Z, angles=[a,b,c,d]

Requirements:
- Maximize uniformity (>90%)
- Efficient depth
- Strong entanglement
- Balanced angles"""
    
    messages = [
        {"role": "user", "content": prompt1},
        {"role": "assistant", "content": response1},
        {"role": "user", "content": prompt3}
    ]
    response3 = provider.complete(messages=messages, stream=False)
    print(response3)
    
else:
    print("\n⚠️  LLM not available - skipping AI analysis")
    print("To enable: Configure OPENAI_API_KEY, AZURE_OPENAI_API_KEY, or start LMStudio")

# ========== RANKINGS ==========
print("\n" + "=" * 70)
print("  📊 QUANTUM CIRCUIT RANKINGS")
print("=" * 70)

sorted_results = sorted(results, key=lambda x: x['analysis']['uniformity'], reverse=True)

print("\n🏆 By Uniformity (Best for ML):")
for i, r in enumerate(sorted_results[:5], 1):
    print(f"  {i}. {r['config']['name']:25s} → {r['analysis']['uniformity']:.1%}")

print("\n🎯 By Concentration (Best for State Prep):")
sorted_conc = sorted(results, key=lambda x: x['analysis']['max_prob'], reverse=True)
for i, r in enumerate(sorted_conc[:5], 1):
    print(f"  {i}. {r['config']['name']:25s} → {r['analysis']['max_prob']:.1%}")

# ========== VISUALIZATIONS ==========
print("\n" + "=" * 70)
print("  📊 CREATING VISUALIZATIONS")
print("=" * 70)

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Plot 1: Uniformity
ax = axes[0, 0]
names = [r['config']['name'] for r in sorted_results]
uniformities = [r['analysis']['uniformity'] for r in sorted_results]
colors = plt.cm.viridis(np.linspace(0, 1, len(names)))
ax.barh(range(len(names)), uniformities, color=colors, edgecolor='black', linewidth=2)
ax.set_yticks(range(len(names)))
ax.set_yticklabels(names, fontsize=9)
ax.set_xlabel('Uniformity', fontsize=11, fontweight='bold')
ax.set_title('Quantum Circuit Uniformity', fontsize=12, fontweight='bold')
ax.set_xlim(0, 1)
ax.grid(axis='x', alpha=0.3)

# Plot 2: Max Probability
ax = axes[0, 1]
max_probs = [r['analysis']['max_prob'] for r in results]
couplings = [r['config']['coupling'] for r in results]
ax.scatter(uniformities[:len(results)], max_probs, s=300, c=couplings, 
          cmap='coolwarm', edgecolor='black', linewidth=2)
ax.set_xlabel('Uniformity', fontsize=11, fontweight='bold')
ax.set_ylabel('Max Probability', fontsize=11, fontweight='bold')
ax.set_title('Uniformity vs Concentration', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3)
cbar = plt.colorbar(ax.collections[0], ax=ax)
cbar.set_label('Coupling', fontsize=10)

# Plot 3: Best config distribution
ax = axes[1, 0]
best = sorted_results[0]
probs = best['analysis']['probs']
states = [format(i, '04b') for i in range(len(probs))]
bars = ax.bar(range(len(probs)), probs, color='steelblue', edgecolor='black', linewidth=1)
bars[np.argmax(probs)].set_color('coral')
ax.set_xlabel('Quantum State', fontsize=11, fontweight='bold')
ax.set_ylabel('Probability', fontsize=11, fontweight='bold')
ax.set_title(f'Best Config: {best["config"]["name"]}', fontsize=12, fontweight='bold')
ax.set_xticks(range(len(probs)))
ax.set_xticklabels(states, rotation=45, ha='right', fontsize=8)
ax.grid(axis='y', alpha=0.3)

# Plot 4: Coupling impact
ax = axes[1, 1]
all_couplings = [r['config']['coupling'] for r in results]
all_uniformities = [r['analysis']['uniformity'] for r in results]
ax.scatter(all_couplings, all_uniformities, s=200, c=range(len(results)), 
          cmap='plasma', edgecolor='black', linewidth=2)
ax.set_xlabel('Coupling Strength', fontsize=11, fontweight='bold')
ax.set_ylabel('Uniformity', fontsize=11, fontweight='bold')
ax.set_title('Coupling vs Uniformity', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('quantum_ai_analysis.png', dpi=150, bbox_inches='tight')
print("✓ Saved: quantum_ai_analysis.png")

# ========== SUMMARY ==========
print("\n" + "=" * 70)
print("  ✅ COMPLETE")
print("=" * 70)

print(f"\n🏆 Best Configuration:")
print(f"   {best['config']['name']}")
print(f"   Uniformity: {best['analysis']['uniformity']:.1%}")
print(f"   Coupling: {best['config']['coupling']}, Layers: {best['config']['layers']}")

print(f"\n📁 Generated:")
print(f"   • quantum_ai_analysis.png")

print("\n" + "=" * 70)
print("  🎉 QUANTUM-LLM INTEGRATION COMPLETE!")
print("=" * 70)
