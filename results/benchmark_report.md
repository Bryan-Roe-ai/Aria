# Quantum AI Benchmark Report

**Date:** 2025-11-16 21:13:05

## Model Configuration
- **Architecture:** Hybrid Quantum-Classical Neural Network
- **Quantum Circuit:** 4 qubits, 2 variational layers
- **Classical Layers:** 16-node hidden layer with dropout (0.2)
- **Training:** 25 epochs, batch size 16, learning rate 0.001
- **Optimizer:** Adam

## Results Summary

| Dataset | Samples | Features | Best Accuracy | Final Accuracy | Grade |
|---------|---------|----------|---------------|----------------|-------|
| ionosphere | 350 | 34 | 85.71% | 85.71% | 🏆 Excellent |
| banknote | 1371 | 4 | 99.27% | 99.27% | 🏆 Excellent |
| heart_disease | 302 | 13 | 81.97% | 78.69% | ⭐ Very Good |
| sonar | 207 | 60 | 76.19% | 71.43% | ⭐ Very Good |
| diabetes | 767 | 8 | 70.78% | 68.18% | ✅ Good |
| blood_transfusion | 748 | 4 | 83.33% | 82.00% | ⭐ Very Good |
| magic_gamma | 19019 | 10 | 78.05% | 77.44% | ⭐ Very Good |
| iris | 149 | 4 | 96.67% | 96.67% | 🏆 Excellent |
| glass | 213 | 10 | 88.37% | 86.05% | 🏆 Excellent |

## Detailed Results


### Ionosphere

**Description:** Radar returns classification

**Task:** Binary classification: Good vs Bad radar signals

**Metrics:**
- Best Validation Accuracy: **85.71%**
- Final Training Loss: 0.3625
- Training Samples: 280
- Validation Samples: 70

### Banknote

**Description:** Banknote authentication

**Task:** Binary classification: Genuine vs Forged banknotes

**Metrics:**
- Best Validation Accuracy: **99.27%**
- Final Training Loss: 0.0777
- Training Samples: 1096
- Validation Samples: 275

### Heart_Disease

**Description:** Heart disease diagnosis

**Task:** Binary classification: Disease present vs absent

**Metrics:**
- Best Validation Accuracy: **81.97%**
- Final Training Loss: 0.4267
- Training Samples: 241
- Validation Samples: 61

### Sonar

**Description:** Sonar returns classification

**Task:** Binary classification: Mine vs Rock detection

**Metrics:**
- Best Validation Accuracy: **76.19%**
- Final Training Loss: 0.5059
- Training Samples: 165
- Validation Samples: 42

### Diabetes

**Description:** Pima Indians Diabetes

**Task:** Binary classification: Diabetes onset prediction

**Metrics:**
- Best Validation Accuracy: **70.78%**
- Final Training Loss: 0.5195
- Training Samples: 613
- Validation Samples: 154

### Blood_Transfusion

**Description:** Blood Transfusion Service Center

**Task:** Binary: Blood donation prediction

**Metrics:**
- Best Validation Accuracy: **83.33%**
- Final Training Loss: 0.4831
- Training Samples: 598
- Validation Samples: 150

### Magic_Gamma

**Description:** MAGIC Gamma Telescope

**Task:** Binary: Gamma signal vs Hadron background

**Metrics:**
- Best Validation Accuracy: **78.05%**
- Final Training Loss: 0.4951
- Training Samples: 15215
- Validation Samples: 3804

### Iris

**Description:** Iris Flower Species

**Task:** Multi-class: Iris species (setosa, versicolor, virginica)

**Metrics:**
- Best Validation Accuracy: **96.67%**
- Final Training Loss: 0.1720
- Training Samples: 119
- Validation Samples: 30

### Glass

**Description:** Glass Identification

**Task:** Multi-class: Glass type classification

**Metrics:**
- Best Validation Accuracy: **88.37%**
- Final Training Loss: 0.3997
- Training Samples: 170
- Validation Samples: 43

## Conclusions

- **Best Performance:** banknote (99.27%)
- **Average Accuracy:** 84.48%
- **Total Datasets Tested:** 9

✅ **Overall Assessment:** The quantum AI model demonstrates strong performance across all datasets!