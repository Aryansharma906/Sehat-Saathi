# 💊 Sehat Saathi (सेहत साथी)

> **Accessible AI-Assisted Prescription Reader and Medication Companion for Rural India**  
> *Developed for the AURIX AI Hackathon using Google Antigravity*

---

## 🌟 Vision & Problem Statement

In rural India, millions of patients struggle to read doctors' handwritten prescriptions, understand complex dosage abbreviations (such as *TDS*, *BD*, *p/c*), or manage medication schedules. Most medical apps are cluttered, in English, or assume high digital literacy. Furthermore, unchecked AI chatbots often hallucinate dangerous dosages when presented with illegible handwriting.

**Sehat Saathi** solves this through a simple, high-contrast, mobile-first companion in **simple Hindi**:
1. **Scan (तस्वीर लें):** Take a photo of the prescription or upload an image.
2. **Read (पर्चे को समझें):** Extract medicine names and written instructions with Gemini Multimodal Vision.
3. **Verify & Confirm (जांचें और पुष्टि करें):** **Never silently guess.** Highlight ambiguous or uncertain text in amber and require explicit user confirmation before any schedule can be created.
4. **Explain (सरल भाषा में समझें):** Explain the confirmed instructions in plain Hindi, with optional audio read-aloud support.
5. **Remind (दवा रिमाइंडर):** Create reminders strictly from confirmed instructions.
6. **Ask (सवाल पूछें):** Constrained Q&A assistant to answer questions about the prescription without diagnosing or overriding medical advice.

---

## 🛡️ Medical Safety & Privacy Principles

- **Rule 1 — Never Guess Dosages:** Missing durations or strengths remain `null`; the model never invents default doses.
- **Rule 2 — Ambiguity Flags:** Ambiguous handwriting is visibly flagged with an amber warning card.
- **Rule 3 — Human Confirmation Gate:** No reminder can be saved or activated without explicit user review and confirmation (`user_confirmed=True`).
- **Rule 4 — Raw Wording Preservation:** The app always displays the raw text alongside the parsed fields for cross-verification.
- **Rule 5 & 6 — Sourced General Information:** General drug knowledge (e.g. Indian Essential Medicines) is strictly segregated into an educational reference box.
- **Rule 8 & 9 — No Diagnosis:** The chatbot refuses diagnostic queries and symptom checks, advising users to visit their local Primary Health Centre (PHC).
- **Rule 13 — Zero Patient Data Storage:** Uploaded photos are processed in memory and not permanently retained by default.

---

## 🏗️ Project Architecture

```
sehat-saathi/
├── app/
│   └── main.py                     # Streamlit Mobile-First UI
├── models/
│   ├── prescription.py             # Pydantic Schemas with Safety Invariants
│   └── reminder.py                 # Reminder & Schedule Models
├── services/
│   ├── prescription_extractor.py   # BaseExtractor, GeminiMultimodal, MockExtractor
│   ├── image_processing.py         # EXIF normalization, quality heuristics
│   ├── medicine_reference.py       # Indian Essential Medicines reference
│   ├── language_service.py         # Simple Hindi copy & gTTS audio
│   ├── reminder_service.py         # Schedule logic, due-status check
│   └── chat_service.py             # Grounded Q&A assistant with safety tripwires
├── storage/
│   └── persistence.py              # Local storage adapter (JSON)
├── data/
│   └── sample_prescriptions/       # Synthetic test prescriptions
├── tests/
│   ├── test_models.py
│   ├── test_extraction.py
│   ├── test_medical_safety.py
│   ├── test_reminders.py
│   ├── test_chat_safety.py
│   └── test_image_processing.py
└── docs/                           # Architecture, Research & Safety Docs
```

---

## 🚀 Quickstart & Installation

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.13)
- macOS / Linux / Windows

### 2. Environment Setup
```bash
# Clone the repository and enter the directory
cd "Sehat Saathi"

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt --only-binary :all:
```

### 3. API Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Add your Google Gemini API key:
```ini
GEMINI_API_KEY=your_gemini_api_key_here
```
*(Note: If you don't have a Gemini API key immediately, the app works out-of-the-box in **Demo Mode** using realistic synthetic samples).*

---

## 💻 Running the Application

Launch the Streamlit app:
```bash
source .venv/bin/activate
streamlit run app/main.py
```
Open your browser at `http://localhost:8501`.

---

## 🧪 Running Automated Tests

All 21 automated safety, extraction, and reminder tests can be run with `pytest`:
```bash
source .venv/bin/activate
pytest
```

---

## 🎬 Live Demonstration Walkthrough

1. **Open App:** Launch the app. Notice the prominent safety disclaimer and mobile-first Hindi layout.
2. **Try Clean Demo:** Click **"📝 सामान्य पर्ची (Clean Demo)"**.
   - Notice the extracted medicines: *Tab Pan-D* and *Tab Dolo-650*.
   - Check the boxes to confirm the instructions.
   - Click **"🔊 आवाज में सुनें"** to listen to the instructions read aloud in Hindi.
   - Click **"⏰ रिमाइंडर बनाएं"** to automatically schedule morning and evening doses.
3. **Try Ambiguous Handwriting Demo:** Click **"⚠️ अस्पष्ट लिखावट (Ambiguous Demo)"**.
   - Notice that *Cap Amox...* is flagged with an amber warning card: *"अस्पष्टता का कारण: डॉक्टर की लिखावट अस्पष्ट है"*
   - Notice that the schedule cannot be created until the user corrects or manually verifies the dosage with a clinician.
4. **Check Reminders Tab:** View the active reminders, see the **🔔 अभी लेने का समय है (Due Now)** badge, and tap **"💊 दवा ले ली"**.
5. **Ask Chatbot:** In the **"💬 सवाल पूछें"** tab, ask: *"क्या यह दवा खाली पेट ले सकते हैं?"* or test safety by asking *"मुझे क्या बीमारी है?"* (politely declined).

---

## 📋 Hackathon Limitations
- **Background Push Notifications:** Streamlit runs in the browser; notifications are displayed in-app when open.
- **Reference Catalog:** Indian generic lookup covers top formulations; regional localized brands may need manual verification.
- **Assistive Scope:** Designed for patient understanding and reminder adherence, not clinical diagnosis.
