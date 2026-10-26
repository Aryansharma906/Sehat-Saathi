# UX & Accessibility Specification

**Project:** Sehat Saathi (सेहत साथी)  
**Lead:** Agent 4 (UX and Accessibility)  
**Target Audience:** Rural India, users with low digital literacy, family caregivers  
**Primary Language:** Simple Hindi (सरल हिंदी) with bilingual English subtext  

---

## 1. Design & Accessibility Principles

1. **Mobile-First Responsive Layout**: Optimized for vertical handheld screens (360px - 480px width).
2. **Large, High-Contrast Touch Targets**: Minimum 48px touch targets, high contrast green/blue primary actions, amber warning badges.
3. **Short, Simple Hindi Sentences**: Avoid medical jargon (e.g. use "दिन में दो बार - सुबह और शाम" instead of "b.i.d." or "twice daily administration").
4. **Icons Paired with Text**: Every primary button pairs an intuitive icon with clear text (e.g., 📸 फोटो खींचें / अपलोड करें).
5. **No Cluttered Dashboards**: Single sequential task flow:
   - **होम (Home)** ➔ **अपलोड (Scan/Upload)** ➔ **जांचें (Review & Confirm)** ➔ **समझें (Explanation & Voice)** ➔ **रिमाइंडर (Reminders)**.
6. **Prominent Uncertainty Flags**: Ambiguous or uncertain text is rendered with an amber warning card and exclamation mark.
7. **Graceful Voice Assistance**: Optional audio read-aloud button (🔊 बोलकर सुनाएं) for low-literacy users.

---

## 2. Screen-by-Screen Journey

### Screen 1: Home (होम स्क्रीन)
- **Title:** सेहत साथी (Sehat Saathi) — आपका दवा साथी
- **Safety Badge:** ℹ️ यह ऐप केवल आपकी सहायता के लिए है। यह डॉक्टर या फार्मासिस्ट का विकल्प नहीं है।
- **Two Big Action Cards:**
  1. 📸 **नई पर्ची पढ़ें (Scan / Upload Prescription)** [Primary Button]
  2. ⏰ **मेरी दवाओं के रिमाइंडर देखें (View My Medication Reminders)** [Secondary Button]
- **Sample Mode Option:** "बिना पर्ची के डेमो देखें (Try Demo Sample)" for instant testing without camera.

### Screen 2: Prescription Upload & Quality Check (पर्ची की तस्वीर)
- Camera capture (`st.camera_input`) or file uploader (`st.file_uploader`) accepting JPG/PNG.
- Image quality helper:
  - If image is blurry or very low contrast: *"तस्वीर धुंधली लग रही है। कृपया अच्छी रोशनी में दोबारा फोटो लें।"*
  - Preview card with option to retake/replace.
- Single green button: 🚀 **पर्ची से जानकारी निकालें (Extract Details)**

### Screen 3: Review & Confirmation (जांचें और सही करें)
- **Status header:** "कंप्यूटर ने यह पढ़ा है। कृपया नीचे दी गई जानकारी को अपनी पर्ची से मिलाकर जांच लें।"
- **For each medicine found:**
  - Card with:
    - **Original text read from image:** `पर्ची पर लिखा शब्द: [raw_medicine_name]`
    - **Editable Medicine Name:** [Text Input]
    - **Editable Dosage & Strength:** [Text Input]
    - **Timing & Frequency:** [Selectbox / Radio: सुबह, दोपहर, रात / खाने के पहले या बाद]
    - **Uncertainty Warning (if any):** ⚠️ *"यह लिखावट पूरी तरह स्पष्ट नहीं है। कृपया पुष्टि करें।"*
  - Explicit Confirmation checkbox: ☑️ **"मैंने इस दवा के नाम और समय की पुष्टि कर ली है।"**
- Action Button: 💾 **पुष्टि करें और समझाएं (Confirm & Explain)** (Disabled until user confirms or edits).

### Screen 4: Explanation & Audio (दवा को आसान भाषा में समझें)
- Simple Hindi summary breakdown:
  - 💊 **दवा का नाम:** क्या काम आती है (सामान्य जानकारी)
  - 🕒 **कब लेनी है:** स्पष्ट समय (जैसे: सुबह 8:00 बजे, नाश्ते के बाद)
  - 📅 **कितने दिन लेनी है:** (जैसे: 5 दिन तक)
- 🔊 **बोलकर सुनाएं (Read Aloud Button)**
- Educational reference section (clearly demarcated: *"यह सामान्य ज्ञान है, डॉक्टर की पर्ची नहीं"*).

### Screen 5: Reminders & Questions (रिमाइंडर और सवाल)
- List of confirmed active reminders with toggle switch (चालू / बंद).
- Status indicator: **समय पर (Due)**, **आगामी (Upcoming)**.
- Button to mark as taken: 💊 **दवा ले ली (Mark as Taken)**.
- 💬 **पर्ची के बारे में सवाल पूछें (Ask Questions Chatbot)**:
  - Constrained Q&A only regarding the confirmed prescription.
  - Safe boundary alert if user asks for diagnosis or dosage changes.
