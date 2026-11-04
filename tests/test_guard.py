"""
SafeLoop Two-Key Family Guard Comprehensive Test Suite
Author: Person 2 (Geerthiga) & Person 4 (Arun)

Validates the full Two-Key Guard lifecycle:
1. Whitelist Fast-Path (Zero Friction for known vendors)
2. Risk & Anomaly Escrow Hold (High-value or unverified payees)
3. Check A: Secret Family Code with 3-attempt lockout policy
4. Check A Safeguard: Correct code NEVER releases funds alone; unlocks Check B
5. Check B: Son Rahul interactive WhatsApp approval releases payment
6. Check B: Son Rahul BLOCK aborts payment ($0 loss) & adds payee to threat blocklist
7. Community Immunity: Blacklisted entity blocked automatically on subsequent attempts
8. Speech-to-Text (STT) Whisper Voice Note Ingestion
"""

import os
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure root folder is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import SessionLocal, init_db, Payment, Approval, User, FamilyContact, TrustedPayee, FlaggedEntity
from app.services.guard import TwoKeyGuardService
from app.services.stt import transcribe_voice_note


def test_whitelisted_payee_fastpath(db):
    print("\n[Test 1: Whitelisted Payee Fast-Path (Zero Friction)]")
    # Anand milkman is whitelisted in seed data
    result = TwoKeyGuardService.initiate_payment(
        db=db,
        user_id=1,
        payee_identifier="anand.milk@upi",
        amount=450.0,
        for_family=False
    )
    print(f"  • Result: Status = {result['status']} | Risk Score = {result['risk_score']}")
    print(f"  • Reasons: {result['reasons']}")

    assert result["status"] == "allowed", "Whitelisted payee must be allowed immediately without hold"
    assert result["next_step"] is None
    assert result["risk_score"] <= 0.20
    print("  [PASS] Whitelisted payee released with zero friction.")


def test_unverified_high_risk_held(db):
    print("\n[Test 2: High-Risk Unverified Payee Escrow Hold]")
    # Scammer demanding 50k
    result = TwoKeyGuardService.initiate_payment(
        db=db,
        user_id=1,
        payee_identifier="clearance.cop@sbi",
        amount=50000.0,
        for_family=False,
        context_text="CBI digital arrest warrant pay 50000 immediately"
    )
    print(f"  • Result: Status = {result['status']} | Next Step = {result['next_step']}")
    print(f"  • Risk Score = {result['risk_score']} | Reasons = {result['reasons']}")

    assert result["status"] == "held", "High risk novel payee must be placed in escrow HOLD"
    assert result["next_step"] == "check_b", "Direct high-risk transfer should prompt family Check B"
    assert result["risk_score"] >= 0.70
    print("  [PASS] High-risk payment held behind Two-Key Guard.")


def test_check_a_lockout_policy(db):
    print("\n[Test 3: Check A Secret Code Verification & 3-Attempt Lockout]")
    # Payment claiming to be for relative in hospital
    init_res = TwoKeyGuardService.initiate_payment(
        db=db,
        user_id=1,
        payee_identifier="hospital.desk@okaxis",
        amount=25000.0,
        for_family=True
    )
    payment_id = init_res["payment_id"]
    assert init_res["status"] == "held"
    assert init_res["next_step"] == "check_a"

    # Attempt 1: Wrong code
    try1 = TwoKeyGuardService.evaluate_check_a(db, payment_id, "wrong_code_1")
    assert try1["success"] is False
    assert try1["payment_status"] == "held"
    assert try1["remaining_attempts"] == 2
    print("  • Attempt 1 (Wrong): 2 tries remaining.")

    # Attempt 2: Wrong code
    try2 = TwoKeyGuardService.evaluate_check_a(db, payment_id, "wrong_code_2")
    assert try2["success"] is False
    assert try2["remaining_attempts"] == 1
    print("  • Attempt 2 (Wrong): 1 try remaining.")

    # Attempt 3: Wrong code -> LOCKOUT!
    try3 = TwoKeyGuardService.evaluate_check_a(db, payment_id, "wrong_code_3")
    assert try3["success"] is False
    assert try3["payment_status"] == "blocked"
    print("  • Attempt 3 (Wrong): Lockout triggered -> Status is 'blocked'.")

    # Verify in DB
    p_db = db.query(Payment).filter(Payment.id == payment_id).first()
    assert p_db.status == "blocked", "Payment must be permanently blocked after 3 failed attempts"
    print("  [PASS] 3-attempt lockout successfully protected user.")


def test_check_a_success_unlocks_check_b(db):
    print("\n[Test 4: Check A Success Unlocks Check B (Code Alone Cannot Release)]")
    # Initiate fresh payment
    init_res = TwoKeyGuardService.initiate_payment(
        db=db,
        user_id=1,
        payee_identifier="friend.emergency@upi",
        amount=15000.0,
        for_family=True
    )
    payment_id = init_res["payment_id"]

    # Enter correct secret code ("anandham")
    check_a_res = TwoKeyGuardService.evaluate_check_a(db, payment_id, "anandham")
    print(f"  • Check A Result: Success = {check_a_res['success']} | Status = {check_a_res['payment_status']}")
    print(f"  • Message: {check_a_res['message']}")

    assert check_a_res["success"] is True
    # CRITICAL INVARIANT: Money is STILL HELD! It cannot release without Rahul's approval!
    assert check_a_res["payment_status"] == "held"
    assert check_a_res["next_step"] == "check_b"

    print("  [PASS] Check A passed and transitioned to Check B without leaking funds.")

    # Now Rahul approves Check B
    check_b_res = TwoKeyGuardService.evaluate_check_b(
        db=db,
        payment_id=payment_id,
        action="APPROVE",
        reviewer_phone="+919876543211"
    )
    assert check_b_res["success"] is True
    assert check_b_res["payment_status"] == "released"
    print("  • Check B: Rahul approved -> Payment status is 'released'.")
    print("  [PASS] Two-Key workflow executed cleanly.")


def test_check_b_block_and_community_immunity(db):
    print("\n[Test 5: Check B BLOCK & Instant Community Threat Blacklist]")
    syndicate_upi = "scam.mule.ring99@paytm"

    # Step 1: Amma initiates payment
    init_res = TwoKeyGuardService.initiate_payment(
        db=db,
        user_id=1,
        payee_identifier=syndicate_upi,
        amount=35000.0,
        for_family=False
    )
    payment_id = init_res["payment_id"]
    assert init_res["status"] == "held"

    # Step 2: Son Rahul receives WhatsApp alert and taps BLOCK
    block_res = TwoKeyGuardService.evaluate_check_b(
        db=db,
        payment_id=payment_id,
        action="BLOCK",
        reviewer_phone="+919876543211",
        reason="Son intervened: digital arrest imposter"
    )
    assert block_res["action"] == "BLOCKED"
    assert block_res["payment_status"] == "blocked"
    print(f"  • Son Rahul BLOCKED transaction. Response: {block_res['message']}")

    # Step 3: Verify entity is now in global threat blocklist
    flagged = db.query(FlaggedEntity).filter(
        FlaggedEntity.entity_value == syndicate_upi
    ).first()
    assert flagged is not None, "Payee should be in flagged_entities table"
    assert flagged.risk_score == 1.0
    print(f"  • Threat Intelligence verified: '{syndicate_upi}' blacklisted with score {flagged.risk_score}")

    # Step 4: COMMUNITY IMMUNITY: Another elderly user attempts to pay the same syndicate UPI
    second_attempt = TwoKeyGuardService.initiate_payment(
        db=db,
        user_id=1,
        payee_identifier=syndicate_upi,
        amount=500.0,  # Even small amount!
        for_family=False
    )
    print(f"  • Second User Attempt: Status = {second_attempt['status']} | Risk Score = {second_attempt['risk_score']}")
    print(f"  • Reasons: {second_attempt['reasons']}")

    assert second_attempt["status"] == "held"
    assert second_attempt["risk_score"] == 1.0
    assert any("blacklisted" in r.lower() or "cybercrime" in r.lower() for r in second_attempt["reasons"])
    print("  [PASS] Community Immunity active: Rahul's single block protected all future users!")


def test_stt_voice_note_transcription():
    print("\n[Test 6: Speech-to-Text (STT) Audio Transcription]")
    # Create a test audio note with sidecar
    test_dir = Path("app/static")
    test_dir.mkdir(parents=True, exist_ok=True)
    test_audio = test_dir / "voice_scam_test.ogg"
    test_audio.write_bytes(b"MOCK_OGG_HEADER_DATA_12345")
    sidecar = test_dir / "voice_scam_test.ogg.txt"
    sidecar.write_text("Hello Amma CBI police warrant is against you send 50000 now", encoding="utf-8")

    stt_result = transcribe_voice_note(str(test_audio))
    print(f"  • Transcribed Text: '{stt_result['text']}'")
    print(f"  • Detected Language: {stt_result['language']} | Source: {stt_result.get('source')}")

    assert "police" in stt_result["text"].lower() or "warrant" in stt_result["text"].lower()
    print("  [PASS] Voice note speech-to-text successfully transcribed.")


if __name__ == "__main__":
    init_db()
    db = SessionLocal()
    test_whitelisted_payee_fastpath(db)
    test_unverified_high_risk_held(db)
    test_check_a_lockout_policy(db)
    test_check_a_success_unlocks_check_b(db)
    test_check_b_block_and_community_immunity(db)
    test_stt_voice_note_transcription()
    db.close()
    print("\n" + "=" * 70)
    print(" [OK] ALL 6 TWO-KEY GUARD & STT TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 70 + "\n")
