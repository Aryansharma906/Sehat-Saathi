# Repository Research & Reusability Matrix

**Project:** Sehat Saathi  
**Date Checked:** 2026-10-26  
**Research Lead:** Agent 2 (API & Repository Researcher)

---

## 1. Candidate Repositories Review

| Repository | Focus / Tech Stack | Strengths | Limitations & Risks | Reusability Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **Kurshidd/prescription-parser** | Vision + LLM parser | Simple pipeline for reading prescription fields | Lack of structured confidence/uncertainty flagging; assumes ideal inputs | Takeaway: Keep pipeline simple, but add strict Pydantic validation and uncertainty checks. |
| **Mohammedvaraliya/Multi-Lingual-Prescription-App** | Gemini Vision + Translation UI | Multi-lingual translation concept; interactive review | Relies heavily on LLM translation without medical grounding; UI complexity | Takeaway: Editable review table pattern is good; adopt structured field editor. |
| **SAHADIYA-M/Medizin** | Medication tracking & alerts | Reminder scheduling models, dosage timing | Desktop-heavy or notification-dependent architecture | Takeaway: In-app schedule list with clear status indicators is far more reliable for web MVPs. |
| **DaZaiOsamu007/PrescriptionOCR_TrOCR** | HuggingFace TrOCR fine-tuned models | Dedicated handwriting OCR | High compute footprint (PyTorch/CUDA), slow CPU inference, fragile on unconstrained Indian doctor handwriting | Reject for MVP: Too heavy for lightweight hackathon deployment; Gemini multimodal vision is faster & more accurate. |
| **yashika641/Pharmalens** | Streamlit + Gemini OCR + drug database | End-to-end user journey in Streamlit | Direct display of raw LLM output without human-in-the-loop verification step | Takeaway: Human confirmation step is our core differentiator; do not auto-save schedules. |
| **abelmou/Healthcare-Assistant** | Multilingual RAG assistant | Q&A interface for health queries | Risk of hallucinated medical triage/diagnosis if unconstrained | Takeaway: Chatbot must have hard guardrails (Rule 8 & 9: no diagnosis, refer to doctor). |
| **Sankeerth5/EzMED** | Medication assistant | Patient workflow and voice concepts | Monolithic codebase; hard-coded dependencies | Reject direct code; adopt decoupled modular design. |
| **navyamishra10/medgemma-prescription-review** | MedGemma / human review prototype | Strong emphasis on human verification step | Specific to fine-tuned MedGemma weights; higher setup friction | Adopt core philosophy: human reviewer must verify every critical medicine field before activation. |
| **pierremontanov/DocIQ** | Document processing pipeline | Clean multi-stage pipeline (Quality -> Extract -> Validate) | Generic document scope, not specialized for clinical safety | Adopt 3-stage pipeline architecture (Image Quality -> Structured Parse -> Human Review). |

---

## 2. Reusability & Architecture Decisions
1. **Do NOT clone or copy wholesale codebases**: Most open-source prototypes lack medical safety constraints, leak unverified LLM hallucinations into UI, or have heavy deep-learning dependencies (TrOCR / CUDA).
2. **Adopt the "Human-in-the-Loop" Pattern**: The single best pattern observed across research is the staged confirmation gate: *Extract -> Flag Ambiguity -> User Confirms/Edits -> Schedule & Remind*.
3. **Clean Decoupled Architecture**: Provide abstract interfaces so providers (Gemini, Vision, Bhashini) can be switched without rewriting the presentation layer.
