"""
SafeLoop Two-Key Payment Guard State Machine (L4: Protect)
Owned by: Person 2 (Geerthiga)

The Two-Key Guard protects elderly users (Amma / Appa) from coerced financial transactions:
1. Whitelist Fast-Path: Trusted payees (milkman, electricity, approved shops) pass instantly with 0 friction.
2. Risk & Anomaly Interception: Unverified or high-risk transfers are placed in an escrow HOLD.
3. Check A (Secret Family Code): When the caller claims to be a relative in trouble or hospital emergency,
   Amma enters an agreed-upon offline family secret code (bcrypt hash match with 3-attempt lockout).
4. Check B (Real Family WhatsApp Approval): The real family member (Son Rahul) receives an interactive alert:
   "Amma is attempting to pay ₹X to Y. Reply APPROVE, BLOCK, or CALL HER".
   - A correct Check A code NEVER releases money on its own; Check B is authoritative.
   - If Rahul replies BLOCK, the transaction is cancelled and the payee is automatically elevated
     to the global cybercrime blocklist via Person 4's active learning retrainer.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

try:
    import bcrypt
except ImportError:
    bcrypt = None

from sqlalchemy.orm import Session
from app.database import Payment, Approval, User, FamilyContact, TrustedPayee, FlaggedEntity
from app.services.risk_engine import evaluate_risk
from app.services.baseline import evaluate_baseline_deviation
from app.services.retrainer import record_family_feedback
from app.utils.audit import log_event

logger = logging.getLogger("safeloop.guard")

MAX_CHECK_A_ATTEMPTS = 3
DEFAULT_COOLING_OFF_MINUTES = 15


class TwoKeyGuardService:
    """Manages the full lifecycle of payment holds, Check A, and Check B verifications."""

    @staticmethod
    def hash_family_code(plain_code: str) -> str:
        """Computes a secure bcrypt hash of a family secret code."""
        if not bcrypt:
            raise ImportError("bcrypt is required to hash family secret codes.")
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(plain_code.strip().encode("utf-8"), salt).decode("utf-8")

    @staticmethod
    def verify_family_code(plain_code: str, hashed_code: str) -> bool:
        """Verifies a plain secret code against a stored bcrypt hash."""
        if not bcrypt or not plain_code or not hashed_code:
            return False
        try:
            return bcrypt.checkpw(plain_code.strip().encode("utf-8"), hashed_code.encode("utf-8"))
        except Exception as e:
            logger.error("[Guard] Error verifying family code hash: %s", e)
            return False

    @classmethod
    def initiate_payment(
        cls,
        db: Session,
        user_id: int,
        payee_identifier: str,
        amount: float,
        for_family: bool = False,
        context_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Initiates a payment transaction attempt and executes the Two-Key Guard evaluation.

        Returns:
            Dict containing:
            - payment_id: int
            - status: 'allowed' | 'held' | 'blocked'
            - next_step: None | 'check_a' | 'check_b'
            - risk_score: float
            - risk_level: str
            - reasons: List[str]
            - guardian_contact: Optional[Dict]
        """
        clean_payee = (payee_identifier or "").strip().lower()

        # Fetch user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User ID {user_id} not found in database.")

        # ----------------------------------------------------------------------
        # 1. Fast-Path: Whitelisted Trusted Payee Check (Zero Friction)
        # ----------------------------------------------------------------------
        trusted = db.query(TrustedPayee).filter(
            TrustedPayee.user_id == user_id,
            TrustedPayee.payee_identifier.ilike(clean_payee)
        ).first()

        if trusted:
            # Trusted payee passes without friction
            payment = Payment(
                user_id=user_id,
                payee_identifier=clean_payee,
                amount=amount,
                for_family=for_family,
                status="allowed",
                risk_score=0.05,
                created_at=datetime.utcnow()
            )
            db.add(payment)
            db.commit()
            db.refresh(payment)

            log_event(
                db=db,
                event_type="PAYMENT_ALLOWED_FASTPATH",
                details={
                    "payment_id": payment.id,
                    "payee": clean_payee,
                    "nickname": trusted.nickname,
                    "category": trusted.category,
                    "amount": amount
                },
                user_id=str(user_id)
            )

            return {
                "payment_id": payment.id,
                "status": "allowed",
                "next_step": None,
                "risk_score": 0.05,
                "risk_level": "safe",
                "reasons": [f"Payee '{trusted.nickname}' is on your verified trusted payee list."]
            }

        # ----------------------------------------------------------------------
        # 2. Risk Engine & Spending Baseline Anomaly Assessment
        # ----------------------------------------------------------------------
        eval_text = context_text or f"Transfer Rs {amount} to {clean_payee}"
        entities_dict = {
            "amounts": [amount],
            "upi_ids": [clean_payee] if "@" in clean_payee else [],
            "phones": [clean_payee] if clean_payee.replace("+", "").isdigit() else []
        }

        risk_assessment = evaluate_risk(
            user_id=str(user_id),
            message_type="payment",
            text=eval_text,
            entities=entities_dict,
            db=db
        )

        composite_score = risk_assessment["score"]
        composite_level = risk_assessment["level"]
        reasons = list(risk_assessment["reasons"])

        # Check if payee is on threat blocklist
        flagged = db.query(FlaggedEntity).filter(
            FlaggedEntity.entity_value == clean_payee
        ).first()
        if flagged:
            composite_score = 1.0
            composite_level = "high"
            reasons.insert(0, f"Payee '{clean_payee}' is blacklisted: {flagged.reason or 'Confirmed Fraud Ring'}.")

        # ----------------------------------------------------------------------
        # 3. Two-Key Guard State Enforcement
        # ----------------------------------------------------------------------
        # Rule: Any unverified payee, high amount, anomaly, or scam context triggers ESCROW HOLD
        is_held = (
            composite_level in ["high", "suspicious"]
            or composite_score >= 0.35
            or for_family
            or flagged is not None
        )

        payment_status = "held" if is_held else "allowed"

        payment = Payment(
            user_id=user_id,
            payee_identifier=clean_payee,
            amount=amount,
            for_family=for_family,
            status=payment_status,
            risk_score=composite_score,
            created_at=datetime.utcnow()
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)

        # If payment is allowed directly
        if payment_status == "allowed":
            log_event(
                db=db,
                event_type="PAYMENT_ALLOWED_DIRECT",
                details={
                    "payment_id": payment.id,
                    "payee": clean_payee,
                    "amount": amount,
                    "score": composite_score
                },
                user_id=str(user_id)
            )
            return {
                "payment_id": payment.id,
                "status": "allowed",
                "next_step": None,
                "risk_score": composite_score,
                "risk_level": composite_level,
                "reasons": reasons
            }

        # ----------------------------------------------------------------------
        # 4. Payment is HELD -> Determine whether Check A or Check B is next
        # ----------------------------------------------------------------------
        # Fetch family contact (Guardian)
        family_member = db.query(FamilyContact).filter(
            FamilyContact.user_id == user_id
        ).order_by(FamilyContact.priority.asc()).first()

        guardian_info = None
        if family_member:
            guardian_info = {
                "name": family_member.contact_name,
                "phone": family_member.contact_phone,
                "relation": family_member.relation
            }

        # If transaction claims to be for a family member or friend in trouble, Check A is required first!
        if for_family and family_member and family_member.family_code_hash:
            next_step = "check_a"
            approval_record = Approval(
                payment_id=payment.id,
                check_type="check_a",
                reviewer_phone=family_member.contact_phone,
                status="pending",
                attempts=0,
                created_at=datetime.utcnow()
            )
            db.add(approval_record)
            db.commit()
        else:
            # Check B directly (Son's interactive WhatsApp approval)
            next_step = "check_b"
            approval_record = Approval(
                payment_id=payment.id,
                check_type="check_b",
                reviewer_phone=family_member.contact_phone if family_member else None,
                status="pending",
                attempts=0,
                created_at=datetime.utcnow()
            )
            db.add(approval_record)
            db.commit()

        log_event(
            db=db,
            event_type="PAYMENT_HELD_BY_GUARD",
            details={
                "payment_id": payment.id,
                "payee": clean_payee,
                "amount": amount,
                "score": composite_score,
                "next_step": next_step,
                "for_family": for_family
            },
            user_id=str(user_id)
        )

        return {
            "payment_id": payment.id,
            "status": "held",
            "next_step": next_step,
            "risk_score": composite_score,
            "risk_level": composite_level,
            "reasons": reasons,
            "guardian_contact": guardian_info,
            "message_to_user": "⚠️ Payment has been safely paused by SafeLoop Two-Key Guard. Please stay calm."
        }

    @classmethod
    def evaluate_check_a(
        cls,
        db: Session,
        payment_id: int,
        secret_code_input: str
    ) -> Dict[str, Any]:
        """
        Executes Check A: Verifies the entered secret family code against the stored bcrypt hash.
        Includes a 3-attempt lockout policy.
        """
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise ValueError(f"Payment ID {payment_id} does not exist.")

        if payment.status != "held":
            return {
                "success": False,
                "payment_status": payment.status,
                "message": f"Payment is already '{payment.status}'. Cannot evaluate Check A."
            }

        # Find Check A approval record
        approval = db.query(Approval).filter(
            Approval.payment_id == payment_id,
            Approval.check_type == "check_a"
        ).first()

        if not approval:
            # Create if missing
            approval = Approval(
                payment_id=payment_id,
                check_type="check_a",
                status="pending",
                attempts=0,
                created_at=datetime.utcnow()
            )
            db.add(approval)
            db.commit()
            db.refresh(approval)

        # Check for lockout
        if approval.attempts >= MAX_CHECK_A_ATTEMPTS:
            payment.status = "blocked"
            approval.status = "rejected"
            db.commit()

            log_event(
                db=db,
                event_type="CHECK_A_LOCKOUT_BLOCKED",
                details={
                    "payment_id": payment_id,
                    "attempts": approval.attempts,
                    "reason": "Exceeded 3 attempts for secret family code"
                },
                user_id=str(payment.user_id)
            )

            return {
                "success": False,
                "payment_status": "blocked",
                "next_step": None,
                "message": "🚨 Security Lockout: Incorrect secret code entered 3 times. Transaction cancelled to protect your account. Family alerted."
            }

        # Fetch user's family contact
        family_member = db.query(FamilyContact).filter(
            FamilyContact.user_id == payment.user_id
        ).order_by(FamilyContact.priority.asc()).first()

        if not family_member or not family_member.family_code_hash:
            return {
                "success": False,
                "payment_status": payment.status,
                "message": "No secret family code registered for this user profile."
            }

        # Increment attempt count
        approval.attempts += 1
        is_match = cls.verify_family_code(secret_code_input, family_member.family_code_hash)

        if is_match:
            approval.status = "approved"
            approval.responded_at = datetime.utcnow()

            # ARCHITECTURAL SAFEGUARD:
            # Check A match alone NEVER releases money. It unlocks Check B!
            check_b_record = db.query(Approval).filter(
                Approval.payment_id == payment_id,
                Approval.check_type == "check_b"
            ).first()

            if not check_b_record:
                check_b_record = Approval(
                    payment_id=payment_id,
                    check_type="check_b",
                    reviewer_phone=family_member.contact_phone,
                    status="pending",
                    attempts=0,
                    created_at=datetime.utcnow()
                )
                db.add(check_b_record)

            db.commit()

            log_event(
                db=db,
                event_type="CHECK_A_PASSED",
                details={
                    "payment_id": payment_id,
                    "attempts": approval.attempts,
                    "guardian": family_member.contact_phone
                },
                user_id=str(payment.user_id)
            )

            return {
                "success": True,
                "payment_status": "held",
                "next_step": "check_b",
                "message": f"✅ Secret code verified. Check B initiated: Live approval requested from {family_member.contact_name} ({family_member.relation})."
            }
        else:
            remaining = MAX_CHECK_A_ATTEMPTS - approval.attempts
            if remaining <= 0:
                payment.status = "blocked"
                approval.status = "rejected"
                db.commit()
                return {
                    "success": False,
                    "payment_status": "blocked",
                    "next_step": None,
                    "message": "🚨 Incorrect code. Maximum attempts reached. Transaction blocked for safety."
                }
            
            db.commit()
            return {
                "success": False,
                "payment_status": "held",
                "next_step": "check_a",
                "remaining_attempts": remaining,
                "message": f"❌ Incorrect secret code. {remaining} attempt(s) remaining before automatic lockout."
            }

    @classmethod
    def evaluate_check_b(
        cls,
        db: Session,
        payment_id: int,
        action: str,  # "APPROVE", "BLOCK", "CALL_HER"
        reviewer_phone: Optional[str] = None,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes Check B: Ingests the real family member's WhatsApp response.
        - APPROVE -> Releases payment (status: 'released').
        - BLOCK   -> Cancels payment (status: 'blocked') & writes payee to threat blocklist.
        - CALL_HER -> Keeps held & advises calling immediately.
        """
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise ValueError(f"Payment ID {payment_id} does not exist.")

        action_upper = action.strip().upper()

        approval = db.query(Approval).filter(
            Approval.payment_id == payment_id,
            Approval.check_type == "check_b"
        ).first()

        if not approval:
            approval = Approval(
                payment_id=payment_id,
                check_type="check_b",
                status="pending",
                attempts=0,
                created_at=datetime.utcnow()
            )
            db.add(approval)

        approval.reviewer_phone = reviewer_phone or approval.reviewer_phone
        approval.responded_at = datetime.utcnow()

        if action_upper == "APPROVE":
            payment.status = "released"
            approval.status = "approved"
            db.commit()

            log_event(
                db=db,
                event_type="CHECK_B_APPROVED",
                details={
                    "payment_id": payment_id,
                    "amount": payment.amount,
                    "payee": payment.payee_identifier,
                    "reviewer_phone": reviewer_phone
                },
                user_id=str(payment.user_id)
            )

            return {
                "success": True,
                "action": "APPROVED",
                "payment_status": "released",
                "message": "✅ Family member approved the transaction. Payment has been securely released."
            }

        elif action_upper == "BLOCK":
            payment.status = "blocked"
            approval.status = "rejected"
            db.commit()

            # Active Learning Loop: Add entity to threat intelligence blocklist!
            block_reason = reason or "Family member blocked transfer via WhatsApp Check B"
            flagged = record_family_feedback(
                db=db,
                entity_type="upi_id" if "@" in payment.payee_identifier else "phone",
                entity_value=payment.payee_identifier,
                verdict="BLOCK",
                reporter_phone=reviewer_phone,
                reason=block_reason
            )

            log_event(
                db=db,
                event_type="CHECK_B_BLOCKED",
                details={
                    "payment_id": payment_id,
                    "amount": payment.amount,
                    "payee": payment.payee_identifier,
                    "reviewer_phone": reviewer_phone,
                    "blacklisted": flagged is not None
                },
                user_id=str(payment.user_id)
            )

            return {
                "success": True,
                "action": "BLOCKED",
                "payment_status": "blocked",
                "blacklisted_entity": payment.payee_identifier,
                "message": f"🚨 Family member blocked the payment. Transaction aborted ($0 loss). Payee '{payment.payee_identifier}' added to national threat blocklist."
            }

        elif action_upper in ["CALL_HER", "CALL"]:
            approval.status = "call_requested"
            db.commit()

            log_event(
                db=db,
                event_type="CHECK_B_CALL_REQUESTED",
                details={"payment_id": payment_id, "reviewer_phone": reviewer_phone},
                user_id=str(payment.user_id)
            )

            return {
                "success": True,
                "action": "CALL_REQUESTED",
                "payment_status": "held",
                "message": "📞 Guardian requested immediate telephone contact. Payment remains safely HELD."
            }

        else:
            raise ValueError(f"Invalid Check B action '{action}'. Expected 'APPROVE', 'BLOCK', or 'CALL_HER'.")

    @classmethod
    def get_payment_status(cls, db: Session, payment_id: int) -> Dict[str, Any]:
        """Fetches the current real-time status and audit trail of a payment."""
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise ValueError(f"Payment ID {payment_id} not found.")

        approvals = db.query(Approval).filter(Approval.payment_id == payment_id).all()
        approvals_list = [
            {
                "check_type": a.check_type,
                "status": a.status,
                "attempts": a.attempts,
                "responded_at": a.responded_at.isoformat() if a.responded_at else None
            }
            for a in approvals
        ]

        return {
            "payment_id": payment.id,
            "user_id": payment.user_id,
            "payee_identifier": payment.payee_identifier,
            "amount": payment.amount,
            "status": payment.status,
            "risk_score": payment.risk_score,
            "created_at": payment.created_at.isoformat(),
            "approvals": approvals_list
        }

