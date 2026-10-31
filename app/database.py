"""
SafeLoop Database Models & Engine Configuration
Owned by: Person 4 (Arun)

Supports dual environments seamlessly:
1. SQLite: Local development / offline hackathon fallback
2. Neon PostgreSQL: Shared team database for cloud collaboration
"""

import os
from datetime import datetime
from typing import Generator
from dotenv import load_dotenv

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

load_dotenv()

# Default to SQLite local database if not specified
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./safeloop.db")

# Handle SQLite vs PostgreSQL engine arguments
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ==============================================================================
# 1. User & Contact Models (Used by Person 2: Registration & Guard)
# ==============================================================================

class User(Base):
    """Elderly user profile (Amma / Appa)"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(32), unique=True, index=True, nullable=False)
    name = Column(String(128), nullable=True)
    language_pref = Column(String(16), default="en")  # "en", "hi", "ta"
    consent_given = Column(Boolean, default=False, nullable=False)
    onboarded_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    family_contacts = relationship("FamilyContact", back_populates="user", cascade="all, delete-orphan")
    trusted_payees = relationship("TrustedPayee", back_populates="user", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="user")
    payments = relationship("Payment", back_populates="user")


class FamilyContact(Base):
    """Family members authorized for Check A (code) & Check B (approval)"""
    __tablename__ = "family_contacts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    contact_name = Column(String(128), nullable=False)
    contact_phone = Column(String(32), index=True, nullable=False)
    relation = Column(String(64), default="child")  # "son", "daughter", "relative"
    priority = Column(Integer, default=1)  # 1 = primary, 2 = secondary fallback
    family_code_hash = Column(String(256), nullable=True)  # bcrypt hash of secret code
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="family_contacts")


class TrustedPayee(Base):
    """Whitelist of known shops, utilities, and relatives that pass without friction"""
    __tablename__ = "trusted_payees"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    payee_identifier = Column(String(128), index=True, nullable=False)  # UPI ID, phone, account number
    nickname = Column(String(128), nullable=False)  # "Milkman Anand", "TNEB Electricity"
    category = Column(String(64), default="shop")  # "shop", "utility", "family", "doctor"
    added_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="trusted_payees")


# ==============================================================================
# 2. Message & Verdict Models (Used by Person 1: Bot & LLM Analyzer)
# ==============================================================================

class Message(Base):
    """Log of every inbound and outbound message/voice note"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    direction = Column(String(16), default="inbound")  # "inbound", "outbound"
    message_type = Column(String(16), default="text")  # "text", "voice", "payment_request"
    raw_text = Column(Text, nullable=True)
    transcript = Column(Text, nullable=True)  # Whisper output for voice notes
    sender_phone = Column(String(32), index=True, nullable=False)
    received_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="messages")
    verdict = relationship("Verdict", back_populates="message", uselist=False)


class Verdict(Base):
    """Risk analysis result for an ingested message or voice note"""
    __tablename__ = "verdicts"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False)
    risk_score = Column(Float, nullable=False)  # Calibrated 0.0 to 1.0
    risk_level = Column(String(16), nullable=False)  # "safe", "suspicious", "high"
    scam_type = Column(String(64), nullable=True)  # "digital_arrest", "kbc_lottery", "electricity_cut", etc.
    tactics_json = Column(Text, nullable=True)  # JSON array: ["urgency", "authority", "secrecy"]
    reasons_json = Column(Text, nullable=True)  # JSON array of explanation bullet points
    created_at = Column(DateTime, default=datetime.utcnow)

    message = relationship("Message", back_populates="verdict")


# ==============================================================================
# 3. Global Threat Intelligence & Blocklist (Used by All & Person 4)
# ==============================================================================

class FlaggedEntity(Base):
    """Global blocklist fed by user reports, family BLOCKs, and graph analytics"""
    __tablename__ = "flagged_entities"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(32), index=True, nullable=False)  # "upi", "phone", "url", "bank_account"
    entity_value = Column(String(256), index=True, unique=True, nullable=False)
    source = Column(String(64), nullable=False)  # "family_block", "mule_graph", "user_report", "safebrowsing"
    risk_score = Column(Float, default=1.0)
    reason = Column(String(256), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# ==============================================================================
# 4. Two-Key Payment Guard Models (Used by Person 2: Guard & Holds)
# ==============================================================================

class Payment(Base):
    """Payment transaction attempt and its lifecycle state"""
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    payee_identifier = Column(String(128), index=True, nullable=False)
    amount = Column(Float, nullable=False)
    for_family = Column(Boolean, default=False)  # True if caller claimed relative in distress
    status = Column(String(32), default="held")  # "allowed", "held", "blocked", "released", "expired"
    risk_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="payments")
    approvals = relationship("Approval", back_populates="payment", cascade="all, delete-orphan")


class Approval(Base):
    """Two-key verification events (Check A family code & Check B family WhatsApp approval)"""
    __tablename__ = "approvals"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False)
    check_type = Column(String(32), nullable=False)  # "check_a_code", "check_b_family_approval"
    reviewer_phone = Column(String(32), nullable=True)  # Son's phone for Check B
    status = Column(String(32), default="pending")  # "pending", "approved", "rejected", "lockout", "expired"
    attempts = Column(Integer, default=0)  # Max 3 attempts for Check A
    responded_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    payment = relationship("Payment", back_populates="approvals")


# ==============================================================================
# 5. Financial Graph & Mule Accounts (Used by Person 3: Graph & Bank Console)
# ==============================================================================

class Account(Base):
    """Simulated banking account node in the mule graph"""
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(String(64), unique=True, index=True, nullable=False)
    upi_id = Column(String(128), unique=True, index=True, nullable=True)
    owner_name = Column(String(128), nullable=False)
    bank_name = Column(String(64), default="Simulated Bank")
    is_mule = Column(Boolean, default=False)
    ring_id = Column(String(64), nullable=True)  # Identifier for planted fraud ring
    risk_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)


class Transaction(Base):
    """Simulated transaction edges connecting accounts in the financial network"""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    sender_account = Column(String(64), index=True, nullable=False)
    receiver_account = Column(String(64), index=True, nullable=False)
    amount = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_mule_flow = Column(Boolean, default=False)


# ==============================================================================
# 6. Immutable Audit Log (L8 Trust & Compliance - Person 4)
# ==============================================================================

class Event(Base):
    """Append-only audit trail for all security, payment, and analysis events"""
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    user_id_hash = Column(String(64), index=True, nullable=True)  # Anonymized user ID hash
    event_type = Column(String(64), index=True, nullable=False)  # "SCAM_DETECTED", "HOLD_TRIGGERED", "CHECK_B_APPROVED"
    details_json = Column(Text, nullable=False)  # JSON payload of details
    created_at = Column(DateTime, default=datetime.utcnow)


# ==============================================================================
# Database Helper Functions
# ==============================================================================

def init_db():
    """Initializes and creates all database tables if they do not exist."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator:
    """FastAPI dependency for obtaining a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
