"""Run from the repo root:  python -m pytest tests/test_translator.py"""
import pytest
from app.services.translator import build_reply, HEADER, SCAM_TYPE, TACTIC, ACTION

ANALYSIS = {"scam_type": "fake_kyc", "impersonated_org": "SBI",
            "tactics": ["urgency", "secrecy", "authority"], "explanation": "Fake bank message.",
            "language": "en"}


def test_high_english():
    r = build_reply("high", ANALYSIS)
    assert "DANGER" in r and "SBI" in r and "1930" in r and "Chakshu" in r
    assert "It rushes you." in r and "Fake bank message." in r


@pytest.mark.parametrize("lang", ["en", "ta", "hi"])
def test_high_has_1930_in_every_language(lang):
    assert "1930" in build_reply("high", ANALYSIS, lang=lang)


def test_tamil_and_hindi_use_their_script():
    assert "மோசடி" in build_reply("high", ANALYSIS, lang="ta")
    assert "धोखाधड़ी" in build_reply("high", ANALYSIS, lang="hi")


def test_tamil_reply_has_no_english_explanation():
    assert "Fake bank message." not in build_reply("high", ANALYSIS, lang="ta")


def test_language_follows_analysis_and_tanglish_gets_tamil():
    assert "மோசடி" in build_reply("high", {**ANALYSIS, "language": "tanglish"})
    assert "धोखाधड़ी" in build_reply("high", {**ANALYSIS, "language": "hi"})
    assert "DANGER" in build_reply("high", {**ANALYSIS, "language": "fr"})   # unknown -> English


def test_safe_is_short_and_has_no_scam_lines():
    r = build_reply("safe", {"scam_type": "none", "tactics": []}, lang="en")
    assert "SAFE" in r and "rushes" not in r


def test_unknown_inputs_do_not_crash():
    assert build_reply("weird", None)
    assert build_reply("high", {"scam_type": "made_up", "tactics": ["x"]})


def test_every_template_has_all_three_languages():
    for table in (HEADER, SCAM_TYPE, TACTIC, ACTION):
        for key, langs in table.items():
            assert set(langs) == {"en", "ta", "hi"}, key


def test_reply_fits_whatsapp_limit():
    assert len(build_reply("high", ANALYSIS, lang="ta")) < 1600
