
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
export XI_API_KEY="pk_..."          # ElevenLabs API key
export AGENT_ID="agent_..."         # The agent you want to use (en or hi)
export PHONE_ID="PN..."             # Your Twilio/SIP number ID
export RECIPIENTS_JSON='[
  {
    "phone_number": "+911234567890",
    "conversation_initiation_client_data": {
      "type": "conversation_initiation_client_data",
      "dynamic_variables": {
        "name": "Rahul",
        "last_session_date": "2025-06-20",
        "sessions_completed": 2
      }
    }
  },
  {
    "phone_number": "+919876543210",
    "conversation_initiation_client_data": {
      "type": "conversation_initiation_client_data",
      "dynamic_variables": {
        "name": "Seema",
        "last_session_date": "2025-06-10",
        "sessions_completed": 1
      }
    }
  }
]'
```

### 2. Send the request to ElevenLabs

```bash
curl -X POST "https://api.elevenlabs.io/v1/convai/batch-calling/submit" \
  -H "xi-api-key: ${XI_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
        "call_name": "meditation-en-'"$(date -u +"%Y-%m-%dT%H:%M:%SZ")"'",
        "agent_id": "'"${AGENT_ID}"'",
        "agent_phone_number_id": "'"${PHONE_ID}"'",
        "scheduled_time_unix": '"$(date +%s)"',
        "recipients": '"${RECIPIENTS_JSON}"'
      }'
```

---

