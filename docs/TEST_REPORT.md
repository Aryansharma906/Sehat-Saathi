# Automated QA & Medical Safety Test Report

**Project:** Sehat Saathi (सेहत साथी)  
**QA Lead:** Agent 8 (QA, Security & Integration)  
**Test Suite:** Pytest 9.1.1, Python 3.13.7  
**Execution Date:** 2026-10-26  
**Status:** **21 / 21 TESTS PASSED (100% Pass Rate)**

---

## 1. Test Execution Breakdown

| Test Module | Tests Run | Result | Coverage Area |
| :--- | :--- | :--- | :--- |
| **`tests/test_models.py`** | 4 | **PASS** | Non-empty raw names, `null` preservation for unwritten fields, Safety Invariant 3 gate on unconfirmed models, time validation |
| **`tests/test_extraction.py`** | 4 | **PASS** | Mock clean extraction, ambiguous handwriting uncertainty flagging, failure handling, graceful handling of missing Gemini API key |
| **`tests/test_medical_safety.py`** | 6 | **PASS** | Strict verification of Rules 1, 2, 3, 4, 5, 6, 11 (Never invent dosage, never guess ambiguous names, block unconfirmed reminders, preserve raw wording, isolate external drug reference, require manual click for taken status) |
| **`tests/test_reminders.py`** | 2 | **PASS** | Reminder CRUD lifecycle (add, toggle, mark as taken, delete) and real-time `is_due_now` window calculation |
| **`tests/test_chat_safety.py`** | 3 | **PASS** | Emergency triage tripwire (108/112 advisory), symptom diagnosis refusal tripwire, grounded prescription fallback response |
| **`tests/test_image_processing.py`** | 2 | **PASS** | Empty file rejection, EXIF normalization, brightness/contrast quality heuristics |

---

## 2. Security & Privacy Audit

- [x] **No hardcoded secrets:** Verified across all `.py` and `.md` files.
- [x] **Gitignore protection:** `.env`, `.venv`, `.streamlit/secrets.toml`, and patient upload folders are properly excluded.
- [x] **Privacy Invariant (Rule 13):** Uploaded prescription photos are loaded in-memory (`BytesIO`) and not saved to disk by default.
- [x] **Synthetic Test Data Only (Rule 14):** Test prescriptions in `data/sample_prescriptions/` use 100% fictional patient identities (*Sunita Devi*, *Ramesh Kumar*).
- [x] **Graceful Failure (Rule 10):** When `GEMINI_API_KEY` is omitted, the app displays a clear setup message and falls back to mock demo mode without crashing.

---

## 3. Known Limitations & Hackathon Boundaries

1. **Browser Notifications vs OS Notifications:** Reminders are managed dynamically inside the Streamlit web application. If the browser tab or device is completely closed, native background push notifications or SMS are not guaranteed without a dedicated mobile app wrapper or SMS gateway.
2. **Indian Brand Nomenclature:** While the curated Indian Essential Medicines database handles the top 10 most common Indian generic formulations and brand examples, regional local brand variations from small manufacturers may not match and will be flagged for user verification.
3. **Assistive Nature:** Sehat Saathi is an assistive tool to aid understanding and schedule compliance; it is not a certified medical device.
