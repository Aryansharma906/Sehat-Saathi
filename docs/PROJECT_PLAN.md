# Master Project Plan & Execution Checklist

**Project:** Sehat Saathi (सेहत साथी)  
**Lead Coordinator:** Agent 1 (Technical Lead)  
**Target:** Hackathon MVP (Demonstrable, Safe, Reliable)

---

## 1. Agent Assignment Matrix

| Agent Role | Assigned Lead | Core Responsibilities | Target Deliverables |
| :--- | :--- | :--- | :--- |
| **Agent 1** | Technical Lead | Project plan, architecture, integration, schema truth | `PROJECT_PLAN.md`, `ARCHITECTURE.md`, `DECISIONS.md` |
| **Agent 2** | API & Repo Researcher | Documentation verification, repo analysis, costs/quotas | `API_RESEARCH.md`, `REPOSITORY_RESEARCH.md` |
| **Agent 3** | Medical Safety | 15 Safety invariants, ambiguity gates, safety tests | `MEDICAL_SAFETY.md`, `test_medical_safety.py` |
| **Agent 4** | UX & Accessibility | Low-literacy mobile flow, Hindi copy, UI states | `UX_SPEC.md`, UI design patterns |
| **Agent 5** | Backend & Extraction | Pydantic schemas, Gemini extraction service, mocks | `models/`, `services/prescription_extractor.py` |
| **Agent 6** | Frontend Engineer | Streamlit app, review screen, status badges | `app/main.py`, `app/components/` |
| **Agent 7** | Reminders & Voice | Reminder service, schedule logic, speech TTS | `services/reminder_service.py`, `language_service.py` |
| **Agent 8** | QA & Security | Test suite, integration tests, privacy scan, report | `tests/`, `docs/TEST_REPORT.md` |

---

## 2. Phase-by-Phase Roadmap

### Phase 0: Discovery, Architecture & Setup (CURRENT)
- [x] Workspace inspection (empty directory, Python 3.13.7 verified).
- [x] Git repository initialized with `.gitignore` and `.env.example`.
- [x] Virtual environment `.venv` created.
- [x] API research documented (`docs/API_RESEARCH.md`).
- [x] Repository research documented (`docs/REPOSITORY_RESEARCH.md`).
- [x] Medical safety invariants established (`docs/MEDICAL_SAFETY.md`).
- [x] UX & accessibility specification authored (`docs/UX_SPEC.md`).
- [x] Integrations & permissions matrix created (`docs/INTEGRATIONS_AND_PERMISSIONS.md`).
- [x] Project architecture finalized (`docs/ARCHITECTURE.md`).

### Phase 1: Working Skeleton & Data Models
- [ ] Define dependencies in `requirements.txt`.
- [ ] Implement core Pydantic data models (`models/prescription.py`, `models/reminder.py`).
- [ ] Build minimal Streamlit skeleton (`app/main.py`) that launches cleanly even without API key.
- [ ] Implement synthetic sample prescription generator for testing without physical files.
- [ ] Verify Phase 1 tests (`pytest tests/test_models.py`).

### Phase 2: Extraction Service & Uncertainty Handling
- [ ] Implement abstract interface `BasePrescriptionExtractor`.
- [ ] Implement `GeminiMultimodalExtractor` using current `google-genai` SDK with structured JSON schemas.
- [ ] Implement `MockPrescriptionExtractor` for deterministic unit testing without API costs.
- [ ] Add image validation & quality check helper (`services/image_processing.py`).
- [ ] Enforce uncertainty flags whenever confidence is low or handwriting is ambiguous.
- [ ] Run extraction test suite (`tests/test_extraction.py`).

### Phase 3: Review, Confirmation & Explanation
- [ ] Build interactive Streamlit Review Card showing raw text vs parsed fields.
- [ ] Require user confirmation checkbox before saving any instruction.
- [ ] Implement `services/language_service.py` for plain-Hindi explanations.
- [ ] Implement `services/medicine_reference.py` for Indian Essential Medicines lookup.
- [ ] Test safety invariants (`tests/test_medical_safety.py`).

### Phase 4: Reminder Service & Grounded Q&A
- [ ] Implement `services/reminder_service.py` (add, list, toggle, delete, due-status check).
- [ ] Enforce Invariant 3: Unconfirmed instructions cannot produce active reminders.
- [ ] Build grounded Q&A helper for prescription questions (Rule 8: no diagnosis, refer to clinician).
- [ ] Run reminder test suite (`tests/test_reminders.py`).

### Phase 5: Voice & Accessibility
- [ ] Implement browser audio / speech synthesis fallback for reading Hindi instructions aloud.
- [ ] Test audio playback in Streamlit interface.

### Phase 6: End-to-End QA, Polish & Acceptance
- [ ] Full automated test suite execution via `pytest`.
- [ ] Security audit: verify `.env` is uncommitted and zero sensitive logs.
- [ ] Author comprehensive `README.md` with demo walkthrough and setup instructions.
- [ ] Generate `docs/TEST_REPORT.md`.
