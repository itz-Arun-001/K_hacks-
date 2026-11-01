"""
SafeLoop Risk Engine (L3: Decide)
Owned by: Person 4 (Arun)

Contract:
input:  { user_id, type, text, entities: {links, phones, upi_ids, amounts}, scam_tags }
output: { score, level: "safe|suspicious|high", reasons: [...] }

Integrated Pipeline:
1. Threat Intelligence Blocklist: Hard instant-flag for confirmed mule rings and family blocks.
2. Calibrated Scikit-Learn Model: TF-IDF + meta-feature probability score P(scam | x).
3. Zero-Day Heuristic Parser: Psychological coercion keywords (Digital arrest, utility cutoff, fake jobs, etc.).
4. Link Threat Analyzer: Unofficial domains, suspicious TLDs (.info, .cc, .top).
5. User Spending Baseline Deviation: Anomaly score for unusual amount spikes and new payees (Arun).
6. LLM Signal: Tactics parsing and intent confidence (from Person 1: Aiman).
"""

from typing import Dict, List, Any, Optional

try:
    from sqlalchemy.orm import Session
    from app.database import FlaggedEntity
except ImportError:
    Session = None
    FlaggedEntity = None

try:
    from app.services.baseline import evaluate_baseline_deviation
except ImportError:
    evaluate_baseline_deviation = None

try:
    from app.services.ml_model import get_ml_classifier
except ImportError:
    get_ml_classifier = None


# Pre-defined high-risk keywords for comprehensive heuristic scoring
SCAM_KEYWORDS = {
    "digital_arrest": [
        "digital arrest", "cbi", "police warrant", "trai warning", "customs",
        "cyber crime", "money laundering", "non-bailable warrant", "supreme court order"
    ],
    "utility_disconnection": [
        "electricity will be", "power cut", "cut off", "water supply", "electricity officer", "bill overdue",
        "disconnection", "bill was not updated", "gas connection", "bharat gas",
        "mobile number will be blocked", "calls on your mobile", "sim blocked"
    ],
    "lottery_and_rewards": [
        "kbc lottery", "congratulations won", "claim prize", "lucky draw",
        "25 lakh", "prize money", "reward points", "points expiring", "redeem cash"
    ],
    "relative_in_trouble": [
        "accident", "arrested by police", "don't tell appa", "send money to hospital",
        "friend in emergency", "nephew suresh", "cannot talk"
    ],
    "fake_jobs_and_loans": [
        "part-time job", "part time job", "earn daily", "liking youtube",
        "task link", "activation fee", "earn from home", "pre-approved loan",
        "without collateral", "file processing fee"
    ],
    "phishing_kyc": [
        "account will be blocked", "kyc update", "pan card immediately",
        "services will be terminated", "atm pin", "refund approved", "verify your bank account"
    ],
    "urgency_triggers": [
        "within 10 minutes", "within 15 minutes", "within 2 hours", "within 24 hours",
        "immediately", "do not disconnect", "urgent transfer", "secretly", "urgently", "expiring tonight"
    ]
}


def evaluate_risk(
    user_id: Optional[str] = None,
    message_type: str = "text",
    text: Optional[str] = "",
    entities: Optional[Dict[str, List[Any]]] = None,
    scam_tags: Optional[Dict[str, Any]] = None,
    db: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Evaluates composite risk score and generates reasons based on ML model, rules, entities, LLM tags, and user baseline.
    """
    entities = entities or {}
    scam_tags = scam_tags or {}
    text_lower = (text or "").lower()
    
    reasons: List[str] = []
    score: float = 0.0

    # --------------------------------------------------------------------------
    # 1. Database Blocklist Check (Flagged Entities from Mule Graph / Family Blocks)
    # --------------------------------------------------------------------------
    if db and FlaggedEntity is not None:
        checked_values = []
        checked_values.extend(entities.get("upi_ids", []))
        checked_values.extend(entities.get("phones", []))
        checked_values.extend(entities.get("links", []))
        
        if checked_values:
            flagged = db.query(FlaggedEntity).filter(
                FlaggedEntity.entity_value.in_(checked_values)
            ).first()
            if flagged:
                score = max(score, flagged.risk_score or 0.98)
                reasons.append(f"Entity '{flagged.entity_value}' is on the cybercrime / mule blocklist ({flagged.reason or 'Flagged'}).")

    # --------------------------------------------------------------------------
    # 2. User Spending Baseline Deviation Check (Person 4: Arun)
    # --------------------------------------------------------------------------
    baseline_anomaly_score = 0.0
    amounts = entities.get("amounts", [])
    if db and user_id and evaluate_baseline_deviation and amounts:
        try:
            val = float(amounts[0])
            payee_id = (entities.get("upi_ids") or [None])[0] or (entities.get("phones") or [None])[0]
            numeric_uid = int(user_id) if str(user_id).isdigit() else 1
            
            baseline_result = evaluate_baseline_deviation(db, numeric_uid, payee_id or "", val)
            if baseline_result["anomaly_score"] > 0:
                baseline_anomaly_score = baseline_result["anomaly_score"]
                score += baseline_anomaly_score
                reasons.extend(baseline_result["reasons"])
        except (ValueError, TypeError, Exception):
            pass
    elif amounts:
        for amt in amounts:
            try:
                val = float(amt)
                if val >= 50000:
                    score += 0.40
                    reasons.append(f"High-value transfer request (₹{val:,.2f}) above typical threshold.")
                elif val >= 10000:
                    score += 0.20
            except (ValueError, TypeError):
                continue

    # --------------------------------------------------------------------------
    # 3. Calibrated Scikit-Learn Model Prediction
    # --------------------------------------------------------------------------
    ml_prob = None
    if get_ml_classifier:
        classifier = get_ml_classifier()
        if classifier and classifier.is_trained:
            ml_prob = classifier.predict_proba(text, entities, baseline_anomaly_score)
            score = max(score, ml_prob)
            ml_reasons = classifier.explain(text, entities, top_k=2)
            reasons.extend(ml_reasons)

    # --------------------------------------------------------------------------
    # 4. Zero-Day Heuristic Keyword Matching (Fallback & Reinforcement)
    # --------------------------------------------------------------------------
    for category, keywords in SCAM_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                if category == "digital_arrest":
                    score = max(score, 0.75)
                    reasons.append("Detected 'Digital Arrest' impersonation tactic (fake police/CBI warrant).")
                elif category == "utility_disconnection":
                    score = max(score, 0.70)
                    reasons.append("Detected urgent utility/service cut-off threat.")
                elif category == "lottery_and_rewards":
                    score = max(score, 0.75)
                    reasons.append("Detected fraudulent lottery/reward points advance-fee pattern.")
                elif category == "relative_in_trouble":
                    score = max(score, 0.80)
                    reasons.append("Detected fake relative in distress / accident coercion pattern.")
                elif category == "fake_jobs_and_loans":
                    score = max(score, 0.75)
                    reasons.append("Detected high-risk work-from-home or unsecured loan advance fee trap.")
                elif category == "phishing_kyc":
                    score = max(score, 0.75)
                    reasons.append("Detected banking KYC suspension threat or fake refund lure.")
                elif category == "urgency_triggers":
                    score += 0.15
                    reasons.append("Extreme urgency pressure detected ('act immediately to avoid action').")
                break

    # --------------------------------------------------------------------------
    # 5. Suspicious Links & Phishing Indicators
    # --------------------------------------------------------------------------
    links = entities.get("links", [])
    for link in links:
        link_lower = link.lower()
        if any(suspicious_tld in link_lower for suspicious_tld in [".info", ".cc", ".top", ".xyz", ".club"]):
            score = max(score, 0.80)
            reasons.append(f"Suspicious unverified domain extension in link: {link}")
        elif "sbi" in link_lower or "incometax" in link_lower or "kyc" in link_lower:
            score = max(score, 0.85)
            reasons.append(f"Phishing link impersonating government/banking institution: {link}")

    # --------------------------------------------------------------------------
    # 6. LLM Signal Integration (from Person 1: Aiman)
    # --------------------------------------------------------------------------
    if scam_tags:
        llm_confidence = scam_tags.get("confidence", 0.0)
        llm_type = scam_tags.get("scam_type")
        tactics = scam_tags.get("tactics", [])
        
        if llm_type and llm_type != "none":
            score = max(score, llm_confidence)
            reasons.append(f"AI identified scam pattern: {llm_type.replace('_', ' ').title()}.")
            
        if tactics:
            reasons.append(f"Identified psychological pressure tactics: {', '.join(tactics)}.")

    # --------------------------------------------------------------------------
    # 7. Standard Transactional Banking Notification Safeguard
    # --------------------------------------------------------------------------
    is_standard_bank_sms = any(b in text_lower for b in ["withdrawn from atm", "debited from a/c", "debited from account", "credited to your"])
    if is_standard_bank_sms and not entities.get("upi_ids") and not entities.get("links"):
        score = min(score, 0.15)
        reasons = [r for r in reasons if "ML pattern" not in r]

    # --------------------------------------------------------------------------
    # 8. Calibrate Final Score & Level
    # --------------------------------------------------------------------------
    final_score = min(max(round(score, 2), 0.0), 1.0)
    
    if final_score >= 0.70:
        level = "high"
        if not reasons:
            reasons.append("Multiple high-risk fraud signals detected.")
    elif final_score >= 0.50:
        level = "suspicious"
        if not reasons:
            reasons.append("Unverified payee or suspicious context detected.")
    else:
        level = "safe"
        if not reasons:
            reasons.append("No immediate fraud or coercion indicators detected.")

    unique_reasons = list(dict.fromkeys(reasons))

    return {
        "score": final_score,
        "level": level,
        "reasons": unique_reasons
    }
