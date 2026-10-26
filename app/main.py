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
from services.reminder_service import ReminderService
from services.chat_service import PrescriptionChatService
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


# Services
reminder_service = ReminderService()
language_service = SimpleHindiLanguageService()


# Top Header
st.title("💊 सेहत साथी (Sehat Saathi)")
st.caption("ग्रामीण भारत के लिए सरल AI पर्ची वाचक और दवा साथी")

# Safety Disclaimer (Rule 12)
st.markdown("""
<div class="disclaimer-banner">
    ℹ️ <b>महत्वपूर्ण सुरक्षा सूचना:</b> यह ऐप केवल पर्चे को पढ़ने और समझने में मदद करता है। 
    यह किसी डॉक्टर या फार्मासिस्ट का विकल्प नहीं है। किसी भी संदेह में तुरंत डॉक्टर से पूछें।
</div>
""", unsafe_allow_html=True)


# Top Navigation
tab_scan, tab_reminders, tab_chat, tab_settings = st.tabs([
    "📸 पर्ची पढ़ें (Scan)",
    "⏰ रिमाइंडर (Reminders)",
    "💬 सवाल पूछें (Ask)",
    "⚙️ सेटिंग्स (Settings)"
])


# -------------------------------------------------------------
# TAB 1: SCAN & PROCESS PRESCRIPTION
# -------------------------------------------------------------
with tab_scan:
    st.subheader("1. पर्ची की फोटो लें या अपलोड करें")

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
        st.subheader("2. पर्ची की जांच और पुष्टि करें (Review & Verify)")
        st.write("कृपया AI द्वारा पढ़े गए शब्दों को अपने पर्चे से मिलाकर जांच लें:")

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

                med.user_confirmed = st.checkbox(
                    f"☑️ मैंने दवा #{idx+1} ({med.candidate_medicine_name}) की जानकारी पर्चे से जांच ली है",
                    value=med.user_confirmed,
                    key=f"confirm_{idx}"
                )
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
            if st.button("⏰ पुष्टि की गई दवाओं के रिमाइंडर बनाएं (Create Reminders)", type="primary"):
                created_count = 0
                for med in presc.medicines:
                    if med.user_confirmed:
                        created = reminder_service.create_reminders_from_instruction(med)
                        created_count += len(created)
                st.success(f"🎉 कुल {created_count} रिमाइंडर सफलतापूर्वक सेट किए गए! 'रिमाइंडर' टैब में देखें।")
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
        for rem in all_reminders:
            is_due = reminder_service.is_due_now(rem)
            with st.expander(f"💊 {rem.medicine_name} — {rem.timing_label} ({rem.reminder_time})", expanded=is_due):
                if is_due:
                    st.markdown('<span class="due-badge">🔔 अभी लेने का समय है (Due Now)</span>', unsafe_allow_html=True)

                st.write(f"🔹 **मात्रा:** {rem.dosage or '1 खुराक'}")
                st.write(f"🔹 **समय निर्देश:** {rem.food_relation}")
                st.write(f"🔹 **निर्धारित समय:** {rem.reminder_time} बजे")

                col_t1, col_t2 = st.columns(2)
                with col_t1:
                    if rem.taken_today:
                        st.success("✅ आज दवा ले ली गई है")
                    else:
                        if st.button(f"💊 दवा ले ली (Mark Taken)", key=f"taken_{rem.id}"):
                            reminder_service.mark_as_taken(rem.id, True)
                            st.rerun()

                with col_t2:
                    if st.button(f"🗑️ हटाएं (Delete)", key=f"del_{rem.id}"):
                        reminder_service.delete_reminder(rem.id)
                        st.rerun()

    st.markdown("---")
    st.info("ℹ️ **सूचना:** यह वेब ऐप आपके ब्राउज़र के भीतर रिमाइंडर प्रदर्शित करता है। फोन पूरी तरह लॉक या बंद होने पर सिस्टम पुश नोटिफिकेशन नहीं भेजेगा।")


# -------------------------------------------------------------
# TAB 3: CHAT / QUESTIONS
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
