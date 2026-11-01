"""
SafeLoop Audit Logger (L8: Trust & Responsibility)
Owned by: Person 4 (Arun)

Maintains an immutable, append-only event stream of all security-critical operations:
- Scam detections & risk evaluations
- Payment hold triggers
- Check A code attempts (only record pass/fail/attempt count, NEVER the plain code)
- Check B family approvals and blocks
- Global blocklist updates

User IDs are cryptographically hashed (SHA-256) to ensure privacy compliance.
"""

import json
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import Event


def hash_identifier(identifier: Optional[str]) -> Optional[str]:
    """Computes a SHA-256 hash of an identifier (phone or user ID) for PII safety."""
    if not identifier:
        return None
    return hashlib.sha256(str(identifier).strip().encode("utf-8")).hexdigest()[:16]


def log_event(
    db: Session,
    event_type: str,
    details: Dict[str, Any],
    user_id: Optional[str] = None
) -> Event:
    """
    Appends a new immutable event log entry into the database.
    
    Args:
        db: Active SQLAlchemy session
        event_type: Event category (e.g., 'SCAM_DETECTED', 'PAYMENT_HELD', 'CHECK_A_ATTEMPT', 'CHECK_B_DECISION')
        details: Dict containing structured context (must NOT contain plaintext passwords or full PII)
        user_id: Raw user phone/ID (will be hashed automatically)
        
    Returns:
        The created Event database instance
    """
    hashed_user = hash_identifier(user_id) if user_id else None
    
    event = Event(
        user_id_hash=hashed_user,
        event_type=event_type,
        details_json=json.dumps(details, default=str),
        created_at=datetime.utcnow()
    )
    
    db.add(event)
    # NOTE: We use flush() here, not commit(). This writes the row to the
    # current transaction so the caller gets a valid event.id, but the actual
    # COMMIT is left to the calling scope. This prevents double-commit issues
    # when log_event is nested inside another transaction (e.g., record_family_feedback).
    db.flush()
    db.refresh(event)
    return event
