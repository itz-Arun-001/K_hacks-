"""
SafeLoop 3,000+ Extensive Dataset Generator
Author: Person 4 (Arun) - Core ML & Threat Intelligence Architect

Generates 3,200+ distinct, realistic samples representing Indian cyber fraud vectors
(English, Tanglish, Hinglish, regional variations, zero-day links, and clean transactions)
with full entity metadata (amounts, upi_ids, phones, links).
"""

import json
import random
import os
from pathlib import Path

random.seed(42)

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_FILE = BASE_DIR / "data" / "large_dataset_3000.json"

# ==============================================================================
# VOCABULARY & TEMPLATE COMPONENTS
# ==============================================================================

CITIES = ["Chennai", "Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Kolkata", "Pune", "Coimbatore", "Madurai", "Trichy"]
OFFICERS = ["DCP Sharma", "Inspector Rathore", "Officer Kumar", "Superintendent Verma", "Inspector Vijay", "Officer Murugan", "CBI Director Gupta"]
RELATIVES_EN = ["son Rahul", "son Karthik", "nephew Suresh", "daughter Priya", "friend Anand", "cousin Vignesh"]
RELATIVES_TA = ["Amma", "Paati", "Appa", "Thatha"]
RELATIVES_HI = ["Mummy", "Papa", "Dadi", "Bhaiya"]

SCAM_UPI_HANDLES = ["police.desk", "cbi.settlement", "trai.clearance", "eb.officer", "court.bail", "task.finance", "kbc.tax", "lottery.hr", "fast.loan", "refund.dept"]
SCAM_DOMAINS = ["sbi-yono.xyz", "tneb-bill.cc", "incometax-refund.top", "kyc-verify.info", "court-warrant.club", "police-clearance.xyz", "eb-payment.online"]
SHORTENERS = ["https://bit.ly/", "https://tinyurl.com/", "https://t.co/", "https://is.gd/"]

CLEAN_FOOD = ["tomato rasam", "filter coffee", "sambar sadham", "idli sambar", "curd rice", "masala dosa", "paneer butter masala", "roti and dal"]
DOCTORS = ["Dr. Ramanathan", "Dr. Meenakshi", "Dr. Swaminathan", "Dr. Shalini", "Dr. Venkatesh", "Dr. Arvind"]
HOSPITALS = ["Apollo Hospital", "Kauvery Hospital", "Fortis Hospital", "MIOT International", "SIMS Hospital"]
COURIERS = ["Blue Dart", "DTDC Express", "India Post", "Delhivery", "Amazon Transport"]
WHITELISTED_PAYEES = ["anand.milk@upi", "tneb.bill@upi", "apollo.pharmacy@upi", "saravana.groceries@upi", "newspaper.vendor@upi"]

samples = []
sample_id = 1

# ==============================================================================
# 1. SCAM GENERATORS (~1,600 SAMPLES)
# ==============================================================================

# 1.1 Digital Arrest & Law Enforcement Coercion (~350 samples)
for i in range(350):
    city = random.choice(CITIES)
    officer = random.choice(OFFICERS)
    amount = random.choice([25000, 35000, 50000, 75000, 95000, 120000, 150000, 250000])
    phone = f"98{random.randint(10000000, 99999999)}"
    upi = f"{random.choice(SCAM_UPI_HANDLES)}{random.randint(10,99)}@{random.choice(['sbi', 'okaxis', 'paytm', 'icici'])}"
    
    templates = [
        f"URGENT NOTICE FROM CBI: A digital arrest warrant has been issued against your Aadhaar in {city} for money laundering FIR #{random.randint(100,999)}. Do not disconnect. Transfer ₹{amount:,} security deposit to {upi} within 15 minutes.",
        f"Supreme Court Order: Non-bailable arrest warrant issued against you by Cyber Crime {city}. Contact {officer} at {phone} immediately or transfer ₹{amount:,} bail bond to {upi}.",
        f"Narcotics Control Bureau (NCB) notice: 140 grams MDMA seized at {city} airport cargo addressed to your phone number. You are placed under digital arrest. Stay on video call or transfer ₹{amount:,} clearance fee to {upi}.",
        f"Telecom Regulatory Authority (TRAI) Warning: Your mobile number will be permanently disconnected within 2 hours for cyber extortion. Call {officer} on {phone} immediately to cancel police arrest.",
        f"Enforcement Directorate (ED) summons: Your bank account is linked to ₹14 Crore hawala racket. Transfer ₹{amount:,} verification balance to RBI holding account {upi} to avoid immediate arrest.",
        f"Mumbai Customs Alert: Contraband parcel detained under your Aadhaar. Video surveillance active. To verify identity, transfer ₹{amount:,} to court escrow {upi} urgently."
    ]
    text = random.choice(templates)
    samples.append({
        "id": f"SCAM_DA_{sample_id:04d}",
        "text": text,
        "category": "scam",
        "expected_level": "high",
        "scam_type": "digital_arrest",
        "entities": {
            "links": [],
            "phones": [phone] if phone in text else [],
            "upi_ids": [upi] if upi in text else [],
            "amounts": [amount] if f"₹{amount:,}" in text else []
        }
    })
    sample_id += 1

# 1.2 Urgent Utility & Service Disconnection (~300 samples)
for i in range(300):
    amount = random.choice([1450, 2180, 2850, 3450, 4200, 5600])
    phone = f"97{random.randint(10000000, 99999999)}"
    short = f"{random.choice(SHORTENERS)}eb-{random.randint(1000,9999)}"
    dom = f"https://{random.choice(SCAM_DOMAINS)}"
    link = random.choice([short, dom])
    
    templates = [
        f"Dear Consumer, your electricity power will be disconnected tonight at 9:30 PM by EB officer because previous month bill was not updated. Pay ₹{amount:,} immediately at {link} or call {phone}.",
        f"Electricity Bill Overdue: Power supply to your meter #04-201-{random.randint(100,999)} will be cut off in 2 hours. Kindly settle ₹{amount:,} via {link} to avoid penalty.",
        f"Bharat Gas Alert: Your LPG cylinder subsidy cancelled and gas connection will be blocked tonight. Settle outstanding ₹{amount:,} now at {link}",
        f"Urgent Water Supply Notice: Pipeline connection will be terminated today by municipal board. Pay pending bill ₹{amount:,} immediately at {link} or call officer {phone}.",
        f"TNEB Power Cut Alert: Dear user, your electricity line scheduled for disconnection tonight at 8:00 PM. Call electricity officer immediately at {phone} or pay ₹{amount:,} at {link}"
    ]
    text = random.choice(templates)
    samples.append({
        "id": f"SCAM_UT_{sample_id:04d}",
        "text": text,
        "category": "scam",
        "expected_level": "high",
        "scam_type": "utility_disconnection",
        "entities": {
            "links": [link],
            "phones": [phone] if phone in text else [],
            "upi_ids": [],
            "amounts": [amount]
        }
    })
    sample_id += 1

# 1.3 Relative in Distress / Hospital / Dialect Scams (~350 samples)
for i in range(350):
    amount = random.choice([8000, 15000, 22000, 35000, 45000, 60000])
    phone = f"94{random.randint(10000000, 99999999)}"
    upi = f"emergency.{random.randint(100,999)}@{random.choice(['okaxis', 'paytm', 'ybl'])}"
    
    # Mix of English, Tanglish, Hinglish
    dialect_type = random.choice(["tanglish", "hinglish", "english"])
    if dialect_type == "tanglish":
        rel = random.choice(["Amma", "Paati"])
        text = random.choice([
            f"{rel}, idhu Rahul. Phone tholanjipochu, friends phn la irundhu anupren. Urgent-ah ₹{amount:,} GPay pannu indha UPI-ku: {upi}. Hospital bill kattanum seekiram pannu.",
            f"{rel}, accident aaiduchu bike la near Anna Nagar. Police station la iruken, case cancel panna ₹{amount:,} kekaaranga. Urgent-ah indha UPI-ku {upi} anupu. Appa kita sollatha.",
            f"{rel}, en friend hospitalized, ICU la irukan. Doctor injection poda ₹{amount:,} kekuranga. Please seekiram indha number-ku {upi} GPay pannunga."
        ])
    elif dialect_type == "hinglish":
        rel = random.choice(["Mummy", "Dadi"])
        text = random.choice([
            f"{rel} jaldi ₹{amount:,} bhejo police station me fasa hu case cancel karwana hai upi: {upi} emergency hai mat batana kisi ko.",
            f"{rel}, mera phone kho gaya tha. Yeh friend ka phone hai. Mera accident ho gaya hai doctor ₹{amount:,} mang raha hai. Jaldi GPay karo {upi} par.",
            f"{rel}, friend hospital me admit hai, urgent blood arrange karna hai. ₹{amount:,} transfer karo turant is UPI par: {upi}."
        ])
    else:
        rel = random.choice(RELATIVES_EN)
        text = random.choice([
            f"Amma, I had a severe bike accident on GST road. Admitted in emergency. Transfer ₹{amount:,} immediately to doctor's desk {upi} or surgery will be delayed.",
            f"Emergency Alert: Your {rel} is detained in police station after road incident. Send ₹{amount:,} compromise fine to inspector upi: {upi} within 30 minutes to release without FIR.",
            f"Amma, my wallet and phone were stolen in train. I am stranded without money. Send ₹{amount:,} to station vendor upi: {upi} urgently so I can reach home."
        ])
        
    samples.append({
        "id": f"SCAM_REL_{sample_id:04d}",
        "text": text,
        "category": "scam",
        "expected_level": "high",
        "scam_type": "relative_in_trouble",
        "entities": {
            "links": [],
            "phones": [],
            "upi_ids": [upi],
            "amounts": [amount]
        }
    })
    sample_id += 1

# 1.4 Fake Work-from-Home, YouTube Tasks & Fake Loans (~300 samples)
for i in range(300):
    daily = random.choice([2500, 3500, 4800, 6000, 8500])
    fee = random.choice([800, 1200, 1850, 2500, 3500])
    loan_amt = random.choice([200000, 500000, 1000000])
    short = f"{random.choice(SHORTENERS)}job-{random.randint(100,999)}"
    upi = f"task.finance{random.randint(10,99)}@paytm"
    
    templates = [
        f"Part-time Job Offer! Earn ₹{daily:,} daily just by liking YouTube videos and rating hotels on Google Maps. No experience needed. Pay refundable registration fee of ₹{fee:,} to {upi} to activate ID.",
        f"Telegram Work from Home: Daily payout ₹{daily:,}. Complete simple rating tasks on {short}. To unlock VIP task tier, deposit ₹{fee:,} security fee to {upi}.",
        f"Pre-Approved Loan Alert: Your personal loan of ₹{loan_amt:,} is approved at 2.5% interest without collateral. Pay processing documentation charge ₹{fee:,} to {upi} to disburse money within 1 hour.",
        f"Amazon Part-Time Hiring: Work 1 hour from phone, earn ₹{daily:,} per day. Registration closing today. Register at {short} or pay activation fee ₹{fee:,} via UPI: {upi}",
        f"Crypto Wealth Program: Guaranteed 300% return in 7 days. Invest ₹{fee:,} and get daily ₹{daily:,} payout directly to bank. Join now at {short}"
    ]
    text = random.choice(templates)
    samples.append({
        "id": f"SCAM_JOB_{sample_id:04d}",
        "text": text,
        "category": "scam",
        "expected_level": "high",
        "scam_type": "fake_jobs_and_loans",
        "entities": {
            "links": [short] if short in text else [],
            "phones": [],
            "upi_ids": [upi] if upi in text else [],
            "amounts": [fee]
        }
    })
    sample_id += 1

# 1.5 Banking Phishing, KYC & KBC Lottery (~300 samples)
for i in range(300):
    prize = random.choice(["25 Lakh", "50 Lakh", "1 Crore", "Tata Safari"])
    tax = random.choice([6500, 9500, 12500, 18500, 24000])
    refund = random.choice([18450, 24800, 32150, 48900])
    short = f"{random.choice(SHORTENERS)}kyc-{random.randint(100,999)}"
    dom = f"https://{random.choice(SCAM_DOMAINS)}"
    link = random.choice([short, dom])
    upi = f"claim.tax{random.randint(10,99)}@sbi"
    
    templates = [
        f"Dear customer, your State Bank account will be blocked within 24 hours due to expired KYC. Update your PAN card and Aadhaar immediately at {link} to avoid freeze.",
        f"Income Tax Refund Approved: ₹{refund:,} has been credited for your refund application. To release funds to your bank account, verify bank details at {link}",
        f"Congratulations! Your mobile number won {prize} in KBC Jio Lucky Draw. To claim your lottery cheque, deposit government clearance tax ₹{tax:,} to {upi} immediately.",
        f"HDFC NetBanking Alert: Your access has been suspended due to unusual login. Reactivate your netbanking password immediately at {link} within 2 hours.",
        f"SBI Yono Notice: Your netbanking card is locked. Click {link} to update KYC and prevent permanent account cancellation.",
        f"Reward Points Expiring: Your ICICI credit card reward points worth ₹{tax:,} expire tonight! Redeem cash directly to your bank account at {link}"
    ]
    text = random.choice(templates)
    samples.append({
        "id": f"SCAM_PHISH_{sample_id:04d}",
        "text": text,
        "category": "scam",
        "expected_level": "high",
        "scam_type": "phishing_kyc",
        "entities": {
            "links": [link] if link in text else [],
            "phones": [],
            "upi_ids": [upi] if upi in text else [],
            "amounts": [tax] if f"₹{tax:,}" in text else ([refund] if f"₹{refund:,}" in text else [])
        }
    })
    sample_id += 1

# ==============================================================================
# 2. LEGITIMATE / CLEAN GENERATORS (~1,600 SAMPLES)
# ==============================================================================

# 2.1 Family & Social Chats (~450 samples)
for i in range(450):
    rel = random.choice(["Amma", "Paati", "Akka", "Maami", "Chithi", "Anni", "Appa"])
    food = random.choice(CLEAN_FOOD)
    city = random.choice(CITIES)
    
    templates = [
        f"{rel}, did you have lunch? I made {food} today. It came out very well, will bring some in the evening.",
        f"{rel}, when are you reaching {city}? Let me know your train coach number so I can come to the railway station to pick you up.",
        f"Happy birthday {rel}! Wishing you a healthy and blessed year ahead. We will all visit your home this Sunday.",
        f"{rel}, please remember to take your blood pressure medicine after breakfast. Rahul told me you forgot yesterday.",
        f"{rel}, how is Thatha feeling today? Did the knee pain subside? Doctor told to walk 15 minutes in the garden.",
        f"Please send me the recipe for {food} when you get time. Kids are asking for it today.",
        f"Good morning {rel}! Hope you slept well. Today weather is very pleasant in {city}.",
        f"{rel}, the electrician came and repaired the bedroom fan. Everything is working fine now."
    ]
    text = random.choice(templates)
    samples.append({
        "id": f"GEN_FAM_{sample_id:04d}",
        "text": text,
        "category": "genuine",
        "expected_level": "safe",
        "scam_type": "none",
        "entities": {"links": [], "phones": [], "upi_ids": [], "amounts": []}
    })
    sample_id += 1

# 2.2 Legitimate Bank SMS Alerts (Debit / ATM / Salary - No Links/UPIs) (~400 samples)
for i in range(400):
    amt = random.choice([200, 450, 750, 1200, 2000, 3500, 5000, 8500, 12000])
    acc = random.randint(1000, 9999)
    bal = random.randint(25000, 185000)
    bank = random.choice(["SBI", "HDFC Bank", "ICICI Bank", "Axis Bank", "Canara Bank", "Bank of Baroda"])
    
    templates = [
        f"{bank}: ₹{amt:,.2f} withdrawn from ATM card ending {acc} on 01-Nov-26. Avl Bal: ₹{bal:,.2f}.",
        f"Your A/c ending {acc} debited by ₹{amt:,.2f} on 01-Nov-26 towards POS purchase at Reliance Fresh. Avl Bal: ₹{bal:,.2f}.",
        f"Salary of ₹{amt*10:,.2f} credited to your A/c ending {acc} on 01-Nov-26 by EPFO/Employer. Total Bal: ₹{bal:,.2f}.",
        f"{bank} Alert: ₹{amt:,.2f} debited from account {acc} for annual locker maintenance fee. Clear balance: ₹{bal:,.2f}.",
        f"Dear Customer, scheduled maintenance on our netbanking portal will take place on Sunday 02:00 AM to 05:00 AM. Services will resume normally."
    ]
    text = random.choice(templates)
    samples.append({
        "id": f"GEN_BANK_{sample_id:04d}",
        "text": text,
        "category": "genuine",
        "expected_level": "safe",
        "scam_type": "none",
        "entities": {
            "links": [],
            "phones": [],
            "upi_ids": [],
            "amounts": [amt]
        }
    })
    sample_id += 1

# 2.3 Legitimate Official Utility & Scheduled Shutdown Notices (~300 samples)
for i in range(300):
    amt = random.choice([380, 540, 680, 820, 1150, 1420])
    consumer = f"04-201-002-{random.randint(100,999)}"
    official_domain = random.choice(["https://www.tnebnet.org", "https://tneb.tn.gov.in", "https://www.bescom.co.in", "https://billdesk.com"])
    
    templates = [
        f"TNEB: Bill for Consumer {consumer} for ₹{amt:,} is generated. Due date 18-Nov-2026. Pay safely via official portal {official_domain}",
        f"TNEB Power Shutdown: Scheduled maintenance power shutdown in Anna Nagar area on Tuesday from 9:00 AM to 2:00 PM. Inconvenience regretted.",
        f"Airtel Thanks: Your broadband bill of ₹{amt:,} for account #490218 is generated. Auto-debit will execute on due date.",
        f"Indane Gas: Your refill cylinder booking #849102 is confirmed. Delivery agent will arrive within 2 business days. Cash on delivery ₹850.",
        f"Your LIC policy #8493021 premium of ₹{amt*3:,} is due on 15-Nov-2026. Pay online at licindia.in or at nearest branch."
    ]
    text = random.choice(templates)
    samples.append({
        "id": f"GEN_UTIL_{sample_id:04d}",
        "text": text,
        "category": "genuine",
        "expected_level": "safe",
        "scam_type": "none",
        "entities": {
            "links": [official_domain] if official_domain in text else [],
            "phones": [],
            "upi_ids": [],
            "amounts": [amt]
        }
    })
    sample_id += 1

# 2.4 Legitimate Healthcare, Hospital Appointments & Deliveries (~450 samples)
for i in range(450):
    doc = random.choice(DOCTORS)
    hosp = random.choice(HOSPITALS)
    courier = random.choice(COURIERS)
    whitelisted = random.choice(WHITELISTED_PAYEES)
    amt = random.choice([350, 450, 600, 750, 900])
    
    templates = [
        f"{hosp}: Your consultation with {doc} is confirmed for tomorrow at 10:30 AM. Please arrive 15 minutes early at reception counter 3.",
        f"Apollo Pharmacy: Your monthly prescription medicine order #84910 is dispatched and will be delivered by 4:00 PM today.",
        f"{courier}: Courier shipment with AWB 849201849 from Chennai is out for delivery with our delivery executive. Please keep OTP ready.",
        f"Swiggy Instamart: Your order of fresh vegetables and milk has been delivered. Thank you for shopping with us.",
        f"Amma, milk bill for this week is ₹{amt:,}. Please transfer to {whitelisted} when you are free.",
        f"Saravana Stores: Thank you for shopping with us! Bill amount ₹{amt*2:,}. 50 reward points credited to your loyalty card."
    ]
    text = random.choice(templates)
    samples.append({
        "id": f"GEN_SVC_{sample_id:04d}",
        "text": text,
        "category": "genuine",
        "expected_level": "safe",
        "scam_type": "none",
        "entities": {
            "links": [],
            "phones": [],
            "upi_ids": [whitelisted] if whitelisted in text else [],
            "amounts": [amt] if f"₹{amt:,}" in text else []
        }
    })
    sample_id += 1

# Shuffle entire dataset
random.shuffle(samples)

# Assign 80% Train / 20% Held-Out Test split
train_cutoff = int(len(samples) * 0.8)
for idx, s in enumerate(samples):
    s["split"] = "train" if idx < train_cutoff else "test"

# Summary metrics
scams_count = sum(1 for s in samples if s["category"] == "scam")
clean_count = sum(1 for s in samples if s["category"] == "genuine")
train_count = sum(1 for s in samples if s["split"] == "train")
test_count = sum(1 for s in samples if s["split"] == "test")

print(f"[+] Total Samples Generated: {len(samples)}")
print(f"    • Scam / Threat Samples: {scams_count} ({scams_count/len(samples)*100:.1f}%)")
print(f"    • Clean / Genuine Samples: {clean_count} ({clean_count/len(samples)*100:.1f}%)")
print(f"    • Train Split: {train_count} (80%)")
print(f"    • Held-Out Test Split: {test_count} (20%)")

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(samples, f, indent=2, ensure_ascii=False)

print(f"[OK] Large-Scale Dataset saved to: {OUTPUT_FILE}")

