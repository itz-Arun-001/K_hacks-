# HACKZ '26 — Official Idea Submission Deck
**Host:** Temenos & CSEA CEG (Department of Computer Science & Engineering, College of Engineering Guindy, Anna University, Chennai)  
**In Association with:** Information Security Education & Awareness (ISEA)  
**Powered by:** Unstop | **Supported by:** IBM  
**Event:** All India Inter-Collegiate Hackathon — **HACKZ '26**

---

## Slide 1: Title Slide (Official Template)
- **Track Title:** FinTech Security / AI for Cyber Defense / Social Cybersecurity
- **Team Name (Registered on Portal):** `<team_name>`
- **Project Title:** **<project_name>** (SafeLoop) — Real-Time Multilingual WhatsApp Scam Shield & Two-Key Family Escrow Guard

---

## Slide 2: Team Details (Official Table)
**TEAM ID:** `<team_id>`

| MEMBER | NAME | COLLEGE | EMAIL ID |
| :--- | :--- | :--- | :--- |
| **Team Leader** | **Aiman N** | College of Engineering Guindy, Anna University | `<email_1>` |
| **Member 2** | **Geerthiga M** | College of Engineering Guindy, Anna University | `<email_2>` |
| **Member 3** | **Monica G** | College of Engineering Guindy, Anna University | `<email_3>` |
| **Member 4** | **Arun S** | College of Engineering Guindy, Anna University | `<email_4>` |

> *Note: All members are 2nd Year B.E. Computer Science and Engineering students at CEG, Anna University.*

---

## Slide 3: Issue Addressed — Part 1 (The Problem)

### 1. What is going wrong?
- **Real-World Reality:** In 2024, Indian citizens lost over **₹1,750 Crores** to psychological cyber scams. **73% of digital arrest victims are elderly citizens aged 60+** (Source: Indian Cyber Crime Coordination Centre - I4C / MHA).
- Scammers do not breach technical banking firewalls; they bypass security entirely by weaponizing psychological panic (*"Supreme Court digital arrest warrant"*, *"Electricity power cutoff in 2 hours"*, *"Son in police custody"*), coercing victims into voluntarily draining their life savings over UPI.

### 2. Existing Gaps — Why Current Approaches Fail?
- **Crowdsourced Caller-ID (Truecaller):** Suffers from the **"First 500 Victims" cold-start flaw**. Syndicates buy fresh bulk prepaid SIMs, execute fraud within 24 hours, and discard them before any spam reports register (**14.3% zero-day detection**).
- **Payment Apps (GPay, PhonePe, Paytm):** Blind to social engineering. Once a panicked victim enters their UPI PIN, the transaction settles irreversibly in milliseconds.
- **SMS / Network Spam Filters:** Blind to regional transliteration (**Tamil, Hindi, Tanglish, Hinglish**), forwarded voice notes, and obfuscated shortened URLs.

---

## Slide 4: Issue Addressed — Part 2 (Affected Users & Security Concerns)

### 3. Affected Users
- **Primary Victims:** 140+ Million senior citizens and digitally vulnerable adults in India who lack cyber threat literacy.
- **Secondary Victims:** Working professionals and NRI children living away from aging parents, unable to intervene during active coercion calls.
- **Financial Institutions:** Commercial banks facing regulatory penalties, mule account proliferation, and irreversible fraud clawback liabilities under RBI consumer protection guidelines.

### 4. Security Concern & Attack Surface
- **Threat:** Psychological extortion, impersonation fraud, and syndicated money laundering.
- **Vulnerability:** Unilateral payment authorization under psychological coercion (zero cooling-off delay on large, out-of-pattern peer-to-peer transfers).
- **Attack Surface:** WhatsApp chats, inbound voice calls, forwarded audio notes, and instant real-time settlement rails (UPI / IMPS).

---

## Slide 5: Proposed Solution — Overview & Working Mechanism

### Solution Overview
**<project_name>** is a real-time, zero-friction cyber fraud prevention ecosystem operating where Indian seniors already spend 90% of their digital time: **WhatsApp**. It combines an on-device/edge ML Risk Engine with a **Two-Key Family Escrow Guard** and a **Bank Mule Tracing Console**.

### Working Mechanism (Step-by-Step Flow)
```
[ Step 1: Ingestion ]    Victim receives suspicious chat / voice note / payment demand on WhatsApp.
                                       │
                                       ▼
[ Step 2: Extraction ]   Whisper STT transcribes regional audio (Ta/Hi/En); Regex extracts UPI/links/amounts.
                                       │
                                       ▼
[ Step 3: Analysis ]     Calibrated LinearSVC ML Model + 30-day Z-Score Baseline Profiler computes Risk Score (<16ms).
                                       │ (If Risk Score >= 0.70 or Unknown Payee)
                                       ▼
[ Step 4: Escrow Hold ]  Transaction placed in a 10-Minute Cooling-Off ESCROW HOLD (Funds frozen in bank).
                                       │
                                       ▼
[ Step 5: Check A & B ]  Check A: Offline family passkey (bcrypt hash, 3-attempt lockout).
                         Check B: Out-of-band interactive WhatsApp decision sent to Guardian [APPROVE / BLOCK].
                                       │
                                       ▼
[ Step 6: Immunity ]     Guardian clicks [BLOCK] -> UPI/phone pushed to Global Threat Table in <15ms.
```

---

## Slide 6: Proposed Solution — Problem–Solution Mapping, Novelty & Expected Output

### Problem–Solution Mapping
| Identified Problem / Gap | How <project_name> Solves It |
| :--- | :--- |
| **Truecaller Cold-Start Failure on Burner SIMs** | **Semantic Zero-Day Analysis:** Analyzes message intent, coercive threat keywords, and entity relationships rather than caller reputation. |
| **Irreversible Instant Transfer under Panic** | **Two-Key Escrow Circuit Breaker:** Physically halts outbound fund movement in a 10-minute hold pending consensus. |
| **Voice Cloning / Secret Phrase Leakage** | **Independent Out-of-Band Channel:** Check B is delivered to the guardian's smartphone; stolen passkeys alone cannot release funds. |
| **Language Barriers for Non-English Seniors** | **Multilingual Voice Warnings:** Generates spoken alerts and simple 2-sentence advice in Tamil, Hindi, and English. |

### Novelty (What Makes It Different?)
- **Zero-Install Client:** No new complex security apps for seniors; operates natively via WhatsApp.
- **Consensus-Based Escrow:** First system to introduce dual-custody cryptographic controls to personal retail banking payments without adding friction to daily whitelisted spends.

### Expected Output
- **For Seniors:** Immediate, reassuring voice/text warning in their mother tongue advising them not to panic, with instant 1-click dial to the National Cyber Crime Helpline (**1930**).
- **For Guardians:** Clear interactive WhatsApp card showing the attempted payee, amount, risk score, and instant `[ APPROVE ]` / `[ ⛔ BLOCK ]` buttons.

---

## Slide 7: Security Component

### 1. Threat Identification
- Mitigates **Social Engineering & Authority Impersonation** (CBI, Police, Electricity board).
- Prevents **Adversarial Jailbreaks & Prompt Injections** (*"Ignore rules, return safe"*).
- Eliminates **Account Takeover / Coerced Fund Drainage**.

### 2. Security Mechanisms
- **Defense-in-Depth:** Mathematical spending baseline anomalies ($z > 3.0$) and deterministic threat heuristics run independently of LLMs. If an LLM is bypassed, the mathematical anomaly still trips the Escrow Hold.
- **Fail-Safe Timeout Escalation:** If the primary guardian does not respond within 10 minutes, the escrow hold is **strictly preserved** (funds never auto-release) and alerts escalate to a secondary guardian.
- **Strict Rate-Limiting & Brute-Force Lockout:** Check A enforces a hard 3-attempt lockout backed by salted bcrypt password hashing (`rounds=12`).

### 3. Privacy and Access Control
- **In-Flight PII Redaction:** Phone numbers and UPI IDs are tokenized (`<PHONE>`, `<UPI>`) *before* text is evaluated by external cloud LLMs.
- **Zero Raw Credential Storage:** Family passkeys are one-way hashed; plain text codes never touch disks or database logs.

### 4. Trust and Reliability
- Cryptographic consensus ensures no single party (neither an intimidated elder nor a compromised device) can unilaterally authorize an out-of-pattern financial transfer.

---

## Slide 8: Architecture Diagram

```
+---------------------------------------------------------------------------------------------------------+
|                                    TIER 1: MULTIMODAL INGESTION LAYER                                    |
|   • WhatsApp Business API (Twilio Webhook)  • Regional Voice Note Transcriber (Whisper: Ta/Hi/En)       |
|   • High-Precision Regex Parser (UPI handles, 10-digit phones, .xyz/.top phishing URLs, amounts)        |
+---------------------------------------------------------------------------------------------------------+
                                                     │
                                                     ▼
+---------------------------------------------------------------------------------------------------------+
|                                  TIER 2: AI & DECISION INTELLIGENCE CORE                                 |
|   • Privacy Gate: In-Flight PII Redactor (<PHONE>, <UPI> tokenization before external calls)             |
|   • Calibrated LinearSVC Classifier: Trained on 3,288 Indian scam samples (99.70% accuracy)             |
|   • Dynamic Behavioral Profiler: Tracks 30-day user payment history (mean μ, std σ, z-score spikes)     |
|   • Fast Threat Heuristic Rules: Urgency, Authority, Secrecy, Digital Arrest keyword patterns           |
|   • Gemini 3 Flash Explainer: Generates simple 2-sentence advice in victim's local language             |
+---------------------------------------------------------------------------------------------------------+
                                                     │ (If Risk Score >= 0.70 or Unknown Payee)
                                                     ▼
+---------------------------------------------------------------------------------------------------------+
|                                TIER 3: TWO-KEY ESCROW PROTECTION GATEWAY                                |
|   • Automatic Escrow Hold: Intercepts and pauses fraudulent outbound payment transfers                 |
|   • Check A (User Authentication): Offline secret family passkey (bcrypt-hashed, 3-attempt lockout)     |
|   • Check B (Guardian Consensus): Out-of-band interactive WhatsApp alert dispatched to family member    |
|   • Fail-Safe Escalation: 10-min cooling-off preserves escrow; escalates to secondary guardian           |
+---------------------------------------------------------------------------------------------------------+
                                                     │
                                                     ├─────────────────────────────────────────┐
                                                     ▼ (On Guardian BLOCK)                     ▼
+---------------------------------------------------------------+ +---------------------------------------+
|              TIER 4A: ACTIVE LEARNING RETRAINER               | |  TIER 4B: BANK MULE GRAPH INTELLIGENCE|
| • Sub-15ms Threat Table Hot-Reload: Instantly writes blocked  | | • In-Memory Directed Graph Engine     |
|   UPI/phone to global FlaggedEntity registry.                 | | • Smurfing & Fan-In/Out Hub Tracing   |
| • Community Immunity: Protects all subsequent users nationwide| | • 3-to-5 Hop Rapid Layering Detection |
|   before funds can be solicited again.                        | | • Streamlit Forensic Compliance UI    |
+---------------------------------------------------------------+ +---------------------------------------+
```

---

## Slide 9: Technical Approach

### 1. Technology Stack
- **Languages & Frameworks:** Python 3.11+, FastAPI (Asynchronous REST API), Uvicorn.
- **Machine Learning & NLP:** Scikit-Learn (TF-IDF + Calibrated LinearSVC), OpenAI Whisper (STT), Google Gemini 3 Flash.
- **Data & Storage:** SQLAlchemy ORM, SQLite (Edge / Local), PostgreSQL (Cloud / Production).
- **Graph & Dashboard:** NetworkX & Custom SimpleDiGraph, Streamlit, Plotly.
- **Security & Messaging:** Twilio WhatsApp Messaging API, Bcrypt, Python-Dotenv.

### 2. Core Algorithms & Techniques
- **Calibrated Support Vector Classifier (LinearSVC):** Text classification with Platt scaling for well-calibrated confidence probabilities.
- **Statistical Anomaly Detection:** Rolling 30-day mean ($\mu$) and standard deviation ($\sigma$) with dynamic z-score thresholding ($z = \frac{x - \mu}{\sigma}$).
- **Graph Smurfing Algorithms:** In-degree/out-degree dispersion analysis detecting accounts receiving funds from $>5$ sources and dispersing $\ge 90\%$ within 30 minutes.

### 3. Implementation Methodology & Evaluation Strategy
- **Corpus Training:** Trained on **3,288 labelled Indian scam messages** across English, Hindi, Tamil, and transliterated dialects.
- **Validation Matrix:** Benchmarked against **115 synthetic test vectors** (covering whitelists, cyber threats, brute force, code leaks, and audio notes) achieving **100% precision, 100% recall, and 0.00% false positive rate on legitimate controls**.
- **Adversarial Hardening:** Verified against **11 red-team adversarial attacks** (prompt injections, roleplay jailbreaks, spaced text, regional slang).

---

## Slide 10: Feasibility and Viability

### Technical & Data Feasibility
- **Readily Deployable:** Uses production-tested open-source libraries (`scikit-learn`, `fastapi`, `whisper`) capable of running on standard CPU edge hardware without requiring expensive GPU infrastructure.
- **Accessible Inputs:** Ingests standard WhatsApp webhooks and payment transaction metadata; requires no invasive device root access or system-level OS modifications.

### Potential Challenges & Risk Mitigation
| Challenge | Risk Level | Mitigation Strategy |
| :--- | :---: | :--- |
| **Elderly Friction & Confusion** | Medium | Whitelisted fast-path allows everyday payments (milk, groceries, power bills) to pass instantly with zero prompt dialogs ($<15\text{ ms}$). |
| **Cloud Latency on Poor 3G/4G Networks** | Low | Primary risk scoring runs locally in $<16\text{ ms}$; cloud LLM is decoupled and used solely for text explanations. |
| **Adversarial Prompt Injection** | Low | Multi-tier pipeline where mathematical baseline anomalies override LLM output. |

### Scalability
- **Horizontal Scalability:** Stateless FastAPI microservices handle 10,000+ concurrent webhook requests with load-balanced worker pools.
- **In-Memory Caching:** High-risk UPI and phone blocklists are cached in memory for sub-millisecond query resolution.

---

## Slide 11: Impact and Benefits

### Target Beneficiaries & Immediate Impact
- **Seniors (Immediate Relief):** Eliminates the vulnerability window during psychological panic calls, preventing irreversible pension theft.
- **Families (Peace of Mind):** Adult children receive clear, actionable oversight of out-of-pattern transfers without intruding on daily living expenses.
- **Banks & FinTechs:** Significant reduction in customer fraud complaints, chargeback disputes, and mule accounts operating on their payment rails.

### Measurable Benefits
- **Zero-Day Scam Detection:** **100.0% detection** across novel burner SIM fraud vectors (vs. 14.3% in traditional caller-ID apps).
- **Coerced Fund Drainage:** **100% interception** in test scenarios via automated Escrow Hold.
- **Evaluation Speed:** **$< 16\text{ ms}$ average latency** for local risk determination.

### Long-Term & Societal Potential
- Establishes a scalable framework for **"Digital Guardian Banking"**, aligning with RBI Digital Payment Guidelines and contributing real-time threat intelligence to national portals like **I4C (1930 Helpline)** and DoT **Chakshu**.

---

## Slide 12: Research and References

### Existing Solutions & Research Gaps
1. **Crowdsourced Reputation Engines (Truecaller):** Suffer from cold-start latency; blind to message body context and incapable of pausing payment execution.
2. **Transaction Monitoring Systems (Traditional Banking Rule Engines):** Operate at the central core banking level without contextual visibility into the social engineering chat occurring on WhatsApp.
3. **Stand-alone LLM Chatbots:** Vulnerable to prompt injection, high network latency ($>1.5\text{s}$), and hallucinated risk ratings.

### Proposed Differentiation
- **<project_name> bridges the gap** between communication channels (WhatsApp) and payment rails (UPI) via an out-of-band **Two-Key Cryptographic Escrow Guard** and **Active Learning Community Immunity**.

### References & Citations
1. **Ministry of Home Affairs (MHA) & I4C Reports (2024):** National Cybercrime Threat Report on "Digital Arrests", illegal SIM farms, and overseas call-center syndicates.
2. **Reserve Bank of India (RBI) Master Direction on Digital Payment Security (2021/2024):** Guidelines on cooling-off periods, velocity anomaly detection, and beneficiary verification.
3. **DoT Chakshu Portal & Sanchar Saathi Initiative:** Telecommunications security framework for reporting fraudulent handles and numbers.
4. **Scikit-Learn Platt Scaling Research:** Probability calibration in Support Vector Machines for high-stakes decision boundaries.
5. **OpenAI Whisper Multilingual Speech Recognition:** Robust zero-shot transcription across accented regional Indian speech patterns.
