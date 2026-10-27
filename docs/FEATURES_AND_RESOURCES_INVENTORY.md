# Sehat Saathi (सेहत साथी) — Features & Resources Inventory

**Project:** Sehat Saathi  
**Target Demographic:** Rural India, Older Adults, Family Caregivers  
**Interface Language:** Simple Hindi + Universal Visual Icons + Audio (gTTS)  
**Safety Classification:** Assistive Medical Information & Schedule Companion (Strict Non-Diagnostic)

---

## 1. Feature-by-Feature Requirements Matrix

The table below catalogs every feature, what is needed to support it, external public datasets, device specs, and fallback mechanisms:

| Feature | Key Capability | Things / Resources Needed | Public APIs / Open Datasets | Offline / Fallback Capability |
| :--- | :--- | :--- | :--- | :--- |
| **1. Mobile Prescription OCR & Extraction** | Scan handwriting, extract medicines, doses, frequencies, and timings | • Google Gemini API Key (`GEMINI_API_KEY`)<br>• Camera / File Upload UI<br>• EXIF normalizer (`Pillow`) | `gemini-2.5-flash` Multimodal Vision via `google-genai` SDK | Explicit synthetic sample controls for zero-API demo; real uploads fail clearly without a live extractor |
| **2. Medical Ambiguity & Safety Barrier** | Amber warning card on uncertain handwriting; never fabricate missing values | • `MedicineInstruction.is_uncertain`<br>• Safety Invariant validator rules<br>• Human confirmation barrier (`user_confirmed=True`) | Open Health Data Standards / WHO Safety Invariants | Runs 100% locally on device |
| **3. Indian Healthcare & Drug Database Grounding** | Map brand names (Dolo, Pan-D, Combiflam) to active generic salts & NLEM status | • Curated Indian NLEM & Jan Aushadhi catalog (`data/nlem_catalog.json`)<br>• Fast dictionary lookup | • National List of Essential Medicines (NLEM - MoHFW)<br>• Jan Aushadhi (PMBI / PMBJP) generic catalog | 100% local JSON catalog. Zero cloud DB latency |
| **4. Language Explanation & Audio** | Explain confirmed instructions in English, Hindi, or Hinglish in the browser; Hindi/Hinglish in Streamlit; optional audio playback in the browser | • `SimpleHindiLanguageService`<br>• `gTTS` / HTML5 Audio | Google Text-to-Speech through the `gtts` Python package | Plain text remains available if audio/network fails; requested audio sends explanation text to the external speech service |
| **5. Non-Destructive Reminders & Conflict Detection** | Set reminders without wiping old prescriptions; warn on dosage differences | • Schedule CRUD engine<br>• Dosage conflict comparator<br>• Source prescription ID & date traceability | Local JSON Persistence (`data/saved_schedules.json`) | 100% offline local storage |
| **6. Emergency Helplines (1-Tap Dialing)** | Direct calls for 108 (Ambulance), 112 (Unified), 104 (Health advice), 102 (Maternity) | • Emergency directory (`data/emergency_contacts_india.json`)<br>• HTML5 `tel:` URI protocol | • NHM 108 Emergency Ambulance<br>• MHA 112 ERSS<br>• State 104 Helplines | Native phone dialer works without active internet or data connection |
| **7. Facilities & Chemist Map Locator** | One-time, permission-based browser GPS or manual city/coordinate lookup; show curated pilot entries or live nearby results | • Browser Geolocation API<br>• Static pilot facilities in `services/proximity_service.py`<br>• OpenStreetMap geocoding and facility lookup in `services/openstreetmap_facilities.py`<br>• Google Maps search/directions deep-links | OpenStreetMap Nominatim and Overpass public services; Google Maps fallback | GPS is not continuously tracked. A live search sends the selected city or GPS coordinates to OpenStreetMap. Community-mapped listings may be incomplete or out of date; Google Maps is a fallback. |
| **8. Environmental Health & Disease Prevention** | Actionable guides on clean water, vector control, clean cooking air | • Prevention guides catalog (`data/disease_prevention_guides.json`) | • WHO WASH Guidelines<br>• NVBDCP (National Vector Borne Disease Control)<br>• NTEP (TB Control) | 100% offline static guidelines |
| **9. Treatment Adverse Issue Logger & WhatsApp Doctor Alert** | Log adverse reactions during treatment; auto-detect severe allergy; alert doctor | • Adverse reaction taxonomy<br>• Severe symptom scanner (anaphylaxis/breathing)<br>• WhatsApp Click-to-Chat URL generator | WhatsApp Universal API (`https://api.whatsapp.com/send?...`) | Local persistent logging in `data/treatment_issues.json` |
| **10. 30-Second Recovery Questionnaire** | 3-question observational test tracking recovery percentage (0–100%) | • Adherence and relief scoring matrix<br>• Escalation triggers (`doctor_visit_advised`) | ICMR Patient-Reported Outcome Measures (PROMs) | 100% local client-side evaluation |
| **11. Health Device Vitals Import & Clinical Alerts** | Log BP, SpO2, Blood Sugar, Temperature; alert on abnormal readings; import device data | • Standardized Vitals Schema<br>• Clinical range boundaries (`data/clinical_vitals_thresholds.json`)<br>• Bluetooth export JSON importer | Standard Bluetooth SIG Health Device GATT Profiles (Blood Pressure 0x1810, Pulse Oximeter 0x1822, Glucose 0x1808) | Offline local storage (`data/device_vitals.json`) + sample exports in `data/sample_device_exports/` |
| **12. Mental Health Screening & Tele-MANAS** | 3-question observational well-being check; 1-tap call to National Helpline 14416 | • Emotional well-being questionnaire<br>• Supportive guidance copy<br>• Direct `tel:14416` dialer link | Ministry of Health & Family Welfare (MoHFW) / NIMHANS Tele-MANAS National Helpline | Native phone dialer to toll-free 14416 works 24/7 on any phone network |
| **13. Discard & Mistake Recovery** | Cancel draft prescription, remove individual misread lines, purge inactive reminders | • `Prescription.discard_medicine()`<br>• `ReminderService.discard_inactive_reminders()`<br>• Deletion hooks on all stored models | Local state management & Python Pydantic validators | 100% instant client-side execution |

---

## 2. Gathered Datasets & Catalog Files

All required datasets have been curated, standardized, and stored in the repository:

1. **`data/nlem_catalog.json`**:
   - Contains 20 essential drug classes widely prescribed in Indian healthcare (Paracetamol, Dolo, Pantoprazole, Pan-D, Amoxicillin-Clavulanic, Azithromycin, Metformin, Amlodipine, Telmisartan, ORS, Cetirizine, Salbutamol, etc.).
   - Specifies commercial brand examples, generic salts, therapeutic classes, plain-language Hindi guidance, and Jan Aushadhi generic availability.

2. **`data/emergency_contacts_india.json`**:
   - Direct emergency agency numbers (`108`, `112`, `104`, `102`, `14416`, `1075`), official jurisdictions, 24/7 toll-free status, and priority routing.

3. **`data/clinical_vitals_thresholds.json`**:
   - Medical classification ranges based on ICMR and WHO protocols:
     - **Blood Pressure:** Normal (<120/80), Stage 1 (140/90), Crisis (>180/120).
     - **Oxygen Saturation ($SpO_2$):** Normal (95–100%), Warning (92–94%), Critical (<92%).
     - **Blood Glucose:** Fasting vs Postprandial ranges for hypoglycemia, normal, and diabetes (>200 mg/dL).
     - **Body Temperature:** Normal, Low-grade, High fever (≥101°F).

4. **`data/disease_prevention_guides.json`**:
   - MoHFW/NHM compliant Hindi advisories on water chlorination/boiling, mosquito breeding prevention, and indoor biomass smoke ventilation.

5. **`data/sample_device_exports/`**:
   - Ready-to-use JSON export fixtures for testing:
     - `sample_bp_monitor.json` (Omron BP format)
     - `sample_pulse_oximeter.json` (SpO2 & pulse)
     - `sample_glucometer.json` (Fasting & postprandial glucose)
     - `sample_thermometer.json` (Digital fever readings)

6. **`data/sample_prescriptions/`**:
   - Realistic synthetic handwritten prescription images:
     - `clean_sample_prescription.jpg` (Legible script)
     - `ambiguous_sample_prescription.jpg` (Ambiguous dosage script)

---

## 3. Technology Stack & Dependencies

```ini
# Core UI & Application Framework
streamlit>=1.40.0

# Gemini Multimodal AI SDK (Official Google GenAI SDK v1.0+)
google-genai>=1.0.0

# Robust Data Modeling & Safety Invariant Enforcement
pydantic>=2.10.0

# Image Processing, Orientation Normalization & Heuristics
pillow>=10.4.0

# Audio Read-Aloud for Rural Accessibility
gTTS>=2.5.0

# Secure Configuration & Environment Loading
python-dotenv>=1.0.0

# External Network Requests & Deep Linking
requests>=2.32.0

# Automated Testing & Verification
pytest>=8.3.0
anyio>=4.0.0
```

---

## 4. Hardware & Sensor Compatibility Guidelines

For real-world rural clinic or home usage, Sehat Saathi supports two primary hardware integration pathways:

### Pathway A: Direct JSON / File Sync (Implemented & Ready)
- Any Bluetooth companion app or smart clinic hub can export standard JSON or CSV files into Sehat Saathi's `DeviceDataService.import_device_json_data()`.
- Tested with sample fixtures in `data/sample_device_exports/`.

### Pathway B: Web Bluetooth API (Browser-level)
- Supported Bluetooth Low Energy (BLE) GATT Profiles:
  - **Blood Pressure Profile (BLP):** Service UUID `0x1810` (Characteristic `0x2A35`)
  - **Pulse Oximeter Profile (PLXP):** Service UUID `0x1822` (Characteristic `0x2A5F`)
  - **Glucose Profile (GLP):** Service UUID `0x1808` (Characteristic `0x2A18`)
  - **Health Thermometer Profile (HTP):** Service UUID `0x1809` (Characteristic `0x2A1C`)
- Sehat Saathi's data schema ([models/vitals_and_mental_health.py](file:///Users/aryansharma/Downloads/Sehat%20Saathi/models/vitals_and_mental_health.py)) directly maps these GATT standard floats into its verified validation pipeline.

---

## 5. Security & Privacy Invariants

- **Local Image Handling:** Prescription photos are held in temporary memory and not written to the app's local store. Real scans send the image bytes to Gemini; this does not guarantee the provider's retention or handling practices.
- **External Speech Processing:** The optional browser read-aloud sends the explanation text to Google Text-to-Speech through gTTS.
- **Nearby Location Search:** Live facility lookups send the selected town/city or GPS coordinates to public OpenStreetMap services. Their community-maintained data may be incomplete or stale.
- **Local JSON Persistence:** Medication records and device vitals reside locally on the user's host machine or browser sandbox (`data/*.json`).
- **No Cloud Account Prerequisite:** Works for rural patients and visiting caregivers without mandatory user sign-up or passwords.
