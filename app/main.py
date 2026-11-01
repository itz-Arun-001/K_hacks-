"""
SafeLoop Backend Entrypoint (FastAPI)
Architecture: Layer 1 (API Gateway) & Layer 8 (Audit Integration)
Owned by: Person 4 (Arun) & Team SafeLoop
"""

import os
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import init_db, get_db, Event, FlaggedEntity
from app.services.risk_engine import evaluate_risk
from app.services.retrainer import record_family_feedback
from app.utils.audit import log_event


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on server startup
    print("\n[SafeLoop] Initializing database tables...")
    init_db()
    print("[SafeLoop] Database initialized successfully (SQLite / Neon Postgres ready).\n")
    yield
    print("[SafeLoop] Server shutting down...")


app = FastAPI(
    title="SafeLoop API",
    description="WhatsApp Fraud Shield & Risk Engine for Elderly Protection",
    version="0.1.0",
    lifespan=lifespan
)

# Enable CORS for local Streamlit / Frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==============================================================================
# Pydantic Schemas for Layer 1 API Contracts
# ==============================================================================

class EntitiesSchema(BaseModel):
    links: list[str] = Field(default_factory=list)
    phones: list[str] = Field(default_factory=list)
    upi_ids: list[str] = Field(default_factory=list)
    amounts: list[float] = Field(default_factory=list)


class RiskCheckRequest(BaseModel):
    user_id: Optional[str] = None
    message_type: str = Field(default="text", description="text, voice, or payment")
    text: Optional[str] = Field(default="", description="Raw text or transcribed audio")
    entities: Optional[EntitiesSchema] = Field(default_factory=EntitiesSchema)
    scam_tags: Optional[Dict[str, Any]] = Field(default_factory=dict)


class RiskCheckResponse(BaseModel):
    score: float
    level: str  # "safe", "suspicious", "high"
    reasons: list[str]


class FeedbackRequest(BaseModel):
    entity_type: str = Field(..., description="upi_id, phone, link, or account", max_length=32)
    entity_value: str = Field(..., description="Malicious or approved entity identifier", max_length=256)
    verdict: str = Field(..., description="'BLOCK' or 'APPROVE'", pattern="^(BLOCK|APPROVE)$")
    reporter_phone: Optional[str] = Field(default=None, description="Phone of family member", max_length=32)
    reason: Optional[str] = Field(default="Family member blocked via WhatsApp Check B", max_length=256)


# ==============================================================================
# Core API Routes
# ==============================================================================

@app.get("/")
def health_check():
    """Health check endpoint for deployment monitoring."""
    return {
        "status": "online",
        "service": "SafeLoop Fraud Shield API",
        "version": "0.1.0",
        "team": "Team SafeLoop"
    }


@app.post("/risk-check", response_model=RiskCheckResponse)
def check_risk(payload: RiskCheckRequest, db: Session = Depends(get_db)):
    """
    Core Risk Assessment API.
    Called by:
    - Person 1's WhatsApp webhook handler
    - Person 2's Mock payment screen
    - External banking/UPI simulator
    """
    entities_dict = payload.entities.model_dump() if payload.entities else {}
    
    result = evaluate_risk(
        user_id=payload.user_id,
        message_type=payload.message_type,
        text=payload.text,
        entities=entities_dict,
        scam_tags=payload.scam_tags,
        db=db
    )

    # Layer 8: Log audit event for high/suspicious checks
    if result["level"] in ["high", "suspicious"]:
        log_event(
            db=db,
            event_type="RISK_CHECK_EVALUATED",
            details={
                "level": result["level"],
                "score": result["score"],
                "reasons": result["reasons"],
                "message_type": payload.message_type
            },
            user_id=payload.user_id
        )

    return result


@app.get("/audit-logs")
def view_audit_logs(limit: int = 50, db: Session = Depends(get_db)):
    """Fetches recent audit log entries (L8 compliance verification)."""
    limit = max(1, min(limit, 500))  # Guard: clamp to [1, 500]
    logs = db.query(Event).order_by(Event.created_at.desc()).limit(limit).all()
    return [
        {
            "id": log.id,
            "event_type": log.event_type,
            "user_id_hash": log.user_id_hash,
            "details": log.details_json,
            "created_at": log.created_at
        }
        for log in logs
    ]


@app.post("/feedback")
def submit_family_feedback(payload: FeedbackRequest, db: Session = Depends(get_db)):
    """
    Check B Family Feedback Endpoint (L6: Active Learning Loop).
    Called by Person 2's Twilio webhook when Son replies 'BLOCK' or 'APPROVE'.
    Automatically writes malicious entities to the global threat blocklist.
    """
    flagged = record_family_feedback(
        db=db,
        entity_type=payload.entity_type,
        entity_value=payload.entity_value,
        verdict=payload.verdict,
        reporter_phone=payload.reporter_phone,
        reason=payload.reason
    )
    
    if flagged:
        return {
            "status": "success",
            "action": "ENTITY_BLACKLISTED",
            "entity": flagged.entity_value,
            "risk_score": flagged.risk_score,
            "message": f"Entity '{flagged.entity_value}' has been permanently added to the global blocklist."
        }
    return {
        "status": "success",
        "action": "FEEDBACK_RECORDED",
        "verdict": payload.verdict,
        "message": "Feedback recorded without blocklist elevation."
    }


@app.get("/flagged-entities")
def list_flagged_entities(limit: int = 100, db: Session = Depends(get_db)):
    """
    Threat Intelligence Query API (L5: Mule Network).
    Called by Person 3's Bank Mule Graph Console to visualize flagged hubs.
    """
    limit = max(1, min(limit, 1000))  # Guard: clamp to [1, 1000]
    entities = db.query(FlaggedEntity).order_by(FlaggedEntity.created_at.desc()).limit(limit).all()
    return [
        {
            "id": e.id,
            "entity_type": e.entity_type,
            "entity_value": e.entity_value,
            "source": e.source,
            "risk_score": e.risk_score,
            "reason": e.reason,
            "created_at": e.created_at
        }
        for e in entities
    ]

