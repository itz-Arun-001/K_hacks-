"""
SafeLoop Synthetic Banking & Mule Network Dataset Generator
Author: Person 3 (Monica) - Graph Intelligence & Bank Console Lead
Branch: p3-graph

Generates ~500 realistic synthetic Indian bank accounts and an extensive
transaction graph containing:
1. Normal everyday peer-to-peer and merchant transactions.
2. Suspicious laundering rings:
   - Fan-in / Fan-out hub (featuring clearance.cop@sbi, dispersing 95% within 30 min)
   - Multi-hop layering chains (3 to 5 hops)
   - Circular transaction loops (cycles)
3. Innocent baseline controls (must NOT be falsely flagged by graph detectors):
   - Busy tea stall: High in-degree, low amounts, no rapid outbound dispersal.
   - Landlord: Multiple high-value rent inflows on the 1st of the month, funds held.

Saves the complete network graph to: data/synthetic_mules.json
"""

import os
import sys
import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Tuple

# Set fixed random seed for 100% reproducible data generation
RANDOM_SEED = 42
random.seed(RANDOM_SEED)

# Attempt to import Faker; provide built-in Indian data fallback if not yet installed
try:
    from faker import Faker
    fake = Faker("en_IN")
    Faker.seed(RANDOM_SEED)
except ImportError:
    fake = None

# ==============================================================================
# CONFIGURATION & CONSTANTS
# ==============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_FILE = BASE_DIR / "data" / "synthetic_mules.json"

INDIAN_BANKS = [
    "State Bank of India",
    "HDFC Bank",
    "ICICI Bank",
    "Axis Bank",
    "Punjab National Bank",
    "Canara Bank",
    "Bank of Baroda",
    "Kotak Mahindra Bank",
    "Union Bank of India",
    "IndusInd Bank",
]

UPI_HANDLES = [
    "oksbi",
    "okhdfcbank",
    "icici",
    "okaxis",
    "paytm",
    "ybl",
    "barodampay",
    "pnb",
]

# Fallback Indian names if Faker is not installed
INDIAN_FIRST_NAMES = [
    "Aarav", "Aditi", "Ananya", "Arun", "Deepak", "Divya", "Ganesh", "Gayathri",
    "Harish", "Ishaan", "Kavya", "Karthik", "Lakshmi", "Madhav", "Meenakshi",
    "Manoj", "Naveen", "Nandini", "Pooja", "Pradeep", "Priya", "Rahul", "Rajesh",
    "Ramesh", "Rekha", "Rohan", "Sanjay", "Saravanan", "Shalini", "Sneha",
    "Suresh", "Swaminathan", "Varun", "Venkatesh", "Vidya", "Vignesh", "Vijay",
]

INDIAN_LAST_NAMES = [
    "Agarwal", "Balan", "Bose", "Chawla", "Deshmukh", "Gupta", "Iyer", "Jadhav",
    "Joshi", "Kapoor", "Kumar", "Menon", "Mishra", "Murugan", "Nair", "Patel",
    "Pillai", "Prasad", "Raman", "Rao", "Reddy", "Sengupta", "Sharma", "Singh",
    "Subramanian", "Sundaram", "Verma", "Vyas", "Yadav",
]

MERCHANT_NAMES = [
    ("Saravana Stores Groceries", "groceries"),
    ("Apollo Pharmacy", "medical"),
    ("Nilgiris Supermarket", "groceries"),
    ("Anand Milk & Dairy", "dairy"),
    ("Krishna Sweets & Bakery", "food"),
    ("Bharat Petroleum Pump", "fuel"),
    ("TNEB Electricity Collection", "utility"),
    ("Swiggy Orders Desk", "food"),
    ("Zomato Payments", "food"),
    ("Reliance Digital Retail", "electronics"),
    ("Chennai Silks Textiles", "apparel"),
]


# ==============================================================================
# HELPER GENERATOR FUNCTIONS
# ==============================================================================

def generate_random_name() -> str:
    """Generates a realistic Indian person name."""
    if fake:
        return fake.name()
    fn = random.choice(INDIAN_FIRST_NAMES)
    ln = random.choice(INDIAN_LAST_NAMES)
    return f"{fn} {ln}"


def clean_upi_string(name: str, handle: str) -> str:
    """Creates a clean UPI handle from an owner name and bank extension."""
    clean = "".join(c.lower() for c in name if c.isalnum() or c == " ")
    parts = clean.split()
    if len(parts) >= 2:
        prefix = f"{parts[0]}.{parts[1]}"
    elif parts:
        prefix = f"{parts[0]}{random.randint(10, 99)}"
    else:
        prefix = f"user{random.randint(1000, 9999)}"
    return f"{prefix}@{handle}"


def generate_account_number(bank_code: str, seq: int) -> str:
    """Generates a unique 12-to-14 digit Indian bank account number."""
    return f"{bank_code}{seq:08d}"


# ==============================================================================
# 1. GENERATE BASE & NORMAL ACCOUNTS (~460 ACCOUNTS)
# ==============================================================================

def create_normal_accounts(target_count: int = 460) -> List[Dict[str, Any]]:
    """Generates regular Indian citizens and local businesses."""
    accounts = []
    used_upis = set()
    used_accs = set()

    bank_prefixes = {
        "State Bank of India": "SBIN",
        "HDFC Bank": "HDFC",
        "ICICI Bank": "ICIC",
        "Axis Bank": "UTIB",
        "Punjab National Bank": "PUNB",
        "Canara Bank": "CNRB",
        "Bank of Baroda": "BARB",
        "Kotak Mahindra Bank": "KKBK",
        "Union Bank of India": "UBIN",
        "IndusInd Bank": "INDB",
    }

    # Add standard merchants
    for name, cat in MERCHANT_NAMES:
        bank = random.choice(INDIAN_BANKS)
        prefix = bank_prefixes[bank]
        acc_num = f"{prefix}{random.randint(10000000, 99999999)}"
        upi = f"{name.split()[0].lower()}.pay@{random.choice(UPI_HANDLES)}"
        used_upis.add(upi)
        used_accs.add(acc_num)
        accounts.append({
            "account_number": acc_num,
            "upi_id": upi,
            "owner_name": name,
            "bank_name": bank,
            "is_mule": False,
            "ring_id": None,
            "risk_score": 0.02,
            "account_type": f"merchant_{cat}",
            "created_at": "2026-08-15T09:00:00",
        })

    # Add general individual accounts
    seq = 1000
    while len(accounts) < target_count:
        seq += 1
        bank = random.choice(INDIAN_BANKS)
        prefix = bank_prefixes[bank]
        acc_num = generate_account_number(prefix, seq)
        if acc_num in used_accs:
            continue

        name = generate_random_name()
        handle = random.choice(UPI_HANDLES)
        upi = clean_upi_string(name, handle)
        if upi in used_upis:
            upi = f"{upi.split('@')[0]}{random.randint(10, 99)}@{handle}"

        used_upis.add(upi)
        used_accs.add(acc_num)

        accounts.append({
            "account_number": acc_num,
            "upi_id": upi,
            "owner_name": name,
            "bank_name": bank,
            "is_mule": False,
            "ring_id": None,
            "risk_score": round(random.uniform(0.01, 0.15), 2),
            "account_type": "savings",
            "created_at": (datetime(2026, 1, 1) + timedelta(days=random.randint(0, 250))).isoformat(),
        })

    return accounts


# ==============================================================================
# 2. GENERATE INNOCENT LOOKALIKES (TEA STALL & LANDLORD)
# ==============================================================================

def create_innocent_controls(normal_accounts: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Creates two innocent baseline accounts with high or bursty transaction
    volumes that MUST NOT be flagged as mule rings:
    1. Busy Tea Stall: 60+ small incoming payments, zero rapid dispersal.
    2. Landlord: 8 monthly rent collections on 1st of month, funds held.
    
    Draws customers, tenants, and merchants from normal_accounts to ensure
    100% referential integrity (zero orphan transaction endpoints).
    """
    accounts = []
    transactions = []

    citizens = [a for a in normal_accounts if a["account_type"] == "savings"]
    merchants = [a for a in normal_accounts if a["account_type"].startswith("merchant_")]

    # --------------------------------------------------------------------------
    # Control 1: Murugan Tea Stall (High In-Degree, Micro-Amounts, No Dispersal)
    # --------------------------------------------------------------------------
    tea_acc_num = "UTIB00881921"
    tea_upi = "murugan.tea@okaxis"
    tea_account = {
        "account_number": tea_acc_num,
        "upi_id": tea_upi,
        "owner_name": "Murugan Tea Stall & Snacks",
        "bank_name": "Axis Bank",
        "is_mule": False,
        "ring_id": None,
        "risk_score": 0.05,
        "account_type": "innocent_tea_stall",
        "created_at": "2025-06-10T10:00:00",
        "notes": "Legitimate high-frequency micro merchant; no pass-through dispersal",
    }
    accounts.append(tea_account)

    # Generate 65 small payments over 3 days (₹15 to ₹80) from regular citizens
    base_time_tea = datetime(2026, 11, 1, 7, 30, 0)
    for i in range(65):
        tx_time = base_time_tea + timedelta(
            days=random.choice([0, 1, 2]),
            hours=random.randint(0, 12),
            minutes=random.randint(1, 59),
            seconds=random.randint(0, 59)
        )
        amt = random.choice([15.0, 20.0, 25.0, 30.0, 40.0, 50.0, 75.0])
        cust = citizens[i % len(citizens)]
        transactions.append({
            "transaction_id": f"TXN_TEA_{i+1:04d}",
            "sender_account": cust["account_number"],
            "receiver_account": tea_acc_num,
            "sender_upi": cust["upi_id"],
            "receiver_upi": tea_upi,
            "amount": amt,
            "timestamp": tx_time.isoformat(),
            "is_mule_flow": False,
            "pattern": "innocent_tea_stall",
            "description": f"Tea & snacks order #{i+1}",
        })

    # Tea stall makes only 1 standard weekly supplier payment days later (NOT rapid)
    dairy_supplier = next((m for m in merchants if "dairy" in m["account_type"]), merchants[0])
    supplier_time = datetime(2026, 11, 4, 18, 0, 0)
    transactions.append({
        "transaction_id": "TXN_TEA_SUPPLY_01",
        "sender_account": tea_acc_num,
        "receiver_account": dairy_supplier["account_number"],
        "sender_upi": tea_upi,
        "receiver_upi": dairy_supplier["upi_id"],
        "amount": 1450.0,
        "timestamp": supplier_time.isoformat(),
        "is_mule_flow": False,
        "pattern": "normal_supplier",
        "description": "Weekly milk & tea powder purchase",
    })

    # --------------------------------------------------------------------------
    # Control 2: R. K. Sharma (Landlord - Batch Rent Collection, Funds Retained)
    # --------------------------------------------------------------------------
    landlord_acc_num = "ICIC00119283"
    landlord_upi = "sharma.rentals@icici"
    landlord_account = {
        "account_number": landlord_acc_num,
        "upi_id": landlord_upi,
        "owner_name": "R. K. Sharma (Landlord)",
        "bank_name": "ICICI Bank",
        "is_mule": False,
        "ring_id": None,
        "risk_score": 0.08,
        "account_type": "innocent_landlord",
        "created_at": "2024-11-01T08:00:00",
        "notes": "Legitimate landlord receiving batch monthly rent; funds held in savings",
    }
    accounts.append(landlord_account)

    # 8 tenants paying rent on 1st November 2026 between 08:00 and 19:00
    rent_amounts = [18000.0, 20000.0, 22500.0, 25000.0, 19000.0, 21000.0, 24000.0, 20000.0]
    base_time_rent = datetime(2026, 11, 1, 8, 0, 0)
    tenants = citizens[:8]
    for i, amt in enumerate(rent_amounts):
        t_time = base_time_rent + timedelta(hours=i * 1.3, minutes=random.randint(5, 30))
        tenant = tenants[i]
        transactions.append({
            "transaction_id": f"TXN_RENT_{i+1:03d}",
            "sender_account": tenant["account_number"],
            "receiver_account": landlord_acc_num,
            "sender_upi": tenant["upi_id"],
            "receiver_upi": landlord_upi,
            "amount": amt,
            "timestamp": t_time.isoformat(),
            "is_mule_flow": False,
            "pattern": "innocent_landlord",
            "description": f"Apartment rent for November 2026 - Flat {101+i}",
        })

    # Landlord does not disperse money out rapidly. Only one normal electricity bill paid
    utility_supplier = next((m for m in merchants if "utility" in m["account_type"]), merchants[1])
    transactions.append({
        "transaction_id": "TXN_LANDLORD_EB_01",
        "sender_account": landlord_acc_num,
        "receiver_account": utility_supplier["account_number"],
        "sender_upi": landlord_upi,
        "receiver_upi": utility_supplier["upi_id"],
        "amount": 3200.0,
        "timestamp": "2026-11-05T14:20:00",
        "is_mule_flow": False,
        "pattern": "normal_utility",
        "description": "Building common area electricity bill",
    })

    return accounts, transactions


# ==============================================================================
# 3. GENERATE SUSPICIOUS FRAUD PATTERN 1: FAN-IN / FAN-OUT RING
# ==============================================================================

def create_fan_in_fan_out_ring() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Generates Ring 1: High-Velocity Aggregation & Dispersal Hub.
    - 10 victim accounts send ₹25,000 - ₹50,000 to clearance.cop@sbi (Fan-in)
    - clearance.cop@sbi forwards 95% of the total funds to 5 cash-out mule accounts
      within 30 minutes (Fan-out)
    """
    accounts = []
    transactions = []

    ring_id = "ring_fan_in_out"
    hub_acc_num = "SBIN00551902"
    hub_upi = "clearance.cop@sbi"  # Target entity from Live Demo Script

    # Central Hub Mule Account
    hub_account = {
        "account_number": hub_acc_num,
        "upi_id": hub_upi,
        "owner_name": "Clearance Officer Desk (Syndicate Hub)",
        "bank_name": "State Bank of India",
        "is_mule": True,
        "ring_id": ring_id,
        "risk_score": 0.98,
        "account_type": "mule_hub",
        "created_at": "2026-10-25T11:00:00",
        "notes": "Central aggregation hub for Digital Arrest extortion syndicate",
    }
    accounts.append(hub_account)

    # 10 Victim / Coerced Senders
    victim_amounts = [35000.0, 50000.0, 45000.0, 25000.0, 40000.0, 50000.0, 30000.0, 45000.0, 50000.0, 30000.0]
    total_inflow = sum(victim_amounts)  # ₹4,00,000

    # Inbound Fan-In: Nov 1, 2026 between 09:00:00 and 09:30:00
    base_time_in = datetime(2026, 11, 1, 9, 0, 0)
    for i, amt in enumerate(victim_amounts):
        in_time = base_time_in + timedelta(minutes=i * 2.8, seconds=random.randint(5, 45))
        v_acc = f"VICTIM_{i+1:03d}_{random.randint(1000, 9999)}"
        v_upi = f"senior.citizen{i+1}@okhdfcbank"

        # Victim account entry
        accounts.append({
            "account_number": v_acc,
            "upi_id": v_upi,
            "owner_name": f"Victim Elderly Parent {i+1}",
            "bank_name": "HDFC Bank",
            "is_mule": False,
            "ring_id": ring_id,
            "risk_score": 0.40,
            "account_type": "victim_coerced",
            "created_at": "2025-01-15T10:00:00",
        })

        transactions.append({
            "transaction_id": f"TXN_FAN_IN_{i+1:02d}",
            "sender_account": v_acc,
            "receiver_account": hub_acc_num,
            "sender_upi": v_upi,
            "receiver_upi": hub_upi,
            "amount": amt,
            "timestamp": in_time.isoformat(),
            "is_mule_flow": True,
            "pattern": "fan_in",
            "description": f"Coerced Digital Arrest bond payment #{i+1}",
        })

    # Outbound Fan-Out: 5 Cash-out Mules receiving 95% of inflow within 30 min (09:35 to 09:55)
    # Total outflow = 0.95 * 4,00,000 = ₹3,80,000 (avg ₹76,000 each)
    cashout_amounts = [80000.0, 80000.0, 75000.0, 75000.0, 70000.0]
    cashout_banks = ["Punjab National Bank", "Canara Bank", "Paytm Payments Bank", "Axis Bank", "State Bank of India"]
    cashout_handles = ["pnb", "cnrb", "paytm", "okaxis", "oksbi"]

    base_time_out = datetime(2026, 11, 1, 9, 35, 0)
    for j, (out_amt, c_bank, c_handle) in enumerate(zip(cashout_amounts, cashout_banks, cashout_handles)):
        out_time = base_time_out + timedelta(minutes=j * 4.2, seconds=random.randint(10, 40))
        c_acc = f"CASHOUT_MULE_{j+1:02d}_{random.randint(1000, 9999)}"
        c_upi = f"cashout.agent{j+1}@{c_handle}"

        accounts.append({
            "account_number": c_acc,
            "upi_id": c_upi,
            "owner_name": f"Cashout Runner {j+1}",
            "bank_name": c_bank,
            "is_mule": True,
            "ring_id": ring_id,
            "risk_score": 0.95,
            "account_type": "mule_cashout",
            "created_at": "2026-10-28T14:00:00",
        })

        transactions.append({
            "transaction_id": f"TXN_FAN_OUT_{j+1:02d}",
            "sender_account": hub_acc_num,
            "receiver_account": c_acc,
            "sender_upi": hub_upi,
            "receiver_upi": c_upi,
            "amount": out_amt,
            "timestamp": out_time.isoformat(),
            "is_mule_flow": True,
            "pattern": "fan_out",
            "description": f"Rapid mule dispersal #{j+1} to secondary cashout operative",
        })

    return accounts, transactions


# ==============================================================================
# 4. GENERATE SUSPICIOUS FRAUD PATTERN 2: MULTI-HOP LAYERING CHAINS
# ==============================================================================

def create_layering_chains() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Generates Multi-Hop Layering Chains:
    - Chain 1 (5 accounts, 4 hops): A -> B -> C -> D -> E
    - Chain 2 (4 accounts, 3 hops): W -> X -> Y -> Z
    Money passes between hops in 3-5 minute intervals with small fee haircuts.
    """
    accounts = []
    transactions = []

    # --------------------------------------------------------------------------
    # Chain 1: 5-Account, 4-Hop Layering Chain
    # --------------------------------------------------------------------------
    chain1_id = "ring_chain_5hop"
    chain1_names = [
        ("ACC_CH1_HOP0_SRC", "phish.victim.source@oksbi", "Source Victim (Electricity Phishing)", "State Bank of India", False),
        ("ACC_CH1_HOP1_L1", "layer1.transit@okhdfcbank", "Layer 1 Smurfing Mule", "HDFC Bank", True),
        ("ACC_CH1_HOP2_L2", "layer2.transit@icici", "Layer 2 Bridge Mule", "ICICI Bank", True),
        ("ACC_CH1_HOP3_L3", "layer3.transit@okaxis", "Layer 3 Washing Mule", "Axis Bank", True),
        ("ACC_CH1_HOP4_EXIT", "crypto.cashout.exit@paytm", "Layer 4 P2P Crypto Cashout", "Paytm Payments Bank", True),
    ]

    for acc_num, upi, name, bank, is_m in chain1_names:
        accounts.append({
            "account_number": acc_num,
            "upi_id": upi,
            "owner_name": name,
            "bank_name": bank,
            "is_mule": is_m,
            "ring_id": chain1_id,
            "risk_score": 0.95 if is_m else 0.35,
            "account_type": "layering_hop",
            "created_at": "2026-10-10T12:00:00",
        })

    chain1_amounts = [75000.0, 73500.0, 72000.0, 70500.0]
    base_time_ch1 = datetime(2026, 11, 2, 11, 0, 0)
    for k in range(4):
        src_acc = chain1_names[k][0]
        src_upi = chain1_names[k][1]
        dst_acc = chain1_names[k+1][0]
        dst_upi = chain1_names[k+1][1]
        tx_t = base_time_ch1 + timedelta(minutes=k * 4.5, seconds=random.randint(5, 30))

        transactions.append({
            "transaction_id": f"TXN_CHAIN1_HOP_{k+1}",
            "sender_account": src_acc,
            "receiver_account": dst_acc,
            "sender_upi": src_upi,
            "receiver_upi": dst_upi,
            "amount": chain1_amounts[k],
            "timestamp": tx_t.isoformat(),
            "is_mule_flow": True,
            "pattern": "layering_chain_5hop",
            "description": f"Layering chain hop {k+1} -> {k+2}",
        })

    # --------------------------------------------------------------------------
    # Chain 2: 4-Account, 3-Hop Layering Chain
    # --------------------------------------------------------------------------
    chain2_id = "ring_chain_4hop"
    chain2_names = [
        ("ACC_CH2_HOP0_SRC", "job.fraud.victim@oksbi", "Source Victim (Task Job Scam)", "State Bank of India", False),
        ("ACC_CH2_HOP1_L1", "transit.gateway1@barodampay", "Transit Relay Mule Alpha", "Bank of Baroda", True),
        ("ACC_CH2_HOP2_L2", "transit.gateway2@pnb", "Transit Relay Mule Beta", "Punjab National Bank", True),
        ("ACC_CH2_HOP3_EXIT", "atm.runner.exit@ybl", "Final ATM Withdrawal Mule", "Yes Bank", True),
    ]

    for acc_num, upi, name, bank, is_m in chain2_names:
        accounts.append({
            "account_number": acc_num,
            "upi_id": upi,
            "owner_name": name,
            "bank_name": bank,
            "is_mule": is_m,
            "ring_id": chain2_id,
            "risk_score": 0.92 if is_m else 0.35,
            "account_type": "layering_hop",
            "created_at": "2026-10-15T15:00:00",
        })

    chain2_amounts = [60000.0, 58800.0, 57600.0]
    base_time_ch2 = datetime(2026, 11, 2, 14, 30, 0)
    for m in range(3):
        src_acc = chain2_names[m][0]
        src_upi = chain2_names[m][1]
        dst_acc = chain2_names[m+1][0]
        dst_upi = chain2_names[m+1][1]
        tx_t = base_time_ch2 + timedelta(minutes=m * 5.0, seconds=random.randint(10, 40))

        transactions.append({
            "transaction_id": f"TXN_CHAIN2_HOP_{m+1}",
            "sender_account": src_acc,
            "receiver_account": dst_acc,
            "sender_upi": src_upi,
            "receiver_upi": dst_upi,
            "amount": chain2_amounts[m],
            "timestamp": tx_t.isoformat(),
            "is_mule_flow": True,
            "pattern": "layering_chain_4hop",
            "description": f"Layering chain hop {m+1} -> {m+2}",
        })

    return accounts, transactions


# ==============================================================================
# 5. GENERATE SUSPICIOUS FRAUD PATTERN 3: TRANSACTION CYCLES (CIRCULAR LOOPS)
# ==============================================================================

def create_circular_rings() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Generates Circular Transaction Rings (Loops):
    - Cycle 1 (3 nodes): Account A -> B -> C -> A (₹45,000 recirculated)
    - Cycle 2 (4 nodes): Account W -> X -> Y -> Z -> W (₹30,000 recirculated)
    Used by syndicates to artificially inflate account activity and churn balances.
    """
    accounts = []
    transactions = []

    # --------------------------------------------------------------------------
    # Cycle 1: 3-Node Circular Loop (A -> B -> C -> A)
    # --------------------------------------------------------------------------
    cycle1_id = "ring_cycle_3node"
    cycle1_nodes = [
        ("ACC_CYC1_A", "cycle.nodeA@oksbi", "Circular Operative A", "State Bank of India"),
        ("ACC_CYC1_B", "cycle.nodeB@okhdfcbank", "Circular Operative B", "HDFC Bank"),
        ("ACC_CYC1_C", "cycle.nodeC@okaxis", "Circular Operative C", "Axis Bank"),
    ]

    for acc_num, upi, name, bank in cycle1_nodes:
        accounts.append({
            "account_number": acc_num,
            "upi_id": upi,
            "owner_name": name,
            "bank_name": bank,
            "is_mule": True,
            "ring_id": cycle1_id,
            "risk_score": 0.90,
            "account_type": "mule_cycle",
            "created_at": "2026-09-20T10:00:00",
        })

    cycle1_edges = [
        (0, 1, 45000.0, 0),
        (1, 2, 44200.0, 18),
        (2, 0, 43500.0, 36),
    ]
    base_time_cyc1 = datetime(2026, 11, 3, 16, 0, 0)
    for idx, (s_idx, d_idx, amt, delta_min) in enumerate(cycle1_edges):
        tx_t = base_time_cyc1 + timedelta(minutes=delta_min, seconds=random.randint(5, 30))
        transactions.append({
            "transaction_id": f"TXN_CYCLE1_LEG_{idx+1}",
            "sender_account": cycle1_nodes[s_idx][0],
            "receiver_account": cycle1_nodes[d_idx][0],
            "sender_upi": cycle1_nodes[s_idx][1],
            "receiver_upi": cycle1_nodes[d_idx][1],
            "amount": amt,
            "timestamp": tx_t.isoformat(),
            "is_mule_flow": True,
            "pattern": "cycle_3node",
            "description": f"Circular loop churn leg {idx+1} ({cycle1_nodes[s_idx][1]} -> {cycle1_nodes[d_idx][1]})",
        })

    # --------------------------------------------------------------------------
    # Cycle 2: 4-Node Circular Loop (W -> X -> Y -> Z -> W)
    # --------------------------------------------------------------------------
    cycle2_id = "ring_cycle_4node"
    cycle2_nodes = [
        ("ACC_CYC2_W", "cycle2.alpha@icici", "Syndicate Churner W", "ICICI Bank"),
        ("ACC_CYC2_X", "cycle2.beta@sbi", "Syndicate Churner X", "State Bank of India"),
        ("ACC_CYC2_Y", "cycle2.gamma@okaxis", "Syndicate Churner Y", "Axis Bank"),
        ("ACC_CYC2_Z", "cycle2.delta@pnb", "Syndicate Churner Z", "Punjab National Bank"),
    ]

    for acc_num, upi, name, bank in cycle2_nodes:
        accounts.append({
            "account_number": acc_num,
            "upi_id": upi,
            "owner_name": name,
            "bank_name": bank,
            "is_mule": True,
            "ring_id": cycle2_id,
            "risk_score": 0.88,
            "account_type": "mule_cycle",
            "created_at": "2026-09-22T14:00:00",
        })

    cycle2_edges = [
        (0, 1, 30000.0, 0),
        (1, 2, 29400.0, 15),
        (2, 3, 28800.0, 30),
        (3, 0, 28200.0, 48),
    ]
    base_time_cyc2 = datetime(2026, 11, 4, 10, 0, 0)
    for idx, (s_idx, d_idx, amt, delta_min) in enumerate(cycle2_edges):
        tx_t = base_time_cyc2 + timedelta(minutes=delta_min, seconds=random.randint(5, 30))
        transactions.append({
            "transaction_id": f"TXN_CYCLE2_LEG_{idx+1}",
            "sender_account": cycle2_nodes[s_idx][0],
            "receiver_account": cycle2_nodes[d_idx][0],
            "sender_upi": cycle2_nodes[s_idx][1],
            "receiver_upi": cycle2_nodes[d_idx][1],
            "amount": amt,
            "timestamp": tx_t.isoformat(),
            "is_mule_flow": True,
            "pattern": "cycle_4node",
            "description": f"Circular loop churn leg {idx+1} ({cycle2_nodes[s_idx][1]} -> {cycle2_nodes[d_idx][1]})",
        })

    return accounts, transactions


# ==============================================================================
# 6. GENERATE NORMAL EVERYDAY TRANSACTIONS (~850 TRANSACTIONS)
# ==============================================================================

def create_normal_transactions(
    normal_accounts: List[Dict[str, Any]],
    target_count: int = 850
) -> List[Dict[str, Any]]:
    """Generates realistic normal retail and P2P transactions between normal citizens."""
    transactions = []
    merchants = [a for a in normal_accounts if a["account_type"].startswith("merchant_")]
    citizens = [a for a in normal_accounts if not a["account_type"].startswith("merchant_")]

    base_date = datetime(2026, 10, 15)

    for i in range(target_count):
        days_offset = random.randint(0, 20)
        hours_offset = random.randint(8, 22)
        mins_offset = random.randint(0, 59)
        secs_offset = random.randint(0, 59)
        tx_time = base_date + timedelta(days=days_offset, hours=hours_offset, minutes=mins_offset, seconds=secs_offset)

        # 70% merchant purchases, 30% peer-to-peer family/friend transfers
        if random.random() < 0.70 and merchants:
            sender = random.choice(citizens)
            receiver = random.choice(merchants)
            amt = round(random.uniform(35.0, 3200.0), 2)
            desc = f"Purchase at {receiver['owner_name']}"
            pattern = "normal_retail"
        else:
            sender, receiver = random.sample(citizens, 2)
            amt = round(random.uniform(100.0, 7500.0), 2)
            desc = random.choice([
                "Dinner split with friends",
                "Medicine reimbursement",
                "Shared auto fare",
                "Birthday gift money",
                "Book club contribution",
                "Utility share",
            ])
            pattern = "normal_p2p"

        transactions.append({
            "transaction_id": f"TXN_NORM_{i+1:05d}",
            "sender_account": sender["account_number"],
            "receiver_account": receiver["account_number"],
            "sender_upi": sender["upi_id"],
            "receiver_upi": receiver["upi_id"],
            "amount": amt,
            "timestamp": tx_time.isoformat(),
            "is_mule_flow": False,
            "pattern": pattern,
            "description": desc,
        })

    return transactions


# ==============================================================================
# MAIN GENERATOR ORCHESTRATOR
# ==============================================================================

def generate_synthetic_dataset() -> Dict[str, Any]:
    """Coordinates generation of all normal, innocent, and suspicious graph entities."""
    print("\n" + "=" * 70)
    print(" SAFELOOP SYNTHETIC MULE NETWORK GENERATOR")
    print(" Lead: Person 3 (Monica) | Branch: p3-graph")
    print("=" * 70)

    # 1. Base normal accounts (target count: 466 so grand total equals exactly 500)
    print("\n[1/5] Generating ~466 normal citizen and merchant accounts...")
    normal_accounts = create_normal_accounts(target_count=466)
    print(f"      Created {len(normal_accounts)} normal accounts.")

    # 2. Innocent controls (Tea Stall & Landlord)
    print("\n[2/5] Creating 2 innocent baseline controls (Tea Stall & Landlord)...")
    innocent_accs, innocent_txs = create_innocent_controls(normal_accounts)
    print(f"      Created {len(innocent_accs)} control accounts with {len(innocent_txs)} transactions.")

    # 3. Suspicious Rings:
    # 3.1 Fan-in / Fan-out (clearance.cop@sbi)
    print("\n[3/5] Planting Suspicious Fraud Pattern 1: Fan-In / Fan-Out Hub...")
    fan_accs, fan_txs = create_fan_in_fan_out_ring()
    print(f"      Hub: clearance.cop@sbi (Inbound: 10 victims, Outbound: 5 cashouts, 95% velocity).")
    print(f"      Added {len(fan_accs)} accounts and {len(fan_txs)} transactions.")

    # 3.2 Layering Chains (5-hop and 4-hop)
    print("\n[4/5] Planting Suspicious Fraud Pattern 2: Multi-Hop Layering Chains...")
    chain_accs, chain_txs = create_layering_chains()
    print(f"      Added {len(chain_accs)} accounts and {len(chain_txs)} transactions across 2 chains.")

    # 3.3 Circular Loops (3-node and 4-node cycles)
    print("\n[5/5] Planting Suspicious Fraud Pattern 3: Circular Transaction Cycles...")
    cycle_accs, cycle_txs = create_circular_rings()
    print(f"      Added {len(cycle_accs)} accounts and {len(cycle_txs)} transactions across 2 cycles.")

    # 4. Normal Background Transactions
    print("\n[+] Generating ~850 normal peer-to-peer and merchant transactions...")
    normal_txs = create_normal_transactions(normal_accounts, target_count=850)
    print(f"      Created {len(normal_txs)} background transactions.")

    # Combine all accounts and transactions
    all_accounts = normal_accounts + innocent_accs + fan_accs + chain_accs + cycle_accs
    all_transactions = normal_txs + innocent_txs + fan_txs + chain_txs + cycle_txs

    # Sort transactions chronologically
    all_transactions.sort(key=lambda x: x["timestamp"])

    # Compute network summary stats
    mule_accounts = [a for a in all_accounts if a["is_mule"]]
    mule_transactions = [t for t in all_transactions if t["is_mule_flow"]]

    dataset = {
        "metadata": {
            "title": "SafeLoop Synthetic Indian Mule Banking Network",
            "author": "Person 3 (Monica)",
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "random_seed": RANDOM_SEED,
            "total_accounts": len(all_accounts),
            "total_transactions": len(all_transactions),
            "mule_accounts_count": len(mule_accounts),
            "mule_transactions_count": len(mule_transactions),
            "innocent_controls_count": len(innocent_accs),
            "rings": [
                {
                    "ring_id": "ring_fan_in_out",
                    "type": "fan_in_fan_out",
                    "target_hub_upi": "clearance.cop@sbi",
                    "description": "10 victim accounts send funds to clearance.cop@sbi; 95% dispersed to 5 cashout mules within 30 min",
                    "accounts_count": len(fan_accs),
                    "transactions_count": len(fan_txs),
                },
                {
                    "ring_id": "ring_chain_5hop",
                    "type": "multi_hop_chain",
                    "description": "5-account 4-hop chain moving funds with small haircut in 4-minute intervals",
                    "hops": 4,
                },
                {
                    "ring_id": "ring_chain_4hop",
                    "type": "multi_hop_chain",
                    "description": "4-account 3-hop chain moving funds in 5-minute intervals",
                    "hops": 3,
                },
                {
                    "ring_id": "ring_cycle_3node",
                    "type": "circular_loop",
                    "description": "3-account cycle A -> B -> C -> A recirculating ₹45,000",
                    "nodes": 3,
                },
                {
                    "ring_id": "ring_cycle_4node",
                    "type": "circular_loop",
                    "description": "4-account cycle W -> X -> Y -> Z -> W recirculating ₹30,000",
                    "nodes": 4,
                },
            ],
            "innocent_controls": [
                {
                    "control_id": "murugan_tea_stall",
                    "upi_id": "murugan.tea@okaxis",
                    "name": "Murugan Tea Stall & Snacks",
                    "expected_verdict": "SAFE",
                    "reason": "High frequency micro-inflows without rapid outbound pass-through dispersal",
                },
                {
                    "control_id": "sharma_landlord",
                    "upi_id": "sharma.rentals@icici",
                    "name": "R. K. Sharma (Landlord)",
                    "expected_verdict": "SAFE",
                    "reason": "Batch rent collection on 1st of month; funds held in savings account",
                },
            ],
        },
        "accounts": all_accounts,
        "transactions": all_transactions,
    }

    return dataset


def save_dataset(dataset: Dict[str, Any], filepath: Path):
    """Saves generated dataset to a formatted JSON file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2)

    file_size_kb = round(os.path.getsize(filepath) / 1024, 1)
    print(f"\n[OK] Successfully saved dataset to: {filepath} ({file_size_kb} KB)")


def print_summary(dataset: Dict[str, Any]):
    """Displays a clean summary table of the generated dataset."""
    meta = dataset["metadata"]
    print("\n" + "=" * 70)
    print(" 📊 GENERATED SYNTHETIC DATASET SUMMARY")
    print("=" * 70)
    print(f"  • Total Bank Accounts:           {meta['total_accounts']}")
    print(f"  • Total Transactions:            {meta['total_transactions']}")
    print(f"  • Ground-Truth Mule Accounts:    {meta['mule_accounts_count']}")
    print(f"  • Ground-Truth Mule Flows:       {meta['mule_transactions_count']}")
    print(f"  • Innocent Control Accounts:     {meta['innocent_controls_count']}")
    print(f"  • Target Fraud Hub Planted:      clearance.cop@sbi (Ring 1)")
    print(f"  • Innocent Controls Planted:     murugan.tea@okaxis & sharma.rentals@icici")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    data = generate_synthetic_dataset()
    save_dataset(data, OUTPUT_FILE)
    print_summary(data)
