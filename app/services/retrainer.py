"""
SafeLoop Feedback & Retraining Module (L6: Learn)
Owned by: Person 4 (Arun)

Implements the active closed-loop learning mechanism:
1. Ingests family verdicts (son replies BLOCK on a held payment).
2. Automatically syncs malicious UPI IDs, phones, and accounts to the global blocklist (flagged_entities).
3. Compares precision and recall metrics before vs. after feedback to prove model learning to judges.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.database import FlaggedEntity, Event
from app.services.risk_engine import evaluate_risk
from app.utils.audit import log_event


def record_family_feedback(
    db: Session,
    entity_type: str,
    entity_value: str,
    verdict: str,  # "BLOCK" or "APPROVE"
    reporter_phone: Optional[str] = None,
    reason: Optional[str] = "Family member blocked via WhatsApp Check B"
) -> Optional[FlaggedEntity]:
    """
    Ingests family feedback from Check B.
    If verdict is 'BLOCK', promotes the entity to the global blocklist.
    """
    if not db or not entity_value:
        return None

    VALID_ENTITY_TYPES = {"upi_id", "upi", "phone", "link", "account", "email"}
    if entity_type not in VALID_ENTITY_TYPES:
        import logging
        logging.getLogger(__name__).warning(
            "[SafeLoop Retrainer] Unrecognised entity_type '%s'. "
            "Accepted values: %s. Defaulting to 'upi_id'.",
            entity_type, VALID_ENTITY_TYPES,
        )
        entity_type = "upi_id"

    clean_val = entity_value.strip().lower()

    if verdict.upper() == "BLOCK":
        # Check if already present
        existing = db.query(FlaggedEntity).filter(
            FlaggedEntity.entity_value == clean_val
        ).first()

        if existing:
            existing.risk_score = 1.0
            existing.reason = reason
            existing.source = "family_block"
            target_entity = existing
        else:
            target_entity = FlaggedEntity(
                entity_type=entity_type,
                entity_value=clean_val,
                source="family_block",
                risk_score=1.0,
                reason=reason,
                created_at=datetime.utcnow()
            )
            db.add(target_entity)

        # Log audit trail
        log_event(
            db=db,
            event_type="FEEDBACK_BLOCKLIST_UPDATED",
            details={
                "entity": clean_val,
                "action": "ADDED_TO_BLOCKLIST",
                "source": "family_block",
                "reporter_phone": reporter_phone
            },
            user_id=reporter_phone
        )

        db.commit()
        db.refresh(target_entity)
        return target_entity

    return None


def calculate_metrics(
    samples: List[Dict[str, Any]],
    db: Optional[Session] = None
) -> Dict[str, float]:
    """
    Runs the Risk Engine on a list of samples and computes statistical metrics.
    """
    tp = 0
    fp = 0
    tn = 0
    fn = 0

    for item in samples:
        text = item.get("text", "")
        is_scam = item.get("category") == "scam"
        entities = item.get("entities", {})

        result = evaluate_risk(
            message_type="text",
            text=text,
            entities=entities,
            db=db
        )
        predicted_as_scam = result["level"] in ["high", "suspicious"]

        if is_scam and predicted_as_scam:
            tp += 1
        elif not is_scam and not predicted_as_scam:
            tn += 1
        elif not is_scam and predicted_as_scam:
            fp += 1
        elif is_scam and not predicted_as_scam:
            fn += 1

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0

    return {
        "total": len(samples),
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "precision": round(precision * 100, 1),
        "recall": round(recall * 100, 1),
        "f1": round(f1 * 100, 1),
        "fpr": round(fpr * 100, 1)
    }
