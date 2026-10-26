"""
Sehat Saathi (सेहत साथी) — Main Streamlit Application
AI-assisted prescription reader and medication companion for rural India.
"""

import streamlit as st
import os
import io
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image

# Load environment variables
load_dotenv()

from models.prescription import Prescription, MedicineInstruction, ExtractionStatus
from services.image_processing import ImageProcessingService
from services.prescription_extractor import (
    GeminiMultimodalExtractor,
    MockPrescriptionExtractor,
    BasePrescriptionExtractor
)
from services.language_service import SimpleHindiLanguageService
from services.medicine_reference import MedicineReferenceService
from services.reminder_service import ReminderService
from services.chat_service import PrescriptionChatService
from services.prevention_and_facilities import PreventionAndFacilitiesService
from services.emergency_service import EmergencyService
from services.health_issue_service import HealthIssueService, COMMON_ISSUE_TYPES
from services.progress_tracker_service import ProgressTrackerService
from services.mental_health_service import MentalHealthService
from services.device_data_service import DeviceDataService
from services.complication_prediction_service import ComplicationPredictionService
from models.complication_prediction import ComplicationPredictionInput, RiskTier
from storage.persistence import LocalStorageAdapter


# Streamlit Page Configuration
st.set_page_config(
    page_title="Sehat Saathi | सेहत साथी",
    page_icon="💊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Mobile-First, Accessible, High-Contrast UI
st.markdown("""
<style>
    /* Mobile-first viewport and typography */
    .main {
        max-width: 600px;
        margin: 0 auto;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        font-size: 1.15rem;
        padding: 0.65rem 1rem;
        font-weight: 600;
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .big-primary-btn button {
        background-color: #0b8043 !important;
        color: white !important;
    }
    .uncertain-card {
        background-color: #fff8e1;
        border-left: 6px solid #fbc02d;
        padding: 14px 18px;
        border-radius: 8px;
        margin-bottom: 12px;
    }
    .confirmed-card {
        background-color: #e8f5e9;
        border-left: 6px solid #4caf50;
        padding: 14px 18px;
        border-radius: 8px;
        margin-bottom: 12px;
    }
    .disclaimer-banner {
        background-color: #e3f2fd;
        border-left: 6px solid #1976d2;
        padding: 10px 14px;
        border-radius: 6px;
        font-size: 0.92rem;
        margin-bottom: 15px;
    }
    .due-badge {
        background-color: #ffebee;
        color: #c62828;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# Initialize Session State
if "prescription" not in st.session_state:
    st.session_state.prescription = None
if "image_bytes" not in st.session_state:
    st.session_state.image_bytes = None
if "confirmed_medicines" not in st.session_state:
    st.session_state.confirmed_medicines = []
if "demo_mode" not in st.session_state:
    st.session_state.demo_mode = True  # Defaults to true so app works immediately
if "large_font_mode" not in st.session_state:
    st.session_state.large_font_mode = False


# Top Controls: Accessibility Mode for Older Adults
col_title, col_a11y = st.columns([3, 1])
with col_title:
    st.title("💊 सेहत साथी (Sehat Saathi)")
    st.caption("बुजुर्गों और ग्रामीण भारत के लिए सरल AI पर्ची वाचक और दवा साथी")
with col_a11y:
    st.session_state.large_font_mode = st.toggle("🔍 बड़े अक्षर", value=st.session_state.large_font_mode, help="बुजुर्गों के लिए बड़े और स्पष्ट अक्षर")

if st.session_state.large_font_mode:
    st.markdown("""
    <style>
        .main p, .main span, .main label, .main div {
            font-size: 1.18rem !important;
            line-height: 1.6 !important;
        }
        .stButton>button {
            font-size: 1.3rem !important;
            padding: 0.85rem 1.2rem !important;
        }
    </style>
    """, unsafe_allow_html=True)

# Safety Disclaimer (Rule 12)
st.markdown("""
<div class="disclaimer-banner">
    ℹ️ <b>महत्वपूर्ण सुरक्षा सूचना:</b> यह ऐप केवल पर्चे को पढ़ने और समझने में मदद करता है। 
    यह किसी डॉक्टर या फार्मासिस्ट का विकल्प नहीं है। किसी भी संदेह में तुरंत डॉक्टर से पूछें।
</div>
""", unsafe_allow_html=True)

# Persistent 1-Tap Emergency Calling Bar (India Emergency Agencies)
with st.expander("🚨 आपातकाल में तुरंत मदद (Emergency Call 108 / 112)", expanded=False):
    st.markdown("⚠️ **यदि मरीज को तेज दर्द, सांस लेने में तकलीफ, या बेहोशी हो, तो ऐप छोड़ें और तुरंत कॉल करें:**")
    agencies = EmergencyService.get_emergency_numbers()
    col_em1, col_em2 = st.columns(2)
    for idx, ag in enumerate(agencies):
        target_col = col_em1 if idx % 2 == 0 else col_em2
        with target_col:
            tel_link = EmergencyService.build_tel_link(ag["number"])
            st.markdown(
                f'<a href="{tel_link}" style="text-decoration:none;">'
                f'<div style="background-color:{ag["color"]}; color:white; padding:10px 12px; border-radius:10px; margin-bottom:6px; font-weight:bold; text-align:center;">'
                f'{ag["icon"]} कॉल {ag["number"]} : {ag["name_hindi"]}'
                f'</div></a>',
                unsafe_allow_html=True
            )
            st.caption(ag["desc_hindi"])


# Top Navigation
tab_scan, tab_reminders, tab_vitals, tab_facilities, tab_chat, tab_settings = st.tabs([
    "📸 पर्ची पढ़ें (Scan)",
    "⏰ रिमाइंडर (Reminders)",
    "🩺 जांच व मन की शांति (Vitals & Wellness)",
    "🏥 अस्पताल व बचाव (Clinics & Prevention)",
    "💬 सवाल पूछें (Ask)",
    "⚙️ सेटिंग्स (Settings)"
])


# -------------------------------------------------------------
# TAB 1: SCAN & PROCESS PRESCRIPTION
# -------------------------------------------------------------
with tab_scan:
    st.subheader("1. पर्ची की फोटो लें या अपलोड करें")

    # Accessible Photo Guidance for Rural Users
    with st.expander("📸 साफ और सही फोटो लेने के 3 सरल नियम (Photo Tips)", expanded=False):
        st.markdown("""
        1. 📄 **पर्ची को सीधा और समतल रखें:** मुड़ी हुई पर्ची को हाथ से सीधा करें।
        2. 💡 **अच्छी रोशनी में रखें:** परछाई न पड़ने दें; खिड़की के पास या बल्ब के नीचे रखें।
        3. 📐 **चारों कोने दिखने चाहिए:** फोन को पर्चे के ठीक ऊपर सीधा पकड़ें।
        """)

    st.caption("🟢 **ऑफ़लाइन तैयार:** आपके पुराने सहेजे गए रिमाइंडर बिना इंटरनेट के भी सुरक्षित हैं। नई पर्ची स्कैन करने के लिए नेटवर्क आवश्यक है।")

    # Demo quick-load buttons
    st.markdown("**बिना फोटो के तुरंत टेस्ट करें (Quick Demo):**")
    col_demo1, col_demo2 = st.columns(2)
    with col_demo1:
        if st.button("📝 सामान्य पर्ची (Clean Demo)"):
            extractor = MockPrescriptionExtractor(scenario="clean")
            st.session_state.prescription = extractor.extract_from_image(b"mock")
            st.rerun()
    with col_demo2:
        if st.button("⚠️ अस्पष्ट लिखावट (Ambiguous Demo)"):
            extractor = MockPrescriptionExtractor(scenario="ambiguous")
            st.session_state.prescription = extractor.extract_from_image(b"mock")
            st.rerun()

    st.markdown("---")
    
    # Image Input: File Uploader or Camera
    input_method = st.radio("फोटो का तरीका चुनें:", ["फाइल अपलोड करें (File Upload)", "कैमरे से फोटो लें (Camera)"], horizontal=True)
    uploaded_file = None

    if input_method == "फाइल अपलोड करें (File Upload)":
        uploaded_file = st.file_uploader("पर्चे की तस्वीर चुनें (JPG, PNG)", type=["jpg", "jpeg", "png", "webp"])
    else:
        uploaded_file = st.camera_input("कैमरे से पर्चे की फोटो लें")

    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        st.session_state.image_bytes = file_bytes

        # Validation & Quality Check
        valid, err_msg = ImageProcessingService.validate_file(file_bytes)
        if not valid:
            st.error(err_msg)
        else:
            img, load_err = ImageProcessingService.load_and_normalize(file_bytes)
            if load_err:
                st.error(load_err)
            elif img:
                st.image(img, caption="अपलोड की गई पर्ची का पूर्वावलोकन (Preview)", use_container_width=True)
                quality_ok, quality_warning = ImageProcessingService.assess_quality(img)
                if not quality_ok:
                    st.warning(quality_warning)

                if st.button("🚀 पर्ची से दवाएं निकालें (Extract Medicines)", key="btn_extract"):
                    with st.spinner("AI पर्ची पढ़ रहा है... कृपया प्रतीक्षा करें"):
                        api_key = os.environ.get("GEMINI_API_KEY")
                        if api_key and not st.session_state.demo_mode:
                            extractor = GeminiMultimodalExtractor(api_key=api_key)
                        else:
                            extractor = MockPrescriptionExtractor(scenario="ambiguous" if "ambiguous" in uploaded_file.name.lower() else "clean")
                        
                        st.session_state.prescription = extractor.extract_from_image(file_bytes)
                        st.rerun()

    # Step 2: Review & Confirmation Screen (Feature D)
    if st.session_state.prescription:
        presc: Prescription = st.session_state.prescription
        st.markdown("---")
        
        col_rev_head, col_rev_discard = st.columns([3, 1])
        with col_rev_head:
            st.subheader("2. पर्ची की जांच और पुष्टि करें (Review & Verify)")
            st.write("कृपया AI द्वारा पढ़े गए शब्दों को अपने पर्चे से मिलाकर जांच लें:")
        with col_rev_discard:
            if st.button("🗑️ पूरी पर्ची रद्द करें (Discard)", key="btn_discard_presc", help="इस पर्चे को छोड़ें और नया पर्चा शुरू करें"):
                st.session_state.prescription = None
                st.rerun()

        if presc.patient_name:
            st.info(f"👤 **मरीज का नाम:** {presc.patient_name} | 📅 **तारीख:** {presc.prescription_date or 'अनुपलब्ध'}")

        if presc.has_uncertain_critical_fields():
            st.markdown("""
            <div class="uncertain-card">
                ⚠️ <b>ध्यान दें:</b> कुछ दवाइयों के नाम या मात्रा पर्चे में पूरी तरह स्पष्ट नहीं पढ़े जा सके हैं। 
                कृपया नीचे सही जानकारी भरें और पुष्टि करें।
            </div>
            """, unsafe_allow_html=True)

        confirmed_all = True

        for idx, med in enumerate(presc.medicines):
            with st.container():
                card_class = "uncertain-card" if med.is_uncertain else "confirmed-card"
                st.markdown(f'<div class="{card_class}"><b>दवा #{idx+1}:</b> {med.raw_medicine_name}</div>', unsafe_allow_html=True)
                
                col_a, col_b = st.columns(2)
                with col_a:
                    med.candidate_medicine_name = st.text_input(
                        f"दवा का नाम #{idx+1}",
                        value=med.candidate_medicine_name or med.raw_medicine_name,
                        key=f"med_name_{idx}"
                    )
                    med.strength = st.text_input(
                        f"ताकत/पावर (Strength) #{idx+1}",
                        value=med.strength or "",
                        placeholder="जैसे 500mg (खाली रखें यदि पर्चे में न हो)",
                        key=f"med_strength_{idx}"
                    )
                with col_b:
                    med.dose_instruction_raw = st.text_input(
                        f"खुराक (Dose) #{idx+1}",
                        value=med.dose_instruction_raw or "1 गोली",
                        key=f"med_dose_{idx}"
                    )
                    med.frequency_raw = st.text_input(
                        f"कितनी बार (Frequency) #{idx+1}",
                        value=med.frequency_raw or "दिन में 2 बार (BD)",
                        key=f"med_freq_{idx}"
                    )

                med.timing_raw = st.selectbox(
                    f"लेने का समय #{idx+1}",
                    options=["खाने के बाद (After Food)", "खाने से पहले (Before Food)", "खाली पेट (Empty Stomach)", "रात को सोते समय (At Bedtime)"],
                    index=0,
                    key=f"med_timing_{idx}"
                )

                if med.is_uncertain:
                    st.warning(f"⚠️ अस्पष्टता का कारण: {med.uncertainty_reason or 'हैंडराइटिंग अस्पष्ट'}")

                # Indian Healthcare & Drug Database Grounding (NLEM & Jan Aushadhi)
                ref_info = MedicineReferenceService.lookup_medicine(med.candidate_medicine_name or med.raw_medicine_name)
                if ref_info:
                    with st.expander("🏛️ भारतीय स्वास्थ्य संदर्भ (Indian NLEM / Jan Aushadhi)", expanded=False):
                        st.caption(f"🔹 **मूल जेनेरिक दवा:** {ref_info['generic_name']}")
                        st.caption(f"🔹 **काम:** {ref_info['purpose_hindi']}")
                        if ref_info.get('nlem_listed'):
                            st.caption("✅ भारत सरकार की राष्ट्रीय आवश्यक दवा सूची (NLEM) में शामिल।")
                        if ref_info.get('jan_aushadhi_available'):
                            st.caption("💡 यह दवा प्रधानमंत्री जन औषधि केंद्र पर किफायती दर पर भी मिलती है।")

                col_conf, col_discard_med = st.columns([3, 1])
                with col_conf:
                    med.user_confirmed = st.checkbox(
                        f"☑️ मैंने दवा #{idx+1} ({med.candidate_medicine_name}) की जानकारी पर्चे से जांच ली है",
                        value=med.user_confirmed,
                        key=f"confirm_{idx}"
                    )
                with col_discard_med:
                    if st.button("🗑️ दवा हटाएं", key=f"discard_med_{med.id}", help="यदि यह लाइन दवा नहीं है या आप इसे नहीं सहेजना चाहते"):
                        presc.discard_medicine(med.id)
                        if not presc.medicines:
                            st.session_state.prescription = None
                        st.rerun()

                if not med.user_confirmed:
                    confirmed_all = False

        st.markdown("---")

        # Step 3: Explanation & Reminder Setup (Features E & F)
        if confirmed_all and presc.medicines:
            st.success("✅ सभी दवाओं की पुष्टि हो चुकी है!")

            st.subheader("3. सरल हिंदी में समझें (Plain Hindi Explanation)")
            summary_text = language_service.explain_prescription_summary(presc)
            st.markdown(summary_text)

            # Voice Read Aloud (Feature H)
            if st.button("🔊 आवाज में सुनें (Listen in Hindi Audio)"):
                with st.spinner("आवाज तैयार हो रही है..."):
                    audio_bytes = language_service.generate_speech_audio(summary_text)
                    if audio_bytes:
                        st.audio(audio_bytes, format="audio/mp3")
                    else:
                        st.info("आवाज सेवा वर्तमान में अनुपलब्ध है। कृपया ऊपर लिखा विवरण पढ़ें।")

            st.markdown("---")
            st.subheader("4. दवा रिमाइंडर सेट करें (Set Reminders)")

            # Requirement 3: Check for conflicting instructions with existing schedules
            potential_conflicts = []
            for med in presc.medicines:
                conf = reminder_service.check_potential_conflicts(med)
                if conf:
                    potential_conflicts.extend(conf)

            if potential_conflicts:
                st.markdown("""
                <div class="uncertain-card">
                    ⚠️ <b>खुराक में अंतर मिला (Prescription Conflict Detected):</b><br>
                    यह दवा आपके पहले से सहेजे गए शेड्यूल में अलग खुराक के साथ मौजूद है। 
                    पुराने और नए पर्चे में अंतर होने पर कृपया अपने डॉक्टर या केमिस्ट से परामर्श लें।
                </div>
                """, unsafe_allow_html=True)
                for c in potential_conflicts:
                    st.caption(f"• **{c['medicine_name']}**: {c['reason']}")

            if st.button("⏰ पुष्टि की गई दवाओं के रिमाइंडर जोड़ें (Save Reminders)", type="primary"):
                created_count = 0
                for med in presc.medicines:
                    if med.user_confirmed:
                        created = reminder_service.create_reminders_from_instruction(
                            med,
                            prescription_id=presc.id,
                            prescription_date=presc.prescription_date
                        )
                        created_count += len(created)
                st.success(f"🎉 कुल {created_count} रिमाइंडर सफलतापूर्वक जोड़े गए! पुराने शेड्यूल सुरक्षित हैं।")
        else:
            st.warning("⚠️ रिमाइंडर बनाने के लिए कृपया ऊपर दी गई सभी दवाओं की पुष्टि (चेकबॉक्स टिक) करें।")


# -------------------------------------------------------------
# TAB 2: MEDICATION REMINDERS
# -------------------------------------------------------------
with tab_reminders:
    st.subheader("⏰ आपकी दवाइयों का शेड्यूल")
    st.caption("यह रिमाइंडर आपके फोन में सेव हैं ताकि आप समय पर दवा लेना न भूलें।")

    all_reminders = reminder_service.get_all_reminders()

    if not all_reminders:
        st.info("फिलहाल कोई रिमाइंडर सेट नहीं है। 'पर्ची पढ़ें' टैब से पर्चा स्कैन करके रिमाइंडर जोड़ें।")
    else:
        # Caregiver helper: 1-Tap WhatsApp share (Requirement 5)
        import urllib.parse
        share_lines = ["*💊 सेहत साथी - परिवार/मरीज की दवाओं का शेड्यूल:*"]
        for r in all_reminders:
            if r.enabled:
                share_lines.append(f"• {r.medicine_name}: {r.timing_label} ({r.reminder_time} बजे) - {r.food_relation}")
        encoded_text = urllib.parse.quote("\n".join(share_lines))
        st.markdown(
            f'<a href="https://api.whatsapp.com/send?text={encoded_text}" target="_blank" style="text-decoration:none;">'
            f'<div style="background-color:#25D366; color:white; text-align:center; padding:10px; border-radius:10px; font-weight:bold; margin-bottom:15px;">'
            f'📲 व्हाट्सएप पर परिवार/केयरगिवर को शेड्यूल भेजें (Share on WhatsApp)'
            f'</div></a>',
            unsafe_allow_html=True
        )

        with st.expander("🗑️ पुराने या सभी रिमाइंडर हटाएं (Discard / Clear Reminders)", expanded=False):
            st.caption("यदि आपका इलाज पूरा हो चुका है या आप पुराने शेड्यूल हटाना चाहते हैं:")
            col_disc1, col_disc2 = st.columns(2)
            with col_disc1:
                if st.button("🗑️ केवल बंद (Inactive) रिमाइंडर हटाएं", key="btn_discard_inactive"):
                    count = reminder_service.discard_inactive_reminders()
                    st.success(f"{count} पुराने निष्क्रिय रिमाइंडर हटा दिए गए।")
                    st.rerun()
            with col_disc2:
                confirm_all = st.checkbox("हां, मैं सभी रिमाइंडर हटाना चाहता हूँ", key="confirm_clear_all_rem")
                if confirm_all:
                    if st.button("⚠️ सभी रिमाइंडर हमेशा के लिए हटाएं", type="primary", key="btn_discard_all_rem"):
                        reminder_service.delete_all_reminders()
                        st.success("सभी रिमाइंडर हटा दिए गए हैं।")
                        st.rerun()

        for rem in all_reminders:
            is_due = reminder_service.is_due_now(rem)
            status_symbol = "🟢" if rem.enabled else "⚪ (निष्क्रिय / Inactive)"
            with st.expander(f"{status_symbol} 💊 {rem.medicine_name} — {rem.timing_label} ({rem.reminder_time})", expanded=is_due):
                if is_due:
                    st.markdown('<span class="due-badge">🔔 अभी लेने का समय है (Due Now)</span>', unsafe_allow_html=True)

                st.write(f"🔹 **मात्रा:** {rem.dosage or '1 खुराक'}")
                st.write(f"🔹 **समय निर्देश:** {rem.food_relation}")
                st.write(f"🔹 **निर्धारित समय:** {rem.reminder_time} बजे")
                
                # Traceability (Requirement 3)
                if rem.source_prescription_date or rem.source_raw_text:
                    st.caption(f"📄 **पर्चे का संदर्भ:** तारीख: {rem.source_prescription_date or 'पूर्व रिकॉर्ड'} | पर्चे में लिखा शब्द: '{rem.source_raw_text or rem.medicine_name}'")

                col_t1, col_t2 = st.columns(2)
                with col_t1:
                    if rem.taken_today:
                        st.success("✅ आज दवा ले ली गई है")
                    else:
                        if st.button(f"💊 दवा ले ली (Mark Taken)", key=f"taken_{rem.id}"):
                            reminder_service.mark_as_taken(rem.id, True)
                            st.rerun()

                with col_t2:
                    col_sub1, col_sub2 = st.columns(2)
                    with col_sub1:
                        toggle_lbl = "बंद करें" if rem.enabled else "चालू करें"
                        if st.button(toggle_lbl, key=f"tog_{rem.id}"):
                            reminder_service.toggle_reminder(rem.id)
                            st.rerun()
                    with col_sub2:
                        if st.button(f"🗑️ हटाएं", key=f"del_{rem.id}"):
                            reminder_service.delete_reminder(rem.id)
                            st.rerun()

    st.markdown("---")
    
    # Progress Tracker & Frequent Health Questionnaire (Requirement: Questionnaire & test to track progress)
    tracker_service = ProgressTrackerService()
    with st.expander("📊 स्वास्थ्य सुधार जांच प्रश्नावली (Progress Tracker & Check-in)", expanded=False):
        st.markdown("दवा का असर और आपकी सेहत में सुधार जानने के लिए 3 आसान सवालों के जवाब दें:")
        q_items = ProgressTrackerService.get_questionnaire_items()
        
        ans_feeling = st.radio(q_items[0]["question_hindi"], q_items[0]["options"], key="prog_q_feeling")
        ans_adherence = st.radio(q_items[1]["question_hindi"], q_items[1]["options"], key="prog_q_adherence")
        ans_symptoms = st.radio(q_items[2]["question_hindi"], q_items[2]["options"], key="prog_q_symptoms")

        if st.button("📈 सुधार की जांच करें (Check My Progress)", key="btn_submit_progress"):
            checkin_res = tracker_service.evaluate_checkin(ans_feeling, ans_adherence, ans_symptoms)
            
            st.markdown(f"### आपकी सुधार प्रगति: **{checkin_res.recovery_score}%**")
            st.progress(checkin_res.recovery_score / 100.0)

            if checkin_res.doctor_visit_advised:
                st.markdown(f"""
                <div style="background-color:#fff3e0; border-left:6px solid #f57c00; padding:12px; border-radius:8px; margin-top:10px;">
                    {checkin_res.recommendation_hindi}<br><br>
                    👉 <a href="tel:104" style="color:#d32f2f; font-weight:bold;">📞 104 सरकारी स्वास्थ्य हेल्पलाइन पर डॉक्टर से बात करें</a>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.success(checkin_res.recommendation_hindi)

        past_checkins = tracker_service.get_all_checkins()
        if past_checkins:
            st.markdown("---")
            st.markdown("#### 🕒 पिछली जांच का रिकॉर्ड (Past Progress Records):")
            for pc in past_checkins[:3]:
                st.caption(f"📅 **{pc.timestamp}** — प्रगति: **{pc.recovery_score}%** | *{pc.overall_feeling.split('(')[0]}*")

    st.markdown("---")

    # Treatment Issue Logging & Doctor Notification (Requirement: Record health problems & notify doctor)
    issue_service = HealthIssueService()
    with st.expander("📝 दवा के दौरान होने वाली परेशानी दर्ज करें व डॉक्टर को बताएं (Report Issue to Doctor)", expanded=False):
        st.markdown("दवा लेने के बाद यदि कोई नई परेशानी, चकत्ते, उल्टी या बेचैनी हो, तो यहां दर्ज करें:")

        # Options for medicine
        med_options = [r.medicine_name for r in all_reminders] + ["अन्य दवा / सामान्य"]
        selected_med = st.selectbox("किस दवा से परेशानी महसूस हुई?", options=med_options, key="issue_med_select")
        
        selected_issue = st.selectbox("क्या समस्या हुई?", options=COMMON_ISSUE_TYPES, key="issue_type_select")
        selected_sev = st.radio("समस्या की गंभीरता (Severity):", ["सामान्य (Mild)", "मध्यम (Moderate)", "गंभीर (Severe)"], horizontal=True, key="issue_sev_radio")
        issue_notes = st.text_input("अन्य विवरण (वैकल्पिक):", placeholder="उदा. दवा लेने के 1 घंटे बाद खुजली शुरू हुई", key="issue_notes_input")

        dr_phone = st.text_input("डॉक्टर / केमिस्ट का मोबाइल नंबर (वैकल्पिक):", placeholder="उदा. 9876543210 (व्हाट्सएप के लिए)", key="dr_phone_input")

        if st.button("💾 परेशानी दर्ज करें और डॉक्टर को सूचित करें (Log & Notify Doctor)", key="btn_save_issue"):
            logged = issue_service.log_issue(
                medicine_name=selected_med,
                issue_type=selected_issue,
                severity=selected_sev,
                notes=issue_notes
            )
            st.success("✅ परेशानी सफलतापूर्वक दर्ज कर ली गई है!")

            if logged.is_severe_alert:
                st.markdown("""
                <div style="background-color:#ffebee; border-left:6px solid #d32f2f; padding:12px; border-radius:8px; margin-top:10px;">
                    🚨 <b>अति-आवश्यक चेतावनी (Severe Reaction Alert):</b><br>
                    यह गंभीर एलर्जी या सांस से संबंधित लक्षण हो सकते हैं। 
                    <b>दवा की अगली खुराक तुरंत रोकें</b> और अपने डॉक्टर या 
                    <a href="tel:108" style="color:#d32f2f; font-weight:bold;">108 एम्बुलेंस</a> पर तुरंत संपर्क करें!
                </div>
                """, unsafe_allow_html=True)

            # 1-Tap WhatsApp share to Doctor / Chemist
            patient_name_val = st.session_state.prescription.patient_name if st.session_state.prescription else None
            wa_url = HealthIssueService.generate_whatsapp_share_url(logged, patient_name=patient_name_val, doctor_phone=dr_phone)
            st.markdown(
                f'<a href="{wa_url}" target="_blank" style="text-decoration:none;">'
                f'<div style="background-color:#25D366; color:white; text-align:center; padding:12px; border-radius:10px; font-weight:bold; margin-top:10px;">'
                f'📲 डॉक्टर / केमिस्ट को व्हाट्सएप पर सूचना भेजें (Send to Doctor)'
                f'</div></a>',
                unsafe_allow_html=True
            )

        # Show previously recorded issues
        past_issues = issue_service.get_all_issues()
        if past_issues:
            st.markdown("---")
            st.markdown("#### 📋 पहले दर्ज की गई समस्याएं (Past Recorded Issues):")
            for pi in past_issues[:5]:  # Show top 5
                col_pi_txt, col_pi_del = st.columns([4, 1])
                with col_pi_txt:
                    alert_icon = "🚨" if pi.is_severe_alert else "🔹"
                    st.caption(f"{alert_icon} **{pi.timestamp}** | {pi.medicine_name} — *{pi.issue_type}* ({pi.severity})")
                with col_pi_del:
                    if st.button("🗑️ हटाएं", key=f"del_issue_{pi.id}", help="इस परेशानी रिकॉर्ड को हटाएं"):
                        issue_service.delete_issue(pi.id)
                        st.rerun()

    st.markdown("---")
    st.info("ℹ️ **सूचना:** यह वेब ऐप आपके ब्राउज़र के भीतर रिमाइंडर प्रदर्शित करता है। फोन पूरी तरह लॉक या बंद होने पर सिस्टम पुश नोटिफिकेशन नहीं भेजेगा।")


# -------------------------------------------------------------
# TAB 3: HEALTH DEVICES & MENTAL WELLNESS
# -------------------------------------------------------------
with tab_vitals:
    st.subheader("⌚ स्वास्थ्य उपकरण (Health Devices) और मन की शांति")
    st.caption("घर में इस्तेमाल होने वाले स्वास्थ्य उपकरणों की रीडिंग दर्ज करें या मानसिक स्वास्थ्य जांचें:")

    device_service = DeviceDataService()
    mental_service = MentalHealthService()

    # Part A: Health Devices Vitals Recorder
    with st.expander("🩺 स्वास्थ्य उपकरण से रीडिंग सहेजें (Health Devices Vitals)", expanded=True):
        st.markdown("अपने घर के डिजिटल उपकरण से आई रीडिंग यहां दर्ज करें:")
        
        dev_choice = st.selectbox(
            "उपकरण चुनें (Select Device):",
            [
                "🩺 पल्स ऑक्सीमीटर (Pulse Oximeter - SpO2 / नाड़ी)",
                "🩸 डिजिटल बीपी मॉनिटर (BP Monitor - रक्तचाप)",
                "🍬 डिजिटल ग्लूकोमीटर (Glucometer - शुगर)",
                "🌡️ डिजिटल थर्मामीटर (Thermometer - बुखार)"
            ],
            key="dev_choice_select"
        )

        col_val1, col_val2 = st.columns(2)
        with col_val1:
            if "ऑक्सीमीटर" in dev_choice:
                v_metric = "ऑक्सीजन (SpO2)"
                v_unit = "%"
                v_hint = "उदा. 98"
            elif "बीपी" in dev_choice:
                v_metric = "रक्तचाप (Blood Pressure)"
                v_unit = "mmHg"
                v_hint = "उदा. 120/80"
            elif "ग्लूकोमीटर" in dev_choice:
                v_metric = "रक्त शर्करा (Blood Sugar)"
                v_unit = "mg/dL"
                v_hint = "उदा. 110"
            else:
                v_metric = "शरीर का तापमान (Temperature)"
                v_unit = "°F"
                v_hint = "उदा. 98.6"

            val_input = st.text_input(f"रीडिंग दर्ज करें ({v_metric}):", placeholder=v_hint, key="vital_val_input")

        with col_val2:
            st.caption(f"इकाई (Unit): **{v_unit}**")
            st.caption("स्रोत: **डिजिटल हेल्थ डिवाइस**")

        if st.button("💾 उपकरण रीडिंग सहेजें (Save Reading)", key="btn_save_vital"):
            if val_input.strip():
                rec = device_service.record_reading(
                    device_type=dev_choice.split("(")[0].strip(),
                    metric_name=v_metric,
                    value=val_input,
                    unit=v_unit
                )
                st.success(f"✅ {v_metric} रीडिंग ({val_input} {v_unit}) दर्ज हो गई!")
                if rec.alert_message:
                    st.warning(rec.alert_message)
            else:
                st.warning("कृपया रीडिंग का मान दर्ज करें।")

        # Device Export Import Option (Compatibility)
        with st.expander("📥 डिवाइस डेटा फाइल इंपोर्ट करें (Import Device JSON)", expanded=False):
            st.caption("स्मार्टवॉच या ब्लूटूथ डिवाइस के एक्सपोर्ट किए गए डेटा को सीधे इंपोर्ट करें:")
            sample_json = '[{"device_type": "Pulse Oximeter", "metric_name": "SpO2", "value": "98", "unit": "%"}]'
            json_text = st.text_area("डिवाइस JSON डेटा पेस्ट करें:", value=sample_json, height=70, key="dev_json_area")
            if st.button("डेटा इंपोर्ट करें (Sync Data)", key="btn_import_dev"):
                imp = device_service.import_device_json_data(json_text)
                st.success(f"🎉 {len(imp)} डिवाइस रीडिंग सफलतापूर्वक सिंक हो गईं!")

        # Past Readings
        all_readings = device_service.get_all_readings()
        if all_readings:
            st.markdown("---")
            st.markdown("#### 📋 हालिया उपकरण रीडिंग (Recent Readings):")
            for r in all_readings[:4]:
                col_r_txt, col_r_del = st.columns([4, 1])
                with col_r_txt:
                    st.caption(f"🔹 **{r.timestamp}** — {r.device_type}: **{r.value} {r.unit}** ({r.status_flag})")
                with col_r_del:
                    if st.button("🗑️ हटाएं", key=f"del_vital_{r.id}", help="इस रीडिंग को हटाएं"):
                        device_service.delete_reading(r.id)
                        st.rerun()

    st.markdown("---")

    # Part B: Mental Health & Tele-MANAS (14416)
    with st.expander("🧘 मन की बात — मानसिक स्वास्थ्य व नींद की जांच (Mental Wellness)", expanded=False):
        st.markdown("शारीरिक स्वास्थ्य के साथ-साथ मानसिक शांति भी जरूरी है। इन 3 आसान सवालों के उत्तर दें:")
        
        m_sleep = st.radio(
            "1. रात में नींद कैसी आ रही है?",
            ["अच्छी नींद (Good Sleep)", "कभी-कभी परेशानी (Disturbed)", "बहुत कम नींद (Insomnia / Sleepless)"],
            key="m_sleep_radio"
        )
        m_stress = st.radio(
            "2. क्या किसी बात को लेकर अत्यधिक चिंता या घबराहट रहती है?",
            ["सामान्य (Normal)", "हल्का तनाव (Mild Worry)", "बहुत अधिक चिंता (Severe Anxiety)"],
            key="m_stress_radio"
        )
        m_mood = st.radio(
            "3. मन की स्थिति कैसी है?",
            ["प्रसन्न (Happy / Positive)", "सामान्य (Neutral)", "उदास या अकेलापन (Sad / Low Interest)"],
            key="m_mood_radio"
        )

        if st.button("🌸 मन की स्थिति जांचें (Check Mental Wellness)", key="btn_check_mental"):
            m_res = mental_service.evaluate_mental_wellness(m_sleep, m_stress, m_mood)
            st.markdown(f"### मानसिक शांति स्कोर: **{m_res.wellness_score}%**")
            st.progress(m_res.wellness_score / 100.0)
            st.info(m_res.supportive_advice_hindi)

            if m_res.tele_manas_recommended:
                st.markdown("""
                <div style="background-color:#fce4ec; border-left:6px solid #c2185b; padding:12px; border-radius:8px; margin-top:10px;">
                    🌸 <b>राष्ट्रीय मानसिक स्वास्थ्य हेल्पलाइन (Tele-MANAS - MoHFW):</b><br>
                    मन की बात साझा करने के लिए सरकार की 24x7 मुफ्त और गोपनीय हेल्पलाइन पर सीधे मनोवैज्ञानिक से बात करें:<br><br>
                    👉 <a href="tel:14416" style="background-color:#c2185b; color:white; padding:8px 14px; border-radius:8px; text-decoration:none; font-weight:bold;">
                    📞 14416 पर तुरंत फोन करें (Tele-MANAS Toll-Free)
                    </a>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")

    # Part C: AI / ML Health Complication Risk Prediction
    with st.expander("🤖 AI / ML स्वास्थ्य जटिलता जोखिम पूर्वानुमान (Complication Prediction)", expanded=False):
        st.markdown("""
        यह मशीन लर्निंग (ML) मॉडल आपके रक्तचाप, शुगर, ऑक्सीजन और दवा नियमितता के आधार पर 
        भविष्य में होने वाली स्वास्थ्य जटिलताओं (जैसे दिल का दौरा, स्ट्रोक, शुगर असंतुलन) के जोखिम का पूर्वानुमान लगाता है:
        """)

        col_cp1, col_cp2 = st.columns(2)
        with col_cp1:
            inp_age = st.number_input("मरीज की आयु (Age):", min_value=1, max_value=110, value=58, key="ml_age")
            inp_sys = st.number_input("सिस्टोलिक बीपी (ऊपर का BP):", min_value=60, max_value=240, value=135, key="ml_sys")
            inp_dia = st.number_input("डायस्टोलिक बीपी (नीचे का BP):", min_value=40, max_value=140, value=88, key="ml_dia")
        with col_cp2:
            inp_sugar = st.number_input("ब्लड शुगर (mg/dL):", min_value=40, max_value=500, value=130, key="ml_sugar")
            inp_spo2 = st.number_input("ऑक्सीजन स्तर SpO2 (%):", min_value=60, max_value=100, value=97, key="ml_spo2")
            inp_adh = st.slider("दवा समय पर लेने का प्रतिशत (%):", min_value=0, max_value=100, value=90, key="ml_adh")

        # Multi-day BP trend analysis (Deep Learning time-series simulation)
        with st.expander("📈 पिछले 3-4 दिनों के रक्तचाप का ट्रेंड (Deep Learning Sequence Analysis)", expanded=False):
            st.caption("पिछले दिनों का सिस्टोलिक बीपी कॉमा (,) लगाकर लिखें:")
            bp_seq_str = st.text_input("दैनिक बीपी क्रम (उदा. 125, 130, 142):", value="125, 130, 138", key="ml_bp_seq")

        if st.button("🔮 जटिलता जोखिम की जांच करें (Predict Complication Risk)", key="btn_run_ml_predict"):
            pred_input = ComplicationPredictionInput(
                age=int(inp_age),
                systolic_bp=float(inp_sys),
                diastolic_bp=float(inp_dia),
                blood_sugar=float(inp_sugar),
                spo2=float(inp_spo2),
                adherence_percentage=float(inp_adh),
                active_medications_count=len(all_reminders) if 'all_reminders' in locals() and all_reminders else 2
            )
            
            res = ComplicationPredictionService.predict_complication_risk(pred_input)

            # Display Risk Tier & Score
            tier_badge = "🟢" if res.risk_tier == RiskTier.LOW else ("🟡" if res.risk_tier == RiskTier.MODERATE else "🔴")
            st.markdown(f"### {tier_badge} जोखिम स्कोर: **{res.risk_score_percentage}%** — {res.risk_tier.value}")
            st.progress(res.risk_score_percentage / 100.0)

            st.markdown(res.clinical_guidance_hindi)

            st.markdown("#### 🔍 संभावित स्वास्थ्य जटिलताएं (Potential Complications):")
            for c in res.potential_complications_hindi:
                st.markdown(f"• **{c}**")

            if res.key_risk_factors:
                st.markdown("#### 📊 मुख्य जोखिम कारक (Key Contributing Drivers):")
                for rf in res.key_risk_factors:
                    badge = "⚠️" if rf.impact_level == "चिंताजनक" else "🚨"
                    st.caption(f"{badge} **{rf.feature_name}** ({rf.observed_value}): {rf.explanation_hindi}")

            # Check Deep Learning sequence trajectory
            try:
                trend_vals = [float(x.strip()) for x in bp_seq_str.split(",") if x.strip()]
                if len(trend_vals) >= 2:
                    t_res = ComplicationPredictionService.predict_temporal_trajectory(trend_vals)
                    st.markdown("---")
                    st.markdown(f"📈 **समय-श्रृंखला रुझान (Trajectory):** {t_res['trend_direction']}")
                    st.caption(t_res['warning_message_hindi'])
            except Exception:
                pass

            if res.emergency_dial_advised:
                st.markdown("""
                <div style="background-color:#ffebee; border-left:6px solid #d32f2f; padding:12px; border-radius:8px; margin-top:10px;">
                    🚨 <b>आपातकालीन चेतावनी:</b> महत्वपूर्ण संकेतक संकट सीमा में हैं। 
                    तुरंत <a href="tel:108" style="color:#d32f2f; font-weight:bold;">108 एम्बुलेंस</a> या नजदीकी अस्पताल से संपर्क करें!
                </div>
                """, unsafe_allow_html=True)

            st.caption(f"🔬 *मॉडल: {res.model_name}* | {res.disclaimer}")


# -------------------------------------------------------------
# TAB 4: NEARBY CLINICS, DOCTORS & DISEASE PREVENTION
# -------------------------------------------------------------
with tab_facilities:
    st.subheader("🏥 नजदीकी अस्पताल, क्लीनिक और डॉक्टर खोजें")
    st.caption("अपने फोन के नक्शे (Map) पर एक क्लिक में नजदीकी स्वास्थ्य केंद्र और डॉक्टरों का रास्ता देखें:")

    user_locality = st.text_input("📍 अपना गांव, शहर या कस्बा (वैकल्पिक):", placeholder="उदा. नीमराना, बहराइच, या खाली छोड़ें")

    col_map1, col_map2 = st.columns(2)
    with col_map1:
        phc_url = PreventionAndFacilitiesService.build_maps_search_url("Primary Health Centre PHC Hospital", user_locality)
        st.markdown(
            f'<a href="{phc_url}" target="_blank" style="text-decoration:none;">'
            f'<div style="background-color:#1b5e20; color:white; text-align:center; padding:12px; border-radius:10px; font-weight:bold; margin-bottom:10px;">'
            f'🏥 सरकारी अस्पताल / PHC का रास्ता'
            f'</div></a>',
            unsafe_allow_html=True
        )

        chemist_url = PreventionAndFacilitiesService.build_maps_search_url("Medical Store Chemist Pharmacy", user_locality)
        st.markdown(
            f'<a href="{chemist_url}" target="_blank" style="text-decoration:none;">'
            f'<div style="background-color:#00695c; color:white; text-align:center; padding:12px; border-radius:10px; font-weight:bold; margin-bottom:10px;">'
            f'🏪 नजदीकी मेडिकल स्टोर / केमिस्ट'
            f'</div></a>',
            unsafe_allow_html=True
        )

    with col_map2:
        ja_url = PreventionAndFacilitiesService.build_maps_search_url("Pradhan Mantri Jan Aushadhi Kendra", user_locality)
        st.markdown(
            f'<a href="{ja_url}" target="_blank" style="text-decoration:none;">'
            f'<div style="background-color:#e65100; color:white; text-align:center; padding:12px; border-radius:10px; font-weight:bold; margin-bottom:10px;">'
            f'💊 जन औषधि केंद्र (सस्ती जेनेरिक दवा)'
            f'</div></a>',
            unsafe_allow_html=True
        )

        dr_url = PreventionAndFacilitiesService.build_maps_search_url("Doctor Clinic", user_locality)
        st.markdown(
            f'<a href="{dr_url}" target="_blank" style="text-decoration:none;">'
            f'<div style="background-color:#0277bd; color:white; text-align:center; padding:12px; border-radius:10px; font-weight:bold; margin-bottom:10px;">'
            f'🩺 नजदीकी डॉक्टर व क्लीनिक'
            f'</div></a>',
            unsafe_allow_html=True
        )

    # Online Ordering Guidance (Drugs & Cosmetics Act compliant)
    order_guide = PreventionAndFacilitiesService.get_online_ordering_guide()
    with st.expander("📦 घर बैठे ऑनलाइन दवा कैसे मंगवाएं? (How to Order Online Safely)", expanded=False):
        st.markdown(f'<div class="disclaimer-banner">{order_guide["disclaimer_hindi"]}</div>', unsafe_allow_html=True)
        st.markdown("#### 3 आसान नियम:")
        for s in order_guide["steps"]:
            st.markdown(f"**{s['step_num']}. {s['title']}:** {s['desc']}")

        st.markdown("---")
        st.markdown("#### विश्वसनीय प्लेटफॉर्म और पोर्टल (Trusted Platforms):")
        cols_plat = st.columns(len(order_guide["trusted_platforms"]))
        for col_p, plat in zip(cols_plat, order_guide["trusted_platforms"]):
            with col_p:
                st.markdown(f'[{plat["name"]}]({plat["url"]})')

    # Interactive Facility Map Preview
    import pandas as pd
    sample_facs = PreventionAndFacilitiesService.get_sample_facilities()
    df_map = pd.DataFrame([{"lat": f["latitude"], "lon": f["longitude"]} for f in sample_facs])
    with st.expander("🗺️ स्वास्थ्य केंद्र नक्शा पूर्वावलोकन (Interactive Map Preview)", expanded=False):
        st.map(df_map)
        for f in sample_facs:
            st.caption(f"🔹 **{f['name']}** ({f['type']}) — *{f['timing']}*")

    st.markdown("---")
    st.subheader("🌿 स्वच्छ पर्यावरण और बीमारियों से बचाव (Disease Prevention)")
    st.caption("राष्ट्रीय स्वास्थ्य मिशन (NHM) के दिशा-निर्देशों पर आधारित ग्रामीण स्वास्थ्य और स्वच्छता सलाह:")

    topics = PreventionAndFacilitiesService.get_prevention_topics()
    for topic in topics:
        with st.expander(f"{topic['icon']} {topic['title_hindi']}", expanded=False):
            st.markdown(f"**💡 मुख्य बात:** {topic['subtitle']}")
            for pt in topic["action_points"]:
                st.write(f"• {pt}")
            
            # Audio Read Aloud for low-literacy users
            if st.button(f"🔊 यह सलाह बोलकर सुनें", key=f"audio_prev_{topic['id']}"):
                with st.spinner("सलाह तैयार हो रही है..."):
                    audio_text = f"{topic['title_hindi']}। {topic['subtitle']}। " + " ".join(topic["action_points"])
                    aud = language_service.generate_speech_audio(audio_text)
                    if aud:
                        st.audio(aud, format="audio/mp3")
                    else:
                        st.info("आवाज वर्तमान में अनुपलब्ध है।")


# -------------------------------------------------------------
# TAB 4: CHAT / QUESTIONS
# -------------------------------------------------------------
with tab_chat:
    st.subheader("💬 पर्ची के बारे में सवाल पूछें")
    st.caption("आप अपनी पुष्टि की गई पर्ची और दवाओं के बारे में सरल सवाल पूछ सकते हैं।")

    chat_service = PrescriptionChatService()

    sample_questions = [
        "यह दवा खाने के पहले लेनी है या बाद में?",
        "क्या मुझे यह दवा बुखार में लेनी चाहिए?",
        "क्या यह दवा खाली पेट ले सकते हैं?",
        "डॉक्टर ने यह दवा कितने दिन तक लिखी है?"
    ]

    selected_sample = st.selectbox("अक्सर पूछे जाने वाले सवाल:", ["-- सवाल चुनें या नीचे लिखें --"] + sample_questions)
    
    user_input = st.text_input("अपना सवाल यहां लिखें (हिंदी या आसान शब्दों में):")
    query_to_send = user_input if user_input.strip() else (selected_sample if selected_sample != "-- सवाल चुनें या नीचे लिखें --" else "")

    if st.button("उत्तर पूछें (Ask)", key="btn_ask"):
        if not query_to_send:
            st.warning("कृपया कोई सवाल लिखें।")
        else:
            with st.spinner("उत्तर तैयार किया जा रहा है..."):
                answer = chat_service.ask_question(query_to_send, st.session_state.prescription)
                st.markdown(f"**उत्तर:**\n\n{answer}")


# -------------------------------------------------------------
# TAB 4: SETTINGS
# -------------------------------------------------------------
with tab_settings:
    st.subheader("⚙️ ऐप सेटिंग्स और कॉन्फ़िगरेशन")

    env_api_key = os.environ.get("GEMINI_API_KEY", "")
    key_status = "✅ कॉन्फ़िगर है" if env_api_key else "❌ उपलब्ध नहीं है"
    st.write(f"**Gemini API Key स्थिति:** {key_status}")

    custom_key = st.text_input("कस्टम Gemini API Key दर्ज करें (वैकल्पिक):", value=env_api_key, type="password")
    if custom_key:
        os.environ["GEMINI_API_KEY"] = custom_key

    st.session_state.demo_mode = st.toggle("डेमो / ऑफलाइन मोड का उपयोग करें (Use Mock Mode without API)", value=st.session_state.demo_mode)
    if st.session_state.demo_mode:
        st.info("डेमो मोड सक्रिय है: पर्ची पढ़ने के लिए सिंथेटिक सुरक्षित टेस्ट डेटा का उपयोग किया जाएगा।")

    st.markdown("---")
    if st.button("🗑️ सभी सहेजे गए रिमाइंडर हटाएं (Reset Saved Reminders)"):
        LocalStorageAdapter().clear_all()
        st.success("सभी रिमाइंडर हटा दिए गए हैं।")
        st.rerun()
