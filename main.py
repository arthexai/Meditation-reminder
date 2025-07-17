
import os, json, time, requests
from datetime import datetime
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from collections import defaultdict

# Load environment variables
API_KEY     = st.secrets["API_KEY"]
PHONE_ID    = st.secrets["PHONE_ID"]
AGENT_EN_ID = st.secrets["AGENT_EN_ID"]
AGENT_HI_ID = st.secrets["AGENT_HI_ID"]


AGENT_FOR_LANG = { "en": AGENT_EN_ID, "hi": AGENT_HI_ID }
ENDPOINT = "https://api.elevenlabs.io/v1/convai/batch-calling/submit"
HEADERS  = { "xi-api-key": API_KEY, "Content-Type": "application/json" }

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

# ---------------- Helper Functions ---------------- #

def safe(row, key):
    val = str(row.get(key, "")).strip()
    if key == "sessions_completed":
        try: return int(val)
        except: return DEFAULTS["sessions_completed"]
    return val or DEFAULTS[key]

def make_recipient(row, en_prompt=None, hi_prompt=None):
    lang = safe(row, "language").lower()

    if lang == "en" and en_prompt:
        prompt = en_prompt
    elif lang == "hi" and hi_prompt:
        prompt = hi_prompt
    else:
        prompt = SYSTEM_PROMPT.get(lang, SYSTEM_PROMPT["en"])

    return lang, {
        "phone_number": str(row["phone_number"]),
        "conversation_initiation_client_data": {
            "type": "conversation_initiation_client_data",
            "dynamic_variables": {
                "name": safe(row, "name"),
                "last_session_date": safe(row, "last_session_date"),
                "sessions_completed": safe(row, "sessions_completed")
            },
            "conversation_config_override": {
                "agent": {
                    "prompt": { "prompt": prompt }
                }
            }
        }
    }

# ---------------- Streamlit UI ---------------- #

st.set_page_config(page_title="Shakti Meditation Caller", layout="centered")
st.title("Shakti: Meditation Reminder")

st.markdown("""
Upload a CSV file with the following columns:  
- `phone_number`, `name`, `sessions_completed`, `last_session_date`, `language`
""")

# Custom prompt inputs
st.markdown("### Customize System Prompts")
custom_en_prompt = st.text_area("🗣️ English Prompt (Optional)", value="", height=200, placeholder="Leave blank to use default English prompt...")
custom_hi_prompt = st.text_area("🗣️ Hindi Prompt (Optional)", value="", height=200, placeholder="Leave blank to use default Hindi prompt...")

sample_csv = """phone_number,name,last_session_date,sessions_completed,language
"""
# File Upload
uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

st.download_button(
    label="Download Sample CSV",
    data=sample_csv,
    file_name="sample.csv",
    mime="text/csv"
)


if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("Preview Uploaded Data")
    st.dataframe(df)

    if st.button("Submit Batch Call Request"):
        groups = defaultdict(list)

        for _, row in df.iterrows():
            lang, recipient = make_recipient(row, en_prompt=custom_en_prompt, hi_prompt=custom_hi_prompt)
            groups[lang].append(recipient)

        results = []
        for lang, recipients in groups.items():
            agent_id = AGENT_FOR_LANG.get(lang)
            if not agent_id:
                st.warning(f"No agent configured for language: {lang}")
                continue

            payload = {
                "call_name": f"meditation-{lang}-{datetime.utcnow().isoformat(timespec='seconds')}",
                "agent_id": agent_id,
                "agent_phone_number_id": PHONE_ID,
                "scheduled_time_unix": int(time.time()),
                "recipients": recipients
            }

            try:
                r = requests.post(ENDPOINT, headers=HEADERS, data=json.dumps(payload), timeout=30)
                r.raise_for_status()
                batch_id = r.json().get("id", "N/A")
                results.append((lang, batch_id))
            except requests.exceptions.HTTPError as e:
                st.error(f"HTTP Error for {lang.upper()}: {e}")
                st.code(json.dumps(payload, indent=2), language="json")
            except Exception as ex:
                st.error(f" Unexpected Error: {str(ex)}")

        if results:
            st.success("Batch Submitted Successfully!")
            for lang, batch_id in results:
                st.write(f"`{lang.upper()}` → Batch ID: `{batch_id}`")
