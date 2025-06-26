import os, csv, json, time, requests
from datetime import datetime
from collections import defaultdict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the variables
API_KEY   = os.getenv("API_KEY")
AGENT_EN_ID = os.getenv("AGENT_EN_ID")
AGENT_HI_ID = os.getenv("AGENT_HI_ID")
PHONE_ID  = os.getenv("PHONE_ID")
CSV_FILE = "recipients.csv"
TIMEOUT_SECS  = 30

# ─────── FALLBACKS ───────
DEFAULTS = {
    "name": "friend",
    "sessions_completed": 0,
    "last_session_date": "a while ago",
    "language": "en"
}

# ─────── HELPERS ───────
def safe(row, key):
    val = row.get(key, "").strip()
    return int(val) if key == "sessions_completed" else (val or DEFAULTS[key])

def make_recipient(row):
    lang = safe(row, "language").lower()
    return lang, {
        "phone_number": row["phone_number"],
        "conversation_initiation_client_data": {
            "type": "conversation_initiation_client_data",
            "dynamic_variables": {
                "name": safe(row, "name"),
                "last_session_date": safe(row, "last_session_date"),
                "sessions_completed": safe(row, "sessions_completed")
            }
        }
    }

# ─────── PROCESS CSV ───────
groups = defaultdict(list)
with open(CSV_FILE, newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        lang, recipient = make_recipient(row)
        groups[lang].append(recipient)

# ─────── LANGUAGE → AGENT ID ───────
AGENT_FOR_LANG = {
    "en": AGENT_EN_ID,
    "hi": AGENT_HI_ID
}

# ─────── SUBMIT PER AGENT ───────
ENDPOINT = "https://api.elevenlabs.io/v1/convai/batch-calling/submit"
HEADERS = {"xi-api-key": API_KEY, "Content-Type": "application/json"}

for lang, recipients in groups.items():
    agent_id = AGENT_FOR_LANG.get(lang)
    if not agent_id:
        print(f"⚠️  Skipping unsupported language: {lang}")
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
    print(f"✅  {lang.upper()} batch submitted → ID: {r.json()['id']}")