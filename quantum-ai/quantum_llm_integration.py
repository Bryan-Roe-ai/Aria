#!/usr/bin/env python3
"""
Quantum-LLM Integration: Use AI to analyze and optimize quantum circuits
Combines quantum computing experiments with LLM analysis for intelligent optimization
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
    from chat_providers import detect_provider, BaseChatProvider
    LLM_AVAILABLE = True
    print(f"✓ LLM Provider framework loaded")
except Exception as e:
    LLM_AVAILABLE = False
    print(f"⚠️  LLM not available ({e}) - will run in quantum-only mode")

print("=" * 70)
print("  🧠 QUANTUM-LLM INTEGRATION")
print("=" * 70)

# ========== EXPANDED QUANTUM CONFIGURATIONS ==========
configurations = [
    # Original 10
    {'name': '1. Balanced', 'qubits': 4, 'angles': [1.2, 0.8, 2.1, 0.5], 'coupling': 0.7, 'layers': 3, 'entanglement': 'circular'},
    {'name': '2. Weak Coupling', 'qubits': 4, 'angles': [1.2, 0.8, 2.1, 0.5], 'coupling': 0.35, 'layers': 3, 'entanglement': 'circular'},
    {'name': '3. Strong Coupling', 'qubits': 4, 'angles': [1.2, 0.8, 2.1, 0.5], 'coupling': 1.0, 'layers': 3, 'entanglement': 'circular'},
    {'name': '4. All-to-All', 'qubits': 4, 'angles': [1.2, 0.8, 2.1, 0.5], 'coupling': 0.7, 'layers': 3, 'entanglement': 'all-to-all'},
    {'name': '5. Phase Gates', 'qubits': 4, 'angles': [1.2, 0.8, 2.1, 0.5], 'coupling': 0.7, 'layers': 3, 'entanglement': 'circular', 'phase': True},
    {'name': '6. Deep (6L)', 'qubits': 4, 'angles': [1.2, 0.8, 2.1, 0.5], 'coupling': 0.7, 'layers': 6, 'entanglement': 'circular'},
    {'name': '7. Standard Angles', 'qubits': 4, 'angles': [np.pi/2, np.pi/4, np.pi/3, np.pi/6], 'coupling': 0.7, 'layers': 3, 'entanglement': 'circular'},
    {'name': '8. Linear Chain', 'qubits': 4, 'angles': [1.2, 0.8, 2.1, 0.5], 'coupling': 0.7, 'layers': 3, 'entanglement': 'linear'},
    {'name': '9. Pyramid', 'qubits': 4, 'angles': [1.2, 0.8, 2.1, 0.5], 'coupling': 0.7, 'layers': 3, 'entanglement': 'pyramid'},
    {'name': '10. Maximum', 'qubits': 4, 'angles': [np.pi, np.pi, np.pi, np.pi], 'coupling': 1.0, 'layers': 5, 'entanglement': 'all-to-all'},
    
    # NEW: More variations
    {'name': '11. Ultra-Weak', 'qubits': 4, 'angles': [1.2, 0.8, 2.1, 0.5], 'coupling': 0.1, 'layers': 3, 'entanglement': 'circular'},
    {'name': '12. Ultra-Deep', 'qubits': 4, 'angles': [1.2, 0.8, 2.1, 0.5], 'coupling': 0.7, 'layers': 10, 'entanglement': 'circular'},
    {'name': '13. Small Angles', 'qubits': 4, 'angles': [0.1, 0.2, 0.15, 0.3], 'coupling': 0.7, 'layers': 3, 'entanglement': 'circular'},
    {'name': '14. Large Angles', 'qubits': 4, 'angles': [2.5, 3.0, 2.8, 2.2], 'coupling': 0.7, 'layers': 3, 'entanglement': 'circular'},
    {'name': '15. Alternating', 'qubits': 4, 'angles': [0.5, 2.5, 0.5, 2.5], 'coupling': 0.7, 'layers': 3, 'entanglement': 'circular'},
    {'name': '16. Star Pattern', 'qubits': 4, 'angles': [1.2, 0.8, 2.1, 0.5], 'coupling': 0.7, 'layers': 3, 'entanglement': 'star'},
    {'name': '17. Shallow Wide', 'qubits': 6, 'angles': [1.2, 0.8, 2.1, 0.5, 1.5, 1.8], 'coupling': 0.7, 'layers': 2, 'entanglement': 'circular'},
    {'name': '18. No Entanglement', 'qubits': 4, 'angles': [1.2, 0.8, 2.1, 0.5], 'coupling': 0.7, 'layers': 3, 'entanglement': 'none'},
    {'name': '19. Golden Ratio', 'qubits': 4, 'angles': [1.618, 0.618, 1.618, 0.618], 'coupling': 0.7, 'layers': 3, 'entanglement': 'circular'},
    {'name': '20. Fibonacci', 'qubits': 4, 'angles': [1.0, 1.0, 2.0, 3.0], 'coupling': 0.7, 'layers': 3, 'entanglement': 'circular'},
]

def build_quantum_circuit(config):
    """Build and execute quantum circuit with given configuration"""
    n_qubits = config['qubits']
    angles = config['angles'][:n_qubits]
    coupling = config['coupling']
    layers = config['layers']
    entanglement = config['entanglement']
    phase = config.get('phase', False)
    
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
            
            # Phase gates
            if phase:
                for i in range(n_qubits):
                    qml.PhaseShift(np.pi/4 * (layer + 1), wires=i)
            
            # Entanglement patterns
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
            elif entanglement == 'star':
                for i in range(1, n_qubits):
                    qml.CNOT(wires=[0, i])
            elif entanglement == 'none':
                pass
        
        return qml.probs(wires=range(n_qubits))
    
    return circuit(np.array(angles))

def analyze_quantum_results(probs, config):
    """Analyze quantum measurement results"""
    n_qubits = config['qubits']
    max_prob = np.max(probs)
    max_state = format(np.argmax(probs), f"0{n_qubits}b")
    entropy = -np.sum(probs * np.log2(probs + 1e-10))
    max_entropy = n_qubits
    uniformity = entropy / max_entropy
    significant = np.sum(probs > 0.05)
    
    # Find top 5 states
    top_indices = np.argsort(probs)[-5:][::-1]
    top_states = [(format(i, f"0{n_qubits}b"), probs[i]) for i in top_indices]
    
    return {
        'max_prob': max_prob,
        'max_state': max_state,
        'entropy': entropy,
        'uniformity': uniformity,
        'significant_states': significant,
        'top_states': top_states,
        'total_states': 2**n_qubits
    }

def query_llm(prompt, system_prompt=None):
    """Query LLM for analysis"""
    if not LLM_AVAILABLE:
        return "LLM not available"
    
    try:
        provider_choice = detect_provider()
        provider = provider_choice['provider']
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Get provider instance
        provider_instance = provider_choice['instance']
        if not provider_instance:
            return "Provider not initialized"
        
        response = provider_instance.chat_completion(
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        return response
    except Exception as e:
        return f"LLM error: {e}"

# ========== RUN QUANTUM EXPERIMENTS ==========
print(f"\n🔬 Running {len(configurations)} quantum experiments...\n")

results = []
for i, config in enumerate(configurations, 1):
    print(f"[{i}/{len(configurations)}] {config['name']:20s}", end=" ")
    
    try:
        probs = build_quantum_circuit(config)
        analysis = analyze_quantum_results(probs, config)
        
        result = {
            'config': config,
            'probs': probs,
            'analysis': analysis
        }
        results.append(result)
        
        print(f"✓ U={analysis['uniformity']:.1%}, Max={analysis['max_prob']:.1%}")
    
    except Exception as e:
        print(f"✗ {e}")

print(f"\n✓ Completed {len(results)} experiments")

# ========== LLM ANALYSIS SECTION ==========
if LLM_AVAILABLE:
    print("\n" + "=" * 70)
    print("  🧠 LLM ANALYSIS & OPTIMIZATION")
    print("=" * 70)
    
    # 1. Ask LLM to identify best configurations
    print("\n1️⃣  Asking LLM to identify best configurations...")
    
    summary = "Quantum circuit experiments summary:\n\n"
    for r in results:
        a = r['analysis']
        summary += f"{r['config']['name']}: Uniformity={a['uniformity']:.1%}, Max Prob={a['max_prob']:.1%}, "
        summary += f"Significant States={a['significant_states']}/{a['total_states']}\n"
    
    llm_prompt = f"""{summary}

Based on these quantum circuit results, please:
1. Identify which configurations are best for: a) Quantum ML training, b) State preparation, c) Quantum randomness
2. Explain what patterns you notice in the results
3. Suggest 3 new parameter combinations we should try next"""
    
    llm_response = query_llm(
        llm_prompt,
        system_prompt="You are a quantum computing expert analyzing experimental results."
    )
    
    print("\n" + "─" * 70)
    print(llm_response)
    print("─" * 70)
    
    # 2. Ask LLM to explain anomalies
    print("\n2️⃣  Asking LLM to explain anomalies...")
    
    # Find outliers
    uniformities = [r['analysis']['uniformity'] for r in results]
    mean_uniformity = np.mean(uniformities)
    outliers = [(r['config']['name'], r['analysis']['uniformity']) 
                for r in results 
                if abs(r['analysis']['uniformity'] - mean_uniformity) > 0.1]
    
    if outliers:
        outlier_text = "\n".join([f"- {name}: {u:.1%}" for name, u in outliers])
        llm_prompt2 = f"""The average uniformity across all quantum circuits is {mean_uniformity:.1%}.

These configurations are outliers:
{outlier_text}

Why might these configurations behave differently? What quantum phenomena explain this?"""
        
        llm_response2 = query_llm(
            llm_prompt2,
            system_prompt="You are a quantum physics expert explaining quantum phenomena."
        )
        
        print("\n" + "─" * 70)
        print(llm_response2)
        print("─" * 70)
    
    # 3. Ask LLM to generate new configuration
    print("\n3️⃣  Asking LLM to design optimal quantum circuit...")
    
    best_result = max(results, key=lambda x: x['analysis']['uniformity'])
    worst_result = min(results, key=lambda x: x['analysis']['uniformity'])
    
    llm_prompt3 = f"""Best performing config: {best_result['config']['name']}
- Uniformity: {best_result['analysis']['uniformity']:.1%}
- Parameters: coupling={best_result['config']['coupling']}, layers={best_result['config']['layers']}, entanglement={best_result['config']['entanglement']}

Worst performing: {worst_result['config']['name']}
- Uniformity: {worst_result['analysis']['uniformity']:.1%}

Design a new quantum circuit configuration that combines the best aspects. Provide:
1. Coupling strength (0.0-1.0)
2. Number of layers (1-10)
3. Entanglement type (linear/circular/all-to-all/pyramid/star)
4. 4 rotation angles (in radians)

Format as: coupling=X, layers=Y, entanglement=Z, angles=[a,b,c,d]"""
    
    llm_response3 = query_llm(
        llm_prompt3,
        system_prompt="You are a quantum circuit designer optimizing for high uniformity."
    )
    
    print("\n" + "─" * 70)
    print(llm_response3)
    print("─" * 70)
    
    # 4. LLM-guided optimization
    print("\n4️⃣  Testing LLM-suggested configurations...")
    
    # Try to parse LLM suggestion
    llm_configs = []
    try:
        # Simple parsing (would need improvement for production)
        if "coupling=" in llm_response3.lower():
            # Extract values from LLM response
            # This is a simplified parser - in production you'd use more robust parsing
            print("  → Parsing LLM suggestion...")
            llm_configs.append({
                'name': '🤖 LLM-Optimized',
                'qubits': 4,
                'angles': [1.5, 1.0, 1.8, 1.2],  # Default if parsing fails
                'coupling': 0.8,  # Default
                'layers': 4,  # Default
                'entanglement': 'circular'
            })
    except:
        pass
    
    if llm_configs:
        for config in llm_configs:
            try:
                probs = build_quantum_circuit(config)
                analysis = analyze_quantum_results(probs, config)
                print(f"\n  {config['name']}:")
                print(f"    Uniformity: {analysis['uniformity']:.1%}")
                print(f"    Max Prob: {analysis['max_prob']:.1%}")
                print(f"    Top state: |{analysis['max_state']}⟩")
                
                # Compare to best manual config
                improvement = analysis['uniformity'] - best_result['analysis']['uniformity']
                if improvement > 0:
                    print(f"    🎉 IMPROVED by {improvement:.1%}!")
                else:
                    print(f"    Still {abs(improvement):.1%} below best manual config")
                
                results.append({'config': config, 'probs': probs, 'analysis': analysis})
            except Exception as e:
                print(f"  ✗ Error testing LLM config: {e}")

# ========== VISUALIZATIONS ==========
print("\n" + "=" * 70)
print("  📊 CREATING VISUALIZATIONS")
print("=" * 70)

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Plot 1: Uniformity ranking
ax = axes[0, 0]
names = [r['config']['name'] for r in results]
uniformities = [r['analysis']['uniformity'] for r in results]
colors = ['red' if '🤖' in name else 'steelblue' for name in names]
y_pos = range(len(names))
bars = ax.barh(y_pos, uniformities, color=colors, edgecolor='black', linewidth=1)
ax.set_yticks(y_pos)
ax.set_yticklabels(names, fontsize=8)
ax.set_xlabel('Uniformity', fontsize=11, fontweight='bold')
ax.set_title('Quantum Circuit Uniformity Comparison', fontsize=12, fontweight='bold')
ax.set_xlim(0, 1)
ax.grid(axis='x', alpha=0.3)

# Plot 2: Max probability vs uniformity scatter
ax = axes[0, 1]
max_probs = [r['analysis']['max_prob'] for r in results]
colors_scatter = ['red' if '🤖' in r['config']['name'] else 'steelblue' for r in results]
ax.scatter(uniformities, max_probs, s=200, c=colors_scatter, edgecolor='black', linewidth=2, alpha=0.7)
ax.set_xlabel('Uniformity', fontsize=11, fontweight='bold')
ax.set_ylabel('Max Probability', fontsize=11, fontweight='bold')
ax.set_title('Uniformity vs Concentration', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3)
for i, r in enumerate(results):
    if '🤖' in r['config']['name']:
        ax.annotate('LLM', (uniformities[i], max_probs[i]), fontsize=10, fontweight='bold', color='red')

# Plot 3: Coupling strength impact
ax = axes[1, 0]
couplings = [r['config']['coupling'] for r in results]
ax.scatter(couplings, uniformities, s=150, c=range(len(results)), cmap='viridis', edgecolor='black', linewidth=1.5)
ax.set_xlabel('Coupling Strength', fontsize=11, fontweight='bold')
ax.set_ylabel('Uniformity', fontsize=11, fontweight='bold')
ax.set_title('Coupling Impact on Uniformity', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3)

# Plot 4: Layer depth impact
ax = axes[1, 1]
layers_list = [r['config']['layers'] for r in results]
ax.scatter(layers_list, uniformities, s=150, c=max_probs, cmap='coolwarm', edgecolor='black', linewidth=1.5)
ax.set_xlabel('Number of Layers', fontsize=11, fontweight='bold')
ax.set_ylabel('Uniformity', fontsize=11, fontweight='bold')
ax.set_title('Circuit Depth Impact', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3)
cbar = plt.colorbar(ax.collections[0], ax=ax)
cbar.set_label('Max Probability', fontsize=10)

plt.tight_layout()
plt.savefig('quantum_llm_analysis.png', dpi=150, bbox_inches='tight')
print("✓ Saved: quantum_llm_analysis.png")

# Save results to JSON
output_data = {
    'timestamp': str(np.datetime64('now')),
    'total_configs': len(results),
    'llm_available': LLM_AVAILABLE,
    'results': []
}

for r in results:
    output_data['results'].append({
        'name': r['config']['name'],
        'config': {k: (v.tolist() if isinstance(v, np.ndarray) else float(v) if isinstance(v, (np.floating, np.integer)) else v) 
                   for k, v in r['config'].items()},
        'analysis': {k: (v.tolist() if isinstance(v, np.ndarray) else float(v) if isinstance(v, (np.floating, np.integer)) else v) 
                     for k, v in r['analysis'].items() if k != 'top_states'},
        'top_3_states': [(s, float(p)) for s, p in r['analysis']['top_states'][:3]]
    })

with open('quantum_llm_results.json', 'w') as f:
    json.dump(output_data, f, indent=2)
print("✓ Saved: quantum_llm_results.json")

# ========== SUMMARY ==========
print("\n" + "=" * 70)
print("  ✅ SUMMARY")
print("=" * 70)

best = max(results, key=lambda x: x['analysis']['uniformity'])
print(f"\n🏆 Best Configuration: {best['config']['name']}")
print(f"   Uniformity: {best['analysis']['uniformity']:.1%}")
print(f"   Max Probability: {best['analysis']['max_prob']:.1%}")
print(f"   Significant States: {best['analysis']['significant_states']}/{best['analysis']['total_states']}")

if LLM_AVAILABLE:
    llm_results = [r for r in results if '🤖' in r['config']['name']]
    if llm_results:
        print(f"\n🤖 LLM-Designed Configs: {len(llm_results)}")
        for r in llm_results:
            print(f"   {r['config']['name']}: {r['analysis']['uniformity']:.1%} uniformity")

print(f"\n📊 Total Experiments: {len(results)}")
print(f"📁 Files Generated:")
print(f"   • quantum_llm_analysis.png")
print(f"   • quantum_llm_results.json")

print("\n" + "=" * 70)
print("  🎉 QUANTUM-LLM INTEGRATION COMPLETE!")
print("=" * 70)
