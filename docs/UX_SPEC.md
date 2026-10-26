# UX & Accessibility Specification (Rural & Older Adults Edition)

**Project:** Sehat Saathi (सेहत साथी)  
**Lead:** Agent 4 (UX and Accessibility)  
**Target Audience:** Older adults, rural families, users with limited literacy, family caregivers  
**Primary Language:** Simple Hindi (सरल हिंदी) with bilingual English subtext  

---

## 1. Accessibility for Older Adults & Low-Literacy Users

1. **Large Font Toggle (बड़े अक्षर मोड):**
   - A 1-tap switch at the top right increases base font sizes to 1.18rem and button touch-targets to 1.3rem with 1.6 line height for easy reading without glasses.
2. **Photography Guidance for Rural Conditions:**
   - 3 clear visual rules displayed right above the camera/upload control:
     - 📄 **पर्ची को सीधा और समतल रखें** (Keep prescription flat).
     - 💡 **अच्छी रोशनी में रखें** (Avoid harsh shadows).
     - 📐 **चारों कोने दिखने चाहिए** (Keep all four corners in frame).
3. **Recovery Without Losing Work:**
   - Uploaded images, extracted fields, and manual edits are persisted in `st.session_state`. If a user accidentally switches tabs or edits a field, their work is not wiped out.
4. **Icons Paired with Text:**
   - Icons never appear alone. Every primary touchpoint pairs an intuitive symbol with clear words:
     - 📸 पर्ची पढ़ें (Scan)
     - ⏰ रिमाइंडर (Reminders)
     - 🔊 आवाज में सुनें (Listen)
     - 💊 दवा ले ली (Mark Taken)
     - 🗑️ हटाएं (Delete)

---

## 2. Trust, Transparency & Segregation

To avoid confusion, the interface strictly separates 4 tiers of information:
- **स्तर 1 (Tier 1 - Raw Document):** Exact raw words read from the photograph: `पर्ची पर लिखा शब्द: [raw_medicine_name]`.
- **स्तर 2 (Tier 2 - AI Interpretation):** Editable text boxes labeled with candidate medicine name, strength, and frequency.
- **स्तर 3 (Tier 3 - User Confirmation):** Explicit green/amber checkboxes: `☑️ मैंने दवा की जानकारी पर्चे से जांच ली है`.
- **स्तर 4 (Tier 4 - External Reference):** Collapsible box labeled `🏛️ भारतीय स्वास्थ्य संदर्भ (NLEM / Jan Aushadhi)` showing active generic salt and affordable generic options.

---

## 3. Caregiver Assistance & Traceability Flow

- **Caregiver Assistance:** A family member can photograph and verify the prescription for an elderly patient on any smartphone without registering an account.
- **1-Tap WhatsApp Schedule Share:** Once confirmed, a green button formats a clean Hindi WhatsApp message to send to the elder or other caregivers:
  - *“माताजी की दवाओं का समय: 1. Pan-D (सुबह 8:00 बजे खाली पेट), 2. Dolo 650 (रात 8:00 बजे खाने के बाद)。”*
- **Prescription Traceability:** Every saved reminder records the originating prescription date and raw handwritten snippet so caregivers can cross-verify against physical paper.
