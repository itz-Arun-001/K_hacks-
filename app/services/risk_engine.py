"""
SafeLoop Risk Engine (L3: Decide)
Owned by: Person 4 (Arun)

Contract:
input:  { user_id, type, text, entities: {links, phones, upi_ids, amounts}, scam_tags }
output: { score, level: "safe|suspicious|high", reasons: [...] }

Week 1: Foundations & Rule-based Stub Engine
- Unblocks Person 1 (Aiman: Bot) and Person 2 (Geerthiga: Guard) immediately.
- Implements initial heuristic rule checks, keyword triggers, and database blocklist matching.
- Week 2 will introduce the scikit-learn model and per-user anomaly baseline.
"""

from typing import Dict, List, Any, Optional

try:
    from sqlalchemy.orm import Session
    from app.database import FlaggedEntity
except ImportError:
    Session = None
    FlaggedEntity = None


# Pre-defined high-risk keywords for initial heuristic scoring (Week 1)
SCAM_KEYWORDS = {
    "digital_arrest": ["digital arrest", "cbi", "police warrant", "trai block", "customs", "cyber crime", "money laundering"],
    "electricity_scam": ["electricity will be", "power cut", "electricity officer", "bill overdue", "disconnection", "bill was not updated"],
    "lottery_scam": ["kbc lottery", "congratulations won", "claim prize", "lucky draw", "25 lakh", "prize money"],
    "relative_in_trouble": ["accident", "arrested by police", "don't tell appa", "send money to hospital", "friend in emergency"],
    "urgency_triggers": ["within 10 minutes", "within 15 minutes", "immediately", "do not disconnect", "urgent transfer", "secretly", "urgently"]
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
    Evaluates risk score and generates reasons based on rules, entities, and scam tags.
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
                score = max(score, flagged.risk_score or 0.95)
                reasons.append(f"Entity '{flagged.entity_value}' is on the cybercrime / mule blocklist ({flagged.reason or 'Flagged'}).")

    # --------------------------------------------------------------------------
    # 2. Heuristic Keyword Matching (Zero-day scam scripts)
    # --------------------------------------------------------------------------
    for category, keywords in SCAM_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                if category == "digital_arrest":
                    score += 0.55
                    reasons.append("Detected 'Digital Arrest' impersonation tactic (fake police/CBI warrant).")
                elif category == "electricity_scam":
                    score += 0.50
                    reasons.append("Detected fake utility cut-off threat.")
                elif category == "lottery_scam":
                    score += 0.50
                    reasons.append("Detected fraudulent lottery/prize claim pattern.")
                elif category == "relative_in_trouble":
                    score += 0.55
                    reasons.append("Detected fake relative in distress / accident coercion pattern.")
                elif category == "urgency_triggers":
                    score += 0.20
                    reasons.append("Extreme urgency pressure detected ('transfer immediately').")
                break

    # --------------------------------------------------------------------------
    # 3. LLM Signal Integration (from Person 1)
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
    # 4. Amount-based Heuristics (for payments)
    # --------------------------------------------------------------------------
    amounts = entities.get("amounts", [])
    for amt in amounts:
        try:
            val = float(amt)
            if val >= 50000:
                score += 0.30
                reasons.append(f"High-value transfer request (₹{val:,.2f}) above typical threshold.")
            elif val >= 10000:
                score += 0.15
                reasons.append(f"Significant transfer request (₹{val:,.2f}).")
        except (ValueError, TypeError):
            continue

    # --------------------------------------------------------------------------
    # 5. Calibrate Final Score & Level
    # --------------------------------------------------------------------------
    final_score = min(max(round(score, 2), 0.0), 1.0)
    
    if final_score >= 0.70:
        level = "high"
        if not reasons:
            reasons.append("Multiple high-risk fraud signals detected.")
    elif final_score >= 0.35:
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
