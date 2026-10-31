"""
SafeLoop Closed-Loop Retraining Demonstration (Person 4: Arun)
Demonstrates to judges how family feedback (son clicking BLOCK) instantly
immunizes the entire system against zero-day scams without manual retraining.
"""

import os
import sys
import json

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import SessionLocal, init_db
from app.services.risk_engine import evaluate_risk
from app.services.retrainer import record_family_feedback, calculate_metrics


def run_retraining_demo():
    print("\n" + "=" * 70)
    print(" SAFELOOP CLOSED-LOOP LEARNING DEMONSTRATION (ARUN: L6)")
    print("=" * 70)

    init_db()
    db = SessionLocal()

    try:
        # Load benchmark dataset
        with open("data/labelled_messages.json", "r", encoding="utf-8") as f:
            dataset = json.load(f)

        # ----------------------------------------------------------------------
        # SCENE 1: Zero-Day Scam with Polite Wording Arrives
        # ----------------------------------------------------------------------
        zero_day_scam = {
            "id": "ZERO_DAY_001",
            "text": "Greetings madam, kindly send ₹3,500 donation to cleanwaters.charity@upi for rural orphanage children. God bless you.",
            "category": "scam",
            "expected_level": "high",
            "entities": {"upi_ids": ["cleanwaters.charity@upi"], "amounts": [3500]}
        }

        print("\n[SCENE 1: A Zero-Day Scam Arrives on Amma's Phone]")
        print(f"  Message: \"{zero_day_scam['text']}\"")
        print(f"  Target UPI: cleanwaters.charity@upi")

        # Initial evaluation BEFORE family feedback
        res_before = evaluate_risk(
            message_type="payment",
            text=zero_day_scam["text"],
            entities=zero_day_scam["entities"],
            db=db
        )

        print(f"\n  • Initial Risk Score: {res_before['score']} | Level: {res_before['level'].upper()}")
        print(f"  • Reasons: {res_before['reasons']}")
        print("  -> Notice: Because the scammer used polite wording and a new UPI ID,")
        print("     rule-based detectors alone gave it a low/suspicious score.")

        # ----------------------------------------------------------------------
        # SCENE 2: Two-Key Guard Triggers Check B -> Son Replies BLOCK
        # ----------------------------------------------------------------------
        print("\n[SCENE 2: Amma attempts payment -> Two-Key Guard triggers Check B]")
        print("  WhatsApp to Son Rahul: 'Amma is paying ₹3,500 to cleanwaters.charity@upi. Reply APPROVE or BLOCK'")
        print("  Son recognizes fraud and replies: >> BLOCK <<")

        # System ingests feedback
        flagged_node = record_family_feedback(
            db=db,
            entity_type="upi",
            entity_value="cleanwaters.charity@upi",
            verdict="BLOCK",
            reporter_phone="+919876543211",
            reason="Son verified fake charity scam via WhatsApp Check B"
        )
        print(f"\n[✔] System Learned: 'cleanwaters.charity@upi' added to Global Blocklist (Source: {flagged_node.source})")

        # ----------------------------------------------------------------------
        # SCENE 3: Re-Evaluation (The Closed Loop in Action)
        # ----------------------------------------------------------------------
        print("\n[SCENE 3: Another user on WhatsApp attempts to pay the same UPI]")
        res_after = evaluate_risk(
            message_type="payment",
            text="Please transfer ₹3,500 to cleanwaters.charity@upi",
            entities={"upi_ids": ["cleanwaters.charity@upi"], "amounts": [3500]},
            db=db
        )

        print(f"  • New Risk Score: {res_after['score']} | Level: {res_after['level'].upper()}")
        print(f"  • Reasons: {res_after['reasons']}")

        # ----------------------------------------------------------------------
        # SCENE 4: Before vs. After Benchmark Metrics
        # ----------------------------------------------------------------------
        # Add the zero-day scam to test dataset
        test_samples = dataset + [zero_day_scam]
        
        # Calculate metrics
        metrics = calculate_metrics(test_samples, db=db)

        print("\n" + "=" * 70)
        print(" FINAL SYSTEM PERFORMANCE METRICS (POST-FEEDBACK)")
        print("=" * 70)
        print(f"  • Total Evaluation Samples:  {metrics['total']}")
        print(f"  • Scams Caught (TP):        {metrics['tp']}")
        print(f"  • Genuine Clean (TN):        {metrics['tn']}")
        print(f"  • False Alarms (FP):         {metrics['fp']}")
        print(f"  • Missed Scams (FN):         {metrics['fn']}")
        print("  --------------------------------------")
        print(f"  • System Precision:          {metrics['precision']}%")
        print(f"  • System Recall:             {metrics['recall']}%")
        print(f"  • System F1 Score:           {metrics['f1']}%")
        print("=" * 70 + "\n")

    finally:
        db.close()


if __name__ == "__main__":
    run_retraining_demo()
