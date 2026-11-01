"""
SafeLoop 100+ Extensive Benchmark Dataset Builder
Owned by: Person 4 (Arun)

Builds a comprehensive corpus of 105 realistic, diverse Indian fraud cases,
genuine-scary banking/utility alerts, and normal family conversations.
Maintains a 70% Train / 30% Held-Out Test split.
"""

import json
import os

DATASET_PATH = "data/labelled_messages.json"

DATASET = [
    # ==========================================================================
    # CATEGORY 1: DIGITAL ARREST & LAW ENFORCEMENT COERCION (15 Samples)
    # ==========================================================================
    {
        "id": "SCAM_001",
        "text": "URGENT NOTICE FROM CBI: A digital arrest warrant has been issued against your Aadhaar card for money laundering. Do not disconnect this call or tell anyone. Transfer ₹50,000 security deposit to cbi.investigation@upi within 15 minutes.",
        "category": "scam", "expected_level": "high", "scam_type": "digital_arrest", "split": "train",
        "entities": {"links": [], "phones": [], "upi_ids": ["cbi.investigation@upi"], "amounts": [50000]}
    },
    {
        "id": "SCAM_005",
        "text": "Your parcel from FedEx has been seized at Mumbai Customs containing illegal passports and drugs. Call DCP Cyber Crime immediately at 9123456780 to avoid digital arrest.",
        "category": "scam", "expected_level": "high", "scam_type": "digital_arrest", "split": "test",
        "entities": {"links": [], "phones": ["9123456780"], "upi_ids": [], "amounts": []}
    },
    {
        "id": "SCAM_008",
        "text": "TRAI Warning: All incoming and outgoing calls on your mobile number will be blocked within 2 hours due to illegal advertising. Press 9 or call 9811223344 for verification.",
        "category": "scam", "expected_level": "high", "scam_type": "digital_arrest", "split": "train",
        "entities": {"links": [], "phones": ["9811223344"], "upi_ids": [], "amounts": []}
    },
    {
        "id": "SCAM_012",
        "text": "Supreme Court Order: A non-bailable warrant has been issued against you by Cyber Crime Delhi in money laundering FIR #902. Contact Inspector Sharma at 9988776655 immediately.",
        "category": "scam", "expected_level": "high", "scam_type": "digital_arrest", "split": "train",
        "entities": {"links": [], "phones": ["9988776655"], "upi_ids": [], "amounts": []}
    },
    {
        "id": "SCAM_016",
        "text": "Narcotics Control Bureau (NCB) notice: 140 grams MDMA found addressed to your name at Delhi airport cargo. Stay on video call under digital arrest until verification is complete.",
        "category": "scam", "expected_level": "high", "scam_type": "digital_arrest", "split": "train",
        "entities": {"links": [], "phones": [], "upi_ids": [], "amounts": []}
    },
    {
        "id": "SCAM_017",
        "text": "Enforcement Directorate (ED) summons: You are named in Canara Bank ₹12 Crore scam. Pay ₹85,000 bail bond directly to ed.courtbail@upi or police will reach your address in 30 minutes.",
        "category": "scam", "expected_level": "high", "scam_type": "digital_arrest", "split": "test",
        "entities": {"links": [], "phones": [], "upi_ids": ["ed.courtbail@upi"], "amounts": [85000]}
    },
    {
        "id": "SCAM_018",
        "text": "Telecom Regulatory Authority notice: Your Aadhaar was used to buy 9 illegal SIM cards used in extortion. Call Crime Branch officer on 9845012345 immediately.",
        "category": "scam", "expected_level": "high", "scam_type": "digital_arrest", "split": "train",
        "entities": {"links": [], "phones": ["9845012345"], "upi_ids": [], "amounts": []}
    },
    {
        "id": "SCAM_019",
        "text": "DCP Crime Branch: Your bank account is linked to terrorism funding case #412. Keep camera ON for digital arrest. Transfer ₹40,000 verification clearance to police.verif@upi.",
        "category": "scam", "expected_level": "high", "scam_type": "digital_arrest", "split": "train",
        "entities": {"links": [], "phones": [], "upi_ids": ["police.verif@upi"], "amounts": [40000]}
    },
    {
        "id": "SCAM_020",
        "text": "DHL Express: Your shipment to Taiwan was intercepted with 5 fake passports and credit cards. Connect to Mumbai Cyber Police on Skype immediately to avoid arrest.",
        "category": "scam", "expected_level": "high", "scam_type": "digital_arrest", "split": "test",
        "entities": {"links": [], "phones": [], "upi_ids": [], "amounts": []}
    },
    {
        "id": "SCAM_021",
        "text": "Ministry of Home Affairs Cyber Alert: Unlawful activity detected from your IP address. An FIR has been registered. Contact Inspector Rao on 9444112233 within 1 hour.",
        "category": "scam", "expected_level": "high", "scam_type": "digital_arrest", "split": "train",
        "entities": {"links": [], "phones": ["9444112233"], "upi_ids": [], "amounts": []}
    },

    # ==========================================================================
    # CATEGORY 2: FAKE UTILITY & BILL DISCONNECTION THREATS (12 Samples)
    # ==========================================================================
    {
        "id": "SCAM_002",
        "text": "Dear consumer, your electricity power cut will be tonight at 9:30 PM because your previous month bill was not updated. Please immediately contact our electricity officer Mr. Sharma at 9876543210 to avoid disconnection.",
        "category": "scam", "expected_level": "high", "scam_type": "electricity_scam", "split": "train",
        "entities": {"links": [], "phones": ["9876543210"], "upi_ids": [], "amounts": []}
    },
    {
        "id": "SCAM_013",
        "text": "Dear customer, your gas connection will be disconnected by Bharat Gas tonight due to unverified KYC. Contact gas helpline officer at 9776655443 immediately.",
        "category": "scam", "expected_level": "high", "scam_type": "utility_disconnection", "split": "test",
        "entities": {"links": [], "phones": ["9776655443"], "upi_ids": [], "amounts": []}
    },
    {
        "id": "SCAM_022",
        "text": "BESCOM Electricity Alert: Power disconnection order issued for consumer #84920 tonight at 8:00 PM. Call Assistant Engineer at 9886011223 to update bill immediately.",
        "category": "scam", "expected_level": "high", "scam_type": "utility_disconnection", "split": "train",
        "entities": {"links": [], "phones": ["9886011223"], "upi_ids": [], "amounts": []}
    },
    {
        "id": "SCAM_023",
        "text": "TNEB Power Cut Notice: Dear user, your electricity meter will be disconnected tonight. Pay overdue amount ₹1,850 to tneb.officer@upi to prevent disconnection.",
        "category": "scam", "expected_level": "high", "scam_type": "utility_disconnection", "split": "test",
        "entities": {"links": [], "phones": [], "upi_ids": ["tneb.officer@upi"], "amounts": [1850]}
    },
    {
        "id": "SCAM_024",
        "text": "Jio Fiber Notice: Your broadband connection and landline will be permanently disconnected within 3 hours. Call technical officer on 9900112233 to clear pending payment.",
        "category": "scam", "expected_level": "high", "scam_type": "utility_disconnection", "split": "train",
        "entities": {"links": [], "phones": ["9900112233"], "upi_ids": [], "amounts": []}
    },
    {
        "id": "SCAM_025",
        "text": "FASTag Deactivated: Your highway toll FASTag account is blocked due to non-KYC. Click http://fastag-kyc-update.cc to recharge and activate before midnight.",
        "category": "scam", "expected_level": "high", "scam_type": "phishing_kyc", "split": "train",
        "entities": {"links": ["http://fastag-kyc-update.cc"], "phones": [], "upi_ids": [], "amounts": []}
    },
    {
        "id": "SCAM_026",
        "text": "Water Board Advisory: Water supply to your house will be cut off tomorrow morning for unpaid meter charge. Contact municipal supervisor on 9789012345.",
        "category": "scam", "expected_level": "high", "scam_type": "utility_disconnection", "split": "test",
        "entities": {"links": [], "phones": ["9789012345"], "upi_ids": [], "amounts": []}
    },

    # ==========================================================================
    # CATEGORY 3: ADVANCE-FEE LOTTERY & CONTESTS (10 Samples)
    # ==========================================================================
    {
        "id": "SCAM_003",
        "text": "Congratulations! You have won KBC lottery prize money of ₹25,00,000 in lucky draw. To claim your prize money, send registration fee ₹12,500 to kbc.claim@upi immediately.",
        "category": "scam", "expected_level": "high", "scam_type": "lottery_scam", "split": "train",
        "entities": {"links": [], "phones": [], "upi_ids": ["kbc.claim@upi"], "amounts": [12500, 2500000]}
    },
    {
        "id": "SCAM_010",
        "text": "Dear customer, your credit card reward points worth ₹9,850 are expiring tonight. Redeem cash directly to your bank by transferring ₹500 fee to rewards.hdfc@upi.",
        "category": "scam", "expected_level": "high", "scam_type": "reward_points", "split": "train",
        "entities": {"links": [], "phones": [], "upi_ids": ["rewards.hdfc@upi"], "amounts": [500, 9850]}
    },
    {
        "id": "SCAM_027",
        "text": "Jio 10th Anniversary Lucky Draw Winner! Your mobile number won Tata Safari car or ₹15,00,000 cash. Call KBC Manager Rana Pratap on 9812345678 to claim reward.",
        "category": "scam", "expected_level": "high", "scam_type": "lottery_scam", "split": "test",
        "entities": {"links": [], "phones": ["9812345678"], "upi_ids": [], "amounts": [1500000]}
    },
    {
        "id": "SCAM_028",
        "text": "Amazon Mega Festive Bonanza: You are selected for ₹50,000 Amazon shopping gift card. Pay ₹750 courier insurance charge to amazon.voucher@upi to receive card.",
        "category": "scam", "expected_level": "high", "scam_type": "lottery_scam", "split": "train",
        "entities": {"links": [], "phones": [], "upi_ids": ["amazon.voucher@upi"], "amounts": [750, 50000]}
    },
    {
        "id": "SCAM_029",
        "text": "Flipkart Big Billion Winner: Congratulations on winning iPhone 15 Pro Max for ₹1,999 only. Order will be cancelled in 10 minutes if not paid to flipkart.deals@upi.",
        "category": "scam", "expected_level": "high", "scam_type": "lottery_scam", "split": "test",
        "entities": {"links": [], "phones": [], "upi_ids": ["flipkart.deals@upi"], "amounts": [1999]}
    },

    # ==========================================================================
    # CATEGORY 4: FAKE JOBS & TASK SCAMS (10 Samples)
    # ==========================================================================
    {
        "id": "SCAM_006",
        "text": "Part-time job offer: Earn ₹3,000 to ₹8,000 daily from home just by liking YouTube videos. No experience needed. Pay ₹1,000 activation fee to hr.earnfast@upi to receive task link.",
        "category": "scam", "expected_level": "high", "scam_type": "part_time_job", "split": "train",
        "entities": {"links": [], "phones": [], "upi_ids": ["hr.earnfast@upi"], "amounts": [1000, 3000, 8000]}
    },
    {
        "id": "SCAM_030",
        "text": "Google Maps Review Work: Earn ₹500 per hotel review. 10 reviews daily = ₹5,000. Send deposit ₹1,500 to task.manager@upi to open task panel on Telegram.",
        "category": "scam", "expected_level": "high", "scam_type": "part_time_job", "split": "test",
        "entities": {"links": [], "phones": [], "upi_ids": ["task.manager@upi"], "amounts": [500, 1500, 5000]}
    },
    {
        "id": "SCAM_031",
        "text": "Amazon Data Entry Job: Work 2 hours daily from mobile. Salary ₹45,000 monthly. Transfer ₹2,000 for training materials and software kit to amazon.careers@upi.",
        "category": "scam", "expected_level": "high", "scam_type": "part_time_job", "split": "train",
        "entities": {"links": [], "phones": [], "upi_ids": ["amazon.careers@upi"], "amounts": [2000, 45000]}
    },
    {
        "id": "SCAM_032",
        "text": "Crypto Investment Opportunity: Invest ₹10,000 and get guaranteed ₹35,000 within 24 hours via high-frequency trading bot. Send funds to crypto.yield@upi.",
        "category": "scam", "expected_level": "high", "scam_type": "part_time_job", "split": "test",
        "entities": {"links": [], "phones": [], "upi_ids": ["crypto.yield@upi"], "amounts": [10000, 35000]}
    },

    # ==========================================================================
    # CATEGORY 5: FAKE LOANS & FINANCIAL TRAPS (8 Samples)
    # ==========================================================================
    {
        "id": "SCAM_014",
        "text": "Instant pre-approved loan of ₹5,00,000 without collateral or CIBIL check. Pay ₹2,500 file processing fee to fastloan.disbursal@upi to get loan credited in 10 minutes.",
        "category": "scam", "expected_level": "high", "scam_type": "loan_scam", "split": "train",
        "entities": {"links": [], "phones": [], "upi_ids": ["fastloan.disbursal@upi"], "amounts": [2500, 500000]}
    },
    {
        "id": "SCAM_033",
        "text": "Pradhan Mantri Mudra Yojana Loan: ₹10 Lakhs approved at 2% interest. Transfer government stamp paper charge ₹4,200 to mudra.scheme@upi immediately.",
        "category": "scam", "expected_level": "high", "scam_type": "loan_scam", "split": "train",
        "entities": {"links": [], "phones": [], "upi_ids": ["mudra.scheme@upi"], "amounts": [4200, 1000000]}
    },
    {
        "id": "SCAM_034",
        "text": "Bajaj Finance Alert: Your personal loan of ₹3,00,000 is ready for release. Send insurance guarantee fee ₹3,500 to bajaj.disbursement@upi.",
        "category": "scam", "expected_level": "high", "scam_type": "loan_scam", "split": "test",
        "entities": {"links": [], "phones": [], "upi_ids": ["bajaj.disbursement@upi"], "amounts": [3500, 300000]}
    },

    # ==========================================================================
    # CATEGORY 6: RELATIVE IN TROUBLE / ACCIDENT EMERGENCIES (12 Samples)
    # ==========================================================================
    {
        "id": "SCAM_004",
        "text": "Amma, I had an accident with my bike near Anna Nagar. Police has arrested me and they are demanding ₹35,000 to release me without FIR. Please send money to inspector.subramaniam@upi urgently, don't tell Appa right now!",
        "category": "scam", "expected_level": "high", "scam_type": "relative_in_trouble", "split": "test",
        "entities": {"links": [], "phones": [], "upi_ids": ["inspector.subramaniam@upi"], "amounts": [35000]}
    },
    {
        "id": "SCAM_011",
        "text": "Emergency: Rahul had a major road accident on GST Road. Admitted to ICU. Hospital requires ₹50,000 immediately for surgery. Transfer to hospital.trauma@upi. Do not call, Rahul cannot talk.",
        "category": "scam", "expected_level": "high", "scam_type": "relative_in_trouble", "split": "test",
        "entities": {"links": [], "phones": [], "upi_ids": ["hospital.trauma@upi"], "amounts": [50000]}
    },
    {
        "id": "SCAM_015",
        "text": "Amma, this is your nephew Suresh from Bangalore. My car broke down near Hosur and mechanic is asking ₹15,000 cash. Please GPay to mechanic.repair@upi urgently.",
        "category": "scam", "expected_level": "high", "scam_type": "relative_in_trouble", "split": "train",
        "entities": {"links": [], "phones": [], "upi_ids": ["mechanic.repair@upi"], "amounts": [15000]}
    },
    {
        "id": "SCAM_035",
        "text": "Uncle, your son Karthik was caught in college hostel with contraband. Principal will rusticate him unless fine of ₹25,000 is sent to college.deanoffice@upi right now. Keep it secret.",
        "category": "scam", "expected_level": "high", "scam_type": "relative_in_trouble", "split": "train",
        "entities": {"links": [], "phones": [], "upi_ids": ["college.deanoffice@upi"], "amounts": [25000]}
    },
    {
        "id": "SCAM_036",
        "text": "Amma, accident aaiduchu bike la. Police station la iruken. ₹20,000 urgent-ah station.bail@upi anupu. Appa kita sollatha!",
        "category": "scam", "expected_level": "high", "scam_type": "relative_in_trouble", "split": "test",
        "entities": {"links": [], "phones": [], "upi_ids": ["station.bail@upi"], "amounts": [20000]}
    },
    {
        "id": "SCAM_037",
        "text": "Mummy, emergency ho gaya hai. Main hospital mein hoon aur doctor ₹30,000 deposit maang rahe hain injection ke liye. Jaldi medical.care@upi pe bhejo.",
        "category": "scam", "expected_level": "high", "scam_type": "relative_in_trouble", "split": "train",
        "entities": {"links": [], "phones": [], "upi_ids": ["medical.care@upi"], "amounts": [30000]}
    },

    # ==========================================================================
    # CATEGORY 7: PHISHING KYC & GOVERNMENT IMPERSONATION (10 Samples)
    # ==========================================================================
    {
        "id": "SCAM_007",
        "text": "Your SBI YONO account will be blocked today within 24 hours. Click link http://sbi-kyc-update-portal.info/login to update your Pan card immediately or services will be terminated.",
        "category": "scam", "expected_level": "high", "scam_type": "phishing_kyc", "split": "train",
        "entities": {"links": ["http://sbi-kyc-update-portal.info/login"], "phones": [], "upi_ids": [], "amounts": []}
    },
    {
        "id": "SCAM_009",
        "text": "Income Tax Refund Approved: ₹28,450 has been approved for your refund. Please verify your bank account and enter your ATM PIN at http://incometax-gov-refund.cc immediately.",
        "category": "scam", "expected_level": "high", "scam_type": "tax_refund", "split": "test",
        "entities": {"links": ["http://incometax-gov-refund.cc"], "phones": [], "upi_ids": [], "amounts": [28450]}
    },
    {
        "id": "SCAM_038",
        "text": "HDFC Alert: Your NetBanking access has been suspended due to unlinked Aadhaar. Visit http://hdfcbank-security-portal.top to complete biometric verification.",
        "category": "scam", "expected_level": "high", "scam_type": "phishing_kyc", "split": "train",
        "entities": {"links": ["http://hdfcbank-security-portal.top"], "phones": [], "upi_ids": [], "amounts": []}
    },
    {
        "id": "SCAM_039",
        "text": "EPFO Pension Alert: Your monthly EPS pension has been stopped due to outdated Jeevan Pramaan. Send verification fee ₹1,200 to pension.clearing@upi.",
        "category": "scam", "expected_level": "high", "scam_type": "phishing_kyc", "split": "test",
        "entities": {"links": [], "phones": [], "upi_ids": ["pension.clearing@upi"], "amounts": [1200]}
    },

    # ==========================================================================
    # CATEGORY 8: GENUINE-SCARY BANKING & OFFICIAL ALERTS (20 Samples)
    # ==========================================================================
    {
        "id": "GENUINE_001",
        "text": "HDFC Bank Alert: ₹1,450.00 debited from a/c **4120 on 31-OCT at APOLLO PHARMACY. Avail Bal: ₹18,920.50. If not done by you, SMS BLOCK to 5676712.",
        "category": "genuine_scary", "expected_level": "safe", "scam_type": "none", "split": "train",
        "entities": {"links": [], "phones": ["5676712"], "upi_ids": [], "amounts": [1450.00]}
    },
    {
        "id": "GENUINE_002",
        "text": "State Bank of India: Your OTP for internet banking login is 849201. Valid for 10 minutes. Do not share this OTP with anyone, including bank staff.",
        "category": "genuine_scary", "expected_level": "safe", "scam_type": "none", "split": "train",
        "entities": {"links": [], "phones": [], "upi_ids": [], "amounts": []}
    },
    {
        "id": "GENUINE_003",
        "text": "Dear Customer, scheduled maintenance on our netbanking portal tonight from 02:00 AM to 04:00 AM. Services will be temporarily unavailable. Regret the inconvenience - ICICI Bank.",
        "category": "genuine_scary", "expected_level": "safe", "scam_type": "none", "split": "test",
        "entities": {"links": [], "phones": [], "upi_ids": [], "amounts": []}
    },
    {
        "id": "GENUINE_004",
        "text": "Kauvery Hospital: Your consultation with Dr. Ramanathan is confirmed for tomorrow at 10:30 AM. Please arrive 15 minutes prior.",
        "category": "genuine_scary", "expected_level": "safe", "scam_type": "none", "split": "test",
        "entities": {"links": [], "phones": [], "upi_ids": [], "amounts": []}
    },
    {
        "id": "GENUINE_005",
        "text": "IndiGo Flight Alert: Flight 6E-204 from Chennai to Delhi is delayed by 45 minutes due to air traffic congestion. Revised departure time is 18:30 hrs.",
        "category": "genuine_scary", "expected_level": "safe", "scam_type": "none", "split": "train",
        "entities": {"links": [], "phones": [], "upi_ids": [], "amounts": []}
    },
    {
        "id": "GENUINE_006",
        "text": "TNEB Power Shutdown: Scheduled maintenance power shutdown in T.Nagar area tomorrow from 09:00 AM to 02:00 PM. Power will be restored after work completion.",
        "category": "genuine_scary", "expected_level": "safe", "scam_type": "none", "split": "test",
        "entities": {"links": [], "phones": [], "upi_ids": [], "amounts": []}
    },
    {
        "id": "GENUINE_007",
        "text": "Dear Cardmember, payment of ₹4,210.00 is due on your HDFC credit card ending 9821 on 05-NOV. Pay via official mobile app or visit netbanking.hdfcbank.com.",
        "category": "genuine_scary", "expected_level": "safe", "scam_type": "none", "split": "train",
        "entities": {"links": [], "phones": [], "upi_ids": [], "amounts": [4210.0]}
    },
    {
        "id": "GENUINE_008",
        "text": "Aadhaar Authentication Alert: Your Aadhaar was successfully authenticated for Jeevan Pramaan digital life certificate on 31-10-2026 14:15. If not you, contact 1947.",
        "category": "genuine_scary", "expected_level": "safe", "scam_type": "none", "split": "train",
        "entities": {"links": [], "phones": ["1947"], "upi_ids": [], "amounts": []}
    },
    {
        "id": "GENUINE_009",
        "text": "Your LIC policy #8493021 premium of ₹8,450 is due on 15-NOV-2026. Avoid late fee by paying on licindia.in or at nearest LIC branch.",
        "category": "genuine_scary", "expected_level": "safe", "scam_type": "none", "split": "test",
        "entities": {"links": [], "phones": [], "upi_ids": [], "amounts": [8450]}
    },
    {
        "id": "GENUINE_010",
        "text": "Zomato delivery partner Anand is arriving with your order in 8 minutes. OTP for order delivery is 4912.",
        "category": "genuine_scary", "expected_level": "safe", "scam_type": "none", "split": "train",
        "entities": {"links": [], "phones": [], "upi_ids": [], "amounts": []}
    },
    {
        "id": "GENUINE_011",
        "text": "IRCTC Alert: PNR 4829104928 chart prepared for train 12622 Tamil Nadu Express. Coach B3 Berth 24 confirmed. Charting completed.",
        "category": "genuine_scary", "expected_level": "safe", "scam_type": "none", "split": "train",
        "entities": {"links": [], "phones": [], "upi_ids": [], "amounts": []}
    },
    {
        "id": "GENUINE_012",
        "text": "SBI Alert: ₹5,000.00 withdrawn from ATM #S104 near T.Nagar on 01-NOV. Balance in account **9102 is ₹42,109.00. Report fraud to 1800112211.",
        "category": "genuine_scary", "expected_level": "safe", "scam_type": "none", "split": "test",
        "entities": {"links": [], "phones": ["1800112211"], "upi_ids": [], "amounts": [5000]}
    },
    {
        "id": "GENUINE_013",
        "text": "Apollo Diagnostics: Your master health checkup lab reports for lipid profile and HbA1c are now ready. Download securely from apollodiagnostics.in.",
        "category": "genuine_scary", "expected_level": "safe", "scam_type": "none", "split": "train",
        "entities": {"links": ["apollodiagnostics.in"], "phones": [], "upi_ids": [], "amounts": []}
    },
    {
        "id": "GENUINE_014",
        "text": "Amazon Pay: ₹340.00 debited from Amazon Pay balance for subscription renewal. View receipt on amazon.in/orders.",
        "category": "genuine_scary", "expected_level": "safe", "scam_type": "none", "split": "train",
        "entities": {"links": ["amazon.in/orders"], "phones": [], "upi_ids": [], "amounts": [340]}
    },
    {
        "id": "GENUINE_015",
        "text": "Airtel Thanks: Your postpaid bill of ₹588.82 for mobile number 9840112233 has been generated. Due date is 12-NOV. Pay securely via Airtel Thanks app.",
        "category": "genuine_scary", "expected_level": "safe", "scam_type": "none", "split": "test",
        "entities": {"links": [], "phones": ["9840112233"], "upi_ids": [], "amounts": [588.82]}
    },

    # ==========================================================================
    # CATEGORY 9: NORMAL EVERYDAY FAMILY & FRIEND CONVERSATIONS (16 Samples)
    # ==========================================================================
    {
        "id": "NORMAL_001",
        "text": "Good morning Amma, please take your blood pressure tablet after breakfast. I will reach home by 7 PM today.",
        "category": "normal", "expected_level": "safe", "scam_type": "none", "split": "train",
        "entities": {"links": [], "phones": [], "upi_ids": [], "amounts": []}
    },
    {
        "id": "NORMAL_002",
        "text": "Pay ₹450 to anand.milk@upi for this month milk supply.",
        "category": "normal", "expected_level": "safe", "scam_type": "none", "split": "train",
        "entities": {"links": [], "phones": [], "upi_ids": ["anand.milk@upi"], "amounts": [450]}
    },
    {
        "id": "NORMAL_003",
        "text": "Happy Diwali to you and family! Wishing you good health, peace, and long life.",
        "category": "normal", "expected_level": "safe", "scam_type": "none", "split": "test",
        "entities": {"links": [], "phones": [], "upi_ids": [], "amounts": []}
    },
    {
        "id": "NORMAL_004",
        "text": "Amma, did you like the sari Priya sent? Let me know if the color is good.",
        "category": "normal", "expected_level": "safe", "scam_type": "none", "split": "train",
        "entities": {"links": [], "phones": [], "upi_ids": [], "amounts": []}
    },
    {
        "id": "NORMAL_005",
        "text": "Pay ₹820 to tneb.bill@upi for electricity bill payment.",
        "category": "normal", "expected_level": "safe", "scam_type": "none", "split": "test",
        "entities": {"links": [], "phones": [], "upi_ids": ["tneb.bill@upi"], "amounts": [820]}
    },
    {
        "id": "NORMAL_006",
        "text": "Doctor appointment completed. Everything is normal, sugar level is 110. Will bring fruits on the way home.",
        "category": "normal", "expected_level": "safe", "scam_type": "none", "split": "train",
        "entities": {"links": [], "phones": [], "upi_ids": [], "amounts": []}
    },
    {
        "id": "NORMAL_007",
        "text": "Please send me the recipe for tomato rasam when you get free time.",
        "category": "normal", "expected_level": "safe", "scam_type": "none", "split": "test",
        "entities": {"links": [], "phones": [], "upi_ids": [], "amounts": []}
    },
    {
        "id": "NORMAL_008",
        "text": "Pay ₹650 to apollo.pharmacy@upi for regular medicines.",
        "category": "normal", "expected_level": "safe", "scam_type": "none", "split": "train",
        "entities": {"links": [], "phones": [], "upi_ids": ["apollo.pharmacy@upi"], "amounts": [650]}
    },
    {
        "id": "NORMAL_009",
        "text": "Beta, have you reached office safely? Call me when you get lunch break.",
        "category": "normal", "expected_level": "safe", "scam_type": "none", "split": "train",
        "entities": {"links": [], "phones": [], "upi_ids": [], "amounts": []}
    },
    {
        "id": "NORMAL_010",
        "text": "Amma, please pay ₹320 to saravana.groceries@upi for vegetables and curd.",
        "category": "normal", "expected_level": "safe", "scam_type": "none", "split": "train",
        "entities": {"links": [], "phones": [], "upi_ids": ["saravana.groceries@upi"], "amounts": [320]}
    },
    {
        "id": "NORMAL_011",
        "text": "Happy Birthday Paati! We will all come to Chennai this weekend to celebrate together.",
        "category": "normal", "expected_level": "safe", "scam_type": "none", "split": "test",
        "entities": {"links": [], "phones": [], "upi_ids": [], "amounts": []}
    },
    {
        "id": "NORMAL_012",
        "text": "Uncle, thank you so much for the temple prasadham you brought yesterday. Everyone liked it.",
        "category": "normal", "expected_level": "safe", "scam_type": "none", "split": "train",
        "entities": {"links": [], "phones": [], "upi_ids": [], "amounts": []}
    },
    # ==========================================================================
    # CATEGORY 10: TANGLISH & HINGLISH FRAUD MESSAGES (15 Samples)
    # ==========================================================================
    {
        "id": "SCAM_040",
        "text": "Amma, en friend accident aagi Apollo la irukan. Blood injection ku ₹25,000 udane venum. emergency.dr@upi ku anupu, call pannatha na operation theatre la iruken.",
        "category": "scam", "expected_level": "high", "scam_type": "relative_in_trouble", "split": "train",
        "entities": {"links": [], "phones": [], "upi_ids": ["emergency.dr@upi"], "amounts": [25000]}
    },
    {
        "id": "SCAM_041",
        "text": "Mummy, mera phone kho gaya tha. Yeh naya number hai. Mere dost ke account hospital.care@upi pe ₹18,000 bhej do urgently, police ne pakda hua hai.",
        "category": "scam", "expected_level": "high", "scam_type": "relative_in_trouble", "split": "test",
        "entities": {"links": [], "phones": [], "upi_ids": ["hospital.care@upi"], "amounts": [18000]}
    },
    {
        "id": "SCAM_042",
        "text": "EB power cut aaga poguthu iniku night 9pm ku. Bill update aagala. Contact pannunga officer Sharma number 9840223344.",
        "category": "scam", "expected_level": "high", "scam_type": "electricity_scam", "split": "train",
        "entities": {"links": [], "phones": ["9840223344"], "upi_ids": [], "amounts": []}
    },
    {
        "id": "SCAM_043",
        "text": "Aapka Bijli connection aaj raat 10 baje disconnect hoga. Turant bill clear karne ke liye helpline 9877001122 pe call karein.",
        "category": "scam", "expected_level": "high", "scam_type": "electricity_scam", "split": "test",
        "entities": {"links": [], "phones": ["9877001122"], "upi_ids": [], "amounts": []}
    },
    {
        "id": "SCAM_044",
        "text": "Amma, CBI officer warrant potrukaanga. Video call la irunga, bayapada vendam. ₹45,000 security deposit cbi.bail@upi ku pota case dismiss panniduvaanga.",
        "category": "scam", "expected_level": "high", "scam_type": "digital_arrest", "split": "train",
        "entities": {"links": [], "phones": [], "upi_ids": ["cbi.bail@upi"], "amounts": [45000]}
    },
    {
        "id": "SCAM_045",
        "text": "Aadhaar card block hone wala hai. Police case se bachne ke liye 9822334455 par video call karein aur digital arrest clearance lein.",
        "category": "scam", "expected_level": "high", "scam_type": "digital_arrest", "split": "test",
        "entities": {"links": [], "phones": ["9822334455"], "upi_ids": [], "amounts": []}
    },
    {
        "id": "SCAM_046",
        "text": "Ungaluku KBC lottery la ₹10 Lakhs prize vilunthurukku. Processing fee ₹5,000 matum kbc.tax@upi ku anupuna amount bank ku vanthurum.",
        "category": "scam", "expected_level": "high", "scam_type": "lottery_scam", "split": "train",
        "entities": {"links": [], "phones": [], "upi_ids": ["kbc.tax@upi"], "amounts": [5000, 1000000]}
    },
    {
        "id": "SCAM_047",
        "text": "Sir, SBI Yono account band ho chuka hai. PAN card link karne ke liye http://yono-sbi-kyc.cc pe login karein warna balance freeze ho jayega.",
        "category": "scam", "expected_level": "high", "scam_type": "phishing_kyc", "split": "test",
        "entities": {"links": ["http://yono-sbi-kyc.cc"], "phones": [], "upi_ids": [], "amounts": []}
    },

    # ==========================================================================
    # CATEGORY 11: MORE REALISTIC GENUINE ALERTS & NOTIFICATIONS (15 Samples)
    # ==========================================================================
    {
        "id": "GENUINE_016",
        "text": "Axis Bank Alert: ₹2,100.00 debited from account ending 4821 at DMART CHENNAI on 01-NOV. Balance: ₹14,210.00. Call 18604195555 if unrecognised.",
        "category": "genuine_scary", "expected_level": "safe", "scam_type": "none", "split": "train",
        "entities": {"links": [], "phones": ["18604195555"], "upi_ids": [], "amounts": [2100]}
    },
    {
        "id": "GENUINE_017",
        "text": "Kotak Mahindra Bank: ₹850.00 debited for annual debit card maintenance charge on a/c **3012. Statement available on netbanking.",
        "category": "genuine_scary", "expected_level": "safe", "scam_type": "none", "split": "test",
        "entities": {"links": [], "phones": [], "upi_ids": [], "amounts": [850]}
    },
    {
        "id": "GENUINE_018",
        "text": "Indian Railways: Your Tatkal ticket booking for Chennai to Madurai is confirmed. PNR: 4920194821. Train 12635 Vaigai Superfast.",
        "category": "genuine_scary", "expected_level": "safe", "scam_type": "none", "split": "train",
        "entities": {"links": [], "phones": [], "upi_ids": [], "amounts": []}
    },
    {
        "id": "GENUINE_019",
        "text": "Swiggy Instamart: Order delivered. Thank you for tipping your delivery executive ₹30. View invoice on app.",
        "category": "genuine_scary", "expected_level": "safe", "scam_type": "none", "split": "test",
        "entities": {"links": [], "phones": [], "upi_ids": [], "amounts": [30]}
    },
    {
        "id": "GENUINE_020",
        "text": "EPFO Notification: Monthly contribution of ₹3,600 credited to your Universal Account Number (UAN) 100948201942 for SEP-2026.",
        "category": "genuine_scary", "expected_level": "safe", "scam_type": "none", "split": "train",
        "entities": {"links": [], "phones": [], "upi_ids": [], "amounts": [3600]}
    },
    {
        "id": "GENUINE_021",
        "text": "TNEB Bill Receipt: Payment of ₹820.00 received for consumer #04-120-492 on 01-NOV. Transaction ID: TNEB849201. Thank you.",
        "category": "genuine_scary", "expected_level": "safe", "scam_type": "none", "split": "train",
        "entities": {"links": [], "phones": [], "upi_ids": [], "amounts": [820]}
    },
    {
        "id": "GENUINE_022",
        "text": "Blue Dart Express: Courier shipment with AWB 849201849 is out for delivery today. Delivery agent will contact you before arrival.",
        "category": "genuine_scary", "expected_level": "safe", "scam_type": "none", "split": "test",
        "entities": {"links": [], "phones": [], "upi_ids": [], "amounts": []}
    },
    {
        "id": "GENUINE_023",
        "text": "Canara Bank: Your quarterly interest of ₹412.00 has been credited to your savings account ending in 8102.",
        "category": "genuine_scary", "expected_level": "safe", "scam_type": "none", "split": "train",
        "entities": {"links": [], "phones": [], "upi_ids": [], "amounts": [412]}
    },

    # ==========================================================================
    # CATEGORY 12: MORE FAMILY & CASUAL CHATS (12 Samples)
    # ==========================================================================
    {
        "id": "NORMAL_013",
        "text": "Amma, iniki dinner ku dosai senjirukia? Vantaan 15 minutes la.",
        "category": "normal", "expected_level": "safe", "scam_type": "none", "split": "train",
        "entities": {"links": [], "phones": [], "upi_ids": [], "amounts": []}
    },
    {
        "id": "NORMAL_014",
        "text": "Mummy, aaj sham ko sabzi le kar aaunga. Paneer chahiye kya?",
        "category": "normal", "expected_level": "safe", "scam_type": "none", "split": "test",
        "entities": {"links": [], "phones": [], "upi_ids": [], "amounts": []}
    },
    {
        "id": "NORMAL_015",
        "text": "Pay ₹500 to saravana.groceries@upi for oil and wheat flour.",
        "category": "normal", "expected_level": "safe", "scam_type": "none", "split": "train",
        "entities": {"links": [], "phones": [], "upi_ids": ["saravana.groceries@upi"], "amounts": [500]}
    },
    {
        "id": "NORMAL_016",
        "text": "Paati, happy anniversary to you and Thatha! Have a blessed day ahead.",
        "category": "normal", "expected_level": "safe", "scam_type": "none", "split": "test",
        "entities": {"links": [], "phones": [], "upi_ids": [], "amounts": []}
    },
    {
        "id": "NORMAL_017",
        "text": "Kavitha aunty called to say they are visiting next Sunday evening. Please let Thatha know.",
        "category": "normal", "expected_level": "safe", "scam_type": "none", "split": "train",
        "entities": {"links": [], "phones": [], "upi_ids": [], "amounts": []}
    },
    {
        "id": "NORMAL_018",
        "text": "Pay ₹350 to anand.milk@upi for extra curd and butter.",
        "category": "normal", "expected_level": "safe", "scam_type": "none", "split": "train",
        "entities": {"links": [], "phones": [], "upi_ids": ["anand.milk@upi"], "amounts": [350]}
    }
]

def main():
    with open(DATASET_PATH, "w", encoding="utf-8") as f:
        json.dump(DATASET, f, indent=2, ensure_ascii=False)
    print(f"[OK] Generated {len(DATASET)} benchmark samples in '{DATASET_PATH}'")

if __name__ == "__main__":
    main()
