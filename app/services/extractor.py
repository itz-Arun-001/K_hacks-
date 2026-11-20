"""extractor.py - pulls links, phone numbers, UPI IDs and amounts out of a message.
Pure Python (no API, no install). Usage: extract(text) -> dict
"""
import re

# http(s):// links or www. links
LINK_RE = re.compile(r"(?:https?://|www\.)[^\s<>\"']+", re.I)

# UPI ID = name@bank. The lookahead stops emails (a@b.com) from matching.
UPI_RE = re.compile(r"(?<![\w.])[\w.\-]{2,}@[a-zA-Z]{2,}(?![\w]|\.\w)")

# Indian mobile: optional +91 / 91 / 0, then 10 digits starting 6-9
PHONE_RE = re.compile(r"(?<!\d)(?:\+?91[\s-]?|0)?([6-9]\d{4}[\s-]?\d{5})(?!\d)")

# Rs.5,000 / INR 2 lakh   (symbol first)
AMT_PRE_RE = re.compile(
    r"(?:₹|\brs\.?|\binr)\s*(\d[\d,]*(?:\.\d+)?)\s*(lakhs?|crores?|k)?\b", re.I)
# 500 rupees / 5000 rs   (number first)
AMT_POST_RE = re.compile(
    r"(?<![\d,.])(\d[\d,]*(?:\.\d+)?)\s*(lakhs?|crores?|k)?\s*(?:rupees|rs\b|inr\b)", re.I)

MULT = {"k": 1_000, "lakh": 100_000, "lakhs": 100_000, "crore": 10_000_000, "crores": 10_000_000}


def _to_amount(num, unit):
    value = float(num.replace(",", ""))
    if unit:
        value *= MULT[unit.lower()]
    return int(value) if value == int(value) else value


def extract(text):
    # 1. links first, then remove them so their digits/@ don't confuse other regexes
    links = [l.rstrip(".,;:!?)") for l in LINK_RE.findall(text)]
    rest = LINK_RE.sub(" ", text)

    # 2. UPI IDs, then remove them too
    upi_ids = [u.lower() for u in UPI_RE.findall(rest)]
    rest = UPI_RE.sub(" ", rest)

    # 3. phones (normalised to 10 digits)
    phones = [re.sub(r"\D", "", p) for p in PHONE_RE.findall(rest)]
    rest = PHONE_RE.sub(" ", rest)

    # 4. amounts
    amounts = [_to_amount(n, u) for n, u in AMT_PRE_RE.findall(rest)]
    amounts += [_to_amount(n, u) for n, u in AMT_POST_RE.findall(rest)]

    # remove duplicates, keep order
    dedupe = lambda items: list(dict.fromkeys(items))
    return {
        "links": dedupe(links),
        "phones": dedupe(phones),
        "upi_ids": dedupe(upi_ids),
        "amounts": dedupe(amounts),
    }
