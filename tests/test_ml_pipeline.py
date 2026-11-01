"""
Unit Tests for Scikit-Learn Risk Model Pipeline (Person 4: Arun)
"""

import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.ml_model import get_ml_classifier


def test_ml_pipeline():
    print("\n" + "=" * 60)
    print(" TESTING SCIKIT-LEARN RISK MODEL PIPELINE (ARUN)")
    print("=" * 60)

    classifier = get_ml_classifier()
    assert classifier is not None, "Failed to load ML classifier from app/models/"
    assert classifier.is_trained, "Classifier is marked as not trained"

    # Test 1: Known digital arrest text
    scam_text = "CBI police warrant issued for money laundering. Transfer immediately."
    scam_prob = classifier.predict_proba(scam_text)
    explanations = classifier.explain(scam_text)
    print(f"\n[Test 1: Digital Arrest Coercion]")
    print(f"  P(scam): {scam_prob:.2f}")
    print(f"  Explanations: {explanations}")
    assert scam_prob >= 0.50, f"Expected positive scam probability (>=0.50), got {scam_prob}"

    # Test 2: High-risk scam with target UPI & high amount
    full_scam_text = "Urgent: Pay ₹50,000 to cbi.investigation@upi within 15 minutes to avoid digital arrest."
    full_scam_prob = classifier.predict_proba(
        full_scam_text,
        entities={"upi_ids": ["cbi.investigation@upi"], "amounts": [50000.0]}
    )
    print(f"\n[Test 2: Complete Scam with Payment Demand]")
    print(f"  P(scam): {full_scam_prob:.2f}")
    assert full_scam_prob >= 0.85, f"Expected high probability (>=0.85), got {full_scam_prob}"

    # Test 3: Normal family greeting
    normal_text = "Good morning Amma, please take your tablets on time. Love you."
    normal_prob = classifier.predict_proba(normal_text)
    print(f"\n[Test 3: Normal Family Chat]")
    print(f"  P(scam): {normal_prob:.2f}")
    assert normal_prob < 0.20, f"Expected low probability (<0.20), got {normal_prob}"

    print("\n[OK] Scikit-Learn risk model pipeline verified successfully!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    test_ml_pipeline()
