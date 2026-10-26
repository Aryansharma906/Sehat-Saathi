# Master Project Plan & Execution Checklist

**Project:** Sehat Saathi (सेहत साथी)  
**Lead Coordinator:** Agent 1 (Technical Lead)  
**Target:** Hackathon MVP (Accessible Rural Healthcare Edition)

---

## 1. Accessible Rural Healthcare Requirements Matrix

| Requirement | Description | Status | Implementation Details |
| :--- | :--- | :--- | :--- |
| **1. Accessibility by Default** | Mobile-first, large controls, adjustable text mode, high contrast, icons with text, error recovery without losing input | **IMPLEMENTED** | `app/main.py`: Mobile CSS container, `🔍 बड़े अक्षर` font-scaler, session state persistence |
| **2. Prescription Image Quality** | 3-step photography guidance, brightness/contrast validation, EXIF normalization, never fabricate fields | **IMPLEMENTED** | `services/image_processing.py`: EXIF transpose, brightness/contrast heuristics, photo guide expander |
| **3. Confirmed Medication Records** | Traceability to source prescription, non-destructive schedule merging, conflict detection between old and new prescriptions | **IMPLEMENTED** | `models/reminder.py`: `source_prescription_id`, `services/reminder_service.py`: `check_potential_conflicts` |
| **4. Offline-Friendly Operation** | Saved records accessible without internet, separation of local vs online features, clear network notifications | **IMPLEMENTED** | Local JSON storage (`data/saved_schedules.json`), mock demo fallback, offline status badge |
| **5. Caregiver-Friendly Workflow** | Allows family members to scan and review for an elder, no forced accounts for MVP, 1-tap WhatsApp schedule share | **IMPLEMENTED** | `app/main.py`: WhatsApp schedule generator (`https://wa.me/?text=...`), unauthenticated local profile |
| **6. Trust & Transparency** | Distinguish raw text, AI interpretations, user-confirmed data, and external Indian NLEM reference | **IMPLEMENTED** | Review screen visually segregates raw handwriting, editable fields, and NLEM Jan Aushadhi badges |
| **7. Reminder Reliability** | Acknowledge in-app vs OS notification limits, require manual tap for "Mark as Taken", block unconfirmed reminders | **IMPLEMENTED** | `models/reminder.py`: `taken_today=False`, Invariant 3 gate, explicit in-app notification disclaimer banner |
| **8. Scope Control** | Defer complex multi-user accounts, automated pharmacy ordering, and autonomous treatment changes | **DOCUMENTED** | Deferred items cataloged below with rationale |
| **9. Validation** | Automated tests using synthetic fixtures for poor images, missing doses, conflicts, and network failures | **IMPLEMENTED** | 24 automated tests in `tests/` with 100% pass rate |

---

## 2. Feature Implementation Status

### ✅ Implemented in MVP
- [x] Streamlit mobile-first Hindi user interface with large-font mode toggle.
- [x] Gemini Multimodal extraction with Pydantic JSON schema output.
- [x] Image quality pre-check (EXIF rotation, dark/bright image warnings).
- [x] Review & Confirmation gate (amber warning cards for ambiguous handwriting).
- [x] Indian Healthcare Database integration (NLEM & Jan Aushadhi generic salt mappings).
- [x] Plain-Hindi explanation with `gTTS` audio synthesis.
- [x] Non-destructive reminder schedule merging with conflict detection.
- [x] Prescription record traceability (`source_prescription_id`, `source_raw_text`).
- [x] Caregiver 1-tap WhatsApp schedule export.
- [x] Grounded Q&A assistant with emergency tripwire (108/112).
- [x] 24 unit and integration test suites passing.

### ⏳ Deferred Beyond First MVP
- **Complex Multi-User / Cloud Authentication:** Deferred to keep app instant and barrier-free for rural users without requiring OTP or passwords.
- **Background Push Notifications when Phone is Off:** Deferred because browser-based Streamlit cannot trigger native Android background alarms without an APK wrapper.
- **Automated Pharmacy Fulfillment / ABDM Integration:** Deferred to future post-hackathon consent-governed phase.
- **Autonomous Interaction / Drug-Drug Checker:** Deferred to avoid liability and false confidence without doctor oversight.

### 🚫 Explicitly Out of Scope
- Automated medical diagnosis or treatment recommendation.
- Overriding doctor prescriptions or dosage changes.
- Using real patient health records during development.
