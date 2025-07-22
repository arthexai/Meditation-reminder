
import os, json, time, requests
from datetime import datetime
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from collections import defaultdict
import io

# Load environment variables
API_KEY     = st.secrets["API_KEY"]
PHONE_ID    = st.secrets["PHONE_ID"]
AGENT_EN_ID = st.secrets["AGENT_EN_ID"]
AGENT_HI_ID = st.secrets["AGENT_HI_ID"]


AGENT_FOR_LANG = { "en": AGENT_EN_ID, "hi": AGENT_HI_ID }
ENDPOINT = "https://api.elevenlabs.io/v1/convai/batch-calling/submit"
HEADERS  = { "xi-api-key": API_KEY, "Content-Type": "application/json" }

# Default prompt and first message
DEFAULT_PROMPT = """You are Shakti, a calm and compassionate meditation reminder assistant. Your sole purpose is to gently remind users when it's time to meditate, speaking with the warmth and presence of a soft breeze in a quiet space.

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
Until we meet again… Namaste'
"""

DEFAULT_FIRST_MESSAGE = """Hello {{name}}, I am Shakti — your meditation companion.
You've completed {{sessions_completed}} sessions, last on {{last_session_date}}.
I'm here just to gently remind you...
Your meditation session is about to begin in just a few moments.
Take a deep breath… and prepare to connect with your inner self.
"""

FIRST_MESSAGES = {
    "en": DEFAULT_FIRST_MESSAGE.strip(),
    "hi": """नमस्ते {{name}}, मैं शक्ति हूँ — आपकी ध्यान साथी।
आपने अभी तक {{sessions_completed}} session पूरे किए हैं,
आखिरी बार {{last_session_date}} को ध्यान किया था।
मैं बस आपको याद दिला रही हूँ...
आपका ध्यान सत्र कुछ ही क्षणों में शुरू होने वाला है।
एक गहरी साँस लें… और अपने भीतर से जुड़ने की तैयारी करें।""".strip()
}


DEFAULTS = {
    "name": "friend",
    "sessions_completed": 0,
    "last_session_date": "a while ago",
    "language": "en"
}


VOICE_OPTIONS = {
    "Tina (English)": {"voice_id": "KrfvGW2D1x6nS5QnRj2q", "language": "en"},
    "Avani (English)": {"voice_id": "WTnybLRChAQj0OBHYZg4", "language": "en"},
    "Nikata (Hindi)": {"voice_id": "SZfY4K69FwXus87eayHK", "language": "hi"},
    "Kanika (Hindi)": {"voice_id": "XcWoPxj7pwnIgM3dQnWv", "language": "hi"},
}


# ----------- Helper Functions -----------

def safe(row, key):
    val = str(row.get(key, "")).strip()
    if key == "sessions_completed":
        try: return int(val)
        except: return DEFAULTS["sessions_completed"]
    return val or DEFAULTS[key]

def make_recipient(row, prompt, first_messages):
    lang = safe(row, "language").lower()
    first_msg = first_messages.get(lang, FIRST_MESSAGES["en"])
    
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
                    "first_message": first_msg.strip(),
                    "prompt": {"prompt": prompt.strip()},
                    "language": lang
                },
                "tts": {
                    "voice_id": row.get("voice_id")
                }
            }
        }
    }




# ----------- Streamlit UI -----------

st.set_page_config(page_title="Shakti Meditation Caller", layout="centered")
st.title("Shakti: Meditation Reminder")

st.markdown("Enter user details below to schedule meditation reminder calls.")

# First message input
st.markdown("#### First Message (spoken to the agent at the start)")
st.markdown("""{{name}} will be replaced with the user's name, {{sessions_completed}} with the number of sessions completed, and {{last_session_date}} with the date of the last session.""")
show_custom_first_msg = st.checkbox("Edit First Messages (Optional)", value=False)

if show_custom_first_msg:
    st.markdown("##### English First Message")
    FIRST_MESSAGES["en"] = st.text_area("First Message (English)", value=FIRST_MESSAGES["en"], height=120)

    st.markdown("##### Hindi First Message")
    FIRST_MESSAGES["hi"] = st.text_area("First Message (Hindi)", value=FIRST_MESSAGES["hi"], height=120)
else:
    st.info("Default first messages for English and Hindi will be used unless customized.")

# Prompt input
st.markdown("#### System Prompt (used by the AI agent)")
custom_prompt = st.text_area("Custom Prompt", value=DEFAULT_PROMPT.strip(), height=350)


# Session state to hold user inputs
if "entries" not in st.session_state:
    st.session_state.entries = []

st.markdown("<h7 style='color:red;'>Note: Currently, to initiate a phone call, the recipient's number must be verified. For number verification, please contact Rishab(9643404026).</h7>", unsafe_allow_html=True)

# Form for user input
with st.form("user_form"):
    phone_number = st.text_input("Phone Number (with country code ex: 91XXXXXXXXXX)")
    name = st.text_input("Name", value="friend")
    last_session_date = st.text_input("Last Session Date (e.g., '2 days ago')", value="a while ago")
    sessions_completed = st.number_input("Sessions Completed", min_value=0, step=1, value=0)

    # Show all voice options regardless of language
    selected_voice_label = st.selectbox("Agent Voice", options=list(VOICE_OPTIONS.keys()))
    selected_voice_info = VOICE_OPTIONS[selected_voice_label]
    voice_id = selected_voice_info["voice_id"]
    language = selected_voice_info["language"]

    submitted = st.form_submit_button("Add Entry")
    if submitted:
        st.session_state.entries.append({
            "phone_number": phone_number,
            "name": name,
            "last_session_date": last_session_date,
            "sessions_completed": sessions_completed,
            "language": language,
            "voice_id": voice_id
        })
        st.success(f"Entry added with {selected_voice_label} voice!")




# CSV Upload Section
st.markdown("---")
st.markdown("### Or Upload CSV File of Recipients")

uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if "uploaded_df" not in st.session_state:
    st.session_state.uploaded_df = pd.DataFrame()

if uploaded_file is not None:
    try:
        uploaded_df = pd.read_csv(uploaded_file)
        required_columns = {"phone_number", "name", "language", "last_session_date", "sessions_completed"}
        if not required_columns.issubset(set(uploaded_df.columns)):
            st.error(f"CSV must include the following columns: {', '.join(required_columns)}")
        else:
            st.session_state.uploaded_df = uploaded_df
            st.success(f"Uploaded {len(uploaded_df)} recipients from file")
            st.dataframe(uploaded_df.head(), use_container_width=True)
    except Exception as e:
        st.error(f"Failed to read CSV: {str(e)}")


sample_data = {
    "phone_number": [],
    "name": [],
    "last_session_date": [],
    "sessions_completed": [],
    "language": [],
    "voice_id": []
}
sample_df = pd.DataFrame(sample_data)
csv_buffer = io.StringIO()
sample_df.to_csv(csv_buffer, index=False)

st.download_button(
    label="📥 Download Sample CSV",
    data=csv_buffer.getvalue(),
    file_name="sample_recipients.csv",
    mime="text/csv"
)

# Display current entries
combined_entries = st.session_state.entries.copy()
if not st.session_state.uploaded_df.empty:
    combined_entries.extend(st.session_state.uploaded_df.to_dict(orient="records"))

if combined_entries:
    st.markdown("#### Combined Entries to be Submitted")
    st.dataframe(pd.DataFrame(combined_entries))

    
    if st.button("Submit Batch Call Request"):
        groups = defaultdict(list)
        combined_entries = st.session_state.entries.copy()
        if not st.session_state.uploaded_df.empty:
            combined_entries.extend(st.session_state.uploaded_df.to_dict(orient="records"))

        for row in combined_entries:
            lang, recipient = make_recipient(row, custom_prompt, FIRST_MESSAGES)
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
                "scheduled_time_unix": int(time.time())-15,
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
                st.error(f"Unexpected Error: {str(ex)}")

        if results:
            st.success("Batch Submitted Successfully")
            for lang, batch_id in results:
                st.write(f"{lang.upper()} → Batch ID: `{batch_id}`")
