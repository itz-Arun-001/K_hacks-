"""
SafeLoop User Baseline Profiler (L3: Decide)
Owned by: Person 4 (Arun)

Analyzes an elderly user's historical transaction behavior to establish their normal baseline:
- Typical transaction amounts (mean and standard deviation)
- Known and frequent payees
- Unusual transaction spikes (e.g. ₹50,000 when typical spend is ₹400-₹900)

If a user tries to transfer money to a completely unknown entity with an amount
vastly exceeding their normal behavior, an anomaly penalty is added to the Risk Engine.
"""

from typing import Dict, Any, List, Optional
import math
from sqlalchemy.orm import Session

try:
    from app.database import Payment, User, TrustedPayee
except ImportError:
    Payment = None
    User = None
    TrustedPayee = None


def get_user_baseline(db: Session, user_id: int) -> Dict[str, Any]:
    """
    Computes statistical baseline metrics for a user's transaction history.
    """
    if not db or Payment is None:
        return {"count": 0, "mean": 0.0, "std": 0.0, "max": 0.0, "known_payees": []}

    # Fetch approved/allowed payments for the user
    payments = db.query(Payment).filter(
        Payment.user_id == user_id,
        Payment.status.in_(["allowed", "released"])
    ).all()

    if not payments:
        return {
            "count": 0,
            "mean": 500.0,  # Default conservative prior for an Indian senior citizen
            "std": 300.0,
            "max": 1500.0,
            "known_payees": []
        }

    amounts = [p.amount for p in payments]
    count = len(amounts)
    mean_val = sum(amounts) / count
    variance = sum((x - mean_val) ** 2 for x in amounts) / count if count > 1 else 100.0
    std_val = math.sqrt(variance)
    max_val = max(amounts)

    known_payees = list({p.payee_identifier.lower().strip() for p in payments})

    # Also add trusted payees to known payees
    if TrustedPayee is not None:
        trusted = db.query(TrustedPayee).filter(TrustedPayee.user_id == user_id).all()
        for t in trusted:
            known_payees.append(t.payee_identifier.lower().strip())

    return {
        "count": count,
        "mean": round(mean_val, 2),
        "std": round(std_val, 2),
        "max": round(max_val, 2),
        "known_payees": list(set(known_payees))
    }


def evaluate_baseline_deviation(
    db: Session,
    user_id: int,
    payee_identifier: str,
    amount: float
) -> Dict[str, Any]:
    """
    Evaluates whether a new payment deviates significantly from the user's historical profile.

    Returns:
        Dict with:
        - anomaly_score: float (0.0 to 1.0)
        - is_new_payee: bool
        - reasons: list of human-readable explanation strings
    """
    baseline = get_user_baseline(db, user_id)
    reasons: List[str] = []
    anomaly_score: float = 0.0

    mean_amt = baseline["mean"]
    max_amt = baseline["max"]
    known_payees = baseline["known_payees"]
    clean_payee = (payee_identifier or "").lower().strip()

    is_new_payee = clean_payee not in known_payees if clean_payee else True

    # 1. Payee Novelty Check
    if is_new_payee and clean_payee:
        anomaly_score += 0.25
        reasons.append(f"First-time transfer to payee '{payee_identifier}'. Not in usual history.")

    # 2. Amount Deviation Multiplier Check
    if mean_amt > 0 and amount > 0:
        ratio = amount / mean_amt
        if ratio >= 15.0:  # e.g., ₹15,000+ when avg is ₹800
            anomaly_score += 0.60
            reasons.append(
                f"Severe amount anomaly: ₹{amount:,.2f} is {ratio:.1f}x higher than user's 30-day average (₹{mean_amt:,.2f})."
            )
        elif ratio >= 5.0:  # e.g., ₹4,000+ when avg is ₹800
            anomaly_score += 0.35
            reasons.append(
                f"Unusual payment size: ₹{amount:,.2f} is {ratio:.1f}x higher than user's normal average (₹{mean_amt:,.2f})."
            )
        elif amount > max_amt * 2.0:
            anomaly_score += 0.25
            reasons.append(
                f"Amount ₹{amount:,.2f} exceeds user's all-time historical maximum of ₹{max_amt:,.2f}."
            )

    return {
        "anomaly_score": min(round(anomaly_score, 2), 1.0),
        "is_new_payee": is_new_payee,
        "baseline_mean": mean_amt,
        "baseline_max": max_amt,
        "reasons": reasons
    }

