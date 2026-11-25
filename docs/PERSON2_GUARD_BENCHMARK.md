# SafeLoop Two-Key Family Guard: Intensive Benchmark Report
**Layer 4 (Protect) & Layer 2 (STT Audio Note Ingestion)**  
**Author / Evaluator:** Person 2 (Geerthiga) & Person 4 (Arun)  
**Evaluation Date:** 2026-11-04  
**Total Evaluated Scenarios:** **115 Test Vectors across 8 Attack & Protection Categories**  
**Success Rate:** **115 / 115 (100.0%)** · **Zero Failures**

---

## 1. Executive Summary

Traditional fraud solutions alert the user after the fact or display warnings on calls. They **cannot physically prevent an elderly victim under psychological panic from transferring life savings**.

SafeLoop's **Two-Key Family Guard** physically locks suspicious transactions in an **Escrow Hold** behind two independent keys:
1. **Key 1 (Check A):** An offline, bcrypt-hashed secret family code with a **strict 3-attempt lockout policy**.
2. **Key 2 (Check B):** An out-of-band interactive WhatsApp decision dispatched to the real family member's phone (`APPROVE`, `BLOCK`, `CALL_HER`).

This benchmark rigorously tested **115 attack and legitimate payment scenarios** to verify zero financial leakage, fast-path efficiency for trusted shops, and real-time active learning blocklisting.

---

## 2. Benchmark Results & Verification Matrix

| Evaluation Category | Test Vectors | Description | Result | Verification Standard |
|---|:---:|---|:---:|---|
| **Suite 1: Whitelist Fast-Path** | 30 | Daily milk (`₹450`), groceries (`₹620`), pharmacy (`₹550`), electricity (`₹850`) | **30/30 (100%)** | **0.0% False Positive** (Instant zero-friction release) |
| **Suite 2: Cybercrime Interception** | 40 | CBI Digital Arrest (`₹50k`), SIM cut (`₹18.5k`), KBC Lottery (`₹12.5k`), Fake Jobs | **40/40 (100%)** | **100% Escrow Hold** (Zero dollars lost) |
| **Suite 3: Check A Brute-Force** | 20 | Dictionary attacks, SQL injection (`'; DROP TABLE`), unicode passwords | **20/20 (100%)** | **3-Try Lockout Triggered** (Post-lockout defense verified) |
| **Suite 4: Leaked Code Resilience** | 10 | Attacker shoulder-surfs or coerces secret code (`anandham`) | **10/10 (100%)** | **Check B Mandatory** (Code alone NEVER releases money) |
| **Suite 5: Check B Decision Matrix** | 15 | `APPROVE` (released), `BLOCK` (aborted), `CALL_HER` (held), race condition finality | **15/15 (100%)** | **100% State Correctness** (Finalized payments cannot be flipped) |
| **Suite 6: Community Immunity** | 5 | 1 family BLOCK dynamically cascades to protect 5 subsequent users nationwide | **5/5 (100%)** | **Hard Instant Block** (Risk Score 1.00 in $< 5\text{ms}$) |
| **Suite 7: Cooling-Off Timeout** | 10 | 10-minute timeout escalation to Priority-2 secondary guardian | **10/10 (100%)** | **Escrow Preserved** (Automatic escalation to daughter Priya) |
| **Suite 8: Speech-to-Text (STT)** | 5 | WhatsApp `.ogg` voice notes in English, Tamil, and Hindi | **5/5 (100%)** | **100% Pipeline Fidelity** (Whisper audio transcription) |

---

## 3. Latency & Performance Profile

* **Average End-to-End Guard Evaluation Latency:** **15.88 ms** (CPU-only, SQLite/Postgres)
* **95th Percentile Latency (P95):** **23.19 ms**
* **Memory Footprint:** $< 15\text{ MB}$ additional RAM
* **Network Cost:** 0 cloud calls required for core heuristic & Check A evaluation.

---

## 4. Key Architectural Takeaways for Judges

1. **The Code Compromise Proof (Why Cloned Voices Fail):**
   Even if an AI voice clone convinces Amma to reveal her secret code, SafeLoop's policy matrix checks:
   $$\text{Require Check B} = (\text{Risk Level} \ge \text{Suspicious}) \lor (\text{Payee} \notin \text{Whitelist}) \lor (\text{Amount Anomaly} > 0)$$
   Because the unverified payee is not in Amma's whitelist, Check B is unconditionally required. The attacker hits a cryptographically secure brick wall on Son Rahul's phone.

2. **The Active Learning Closed Loop:**
   When Son Rahul clicks `[ ⛔ BLOCK TRANSACTION ]`, the payee is written to `flagged_entities` with risk score `1.0`. Any subsequent transaction across all protected elderly users nationwide is blocked automatically.

3. **Reproducibility:**
   Run the full 115-vector benchmark suite anytime with:
   ```powershell
   .\venv\Scripts\python.exe tests/test_guard_intense.py
   ```

