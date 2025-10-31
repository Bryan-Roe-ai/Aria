"""
Train Quantum AI on Your Custom Dataset
========================================

Ready-to-use template for training on your own data.
Modify the load_your_data() function with your actual data source.

Author: Quantum AI System
Date: October 31, 2025
"""

import numpy as np
import pandas as pd
from pathlib import Path
import sys

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.hybrid_qnn import HybridQNN, QuantumClassicalTrainer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import torch
from torch.utils.data import TensorDataset, DataLoader
import matplotlib.pyplot as plt


def load_your_data():
    """
    ⚠️ MODIFY THIS FUNCTION WITH YOUR DATA SOURCE ⚠️
    
    Returns:
        X: numpy array of shape (n_samples, n_features)
        y: numpy array of shape (n_samples,) with class labels
    """
    
    # ============================================
    # OPTION 1: Load from CSV
    # ============================================
    # df = pd.read_csv("path/to/your/data.csv")
    # X = df.drop('label_column', axis=1).values
    # y = df['label_column'].values
    # return X, y
    
    # ============================================
    # OPTION 2: Load from NumPy files
    # ============================================
    # X = np.load("features.npy")
    # y = np.load("labels.npy")
    # return X, y
    
    # ============================================
    # OPTION 3: Use built-in dataset (DEMO)
    # ============================================
    # For demonstration, we'll use wine dataset
    from sklearn.datasets import load_wine
    data = load_wine()
    X = data.data
    y = (data.target == 0).astype(int)  # Binary: Class 0 vs Others
    
    print(f"📊 Loaded Wine dataset (demo)")
    print(f"   Modify load_your_data() to use your own data!")
    
    return X, y


def preprocess_data(X, y, n_qubits=4, test_size=0.2):
    """
    Preprocess data for quantum ML
    
    Args:
        X: Feature matrix
        y: Labels
        n_qubits: Number of qubits (features will be reduced/padded to match)
        test_size: Validation split ratio
    
    Returns:
        X_train, X_val, y_train, y_val: Preprocessed data
        scaler: Fitted StandardScaler (save this for inference!)
        pca: Fitted PCA (if used, else None)
    """
    print(f"\n🔧 Preprocessing data...")
    print(f"   Original shape: {X.shape}")
    print(f"   Classes: {np.unique(y)}")
    print(f"   Class distribution: {np.bincount(y)}")
    
    # Split data
    X_train, X_val, y_train, y_val = train_test_split(
        X, y,
        test_size=test_size,
        random_state=42,
        stratify=y  # Maintains class balance
    )
    
    # Standardize (CRITICAL for quantum circuits!)
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_val = scaler.transform(X_val)
    
    print(f"   ✅ Standardized (mean≈0, std≈1)")
    
    # Handle feature dimension
    n_features = X_train.shape[1]
    pca = None
    
    if n_features < n_qubits:
        # Pad with zeros
        padding_train = np.zeros((X_train.shape[0], n_qubits - n_features))
        X_train = np.hstack([X_train, padding_train])
        
        padding_val = np.zeros((X_val.shape[0], n_qubits - n_features))
        X_val = np.hstack([X_val, padding_val])
        
        print(f"   ✅ Padded from {n_features} to {n_qubits} features")
        
    elif n_features > n_qubits:
        # Use PCA to reduce dimensions
        pca = PCA(n_components=n_qubits)
        X_train = pca.fit_transform(X_train)
        X_val = pca.transform(X_val)
        
        explained_var = pca.explained_variance_ratio_.sum()
        print(f"   ✅ Reduced from {n_features} to {n_qubits} features using PCA")
        print(f"   ✅ Explained variance: {explained_var:.2%}")
    else:
        print(f"   ✅ Features already match qubits ({n_qubits})")
    
    print(f"   Final training shape: {X_train.shape}")
    print(f"   Final validation shape: {X_val.shape}")
    
    return X_train, X_val, y_train, y_val, scaler, pca


def plot_training_results(history, save_path="results/custom_training.png"):
    """Plot training curves"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    
    # Loss curves
    ax1.plot(history['train_loss'], label='Training Loss', linewidth=2)
    ax1.plot(history['val_loss'], label='Validation Loss', linewidth=2)
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Loss')
    ax1.set_title('Training Progress')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Accuracy curve
    ax2.plot(history['val_acc'], label='Validation Accuracy', linewidth=2, color='green')
    ax2.axhline(y=max(history['val_acc']), color='red', linestyle='--', 
                label=f'Best: {max(history["val_acc"]):.4f}')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Accuracy')
    ax2.set_title('Validation Accuracy')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"\n📊 Training plot saved to: {save_path}")
    plt.close()


def save_model_and_preprocessors(model, scaler, pca=None, 
                                  model_path="results/custom_model.pt",
                                  scaler_path="results/custom_scaler.pkl",
                                  pca_path="results/custom_pca.pkl"):
    """Save model and preprocessing objects"""
    import joblib
    
    # Save model weights
    torch.save(model.state_dict(), model_path)
    print(f"💾 Model saved to: {model_path}")
    
    # Save scaler
    joblib.dump(scaler, scaler_path)
    print(f"💾 Scaler saved to: {scaler_path}")
    
    # Save PCA if used
    if pca is not None:
        joblib.dump(pca, pca_path)
        print(f"💾 PCA saved to: {pca_path}")


def train_quantum_model(model, X_train, y_train, X_val, y_val, 
                       num_epochs=20, batch_size=32, learning_rate=0.001):
    """
    Train the quantum model
    
    Args:
        model: HybridQNN model
        X_train, y_train: Training data
        X_val, y_val: Validation data
        num_epochs: Number of training epochs
        batch_size: Batch size
        learning_rate: Learning rate
    
    Returns:
        history: Dictionary with training metrics
    """
    # Convert to PyTorch tensors
    X_train_tensor = torch.FloatTensor(X_train)
    y_train_tensor = torch.LongTensor(y_train)
    X_val_tensor = torch.FloatTensor(X_val)
    y_val_tensor = torch.LongTensor(y_val)
    
    # Create data loaders
    train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
    val_dataset = TensorDataset(X_val_tensor, y_val_tensor)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    # Create trainer
    trainer = QuantumClassicalTrainer(model, learning_rate=learning_rate)
    
    # Train
    trainer.train(train_loader, val_loader, num_epochs)
    
    # Return history
    history = {
        'train_loss': trainer.train_losses,
        'val_acc': trainer.val_accuracies,
        'val_loss': [0] * len(trainer.val_accuracies)  # Placeholder, can be computed in trainer
    }
    
    return history


def main():
    """Main training pipeline"""
    
    print("="*70)
    print("  QUANTUM AI - CUSTOM DATASET TRAINING")
    print("="*70)
    
    # ============================================
    # 1. LOAD DATA
    # ============================================
    print("\n📁 Step 1: Loading your data...")
    X, y = load_your_data()
    
    # ============================================
    # 2. PREPROCESS
    # ============================================
    print("\n🔧 Step 2: Preprocessing...")
    X_train, X_val, y_train, y_val, scaler, pca = preprocess_data(X, y)
    
    # ============================================
    # 3. CREATE MODEL
    # ============================================
    print("\n🧠 Step 3: Creating quantum model...")
    n_qubits = X_train.shape[1]  # Should be 4 after preprocessing
    
    # Determine number of classes
    n_classes = len(np.unique(y_train))
    
    # Create hybrid quantum-classical model
    model = HybridQNN(
        input_dim=n_qubits,
        hidden_dim=16,
        num_qubits=n_qubits,
        quantum_layers=2,
        output_dim=n_classes,
        dropout=0.2
    )
    print(f"   ✅ Created HybridQNN")
    print(f"   ✅ Quantum circuit: {n_qubits} qubits, 2 layers")
    print(f"   ✅ Output classes: {n_classes}")
    
    # ============================================
    # 4. TRAIN MODEL
    # ============================================
    print("\n🚀 Step 4: Training quantum model...")
    print("   This may take a few minutes...")
    
    history = train_quantum_model(
        model=model,
        X_train=X_train,
        y_train=y_train,
        X_val=X_val,
        y_val=y_val
    )
    
    # ============================================
    # 5. EVALUATE RESULTS
    # ============================================
    print("\n" + "="*70)
    print("  TRAINING COMPLETE!")
    print("="*70)
    
    final_train_loss = history['train_loss'][-1]
    final_val_loss = history['val_loss'][-1]
    final_val_acc = history['val_acc'][-1]
    best_val_acc = max(history['val_acc'])
    
    print(f"\n📊 Final Results:")
    print(f"   Training Loss:        {final_train_loss:.4f}")
    print(f"   Validation Loss:      {final_val_loss:.4f}")
    print(f"   Validation Accuracy:  {final_val_acc:.4f} ({final_val_acc*100:.2f}%)")
    print(f"   Best Val Accuracy:    {best_val_acc:.4f} ({best_val_acc*100:.2f}%)")
    
    # Determine performance level
    if best_val_acc >= 0.90:
        grade = "🏆 EXCELLENT!"
        emoji = "🎉"
    elif best_val_acc >= 0.80:
        grade = "⭐ VERY GOOD!"
        emoji = "🚀"
    elif best_val_acc >= 0.70:
        grade = "✅ GOOD"
        emoji = "👍"
    elif best_val_acc >= 0.60:
        grade = "⚠️  FAIR"
        emoji = "📈"
    else:
        grade = "❌ NEEDS IMPROVEMENT"
        emoji = "🔧"
    
    print(f"\n{emoji} Performance Grade: {grade}")
    
    # ============================================
    # 6. SAVE MODEL
    # ============================================
    print("\n💾 Step 5: Saving model and preprocessors...")
    save_model_and_preprocessors(model, scaler, pca)
    
    # ============================================
    # 7. PLOT RESULTS
    # ============================================
    print("\n📊 Step 6: Generating training plots...")
    plot_training_results(history)
    
    # ============================================
    # 8. RECOMMENDATIONS
    # ============================================
    print("\n💡 Recommendations:")
    
    if best_val_acc < 0.70:
        print("   ⚠️  Accuracy is low. Try:")
        print("      - More training data (currently {len(X_train)} samples)")
        print("      - Better feature engineering")
        print("      - Hyperparameter tuning (run experiments/parameter_tuning.py)")
        print("      - Check if data is properly standardized")
    
    elif best_val_acc >= 0.90:
        print("   🎉 Excellent performance! Consider:")
        print("      - Deploy to production")
        print("      - Test on Azure Quantum hardware")
        print("      - Try ensemble methods for even better results")
    
    else:
        print("   ✅ Good performance! To improve further:")
        print("      - Run hyperparameter optimization")
        print("      - Try different quantum circuit architectures")
        print("      - Collect more training data")
    
    print("\n📚 Next Steps:")
    print("   1. Review training plot: results/custom_training.png")
    print("   2. Load model for inference:")
    print("      model.load_state_dict(torch.load('results/custom_model.pt'))")
    print("   3. Run hyperparameter tuning:")
    print("      python experiments/parameter_tuning.py")
    print("   4. Deploy to Azure Quantum:")
    print("      See experiments/AZURE_QUICKSTART.md")
    
    print("\n" + "="*70)
    print("  🎉 QUANTUM AI TRAINING COMPLETE!")
    print("="*70 + "\n")
    return model, history


if __name__ == "__main__":
    model, history = main()
