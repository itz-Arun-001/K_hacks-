# 🛡️ Team SafeLoop: Developer Handbook & Git Workflow

Welcome to **Team SafeLoop**! This document explains how our repository is structured, which branch you own, how to run and test your code locally, and how to safely commit and push your work to GitHub without causing merge conflicts.

---

## 📌 Repository Quick Reference

- **GitHub Repository:** [https://github.com/itz-Arun-001/K_hacks-](https://github.com/itz-Arun-001/K_hacks-)
- **Default Protected Branch:** `main` (Nobody commits directly to `main`!)
- **Team Branches:**
  - `p1-bot` (Aiman)
  - `p2-guard` (Geerthiga)
  - `p3-graph` (Monica)
  - `p4-engine` (Arun)

---

## 💻 1. First-Time Setup (Run Once on Your Machine)

Open VS Code / Terminal on your laptop and execute:

```bash
# 1. Clone the repository
git clone https://github.com/itz-Arun-001/K_hacks-.git
cd K_hacks-

# 2. Create and activate your virtual environment
python -m venv venv

# On Windows (PowerShell):
.\venv\Scripts\activate
# On Mac / Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create your local .env configuration file
cp .env.example .env
```

---

## 🔀 2. Daily Git Commands & Workflow

### The Golden Rule:

> **Never work directly on `main`.** You will work on your dedicated branch, push your changes to your remote branch, and create a Pull Request (PR) for Arun to review and merge into `main`.

### Daily Workflow Cheat Sheet:

```bash
# 1. Before starting work, switch to YOUR branch and pull the latest changes:
git checkout <your-branch-name>
git pull origin <your-branch-name>

# 2. Write and test your code locally...

# 3. Check what files you modified:
git status

# 4. Stage your modified files:
git add .

# 5. Commit with a meaningful message:
git commit -m "feat: implement initial entity extractor for UPI and phone"

# 6. Push changes to YOUR remote branch on GitHub:
git push origin <your-branch-name>
```

### When Your Feature is Complete & Tested:

1. Open [https://github.com/itz-Arun-001/K_hacks-](https://github.com/itz-Arun-001/K_hacks-)
2. You will see a banner: **`"<your-branch> had recent pushes"`** $\rightarrow$ Click **"Compare & pull request"**.
3. Set base to `main` and compare to `<your-branch>`.
4. Click **Create pull request**.
5. Arun reviews the code, checks for any conflicts, and merges it into `main`!

---

## 👤 Person 1: Aiman (Bot, NLP & Message AI)

- **Goal:** WhatsApp bot receives any text/link/UPI/phone, extracts facts, asks Gemini LLM for scam tactics, gets a risk score from Arun's engine, and replies in English, Tamil, or Hindi.
- **Your Branch:** **`p1-bot`**
- **Access your branch:**
  ```bash
  git checkout p1-bot
  git pull origin p1-bot
  ```

### Files You Own:

- `app/api/webhook.py` (Twilio WhatsApp Webhook endpoint)
- `app/services/extractor.py` (Regex entity extractor)
- `app/services/llm_analyzer.py` (Gemini API scam intent & tactics parser)
- `app/services/translator.py` (Multilingual template replies in EN, TA, HI)

### Step-by-Step Flow:

1. **(Hello-World)**:
   - Join the Twilio WhatsApp Sandbox from two phones.
   - Start your FastAPI server (`uvicorn app.main:app --reload --port 8000`) and run `ngrok http 8000`.
   - In `app/api/webhook.py`, write a simple bot that echoes back whatever message you send it.
   - In `app/services/llm_analyzer.py`, write a small test script calling Gemini API with a sample scam text.
2. **(Core Extraction & Analysis)**:
   - In `app/services/extractor.py`, write regex functions to extract:
     - UPI IDs (`[\w\.\-]+@[\w]+`)
     - Indian phone numbers (10 digits)
     - Links/URLs and Money amounts (₹50,000, 50000, Rs. 500).
   - Connect to Arun's engine: Call `evaluate_risk(text=text, entities=extracted, scam_tags=llm_tags)`.
3. **(Multilingual Replies & Chakshu)**:
   - In `app/services/translator.py`, write clean responses for Safe, Suspicious, and High Risk in Tamil, Hindi, and English.
   - In High Risk replies, include Chakshu (reporting) and 1930 helpline pointers.

---

## 👤 Person 2: Geerthiga (Voice, Payment Guard & Family Loop)

- **Goal:** Whisper converts WhatsApp voice notes to text; the Two-Key guard holds risky payments, checks the secret family code (Check A), and sends real-time approval requests to the son's phone (Check B).
- **Your Branch:** **`p2-guard`**
- **Access your branch:**
  ```bash
  git checkout p2-guard
  git pull origin p2-guard
  ```

### Files You Own:

- `app/services/stt.py` (Whisper speech-to-text handler for WhatsApp `.ogg` audio)
- `app/services/guard.py` (Two-Key Guard state machine: Hold $\rightarrow$ Check A $\rightarrow$ Check B)
- `app/api/risk.py` (Mock payment API & screen)

### Step-by-Step Flow:

1. **(Hello-World)**:
   - In `app/services/stt.py`, test Whisper transcribing a sample `.ogg` voice note to text.
   - Write `hash_family_code(code)` and `verify_family_code(code, hash)` using `bcrypt`.
2. **(Registration Flow)**:
   - Create a registration flow that saves Amma's phone, son's phone, and the hashed family code into the `family_contacts` database table.
   - Feed transcribed voice notes from `stt.py` into Aiman's message pipeline.
3. **(Two-Key Guard & Holds)**:
   - In `app/services/guard.py`:
     - If payee is in `trusted_payees` table $\rightarrow$ `status: "allowed"` (no friction).
     - If new or unverified $\rightarrow$ `status: "held"`.
   - **Check A**: If payment is for a relative, prompt for the family code (3-try lockout).
   - **Check B**: Send a WhatsApp alert to the son's phone via Twilio REST API:
     _"Amma is trying to pay ₹X to Y. Reply APPROVE, BLOCK, or CALL HER"_.
   - If son replies `APPROVE` $\rightarrow$ payment released. If `BLOCK` $\rightarrow$ payment blocked and added to global blocklist.

---

## 👤 Person 3: Monica (Mule Graph & Bank Console)

- **Goal:** Generate 500 synthetic accounts with planted mule rings; build NetworkX graph detectors; build the Streamlit Bank Console.
- **Your Branch:** **`p3-graph`**
- **Access your branch:**
  ```bash
  git checkout p3-graph
  git pull origin p3-graph
  ```

### Files You Own:

- `scripts/generate_mules.py` (Faker synthetic transaction generator)
- `app/services/graph.py` (NetworkX graph algorithms: fan-in/fan-out, cycles, 3-5 hop chains)
- `dashboard/app.py` (Interactive Streamlit Bank Console)

### Step-by-Step Flow:

1. **(Hello-World)**:
   - In `scripts/generate_mules.py`, write a script using `Faker` to generate ~500 fake Indian bank accounts and normal transactions.
   - Load them into a `networkx.DiGraph` and print node/edge statistics.
2. **(Planted Rings & Detectors)**:
   - Plant fraud rings in the synthetic dataset:
     - Fan-in / Fan-out: 10 accounts send money to 1 hub, which quickly disperses it to 5 cash-out accounts.
     - 3–5 hop chains and cycles.
     - Plant `kbc.claim@upi` inside one of the rings!
   - Plant innocent lookalikes: A busy tea shop (many small payments in, no fast transfers out) and a landlord (monthly rent).
   - In `app/services/graph.py`, write detectors to identify high-velocity pass-through accounts and write flagged accounts into Arun's `flagged_entities` table.
3. **(Streamlit Bank Console)**:
   - In `dashboard/app.py`, run `streamlit run dashboard/app.py`.
   - Show metric cards: Total Transactions, Flagged Mule Accounts, Active Rings.
   - Render an interactive graph: normal accounts in grey, flagged mule rings in **red**.
   - Click an account to display: _"Why flagged: 95% pass-through within 3 minutes; part of Ring #4."_

---

## 👤 Person 4: Arun (Core Engine, ML & Integration)

- **Your Branch:** **`p4-engine`**
- **Access your branch:**
  ```bash
  git checkout p4-engine
  git pull origin p4-engine
  ```
- **Tasks:**
  - User Baseline anomaly profiler (`app/services/baseline.py`).
  - Seed demo script (`scripts/seed_demo_data.py`).
  - Expand the labelled test set (`data/labelled_messages.json`).
  - Review and merge PRs from Aiman, Geerthiga, and Monica into `main`.

---

## ⚠️ Important Rules to Avoid Merge Conflicts

1. **Only edit your assigned files**: If Person 1 needs database changes, ask Arun to update `app/database.py` rather than editing it yourself.
2. **Sync with `main` frequently**:
   ```bash
   git fetch origin
   git merge origin/main
   ```
3. **Never commit `.env` or sensitive API keys**: Always keep your secrets in your local `.env`.
