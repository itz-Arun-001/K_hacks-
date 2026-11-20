"""translator.py - reply writer (Person 1). English / Tamil / Hindi, short lines, large-text friendly.
build_reply(level, analysis, lang=None) -> str
  level    : "safe" | "suspicious" | "high"   (from Arun's evaluate_risk)
  analysis : dict from llm_analyzer.analyze_message()
  lang     : "en" | "ta" | "hi"; if None it follows analysis["language"]
Fixed templates on purpose: the wording is predictable and a Tamil/Hindi speaker can review it.
"""

LANG_MAP = {"en": "en", "ta": "ta", "hi": "hi", "tanglish": "ta"}   # anything else -> English

HEADER = {
    "safe": {"en": "✅ LOOKS SAFE", "ta": "✅ பாதுகாப்பாகத் தெரிகிறது", "hi": "✅ सुरक्षित लगता है"},
    "suspicious": {"en": "⚠️ BE CAREFUL", "ta": "⚠️ கவனமாக இருங்கள்", "hi": "⚠️ सावधान रहें"},
    "high": {"en": "🚨 DANGER - THIS IS A SCAM", "ta": "🚨 ஆபத்து - இது மோசடி",
             "hi": "🚨 खतरा - यह धोखाधड़ी है"},
}

SCAM_TYPE = {
    "fake_kyc": {"en": "This looks like a fake KYC or bank message.",
                 "ta": "இது போலி KYC / வங்கி செய்தி போல உள்ளது.",
                 "hi": "यह नकली KYC / बैंक संदेश लगता है."},
    "lottery": {"en": "This looks like a fake lottery or prize message.",
                "ta": "இது போலி லாட்டரி / பரிசு செய்தி போல உள்ளது.",
                "hi": "यह नकली लॉटरी / इनाम का संदेश लगता है."},
    "fake_customer_care": {"en": "This looks like a fake customer care call.",
                           "ta": "இது போலி வாடிக்கையாளர் சேவை அழைப்பு போல உள்ளது.",
                           "hi": "यह नकली कस्टमर केयर कॉल लगता है."},
    "otp_phishing": {"en": "Someone is trying to get your OTP or PIN.",
                     "ta": "யாரோ உங்கள் OTP அல்லது PIN-ஐ பெற முயல்கிறார்கள்.",
                     "hi": "कोई आपका OTP या PIN लेने की कोशिश कर रहा है."},
    "investment": {"en": "This looks like a fake investment offer.",
                   "ta": "இது போலி முதலீட்டு வாய்ப்பு போல உள்ளது.",
                   "hi": "यह नकली निवेश ऑफर लगता है."},
    "family_impersonation": {"en": "Someone may be pretending to be your family.",
                             "ta": "உங்கள் குடும்பத்தினர் போல யாரோ நடிக்கலாம்.",
                             "hi": "कोई आपके परिवार का बनकर बात कर सकता है."},
    "job_offer": {"en": "This looks like a fake job offer.",
                  "ta": "இது போலி வேலை வாய்ப்பு போல உள்ளது.",
                  "hi": "यह नकली नौकरी का ऑफर लगता है."},
    "other_scam": {"en": "This message has signs of a scam.",
                   "ta": "இந்த செய்தியில் மோசடி அறிகுறிகள் உள்ளன.",
                   "hi": "इस संदेश में धोखाधड़ी के संकेत हैं."},
}

TACTIC = {
    "urgency": {"en": "It rushes you.", "ta": "அவசரப்படுத்துகிறது.", "hi": "यह आपको जल्दबाजी में डालता है."},
    "secrecy": {"en": "It asks you to keep it secret.", "ta": "ரகசியமாக வைக்கச் சொல்கிறது.",
                "hi": "यह बात छिपाने को कहता है."},
    "authority": {"en": "It pretends to be a bank or government.",
                  "ta": "வங்கி அல்லது அரசு போல நடிக்கிறது.",
                  "hi": "यह बैंक या सरकार होने का नाटक करता है."},
    "fear": {"en": "It tries to scare you.", "ta": "பயமுறுத்த முயல்கிறது.",
             "hi": "यह आपको डराने की कोशिश करता है."},
    "reward": {"en": "It promises money or a prize.", "ta": "பணம் அல்லது பரிசு தருவதாகச் சொல்கிறது.",
               "hi": "यह पैसे या इनाम का लालच देता है."},
    "payment_request": {"en": "It asks you to send money.", "ta": "பணம் அனுப்பச் சொல்கிறது.",
                        "hi": "यह पैसे भेजने को कहता है."},
}

ACTION = {
    "high": {
        "en": "Do NOT click any link.\nDo NOT send money.\nDo NOT share OTP or PIN.\n\n"
              "Lost money? Call 1930 now.\nReport the number at Chakshu (sancharsaathi.gov.in).",
        "ta": "எந்த லிங்கையும் கிளிக் செய்யாதீர்கள்.\nபணம் அனுப்பாதீர்கள்.\nOTP / PIN யாரிடமும் சொல்லாதீர்கள்.\n\n"
              "பணம் போய்விட்டதா? உடனே 1930-க்கு அழைக்கவும்.\nChakshu-வில் புகார் செய்யவும் (sancharsaathi.gov.in).",
        "hi": "कोई लिंक न खोलें.\nपैसे न भेजें.\nOTP या PIN किसी को न बताएं.\n\n"
              "पैसे चले गए? अभी 1930 पर कॉल करें.\nChakshu पर शिकायत करें (sancharsaathi.gov.in).",
    },
    "suspicious": {
        "en": "Do not click or pay yet.\nAsk your family first.\nCall your bank on its official number.",
        "ta": "இப்போது கிளிக் செய்யவோ பணம் அனுப்பவோ வேண்டாம்.\nமுதலில் குடும்பத்தினரிடம் கேளுங்கள்.\n"
              "வங்கியின் அதிகாரப்பூர்வ எண்ணில் அழையுங்கள்.",
        "hi": "अभी लिंक न खोलें, पैसे न भेजें.\nपहले परिवार से पूछें.\nबैंक के आधिकारिक नंबर पर कॉल करें.",
    },
    "safe": {
        "en": "No scam signs found.\nStill, never share OTP or PIN.",
        "ta": "மோசடி அறிகுறி எதுவும் இல்லை.\nஆனாலும் OTP / PIN யாரிடமும் சொல்லாதீர்கள்.",
        "hi": "धोखाधड़ी का कोई संकेत नहीं मिला.\nफिर भी OTP या PIN किसी को न बताएं.",
    },
}

ORG_LINE = {"en": "It pretends to be: {}", "ta": "இவர்கள் போல நடிக்கிறது: {}", "hi": "यह इनका नाम लेकर ठगता है: {}"}


def build_reply(level, analysis=None, lang=None):
    analysis = analysis or {}
    level = level if level in HEADER else "suspicious"
    lang = LANG_MAP.get(lang or analysis.get("language"), "en")

    lines = [HEADER[level][lang], ""]

    if level != "safe":
        scam_line = SCAM_TYPE.get(analysis.get("scam_type"))
        if scam_line:
            lines.append(scam_line[lang])
        org = analysis.get("impersonated_org")
        if org:
            lines.append(ORG_LINE[lang].format(org))
        for tactic in analysis.get("tactics", [])[:3]:
            if tactic in TACTIC:
                lines.append("• " + TACTIC[tactic][lang])
        # Gemini's explanation is English only, so it is used for English replies
        if lang == "en" and analysis.get("explanation"):
            lines += ["", analysis["explanation"]]
        lines.append("")

    lines.append(ACTION[level][lang])
    return "\n".join(lines).strip()
