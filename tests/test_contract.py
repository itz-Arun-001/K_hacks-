"""Checks that the database and the dummy engine follow the agreed contract."""
import os
os.environ["DATABASE_URL"] = "sqlite:///./test_surakshit.db"  # throwaway DB for tests

import pytest

from app.database import Event, FlaggedEntity, User, get_session, init_db
from app.services.risk_engine import risk_check


@pytest.fixture(autouse=True, scope="module")
def setup_db():
    init_db()
    yield
    os.remove("test_surakshit.db")


def _request(**overrides):
    base = {
        "user_id": None, "type": "text", "text": "You won a lottery!",
        "entities": {"links": [], "phones": [], "upi_ids": [], "amounts": []},
        "scam_tags": [],
    }
    base.update(overrides)
    return base


def test_engine_returns_contract_shape():
    result = risk_check(_request())
    assert set(result) == {"score", "level", "reasons", "engine_version"}
    assert 0.0 <= result["score"] <= 1.0
    assert result["level"] in {"safe", "suspicious", "high"}
    assert isinstance(result["reasons"], list) and result["reasons"]


def test_engine_rejects_bad_input():
    with pytest.raises(ValueError):
        risk_check(_request(type="banana"))
    with pytest.raises(ValueError):
        risk_check({"type": "text"})


def test_engine_writes_audit_event():
    risk_check(_request())
    with get_session() as s:
        assert s.query(Event).filter_by(event_type="verdict_created").count() >= 1


def test_tables_work_and_blocklist_is_unique():
    with get_session() as s:
        s.add(User(phone="+910000000001", name="Test Amma", language="ta"))
        s.add(FlaggedEntity(kind="upi", value="kbc.claim@upi", source="user_report"))
        s.commit()
        assert s.query(User).count() == 1
        s.add(FlaggedEntity(kind="upi", value="kbc.claim@upi"))
        with pytest.raises(Exception):
            s.commit()  # duplicate (kind, value) must be rejected
