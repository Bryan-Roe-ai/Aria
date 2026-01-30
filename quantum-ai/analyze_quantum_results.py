#!/usr/bin/env python3
"""
Quantum Results Analyzer - Summarize and interpret quantum experiment data
"""
import json
import numpy as np

print("=" * 70)
print("  📊 QUANTUM RESULTS ANALYSIS")
print("=" * 70)

# Load results
with open('quantum_llm_results.json', 'r') as f:
    data = json.load(f)

results = data['results']
print(f"\nAnalyzing {len(results)} quantum circuit configurations")
print(f"Timestamp: {data['timestamp']}")

# ========== KEY FINDINGS ==========
print("\n" + "=" * 70)
print("  🔍 KEY FINDINGS")
print("=" * 70)

# Sort by uniformity
sorted_uniform = sorted(results, key=lambda x: x['analysis']['uniformity'], reverse=True)
sorted_concentrated = sorted(results, key=lambda x: x['analysis']['max_prob'], reverse=True)

print("\n🏆 TOP 5 MOST UNIFORM (Best for Quantum ML):")
for i, r in enumerate(sorted_uniform[:5], 1):
    print(f"  {i}. {r['name']:25s} → {r['analysis']['uniformity']:.1%} uniformity")
    print(f"     Config: coupling={r['config']['coupling']}, layers={r['config']['layers']}, {r['config']['entanglement']}")

print("\n🎯 TOP 5 MOST CONCENTRATED (Best for State Preparation):")
for i, r in enumerate(sorted_concentrated[:5], 1):
    print(f"  {i}. {r['name']:25s} → {r['analysis']['max_prob']:.1%} in |{r['analysis']['max_state']}⟩")
    print(f"     Config: coupling={r['config']['coupling']}, layers={r['config']['layers']}, {r['config']['entanglement']}")

# ========== PATTERN ANALYSIS ==========
print("\n" + "=" * 70)
print("  🔬 PATTERN ANALYSIS")
print("=" * 70)

# Group by coupling strength
low_coupling = [r for r in results if r['config']['coupling'] <= 0.4]
mid_coupling = [r for r in results if 0.4 < r['config']['coupling'] < 0.9]
high_coupling = [r for r in results if r['config']['coupling'] >= 0.9]

print(f"\n📈 Coupling Strength Impact:")
if low_coupling:
    avg_low = np.mean([r['analysis']['uniformity'] for r in low_coupling])
    print(f"  Low (≤0.4):  {len(low_coupling)} configs, avg uniformity = {avg_low:.1%}")
if mid_coupling:
    avg_mid = np.mean([r['analysis']['uniformity'] for r in mid_coupling])
    print(f"  Mid (0.4-0.9): {len(mid_coupling)} configs, avg uniformity = {avg_mid:.1%}")
if high_coupling:
    avg_high = np.mean([r['analysis']['uniformity'] for r in high_coupling])
    print(f"  High (≥0.9): {len(high_coupling)} configs, avg uniformity = {avg_high:.1%}")

# Group by layer depth
shallow = [r for r in results if r['config']['layers'] <= 3]
mid_depth = [r for r in results if 3 < r['config']['layers'] < 7]
deep = [r for r in results if r['config']['layers'] >= 7]

print(f"\n🏗️  Circuit Depth Impact:")
if shallow:
    avg_shallow = np.mean([r['analysis']['uniformity'] for r in shallow])
    print(f"  Shallow (≤3): {len(shallow)} configs, avg uniformity = {avg_shallow:.1%}")
if mid_depth:
    avg_mid_depth = np.mean([r['analysis']['uniformity'] for r in mid_depth])
    print(f"  Mid (4-6):    {len(mid_depth)} configs, avg uniformity = {avg_mid_depth:.1%}")
if deep:
    avg_deep = np.mean([r['analysis']['uniformity'] for r in deep])
    print(f"  Deep (≥7):    {len(deep)} configs, avg uniformity = {avg_deep:.1%}")

# Group by entanglement type
entanglement_types = {}
for r in results:
    ent = r['config']['entanglement']
    if ent not in entanglement_types:
        entanglement_types[ent] = []
    entanglement_types[ent].append(r['analysis']['uniformity'])

print(f"\n🔗 Entanglement Pattern Impact:")
for ent, uniformities in sorted(entanglement_types.items(), key=lambda x: np.mean(x[1]), reverse=True):
    avg_uni = np.mean(uniformities)
    print(f"  {ent:15s} → {avg_uni:.1%} avg uniformity ({len(uniformities)} configs)")

# ========== EXTREME CASES ==========
print("\n" + "=" * 70)
print("  ⚡ EXTREME CASES")
print("=" * 70)

# Most extreme concentration
most_concentrated = max(results, key=lambda x: x['analysis']['max_prob'])
print(f"\n🔴 Most Concentrated State:")
print(f"   {most_concentrated['name']}")
print(f"   → {most_concentrated['analysis']['max_prob']:.1%} in |{most_concentrated['analysis']['max_state']}⟩")
print(f"   → Only {most_concentrated['analysis']['significant_states']} significant states")
print(f"   Use case: Perfect for preparing specific quantum states")

# Most uniform
most_uniform = max(results, key=lambda x: x['analysis']['uniformity'])
print(f"\n🟢 Most Uniform Distribution:")
print(f"   {most_uniform['name']}")
print(f"   → {most_uniform['analysis']['uniformity']:.1%} uniformity")
print(f"   → {most_uniform['analysis']['significant_states']}/{most_uniform['analysis']['total_states']} significant states")
print(f"   Use case: Ideal for quantum random number generation")

# Best balanced
balanced = [r for r in results if 0.80 <= r['analysis']['uniformity'] <= 0.90]
if balanced:
    best_balanced = max(balanced, key=lambda x: x['analysis']['uniformity'])
    print(f"\n⚖️  Best Balanced Config:")
    print(f"   {best_balanced['name']}")
    print(f"   → {best_balanced['analysis']['uniformity']:.1%} uniformity")
    print(f"   → {best_balanced['analysis']['max_prob']:.1%} max probability")
    print(f"   Use case: Optimal for quantum machine learning")

# ========== RECOMMENDATIONS ==========
print("\n" + "=" * 70)
print("  💡 RECOMMENDATIONS")
print("=" * 70)

print(f"\n📝 Based on {len(results)} experiments:\n")

print("1️⃣  For Quantum Machine Learning:")
print(f"    → Use {best_balanced['name'] if balanced else sorted_uniform[0]['name']}")
print(f"    → Coupling: {best_balanced['config']['coupling'] if balanced else sorted_uniform[0]['config']['coupling']}")
print(f"    → Layers: {best_balanced['config']['layers'] if balanced else sorted_uniform[0]['config']['layers']}")
print(f"    → Entanglement: {best_balanced['config']['entanglement'] if balanced else sorted_uniform[0]['config']['entanglement']}")
print(f"    → Achieves good expressivity without over-concentration")

print(f"\n2️⃣  For State Preparation:")
print(f"    → Use {most_concentrated['name']}")
print(f"    → Coupling: {most_concentrated['config']['coupling']}")
print(f"    → Can prepare |{most_concentrated['analysis']['max_state']}⟩ with {most_concentrated['analysis']['max_prob']:.1%} probability")

print(f"\n3️⃣  For Quantum Randomness:")
print(f"    → Use {most_uniform['name']}")
print(f"    → Coupling: {most_uniform['config']['coupling']}")
print(f"    → Achieves near-perfect uniformity ({most_uniform['analysis']['uniformity']:.1%})")

# ========== INSIGHTS ==========
print("\n" + "=" * 70)
print("  🧠 KEY INSIGHTS")
print("=" * 70)

print("\n✨ What we learned:\n")

# Coupling insight
if avg_high > avg_low:
    print("• Higher coupling → MORE uniform distributions")
    print(f"  (High: {avg_high:.1%} vs Low: {avg_low:.1%})")
else:
    print("• Lower coupling → MORE uniform distributions")
    print(f"  (Low: {avg_low:.1%} vs High: {avg_high:.1%})")

# Depth insight
if avg_deep > avg_shallow:
    print("• Deeper circuits → MORE uniform distributions")
else:
    print("• Shallow circuits → MORE uniform distributions")
    print(f"  (Shallow: {avg_shallow:.1%} vs Deep: {avg_deep:.1%})")

# Entanglement insight
best_ent = max(entanglement_types.items(), key=lambda x: np.mean(x[1]))
worst_ent = min(entanglement_types.items(), key=lambda x: np.mean(x[1]))
print(f"• Best entanglement: {best_ent[0]} ({np.mean(best_ent[1]):.1%})")
print(f"• Worst entanglement: {worst_ent[0]} ({np.mean(worst_ent[1]):.1%})")

# Special patterns
angle_configs = {
    'Small Angles': next((r for r in results if 'Small' in r['name']), None),
    'Large Angles': next((r for r in results if 'Large' in r['name']), None),
    'Standard Angles': next((r for r in results if 'Standard' in r['name']), None),
}

print("\n• Rotation angle impact:")
for name, config in angle_configs.items():
    if config:
        print(f"  {name:20s} → {config['analysis']['uniformity']:.1%} uniformity")

print("\n" + "=" * 70)
print("  🎯 NEXT STEPS")
print("=" * 70)

print("\n🚀 Suggested new experiments:\n")

print("1. Hybrid approach:")
print(f"   → Combine {most_uniform['config']['entanglement']} entanglement")
print(f"   → With {best_balanced['config']['coupling'] if balanced else 0.7} coupling")
print(f"   → And {best_balanced['config']['layers'] if balanced else 3} layers")

print("\n2. Adaptive coupling:")
print(f"   → Start with high coupling ({avg_high:.2f})")
print(f"   → Gradually reduce to {avg_low:.2f}")
print(f"   → Test if gradual change improves results")

print("\n3. Mixed entanglement:")
print(f"   → Layer 1: {best_ent[0]} (best performer)")
print(f"   → Layer 2-3: {sorted(entanglement_types.keys())[1]}")
print(f"   → Test if heterogeneous entanglement helps")

print("\n" + "=" * 70)
print("  ✅ ANALYSIS COMPLETE")
print("=" * 70)
