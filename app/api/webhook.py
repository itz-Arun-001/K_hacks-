"""webhook.py - Twilio WhatsApp webhook (Person 1).
Chain: message -> extract facts -> Gemini analysis -> Arun's evaluate_risk -> translator -> reply
"""
from urllib.parse import parse_qs

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session
from twilio.twiml.messaging_response import MessagingResponse

from app.database import get_db
from app.services.extractor import extract
from app.services.llm_analyzer import analyze_message
from app.services.risk_engine import evaluate_risk
from app.services.translator import build_reply

router = APIRouter()

HELP = ("Please send the message, link, phone number or UPI ID you want me to check.\n"
        "Voice notes will be supported soon.")
ERROR = ("Sorry, I could not check this right now.\n"
         "Do NOT click links or send money.\n"
         "Lost money? Call 1930.")


async def get_form(request: Request):
    """Twilio sends form data. Parsed by hand so no extra package is needed."""
    return parse_qs((await request.body()).decode("utf-8"))


def twiml(text):
    resp = MessagingResponse()                  # Twilio expects TwiML (XML) back
    resp.message(text)
    return Response(content=str(resp), media_type="application/xml")


@router.post("/whatsapp")
def whatsapp(form: dict = Depends(get_form), db: Session = Depends(get_db)):
    text = form.get("Body", [""])[0].strip()    # message the user sent
    sender = form.get("From", [""])[0]          # e.g. whatsapp:+9198xxxxxxxx
    print(f"[whatsapp] From {sender}: {text[:80]}")

    if not text:
        return twiml(HELP)

    try:
        entities = extract(text)                # L2: links, phones, UPI IDs, amounts
        analysis = analyze_message(text)        # L2: Gemini scam tags (or fallback)
        result = evaluate_risk(                 # L3: Arun's risk engine
            user_id=sender,
            message_type="text",
            text=text,
            entities=entities,
            scam_tags={"scam_type": analysis["scam_type"],
                       "confidence": analysis["confidence"],
                       "tactics": analysis["tactics"]},
            db=db,
        )
        print(f"[whatsapp] level={result['level']} score={result['score']} "
              f"llm={analysis['source']}")
        return twiml(build_reply(result["level"], analysis))   # L1: reply in user's language
    except Exception as e:                      # never leave the user without a reply
        print(f"[whatsapp] ERROR: {e}")
        return twiml(ERROR)
