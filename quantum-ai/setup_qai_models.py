#!/usr/bin/env python
"""
QAI Models Setup Script
========================
Initializes quantum-AI models, checkpoints, and configurations.
Ensures all models are ready for training and inference.
"""

import os
import sys
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add quantum-ai src to path
QAI_ROOT = Path(__file__).parent
sys.path.insert(0, str(QAI_ROOT / "src"))

def create_checkpoint_registry() -> Dict[str, Any]:
    """Create model registry for tracking trained models."""
    registry = {
        "created_at": datetime.now().isoformat(),
        "models": {
            "quantum_classifier": {
                "type": "hybrid_quantum_classical",
                "framework": "pennylane",
                "status": "ready",
                "checkpoint": None,
                "config": {
                    "n_qubits": 4,
                    "n_layers": 2,
                    "backend": "lightning.qubit"
                }
            },
            "variational_circuit": {
                "type": "parametrized_quantum_circuit",
                "framework": "pennylane",
                "status": "ready",
                "checkpoint": None,
                "config": {
                    "n_qubits": 4,
                    "n_layers": 3,
                    "encoding": "angle"
                }
            },
            "grover_circuit": {
                "type": "quantum_algorithm",
                "framework": "qiskit",
                "status": "ready",
                "checkpoint": None,
                "config": {
                    "n_qubits": 3,
                    "shots": 1000
                }
            },
            "ensemble_classifier": {
                "type": "ensemble_quantum_classical",
                "framework": "hybrid",
                "status": "ready",
                "checkpoint": None,
                "config": {
                    "n_models": 3,
                    "voting": "soft"
                }
            }
        },
        "datasets": {
            "moons": {"status": "available", "features": 2, "samples": 300},
            "iris": {"status": "available", "features": 4, "samples": 150},
            "banknote": {"status": "available", "features": 4, "samples": 1372}
        },
        "performance_targets": {
            "quantum_classifier_accuracy": 0.80,
            "variational_circuit_loss": 0.1,
            "training_time_seconds": 300
        }
    }
    return registry

def verify_dependencies() -> bool:
    """Verify that all required dependencies are installed."""
    required_packages = {
        "qiskit": "Qiskit",
        "pennylane": "PennyLane",
        "torch": "PyTorch",
        "azure": "Azure SDK"
    }
    
    print("\n" + "="*60)
    print("📦 VERIFYING DEPENDENCIES")
    print("="*60)
    
    missing = []
    for module, name in required_packages.items():
        try:
            __import__(module)
            print(f"✅ {name:20s} - Installed")
        except ImportError:
            print(f"❌ {name:20s} - MISSING")
            missing.append(module)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    print("\n✅ All dependencies verified!")
    return True

def setup_checkpoint_structure() -> Path:
    """Create and organize checkpoint directory structure."""
    print("\n" + "="*60)
    print("📁 SETTING UP CHECKPOINT STRUCTURE")
    print("="*60)
    
    checkpoint_root = QAI_ROOT / "checkpoints"
    checkpoint_root.mkdir(exist_ok=True)
    
    subdirs = [
        "quantum_classifier",
        "variational_circuits",
        "grover_algorithms",
        "ensemble_models",
        "best_models",
        "experiments",
        "backups"
    ]
    
    for subdir in subdirs:
        path = checkpoint_root / subdir
        path.mkdir(exist_ok=True)
        print(f"✅ {path.relative_to(QAI_ROOT)}")
    
    return checkpoint_root

def load_quantum_config() -> Dict[str, Any]:
    """Load quantum configuration from YAML."""
    config_file = QAI_ROOT / "config" / "quantum_config.yaml"
    
    print("\n" + "="*60)
    print("⚙️  LOADING QUANTUM CONFIGURATION")
    print("="*60)
    
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        print(f"✅ Loaded: {config_file.relative_to(QAI_ROOT)}")
        
        # Display key settings
        print("\n📊 Current Configuration:")
        print(f"  • Qubits: {config['ml']['model']['n_qubits']}")
        print(f"  • Layers: {config['ml']['model']['n_layers']}")
        print(f"  • Backend: {config['quantum']['simulator']['backend']}")
        print(f"  • Shots: {config['quantum']['simulator']['shots']}")
        print(f"  • Epochs: {config['ml']['training']['epochs']}")
        print(f"  • Learning Rate: {config['ml']['training']['learning_rate']}")
        
        return config
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return {}

def initialize_models() -> Dict[str, Any]:
    """Initialize core quantum models."""
    print("\n" + "="*60)
    print("🔧 INITIALIZING QUANTUM MODELS")
    print("="*60)
    
    models_status = {}
    
    # Test quantum classifier import
    try:
        from quantum_classifier import QuantumClassifier
        print("✅ Quantum Classifier - Ready")
        models_status["quantum_classifier"] = "ready"
    except ImportError as e:
        print(f"⚠️  Quantum Classifier - {e}")
        models_status["quantum_classifier"] = "import_error"
    
    # Test enhanced variational circuit
    try:
        from enhanced_variational_circuit import EnhancedVariationalCircuit
        print("✅ Enhanced Variational Circuit - Ready")
        models_status["variational_circuit"] = "ready"
    except ImportError as e:
        print(f"⚠️  Enhanced Variational Circuit - {e}")
        models_status["variational_circuit"] = "import_error"
    
    # Test Grover circuit
    try:
        from grover_circuit import GroverCircuit
        print("✅ Grover Circuit - Ready")
        models_status["grover_circuit"] = "ready"
    except ImportError as e:
        print(f"⚠️  Grover Circuit - {e}")
        models_status["grover_circuit"] = "import_error"
    
    # Test circuit visualizer
    try:
        from circuit_visualizer import CircuitVisualizer
        print("✅ Circuit Visualizer - Ready")
        models_status["circuit_visualizer"] = "ready"
    except ImportError as e:
        print(f"⚠️  Circuit Visualizer - {e}")
        models_status["circuit_visualizer"] = "import_error"
    
    return models_status

def save_setup_report(report: Dict[str, Any]) -> None:
    """Save setup report to file."""
    report_file = QAI_ROOT / "SETUP_REPORT.json"
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Report saved: {report_file.relative_to(QAI_ROOT)}")

def print_summary(report: Dict[str, Any]) -> None:
    """Print setup summary."""
    print("\n" + "="*60)
    print("📋 SETUP SUMMARY")
    print("="*60)
    
    print(f"\n✅ Checkpoint structure: Created")
    print(f"✅ Configuration loaded: {report.get('config_loaded', False)}")
    
    models_status = report.get("models_status", {})
    ready_count = sum(1 for s in models_status.values() if s == "ready")
    print(f"✅ Models initialized: {ready_count}/{len(models_status)}")
    
    print("\n📦 Model Registry:")
    for model, status in models_status.items():
        symbol = "✅" if status == "ready" else "⚠️ "
        print(f"  {symbol} {model}: {status}")
    
    print("\n🚀 Next Steps:")
    print("  1. Run training: python ./examples/train_models.py")
    print("  2. Test locally: python ./examples/run_simulations.py")
    print("  3. View dashboard: ./start_dashboard.sh")
    print("  4. Submit to Azure: python ./azure_quantum_deploy.py")
    print("\n" + "="*60)

def main() -> None:
    """Main setup routine."""
    print("\n" + "="*60)
    print("🚀 QAI MODELS SETUP")
    print("="*60)
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "workspace": str(QAI_ROOT),
        "python_version": sys.version,
        "status": "in_progress"
    }
    
    # 1. Verify dependencies
    if not verify_dependencies():
        report["status"] = "failed_dependencies"
        save_setup_report(report)
        print("\n⚠️  Please install missing dependencies first.")
        return
    
    # 2. Load configuration
    config = load_quantum_config()
    report["config_loaded"] = bool(config)
    
    # 3. Setup checkpoints
    checkpoint_dir = setup_checkpoint_structure()
    report["checkpoint_dir"] = str(checkpoint_dir)
    
    # 4. Create model registry
    registry = create_checkpoint_registry()
    registry_file = checkpoint_dir / "registry.json"
    with open(registry_file, 'w') as f:
        json.dump(registry, f, indent=2)
    print(f"\n✅ Model registry: {registry_file.relative_to(QAI_ROOT)}")
    report["registry_file"] = str(registry_file)
    
    # 5. Initialize models
    models_status = initialize_models()
    report["models_status"] = models_status
    
    # 6. Create data directories
    data_dirs = [
        QAI_ROOT / "data_out" / "quantum_training",
        QAI_ROOT / "data_out" / "quantum_inference",
        QAI_ROOT / "results" / "visualizations"
    ]
    for data_dir in data_dirs:
        data_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n✅ Data directories created: {len(data_dirs)}")
    
    report["status"] = "completed"
    report["completion_time"] = datetime.now().isoformat()
    
    # 7. Save report
    save_setup_report(report)
    
    # 8. Print summary
    print_summary(report)

if __name__ == "__main__":
    main()
