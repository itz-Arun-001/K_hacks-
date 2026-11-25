"""Run from the repo root:  python -m pytest tests/test_llm_analyzer.py
These tests use a fake Gemini, so they need no key and no internet."""
from app.services import llm_analyzer as la


def _fake_post(text_out, status=200):
    class R:
        status_code = status
        def json(self):
            return {"candidates": [{"content": {"parts": [{"text": text_out}]}}]}
    return lambda *a, **k: R()


def test_redact_removes_phone_and_upi_but_keeps_link():
    out = la.redact("Call 9876543210 pay scam@upi at http://sbi-kyc.xyz")
    assert "9876543210" not in out and "scam@upi" not in out
    assert "<PHONE>" in out and "<UPI>" in out
    assert "http://sbi-kyc.xyz" in out


def test_good_gemini_answer(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "AIzaFAKE")
    monkeypatch.setattr(la.requests, "post", _fake_post(
        '{"scam_type":"fake_kyc","impersonated_org":"SBI","tactics":["urgency","secrecy","bogus"],'
        '"explanation":"Fake bank message.","language":"en"}'))
    r = la.analyze_message("SBI KYC blocked")
    assert r["source"] == "gemini"
    assert r["scam_type"] == "fake_kyc" and r["impersonated_org"] == "SBI"
    assert r["tactics"] == ["urgency", "secrecy"]          # 'bogus' filtered out


def test_json_in_code_fence(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "AIzaFAKE")
    monkeypatch.setattr(la.requests, "post", _fake_post(
        '```json\n{"scam_type":"lottery","impersonated_org":"","tactics":["reward"],'
        '"explanation":"x","language":"hi"}\n```'))
    assert la.analyze_message("you won")["scam_type"] == "lottery"


def test_bad_json_falls_back(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "AIzaFAKE")
    monkeypatch.setattr(la.requests, "post", _fake_post("not json at all"))
    r = la.analyze_message("Your KYC is blocked, act urgently")
    assert r["source"] == "fallback" and r["scam_type"] == "fake_kyc"


def test_http_error_falls_back(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "AIzaFAKE")
    monkeypatch.setattr(la.requests, "post", _fake_post("{}", status=429))
    assert la.analyze_message("you won a lottery prize")["source"] == "fallback"


def test_no_key_falls_back(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "your_gemini_api_key_here")
    r = la.analyze_message("hello, lunch at 1?")
    assert r["source"] == "fallback" and r["scam_type"] == "none"


def test_unknown_scam_type_is_cleaned(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "AIzaFAKE")
    monkeypatch.setattr(la.requests, "post", _fake_post(
        '{"scam_type":"made_up","impersonated_org":null,"tactics":null,"explanation":null,"language":"fr"}'))
    r = la.analyze_message("x")
    assert r["scam_type"] == "other_scam" and r["tactics"] == [] and r["language"] == "other"


def test_confidence_is_returned_and_clamped(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "AIzaFAKE")
    monkeypatch.setattr(la.requests, "post", _fake_post(
        '{"scam_type":"fake_kyc","confidence":1.7,"impersonated_org":"SBI","tactics":["urgency"],'
        '"explanation":"x","language":"en"}'))
    assert la.analyze_message("x")["confidence"] == 1.0


def test_missing_confidence_gets_default_and_none_is_zero(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "AIzaFAKE")
    monkeypatch.setattr(la.requests, "post", _fake_post(
        '{"scam_type":"lottery","impersonated_org":"","tactics":[],"explanation":"x","language":"en"}'))
    assert la.analyze_message("x")["confidence"] == 0.6
    monkeypatch.setattr(la.requests, "post", _fake_post(
        '{"scam_type":"none","confidence":0.9,"impersonated_org":"","tactics":[],"explanation":"x","language":"en"}'))
    assert la.analyze_message("x")["confidence"] == 0.0


def test_fallback_has_confidence(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "your_gemini_api_key_here")
    assert la.analyze_message("KYC blocked urgent, don't tell anyone")["confidence"] >= 0.7
    assert la.analyze_message("lunch at 1?")["confidence"] == 0.0
