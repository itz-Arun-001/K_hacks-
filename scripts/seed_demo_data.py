"""
SafeLoop Demo Database Seeder
Owned by: Person 4 (Arun)

Sets up a complete demo persona for testing:
1. User: Amma (+919876543210)
2. Primary Family Contact: Rahul (Son, +919876543211, code: 'anandham')
3. Secondary Family Contact: Priya (Daughter, +919876543212)
4. Trusted Payees Whitelist: TNEB, Milkman Anand, Apollo Pharmacy
5. 20 Historical Payments: To calculate normal spending baseline (avg ~₹550)
6. Known Threat Entities: kbc.claim@upi, cbi.investigation@upi
"""

import os
import sys
from datetime import datetime, timedelta
import random

# Ensure root folder is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    import bcrypt
except ImportError:
    bcrypt = None

from app.database import (
    init_db,
    SessionLocal,
    User,
    FamilyContact,
    TrustedPayee,
    Payment,
    FlaggedEntity,
    Event
)


def hash_secret(secret: str) -> str:
    """Hashes a secret code using bcrypt."""
    if bcrypt:
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(secret.encode("utf-8"), salt).decode("utf-8")
    else:
        # Fallback simulation if bcrypt not yet installed
        import hashlib
        return hashlib.sha256(secret.encode("utf-8")).hexdigest()


def seed_database():
    print("\n" + "=" * 65)
    print(" SAFELOOP DEMO DATABASE SEEDER (PERSON 4: ARUN)")
    print("=" * 65)

    init_db()
    db = SessionLocal()

    try:
        # ----------------------------------------------------------------------
        # 1. Create or Retrieve Elderly User (Amma)
        # ----------------------------------------------------------------------
        amma_phone = "+919876543210"
        user = db.query(User).filter(User.phone_number == amma_phone).first()

        if not user:
            user = User(
                phone_number=amma_phone,
                name="Amma (Lakshmi Raman)",
                language_pref="ta",  # Tamil preferred
                consent_given=True,
                onboarded_at=datetime.utcnow() - timedelta(days=60)
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"[+] Created User: {user.name} ({user.phone_number}) [ID: {user.id}]")
        else:
            print(f"[*] Found Existing User: {user.name} [ID: {user.id}]")

        # ----------------------------------------------------------------------
        # 2. Add Family Contacts (Check A & Check B)
        # ----------------------------------------------------------------------
        contacts = [
            {
                "name": "Rahul (Son)",
                "phone": "+919876543211",
                "relation": "son",
                "priority": 1,
                "code": "anandham"  # Secret family passphrase
            },
            {
                "name": "Priya (Daughter)",
                "phone": "+919876543212",
                "relation": "daughter",
                "priority": 2,
                "code": "anandham"
            }
        ]

        for c in contacts:
            existing = db.query(FamilyContact).filter(
                FamilyContact.user_id == user.id,
                FamilyContact.contact_phone == c["phone"]
            ).first()

            if not existing:
                fc = FamilyContact(
                    user_id=user.id,
                    contact_name=c["name"],
                    contact_phone=c["phone"],
                    relation=c["relation"],
                    priority=c["priority"],
                    family_code_hash=hash_secret(c["code"]),
                    created_at=datetime.utcnow() - timedelta(days=60)
                )
                db.add(fc)
                print(f"[+] Added Family Contact: {c['name']} (Priority {c['priority']}, Secret Code: '{c['code']}')")

        # ----------------------------------------------------------------------
        # 3. Add Trusted Payees (Whitelist - Zero Friction)
        # ----------------------------------------------------------------------
        trusted_list = [
            {"id": "tneb.bill@upi", "nick": "TNEB Electricity", "cat": "utility"},
            {"id": "anand.milk@upi", "nick": "Milkman Anand", "cat": "shop"},
            {"id": "apollo.pharmacy@upi", "nick": "Apollo Pharmacy", "cat": "medical"},
            {"id": "saravana.groceries@upi", "nick": "Saravana Stores Grocery", "cat": "shop"}
        ]

        for t in trusted_list:
            existing = db.query(TrustedPayee).filter(
                TrustedPayee.user_id == user.id,
                TrustedPayee.payee_identifier == t["id"]
            ).first()

            if not existing:
                tp = TrustedPayee(
                    user_id=user.id,
                    payee_identifier=t["id"],
                    nickname=t["nick"],
                    category=t["cat"],
                    added_at=datetime.utcnow() - timedelta(days=45)
                )
                db.add(tp)
                print(f"[+] Whitelisted Payee: {t['nick']} ({t['id']})")

        # ----------------------------------------------------------------------
        # 4. Add Historical Normal Payments (to establish Spending Baseline)
        # ----------------------------------------------------------------------
        existing_payments_count = db.query(Payment).filter(Payment.user_id == user.id).count()
        if existing_payments_count < 10:
            print("[+] Seeding 20 historical transactions to train user baseline...")
            normal_payees = ["anand.milk@upi", "tneb.bill@upi", "apollo.pharmacy@upi", "saravana.groceries@upi"]
            for i in range(20):
                days_ago = random.randint(1, 40)
                amount = round(random.uniform(150.0, 950.0), 2)
                p = Payment(
                    user_id=user.id,
                    payee_identifier=random.choice(normal_payees),
                    amount=amount,
                    for_family=False,
                    status="allowed",
                    risk_score=0.05,
                    created_at=datetime.utcnow() - timedelta(days=days_ago)
                )
                db.add(p)

        # ----------------------------------------------------------------------
        # 5. Add Global Threat Intelligence Entities (Mule & Scam Blocklist)
        # ----------------------------------------------------------------------
        known_threats = [
            {"type": "upi", "val": "kbc.claim@upi", "reason": "KBC Lottery Advance Fee Scam", "src": "user_report"},
            {"type": "upi", "val": "cbi.investigation@upi", "reason": "Digital Arrest Extortion Scheme", "src": "mule_graph"},
            {"type": "phone", "val": "9876543210", "reason": "Electricity cut-off phishing caller", "src": "user_report"},
            {"type": "upi", "val": "inspector.sharma@upi", "reason": "Police impersonator mule ring", "src": "family_block"}
        ]

        for threat in known_threats:
            existing = db.query(FlaggedEntity).filter(FlaggedEntity.entity_value == threat["val"]).first()
            if not existing:
                fe = FlaggedEntity(
                    entity_type=threat["type"],
                    entity_value=threat["val"],
                    source=threat["src"],
                    risk_score=0.98,
                    reason=threat["reason"]
                )
                db.add(fe)
                print(f"[+] Added Known Threat to Blocklist: {threat['val']} ({threat['reason']})")

        db.commit()
        print("\n[OK] Demo database seeded successfully into 'safeloop.db'!")
        print("=" * 65 + "\n")

    except Exception as e:
        db.rollback()
        print(f"[!] Error seeding database: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

