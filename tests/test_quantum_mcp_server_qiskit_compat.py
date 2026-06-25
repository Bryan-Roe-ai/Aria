"""Regression tests for local/simulator-safe quantum MCP compatibility paths."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
QUANTUM_ML_DIR = REPO_ROOT / "ai-projects" / "quantum-ml"
if str(QUANTUM_ML_DIR) not in sys.path:
    sys.path.insert(0, str(QUANTUM_ML_DIR))
SRC_DIR = QUANTUM_ML_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def _run(coro):
    """Run a coroutine synchronously."""
    return asyncio.run(coro)


@pytest.mark.unit
def test_create_circuit_handler_uses_qasm2_when_legacy_qasm_is_unavailable(
    monkeypatch: pytest.MonkeyPatch,
):
    """Circuit creation should stay compatible with Qiskit builds that prefer qasm2.dumps."""
    try:
        import quantum_mcp_server as mcp_server
        from qiskit import QuantumCircuit
    except (ImportError, SystemExit):
        pytest.skip("quantum_mcp_server dependencies not installed")

    fake_circuit = QuantumCircuit(1, 1)
    fake_circuit.h(0)
    fake_circuit.measure(0, 0)
    fake_circuit.qasm = None
    isolated_cache = mcp_server.CircuitCache(max_size=4, ttl_seconds=60)

    monkeypatch.setitem(mcp_server.quantum_state, "circuit_cache", isolated_cache)
    monkeypatch.setattr(mcp_server, "_create_circuit_sync", lambda *_args, **_kwargs: fake_circuit)
    monkeypatch.setattr(
        mcp_server,
        "qiskit_qasm2",
        SimpleNamespace(dumps=lambda circuit: "OPENQASM 2.0; // compat export"),
    )

    result = _run(
        mcp_server.create_circuit_handler(
            {
                "n_qubits": 1,
                "circuit_type": "custom",
                "gates": [{"gate": "h", "qubit": 0}],
            }
        )
    )

    assert len(result) == 1
    assert "Created quantum circuit" in result[0].text
    circuit_id = result[0].text.split("Circuit ID: ", 1)[1].splitlines()[0]
    assert isolated_cache.get(circuit_id) is fake_circuit


@pytest.mark.unit
def test_simulate_circuit_handler_retries_in_thread_pool_after_process_pool_failure(
    monkeypatch: pytest.MonkeyPatch,
):
    """Simulation should remain local/safe by falling back to the thread pool."""
    try:
        import quantum_mcp_server as mcp_server
        from qiskit import QuantumCircuit
    except (ImportError, SystemExit):
        pytest.skip("quantum_mcp_server dependencies not installed")

    circuit = QuantumCircuit(1, 1)
    circuit.h(0)
    circuit.measure(0, 0)

    isolated_cache = mcp_server.CircuitCache(max_size=4, ttl_seconds=60)
    monkeypatch.setitem(mcp_server.quantum_state, "circuit_cache", isolated_cache)
    isolated_cache.put("compat-fallback", circuit)

    executor_calls: list[object] = []

    class _LoopProbe:
        def run_in_executor(self, executor, _fn, *_args):
            executor_calls.append(executor)
            future = asyncio.get_running_loop().create_future()
            if len(executor_calls) == 1:
                future.set_exception(RuntimeError("qiskit process-pool compatibility failure"))
            else:
                future.set_result({"0": 3, "1": 1})
            return future

    monkeypatch.setattr(mcp_server.asyncio, "get_event_loop", lambda: _LoopProbe())

    result = _run(mcp_server.simulate_circuit_handler({"circuit_id": "compat-fallback", "shots": 4}))

    assert executor_calls == [mcp_server.cpu_executor, mcp_server.io_executor]
    assert len(result) == 1
    assert "Simulation results for circuit compat-fallback (4 shots):" in result[0].text
    assert "|0⟩: 3 (75.000%)" in result[0].text
    assert "|1⟩: 1 (25.000%)" in result[0].text
