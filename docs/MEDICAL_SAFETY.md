# Medical Safety & Validation Invariants

**Project:** Sehat Saathi (सेहत साथी)  
**Safety Lead:** Agent 3 (Medical Safety & Validation)  
**Status:** Mandatory Invariants Enforced in Code & Tests

---

## 1. Core Mission Statement
> **AI assists with reading and explaining. It must NEVER invent, independently guess, or alter medical instructions.**

Sehat Saathi is an assistive tool for patients and caregivers in rural India. It is **not** a diagnostic device, clinical decision support system, or doctor replacement.

---

## 2. The 15 Mandatory Safety Invariants

| Invariant | Description | Enforcing Mechanism |
| :--- | :--- | :--- |
| **RULE 1: Never invent dosage/freq/duration** | If a handwritten field is illegible or missing, it must remain `null` or `UNKNOWN`. Never hallucinate typical or default doses. | Pydantic model validators + extraction prompt constraints |
| **RULE 2: Never silently resolve ambiguous names** | If handwriting could be two different drugs (e.g. *Celexa* vs *Celebrex*, or *Azithral* vs *Augmentin*), it must be flagged with `is_uncertain=True` and presented to the user. | Confidence thresholding + `unresolved_fields` array |
| **RULE 3: Block schedule on unconfirmed critical fields** | A medication reminder cannot be created or activated unless the user has explicitly verified the medicine name, dosage, and frequency. | `user_confirmed` boolean flag required on `MedicineInstruction` |
| **RULE 4: Preserve raw extracted wording** | The app must always show the exact raw text alongside the parsed interpretation so the user can cross-verify against the physical paper. | `raw_medicine_name` and `dose_instruction_raw` preserved in model |
| **RULE 5: Isolate external drug reference info** | General drug knowledge (e.g., from RxNorm or openFDA) must never be presented as doctor's instructions. | Displayed in a visually distinct, labeled educational box |
| **RULE 6: Reference matches are NOT definitive** | A database match on a brand name does not prove that the doctor wrote that specific brand. | Clear disclaimer: *"यह केवल सामान्य संदर्भ है, डॉक्टर का परामर्श नहीं"* |
| **RULE 7: Explicit clinician/pharmacist escalation** | When an important field cannot be read with high certainty, instruct the user to verify with their pharmacist or doctor before taking the pill. | Standard escalation banner displayed in UI and Hindi voice |
| **RULE 8: No diagnosis or treatment recommendation** | App and chatbot must decline diagnostic questions (e.g., "Do I have malaria? What medicine should I take for fever?"). | Hard-coded system prompt boundaries + fallback guardrails |
| **RULE 9: Chatbot cannot override confirmed prescription** | The chatbot must not suggest altering doses or stopping medication contrary to the confirmed prescription. | Strict conversational system prompt |
| **RULE 10: Fail safely on AI provider downtime** | If the Gemini API or network times out or fails, fail with a clear, calm error message; never fabricate mock medicine data as real data. | Graceful try/except handling with user-friendly Hindi notice |
| **RULE 11: No false claims of medication intake** | Showing a reminder does not mean the user took the medicine. Do not log "Medication Taken" without user tap. | Due status indicator vs user confirmation button |
| **RULE 12: No medical-grade accuracy claims** | The UI, README, and documentation must clearly state prototype and assistive nature. | Prominent disclaimer on Home screen and in footer |
| **RULE 13: Zero real patient data in development** | Real patient identifiable documents must never be used for tests or screenshots. | Synthetic prescription test fixtures only |
| **RULE 14: Use synthetic & anonymized test fixtures** | Test suites use predefined synthetic mock data with known ambiguities. | Fixture directory in `tests/fixtures/` |
| **RULE 15: Plain-language uncertainty explanation** | Uncertainty messages must be in simple, non-technical Hindi (e.g., *"दवा का नाम स्पष्ट नहीं पढ़ पाए"* instead of *"OCR low confidence score < 0.6"*). | User-facing localized strings |

---

## 3. Ambiguity & Fallback Protocol

### Critical Fields:
1. **Medicine Name** (`raw_medicine_name` / `candidate_medicine_name`)
2. **Strength & Dose** (`strength`, `dose_instruction_raw`)
3. **Frequency & Timing** (`frequency_raw`, `timing_raw`)

### If ANY critical field has `is_uncertain == True`:
1. The field is highlighted in amber/red in the Review Screen.
2. A prominent alert states:  
   **"चेतावनी: इस दवा का निर्देश स्पष्ट नहीं है। कृपया अपने फार्मासिस्ट या डॉक्टर से पूछें।"**  
   *(Warning: This instruction is not clear. Please check with your pharmacist or doctor.)*
3. The "Save to Schedule" (रिमाइंडर जोड़ें) button is disabled for this item until the user edits or manually confirms it.
