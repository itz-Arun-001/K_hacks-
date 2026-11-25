"""Run from the repo root:  python -m pytest tests/test_extractor.py"""
from app.services.extractor import extract


def test_full_scam_message():
    r = extract("SBI: Account blocked. Click http://sbi-kyc.xyz and pay ₹10 to scam@upi. "
                "Call +91 98765 43210.")
    assert r["links"] == ["http://sbi-kyc.xyz"]
    assert r["upi_ids"] == ["scam@upi"]
    assert r["amounts"] == [10]
    assert r["phones"] == ["9876543210"]


def test_link_trailing_punctuation():
    assert extract("Visit https://bit.ly/abc123.")["links"] == ["https://bit.ly/abc123"]
    assert extract("go to www.free-gift.in now")["links"] == ["www.free-gift.in"]


def test_email_is_not_upi():
    assert extract("mail me at john@gmail.com")["upi_ids"] == []


def test_upi_variants():
    r = extract("send to kbc.claim@upi or ramesh-22@okaxis")
    assert r["upi_ids"] == ["kbc.claim@upi", "ramesh-22@okaxis"]


def test_phone_formats():
    for p in ["9876543210", "+919876543210", "91 98765-43210", "098765 43210"]:
        assert extract(f"call {p} now")["phones"] == ["9876543210"], p


def test_phone_ignores_bad_numbers():
    assert extract("OTP 123456 and id 5876543210123")["phones"] == []


def test_amount_formats():
    assert extract("pay Rs. 5,000")["amounts"] == [5000]
    assert extract("you won ₹25 lakh")["amounts"] == [2500000]
    assert extract("send 500 rupees")["amounts"] == [500]
    assert extract("INR 1.5 crore prize")["amounts"] == [15000000]


def test_no_false_amount():
    assert extract("in 2 hours")["amounts"] == []


def test_empty_message():
    assert extract("hello") == {"links": [], "phones": [], "upi_ids": [], "amounts": []}
