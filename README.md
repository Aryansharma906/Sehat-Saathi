# 💊 Sehat Saathi (सेहत साथी)

> **Accessible AI-Assisted Prescription Reader and Medication Companion for Rural India & Older Adults**  
> *Developed for the AURIX AI Hackathon using Google Antigravity*

---

## 🌟 Vision & Problem Statement

In rural India, millions of older adults and patients struggle to read doctors' handwritten prescriptions, understand confusing dosage abbreviations (such as *TDS*, *BD*, *p/c*), or manage medication schedules. Most medical apps are cluttered, in English, or assume high digital literacy. Furthermore, unchecked AI chatbots often hallucinate dangerous dosages when presented with illegible handwriting.

**Sehat Saathi** solves this through a simple, high-contrast, mobile-first companion in **simple Hindi**:
1. **Scan (तस्वीर लें):** Take a photo with built-in photography guidance (flat surface, no shadows, 4 corners visible).
2. **Read (पर्चे को समझें):** Extract medicine names and written instructions with Gemini Multimodal Vision.
3. **Verify & Confirm (जांचें और पुष्टि करें):** **Never silently guess.** Highlight ambiguous or uncertain text in amber, check for conflicting instructions against existing schedules, and require explicit user confirmation before any schedule can be created.
4. **Explain (सरल भाषा में समझें):** Explain the confirmed instructions in plain Hindi, with active generic salt mapping (NLEM & Jan Aushadhi) and audio read-aloud support.
5. **Remind (दवा रिमाइंडर):** Create reminders strictly from confirmed instructions without wiping older prescriptions.
6. **Caregiver Share (परिवार को भेजें):** 1-tap WhatsApp schedule export for family caregivers assisting elderly relatives.
7. **Ask (सवाल पूछें):** Constrained Q&A assistant to answer questions about the prescription without diagnosing or overriding medical advice.

---

## 🛡️ Medical Safety & Rural Accessibility Principles

- **Accessibility by Default:** Mobile-first layout, large controls, toggle for **"🔍 बड़े अक्षर (Large Text Mode)"**, and high contrast.
- **Rule 1 — Never Guess Dosages:** Missing durations or strengths remain `null`; the model never invents default doses.
- **Rule 2 — Ambiguity Flags:** Ambiguous handwriting is visibly flagged with an amber warning card.
- **Rule 3 — Human Confirmation Gate:** No reminder can be saved or activated without explicit user review and confirmation (`user_confirmed=True`).
- **Rule 4 — Raw Wording Preservation & Traceability:** The app displays the raw text alongside parsed fields and links each saved reminder to its source prescription date.
- **Rule 5 & 6 — Sourced General Information:** General drug knowledge (Indian NLEM / Jan Aushadhi) is strictly segregated into an educational reference box.
- **Conflict Prevention:** If an incoming prescription has a different dosage for an existing medicine, the app explicitly flags the conflict for clinician clarification.
- **Rule 8 & 9 — No Diagnosis:** The chatbot refuses diagnostic queries and symptom checks, advising users to visit their local Primary Health Centre (PHC).
- **Rule 13 — Zero Patient Data Storage:** Uploaded photos are processed in memory and not permanently retained by default.

---

## 🏗️ Project Architecture

```
sehat-saathi/
├── app/
│   └── main.py                     # Streamlit Mobile-First UI (Large-font mode, Photo guidance, WhatsApp share)
├── models/
│   ├── prescription.py             # Pydantic Schemas with Safety Invariants
│   └── reminder.py                 # Reminder & Schedule Models with Traceability
├── services/
│   ├── prescription_extractor.py   # BaseExtractor, GeminiMultimodal, MockExtractor
│   ├── image_processing.py         # EXIF normalization, quality heuristics
│   ├── medicine_reference.py       # Indian Healthcare Database (NLEM & Jan Aushadhi)
│   ├── language_service.py         # Simple Hindi copy & gTTS audio
│   ├── reminder_service.py         # Schedule logic, conflict detection, due-status check
│   └── chat_service.py             # Grounded Q&A assistant with safety tripwires
├── storage/
│   └── persistence.py              # Offline-friendly local storage adapter (JSON)
├── data/
│   └── sample_prescriptions/       # Synthetic test prescriptions
├── tests/
│   ├── test_models.py
│   ├── test_extraction.py
│   ├── test_medical_safety.py
│   ├── test_conflicts_and_traceability.py
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
*(Note: The app works out-of-the-box in **Demo Mode** using realistic synthetic samples even without an API key).*

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

All 24 automated safety, extraction, traceability, and reminder tests can be run with `pytest`:
```bash
source .venv/bin/activate
pytest
```

---

## 📋 Honest Limitations Disclosure (Requirement 7 & 8)
- **In-App Alerts vs OS Background Alarms:** Reminders are managed dynamically inside the web application. When the browser or phone is fully locked/closed, background OS-level push alarms or SMS are not guaranteed without a native mobile wrapper or SMS gateway.
- **Assistive Scope:** Designed for patient understanding and reminder adherence; never replaces a doctor or pharmacist.
- **Offline Scope:** Saved reminders and past confirmed prescriptions are fully accessible offline; scanning new photos requires an internet connection for Gemini Multimodal processing.
