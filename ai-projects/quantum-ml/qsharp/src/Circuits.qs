/// Fundamental quantum circuits for the Aria quantum-ML project.
/// Covers: Bell states, GHZ, QFT, Grover's search, and a variational
/// quantum classifier layer that mirrors QuantumClassifier in Python.

namespace Aria.Quantum {

    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Measurement;
    open Microsoft.Quantum.Math;
    open Microsoft.Quantum.Arrays;
    open Microsoft.Quantum.Convert;

    // ─────────────────────────────────────────────────────────────────
    // 1. Bell States
    // ─────────────────────────────────────────────────────────────────

    /// Prepare the |Φ⁺⟩ = (|00⟩ + |11⟩)/√2 Bell state and measure.
    /// Returns (qubit0_result, qubit1_result) — always equal for Φ⁺.
    operation BellStatePhi() : (Result, Result) {
        use (q0, q1) = (Qubit(), Qubit());
        H(q0);
        CNOT(q0, q1);
        let r0 = M(q0);
        let r1 = M(q1);
        Reset(q0);
        Reset(q1);
        return (r0, r1);
    }

    /// Prepare one of the four Bell states by choosing |ψ⟩ = X^b1 Z^b0 |Φ⁺⟩.
    /// b0 = phase flip, b1 = bit flip.
    operation PrepBellState(b0 : Bool, b1 : Bool) : (Result, Result) {
        use (q0, q1) = (Qubit(), Qubit());
        H(q0);
        CNOT(q0, q1);
        if b0 { Z(q0); }
        if b1 { X(q0); }
        let r0 = M(q0);
        let r1 = M(q1);
        Reset(q0);
        Reset(q1);
        return (r0, r1);
    }

    // ─────────────────────────────────────────────────────────────────
    // 2. GHZ State  (n-qubit generalisation of Bell)
    // ─────────────────────────────────────────────────────────────────

    /// Prepare the n-qubit GHZ state (|00…0⟩ + |11…1⟩)/√2 and measure all.
    operation GHZState(n : Int) : Result[] {
        use qubits = Qubit[n];
        H(qubits[0]);
        for i in 1 .. n - 1 {
            CNOT(qubits[0], qubits[i]);
        }
        let results = MeasureEachZ(qubits);
        ResetAll(qubits);
        return results;
    }

    // ─────────────────────────────────────────────────────────────────
    // 3. Quantum Fourier Transform
    // ─────────────────────────────────────────────────────────────────

    /// Apply the QFT to a register in-place.
    operation QFT(register : Qubit[]) : Unit is Adj + Ctl {
        let n = Length(register);
        for i in 0 .. n - 1 {
            H(register[i]);
            for j in i + 1 .. n - 1 {
                let angle = 2.0 * PI() / IntAsDouble(1 <<< (j - i + 1));
                Controlled R1([register[j]], (angle, register[i]));
            }
        }
        // Reverse qubit order to match standard convention.
        for i in 0 .. n / 2 - 1 {
            SWAP(register[i], register[n - 1 - i]);
        }
    }

    /// Prepare a computational basis state |x⟩ then apply QFT and measure.
    operation RunQFT(x : Int, n : Int) : Result[] {
        use qubits = Qubit[n];
        // Encode x in binary.
        let bits = IntAsBoolArray(x, n);
        for i in 0 .. n - 1 {
            if bits[i] { X(qubits[i]); }
        }
        QFT(qubits);
        let results = MeasureEachZ(qubits);
        ResetAll(qubits);
        return results;
    }

    // ─────────────────────────────────────────────────────────────────
    // 4. Grover's Search  (2-qubit oracle marking |11⟩)
    // ─────────────────────────────────────────────────────────────────

    /// Oracle that marks the state |11⟩ with a phase flip.
    operation GroverOracle(qubits : Qubit[]) : Unit is Adj + Ctl {
        Controlled Z([qubits[0]], qubits[1]);
    }

    /// Grover diffusion (inversion-about-average) operator.
    operation GroverDiffusion(qubits : Qubit[]) : Unit is Adj + Ctl {
        ApplyToEachCA(H, qubits);
        ApplyToEachCA(X, qubits);
        Controlled Z([qubits[0]], qubits[1]);
        ApplyToEachCA(X, qubits);
        ApplyToEachCA(H, qubits);
    }

    /// Run Grover's algorithm (iterations rounds) and return the found state.
    /// For 2 qubits and oracle marking |11⟩, 1 iteration is optimal.
    operation GroverSearch(iterations : Int) : Result[] {
        use qubits = Qubit[2];
        ApplyToEach(H, qubits);
        for _ in 1 .. iterations {
            GroverOracle(qubits);
            GroverDiffusion(qubits);
        }
        let results = MeasureEachZ(qubits);
        ResetAll(qubits);
        return results;
    }

    // ─────────────────────────────────────────────────────────────────
    // 5. Variational Quantum Classifier layer
    //    Mirrors QuantumClassifier in ai-projects/quantum-ml/src/
    //    Each layer: Ry rotations on all qubits → entangling CNOT ring.
    // ─────────────────────────────────────────────────────────────────

    /// Apply one variational layer: Ry(θ_i) on each qubit followed by a
    /// circular CNOT chain for entanglement.
    operation VQCLayer(qubits : Qubit[], thetas : Double[]) : Unit is Adj + Ctl {
        let n = Length(qubits);
        for i in 0 .. n - 1 {
            Ry(thetas[i], qubits[i]);
        }
        // Circular entanglement: q[0]→q[1]→…→q[n-1]→q[0]
        for i in 0 .. n - 1 {
            CNOT(qubits[i], qubits[(i + 1) % n]);
        }
    }

    /// Run a 2-layer VQC on `nQubits` qubits with parameter vector `params`
    /// (length = 2 * nQubits) and return measurement probabilities via shots.
    /// Returns Result[] from a single shot; repeat externally for statistics.
    operation RunVQC(nQubits : Int, params : Double[]) : Result[] {
        use qubits = Qubit[nQubits];
        // Layer 0: params[0 .. nQubits-1]
        VQCLayer(qubits, params[0 .. nQubits - 1]);
        // Layer 1: params[nQubits .. 2*nQubits-1]
        VQCLayer(qubits, params[nQubits .. 2 * nQubits - 1]);
        let results = MeasureEachZ(qubits);
        ResetAll(qubits);
        return results;
    }

    // ─────────────────────────────────────────────────────────────────
    // 6. Entry point — demonstrate all circuits
    // ─────────────────────────────────────────────────────────────────

    @EntryPoint()
    operation Main() : Unit {
        // Bell state
        let (r0, r1) = BellStatePhi();
        Message($"Bell |Φ⁺⟩ → q0={r0}, q1={r1} (should match)");

        // GHZ 3-qubit
        let ghz = GHZState(3);
        Message($"GHZ(3) → {ghz} (all same)");

        // QFT on |3⟩ (binary 11) with 2 qubits
        let qft = RunQFT(3, 2);
        Message($"QFT(|3⟩, 2 qubits) → {qft}");

        // Grover 2-qubit, 1 iteration — should return [One, One] with high prob
        let grover = GroverSearch(1);
        Message($"Grover search (marking |11⟩) → {grover}");

        // VQC: 3 qubits, 2 layers, all angles = π/4
        let nQ = 3;
        let pi4 = PI() / 4.0;
        let params = [pi4, pi4, pi4, pi4, pi4, pi4];
        let vqc = RunVQC(nQ, params);
        Message($"VQC(3 qubits, 2 layers, θ=π/4) → {vqc}");
    }
}
