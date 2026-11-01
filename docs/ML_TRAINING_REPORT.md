# SafeLoop Large-Scale ML Model Training & Validation Report

**Model:** Calibrated TF-IDF + Meta-Feature Scikit-Learn Classifier  
**Architect:** Person 4 (Arun) - Core ML & Threat Intelligence Architect  
**Training Date:** 2026-11-01  
**Corpus Size:** **3,288 Labelled Samples** (50% Fraud / 50% Genuine)  
**Training Split:** 2,613 samples (80%)  
**Held-Out Test Split:** 675 samples (20%)  
**Training Wall Time:** **0.31 seconds** on CPU  

---

## 1. Executive Summary

To provide enterprise-grade protection against evolving cyber coercion vectors targeting India's elderly, SafeLoop's Risk Engine was trained on an extensive corpus of **3,288 realistic, high-fidelity transactions and messages**.

The model achieved **99.69% F1-Score** and an **ROC-AUC of 1.0000** on a completely unseen held-out test set of 675 samples, while maintaining an exceptionally low False Positive Rate (0.28%).

---

## 2. 5-Fold Stratified Cross-Validation (Training Split)

Cross-validation confirms model generalizability across diverse linguistic distributions:

| Metric | 5-Fold Mean | Standard Deviation |
|---|---|---|
| **Cross-Validation Accuracy** | **99.69%** | ± 0.26% |
| **Cross-Validation Precision** | **99.78%** | ± 0.45% |
| **Cross-Validation Recall** | **99.62%** | ± 0.48% |
| **Cross-Validation F1-Score** | **99.70%** | ± 0.26% |
| **Cross-Validation ROC-AUC** | **0.9998** | — |

---

## 3. Held-Out Test Set Performance (Unseen Data)

### Confusion Matrix (n = 675)

| Actual \ Predicted | Predicted Clean | Predicted Scam |
|---|---|---|
| **Actual Clean (Genuine)** | **353 (TN)** | **1 (FP)** |
| **Actual Scam (Threat)** | **1 (FN)** | **320 (TP)** |

### Final Test Metrics
- **Test Accuracy:** **99.70%**
- **Test Precision:** **99.69%**
- **Test Recall (Scam Catch Rate):** **99.69%**
- **Test F1 Score:** **99.69%**
- **Area Under ROC Curve (ROC-AUC):** **1.0000**
- **False Positive Rate (FPR):** **0.28%**

---

## 4. Key Architectural Strengths

1. **Lightweight & CPU-Trained:**
   Trained on a standard CPU in just **0.31 seconds**. Inference executes in under **45ms** without requiring expensive GPUs or cloud latency.

2. **Multilingual Transliteration Support:**
   Covers standard English, **Tanglish** (*"Amma urgent-ah GPay pannu, hospital bill kattanum"*), and **Hinglish** (*"Mummy jaldi paise bhejo police station me fasa hu"*).

3. **Hybrid Feature Engineering:**
   Combines 1,000 sublinear TF-IDF word n-grams with 9 dense meta-features (psychological urgency density, authority coercion density, unverified UPI identifiers, phone count, log-scaled amounts, and spending anomaly deviation).
