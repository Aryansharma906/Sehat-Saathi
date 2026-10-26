"""
Internationalization (i18n) & Localization Service for Sehat Saathi
Provides seamless multilingual support across Hindi (हिन्दी), English, and Hinglish.
Ensures accessible, respectful, and culturally appropriate terminology for rural and urban users alike.
Every screen, tab, label, card, stat banner, doctor portal, dialog, and prompt is localized.
"""

from typing import Dict, Any

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # App Header & Branding
    "app_title": {
        "hi": "💊 सेहत साथी (Sehat Saathi)",
        "en": "💊 Sehat Saathi (Health Companion)",
        "hinglish": "💊 Sehat Saathi (Aapka Health Saathi)"
    },
    "app_subtitle": {
        "hi": "बुजुर्गों और ग्रामीण भारत के लिए सरल व सुरक्षित AI स्वास्थ्य साथी",
        "en": "Simple & safe AI prescription reader and health companion for families",
        "hinglish": "Senior citizens aur parivaar ke liye simple aur safe AI health assistant"
    },
    "app_tagline": {
        "hi": "सुलभ और सुरक्षित स्वास्थ्य साथी • ग्रामीण स्वास्थ्य सेवा",
        "en": "Intelligent & Accessible Health Companion • Rural Healthcare",
        "hinglish": "Accessible aur Safe Health Companion • Rural Healthcare"
    },
    "status_offline": {
        "hi": "🟢 सुरक्षित व ऑफलाइन तैयार",
        "en": "🟢 Safe & Offline Ready",
        "hinglish": "🟢 Safe & Offline Ready"
    },
    "status_active": {
        "hi": "🟢 सक्रिय",
        "en": "🟢 Active",
        "hinglish": "🟢 Active"
    },
    "btn_large_text": {
        "hi": "🔍 बड़े अक्षर",
        "en": "🔍 Large Text",
        "hinglish": "🔍 Bada Font"
    },
    "lang_picker_label": {
        "hi": "🌐 भाषा / Language:",
        "en": "🌐 Language:",
        "hinglish": "🌐 Bhasha (Language):"
    },
    "safety_disclaimer": {
        "hi": "ℹ️ <b>महत्वपूर्ण सुरक्षा सूचना:</b> यह ऐप केवल पर्चे को पढ़ने और समझने में मदद करता है। यह किसी डॉक्टर या फार्मासिस्ट का विकल्प नहीं है। किसी भी संदेह में तुरंत डॉक्टर से पूछें।",
        "en": "ℹ️ <b>Important Safety Notice:</b> This app assists in reading and understanding prescriptions. It is not a substitute for a doctor or pharmacist. Consult your doctor if in doubt.",
        "hinglish": "ℹ️ <b>Zaroori Safety Notice:</b> Yeh app keval prescription padhne aur samajhne me madad karta hai. Kisi doctor ka substitute nahi hai. Doubt hone par doctor se milein."
    },
    "btn_emergency_108": {
        "hi": "🚨 108 आपातकालीन",
        "en": "🚨 108 Emergency",
        "hinglish": "🚨 108 Emergency"
    },

    # Roles & Identity Popover
    "role_doctor": {
        "hi": "👨‍⚕️ डॉक्टर",
        "en": "👨‍⚕️ Doctor",
        "hinglish": "👨‍⚕️ Doctor"
    },
    "role_staff": {
        "hi": "🏥 स्टाफ",
        "en": "🏥 Staff",
        "hinglish": "🏥 Staff"
    },
    "role_patient": {
        "hi": "👤 मरीज",
        "en": "👤 Patient",
        "hinglish": "👤 Mareez"
    },
    "account_popover_btn": {
        "hi": "🔑 लॉगिन / खाता (Account)",
        "en": "🔑 Login / Account",
        "hinglish": "🔑 Login / Account"
    },
    "user_signin_title": {
        "hi": "🔐 उपयोगकर्ता पहचान (User Sign-In)",
        "en": "🔐 User Sign-In & Verification",
        "hinglish": "🔐 User Sign-In"
    },
    "user_signin_caption": {
        "hi": "डॉक्टर, अस्पताल स्टाफ और मरीज अपने इलाज रिकॉर्ड सुरक्षित रखने के लिए साइन-इन करें:",
        "en": "Doctors, hospital staff, and patients sign in to securely access clinical treatment records:",
        "hinglish": "Doctor, hospital staff aur patients apne records safe rakhne ke liye login karein:"
    },
    "btn_google_signin": {
        "hi": "Google खाते से साइन इन करें (Google Sign-In)",
        "en": "Sign in with Google Account",
        "hinglish": "Google account se Sign In karein"
    },
    "quick_role_select": {
        "hi": "तुरंत भूमिका चुनें (1-Click Test Role):",
        "en": "Select Role (1-Click Switch):",
        "hinglish": "Turant Role Chunein (1-Click):"
    },
    "btn_role_pat": {
        "hi": "👤 मरीज (Patient)",
        "en": "👤 Patient",
        "hinglish": "👤 Mareez (Patient)"
    },
    "btn_role_doc": {
        "hi": "👨‍⚕️ डॉक्टर (Doctor)",
        "en": "👨‍⚕️ Doctor",
        "hinglish": "👨‍⚕️ Doctor"
    },
    "btn_role_staff": {
        "hi": "🏥 स्टाफ (Staff)",
        "en": "🏥 Staff",
        "hinglish": "🏥 Staff"
    },
    "login_mobile_abha_header": {
        "hi": "मोबाइल नंबर या आभा (ABHA) आईडी से लॉगिन:",
        "en": "Sign in with Mobile Number or ABHA ID:",
        "hinglish": "Mobile number ya ABHA ID se login:"
    },
    "lbl_patient_name": {
        "hi": "मरीज का नाम:",
        "en": "Patient Name:",
        "hinglish": "Mareez ka Naam:"
    },
    "lbl_mobile_optional": {
        "hi": "मोबाइल नंबर (वैकल्पिक):",
        "en": "Mobile Number (Optional):",
        "hinglish": "Mobile Number (Optional):"
    },
    "lbl_abha_optional": {
        "hi": "ABHA ID (वैकल्पिक):",
        "en": "ABHA ID (Optional):",
        "hinglish": "ABHA ID (Optional):"
    },
    "btn_save_profile": {
        "hi": "💾 प्रोफ़ाइल सहेजें (Save Profile)",
        "en": "💾 Save Profile",
        "hinglish": "💾 Profile Save Karein"
    },
    "msg_profile_saved": {
        "hi": "प्रोफ़ाइल सफलतापूर्वक सहेजी गई!",
        "en": "Profile updated successfully!",
        "hinglish": "Profile successfully save ho gayi!"
    },

    # Visual Home Hub Cards
    "card_scan_title": {
        "hi": "1. पर्ची पढ़ें",
        "en": "1. Scan Prescription",
        "hinglish": "1. Parchi Padhein"
    },
    "card_scan_desc": {
        "hi": "फोटो खींचें या अपलोड करें",
        "en": "Take photo or upload image",
        "hinglish": "Photo kheenche ya upload karein"
    },
    "card_reminders_title": {
        "hi": "2. मेरी दवाएं",
        "en": "2. My Medicines",
        "hinglish": "2. Meri Dawaiyan"
    },
    "card_reminders_desc": {
        "hi": "सक्रिय रिमाइंडर व खुराक",
        "en": "active reminders & schedule",
        "hinglish": "active reminders aur schedule"
    },
    "card_vitals_title": {
        "hi": "3. स्वास्थ्य जांच",
        "en": "3. Vitals & Health",
        "hinglish": "3. Health Check"
    },
    "card_vitals_desc": {
        "hi": "रीडिंग्स व AI जोखिम पूर्वानुमान",
        "en": "readings & AI risk analysis",
        "hinglish": "readings aur AI risk analysis"
    },
    "card_emergency_title": {
        "hi": "4. आपातकाल 108",
        "en": "4. Emergency 108",
        "hinglish": "4. Emergency 108"
    },
    "card_emergency_desc": {
        "hi": "1-टैप एम्बुलेंस व डॉक्टर कॉल",
        "en": "1-Tap ambulance & doctor call",
        "hinglish": "1-Tap ambulance aur doctor call"
    },

    # Apple Health Banner Tiles
    "tile_bp_title": {
        "hi": "💓 रक्तचाप (BP)",
        "en": "💓 Blood Pressure",
        "hinglish": "💓 Blood Pressure (BP)"
    },
    "tile_bp_status": {
        "hi": "🟢 स्थिर",
        "en": "🟢 Stable",
        "hinglish": "🟢 Stable"
    },
    "tile_spo2_title": {
        "hi": "🫁 ऑक्सीजन SpO2",
        "en": "🫁 Oxygen SpO2",
        "hinglish": "🫁 Oxygen SpO2"
    },
    "tile_spo2_status": {
        "hi": "✅ उत्तम",
        "en": "✅ Optimal",
        "hinglish": "✅ Optimal"
    },
    "tile_sugar_title": {
        "hi": "🩸 ब्लड शुगर",
        "en": "🩸 Blood Sugar",
        "hinglish": "🩸 Blood Sugar"
    },
    "tile_sugar_status": {
        "hi": "🟢 नियंत्रित",
        "en": "🟢 Controlled",
        "hinglish": "🟢 Controlled"
    },
    "tile_adherence_title": {
        "hi": "💊 दवा नियमितता",
        "en": "💊 Adherence",
        "hinglish": "💊 Dawai Adherence"
    },
    "tile_doses_taken": {
        "hi": "खुराक ली गई",
        "en": "Doses Taken",
        "hinglish": "Doses Li Gayi"
    },

    # Tabs
    "tab_scan": {
        "hi": "📸 पर्ची पढ़ें (Scan)",
        "en": "📸 Scan Prescription",
        "hinglish": "📸 Parchi Scan"
    },
    "tab_reminders": {
        "hi": "⏰ रिमाइंडर (Reminders)",
        "en": "⏰ Reminders",
        "hinglish": "⏰ Dawai Reminders"
    },
    "tab_vitals": {
        "hi": "🩺 जांच व जोखिम (Vitals & AI)",
        "en": "🩺 Vitals & AI Prediction",
        "hinglish": "🩺 Vitals aur AI Jaanch"
    },
    "tab_facilities": {
        "hi": "🏥 अस्पताल व बचाव (Clinics & Care)",
        "en": "🏥 Clinics & Prevention",
        "hinglish": "🏥 Clinics aur Bachav"
    },
    "tab_chat": {
        "hi": "💬 सवाल पूछें (Ask AI)",
        "en": "💬 Ask AI Questions",
        "hinglish": "💬 Sawaal Poochein"
    },
    "tab_doctor_portal": {
        "hi": "👨‍⚕️ डॉक्टर व स्टाफ पोर्टल (Doctor & Staff)",
        "en": "👨‍⚕️ Doctor & Staff Portal",
        "hinglish": "👨‍⚕️ Doctor aur Staff Portal"
    },
    "tab_settings": {
        "hi": "⚙️ सेटिंग्स (Settings)",
        "en": "⚙️ Settings",
        "hinglish": "⚙️ Settings"
    },

    # Emergency Drawer
    "emergency_drawer_title": {
        "hi": "🚨 आपातकाल में तुरंत मदद (Emergency Call 108 / 112)",
        "en": "🚨 Emergency Helplines (Call 108 / 112)",
        "hinglish": "🚨 Emergency Help (Call 108 / 112)"
    },
    "emergency_instruction": {
        "hi": "⚠️ यदि मरीज को तेज दर्द, सांस लेने में तकलीफ, या बेहोशी हो, तो तुरंत कॉल करें:",
        "en": "⚠️ In case of severe chest pain, breathing difficulty, or unconsciousness, call immediately:",
        "hinglish": "⚠️ Agar tez dard, saans lene me takleef, ya behoshi ho toh turant call karein:"
    },

    # Tab 1: Scan
    "scan_section_title": {
        "hi": "1. पर्ची की फोटो लें या अपलोड करें",
        "en": "1. Take Photo or Upload Prescription",
        "hinglish": "1. Prescription ki Photo lein ya Upload karein"
    },
    "photo_tips_title": {
        "hi": "📸 साफ और सही फोटो लेने के 3 सरल नियम (Photo Tips)",
        "en": "📸 3 Simple Tips for a Clear Prescription Photo",
        "hinglish": "📸 Saaf photo lene ke 3 simple niyam"
    },
    "quick_demo_title": {
        "hi": "बिना फोटो के तुरंत टेस्ट करें (Try Demo Scenarios):",
        "en": "Try Instant Demo Scenarios (No upload needed):",
        "hinglish": "Bina photo upload kiye instant test karein:"
    },
    "demo_clean_btn": {
        "hi": "📝 सामान्य पर्ची (Clean Demo)",
        "en": "📝 Standard Prescription (Clean Demo)",
        "hinglish": "📝 Clean Prescription Demo"
    },
    "demo_ambig_btn": {
        "hi": "⚠️ अस्पष्ट लिखावट (Ambiguous Demo)",
        "en": "⚠️ Unclear Handwriting (Ambiguous Demo)",
        "hinglish": "⚠️ Asphasht Likhawat Demo"
    },
    "input_mode_label": {
        "hi": "फोटो का तरीका चुनें:",
        "en": "Choose photo method:",
        "hinglish": "Photo ka tareeka chunein:"
    },
    "input_mode_upload": {
        "hi": "फाइल अपलोड करें (File Upload)",
        "en": "Upload File (Image)",
        "hinglish": "File Upload karein"
    },
    "input_mode_camera": {
        "hi": "कैमरे से फोटो लें (Camera)",
        "en": "Use Device Camera",
        "hinglish": "Camera se photo lein"
    },
    "file_uploader_label": {
        "hi": "पर्चे की फोटो चुनें (JPG, PNG, WebP):",
        "en": "Select prescription photo (JPG, PNG, WebP):",
        "hinglish": "Parchi ki photo chunein (JPG, PNG, WebP):"
    },
    "camera_input_label": {
        "hi": "कैमरे से पर्चे की तस्वीर खींचें:",
        "en": "Take prescription photo with camera:",
        "hinglish": "Camera se prescription ki photo kheenchein:"
    },
    "preview_caption": {
        "hi": "पर्चे की झलक (Preview)",
        "en": "Prescription Preview",
        "hinglish": "Parchi ki Preview"
    },
    "extract_btn": {
        "hi": "🚀 पर्ची से दवाएं निकालें (Extract Medicines)",
        "en": "🚀 Extract Medicines from Prescription",
        "hinglish": "🚀 Prescription se Dawaiyan Nikalein"
    },
    "spinner_analyzing": {
        "hi": "AI पर्ची की जांच कर रहा है...",
        "en": "AI analyzing prescription...",
        "hinglish": "AI prescription scan kar raha hai..."
    },
    "review_heading": {
        "hi": "2. पर्ची की जांच और पुष्टि करें (Review & Verify)",
        "en": "2. Review & Verify Medicines",
        "hinglish": "2. Parchi ki Jaanch aur Confirm karein"
    },
    "review_sub": {
        "hi": "कृपया AI द्वारा पढ़े गए शब्दों को अपने पर्चे से मिलाकर जांच लें:",
        "en": "Please cross-check extracted medicines with your physical prescription:",
        "hinglish": "Kripya AI dwara padhi gayi dawaiyon ko parchi se milakar check karein:"
    },
    "discard_presc_btn": {
        "hi": "🗑️ पूरी पर्ची रद्द करें (Discard)",
        "en": "🗑️ Discard Entire Prescription",
        "hinglish": "🗑️ Parchi Cancel Karein"
    },
    "discard_med_btn": {
        "hi": "🗑️ दवा हटाएं",
        "en": "🗑️ Remove Medicine",
        "hinglish": "🗑️ Dawai Hatayein"
    },
    "alert_unclear_handwriting": {
        "hi": "⚠️ <b>ध्यान दें:</b> पर्चे की कुछ लिखावट या खुराक अस्पष्ट थी। कृपया नीचे देखकर पुष्टि करें।",
        "en": "⚠️ <b>Attention:</b> Some medicine names or dosages were unclear. Please review and confirm below.",
        "hinglish": "⚠️ <b>Dhyan Dein:</b> Kuch dawaiyon ke naam ya dose aspasht the. Kripya neeche check karke confirm karein."
    },
    "lbl_medicine_field": {
        "hi": "दवा का नाम",
        "en": "Medicine Name",
        "hinglish": "Dawai ka Naam"
    },
    "lbl_strength_field": {
        "hi": "मात्रा / पावर (उदा. 500mg)",
        "en": "Strength (e.g. 500mg)",
        "hinglish": "Power (jaise 500mg)"
    },
    "lbl_dose_field": {
        "hi": "खुराक (उदा. 1 गोली)",
        "en": "Dose (e.g. 1 tablet)",
        "hinglish": "Dose (jaise 1 goli)"
    },
    "lbl_frequency_field": {
        "hi": "दिन में कितनी बार (उदा. दिन में 2 बार)",
        "en": "Frequency (e.g. Twice daily)",
        "hinglish": "Frequency (jaise din me 2 baar)"
    },
    "lbl_timing_field": {
        "hi": "दवा लेने का समय",
        "en": "Medication Timing",
        "hinglish": "Dawai lene ka time"
    },
    "opt_timing_after_food": {
        "hi": "खाने के बाद (After Food)",
        "en": "After Food",
        "hinglish": "Khane ke baad (After Food)"
    },
    "opt_timing_before_food": {
        "hi": "खाने से पहले (Before Food)",
        "en": "Before Food",
        "hinglish": "Khane se pehle (Before Food)"
    },
    "opt_timing_empty_stomach": {
        "hi": "खाली पेट (Empty Stomach)",
        "en": "Empty Stomach",
        "hinglish": "Khaali pet (Empty Stomach)"
    },
    "opt_timing_bedtime": {
        "hi": "रात को सोते समय (At Bedtime)",
        "en": "At Bedtime",
        "hinglish": "Raat ko sote waqt (At Bedtime)"
    },
    "chk_verified_medicine": {
        "hi": "☑️ मैंने पर्चे से मिलान कर लिया",
        "en": "☑️ I verified with prescription",
        "hinglish": "☑️ Maine parchi se check kar liya"
    },
    "ref_title": {
        "hi": "🏛️ भारतीय NLEM व जन औषधि संदर्भ",
        "en": "🏛️ Indian NLEM & Jan Aushadhi Reference",
        "hinglish": "🏛️ Indian NLEM & Jan Aushadhi Reference"
    },
    "ref_generic_salt": {
        "hi": "🔹 मूल जेनेरिक साल्ट:",
        "en": "🔹 Generic Salt:",
        "hinglish": "🔹 Active Generic Salt:"
    },
    "ref_purpose": {
        "hi": "🔹 मुख्य उपयोग:",
        "en": "🔹 Clinical Purpose:",
        "hinglish": "🔹 Mukhya Upyog:"
    },
    "ref_nlem": {
        "hi": "✅ राष्ट्रीय आवश्यक दवा सूची (NLEM) में शामिल।",
        "en": "✅ Listed on National List of Essential Medicines (NLEM).",
        "hinglish": "✅ National List of Essential Medicines (NLEM) me shaamil."
    },
    "ref_jan_aushadhi": {
        "hi": "💡 प्रधानमंत्री जन औषधि केंद्रों पर सस्ती कीमत पर उपलब्ध।",
        "en": "💡 Available at Pradhan Mantri Jan Aushadhi Kendras at affordable price.",
        "hinglish": "💡 PM Jan Aushadhi Kendra par sasti keemat me uplabdh."
    },
    "msg_all_verified": {
        "hi": "✅ सभी दवाओं की पुष्टि हो गई!",
        "en": "✅ All medicines verified!",
        "hinglish": "✅ Sabhi dawaiyon ki verification ho gayi!"
    },
    "heading_summary": {
        "hi": "3. पर्ची का सरल विवरण (Prescription Summary)",
        "en": "3. Prescription Summary",
        "hinglish": "3. Parchi ka Simple Vivaran"
    },
    "listen_audio_btn": {
        "hi": "🔊 आवाज में सुनें",
        "en": "🔊 Listen Aloud",
        "hinglish": "🔊 Bolkar Sunein"
    },
    "spinner_generating_audio": {
        "hi": "आवाज तैयार हो रही है...",
        "en": "Generating speech audio...",
        "hinglish": "Voice audio ban raha hai..."
    },
    "heading_set_reminders": {
        "hi": "4. रिमाइंडर सेट करें और क्लिनिकल रिकॉर्ड में जोड़ें",
        "en": "4. Set Reminders & Sync to Treatment Database",
        "hinglish": "4. Reminder set karein aur records me jodein"
    },
    "save_reminders_btn": {
        "hi": "⏰ पुष्टि की गई दवाओं के रिमाइंडर जोड़ें (Save Reminders)",
        "en": "⏰ Save Confirmed Reminders",
        "hinglish": "⏰ Confirmed Dawaiyon ke Reminder Save Karein"
    },
    "conflict_alert": {
        "hi": "⚠️ पर्चे में टकराव: यह दवा आपके पहले के शेड्यूल में अलग खुराक से दर्ज है।",
        "en": "⚠️ Prescription Conflict Detected: This medication exists in your saved schedule with a different dosage.",
        "hinglish": "⚠️ Conflict Mila: Yeh dawai schedule me alag dose se pehle se darj hai."
    },
    "msg_reminders_saved": {
        "hi": "रिमाइंडर सफलतापूर्वक सेव किए गए और इलाज रिकॉर्ड में जोड़े गए!",
        "en": "reminders saved & synced to your treatment record!",
        "hinglish": "reminders successfully save hue aur record me jud gaye!"
    },
    "msg_verify_required": {
        "hi": "⚠️ रिमाइंडर सक्रिय करने के लिए कृपया ऊपर सभी दवाओं की पुष्टि करें।",
        "en": "⚠️ Please verify all medicines above to activate reminders.",
        "hinglish": "⚠️ Reminder on karne ke liye kripya upar sabhi dawaiyon ko confirm karein."
    },

    # Tab 2: Reminders & Adherence
    "reminders_heading": {
        "hi": "⏰ आपकी दवाइयों का शेड्यूल",
        "en": "⏰ Your Medication Schedule",
        "hinglish": "⏰ Aapki Dawaiyon ka Schedule"
    },
    "reminders_sub": {
        "hi": "यह रिमाइंडर आपके फोन में सेव हैं ताकि आप समय पर दवा लेना न भूलें।",
        "en": "Saved locally on your device so you never miss a dose.",
        "hinglish": "Yeh reminder aapke device me saved hain taaki time par dawai le sakein."
    },
    "no_reminders": {
        "hi": "फिलहाल कोई रिमाइंडर सेट नहीं है। 'पर्ची पढ़ें' टैब से पर्चा स्कैन करके रिमाइंडर जोड़ें।",
        "en": "No active reminders yet. Scan a prescription to set reminders automatically.",
        "hinglish": "Abhi koi reminder set nahi hai. 'Parchi Padhein' tab se scan karke add karein."
    },
    "todays_progress": {
        "hi": "📊 आज की खुराक प्रगति (Today's Progress)",
        "en": "📊 Today's Progress",
        "hinglish": "📊 Aaj ki Dawai Progress"
    },
    "share_wa_btn": {
        "hi": "📲 व्हाट्सएप पर परिवार/केयरगिवर को शेड्यूल भेजें (Share on WhatsApp)",
        "en": "📲 Share Schedule with Family / Caregiver on WhatsApp",
        "hinglish": "📲 WhatsApp par Family/Caregiver ko Schedule Bhejein"
    },
    "mark_taken_btn": {
        "hi": "💊 दवा ले ली (Mark Taken)",
        "en": "💊 Taken (Mark Dose)",
        "hinglish": "💊 Dawai Le Li (Mark Taken)"
    },
    "taken_today_badge": {
        "hi": "✅ आज दवा ले ली गई है",
        "en": "✅ Dose taken today",
        "hinglish": "✅ Aaj dawai le li gayi hai"
    },
    "expander_clear_reminders": {
        "hi": "🗑️ रिमाइंडर हटाएं या रीसेट करें (Clear Reminders)",
        "en": "🗑️ Discard / Clear Reminders",
        "hinglish": "🗑️ Reminders Hatayein ya Reset Karein"
    },
    "btn_discard_inactive": {
        "hi": "🗑️ बंद रिमाइंडर हटाएं (Discard Inactive)",
        "en": "🗑️ Discard Inactive Reminders",
        "hinglish": "🗑️ Band Reminders Hatayein"
    },
    "chk_confirm_delete_all": {
        "hi": "पुष्टि करें: सभी रिमाइंडर हटाएं",
        "en": "Confirm: Delete all reminders",
        "hinglish": "Confirm karein: Sabhi reminders hatayein"
    },
    "btn_delete_all_reminders": {
        "hi": "⚠️ सभी रिमाइंडर हमेशा के लिए हटाएं",
        "en": "⚠️ Delete All Reminders",
        "hinglish": "⚠️ Sabhi Reminders Delete Karein"
    },
    "lbl_morning": {
        "hi": "☀️ सुबह (Morning)",
        "en": "☀️ Morning",
        "hinglish": "☀️ Subah (Morning)"
    },
    "lbl_afternoon": {
        "hi": "⛅ दोपहर (Afternoon)",
        "en": "⛅ Afternoon",
        "hinglish": "⛅ Dopahar (Afternoon)"
    },
    "lbl_night": {
        "hi": "🌙 रात (Night)",
        "en": "🌙 Night",
        "hinglish": "🌙 Raat (Night)"
    },
    "lbl_scheduled": {
        "hi": "⏰ निर्धारित समय",
        "en": "⏰ Scheduled",
        "hinglish": "⏰ Scheduled Time"
    },
    "lbl_due_now": {
        "hi": "🔔 अभी लेनी है (DUE NOW)",
        "en": "🔔 DUE NOW",
        "hinglish": "🔔 Abhi leni hai"
    },
    "btn_deactivate": {
        "hi": "बंद करें",
        "en": "Deactivate",
        "hinglish": "Band Karein"
    },
    "btn_activate": {
        "hi": "चालू करें",
        "en": "Activate",
        "hinglish": "Shuru Karein"
    },
    "btn_delete": {
        "hi": "हटाएं",
        "en": "Delete",
        "hinglish": "Hatayein"
    },
    "expander_progress_tracker": {
        "hi": "📊 स्वास्थ्य सुधार ट्रैकर (Health Progress Check-in)",
        "en": "📊 Health Progress Tracker (Check-in)",
        "hinglish": "📊 Health Progress Check-in"
    },
    "progress_tracker_intro": {
        "hi": "इलाज से सुधार जानने के लिए 3 सरल प्रश्नों के उत्तर दें:",
        "en": "Answer 3 simple questions to check treatment recovery:",
        "hinglish": "Treatment se sudhaar janne ke liye 3 simple sawaalon ke jawab dein:"
    },
    "btn_check_progress": {
        "hi": "📈 सुधार जांचें (Check Progress)",
        "en": "📈 Check Progress",
        "hinglish": "📈 Sudhaar Jaanch Karein"
    },
    "lbl_recovery_score": {
        "hi": "स्वास्थ्य सुधार स्कोर",
        "en": "Recovery Score",
        "hinglish": "Recovery Score"
    },
    "expander_report_issue": {
        "hi": "📝 दवा की समस्या या दुष्प्रभाव दर्ज करें (Report Side Effect)",
        "en": "📝 Report Medicine Issue / Side Effect",
        "hinglish": "📝 Dawai ki Samasya ya Side Effect Darj Karein"
    },
    "lbl_select_medicine": {
        "hi": "दवा चुनें:",
        "en": "Select Medicine:",
        "hinglish": "Dawai Chunein:"
    },
    "lbl_select_issue": {
        "hi": "समस्या का प्रकार:",
        "en": "Issue Type:",
        "hinglish": "Samasya ka Prakaar:"
    },
    "lbl_severity": {
        "hi": "गंभीरता (Severity):",
        "en": "Severity:",
        "hinglish": "Gambheerta:"
    },
    "lbl_notes_optional": {
        "hi": "अतिरिक्त विवरण (वैकल्पिक):",
        "en": "Notes (optional):",
        "hinglish": "Extra Details (Optional):"
    },
    "lbl_doctor_phone_optional": {
        "hi": "डॉक्टर का फोन नंबर (WhatsApp अलर्ट के लिए):",
        "en": "Doctor's phone for WhatsApp alert (optional):",
        "hinglish": "Doctor ka phone (WhatsApp alert ke liye):"
    },
    "btn_log_issue": {
        "hi": "💾 समस्या दर्ज करें (Log Issue)",
        "en": "💾 Log Issue",
        "hinglish": "💾 Samasya Save Karein"
    },
    "msg_issue_logged": {
        "hi": "समस्या सफलतापूर्वक दर्ज की गई।",
        "en": "Issue logged successfully.",
        "hinglish": "Samasya successfully save hui."
    },
    "msg_severe_alert": {
        "hi": "🚨 गंभीर लक्षण दर्ज। तुरंत 108 आपातकालीन सेवा पर संपर्क करें।",
        "en": "🚨 Severe reaction reported. Please contact emergency services (108).",
        "hinglish": "🚨 Gambheer lakshan darj. Turant 108 par call karein."
    },

    # Tab 3: Vitals & Complication Prediction
    "vitals_heading": {
        "hi": "🩺 स्वास्थ्य उपकरण (Vitals) और AI जटिलता पूर्वानुमान",
        "en": "🩺 Health Vitals & AI Complication Prediction",
        "hinglish": "🩺 Health Vitals aur AI Risk Prediction"
    },
    "vitals_sub": {
        "hi": "डिजिटल स्वास्थ्य उपकरण रीडिंग दर्ज करें और बहु-दिवसीय जोखिम पूर्वानुमान देखें:",
        "en": "Record digital health device readings and evaluate multi-day health risks:",
        "hinglish": "Digital health devices ki reading darj karein aur risk forecast dekhein:"
    },
    "expander_vitals_recorder": {
        "hi": "🩺 स्वास्थ्य उपकरण रीडिंग दर्ज करें (Health Device Vitals Recorder)",
        "en": "🩺 Health Device Vitals Recorder",
        "hinglish": "🩺 Health Device Vitals Recorder"
    },
    "lbl_select_device": {
        "hi": "उपकरण चुनें (Select Device):",
        "en": "Select Device:",
        "hinglish": "Device Chunein:"
    },
    "lbl_enter_reading": {
        "hi": "रीडिंग दर्ज करें",
        "en": "Enter Reading",
        "hinglish": "Reading Darj Karein"
    },
    "lbl_unit": {
        "hi": "इकाई (Unit):",
        "en": "Unit:",
        "hinglish": "Unit:"
    },
    "btn_save_reading": {
        "hi": "💾 रीडिंग सहेजें (Save Reading)",
        "en": "💾 Save Reading",
        "hinglish": "💾 Reading Save Karein"
    },
    "msg_reading_saved": {
        "hi": "इलाज डेटाबेस में सफलतापूर्वक सहेजा गया:",
        "en": "Saved to treatment database:",
        "hinglish": "Treatment database me save ho gaya:"
    },
    "lbl_recent_vitals": {
        "hi": "#### 📋 हाल की रीडिंग (Recent Vitals):",
        "en": "#### 📋 Recent Vitals:",
        "hinglish": "#### 📋 Haal ki Readings:"
    },
    "expander_ai_risk": {
        "hi": "🤖 AI / ML स्वास्थ्य जटिलता पूर्वानुमान (Risk Predictor)",
        "en": "🤖 AI / ML Health Complication Risk Predictor",
        "hinglish": "🤖 AI / ML Risk Predictor"
    },
    "ai_risk_sub": {
        "hi": "वाइटल्स और दवा नियमितता के आधार पर संभावित जटिलताओं का पूर्वानुमान:",
        "en": "Predict potential complications based on vital trends and adherence:",
        "hinglish": "Vitals aur adherence ke aadhar par sambhavit risk ka prediction:"
    },
    "lbl_patient_age": {
        "hi": "मरीज की उम्र (Age):",
        "en": "Patient Age:",
        "hinglish": "Mareez ki Umra:"
    },
    "lbl_systolic_bp": {
        "hi": "सिस्टोलिक बीपी / ऊपर का (mmHg):",
        "en": "Systolic BP (mmHg):",
        "hinglish": "Systolic BP (Upar ka):"
    },
    "lbl_diastolic_bp": {
        "hi": "डायस्टोलिक बीपी / नीचे का (mmHg):",
        "en": "Diastolic BP (mmHg):",
        "hinglish": "Diastolic BP (Neeche ka):"
    },
    "lbl_blood_sugar": {
        "hi": "ब्लड शुगर (mg/dL):",
        "en": "Blood Sugar (mg/dL):",
        "hinglish": "Blood Sugar (mg/dL):"
    },
    "lbl_spo2": {
        "hi": "ऑक्सीजन SpO2 (%):",
        "en": "Oxygen SpO2 (%):",
        "hinglish": "Oxygen SpO2 (%):"
    },
    "lbl_adherence_slider": {
        "hi": "दवा नियमितता / Adherence (%):",
        "en": "Medication Adherence (%):",
        "hinglish": "Dawai Niyamitta (%):"
    },
    "lbl_bp_trend_input": {
        "hi": "कई दिनों का सिस्टोलिक बीपी ट्रेंड (कॉमा लगाकर):",
        "en": "Multi-day systolic BP trend (comma separated):",
        "hinglish": "Pichhle dino ka BP trend (comma lagakar):"
    },
    "predict_btn": {
        "hi": "🔮 जटिलता जोखिम की जांच करें (Predict Complication Risk)",
        "en": "🔮 Predict Health Complication Risk",
        "hinglish": "🔮 Risk Jaanch Karein (Predict Risk)"
    },
    "lbl_risk_score": {
        "hi": "जोखिम स्कोर",
        "en": "Risk Score",
        "hinglish": "Risk Score"
    },
    "lbl_potential_complications": {
        "hi": "#### 🔍 संभावित स्वास्थ्य जटिलताएं (Potential Complications):",
        "en": "#### 🔍 Potential Health Complications:",
        "hinglish": "#### 🔍 Sambhavit Health Risk:"
    },
    "lbl_key_risk_factors": {
        "hi": "#### 📊 प्रमुख योगदानकर्ता कारक (Key Risk Factors):",
        "en": "#### 📊 Key Contributing Risk Factors:",
        "hinglish": "#### 📊 Mukhya Risk Factors:"
    },
    "lbl_trajectory": {
        "hi": "📈 रुझान (Trajectory):",
        "en": "📈 Trajectory:",
        "hinglish": "📈 Trend (Trajectory):"
    },
    "msg_emergency_detected": {
        "hi": "🚨 अत्यंत गंभीर लक्षण पाए गए। कृपया तुरंत 108 एम्बुलेंस पर कॉल करें।",
        "en": "🚨 Critical indicators detected. Please contact 108 Emergency immediately.",
        "hinglish": "🚨 Bahut gambheer lakshan mile. Kripya turant 108 par call karein."
    },
    "mental_wellness_title": {
        "hi": "🧘 मन की बात — मानसिक स्वास्थ्य व नींद की जांच (Mental Wellness)",
        "en": "🧘 Mental Wellness & Sleep Quality Screener",
        "hinglish": "🧘 Mann ki Shaanti aur Neend ki Jaanch"
    },
    "mental_wellness_sub": {
        "hi": "नींद की गुणवत्ता और मानसिक तनाव की जांच करें:",
        "en": "Check sleep quality and stress levels:",
        "hinglish": "Neend ki quality aur mental stress ki jaanch karein:"
    },
    "lbl_sleep_quality": {
        "hi": "1. नींद की गुणवत्ता (Sleep Quality):",
        "en": "1. Sleep Quality:",
        "hinglish": "1. Neend ki Quality:"
    },
    "lbl_stress_level": {
        "hi": "2. चिंता व मानसिक तनाव (Worry / Stress):",
        "en": "2. Worry / Stress Levels:",
        "hinglish": "2. Chinta aur Stress:"
    },
    "lbl_mood": {
        "hi": "3. मन का मिजाज (Overall Mood):",
        "en": "3. Overall Mood:",
        "hinglish": "3. Mann ka Mood:"
    },
    "btn_check_wellness": {
        "hi": "🌸 मानसिक संतुलन जांचें (Check Wellness)",
        "en": "🌸 Check Wellness",
        "hinglish": "🌸 Wellness Jaanch Karein"
    },
    "lbl_wellness_score": {
        "hi": "मानसिक संतुलन स्कोर",
        "en": "Wellness Score",
        "hinglish": "Wellness Score"
    },
    "tele_manas_box_title": {
        "hi": "🌸 राष्ट्रीय मानसिक स्वास्थ्य हेल्पलाइन (Tele-MANAS - MoHFW):",
        "en": "🌸 National Mental Health Helpline (Tele-MANAS - MoHFW):",
        "hinglish": "🌸 Rashtriya Mansik Swasthya Helpline (Tele-MANAS):"
    },
    "tele_manas_box_desc": {
        "hi": "प्रशिक्षित मनोवैज्ञानिकों से 24x7 निःशुल्क और गोपनीय परामर्श लें:",
        "en": "Talk confidentially to trained psychologists 24x7 toll-free:",
        "hinglish": "Trained psychologists se 24x7 muft aur confidential baat karein:"
    },
    "tele_manas_call_btn": {
        "hi": "📞 14416 पर कॉल करें (Tele-MANAS Toll-Free)",
        "en": "📞 Call 14416 (Tele-MANAS Toll-Free)",
        "hinglish": "📞 14416 par Call karein"
    },

    # Tab 4: Facilities & Prevention
    "facilities_heading": {
        "hi": "🏥 नजदीकी अस्पताल, क्लीनिक और डॉक्टर खोजें",
        "en": "🏥 Nearby Hospitals, Clinics & Doctors",
        "hinglish": "🏥 Paas ke Hospital, Clinic aur Doctor Khojein"
    },
    "facilities_sub": {
        "hi": "सरकारी अस्पताल, फार्मेसी, जन औषधि और क्लीनिक के लिए 1-टैप गूगल मैप्स नेविगेशन:",
        "en": "1-Tap Google Maps links for government hospitals, pharmacies, and clinics:",
        "hinglish": "Govt hospital, pharmacy, aur clinics ke liye 1-tap Google Maps directions:"
    },
    "lbl_user_locality": {
        "hi": "📍 आपका इलाका / कस्बा / गाँव (वैकल्पिक):",
        "en": "📍 Locality / Town / Village (optional):",
        "hinglish": "📍 Aapka Ilaaka / Gaon (Optional):"
    },
    "maps_phc_btn": {
        "hi": "🏥 सरकारी अस्पताल / PHC का रास्ता",
        "en": "🏥 Public Hospital / PHC Directions",
        "hinglish": "🏥 Govt Hospital / PHC ka Raasta"
    },
    "maps_chemist_btn": {
        "hi": "🏪 नजदीकी मेडिकल स्टोर / केमिस्ट",
        "en": "🏪 Nearby Pharmacy / Chemist",
        "hinglish": "🏪 Paas ka Medical Store"
    },
    "maps_jan_btn": {
        "hi": "💊 जन औषधि केंद्र (सस्ती जेनेरिक दवा)",
        "en": "💊 Jan Aushadhi Kendra (Affordable Generic)",
        "hinglish": "💊 Jan Aushadhi Kendra (Sasti Dawai)"
    },
    "maps_doctor_btn": {
        "hi": "🩺 नजदीकी डॉक्टर व क्लीनिक",
        "en": "🩺 Doctor & Private Clinic Directions",
        "hinglish": "🩺 Paas ke Doctor aur Clinic"
    },
    "heading_rural_prevention": {
        "hi": "🌿 मौसमी बीमारियाँ व बचाव (National Health Mission)",
        "en": "🌿 Rural Disease Prevention (National Health Mission)",
        "hinglish": "🌿 Rural Disease Prevention (NHM)"
    },
    "lbl_key_advice": {
        "hi": "💡 मुख्य सलाह:",
        "en": "💡 Key Advice:",
        "hinglish": "💡 Mukhya Salah:"
    },
    "btn_read_aloud": {
        "hi": "🔊 आवाज में सुनें",
        "en": "🔊 Read Aloud",
        "hinglish": "🔊 Bolkar Sunein"
    },

    # Tab 5: Chat
    "chat_heading": {
        "hi": "💬 पर्ची के बारे में सवाल पूछें (Ask AI)",
        "en": "💬 Ask Questions About Your Prescription",
        "hinglish": "💬 Prescription ke baare me sawaal poochein"
    },
    "chat_sub": {
        "hi": "अपनी पर्ची और दवाओं के बारे में कोई भी प्रश्न पूछें:",
        "en": "Ask questions about your confirmed prescription medications:",
        "hinglish": "Apni parchi aur dawaiyon ke baare me sawaal poochein:"
    },
    "lbl_sample_questions": {
        "hi": "उदाहरण प्रश्न (Sample Questions):",
        "en": "Sample Questions:",
        "hinglish": "Udaaharan Sawaal:"
    },
    "opt_select_or_type": {
        "hi": "-- चुनें या नीचे अपना प्रश्न लिखें --",
        "en": "-- Select or type below --",
        "hinglish": "-- Chunein ya neeche likhein --"
    },
    "lbl_user_question": {
        "hi": "आपका प्रश्न (Your Question):",
        "en": "Your Question:",
        "hinglish": "Aapka Sawaal:"
    },
    "chat_ask_btn": {
        "hi": "उत्तर पूछें (Ask)",
        "en": "Ask AI",
        "hinglish": "Poochein (Ask)"
    },
    "msg_enter_question": {
        "hi": "कृपया अपना प्रश्न लिखें।",
        "en": "Please type a question.",
        "hinglish": "Kripya apna sawaal likhein."
    },
    "spinner_chat_answer": {
        "hi": "उत्तर तैयार हो रहा है...",
        "en": "Preparing answer...",
        "hinglish": "Jawab taiyar ho raha hai..."
    },
    "lbl_answer": {
        "hi": "उत्तर (Answer):",
        "en": "Answer:",
        "hinglish": "Jawab (Answer):"
    },

    # Tab 6: Doctor & Hospital Staff Treatment Portal
    "portal_heading": {
        "hi": "👨‍⚕️ डॉक्टर और अस्पताल स्टाफ पोर्टल (Doctor & Hospital Staff Portal)",
        "en": "👨‍⚕️ Doctor & Hospital Staff Treatment Portal",
        "hinglish": "👨‍⚕️ Doctor aur Hospital Staff Portal"
    },
    "portal_sub": {
        "hi": "अस्पताल के डॉक्टर, नर्स और PHC स्टाफ के लिए मरीज का संपूर्ण इलाज डेटा और क्लिनिकल ट्राइएज प्रबंधन:",
        "en": "Complete patient clinical records and triage management for doctors, nurses, and hospital staff:",
        "hinglish": "Doctor, nurse aur staff ke liye mareez ka complete treatment data aur triage:"
    },
    "portal_disha_notice": {
        "hi": "🏛️ <b>DISHA / ABDM क्लिनिकल डेटाबेस:</b> यह पोर्टल अधिकृत डॉक्टर व स्वास्थ्य स्टाफ को मरीज के पर्चे, उपकरण रीडिंग, दवा नियमितता और AI जोखिम पूर्वानुमान देखने और क्लिनिकल नोट्स जोड़ने की सुविधा देता है।",
        "en": "🏛️ <b>DISHA / ABDM Clinical Database:</b> Authorized clinical staff can view verified prescriptions, vital trends, adherence logs, AI risk predictions, and document treatment notes.",
        "hinglish": "🏛️ <b>DISHA / ABDM Clinical Database:</b> Doctor aur health staff mareez ki parchi, vitals, adherence aur AI risk dekh sakte hain aur clinical notes add kar sakte hain."
    },
    "lbl_select_patient": {
        "hi": "मरीज चुनें (Select Patient for Treatment Review):",
        "en": "Select Patient for Treatment Review:",
        "hinglish": "Mareez Chunein (Select Patient):"
    },
    "lbl_patient_name_card": {
        "hi": "👤 मरीज का नाम:",
        "en": "👤 Patient Name:",
        "hinglish": "👤 Mareez ka Naam:"
    },
    "lbl_age_gender": {
        "hi": "🎂 आयु / लिंग:",
        "en": "🎂 Age / Gender:",
        "hinglish": "🎂 Umra / Gender:"
    },
    "lbl_blood_group": {
        "hi": "🩸 ब्लड ग्रुप:",
        "en": "🩸 Blood Group:",
        "hinglish": "🩸 Blood Group:"
    },
    "lbl_treatment_consent": {
        "hi": "📋 इलाज सहमति:",
        "en": "📋 Treatment Consent:",
        "hinglish": "📋 Treatment Consent:"
    },
    "lbl_consent_granted": {
        "hi": "✅ मरीज द्वारा सहमति दी गई (Consent Granted)",
        "en": "✅ Consent Granted by Patient",
        "hinglish": "✅ Mareez ki Sehmati Mili (Consent Granted)"
    },
    "lbl_consent_pending": {
        "hi": "❌ सहमति लंबित (Pending)",
        "en": "❌ Consent Pending",
        "hinglish": "❌ Sehmati Pending"
    },
    "lbl_emergency_contact": {
        "hi": "📞 इमरजेंसी संपर्क:",
        "en": "📞 Emergency Contact:",
        "hinglish": "📞 Emergency Contact:"
    },
    "lbl_record_id": {
        "hi": "🆔 रिकॉर्ड आईडी:",
        "en": "🆔 Record ID:",
        "hinglish": "🆔 Record ID:"
    },
    "heading_prescriptions": {
        "hi": "#### 📋 मरीज के पर्चे और दवाएं (Prescription Records):",
        "en": "#### 📋 Prescription Records & Medications:",
        "hinglish": "#### 📋 Mareez ki Parchi aur Dawaiyan:"
    },
    "lbl_no_prescriptions": {
        "hi": "इस मरीज का कोई पर्चा दर्ज नहीं है।",
        "en": "No prescriptions recorded for this patient.",
        "hinglish": "Is mareez ka koi parcha darj nahi hai."
    },
    "heading_device_vitals": {
        "hi": "#### 🩺 स्वास्थ्य उपकरण रीडिंग (Device Vitals & Trends):",
        "en": "#### 🩺 Device Vitals & Trends:",
        "hinglish": "#### 🩺 Device Vitals aur Trends:"
    },
    "lbl_no_vitals": {
        "hi": "कोई उपकरण रीडिंग उपलब्ध नहीं है।",
        "en": "No vitals recorded for this patient.",
        "hinglish": "Koi device reading uplabdh nahi hai."
    },
    "heading_adherence_col": {
        "hi": "#### ⏰ दवा नियमितता (Adherence):",
        "en": "#### ⏰ Medication Adherence:",
        "hinglish": "#### ⏰ Dawai Niyamitta (Adherence):"
    },
    "lbl_adherence_rate": {
        "hi": "नियमितता दर:",
        "en": "Adherence Rate:",
        "hinglish": "Niyamitta Rate:"
    },
    "lbl_doses": {
        "hi": "खुराक",
        "en": "doses",
        "hinglish": "khurak"
    },
    "heading_ai_risk_col": {
        "hi": "#### 🤖 AI जोखिम पूर्वानुमान (AI Risk):",
        "en": "#### 🤖 AI Risk Stratification:",
        "hinglish": "#### 🤖 AI Risk Forecast:"
    },
    "lbl_risk_score_field": {
        "hi": "जोखिम स्कोर:",
        "en": "Risk Score:",
        "hinglish": "Risk Score:"
    },
    "lbl_trend_field": {
        "hi": "ट्रेंड:",
        "en": "Trend:",
        "hinglish": "Trend:"
    },
    "lbl_model_field": {
        "hi": "मॉडल:",
        "en": "Model:",
        "hinglish": "Model:"
    },
    "lbl_no_risk_yet": {
        "hi": "जोखिम पूर्वानुमान अभी नहीं हुआ है।",
        "en": "No complication risk predicted yet.",
        "hinglish": "Abhi risk prediction nahi hua hai."
    },
    "heading_add_clinical_note": {
        "hi": "#### ✍️ डॉक्टर / स्टाफ क्लिनिकल सलाह दर्ज करें (Add Treatment Note):",
        "en": "#### ✍️ Add Clinical Treatment Note (Doctor / Staff):",
        "hinglish": "#### ✍️ Clinical Treatment Note Darj Karein:"
    },
    "lbl_clinical_observations": {
        "hi": "क्लिनिकल अवलोकन व दवा निर्देश (Clinical Observations & Advice):",
        "en": "Clinical Observations & Medication Directives:",
        "hinglish": "Clinical Observations aur Dawai Nirdesh:"
    },
    "ph_clinical_observations": {
        "hi": "मरीज की स्थिति, दवा खुराक में बदलाव, या खानपान संबंधी निर्देश दर्ज करें...",
        "en": "Enter patient condition, dose adjustments, or dietary directives...",
        "hinglish": "Mareez ki condition, dose badlav ya nirdesh darj karein..."
    },
    "lbl_triage_priority": {
        "hi": "ट्राइएज स्थिति (Triage Priority):",
        "en": "Triage Priority:",
        "hinglish": "Triage Priority:"
    },
    "triage_normal": {
        "hi": "🟢 सामान्य / स्थिर (Normal / Stable)",
        "en": "🟢 Normal / Stable",
        "hinglish": "🟢 Normal / Stable"
    },
    "triage_followup": {
        "hi": "🟡 फॉलो-अप आवश्यक (Follow-up Required)",
        "en": "🟡 Follow-up Required",
        "hinglish": "🟡 Follow-up Required"
    },
    "triage_urgent": {
        "hi": "🔴 अति-आवश्यक ध्यान (Urgent Attention)",
        "en": "🔴 Urgent Attention",
        "hinglish": "🔴 Urgent Attention"
    },
    "lbl_recommendation_action": {
        "hi": "सिफारिश (Action):",
        "en": "Recommended Action:",
        "hinglish": "Sifarish (Action):"
    },
    "ph_recommendation_action": {
        "hi": "उदा. 7 दिन बाद दोबारा बीपी नापें",
        "en": "e.g. Re-check BP in 7 days",
        "hinglish": "Jaise 7 din baad BP dobara check karein"
    },
    "btn_save_clinical_note": {
        "hi": "💾 क्लिनिकल सलाह सहेजें (Save Clinical Note)",
        "en": "💾 Save Clinical Note",
        "hinglish": "💾 Clinical Note Save Karein"
    },
    "msg_clinical_note_saved": {
        "hi": "✅ क्लिनिकल सलाह सफलतापूर्वक डेटाबेस में सहेज ली गई!",
        "en": "✅ Clinical note saved to treatment database!",
        "hinglish": "✅ Clinical note successfully database me save hua!"
    },
    "msg_enter_clinical_note": {
        "hi": "कृपया क्लिनिकल अवलोकन दर्ज करें।",
        "en": "Please enter clinical observations.",
        "hinglish": "Kripya clinical observations darj karein."
    },
    "heading_past_notes": {
        "hi": "#### 🕒 पूर्व क्लिनिकल नोट्स (Past Staff Notes):",
        "en": "#### 🕒 Past Clinical Notes:",
        "hinglish": "#### 🕒 Pichhle Clinical Notes:"
    },
    "lbl_triage": {
        "hi": "ट्राइएज:",
        "en": "Triage:",
        "hinglish": "Triage:"
    },
    "lbl_advice": {
        "hi": "सलाह:",
        "en": "Action:",
        "hinglish": "Salah:"
    },
    "btn_export_clinical_summary": {
        "hi": "📥 मरीज का हेल्थ कार्ड डाउनलोड करें (Export Patient Clinical Summary JSON)",
        "en": "📥 Download Patient Health Summary Card (JSON)",
        "hinglish": "📥 Mareez ka Health Card Download Karein (JSON)"
    },

    # Tab 7: Settings
    "settings_heading": {
        "hi": "⚙️ ऐप सेटिंग्स और डिवाइस इंस्टॉलेशन",
        "en": "⚙️ App Settings & Device Installation",
        "hinglish": "⚙️ App Settings aur Installation"
    },
    "lbl_gemini_api_key": {
        "hi": "Gemini API Key स्थिति:",
        "en": "Gemini API Key Status:",
        "hinglish": "Gemini API Key Status:"
    },
    "status_configured": {
        "hi": "✅ कॉन्फ़िगर किया गया (Configured)",
        "en": "✅ Configured",
        "hinglish": "✅ Configured"
    },
    "status_not_configured": {
        "hi": "❌ कॉन्फ़िगर नहीं है (Not configured)",
        "en": "❌ Not configured",
        "hinglish": "❌ Configured Nahi Hai"
    },
    "lbl_custom_api_key": {
        "hi": "कस्टम Gemini API Key (वैकल्पिक):",
        "en": "Custom Gemini API Key (optional):",
        "hinglish": "Custom Gemini API Key (Optional):"
    },
    "toggle_demo_mode": {
        "hi": "बिना API के डेमो मोड चलाएं (Demo Mode)",
        "en": "Use Mock / Demo Mode without API",
        "hinglish": "Bina API ke Demo Mode chalayein"
    },
    "info_demo_mode": {
        "hi": "डेमो मोड सक्रिय: सुरक्षित और ऑफलाइन प्रदर्शन के लिए सिंथेटिक मेडिकल डेटा का उपयोग होता है।",
        "en": "Demo Mode Active: Synthetic medical data is used for safe, offline demonstration.",
        "hinglish": "Demo Mode Active: Safe aur offline demonstration ke liye sample medical data use hota hai."
    },
    "expander_install_pwa": {
        "hi": "📱 मोबाइल और कंप्यूटर पर ऐप इंस्टॉल करें (Install App PWA)",
        "en": "📱 Install App on Mobile & PC (PWA)",
        "hinglish": "📱 Mobile aur PC par App Install Karein (PWA)"
    },
    "btn_reset_all_data": {
        "hi": "🗑️ सभी लोकल डेटा रीसेट करें (Reset All Data)",
        "en": "🗑️ Reset All Local Data",
        "hinglish": "🗑️ Sabhi Local Data Reset Karein"
    },
    "msg_all_data_reset": {
        "hi": "सभी रिमाइंडर और शेड्यूल रीसेट कर दिए गए।",
        "en": "All reminders and schedules reset.",
        "hinglish": "Sabhi reminders aur schedule reset ho gaye."
    },

    # Minimalist Footer & Helplines
    "footer_compliance": {
        "hi": "राष्ट्रीय स्वास्थ्य मिशन (NHM) • आयुष्मान भारत डिजिटल मिशन (ABDM) • DISHA मरीज सहमति व गोपनीयता अनुरूप",
        "en": "National Health Mission (NHM) • Ayushman Bharat Digital Mission (ABDM) • DISHA Patient Consent & Privacy Compliant",
        "hinglish": "National Health Mission (NHM) • Ayushman Bharat Digital Mission (ABDM) • DISHA Compliant"
    },
    "footer_helplines": {
        "hi": "📞 <b>24x7 आपातकालीन हेल्पलाइन (निःशुल्क):</b>",
        "en": "📞 <b>24x7 Emergency Helplines (Toll-Free):</b>",
        "hinglish": "📞 <b>24x7 Emergency Helplines (Muft):</b>"
    },
    "footer_ambulance": {
        "hi": "108 एम्बुलेंस",
        "en": "108 Ambulance",
        "hinglish": "108 Ambulance"
    },
    "footer_emergency": {
        "hi": "112 आपातकाल",
        "en": "112 Emergency",
        "hinglish": "112 Emergency"
    },
    "footer_health_advice": {
        "hi": "104 स्वास्थ्य सलाह",
        "en": "104 Health Advice",
        "hinglish": "104 Health Advice"
    },
    "footer_tele_manas": {
        "hi": "14416 टेली-मानस",
        "en": "14416 Tele-MANAS",
        "hinglish": "14416 Tele-MANAS"
    },
    "footer_copyright": {
        "hi": "कॉपीराइट © 2026 सेहत साथी • ग्रामीण भारत और वरिष्ठ नागरिकों के लिए Apple HIG सिद्धांतों पर आधारित • ऑफलाइन तैयार",
        "en": "Copyright © 2026 Sehat Saathi • Designed with Apple HIG principles for Rural India & Older Adults • PWA Offline Ready",
        "hinglish": "Copyright © 2026 Sehat Saathi • Apple HIG principles ke sath Rural India ke liye designed • Offline Ready"
    }
}


def t(key: str, lang: str = "hi") -> str:
    """
    Retrieves the localized string for a given key and language code.
    Fallback hierarchy: lang -> 'hi' -> key.
    """
    entry = TRANSLATIONS.get(key)
    if not entry:
        return key
    return entry.get(lang) or entry.get("hi") or key
