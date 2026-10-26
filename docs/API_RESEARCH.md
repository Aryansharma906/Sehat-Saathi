# API Research & Suitability Analysis

**Project:** Sehat Saathi  
**Date Checked:** 2026-10-26  
**Research Lead:** Agent 2 (API & Repository Researcher)

---

## 1. Google Gemini API (`google-genai` SDK)

- **Official Source:** [Google AI Studio Docs](https://aistudio.google.com/docs/get-started) & Upstream `google-genai` SDK v1.0+
- **Primary Use:** Multimodal visual extraction from prescription images directly into structured Pydantic JSON schemas; plain-language medical instruction simplification in Hindi.
- **Recommended Model:** `gemini-2.5-flash` (or `gemini-2.0-flash` / alias `gemini-flash-latest`)
- **Key Features Verified:**
  - Native `response_json_schema` via `GenerateContentConfig` supporting Pydantic model schemas.
  - Image input support via `types.Part.from_bytes(data=bytes, mime_type=mime_type)` or inline data.
  - Grounded safety controls: Explicit negative prompting ("do not guess uncertain handwriting; label as uncertain").
- **Cost & Quotas:**
  - Free tier offers substantial RPM/RPD on AI Studio for development and hackathon prototypes.
  - Data-use policy: Free-tier data may be reviewed by human trainers; **mandatory rule: only synthetic/anonymized test images must be submitted**.
- **Decision:** **ADOPT as Primary Multimodal Extraction & Explanation Engine.**

---

## 2. Google Cloud Vision OCR

- **Official Source:** [Google Cloud Vision OCR](https://docs.cloud.google.com/vision/docs/ocr)
- **Role:** Fallback / benchmarking OCR candidate for dense handwritten text.
- **Considerations:**
  - Requires Google Cloud Platform project setup, service account JSON key, and billable API activation.
  - Returns raw text coordinates (`boundingPoly`) but does not natively structure medicine fields without a secondary LLM parsing pipeline.
- **Decision:** **DEFER for initial MVP.** Gemini Flash performs unified visual recognition and structured extraction in a single step. An abstract extraction interface (`BasePrescriptionExtractor`) will allow Cloud Vision to be plugged in later if benchmarking warrants it.

---

## 3. Bhashini (National Language Translation Mission, India)

- **Official Source:** [Bhashini APIs](https://bhashini.gitbook.io/bhashini-apis)
- **Role:** Indian regional language ASR (Speech-to-Text) and TTS (Text-to-Speech) + translation.
- **Considerations:**
  - Requires specialized ULCA API credentials, pipeline config lookups, and asynchronous compute availability.
  - Potential network latency or quota limits during high-traffic hackathons.
- **Decision:** **ISOLATE BEHIND ADAPTER.** For the immediate MVP, support Hindi first with clean browser-based TTS (`st.audio` / browser Web Speech synthesis / offline gTTS fallback). Architecture provides `BaseLanguageService` so Bhashini can be connected as a regional language provider in Phase 5 without touching UI logic.

---

## 4. RxNorm & RxNav REST API (US National Library of Medicine)

- **Official Source:** [RxNav REST API](https://lhncbc.nlm.nih.gov/RxNav/APIs/index.html)
- **Role:** Candidate drug name normalization and concept mapping (`/REST/rxcui.json?name=...`).
- **Critical Limitations:**
  - Heavily US-centric nomenclature.
  - Common Indian commercial brand names (e.g., *Dolo 650*, *Calpol*, *Pan-D*, *Augmentin 625*, *Combiflam*, *Telma-H*) may either not match or map to non-standard national drug codes.
  - A fuzzy match must **never** overwrite or replace the doctor's handwritten text.
- **Decision:** **ADOPT with Strict Disclaimers & Local Indian Essential Drug Reference.** Use an offline curated dictionary of common Indian generic formulations (e.g. Paracetamol, Amoxicillin, Metformin, Pantoprazole, Cetirizine, Azithromycin) combined with optional RxNorm lookup for generic concepts, strictly marked as *supporting external reference*, never altering doctor prescriptions.

---

## 5. openFDA Drug Label API

- **Official Source:** [openFDA Drug Endpoint](https://open.fda.gov/apis/drug/label/how-to-use-the-endpoint/)
- **Role:** General drug purpose, precautions, and administration guidance lookup.
- **Critical Limitations:**
  - US package inserts only. Dosages and contraindications may differ from Indian pharmacopeia (IP).
  - Must never be used to alter written instructions or validate patient-specific dosages.
- **Decision:** **OPTIONAL REFERENCE ONLY.** Isolated in `services/medicine_reference.py`. Presented under an explicit "सामान्य जानकारी (General Reference - US FDA Info)" collapsible section, completely separate from the prescription card.

---

## 6. Streamlit Secrets & Session Management

- **Official Source:** [Streamlit Secrets Guidance](https://docs.streamlit.io/deploy/concepts/secrets)
- **Configuration:** Reads from `st.secrets` in cloud deployment and falls back to `python-dotenv` (`.env`) in local development.
- **Decision:** **ADOPT standard config loader (`app/config.py`).**
