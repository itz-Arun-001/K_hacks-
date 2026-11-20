"""Run from the repo root:  python -m pytest tests/test_webhook.py
Fake Gemini + fake risk engine, so no key, internet or database is needed."""
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import webhook
from app.database import get_db

app = FastAPI()
app.include_router(webhook.router)
app.dependency_overrides[get_db] = lambda: None
client = TestClient(app)

HEAD = {"Content-Type": "application/x-www-form-urlencoded"}
SCAM = "Body=SBI+KYC+blocked+http%3A%2F%2Fsbi-kyc.xyz+pay+%E2%82%B910+to+scam%40upi&From=whatsapp%3A%2B91999"
ANALYSIS = {"scam_type": "fake_kyc", "confidence": 0.9, "impersonated_org": "SBI",
            "tactics": ["urgency"], "explanation": "Fake.", "language": "en", "source": "gemini"}


def test_scam_message_flows_through(monkeypatch):
    seen = {}
    monkeypatch.setattr(webhook, "analyze_message", lambda text: ANALYSIS)

    def fake_engine(**kw):
        seen.update(kw)
        return {"score": 0.9, "level": "high", "reasons": ["x"]}
    monkeypatch.setattr(webhook, "evaluate_risk", fake_engine)

    r = client.post("/whatsapp", content=SCAM, headers=HEAD)
    assert r.status_code == 200 and "xml" in r.headers["content-type"]
    assert "DANGER" in r.text and "1930" in r.text
    assert seen["entities"]["links"] == ["http://sbi-kyc.xyz"]
    assert seen["entities"]["upi_ids"] == ["scam@upi"]
    assert seen["scam_tags"] == {"scam_type": "fake_kyc", "confidence": 0.9, "tactics": ["urgency"]}
    assert seen["user_id"] == "whatsapp:+91999"


def test_tamil_reply(monkeypatch):
    monkeypatch.setattr(webhook, "analyze_message", lambda text: {**ANALYSIS, "language": "ta"})
    monkeypatch.setattr(webhook, "evaluate_risk",
                        lambda **kw: {"score": 0.9, "level": "high", "reasons": []})
    assert "மோசடி" in client.post("/whatsapp", content=SCAM, headers=HEAD).text


def test_empty_message_gets_help():
    r = client.post("/whatsapp", content="Body=&From=whatsapp%3A%2B91999", headers=HEAD)
    assert "Please send the message" in r.text


def test_engine_crash_still_replies(monkeypatch):
    monkeypatch.setattr(webhook, "analyze_message", lambda text: ANALYSIS)

    def boom(**kw):
        raise RuntimeError("db down")
    monkeypatch.setattr(webhook, "evaluate_risk", boom)
    r = client.post("/whatsapp", content=SCAM, headers=HEAD)
    assert r.status_code == 200 and "1930" in r.text and "Do NOT click" in r.text
