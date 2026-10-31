"""
SafeLoop Risk Engine Evaluation Script (Person 4: Arun)
Measures Precision, Recall, F1-Score, and False Positive Rates on the labelled benchmark dataset.
"""

import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure root folder is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.risk_engine import evaluate_risk


def run_evaluation(data_path: str = "data/labelled_messages.json"):
    if not os.path.exists(data_path):
        print(f"Dataset file not found at: {data_path}")
        return

    with open(data_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    print("\n" + "=" * 70)
    print(" SAFELOOP BENCHMARK EVALUATION (PERSON 4: ARUN)")
    print("=" * 70)
    print(f"Total labelled samples: {len(dataset)}")

    for split in ["all", "test"]:
        tp = 0  # True Positives: Scam correctly flagged as high/suspicious
        fp = 0  # False Positives: Genuine flagged as high/suspicious
        tn = 0  # True Negatives: Genuine flagged as safe
        fn = 0  # False Negatives: Scam missed as safe

        mistakes = []
        samples = [item for item in dataset if split == "all" or item.get("split") == split]

        for item in samples:
            text = item.get("text", "")
            expected_level = item.get("expected_level", "safe")
            is_scam = item.get("category") == "scam"
            entities = item.get("entities", {})

            result = evaluate_risk(
                message_type="text",
                text=text,
                entities=entities
            )
            predicted_level = result["level"]
            predicted_as_scam = predicted_level in ["high", "suspicious"]

            if is_scam and predicted_as_scam:
                tp += 1
            elif not is_scam and not predicted_as_scam:
                tn += 1
            elif not is_scam and predicted_as_scam:
                fp += 1
                mistakes.append({
                    "id": item["id"],
                    "type": "FALSE_POSITIVE",
                    "text": text[:60] + "...",
                    "expected": expected_level,
                    "got": predicted_level,
                    "reasons": result["reasons"]
                })
            elif is_scam and not predicted_as_scam:
                fn += 1
                mistakes.append({
                    "id": item["id"],
                    "type": "FALSE_NEGATIVE (MISSED SCAM)",
                    "text": text[:60] + "...",
                    "expected": expected_level,
                    "got": predicted_level,
                    "reasons": result["reasons"]
                })

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0

        split_label = "FULL DATASET" if split == "all" else "HELD-OUT TEST SET (30%)"
        print(f"\n[{split_label}] (n = {len(samples)})")
        print(f"  • True Positives (Scams Caught): {tp}")
        print(f"  • True Negatives (Genuine Passed): {tn}")
        print(f"  • False Positives (False Alarms): {fp}")
        print(f"  • False Negatives (Missed Scams): {fn}")
        print(f"  -------------------------------------")
        print(f"  • Precision:            {precision * 100:.1f}%")
        print(f"  • Recall:               {recall * 100:.1f}%")
        print(f"  • F1 Score:             {f1 * 100:.1f}%")
        print(f"  • False Positive Rate:  {fpr * 100:.1f}%")

        if mistakes:
            print("\n  List of Mistakes:")
            for m in mistakes:
                print(f"    - [{m['type']}] ID: {m['id']} | Predicted: {m['got']} | Expected: {m['expected']}")
                print(f"      Reasons: {m['reasons']}")
        else:
            print("  Mistakes: None! 100% agreement on this split.")

    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    run_evaluation()

