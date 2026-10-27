# 💊 Sehat Saathi (सेहत साथी)

> **Status: local research prototype only.** This is not a government service, not a validated clinical product, and not suitable for real patient data or clinical decisions. The facility directory and public-service configuration cover only a small India-focused demo cluster. Production startup is intentionally blocked. See [deployment readiness](docs/DEPLOYMENT_READINESS.md) before any pilot or deployment discussion.

> **Accessible AI-Assisted Prescription Reader and Medication Companion for Rural India & Older Adults**  
> *Developed for the AURIX AI Hackathon using Google Antigravity*

**Plain-language overview:** [Read the short project brief](docs/PROJECT_BRIEF.md).

**Vercel demo:** the deploy entrypoint is isolated and read-only; it excludes the repository health-data files and accepts only synthetic prescription samples. This is a public demonstration, not a place to enter patient or personal health information.

---

## 🌟 Vision & Problem Statement

In rural India, millions of older adults and patients struggle to read doctors' handwritten prescriptions, understand confusing dosage abbreviations (such as *TDS*, *BD*, *p/c*), or manage medication schedules. Most medical apps are cluttered, in English, or assume high digital literacy. Furthermore, unchecked AI chatbots often hallucinate dangerous dosages when presented with illegible handwriting.

**Sehat Saathi** solves this through a simple, high-contrast, mobile-first companion in **simple Hindi**:
1. **Scan (तस्वीर लें):** Take a photo with built-in photography guidance (flat surface, no shadows, 4 corners visible).
2. **Read (पर्चे को समझें):** Extract medicine names and written instructions with Gemini Multimodal Vision.
3. **Verify & Confirm (जांचें और पुष्टि करें):** **Never silently guess.** Highlight ambiguous or uncertain text in amber, check for conflicting instructions against existing schedules, and require explicit user confirmation before any schedule can be created.
4. **Explain (सरल भाषा में समझें):** After confirmation, explain the instructions in English, Hindi, or Hinglish in the browser app; the Streamlit app also provides Hindi/Hinglish explanations. The browser can read the explanation aloud when its online speech service is available. General medicine references (NLEM & Jan Aushadhi) are shown separately from the doctor's instructions.
5. **Remind (दवा रिमाइंडर):** Create reminders strictly from confirmed instructions without wiping older prescriptions.
6. **Caregiver Share (परिवार को भेजें):** 1-tap WhatsApp schedule export for family caregivers assisting elderly relatives.
7. **Ask (सवाल पूछें):** Health-information assistant that discusses and cautiously ranks plausible causes, asks follow-up questions, and helps explain confirmed prescription details while distinguishing tentative assessments from clinician-confirmed diagnoses.
8. **Emergency Support (आपातकालीन नंबर):** Instant 1-tap calling for 108 (Ambulance), 112 (Emergency), 104 (Health advice), and 102 (Mother/Child).
9. **Clinics & Chemists Map (अस्पताल व दवा दुकानें):** One-time, permission-based GPS or manual city/coordinate search. Curated sample listings cover the Rajasthan pilot cluster; other locations use OpenStreetMap's community-maintained facility data, with Google Maps as a fallback. Live searches send the selected city or GPS coordinates to OpenStreetMap. Listings may be incomplete or out of date and should be confirmed before travelling. GPS is not continuously tracked.
10. **Treatment Reaction Logger & Doctor Escalation (समस्या व डॉक्टर सूचना):** Log side-effects or allergic symptoms and generate 1-tap structured WhatsApp reports for the doctor.
11. **Recovery Progress Tracking (स्वास्थ्य सुधार सवाल):** 30-second observational check-in to track recovery percentage over time.
12. **Health Device Vitals & Mental Wellness (जांच व मन की शांति):** Standardized logging for BP, SpO2, blood sugar, and digital thermometers with clinical alert banners, alongside mental health screening integrated with Govt of India's Tele-MANAS (14416).

---

## 🛡️ Medical Safety & Rural Accessibility Principles

- **Accessibility by Default:** Mobile-first layout, large controls, toggle for **"🔍 बड़े अक्षर (Large Text Mode)"**, and high contrast.
- **Rule 1 — Never Guess Dosages:** Missing durations or strengths remain `null`; the model never invents default doses.
- **Rule 2 — Ambiguity Flags:** Ambiguous handwriting is visibly flagged with an amber warning card.
- **Rule 3 — Human Confirmation Gate:** No reminder can be saved or activated without explicit user review and confirmation (`user_confirmed=True`).
- **Rule 4 — Raw Wording Preservation & Traceability:** The app displays the raw text alongside parsed fields and links each saved reminder to its source prescription date.
- **Rule 5 & 6 — Sourced General Information:** General drug knowledge (Indian NLEM / Jan Aushadhi) is strictly segregated into an educational reference box.
- **Conflict Prevention:** If an incoming prescription has a different dosage for an existing medicine, the app explicitly flags the conflict for clinician clarification.
- **Chat — Symptom Assessment:** The assistant can explain and cautiously rank plausible causes based on reported symptoms, ask focused follow-up questions, and point out urgent warning signs. It must identify uncertainty, cannot claim a confirmed diagnosis, and does not recommend personal prescription dose changes.
- **Rule 13 — Zero Patient Data Storage:** Uploaded photos are processed in memory and not permanently retained by default.

---

## 🏗️ Project Architecture

```
sehat-saathi/
├── webapp/
│   ├── main.py                     # Starlette ASGI server and JSON API
│   └── static/                     # Responsive browser-first application
├── app/
│   └── main.py                     # Legacy Streamlit compatibility UI
├── models/
│   ├── prescription.py             # Pydantic Schemas with Safety Invariants
│   ├── reminder.py                 # Reminder & Schedule Models with Traceability
│   ├── health_issue.py             # Treatment side-effect & reaction logging
│   ├── progress_tracker.py         # 30-second recovery questionnaire models
│   └── vitals_and_mental_health.py # Device vitals (BP, SpO2, Sugar, Temp) & Mental health screening
├── services/
│   ├── prescription_extractor.py   # BaseExtractor, GeminiMultimodal, MockExtractor
│   ├── image_processing.py         # EXIF normalization, quality heuristics
│   ├── medicine_reference.py       # Indian Healthcare Database (NLEM & Jan Aushadhi generic mapping)
│   ├── language_service.py         # Simple Hindi copy & gTTS audio
│   ├── reminder_service.py         # Schedule logic, conflict detection, due-status check
│   ├── chat_service.py             # Multilingual health information and prescription Q&A
│   ├── emergency_service.py        # Direct mobile dialer links (108, 112, 104, 102)
│   ├── prevention_and_facilities.py# Disease prevention guides & universal Map links (PHC, CHC, Chemists)
│   ├── health_issue_service.py     # Side-effect logging & WhatsApp doctor escalation
│   ├── progress_tracker_service.py # 3-question recovery scoring & trend tracking
│   ├── mental_health_service.py    # Mental wellness screening & Tele-MANAS (14416) referral
│   └── device_data_service.py      # Standardized BP, SpO2, Glucose, Temp vitals with clinical alerts
├── storage/
│   └── persistence.py              # Offline-friendly local storage adapter (JSON)
├── data/
│   └── sample_prescriptions/       # Realistic synthetic test prescriptions
├── tests/
│   ├── test_models.py
│   ├── test_extraction.py
│   ├── test_medical_safety.py
│   ├── test_conflicts_and_traceability.py
│   ├── test_reminders.py
│   ├── test_chat_safety.py
│   ├── test_image_processing.py
│   ├── test_emergency_service.py
│   ├── test_prevention_and_facilities.py
│   ├── test_health_issue_service.py
│   ├── test_progress_tracker.py
│   └── test_vitals_and_mental_health.py
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

Start the local browser application:
```bash
uvicorn webapp.main:app --host 127.0.0.1 --port 8000 --env-file .env
```
Open [http://127.0.0.1:8000](http://127.0.0.1:8000). The server binds to your computer only by default. Keep it on loopback unless you configure authentication before exposing it to a network.

The browser interface uses the project's existing Python services and local data stores. Real prescription scans require `GEMINI_API_KEY`; uploaded image bytes are sent to Gemini for extraction. The two sample prescriptions are available in demo mode without an API key and do not call the live extractor. The app processes uploaded photos in memory and does not save them to its local data store, but this does not establish Gemini's retention or handling practices. When read-aloud is requested, the explanation text is sent to Google Text-to-Speech (gTTS), which requires a network connection. A reminder can only be saved after reviewing and confirming its medicine name, dose, supported frequency, and timing; missing or as-needed instructions cannot be scheduled.

**Privacy boundary:** This is a local research prototype without user accounts or per-user data separation. Do not enter real patient information. Nearby live searches share the entered city or selected GPS coordinates with OpenStreetMap's public Nominatim/Overpass services. Keep the server on loopback; do not expose it to a network.

### Temporary, password-protected Vercel test

The Vercel `test` mode enables write workflows behind HTTP Basic authentication. Set `SEHAT_ENV=test` and a strong `SEHAT_TEST_ACCESS_PASSWORD` as **Preview-only** Vercel environment variables before deploying. The username is `tester`. This is a shared-password test gate, not individual accounts: anyone with the password can access shared test records. Records use temporary function storage and can disappear at any time; use synthetic data only. Do not set this mode for a public or production deployment. Live prescription scanning also needs `GEMINI_API_KEY` in Vercel's encrypted environment variables; never commit or paste the key into source code.

To keep access limited, configure the password variables for a single Preview Git branch and share the preview URL/password only with trusted testers. For example, with Vercel CLI already linked to the project:

```bash
vercel env add SEHAT_ENV --environment preview --git-branch feat/nearby-live-listings --value test --yes
vercel env add SEHAT_TEST_ACCESS_PASSWORD --environment preview --git-branch feat/nearby-live-listings
vercel deploy --environment preview
```

The second command prompts for the password; enter a generated password there rather than placing it in shell history. Configure `GEMINI_API_KEY` separately in Vercel's project settings if live OCR is needed. Vercel's free-tier limits, function duration, and Gemini API quotas apply. This temporary test mode is not safe for real patient data and does not provide durable reminders or user-specific records.

For isolated local testing, set `SEHAT_DATA_DIR` to a disposable directory before starting the server. Otherwise, the app uses `data/` in the repository. For example, on macOS/Linux:

```bash
SEHAT_DATA_DIR=/tmp/sehat-saathi-local-data uvicorn webapp.main:app --host 127.0.0.1 --port 8000
```

---

## 🧪 Running Automated Tests

Install the development dependencies, then run the complete safety, service, and UI compatibility suite:
```bash
source .venv/bin/activate
pip install -r requirements-test.txt
pytest
```
The legacy Streamlit UI is only kept for regression compatibility; it is not needed to run the browser app.

---

## 📋 Honest Limitations Disclosure (Requirement 7 & 8)
- **In-App Alerts vs OS Background Alarms:** Reminders are managed dynamically inside the web application. When the browser or phone is fully locked/closed, background OS-level push alarms or SMS are not guaranteed without a native mobile wrapper or SMS gateway.
- **Assistive Scope:** Designed for patient understanding and reminder adherence; never replaces a doctor or pharmacist.
- **Offline Scope:** Health records are stored locally on the host computer and are available while its web server is running. The browser UI is not yet cached for use when the host or server is offline. New AI-assisted prescription scans require an internet connection and a configured Gemini API key.
