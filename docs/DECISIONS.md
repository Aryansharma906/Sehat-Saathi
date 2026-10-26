# Architectural Decision Records (ADR)

**Project:** Sehat Saathi (सेहत साथी)  
**Lead Coordinator:** Agent 1 (Technical Lead)

---

## ADR 1: Unified Multimodal Vision (Gemini 2.5 Flash) over Multi-stage OCR Pipeline
- **Context:** Reading handwritten Indian prescriptions requires deciphering cursive handwriting and mapping it to clinical entities (drug, strength, frequency).
- **Options Considered:**
  1. *TrOCR / Tesseract + NER Pipeline:* Requires local PyTorch, heavy model weights, slow CPU inference, fragile on abbreviations (e.g. "TDS", "OD", "SOS").
  2. *Google Cloud Vision OCR + LLM:* High quality OCR, but requires separate GCP project billing setup, credentials JSON, and two network hops.
  3. *Gemini 2.5/2.0 Flash Multimodal:* Single API call, native multimodal understanding, native Pydantic JSON schema support (`response_json_schema`), fast, and cost-effective on AI Studio.
- **Decision:** Use Gemini Flash with structured output as the primary extractor, hidden behind `BasePrescriptionExtractor`.
- **Consequence:** Easy to test with mocks; minimal dependencies; zero GPU hardware requirements for users/hackathon judges.

---

## ADR 2: Strict Human-in-the-Loop Confirmation Gate
- **Context:** An AI model may misread handwritten letters or fuzzy-match an incorrect dosage.
- **Decision:** Mandate a "Review & Confirm" screen. Every critical instruction requires explicit user confirmation (`user_confirmed=True`) before any reminder can be saved or activated.
- **Consequence:** Eliminates dangerous automated guessing; adheres to Medical Safety Invariant 3.

---

## ADR 3: In-App Reminder Schedule over Push Notifications
- **Context:** Streamlit runs in the browser. Reliable background OS-level push notifications across mobile/desktop require service workers, native Android wrappers, or paid SMS gateways (Twilio/Gupshup).
- **Decision:** Implement a clean, real-time in-app schedule with active/due status indicators, time-of-day groupings (सुबह / दोपहर / रात), and clear user documentation stating: *"यह डेमो ऐप के अंदर रिमाइंडर दिखाता है; फोन बंद होने पर एसएमएस या बैकग्राउंड पुश नोटिफिकेशन नहीं भेजता।"*
- **Consequence:** High reliability, zero broken promises, completely honest about prototype boundaries.

---

## ADR 4: Indian Essential Medicines Reference + Localized Generic Fallback
- **Context:** RxNorm and openFDA are US-centric and lack many Indian commercial brands (e.g., *Dolo 650*, *Pan-D*, *Combiflam*).
- **Decision:** Bundle a curated Indian National List of Essential Medicines (NLEM) reference table with common Indian formulations and colloquial Hindi names, while keeping RxNorm as an optional secondary query for international active ingredients.
- **Consequence:** Highly relevant to rural Indian context while remaining grounded and truthful.
