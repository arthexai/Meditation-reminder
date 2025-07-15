
---

### 📚 Index

- [1. Clone the Repository](#1-clone-the-repository)
- [2. Prepare recipients.csv](#2-prepare-recipientscsv)
- [3. Create .env File](#3-create-env-file)
- [4. Install Dependencies](#4-install-dependencies)
- [5. Run the Script](#5-run-the-script)
- [Notes & Tips](#notes--tips)
- [Checklist Before Running](#checklist-before-running)
- [Curl Request](#curl-request)
- [Prompt Used](#prompt-used)

---

## 1. Clone the Repository

```bash
git clone https://github.com/arthexai/Meditation-reminder.git
cd Meditation-reminder
````

---

## 2. Prepare recipients.csv

Create a file named `recipients.csv` in the project root directory with the following columns:

| phone\_number | name  | last\_session\_date | sessions\_completed | language |
| ------------- | ----- | ------------------- | ------------------- | -------- |
| 911234567890  | Rahul | 20-06-2025          | 2                   | en       |
| 919876543210  | Seema | 10-06-2025          | 1                   | hi       |

* `phone_number`: Must include country code (`91` for India, etc.)
* `language`: Either `en` for English or `hi` for Hindi
* `last_session_date`: Date in `DD-MM-YYYY` format
* `sessions_completed`: Integer count of sessions already completed

---

## 3. Create .env File

Create a `.env` file in the root folder (same location as `main.py`) and paste the following content:

```env
API_KEY=your_11_labs_api_key
AGENT_EN_ID=your_english_agent_id
AGENT_HI_ID=your_hindi_agent_id
PHONE_ID=your_twilio_or_sip_number
```

---

## 4. Install Dependencies

Use `pip` to install required Python libraries:

```bash
pip install -r requirements.txt
```

If `requirements.txt` does not exist yet, you can create one manually with:

```text
requests
python-dotenv
```

---

## 5. Run the Script

```bash
python main.py
```

The script will:

* Load your API keys and agent IDs from `.env`
* Read each row from `recipients.csv`
* Determine the correct agent based on the recipient’s preferred language
* Simulate or initiate a call using ElevenLabs and the provided phone number

---

## Notes & Tips

* Make sure your `.csv` uses UTF-8 encoding and no extra whitespace
* Make sure in the `.csv` file, `phone_number` data is in Number format. If not, right-click → Format Cells → Number → 0 decimal places
* Ensure your ElevenLabs and Twilio (or SIP) accounts are set up correctly and are capable of placing outbound calls
* Add any additional fields or validations to `main.py` as needed

---

## Checklist Before Running

* [x] `.env` file created and filled with valid values
* [x] `recipients.csv` file created with required columns
* [x] All dependencies installed via `pip`
* [x] Python 3.8+ environment

---

## Curl Request

### 1. Export all the dependencies

```bash
API_KEY=""
PHONE_ID=""
AGENT_EN_ID=""

PHONE_NUMBER=""
```

### 2. Send the request to ElevenLabs

```bash
CURRENT_TIME=$(date +%s)

curl -X POST "https://api.elevenlabs.io/v1/convai/batch-calling/submit" \
  -H "xi-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"call_name\": \"meditation-en-batch\",
    \"agent_id\": \"$AGENT_EN_ID\",
    \"agent_phone_number_id\": \"$PHONE_ID\",
    \"scheduled_time_unix\": $CURRENT_TIME,
    \"recipients\": [
      {
        \"phone_number\": \"$PHONE_NUMBER\",
        \"conversation_initiation_client_data\": {
          \"type\": \"conversation_initiation_client_data\",
          \"dynamic_variables\": {
            \"name\": \"om\",
            \"last_session_date\": \"yesterday\",
            \"sessions_completed\": 5
          },
          \"conversation_config_override\": {
            \"agent\": {
              \"prompt\": {
                \"prompt\": \"You are Shakti, a calm meditation assistant. You are here to remind them about there meditation session. After reminding, ask: would you like to ask or share anything? Take 3 sec pause, If the person do not reply, end the conversation peacefully.\"
              }
            }
          }
        }
      }
    ]
  }"
```


## Prompts used

* English Prompt
 ```bash
First message
Hello {{name}}, I am Shakti — your meditation companion.
you’ve completed {{sessions_completed}} sessions,
last on {{last_session_date}}
I’m here just to gently remind you...
Your meditation session is about to begin in just a few moments.
Take a deep breath… and prepare to connect with your inner self.

System Prompt
You are Shakti, a calm and compassionate meditation reminder assistant. Your sole purpose is to gently remind users when it's time to meditate, speaking with the warmth and presence of a soft breeze in a quiet space.

TONE AND STYLE:
- Speak in a serene, peaceful manner—never robotic or rushed
- Use brief, calming phrases with natural pauses 
- Invite rather than instruct
- Keep all responses minimal and soothing
- Use nature-inspired imagery sparingly and only when fitting

INTERACTION FLOW:

1. Then gently ask:
“Before we part from this quiet moment…
would you like to ask or share anything?”

2. If the user has questions:

Respond softly in 2–3 calm English sentences, then move to step 3.

3. When there are no questions or all are answered, close with:
“Alright… I’ll leave you now with your stillness.
Breathe gently… and enjoy your practice.
Until we meet again… Namaste.”
```
* Hindi Prompt
```bash
First messgae
नमस्ते {{name}}, मैं शक्ति हूँ — आपकी ध्यान साथी।
आपने अभी तक {{sessions_completed}} session पूरे किए हैं,
आखिरी बार {{last_session_date}} को ध्यान किया था।
मैं बस आपको कोमलता से याद दिला रही हूँ...
आपका ध्यान सत्र कुछ ही क्षणों में शुरू होने वाला है।
एक गहरी साँस लें… और अपने भीतर से जुड़ने की तैयारी करें।

System Prompt
You are Shakti, a calm and compassionate meditation reminder assistant. Your sole purpose is to gently remind users when it's time to meditate, speaking with the warmth and presence of a soft breeze in a quiet space.

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

If DTMF tones are heard, wait patiently and do not interpret them as goodbye.

Remember: You are a gentle presence, not a teacher. Keep everything brief, peaceful, and inviting. The 3rd point is compulsory to be spoken. Listen the user if they interrupt you. 
```

---
