"""
SafeLoop ML Model Training Script (Person 4: Arun)
Trains the calibrated Scikit-Learn risk classifier and evaluates on the held-out test split.
Saves model bundle to 'app/models/risk_classifier.joblib'.
"""

import os
import sys
import json

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.ml_model import SafeLoopRiskClassifier, MODEL_PATH


def train_and_evaluate():
    print("\n" + "=" * 70)
    print(" SAFELOOP SCIKIT-LEARN RISK MODEL TRAINING (ARUN: L3)")
    print("=" * 70)

    dataset_path = "data/labelled_messages.json"
    if not os.path.exists(dataset_path):
        print(f"[!] Dataset not found at: {dataset_path}")
        return

    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    train_samples = [s for s in dataset if s.get("split") == "train"]
    test_samples = [s for s in dataset if s.get("split") == "test"]

    print(f"Total dataset: {len(dataset)} samples")
    print(f"  • Training split: {len(train_samples)} samples")
    print(f"  • Held-out test split: {len(test_samples)} samples\n")

    # 1. Train Classifier
    print("[+] Training TF-IDF feature extractor + calibrated logistic regression...")
    classifier = SafeLoopRiskClassifier()
    classifier.fit(train_samples)
    print("[OK] Model training complete.")

    # 2. Evaluate on Held-Out Test Split
    print("\n[+] Evaluating model on 100% unseen test samples:")
    tp, tn, fp, fn = 0, 0, 0, 0

    for sample in test_samples:
        text = sample.get("text", "")
        entities = sample.get("entities", {})
        is_scam = sample.get("category") == "scam"

        prob = classifier.predict_proba(text, entities)
        predicted_scam = prob >= 0.50

        if is_scam and predicted_scam:
            tp += 1
            status = "TP (Scam Caught)"
        elif not is_scam and not predicted_scam:
            tn += 1
            status = "TN (Genuine Passed)"
        elif not is_scam and predicted_scam:
            fp += 1
            status = "FP (False Alarm)"
        else:
            fn += 1
            status = "FN (Missed Scam)"

        print(f"  [{status}] P(scam)={prob:.2f} | {text[:55]}...")

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    print("\n" + "-" * 45)
    print(" HELD-OUT TEST SET EVALUATION METRICS:")
    print("-" * 45)
    print(f"  • Scams Caught (TP):   {tp}")
    print(f"  • Genuine Clean (TN):  {tn}")
    print(f"  • False Alarms (FP):   {fp}")
    print(f"  • Missed Scams (FN):   {fn}")
    print(f"  • Test Precision:      {precision * 100:.1f}%")
    print(f"  • Test Recall:         {recall * 100:.1f}%")
    print(f"  • Test F1 Score:       {f1 * 100:.1f}%")
    print("-" * 45)

    # 3. Save Model Bundle
    classifier.save(MODEL_PATH)
    print(f"\n[OK] Trained model artifact saved to: {os.path.relpath(MODEL_PATH)}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    train_and_evaluate()
