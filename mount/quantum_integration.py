"""
Quantum AI Integration Module
Interfaces with quantum-ai training, circuits, and Azure Quantum
"""

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

import yaml


class QuantumIntegration:
    """Integration layer for quantum AI operations"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.workspace_root = Path(config["paths"]["workspace_root"])
        self.quantum_path = Path(config["paths"]["quantum_ai"])
        self.results_dir = Path(config["quantum"].get(
            "results_dir") or (self.quantum_path / "results"))
        self.quantum_config = self._load_quantum_config()

    def _load_quantum_config(self) -> Dict[str, Any]:
        """Load quantum configuration from YAML"""
        configured = self.config["quantum"].get("config_file")
        config_path = Path(
            configured) if configured else self.quantum_path / "config" / "quantum_config.yaml"
        if config_path.exists():
            with open(config_path) as f:
                return yaml.safe_load(f)
        return {}

    async def get_status(self) -> Dict[str, Any]:
        """Get current quantum system status"""
        return {
            "enabled": self.config["quantum"]["enabled"],
            "backend": self.config["quantum"].get("default_backend", "qiskit_aer"),
            "mcp_server": self.config["quantum"].get("mcp_server_enabled", False),
            "azure_connected": self._check_azure_connection(),
            "available_backends": self._get_available_backends(),
            "recent_results": self._get_recent_results(),
        }

    def _check_azure_connection(self) -> bool:
        """Check if Azure Quantum is configured and connected"""
        azure_config = self.quantum_config.get("azure", {})
        return bool(
            azure_config.get("subscription_id")
            and azure_config.get("resource_group")
            and azure_config.get("workspace_name")
        )

    def _get_available_backends(self) -> List[str]:
        """Get list of available quantum backends"""
        backends = ["qiskit_aer", "lightning.qubit"]
        if self._check_azure_connection():
            backends.extend(["rigetti.sim.qvm", "ionq.simulator"])
        return backends

    def _get_recent_results(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent quantum training results"""
        results = []
        results_path = self.results_dir

        if not results_path.exists():
            return results

        # Find all JSON result files
        json_files = sorted(results_path.glob(
            "*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]

        for json_file in json_files:
            try:
                with open(json_file) as f:
                    data = json.load(f)
                    results.append(
                        {
                            "file": json_file.name,
                            "timestamp": data.get("timestamp"),
                            "dataset": data.get("dataset"),
                            "accuracy": data.get("test_accuracy"),
                            "backend": data.get("backend"),
                        }
                    )
            except Exception:
                continue

        return results

    @staticmethod
    def _find_job_status(status_data: Dict[str, Any], job_name: str) -> Dict[str, Any]:
        """Return the most relevant job entry from a status payload.

        The quantum autorun status file has historically used both list- and
        dict-shaped ``jobs`` payloads.  This helper keeps the bridge resilient
        to either format while preserving the per-job details callers expect.
        """
        jobs = status_data.get("jobs")
        if isinstance(jobs, dict):
            entry = jobs.get(job_name)
            return entry if isinstance(entry, dict) else {}

        if isinstance(jobs, list):
            normalized_job_name = job_name.strip().lower()
            for index, entry in enumerate(jobs):
                if not isinstance(entry, dict):
                    continue

                candidate_names = [entry.get("name"), entry.get(
                    "job_name"), entry.get("preset")]
                for candidate in candidate_names:
                    if isinstance(candidate, str) and candidate.strip().lower() == normalized_job_name:
                        return entry

                if len(jobs) == 1:
                    # Preserve backward compatibility with single-job snapshots
                    # even when the stored name is absent or slightly different.
                    return entry

        return {}

    async def train_classifier(
        self,
        dataset: str,
        n_qubits: int = 4,
        n_layers: int = 2,
        epochs: int = 10,
        backend: str = "qiskit_aer",
    ) -> Dict[str, Any]:
        """Train a quantum classifier"""
        try:
            train_script = self.quantum_path / "train_custom_dataset.py"
            resolved_quantum_path = self.quantum_path.resolve()
            resolved_train_script = train_script.resolve()

            if resolved_train_script.parent != resolved_quantum_path or resolved_train_script.name != "train_custom_dataset.py":
                return {
                    "success": False,
                    "error": "Invalid training script path.",
                }

            datasets_path = self.workspace_root / "datasets" / "quantum"
            allowed_datasets = (
                {csv_file.stem for csv_file in datasets_path.glob(
                    "*.csv")} if datasets_path.exists() else set()
            )

            safe_arg_pattern = re.compile(r"^[A-Za-z0-9_.-]+$")

            if not safe_arg_pattern.fullmatch(dataset):
                return {
                    "success": False,
                    "error": f"Invalid dataset '{dataset}'.",
                }

            if dataset not in allowed_datasets:
                return {
                    "success": False,
                    "error": f"Invalid dataset '{dataset}'.",
                }
            safe_dataset = next((name for name in allowed_datasets if name == dataset), None)
            if safe_dataset is None:
                return {
                    "success": False,
                    "error": f"Invalid dataset '{dataset}'.",
                }

            allowed_backends = set(self._get_available_backends())
            if not safe_arg_pattern.fullmatch(backend):
                return {
                    "success": False,
                    "error": f"Invalid backend '{backend}'.",
                }

            if backend not in allowed_backends:
                return {
                    "success": False,
                    "error": f"Invalid backend '{backend}'.",
                }
            safe_backend = next((name for name in allowed_backends if name == backend), None)
            if safe_backend is None:
                return {
                    "success": False,
                    "error": f"Invalid backend '{backend}'.",
                }

            if not isinstance(epochs, int) or isinstance(epochs, bool) or epochs < 1 or epochs > 10000:
                return {
                    "success": False,
                    "error": f"Invalid epochs '{epochs}'.",
                }
            safe_epochs = epochs

            cmd = [
                sys.executable,
                str(resolved_train_script),
                "--preset",
                safe_dataset,
                "--epochs",
                str(safe_epochs),
                "--backend",
                safe_backend,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(
                self.quantum_path), shell=False)

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def list_datasets(self) -> List[Dict[str, Any]]:
        """List available quantum datasets"""
        datasets_path = self.workspace_root / "datasets" / "quantum"

        if not datasets_path.exists():
            return []

        datasets = []
        for csv_file in datasets_path.glob("*.csv"):
            datasets.append(
                {
                    "name": csv_file.stem,
                    "path": str(csv_file),
                    "size_mb": csv_file.stat().st_size / (1024 * 1024),
                }
            )

        return datasets

    async def get_circuit_info(self, circuit_type: str = "variational") -> Dict[str, Any]:
        """Get information about quantum circuit types"""
        return {
            "circuit_type": circuit_type,
            "entanglement_modes": ["linear", "circular", "full"],
            "supported_gates": ["RY", "RZ", "CNOT", "H", "X"],
            "max_qubits": 20,  # Local simulator limit
            "layer_structure": {
                "input": "RY encoding",
                "variational": "RY/RZ + entanglement",
                "measurement": "PauliZ",
            },
        }

    async def run_autorun_job(self, job_name: str, dry_run: bool = False) -> Dict[str, Any]:
        """Run a quantum autorun job"""
        try:
            autorun_script = self.workspace_root / "scripts" / "quantum_autorun.py"
            normalized_job_name = (job_name or "").strip()

            allowed_jobs = {
                "baseline": "baseline",
                "benchmark": "benchmark",
                "nightly": "nightly",
                "smoke": "smoke",
            }
            selected_job = allowed_jobs.get(normalized_job_name)
            if selected_job is None:
                return {
                    "success": False,
                    "error": "Invalid job_name. Allowed values: baseline, benchmark, nightly, smoke.",
                }

            cmd = [sys.executable, str(
                autorun_script), "--job", selected_job]
            if dry_run:
                cmd.append("--dry-run")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.workspace_root),
                check=False,
            )

            # Load status file if it exists
            status_file = self.workspace_root / "data_out" / "quantum_autorun" / "status.json"
            status_data = {}
            if status_file.exists():
                with open(status_file) as f:
                    status_data = json.load(f)

            return {
                "success": result.returncode == 0,
                "job_name": normalized_job_name,
                "dry_run": dry_run,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "status": self._find_job_status(status_data, normalized_job_name),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
