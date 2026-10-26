"""
Internationalization (i18n) & Localization Service for Sehat Saathi
Provides seamless multilingual support across Hindi (हिन्दी), English, and Hinglish.
Ensures accessible, respectful, and culturally appropriate terminology for rural and urban users alike.
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
    "status_offline": {
        "hi": "🟢 सुरक्षित व ऑफलाइन तैयार",
        "en": "🟢 Safe & Offline Ready",
        "hinglish": "🟢 Safe & Offline Ready"
    },
    "btn_large_text": {
        "hi": "🔍 बड़े अक्षर",
        "en": "🔍 Large Text",
        "hinglish": "🔍 Bada Font"
    },
    "lang_picker_label": {
        "hi": "🌐 भाषा / Language",
        "en": "🌐 Language",
        "hinglish": "🌐 Bhasha (Language)"
    },
    "safety_disclaimer": {
        "hi": "ℹ️ <b>महत्वपूर्ण सुरक्षा सूचना:</b> यह ऐप केवल पर्चे को पढ़ने और समझने में मदद करता है। यह किसी डॉक्टर या फार्मासिस्ट का विकल्प नहीं है। किसी भी संदेह में तुरंत डॉक्टर से पूछें।",
        "en": "ℹ️ <b>Important Safety Notice:</b> This app assists in reading and understanding prescriptions. It is not a substitute for a doctor or pharmacist. Consult your doctor if in doubt.",
        "hinglish": "ℹ️ <b>Zaroori Safety Notice:</b> Yeh app keval prescription padhne aur samajhne me madad karta hai. Kisi doctor ka substitute nahi hai. Doubt hone par doctor se milein."
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
        "hi": "आज का शेड्यूल व खुराक",
        "en": "Today's schedule & dosages",
        "hinglish": "Aaj ka schedule aur dosage"
    },
    "card_vitals_title": {
        "hi": "3. स्वास्थ्य जांच",
        "en": "3. Vitals & Health",
        "hinglish": "3. Health Check"
    },
    "card_vitals_desc": {
        "hi": "बीपी, शुगर, SpO2 व AI पूर्वानुमान",
        "en": "BP, Sugar, SpO2 & AI risk prediction",
        "hinglish": "BP, Sugar, SpO2 & AI prediction"
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
        "hi": "⚠️ यदि मरीज को तेज दर्द, सांस लेने में तकलीफ, या बेहोशी हो, तो ऐप छोड़ें और तुरंत कॉल करें:",
        "en": "⚠️ In case of severe chest pain, breathing difficulty, or unconsciousness, exit app and call immediately:",
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
    "extract_btn": {
        "hi": "🚀 पर्ची से दवाएं निकालें (Extract Medicines)",
        "en": "🚀 Extract Medicines from Prescription",
        "hinglish": "🚀 Prescription se Dawaiyan Nikalein"
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
    "listen_audio_btn": {
        "hi": "🔊 आवाज में सुनें",
        "en": "🔊 Listen Aloud",
        "hinglish": "🔊 Bolkar Sunein"
    },
    "save_reminders_btn": {
        "hi": "⏰ पुष्टि की गई दवाओं के रिमाइंडर जोड़ें (Save Reminders)",
        "en": "⏰ Save Confirmed Reminders",
        "hinglish": "⏰ Confirmed Dawaiyon ke Reminder Save Karein"
    },

    # Tab 2: Reminders
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

    # Tab 3: Vitals & Complication Prediction
    "vitals_heading": {
        "hi": "🩺 स्वास्थ्य उपकरण (Vitals) और AI जटिलता पूर्वानुमान",
        "en": "🩺 Health Vitals & AI Complication Prediction",
        "hinglish": "🩺 Health Vitals aur AI Risk Prediction"
    },
    "predict_btn": {
        "hi": "🔮 जटिलता जोखिम की जांच करें (Predict Complication Risk)",
        "en": "🔮 Predict Health Complication Risk",
        "hinglish": "🔮 Risk Jaanch Karein (Predict Risk)"
    },
    "mental_wellness_title": {
        "hi": "🧘 मन की बात — मानसिक स्वास्थ्य व नींद की जांच (Mental Wellness)",
        "en": "🧘 Mental Wellness & Sleep Quality Screener",
        "hinglish": "🧘 Mann ki Shaanti aur Neend ki Jaanch"
    },

    # Tab 4: Facilities
    "facilities_heading": {
        "hi": "🏥 नजदीकी अस्पताल, क्लीनिक और डॉक्टर खोजें",
        "en": "🏥 Nearby Hospitals, Clinics & Doctors",
        "hinglish": "🏥 Paas ke Hospital, Clinic aur Doctor Khojein"
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

    # Tab 5: Chat
    "chat_heading": {
        "hi": "💬 पर्ची के बारे में सवाल पूछें (Ask AI)",
        "en": "💬 Ask Questions About Your Prescription",
        "hinglish": "💬 Prescription ke baare me sawaal poochein"
    },
    "chat_ask_btn": {
        "hi": "उत्तर पूछें (Ask)",
        "en": "Ask AI",
        "hinglish": "Poochein (Ask)"
    },

    # Tab 6: Settings
    "settings_heading": {
        "hi": "⚙️ ऐप सेटिंग्स और डिवाइस इंस्टॉलेशन",
        "en": "⚙️ App Settings & Device Installation",
        "hinglish": "⚙️ App Settings aur Installation"
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
