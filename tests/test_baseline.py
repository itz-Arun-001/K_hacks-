"""
Unit Tests for User Baseline Profiler & Anomaly Detection (Person 4: Arun)
"""

import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import SessionLocal, init_db
from app.services.risk_engine import evaluate_risk
from app.services.baseline import evaluate_baseline_deviation


def test_anomaly_detection_logic():
    print("\n" + "=" * 60)
    print(" TESTING USER BASELINE ANOMALY DETECTION (ARUN)")
    print("=" * 60)

    init_db()
    db = SessionLocal()

    try:
        # 1. Normal transaction (₹450 to known milkman) -> should be safe
        print("\nTest 1: Low-value normal payment (₹450 to whitelisted milkman)")
        res_normal = evaluate_risk(
            user_id="1",
            message_type="payment",
            text="Pay ₹450 to anand.milk@upi",
            entities={"upi_ids": ["anand.milk@upi"], "amounts": [450.0]},
            db=db
        )
        print(f"  Score: {res_normal['score']} | Level: {res_normal['level']}")
        print(f"  Reasons: {res_normal['reasons']}")
        assert res_normal["level"] == "safe", f"Expected safe, got {res_normal['level']}"

        # 2. Extreme anomaly: ₹75,000 to an unknown UPI
        print("\nTest 2: Massive anomaly payment (₹75,000 to unknown account)")
        res_anomaly = evaluate_risk(
            user_id="1",
            message_type="payment",
            text="Pay ₹75,000 to unknown.trader@upi",
            entities={"upi_ids": ["unknown.trader@upi"], "amounts": [75000.0]},
            db=db
        )
        print(f"  Score: {res_anomaly['score']} | Level: {res_anomaly['level']}")
        print(f"  Reasons: {res_anomaly['reasons']}")
        assert res_anomaly["level"] in ["suspicious", "high"], f"Expected suspicious/high, got {res_anomaly['level']}"

        # 3. Threat entity from blocklist: kbc.claim@upi
        print("\nTest 3: Transfer to known blacklisted scammer (kbc.claim@upi)")
        res_scam = evaluate_risk(
            user_id="1",
            message_type="payment",
            text="Pay ₹12,500 to kbc.claim@upi for lottery processing",
            entities={"upi_ids": ["kbc.claim@upi"], "amounts": [12500.0]},
            db=db
        )
        print(f"  Score: {res_scam['score']} | Level: {res_scam['level']}")
        print(f"  Reasons: {res_scam['reasons']}")
        assert res_scam["level"] == "high", f"Expected high, got {res_scam['level']}"

        print("\n[OK] All baseline anomaly tests passed successfully!")
        print("=" * 60 + "\n")

    finally:
        db.close()


if __name__ == "__main__":
    test_anomaly_detection_logic()
