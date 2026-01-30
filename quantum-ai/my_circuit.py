#!/usr/bin/env python3
"""
Custom Quantum Circuit Collection
Multiple quantum circuits with different configurations
"""
import pennylane as qml
import numpy as np
import matplotlib.pyplot as plt

print("=" * 70)
print("  QUANTUM CIRCUIT PLAYGROUND")
print("=" * 70)

# Create a quantum device
n_qubits = 3
dev = qml.device('lightning.qubit', wires=n_qubits, shots=1000)

@qml.qnode(dev)
def my_circuit(params):
    """
    Custom 3-qubit quantum circuit with:
    - Superposition (Hadamard gates)
    - Rotation gates (parameterized)
    - Entanglement (CNOT gates)
    - Measurements
    """
    # Step 1: Create superposition on all qubits
    for i in range(n_qubits):
        qml.Hadamard(wires=i)
    
    # Step 2: Apply parameterized rotations
    qml.RY(params[0], wires=0)
    qml.RZ(params[1], wires=1)
    qml.RX(params[2], wires=2)
    
    # Step 3: Create entanglement
    qml.CNOT(wires=[0, 1])
    qml.CNOT(wires=[1, 2])
    
    # Step 4: More rotations
    qml.RY(params[3], wires=0)
    qml.RZ(params[4], wires=1)
    
    # Return measurement probabilities
    return qml.probs(wires=range(n_qubits))

# Run the circuit with sample parameters
print("\n[1] Circuit Configuration:")
print(f"  • Qubits: {n_qubits}")
print(f"  • Device: {dev.name}")
print(f"  • Shots: {dev.shots}")

# Test parameters
params = np.array([0.5, 1.0, 0.3, 0.8, 0.4])
print(f"\n[2] Running circuit with parameters: {params.tolist()}")

# Execute
results = my_circuit(params)

print(f"\n[3] Measurement Results:")
print(f"  • Total states: {len(results)}")
print(f"\n  Top 5 probable states:")
for i, prob in enumerate(results):
    if prob > 0.05:  # Show states with >5% probability
        binary = format(i, f'0{n_qubits}b')
        print(f"    |{binary}⟩ (decimal {i}): {prob:.3f} ({prob*100:.1f}%)")

# Visualize circuit
print(f"\n[4] Circuit Diagram:")
print("-" * 70)
print(qml.draw(my_circuit)(params))

# Visualize results
print(f"\n[5] Creating probability distribution plot...")
fig, ax = plt.subplots(figsize=(12, 6))
states = [format(i, f'0{n_qubits}b') for i in range(len(results))]
bars = ax.bar(states, results, color='steelblue', edgecolor='black', linewidth=1.5)

# Highlight high-probability states
for i, bar in enumerate(bars):
    if results[i] > 0.1:
        bar.set_color('coral')

ax.set_xlabel('Quantum State', fontsize=12, fontweight='bold')
ax.set_ylabel('Probability', fontsize=12, fontweight='bold')
ax.set_title('Quantum Circuit Measurement Results', fontsize=14, fontweight='bold')
ax.grid(axis='y', alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('my_circuit_results.png', dpi=150, bbox_inches='tight')
print(f"  ✓ Saved to: my_circuit_results.png")

# Try different parameters
print(f"\n[6] Testing with different parameters...")
test_params = [
    np.array([0.0, 0.0, 0.0, 0.0, 0.0]),  # No rotations
    np.array([np.pi, np.pi, np.pi, 0.0, 0.0]),  # π rotations
    np.array([np.pi/2, np.pi/2, np.pi/2, np.pi/2, np.pi/2]),  # π/2 rotations
]

for i, test_p in enumerate(test_params):
    test_result = my_circuit(test_p)
    max_prob = np.max(test_result)
    max_state = format(np.argmax(test_result), f'0{n_qubits}b')
    print(f"  Test {i+1}: max_state=|{max_state}⟩ prob={max_prob:.3f}")

print("\n" + "=" * 70)
print("  CIRCUIT #2: BELL STATE (Maximum Entanglement)")
print("=" * 70)

@qml.qnode(dev)
def bell_circuit():
    """Create Bell state |Φ+⟩ = (|00⟩ + |11⟩)/√2"""
    qml.Hadamard(wires=0)
    qml.CNOT(wires=[0, 1])
    return qml.probs(wires=[0, 1])

bell_probs = bell_circuit()
print("\nBell State Results:")
print("  |00⟩:", f"{bell_probs[0]:.3f}")
print("  |01⟩:", f"{bell_probs[1]:.3f}")
print("  |10⟩:", f"{bell_probs[2]:.3f}")
print("  |11⟩:", f"{bell_probs[3]:.3f}")
print("  → Perfect correlation! Measuring qubit 0 determines qubit 1")

print("\n" + "=" * 70)
print("  CIRCUIT #3: GHZ STATE (3-Qubit Entanglement)")
print("=" * 70)

@qml.qnode(dev)
def ghz_circuit():
    """Create GHZ state |GHZ⟩ = (|000⟩ + |111⟩)/√2"""
    qml.Hadamard(wires=0)
    qml.CNOT(wires=[0, 1])
    qml.CNOT(wires=[1, 2])
    return qml.probs(wires=range(3))

ghz_probs = ghz_circuit()
print("\nGHZ State Results:")
for i in [0, 7]:  # Only show |000⟩ and |111⟩
    binary = format(i, '03b')
    print(f"  |{binary}⟩:", f"{ghz_probs[i]:.3f}")
print("  → All qubits perfectly entangled!")

print("\n" + "=" * 70)
print("  CIRCUIT #4: QUANTUM INTERFERENCE")
print("=" * 70)

@qml.qnode(dev)
def interference_circuit(theta):
    """Demonstrate quantum interference"""
    qml.Hadamard(wires=0)
    qml.RZ(theta, wires=0)
    qml.Hadamard(wires=0)
    return qml.probs(wires=0)

theta_vals = np.linspace(0, 2*np.pi, 50)
probs_0 = [interference_circuit(t)[0] for t in theta_vals]

plt.figure(figsize=(10, 6))
plt.plot(theta_vals, probs_0, 'b-', linewidth=2, label='|0⟩ probability')
plt.plot(theta_vals, [1-p for p in probs_0], 'r-', linewidth=2, label='|1⟩ probability')
plt.xlabel('Rotation Angle θ (radians)', fontsize=12, fontweight='bold')
plt.ylabel('Probability', fontsize=12, fontweight='bold')
plt.title('Quantum Interference Pattern', fontsize=14, fontweight='bold')
plt.legend(fontsize=11)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('interference_pattern.png', dpi=150, bbox_inches='tight')
print("✓ Interference pattern saved to: interference_pattern.png")

print("\n" + "=" * 70)
print("  CIRCUIT #5: TOFFOLI GATE (3-Qubit Logic)")
print("=" * 70)

@qml.qnode(dev)
def toffoli_circuit(state):
    """Toffoli gate (CCNOT): flips target if both controls are |1⟩"""
    # Prepare input state
    if state[0]:
        qml.PauliX(wires=0)
    if state[1]:
        qml.PauliX(wires=1)
    if state[2]:
        qml.PauliX(wires=2)
    
    # Apply Toffoli
    qml.Toffoli(wires=[0, 1, 2])
    
    return qml.probs(wires=range(3))

print("\nToffoli Truth Table:")
print("  Input  → Output")
test_states = [[0,0,0], [0,0,1], [0,1,0], [0,1,1], 
               [1,0,0], [1,0,1], [1,1,0], [1,1,1]]
for state in test_states:
    result = toffoli_circuit(state)
    output_state = np.argmax(result)
    in_bin = ''.join(map(str, state))
    out_bin = format(output_state, '03b')
    print(f"  |{in_bin}⟩ → |{out_bin}⟩")

print("\n" + "=" * 70)
print("  CIRCUIT #6: PHASE KICKBACK")
print("=" * 70)

@qml.qnode(dev)
def phase_kickback_circuit(theta):
    """Demonstrate phase kickback phenomenon"""
    # Control qubit in superposition
    qml.Hadamard(wires=0)
    
    # Target qubit in |1⟩
    qml.PauliX(wires=1)
    
    # Controlled rotation
    qml.ControlledPhaseShift(theta, wires=[0, 1])
    
    # Hadamard on control to see phase
    qml.Hadamard(wires=0)
    
    return qml.probs(wires=0)

test_theta = np.pi/2
pk_probs = phase_kickback_circuit(test_theta)
print(f"\nPhase Kickback (θ={test_theta:.2f}):")
print(f"  Control |0⟩: {pk_probs[0]:.3f}")
print(f"  Control |1⟩: {pk_probs[1]:.3f}")
print("  → Phase information transferred from target to control!")

print("\n" + "=" * 70)
print("  ✓ ALL CIRCUITS COMPLETE!")
print("=" * 70)
print("\nGenerated files:")
print("  • my_circuit_results.png - Original parameterized circuit")
print("  • interference_pattern.png - Quantum interference visualization")
print("\nCircuits demonstrated:")
print("  1. Parameterized VQC (rotation + entanglement)")
print("  2. Bell State (2-qubit entanglement)")
print("  3. GHZ State (3-qubit entanglement)")
print("  4. Quantum Interference (H-RZ-H)")
print("  5. Toffoli Gate (3-qubit logic)")
print("  6. Phase Kickback (quantum phase transfer)")
print("=" * 70)
