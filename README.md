

# Steps to start the code

---

## 📁 1. Clone the Repository

```bash
git clone https://github.com/arthexai/Meditation-reminder.git
cd Meditation-reminder
````

---

## 📋 2. Prepare `recipients.csv`

Create a file named `recipients.csv` in the project root directory with the following columns:

| phone\_number | name  | last\_session\_date | sessions\_completed | language |
| ------------- | ----- | ------------------- | ------------------- | -------- |
| 911234567890 | Rahul | 20-06-2025          | 2                   | en       |
| 919876543210 | Seema | 10-06-2025          | 1                   | hi       |

* `phone_number`: Must include country code (`91` for India, etc.).
* `language`: Either `en` for English or `hi` for Hindi.
* `last_session_date`: Date in `DD-MM-YYYY` format.
* `sessions_completed`: Integer count of sessions already completed.

---

## 🔐 3. Create `.env` File

Create a `.env` file in the root folder (same location as `main.py`) and paste the following content:

```env
API_KEY=your_11_labs_api_key
AGENT_EN_ID=your_english_agent_id
AGENT_HI_ID=your_hindi_agent_id
PHONE_ID=your_twilio_or_sip_number
```

---

## 📦 4. Install Dependencies

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

## 🚀 5. Run the Script

```bash
python main.py
```

The script will:

* Load your API keys and agent IDs from `.env`
* Read each row from `recipients.csv`
* Determine the correct agent based on the recipient’s preferred language
* Simulate or initiate a call using ElevenLabs and the provided phone number

---

## 🧠 Notes & Tips

* Make sure your `.csv` uses UTF-8 encoding and no extra whitespace.
* Make sure in the `.csv` file, phone_number data is in Number format. If not, right click on it, Go to Format Cells..., select Number and make decimal places 0. 
* Ensure your ElevenLabs and Twilio (or SIP) accounts are set up correctly and are capable of placing outbound calls.
* Add any additional fields or validations to `main.py` as needed.

---

## ✅ Checklist Before Running

* [x] `.env` file created and filled with valid values
* [x] `recipients.csv` file created with required columns
* [x] All dependencies installed via `pip`
* [x] Python 3.8+ environment

---

