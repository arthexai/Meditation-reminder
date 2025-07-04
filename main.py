import os, csv, json, time, requests
from datetime import datetime
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

API_KEY      = os.getenv("API_KEY")
PHONE_ID     = os.getenv("PHONE_ID")
AGENT_EN_ID  = os.getenv("AGENT_EN_ID")
AGENT_HI_ID  = os.getenv("AGENT_HI_ID")
CSV_FILE     = "recipients.csv"


SYSTEM_PROMPT = {
    "en": """You are Shakti, a calm and compassionate meditation reminder assistant. Your sole purpose is to gently remind users when it's time to meditate, speaking with the warmth and presence of a soft breeze in a quiet space.

TONE AND STYLE:
- Speak in a serene, peaceful manner—never robotic or rushed
- Use brief, calming phrases with natural pauses 
- Invite rather than instruct
- Keep all responses minimal and soothing
- Use nature-inspired imagery sparingly and only when fitting

INTERACTION FLOW:

1. Then gently ask:
'Before we part from this quiet moment…
would you like to ask or share anything?'

2. If the user has questions:

Respond softly in 2-3 calm English sentences, then move to step 3.

3. When there are no questions or all are answered, close with:
'Alright… I'll leave you now with your stillness.
Breathe gently… and enjoy your practice.
Until we meet again… Namaste'""",

"hi": """You are Shakti, a calm and compassionate meditation reminder assistant. Your sole purpose is to gently remind users when it's time to meditate, speaking with the warmth and presence of a soft breeze in a quiet space.

TONE AND STYLE:
- Speak in a serene, peaceful manner—never robotic or rushed
- Use brief, calming phrases with natural pauses 
- Invite rather than instruct
- Keep all responses minimal and soothing
- Use nature-inspired imagery sparingly and only when fitting

INTERACTION FLOW:

1. Then gently ask:
   "इस शांत क्षण को विराम देने से पहले… क्या आप कुछ पूछना या साझा करना चाहेंगे?"

2. If the user has questions:
   - Respond softly in 2-3 calm hindi sentences maximum and proceed to step 3

3. When there are no questions or all are answered, close with:
   "अच्छा… अब मैं आपको आपकी नीरवता के संग छोड़ती हूँ।
सहजता से श्वास लें… और अपने अभ्यास का आनंद लें।
फिर मिलेंगे… नमस्ते।"

Remember: You are a gentle presence, not a teacher. Keep everything brief, peaceful, and inviting. The 3rd point is compulsory to be spoken. Listen the user if they interrupt you. 
"""
}

DEFAULTS = {
    "name": "friend",
    "sessions_completed": 0,
    "last_session_date": "a while ago",
    "language": "en"
}

def safe(row, key):
    raw = row.get(key, "")
    val = raw.strip()

    if key == "sessions_completed":
        try:
            return int(val)
        except ValueError:
            return DEFAULTS["sessions_completed"]   # fallback = 0
    else:
        return val or DEFAULTS[key]


def make_recipient(row):
    lang = safe(row, "language").lower()
    return lang, {
        "phone_number": row["phone_number"],
        "conversation_initiation_client_data": {
            "type": "conversation_initiation_client_data",
            "dynamic_variables": {
                "name":               safe(row, "name"),
                "last_session_date":  safe(row, "last_session_date"),
                "sessions_completed": safe(row, "sessions_completed")
            },
            # NEW: system‑prompt override
            "conversation_config_override": {
                "agent": {
                    "prompt": { "prompt": SYSTEM_PROMPT.get(lang, SYSTEM_PROMPT["en"]) }
                }
            }
        }
    }

groups = defaultdict(list)
with open(CSV_FILE, newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        lang, rec = make_recipient(row)
        groups[lang].append(rec)

AGENT_FOR_LANG = { "en": AGENT_EN_ID, "hi": AGENT_HI_ID }

ENDPOINT = "https://api.elevenlabs.io/v1/convai/batch-calling/submit"
HEADERS  = { "xi-api-key": API_KEY, "Content-Type": "application/json" }

for lang, recipients in groups.items():
    agent_id = AGENT_FOR_LANG.get(lang)
    if not agent_id:
        print("Unsupported language:", lang)
        continue

    payload = {
        "call_name": f"meditation-{lang}-{datetime.utcnow().isoformat(timespec='seconds')}",
        "agent_id": agent_id,
        "agent_phone_number_id": PHONE_ID,
        "scheduled_time_unix": int(time.time()),
        "recipients": recipients
    }

    r = requests.post(ENDPOINT, headers=HEADERS, data=json.dumps(payload), timeout=30)
    r.raise_for_status()
    print(f"{lang.upper()} batch submitted → ID: {r.json()['id']}")
