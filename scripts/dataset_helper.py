#!/usr/bin/env python3
"""
Quick dataset loading helper for training scripts.

Provides convenience functions to load common datasets used in training.
"""
from pathlib import Path
import sys

# Add parent directory to path so we can import from quantum.src
sys.path.insert(0, str(Path(__file__).parent.parent))

from quantum.src.dataset_loader import load_dataset, preprocess_for_qubits
import numpy as np
from typing import Tuple, Optional

AVAILABLE_QUANTUM = [
    'ionosphere', 'sonar', 'heart_disease', 'banknote', 'digits',
    'california_housing', 'quantum_xor', 'concentric_rings',
    'crescent_moons', 'entangled_features', 'letter_recognition',
    'mushroom', 'optical_digits'
]

AVAILABLE_CHAT = [
    'aria_persona', 'aria_expanded', 'aria_movement', 'aria_simple',
    'coding_instructions', 'dolly', 'openassistant', 'mixed_chat'
]

def quick_load_quantum(name: str, train_size: int = 0.8) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Quick load and split a quantum dataset.

    Args:
        name: Dataset name (e.g., 'ionosphere', 'quantum_xor')
        train_size: Fraction for training (rest is validation)

    Returns:
        X_train, X_val, y_train, y_val (numpy arrays)
    """
    X, y, _ = load_dataset(name, return_feature_names=False)

    split_idx = int(len(X) * train_size)
    indices = np.random.permutation(len(X))
    train_idx, val_idx = indices[:split_idx], indices[split_idx:]

    return X[train_idx], X[val_idx], y[train_idx], y[val_idx]

def quick_load_for_qubits(name: str, n_qubits: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Load a dataset and preprocess it for quantum circuits with n qubits.

    Args:
        name: Dataset name
        n_qubits: Number of qubits (determines dimensionality)

    Returns:
        X_train, X_val, y_train, y_val (all preprocessed and dimensionality-matched)
    """
    X_train, X_val, y_train, y_val = quick_load_quantum(name)
    X_train, X_val, _, _ = preprocess_for_qubits(X_train, X_val, n_qubits)
    return X_train, X_val, y_train, y_val

def list_available() -> None:
    """Print available datasets by category."""
    print("\n=== Available Quantum Datasets ===")
    for ds in AVAILABLE_QUANTUM:
        print(f"  • {ds}")
    print(f"\nTotal: {len(AVAILABLE_QUANTUM)} quantum datasets")

    print("\n=== Available Chat Datasets ===")
    for ds in AVAILABLE_CHAT:
        print(f"  • {ds}")
    print(f"\nTotal: {len(AVAILABLE_CHAT)} chat datasets")

if __name__ == '__main__':
    list_available()
