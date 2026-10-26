"""
Sehat Saathi (सेहत साथी) — Main Streamlit Application
AI-assisted prescription reader, medication companion, and rural healthcare assistant.
Designed for rural India and older adults with multi-lingual UI/UX, Google Sign-In,
and Clinical Relational Database for Doctors, Nurses, and Healthcare Staff.
"""

import os
import sys
from pathlib import Path

# 1. Ensure project root is always at the top of sys.path regardless of working directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# 2. Prevent Streamlit telemetry permission errors in sandboxed/restricted environments
os.environ.setdefault("STREAMLIT_BROWSER_GATHER_USAGE_STATS", "false")
os.environ.setdefault("STREAMLIT_CONFIG_DIR", "/tmp/.streamlit")

import io
import json
import urllib.parse
from datetime import datetime
from dotenv import load_dotenv
from PIL import Image
import streamlit as st
import pandas as pd

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
from services.i18n import t
from services.auth_service import AuthService, User
from services.clinical_db_service import ClinicalDatabaseService

# Instantiate core services
language_service = SimpleHindiLanguageService()
reminder_service = ReminderService()
device_service = DeviceDataService()
issue_service = HealthIssueService()
tracker_service = ProgressTrackerService()
mental_service = MentalHealthService()
clinical_db = ClinicalDatabaseService()


def seed_initial_clinical_data_if_empty(db: ClinicalDatabaseService):
    """Populates realistic initial patients so doctors and staff can test the portal immediately."""
    patients = db.list_all_patients()
    if not patients:
        # Patient 1: Ramesh Kumar
        u1 = db.upsert_user({
            "id": "user_ramesh",
            "name": "रमेश कुमार (Ramesh Kumar)",
            "email": "ramesh.kumar1965@gmail.com",
            "role": "patient",
            "phone": "9123456789",
            "abha_id": "91-1234-5678-9012"
        })
        p1 = db.upsert_patient({
            "id": "pat_ramesh",
            "user_id": u1,
            "name": "रमेश कुमार (Ramesh Kumar)",
            "age": 58,
            "gender": "पुरुष (Male)",
            "blood_group": "B+",
            "emergency_contact": "9876500000",
            "consent_shared_treatment": 1
        })
        db.save_prescription(
            patient_id=p1,
            doctor_name="डॉ. अदिति शर्मा (Dr. Aditi Sharma, MD)",
            clinic_name="नीमराना सामुदायिक स्वास्थ्य केंद्र (CHC)",
            prescription_date="2026-10-24",
            raw_text="Tab Amlodipine 5mg OD pc, Tab Metformin 500mg BD pc",
            verified_medicines=[
                {"candidate_medicine_name": "Amlodipine 5mg", "dose_instruction_raw": "1 गोली", "frequency_raw": "सुबह 1 बार", "timing_raw": "खाने के बाद"},
                {"candidate_medicine_name": "Metformin 500mg", "dose_instruction_raw": "1 गोली", "frequency_raw": "दिन में 2 बार", "timing_raw": "खाने के बाद"}
            ]
        )
        db.save_vital(p1, "डिजिटल बीपी मॉनिटर", "रक्तचाप (Blood Pressure)", "136/86", "mmHg", "उच्च रक्तचाप (High BP Warning)")
        db.save_vital(p1, "पल्स ऑक्सीमीटर", "ऑक्सीजन (SpO2)", "98", "%", "सामान्य (Normal)")
        db.save_vital(p1, "डिजिटल ग्लूकोमीटर", "रक्त शर्करा (Blood Sugar)", "138", "mg/dL", "सामान्य (Normal)")
        db.record_adherence(p1, "Amlodipine 5mg", "1 गोली", "सुबह", "08:00", taken_status=True)
        db.record_adherence(p1, "Metformin 500mg", "1 गोली", "दोपहर", "13:30", taken_status=True)
        db.save_complication_prediction(
            patient_id=p1,
            risk_score=26.4,
            risk_tier="सामान्य जोखिम (Low Risk)",
            systolic_bp=136.0,
            diastolic_bp=86.0,
            blood_sugar=138.0,
            spo2=98.0,
            adherence_pct=92.0,
            trajectory="स्थिर (Stable)",
            model_name="EnsembleClinicalClassifier"
        )
        db.add_staff_clinical_note(
            patient_id=p1,
            staff_id="doc_aiims_001",
            staff_name="डॉ. अदिति शर्मा (Dr. Aditi Sharma, MD)",
            staff_role="Physician / Doctor",
            observation_notes="मरीज का रक्तचाप हल्का बढ़ा हुआ है। दवा नियमित लेने की सलाह दी गई। 15 दिन बाद फॉलो-अप आवश्यक।",
            triage_status="सामान्य फॉलो-अप (Follow-up Required)",
            recommended_action="कम नमक और नियमित सुबह की सैर।"
        )

        # Patient 2: Geeta Devi (High BP crisis sample for triage demonstration)
        u2 = db.upsert_user({
            "id": "user_geeta",
            "name": "गीता देवी (Geeta Devi)",
            "email": "geeta.devi@example.com",
            "role": "patient",
            "phone": "9876543210",
            "abha_id": "91-8899-7766-5544"
        })
        p2 = db.upsert_patient({
            "id": "pat_geeta",
            "user_id": u2,
            "name": "गीता देवी (Geeta Devi)",
            "age": 63,
            "gender": "महिला (Female)",
            "blood_group": "O+",
            "emergency_contact": "108",
            "consent_shared_treatment": 1
        })
        db.save_vital(p2, "डिजिटल बीपी मॉनिटर", "रक्तचाप (Blood Pressure)", "162/98", "mmHg", "अत्यधिक उच्च रक्तचाप (Crisis Warning)")
        db.save_complication_prediction(
            patient_id=p2,
            risk_score=78.5,
            risk_tier="उच्च जोखिम (High Risk)",
            systolic_bp=162.0,
            diastolic_bp=98.0,
            blood_sugar=210.0,
            spo2=94.0,
            adherence_pct=60.0,
            trajectory="तेजी से बढ़ता (Worsening)",
            model_name="EnsembleClinicalClassifier"
        )

seed_initial_clinical_data_if_empty(clinical_db)


# Streamlit Page Configuration
st.set_page_config(
    page_title="Sehat Saathi | सेहत साथी",
    page_icon="💊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Initialize Session State
if "app_lang" not in st.session_state:
    st.session_state.app_lang = "hi"
if "current_user" not in st.session_state:
    # Default patient profile
    st.session_state.current_user = AuthService.create_google_demo_user(role="patient")
if "prescription" not in st.session_state:
    st.session_state.prescription = None
if "image_bytes" not in st.session_state:
    st.session_state.image_bytes = None
if "confirmed_medicines" not in st.session_state:
    st.session_state.confirmed_medicines = []
if "demo_mode" not in st.session_state:
    st.session_state.demo_mode = True
if "large_font_mode" not in st.session_state:
    st.session_state.large_font_mode = False

# Ensure active patient profile exists in database
curr_u = st.session_state.current_user
clinical_db.upsert_user(curr_u.model_dump())
if curr_u.role == "patient":
    curr_pat_id = f"pat_{curr_u.id}"
    if not clinical_db.get_patient(curr_pat_id):
        clinical_db.upsert_patient({
            "id": curr_pat_id,
            "user_id": curr_u.id,
            "name": curr_u.name,
            "age": 58,
            "gender": "पुरुष (Male)",
            "blood_group": "B+",
            "emergency_contact": curr_u.phone or "108",
            "consent_shared_treatment": 1
        })


# Custom CSS & PWA Meta for Cross-Platform Compatibility (iOS, Android & Desktop Web)
st.markdown("""
<!-- PWA & Mobile WebApp Compatibility Tags -->
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="सेहत साथी">
<meta name="mobile-web-app-capable" content="yes">
<meta name="theme-color" content="#047857">
<link rel="manifest" href="static/manifest.json">
<link rel="apple-touch-icon" href="static/icon-192.png">

<script>
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
      navigator.serviceWorker.register('/static/sw.js').catch(function(err) {});
    });
  }
</script>

<style>
    /* Apple Human Interface Typography & Canvas */
    :root {
        --apple-bg: #f5f5f7;
        --apple-card: #ffffff;
        --apple-text: #1d1d1f;
        --apple-subtext: #86868b;
        --apple-blue: #0071e3;
        --apple-green: #34c759;
        --apple-red: #ff3b30;
        --apple-orange: #ff9500;
        --apple-border: rgba(0, 0, 0, 0.08);
    }

    html, body, [class*="css"], .stApp {
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Helvetica Neue", Arial, sans-serif !important;
        background-color: #f5f5f7 !important;
        color: #1d1d1f !important;
        -webkit-font-smoothing: antialiased;
        letter-spacing: -0.012em;
    }

    /* Apple-style floating main card */
    @media (min-width: 769px) {
        .main {
            max-width: 940px !important;
            margin: 24px auto !important;
            background: #ffffff !important;
            border-radius: 28px !important;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.04), 0 2px 8px rgba(0, 0, 0, 0.02) !important;
            padding: 32px 38px !important;
            border: 1px solid rgba(0, 0, 0, 0.06) !important;
        }
    }
    @media (max-width: 768px) {
        .main {
            max-width: 100% !important;
            padding: 10px 14px !important;
            background: #ffffff !important;
        }
        body {
            padding-top: env(safe-area-inset-top);
            padding-bottom: env(safe-area-inset-bottom);
            padding-left: env(safe-area-inset-left);
            padding-right: env(safe-area-inset-right);
        }
    }

    /* Apple Glassmorphic Brand Header */
    .apple-header {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(20px) saturate(180%);
        -webkit-backdrop-filter: blur(20px) saturate(180%);
        border-radius: 22px;
        border: 1px solid rgba(0, 0, 0, 0.08);
        padding: 18px 22px;
        margin-bottom: 14px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
    }

    /* Apple-style Segmented Control Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background-color: #f5f5f7;
        padding: 5px;
        border-radius: 980px;
        border: 1px solid #e5e5ea;
        margin-bottom: 22px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 42px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 980px;
        color: #86868b;
        font-size: 0.94rem;
        font-weight: 500;
        padding: 6px 16px;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
        border: none !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        color: #1d1d1f !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08) !important;
        font-weight: 600 !important;
    }

    /* Apple Pill Primary CTA Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 980px !important;
        font-size: 1.08rem !important;
        padding: 0.72rem 1.4rem !important;
        font-weight: 600 !important;
        min-height: 48px !important;
        border: none !important;
        background: #0071e3 !important;
        color: #ffffff !important;
        box-shadow: 0 2px 8px rgba(0, 113, 227, 0.22) !important;
        transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1) !important;
        letter-spacing: -0.01em;
    }
    .stButton>button:hover {
        background: #0077ed !important;
        transform: scale(1.01) !important;
        box-shadow: 0 6px 18px rgba(0, 113, 227, 0.32) !important;
    }
    .stButton>button:active {
        transform: scale(0.98) !important;
    }

    /* Apple Health Action Hub Cards */
    .hub-card {
        border-radius: 20px;
        padding: 16px 14px;
        color: #ffffff;
        text-align: center;
        box-shadow: 0 4px 18px rgba(0,0,0,0.06);
        transition: transform 0.22s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.22s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .hub-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
    }

    /* Apple Subtle Alert & Notice Cards */
    .uncertain-card {
        background-color: #fff9f0;
        border-left: 5px solid #ff9500;
        padding: 14px 18px;
        border-radius: 16px;
        margin-bottom: 12px;
        font-size: 1.02rem;
        color: #9a4d00;
        border-top: 1px solid rgba(255, 149, 0, 0.15);
        border-right: 1px solid rgba(255, 149, 0, 0.15);
        border-bottom: 1px solid rgba(255, 149, 0, 0.15);
    }
    .confirmed-card {
        background-color: #f6fcf8;
        border-left: 5px solid #34c759;
        padding: 14px 18px;
        border-radius: 16px;
        margin-bottom: 12px;
        font-size: 1.02rem;
        color: #19692c;
        border-top: 1px solid rgba(52, 199, 89, 0.15);
        border-right: 1px solid rgba(52, 199, 89, 0.15);
        border-bottom: 1px solid rgba(52, 199, 89, 0.15);
    }
    .disclaimer-banner {
        background-color: #f5f8ff;
        border-left: 5px solid #0071e3;
        padding: 12px 18px;
        border-radius: 16px;
        font-size: 0.95rem;
        margin-bottom: 14px;
        color: #004b99;
        border-top: 1px solid rgba(0, 113, 227, 0.15);
        border-right: 1px solid rgba(0, 113, 227, 0.15);
        border-bottom: 1px solid rgba(0, 113, 227, 0.15);
    }
    .due-badge {
        background-color: #ff3b30;
        color: white;
        padding: 3px 9px;
        border-radius: 980px;
        font-weight: 700;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)


# -------------------------------------------------------------
# TOP NAVBAR: Apple Glassmorphic Header + User Identity + Language Selection
# -------------------------------------------------------------
lang = st.session_state.app_lang
u_role_badge = t("role_doctor", lang) if curr_u.role == "doctor" else (t("role_staff", lang) if curr_u.role == "staff" else t("role_patient", lang))
st.markdown(f"""
<div class="apple-header" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
    <div style="display: flex; align-items: center; gap: 14px;">
        <div style="background: linear-gradient(135deg, #34c759, #30b0c7); width: 48px; height: 48px; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 1.7rem; box-shadow: 0 4px 14px rgba(52, 199, 89, 0.28);">
            💊
        </div>
        <div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <h1 style="margin: 0; font-size: 1.6rem; font-weight: 700; letter-spacing: -0.03em; color: #1d1d1f;">Sehat Saathi</h1>
                <span style="font-size: 1.15rem; color: #86868b; font-weight: 500;">| सेहत साथी</span>
            </div>
            <p style="margin: 2px 0 0 0; font-size: 0.88rem; color: #86868b; font-weight: 400;">{t('app_tagline', lang)}</p>
        </div>
    </div>
    <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
        <a href="tel:108" style="background:#ff3b30; color:white; padding:6px 14px; border-radius:980px; font-size:0.82rem; font-weight:600; text-decoration:none; display:inline-flex; align-items:center; gap:5px; box-shadow:0 2px 10px rgba(255,59,48,0.25); transition:all 0.2s ease;">
            {t('btn_emergency_108', lang)}
        </a>
        <span style="background: #f5f5f7; border: 1px solid #e5e5ea; padding: 5px 12px; border-radius: 980px; font-size: 0.82rem; font-weight: 600; color: #1d1d1f;">
            {u_role_badge}: {curr_u.name.split('(')[0].strip()}
        </span>
        <span style="background: #eafaf1; border: 1px solid #b7ebd0; padding: 5px 12px; border-radius: 980px; font-size: 0.82rem; font-weight: 600; color: #19692c;">
            {t('status_active', lang)}
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# User Authentication, Language Selector & Accessibility Bar
col_user_bar, col_lang, col_a11y = st.columns([3, 2, 2])

with col_user_bar:
    with st.popover(t("account_popover_btn", lang), help="Google Sign-In, ABHA ID or Switch Profile"):
        st.markdown(f"#### {t('user_signin_title', lang)}")
        st.caption(t("user_signin_caption", lang))
        
        # Google Sign-in button
        google_auth_url = AuthService.get_google_auth_url(redirect_uri="http://localhost:8501")
        st.markdown(f"""
        <a href="{google_auth_url}" target="_blank" style="text-decoration:none;">
            <div style="background-color:#ffffff; border:1.5px solid #dadce0; border-radius:12px; padding:10px 14px; display:flex; align-items:center; justify-content:center; gap:10px; margin-bottom:12px; box-shadow:0 1px 3px rgba(0,0,0,0.08);">
                <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" width="20" height="20" />
                <span style="color:#3c4043; font-weight:600; font-size:0.95rem;">{t('btn_google_signin', lang)}</span>
            </div>
        </a>
        """, unsafe_allow_html=True)

        st.markdown(f"**{t('quick_role_select', lang)}**")
        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            if st.button(t("btn_role_pat", lang), key="btn_role_pat"):
                st.session_state.current_user = AuthService.create_google_demo_user("patient")
                st.rerun()
        with col_r2:
            if st.button(t("btn_role_doc", lang), key="btn_role_doc"):
                st.session_state.current_user = AuthService.create_google_demo_user("doctor")
                st.rerun()
        with col_r3:
            if st.button(t("btn_role_staff", lang), key="btn_role_staff"):
                st.session_state.current_user = AuthService.create_google_demo_user("staff")
                st.rerun()

        st.markdown("---")
        st.markdown(f"**{t('login_mobile_abha_header', lang)}**")
        c_name = st.text_input(t("lbl_patient_name", lang), value=curr_u.name, key="inp_login_name")
        c_phone = st.text_input(t("lbl_mobile_optional", lang), value=curr_u.phone or "", key="inp_login_phone")
        c_abha = st.text_input(t("lbl_abha_optional", lang), value=curr_u.abha_id or "", placeholder="उदा. 91-1234-5678-9012" if lang != "en" else "e.g. 91-1234-5678-9012", key="inp_login_abha")
        if st.button(t("btn_save_profile", lang), key="btn_save_user_prof"):
            new_u = AuthService.create_custom_user(c_name, curr_u.email, c_phone, c_abha, role=curr_u.role)
            st.session_state.current_user = new_u
            clinical_db.upsert_user(new_u.model_dump())
            st.success(t("msg_profile_saved", lang))
            st.rerun()

with col_lang:
    LANG_DISPLAY = ["🇮🇳 हिन्दी", "🇬🇧 English", "🌾 Hinglish"]
    current_index = 0
    if st.session_state.app_lang == "en":
        current_index = 1
    elif st.session_state.app_lang == "hinglish":
        current_index = 2

    chosen_lang_display = st.selectbox(
        t("lang_picker_label", lang),
        LANG_DISPLAY,
        index=current_index,
        key="lang_selector_widget"
    )
    new_lang = "hi"
    if "English" in chosen_lang_display:
        new_lang = "en"
    elif "Hinglish" in chosen_lang_display:
        new_lang = "hinglish"
    if new_lang != st.session_state.app_lang:
        st.session_state.app_lang = new_lang
        st.rerun()

with col_a11y:
    st.write("")
    st.session_state.large_font_mode = st.toggle(
        t("btn_large_text", lang),
        value=st.session_state.large_font_mode,
        help="Increases text size for comfortable reading"
    )

if st.session_state.large_font_mode:
    st.markdown("""
    <style>
        .main p, .main span, .main label, .main div {
            font-size: 1.22rem !important;
            line-height: 1.65 !important;
        }
        .stButton>button {
            font-size: 1.35rem !important;
            padding: 0.95rem 1.3rem !important;
        }
    </style>
    """, unsafe_allow_html=True)


# Dynamic counts for home cards
all_current_reminders = reminder_service.get_all_reminders()
active_rem_count = len([r for r in all_current_reminders if r.enabled])
recent_vitals_count = len(device_service.get_all_readings())

# 4 Apple Health-Style Action Cards (Visual Home Hub)
st.markdown(f"""
<div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin-bottom: 16px;">
    <div class="hub-card" style="background: linear-gradient(135deg, #34c759 0%, #30b0c7 100%);">
        <div style="font-size: 1.8rem; margin-bottom: 4px;">📸</div>
        <div style="font-size: 1.08rem; font-weight: 700; letter-spacing: -0.02em;">{t('card_scan_title', lang)}</div>
        <div style="font-size: 0.82rem; opacity: 0.94; margin-top: 2px;">{t('card_scan_desc', lang)}</div>
    </div>
    <div class="hub-card" style="background: linear-gradient(135deg, #0071e3 0%, #5856d6 100%);">
        <div style="font-size: 1.8rem; margin-bottom: 4px;">⏰</div>
        <div style="font-size: 1.08rem; font-weight: 700; letter-spacing: -0.02em;">{t('card_reminders_title', lang)}</div>
        <div style="font-size: 0.82rem; opacity: 0.94; margin-top: 2px;">{active_rem_count} {t('card_reminders_desc', lang)}</div>
    </div>
    <div class="hub-card" style="background: linear-gradient(135deg, #32ade6 0%, #0071e3 100%);">
        <div style="font-size: 1.8rem; margin-bottom: 4px;">🩺</div>
        <div style="font-size: 1.08rem; font-weight: 700; letter-spacing: -0.02em;">{t('card_vitals_title', lang)}</div>
        <div style="font-size: 0.82rem; opacity: 0.94; margin-top: 2px;">{recent_vitals_count} {t('card_vitals_desc', lang)}</div>
    </div>
    <div class="hub-card" style="background: linear-gradient(135deg, #ff3b30 0%, #ff2d55 100%);">
        <div style="font-size: 1.8rem; margin-bottom: 4px;">🚨</div>
        <div style="font-size: 1.08rem; font-weight: 700; letter-spacing: -0.02em;">{t('card_emergency_title', lang)}</div>
        <div style="font-size: 0.82rem; opacity: 0.94; margin-top: 2px;">{t('card_emergency_desc', lang)}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Feature: Apple Health-Style Summary Tile Banner
target_pat_id = f"pat_{curr_u.id}"
pat_vitals_summary = clinical_db.get_patient_vitals(target_pat_id, limit=4)
bp_val = "136/86 mmHg"
spo2_val = "98%"
sugar_val = "138 mg/dL"
for pv in pat_vitals_summary:
    m_name = pv.get("metric_name", "")
    if "रक्तचाप" in m_name or "BP" in m_name or "Blood Pressure" in m_name:
        bp_val = f"{pv['value']} {pv['unit']}"
    elif "SpO2" in m_name or "ऑक्सीजन" in m_name:
        spo2_val = f"{pv['value']}{pv['unit']}"
    elif "Sugar" in m_name or "शुगर" in m_name:
        sugar_val = f"{pv['value']} {pv['unit']}"
adh_stat = clinical_db.get_patient_adherence_rate(target_pat_id)
adh_pct_str = f"{adh_stat['percentage']}%"

st.markdown(f"""
<div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; margin-bottom: 16px;">
    <div style="background:#ffffff; border:1px solid #e5e5ea; border-radius:18px; padding:12px; text-align:center; box-shadow:0 2px 8px rgba(0,0,0,0.02);">
        <div style="font-size:0.75rem; color:#86868b; font-weight:600; text-transform:uppercase; letter-spacing:0.04em;">{t('tile_bp_title', lang)}</div>
        <div style="font-size:1.35rem; font-weight:700; color:#1d1d1f; letter-spacing:-0.03em; margin:2px 0;">{bp_val}</div>
        <div style="font-size:0.72rem; color:#34c759; font-weight:600;">{t('tile_bp_status', lang)}</div>
    </div>
    <div style="background:#ffffff; border:1px solid #e5e5ea; border-radius:18px; padding:12px; text-align:center; box-shadow:0 2px 8px rgba(0,0,0,0.02);">
        <div style="font-size:0.75rem; color:#86868b; font-weight:600; text-transform:uppercase; letter-spacing:0.04em;">{t('tile_spo2_title', lang)}</div>
        <div style="font-size:1.35rem; font-weight:700; color:#30b0c7; letter-spacing:-0.03em; margin:2px 0;">{spo2_val}</div>
        <div style="font-size:0.72rem; color:#34c759; font-weight:600;">{t('tile_spo2_status', lang)}</div>
    </div>
    <div style="background:#ffffff; border:1px solid #e5e5ea; border-radius:18px; padding:12px; text-align:center; box-shadow:0 2px 8px rgba(0,0,0,0.02);">
        <div style="font-size:0.75rem; color:#86868b; font-weight:600; text-transform:uppercase; letter-spacing:0.04em;">{t('tile_sugar_title', lang)}</div>
        <div style="font-size:1.35rem; font-weight:700; color:#1d1d1f; letter-spacing:-0.03em; margin:2px 0;">{sugar_val}</div>
        <div style="font-size:0.72rem; color:#34c759; font-weight:600;">{t('tile_sugar_status', lang)}</div>
    </div>
    <div style="background:#ffffff; border:1px solid #e5e5ea; border-radius:18px; padding:12px; text-align:center; box-shadow:0 2px 8px rgba(0,0,0,0.02);">
        <div style="font-size:0.75rem; color:#86868b; font-weight:600; text-transform:uppercase; letter-spacing:0.04em;">{t('tile_adherence_title', lang)}</div>
        <div style="font-size:1.35rem; font-weight:700; color:#0071e3; letter-spacing:-0.03em; margin:2px 0;">{adh_pct_str}</div>
        <div style="font-size:0.72rem; color:#0071e3; font-weight:600;">⭐ {adh_stat['total_taken']} {t('tile_doses_taken', lang)}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Safety Disclaimer (Rule 12)
st.markdown(f'<div class="disclaimer-banner">{t("safety_disclaimer", lang)}</div>', unsafe_allow_html=True)

# Persistent 1-Tap Emergency Calling Bar (India Emergency Agencies)
with st.expander(t("emergency_drawer_title", lang), expanded=False):
    st.markdown(t("emergency_instruction", lang))
    agencies = EmergencyService.get_emergency_numbers()
    col_em1, col_em2 = st.columns(2)
    for idx, ag in enumerate(agencies):
        target_col = col_em1 if idx % 2 == 0 else col_em2
        with target_col:
            tel_link = EmergencyService.build_tel_link(ag.get("number", "108"))
            label_text = ag.get("name_en", ag.get("name_hindi", "Emergency")) if lang == "en" else ag.get("name_hindi", "आपातकालीन")
            ag_color = ag.get("color", "#d32f2f")
            ag_icon = ag.get("icon", "🚨")
            ag_num = ag.get("number", "108")
            st.markdown(
                f'<a href="{tel_link}" style="text-decoration:none;">'
                f'<div style="background-color:{ag_color}; color:white; padding:10px 12px; border-radius:12px; margin-bottom:6px; font-weight:bold; text-align:center;">'
                f'{ag_icon} {label_text} ({ag_num})'
                f'</div></a>',
                unsafe_allow_html=True
            )


# -------------------------------------------------------------
# MAIN NAVIGATION TABS (Includes Doctor & Staff Portal)
# -------------------------------------------------------------
tab_scan, tab_reminders, tab_vitals, tab_facilities, tab_chat, tab_portal, tab_settings = st.tabs([
    t("tab_scan", lang),
    t("tab_reminders", lang),
    t("tab_vitals", lang),
    t("tab_facilities", lang),
    t("tab_chat", lang),
    t("tab_doctor_portal", lang),
    t("tab_settings", lang)
])


# -------------------------------------------------------------
# TAB 1: SCAN & PROCESS PRESCRIPTION
# -------------------------------------------------------------
with tab_scan:
    st.subheader(t("scan_section_title", lang))

    # Accessible Photo Guidance for Rural Users
    with st.expander(t("photo_tips_title", lang), expanded=False):
        if lang == "en":
            st.markdown("""
            1. 📄 **Keep prescription flat:** Flatten any folds or wrinkles with your hand.
            2. 💡 **Ensure good lighting:** Avoid harsh shadows; stand near a window or under a bulb.
            3. 📐 **Capture all 4 corners:** Hold phone directly above the paper without tilting.
            """)
        elif lang == "hinglish":
            st.markdown("""
            1. 📄 **Parchi ko seedha aur flat rakhein:** Mudi hui parchi ko haath se seedha karein.
            2. 💡 **Achhi roshni me rakhein:** Parchhai na padne dein; bulb ya khidki ke paas rakhein.
            3. 📐 **Charo kone dikhne chahiye:** Phone ko parchi ke theek upar pakdein.
            """)
        else:
            st.markdown("""
            1. 📄 **पर्ची को सीधा और समतल रखें:** मुड़ी हुई पर्ची को हाथ से सीधा करें।
            2. 💡 **अच्छी रोशनी में रखें:** परछाई न पड़ने दें; खिड़की के पास या बल्ब के नीचे रखें।
            3. 📐 **चारों कोने दिखने चाहिए:** फोन को पर्चे के ठीक ऊपर सीधा पकड़ें।
            """)

    # Demo quick-load buttons
    st.markdown(f"**{t('quick_demo_title', lang)}**")
    col_demo1, col_demo2 = st.columns(2)
    with col_demo1:
        if st.button(t("demo_clean_btn", lang)):
            extractor = MockPrescriptionExtractor(scenario="clean")
            st.session_state.prescription = extractor.extract_from_image(b"mock")
            st.rerun()
    with col_demo2:
        if st.button(t("demo_ambig_btn", lang)):
            extractor = MockPrescriptionExtractor(scenario="ambiguous")
            st.session_state.prescription = extractor.extract_from_image(b"mock")
            st.rerun()

    st.markdown("---")
    
    # Image Input: File Uploader or Camera
    input_options = [t("input_mode_upload", lang), t("input_mode_camera", lang)]
    input_method = st.radio(t("input_mode_label", lang), input_options, horizontal=True)
    uploaded_file = None

    if input_method == input_options[0]:
        uploaded_file = st.file_uploader(t("file_uploader_label", lang), type=["jpg", "jpeg", "png", "webp"])
    else:
        uploaded_file = st.camera_input(t("camera_input_label", lang))

    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        st.session_state.image_bytes = file_bytes

        valid, err_msg = ImageProcessingService.validate_file(file_bytes)
        if not valid:
            st.error(err_msg)
        else:
            img, load_err = ImageProcessingService.load_and_normalize(file_bytes)
            if load_err:
                st.error(load_err)
            elif img:
                st.image(img, caption=t("preview_caption", lang), use_container_width=True)
                quality_ok, quality_warning = ImageProcessingService.assess_quality(img)
                if not quality_ok:
                    st.warning(quality_warning)

                if st.button(t("extract_btn", lang), key="btn_extract"):
                    with st.spinner(t("spinner_analyzing", lang)):
                        api_key = os.environ.get("GEMINI_API_KEY")
                        if api_key and not st.session_state.demo_mode:
                            extractor = GeminiMultimodalExtractor(api_key=api_key)
                        else:
                            is_ambig = hasattr(uploaded_file, "name") and uploaded_file.name and "ambiguous" in uploaded_file.name.lower()
                            extractor = MockPrescriptionExtractor(scenario="ambiguous" if is_ambig else "clean")
                        
                        st.session_state.prescription = extractor.extract_from_image(file_bytes)
                        st.rerun()

    # Step 2: Review & Confirmation Screen
    if st.session_state.prescription:
        presc: Prescription = st.session_state.prescription
        st.markdown("---")
        
        col_rev_head, col_rev_discard = st.columns([3, 1])
        with col_rev_head:
            st.subheader(t("review_heading", lang))
            st.caption(t("review_sub", lang))
        with col_rev_discard:
            if st.button(t("discard_presc_btn", lang), key="btn_discard_presc", help="Discard draft"):
                st.session_state.prescription = None
                st.rerun()

        if presc.patient_name:
            st.info(f"👤 **{presc.patient_name}** | 📅 {presc.prescription_date or 'Recent'}")

        if presc.has_uncertain_critical_fields():
            st.markdown(f"""
            <div class="uncertain-card">
                {t('alert_unclear_handwriting', lang)}
            </div>
            """, unsafe_allow_html=True)

        confirmed_all = True

        for idx, med in enumerate(presc.medicines):
            with st.container():
                card_class = "uncertain-card" if med.is_uncertain else "confirmed-card"
                badge_icon = "⚠️" if med.is_uncertain else "✅"
                st.markdown(f'<div class="{card_class}"><b>{badge_icon} #{idx+1}:</b> {med.raw_medicine_name}</div>', unsafe_allow_html=True)
                
                col_a, col_b = st.columns(2)
                with col_a:
                    med.candidate_medicine_name = st.text_input(
                        f"{t('lbl_medicine_field', lang)} #{idx+1}",
                        value=med.candidate_medicine_name or med.raw_medicine_name,
                        key=f"med_name_{idx}"
                    )
                    med.strength = st.text_input(
                        f"{t('lbl_strength_field', lang)} #{idx+1}",
                        value=med.strength or "",
                        placeholder="e.g. 500mg" if lang == "en" else "उदा. 500mg",
                        key=f"med_strength_{idx}"
                    )
                with col_b:
                    med.dose_instruction_raw = st.text_input(
                        f"{t('lbl_dose_field', lang)} #{idx+1}",
                        value=med.dose_instruction_raw or ("1 tablet" if lang == "en" else "1 गोली"),
                        key=f"med_dose_{idx}"
                    )
                    med.frequency_raw = st.text_input(
                        f"{t('lbl_frequency_field', lang)} #{idx+1}",
                        value=med.frequency_raw or ("Twice daily (BD)" if lang == "en" else "दिन में 2 बार"),
                        key=f"med_freq_{idx}"
                    )

                timing_opts = [
                    t("opt_timing_after_food", lang),
                    t("opt_timing_before_food", lang),
                    t("opt_timing_empty_stomach", lang),
                    t("opt_timing_bedtime", lang)
                ]
                med.timing_raw = st.selectbox(
                    f"{t('lbl_timing_field', lang)} #{idx+1}",
                    options=timing_opts,
                    index=0,
                    key=f"med_timing_{idx}"
                )

                if med.is_uncertain:
                    st.warning(f"⚠️ {med.uncertainty_reason or t('alert_unclear_handwriting', lang)}")

                ref_info = MedicineReferenceService.lookup_medicine(med.candidate_medicine_name or med.raw_medicine_name)
                if ref_info:
                    with st.expander(t("ref_title", lang), expanded=False):
                        st.caption(f"{t('ref_generic_salt', lang)} **{ref_info['generic_name']}**")
                        st.caption(f"{t('ref_purpose', lang)} {ref_info['purpose_hindi']}")
                        if ref_info.get('nlem_listed'):
                            st.caption(t("ref_nlem", lang))
                        if ref_info.get('jan_aushadhi_available'):
                            st.caption(t("ref_jan_aushadhi", lang))

                col_conf, col_discard_med = st.columns([3, 1])
                with col_conf:
                    med.user_confirmed = st.checkbox(
                        f"{t('chk_verified_medicine', lang)} #{idx+1} ({med.candidate_medicine_name})",
                        value=med.user_confirmed,
                        key=f"confirm_{idx}"
                    )
                with col_discard_med:
                    if st.button(t("discard_med_btn", lang), key=f"discard_med_{med.id}"):
                        presc.discard_medicine(med.id)
                        if not presc.medicines:
                            st.session_state.prescription = None
                        st.rerun()

                if not med.user_confirmed:
                    confirmed_all = False

        st.markdown("---")

        # Step 3: Explanation & Reminder Setup (Syncs to Clinical Database)
        if confirmed_all and presc.medicines:
            st.success(t("msg_all_verified", lang))

            col_sum_head, col_sum_voice = st.columns([2, 1])
            with col_sum_head:
                st.subheader(t("heading_summary", lang))
            with col_sum_voice:
                play_audio = st.button(t("listen_audio_btn", lang), key="btn_listen_audio")

            summary_text = language_service.explain_prescription_summary(presc, lang=lang)

            if play_audio:
                with st.spinner(t("spinner_generating_audio", lang)):
                    audio_bytes = language_service.generate_speech_audio(summary_text, lang=lang)
                    if audio_bytes:
                        st.audio(audio_bytes, format="audio/mp3", autoplay=True)
                    else:
                        st.info("Audio narration currently unavailable.")

            st.markdown(summary_text)

            st.markdown("---")
            st.subheader(t("heading_set_reminders", lang))

            potential_conflicts = []
            for med in presc.medicines:
                conf = reminder_service.check_potential_conflicts(med)
                if conf:
                    potential_conflicts.extend(conf)

            if potential_conflicts:
                st.markdown(f"""
                <div class="uncertain-card">
                    {t('conflict_alert', lang)}
                </div>
                """, unsafe_allow_html=True)
                for c in potential_conflicts:
                    st.caption(f"• **{c['medicine_name']}**: {c['reason']}")

            if st.button(t("save_reminders_btn", lang), type="primary"):
                created_count = 0
                verified_med_dicts = []
                for med in presc.medicines:
                    if med.user_confirmed:
                        created = reminder_service.create_reminders_from_instruction(
                            med,
                            prescription_id=presc.id,
                            prescription_date=presc.prescription_date
                        )
                        created_count += len(created)
                        verified_med_dicts.append({
                            "candidate_medicine_name": med.candidate_medicine_name or med.raw_medicine_name,
                            "strength": med.strength,
                            "dose_instruction_raw": med.dose_instruction_raw,
                            "frequency_raw": med.frequency_raw,
                            "timing_raw": med.timing_raw
                        })

                # Sync to Clinical Database for Doctors and Healthcare Staff
                target_pat_id = f"pat_{curr_u.id}"
                clinical_db.save_prescription(
                    patient_id=target_pat_id,
                    doctor_name="Attending PHC Doctor",
                    clinic_name="Community Health Centre",
                    prescription_date=presc.prescription_date or datetime.now().strftime("%Y-%m-%d"),
                    raw_text=presc.patient_name or "Handwritten Prescription",
                    verified_medicines=verified_med_dicts
                )

                st.success(f"🎉 {created_count} {t('msg_reminders_saved', lang)}")
        else:
            st.warning(t("msg_verify_required", lang))


# -------------------------------------------------------------
# TAB 2: MEDICATION REMINDERS & ADHERENCE
# -------------------------------------------------------------
with tab_reminders:
    st.subheader(t("reminders_heading", lang))
    st.caption(t("reminders_sub", lang))

    all_reminders = reminder_service.get_all_reminders()

    if not all_reminders:
        st.info(t("no_reminders", lang))
    else:
        # Today's Adherence Metric Bar
        total_enabled = [r for r in all_reminders if r.enabled]
        taken_count = len([r for r in total_enabled if r.taken_today])
        pct = int((taken_count / len(total_enabled)) * 100) if total_enabled else 100

        st.markdown(f"""
        <div style="background:#f0fdf4; border:1px solid #bbf7d0; border-radius:14px; padding:12px 16px; margin-bottom:14px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                <span style="font-weight:bold; color:#166534;">{t('todays_progress', lang)}</span>
                <span style="font-weight:800; color:#15803d;">{taken_count} / {len(total_enabled)} ({pct}%)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(pct / 100.0)

        # 1-Tap WhatsApp share for caregivers
        share_lines = [f"*💊 Sehat Saathi - {t('reminders_heading', lang)}:*"]
        for r in all_reminders:
            if r.enabled:
                share_lines.append(f"• {r.medicine_name}: {r.timing_label} ({r.reminder_time}) - {r.food_relation}")
        encoded_text = urllib.parse.quote("\n".join(share_lines))
        st.markdown(
            f'<a href="https://api.whatsapp.com/send?text={encoded_text}" target="_blank" style="text-decoration:none;">'
            f'<div style="background-color:#25D366; color:white; text-align:center; padding:10px 14px; border-radius:12px; font-weight:bold; margin-bottom:15px; box-shadow:0 2px 8px rgba(37,211,102,0.2);">'
            f'{t("share_wa_btn", lang)}'
            f'</div></a>',
            unsafe_allow_html=True
        )

        with st.expander(t("expander_clear_reminders", lang), expanded=False):
            col_disc1, col_disc2 = st.columns(2)
            with col_disc1:
                if st.button(t("btn_discard_inactive", lang), key="btn_discard_inactive"):
                    count = reminder_service.discard_inactive_reminders()
                    st.success(f"{count} inactive reminders removed.")
                    st.rerun()
            with col_disc2:
                confirm_all = st.checkbox(t("chk_confirm_delete_all", lang), key="confirm_clear_all_rem")
                if confirm_all:
                    if st.button(t("btn_delete_all_reminders", lang), type="primary", key="btn_discard_all_rem"):
                        reminder_service.delete_all_reminders()
                        st.success("All reminders cleared.")
                        st.rerun()

        for rem in all_reminders:
            is_due = reminder_service.is_due_now(rem)
            
            t_label = rem.timing_label.lower()
            if "सुबह" in t_label or "morning" in t_label:
                icon_time = t("lbl_morning", lang)
                card_border = "#fde68a"
                card_bg = "#fefce8"
            elif "दोपहर" in t_label or "afternoon" in t_label:
                icon_time = t("lbl_afternoon", lang)
                card_border = "#fed7aa"
                card_bg = "#fff7ed"
            elif "रात" in t_label or "night" in t_label:
                icon_time = t("lbl_night", lang)
                card_border = "#c7d2fe"
                card_bg = "#eef2ff"
            else:
                icon_time = t("lbl_scheduled", lang)
                card_border = "#e2e8f0"
                card_bg = "#f8fafc"

            if is_due:
                card_border = "#f97316"
                card_bg = "#fff7ed"

            due_tag = f"<span class='due-badge'>{t('lbl_due_now', lang)}</span>" if is_due else ""
            st.markdown(f"""
            <div style="background-color:{card_bg}; border: 1.5px solid {card_border}; border-radius: 14px; padding: 14px 16px; margin-bottom: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.03);">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-weight:bold; font-size:1rem; color:#334155;">{icon_time} — {rem.reminder_time}</span>
                    <span>{due_tag}</span>
                </div>
                <div style="font-size: 1.3rem; font-weight: 800; color: #1e3a8a; margin-top: 4px;">💊 {rem.medicine_name}</div>
                <div style="font-size: 0.98rem; color: #475569; margin-top: 2px;">🥄 {rem.dosage or '1 dose'} • {rem.food_relation}</div>
            </div>
            """, unsafe_allow_html=True)

            col_t1, col_t2 = st.columns([3, 1])
            with col_t1:
                if rem.taken_today:
                    st.success(f"{t('taken_today_badge', lang)} ({rem.medicine_name})")
                else:
                    if st.button(t("mark_taken_btn", lang), key=f"taken_{rem.id}", type="primary"):
                        reminder_service.mark_as_taken(rem.id, True)
                        # Sync adherence event to Clinical Database
                        target_pat_id = f"pat_{curr_u.id}"
                        clinical_db.record_adherence(
                            patient_id=target_pat_id,
                            medicine_name=rem.medicine_name,
                            dosage=rem.dosage or "1 dose",
                            timing=rem.timing_label,
                            scheduled_time=rem.reminder_time,
                            taken_status=True
                        )
                        st.rerun()

            with col_t2:
                with st.popover("⚙️", help="Options"):
                    toggle_lbl = t("btn_deactivate", lang) if rem.enabled else t("btn_activate", lang)
                    if st.button(toggle_lbl, key=f"tog_{rem.id}"):
                        reminder_service.toggle_reminder(rem.id)
                        st.rerun()
                    if st.button(t("btn_delete", lang), key=f"del_{rem.id}"):
                        reminder_service.delete_reminder(rem.id)
                        st.rerun()

    st.markdown("---")
    
    # Progress Tracker Questionnaire
    with st.expander(t("expander_progress_tracker", lang), expanded=False):
        st.markdown(t("progress_tracker_intro", lang))
        q_items = ProgressTrackerService.get_questionnaire_items()
        
        q1_label = q_items[0]["question_hindi"] if lang == "hi" else ("1. How do you feel after starting this medication?" if lang == "en" else "1. Dawai shuru karne ke baad kaisa feel ho raha hai?")
        q2_label = q_items[1]["question_hindi"] if lang == "hi" else ("2. Have you taken all prescribed doses on time?" if lang == "en" else "2. Kya sabhi dawaiyan time par li hain?")
        q3_label = q_items[2]["question_hindi"] if lang == "hi" else ("3. How much relief in your fever, pain, or main symptoms?" if lang == "en" else "3. Bukhaar, dard ya symptoms me kitna aaram hai?")

        ans_feeling = st.radio(q1_label, q_items[0]["options"], key="prog_q_feeling")
        ans_adherence = st.radio(q2_label, q_items[1]["options"], key="prog_q_adherence")
        ans_symptoms = st.radio(q3_label, q_items[2]["options"], key="prog_q_symptoms")

        if st.button(t("btn_check_progress", lang), key="btn_submit_progress"):
            checkin_res = tracker_service.evaluate_checkin(ans_feeling, ans_adherence, ans_symptoms, lang=lang)
            st.markdown(f"### {t('lbl_recovery_score', lang)}: **{checkin_res.recovery_score}%**")
            st.progress(checkin_res.recovery_score / 100.0)

            if checkin_res.doctor_visit_advised:
                st.warning(checkin_res.recommendation_hindi)
            else:
                st.success(checkin_res.recommendation_hindi)

    # Treatment Issue Logging
    with st.expander(t("expander_report_issue", lang), expanded=False):
        med_options = [r.medicine_name for r in all_reminders] + (["Other / General"] if lang == "en" else ["अन्य / सामान्य"])
        selected_med = st.selectbox(t("lbl_select_medicine", lang), options=med_options, key="issue_med_select")
        selected_issue = st.selectbox(t("lbl_select_issue", lang), options=COMMON_ISSUE_TYPES, key="issue_type_select")
        sev_opts = [t("lbl_mild", lang), t("lbl_moderate", lang), t("lbl_severe", lang)]
        selected_sev = st.radio(t("lbl_severity", lang), sev_opts, horizontal=True, key="issue_sev_radio")
        issue_notes = st.text_input(t("lbl_notes_optional", lang), key="issue_notes_input")
        dr_phone = st.text_input(t("lbl_doctor_phone_optional", lang), key="dr_phone_input")

        if st.button(t("btn_log_issue", lang), key="btn_save_issue"):
            logged = issue_service.log_issue(
                medicine_name=selected_med,
                issue_type=selected_issue,
                severity="Severe" if ("Severe" in selected_sev or "गंभीर" in selected_sev) else ("Moderate" if ("Moderate" in selected_sev or "मध्यम" in selected_sev) else "Mild"),
                notes=issue_notes
            )
            st.success(t("msg_issue_logged", lang))
            if logged.is_severe_alert:
                st.error(t("msg_severe_alert", lang))


# -------------------------------------------------------------
# TAB 3: HEALTH DEVICES, VITALS & COMPLICATION PREDICTION
# -------------------------------------------------------------
with tab_vitals:
    st.subheader(t("vitals_heading", lang))
    st.caption(t("vitals_sub", lang))

    # Part A: Health Devices Vitals Recorder (Syncs to Clinical DB)
    with st.expander(t("expander_vitals_recorder", lang), expanded=True):
        dev_opts = [
            t("dev_oximeter", lang),
            t("dev_bp", lang),
            t("dev_glucometer", lang),
            t("dev_thermometer", lang)
        ]
        dev_choice = st.selectbox(
            t("lbl_select_device", lang),
            dev_opts,
            key="dev_choice_select"
        )

        col_val1, col_val2 = st.columns(2)
        with col_val1:
            if "Oximeter" in dev_choice or "ऑक्सीमीटर" in dev_choice:
                v_metric = "SpO2"
                v_unit = "%"
                v_hint = "e.g. 98"
            elif "BP" in dev_choice or "रक्तचाप" in dev_choice:
                v_metric = "Blood Pressure"
                v_unit = "mmHg"
                v_hint = "e.g. 120/80"
            elif "Glucometer" in dev_choice or "ग्लूकोमीटर" in dev_choice or "शुगर" in dev_choice:
                v_metric = "Blood Sugar"
                v_unit = "mg/dL"
                v_hint = "e.g. 110"
            else:
                v_metric = "Temperature"
                v_unit = "°F"
                v_hint = "e.g. 98.6"

            val_input = st.text_input(f"{t('lbl_enter_reading', lang)} ({v_metric}):", placeholder=v_hint, key="vital_val_input")

        with col_val2:
            st.caption(f"{t('lbl_unit', lang)} **{v_unit}**")
            st.caption("Standard digital device input")

        if st.button(t("btn_save_reading", lang), key="btn_save_vital"):
            if val_input.strip():
                dev_clean = dev_choice.split("(")[0].strip()
                rec = device_service.record_reading(
                    device_type=dev_clean,
                    metric_name=v_metric,
                    value=val_input,
                    unit=v_unit
                )
                # Persist to Clinical Relational Database for Doctors & PHC Staff
                target_pat_id = f"pat_{curr_u.id}"
                clinical_db.save_vital(
                    patient_id=target_pat_id,
                    device_type=dev_clean,
                    metric_name=v_metric,
                    value=val_input,
                    unit=v_unit,
                    status_flag=rec.status_flag,
                    alert_message=rec.alert_message
                )
                st.success(f"✅ {t('msg_reading_saved', lang)} {val_input} {v_unit}")
                if rec.alert_message:
                    st.warning(rec.alert_message)
            else:
                st.warning("Please enter a reading value.")

        # Past Readings
        all_readings = device_service.get_all_readings()
        if all_readings:
            st.markdown("---")
            st.markdown(t("lbl_recent_vitals", lang))
            for r in all_readings[:4]:
                col_r_txt, col_r_del = st.columns([4, 1])
                with col_r_txt:
                    st.caption(f"🔹 **{r.timestamp}** — {r.device_type}: **{r.value} {r.unit}** ({r.status_flag})")
                with col_r_del:
                    if st.button("🗑️", key=f"del_vital_{r.id}", help="Delete"):
                        device_service.delete_reading(r.id)
                        st.rerun()

    st.markdown("---")

    # Part B: AI / ML Health Complication Risk Prediction (Syncs to Clinical DB)
    with st.expander(t("expander_ai_risk", lang), expanded=True):
        st.markdown(t("ai_risk_sub", lang))

        col_cp1, col_cp2 = st.columns(2)
        with col_cp1:
            inp_age = st.number_input(t("lbl_patient_age", lang), min_value=1, max_value=110, value=58, key="ml_age")
            inp_sys = st.number_input(t("lbl_systolic_bp", lang), min_value=60, max_value=240, value=135, key="ml_sys")
            inp_dia = st.number_input(t("lbl_diastolic_bp", lang), min_value=40, max_value=140, value=88, key="ml_dia")
        with col_cp2:
            inp_sugar = st.number_input(t("lbl_blood_sugar", lang), min_value=40, max_value=500, value=130, key="ml_sugar")
            inp_spo2 = st.number_input(t("lbl_spo2", lang), min_value=60, max_value=100, value=97, key="ml_spo2")
            inp_adh = st.slider(t("lbl_adherence_slider", lang), min_value=0, max_value=100, value=90, key="ml_adh")

        bp_seq_str = st.text_input(t("lbl_bp_trend_input", lang), value="125, 130, 138", key="ml_bp_seq")

        if st.button(t("predict_btn", lang), key="btn_run_ml_predict"):
            try:
                active_meds_count = len([r for r in reminder_service.get_all_reminders() if r.enabled])
                pred_input = ComplicationPredictionInput(
                    age=int(inp_age),
                    systolic_bp=float(inp_sys),
                    diastolic_bp=float(inp_dia),
                    blood_sugar=float(inp_sugar),
                    spo2=float(inp_spo2),
                    adherence_percentage=float(inp_adh),
                    active_medications_count=active_meds_count if active_meds_count > 0 else 2
                )
                
                res = ComplicationPredictionService.predict_complication_risk(pred_input, lang=lang)

                tier_badge = "🟢" if res.risk_tier == RiskTier.LOW else ("🟡" if res.risk_tier == RiskTier.MODERATE else "🔴")
                st.markdown(f"### {tier_badge} {t('lbl_risk_score', lang)}: **{res.risk_score_percentage}%** — {res.risk_tier.value}")
                st.progress(res.risk_score_percentage / 100.0)

                st.markdown(res.clinical_guidance_hindi)

                st.markdown(t("lbl_potential_complications", lang))
                for c in res.potential_complications_hindi:
                    st.markdown(f"• **{c}**")

                if res.key_risk_factors:
                    st.markdown(t("lbl_key_risk_factors", lang))
                    for rf in res.key_risk_factors:
                        badge = "⚠️" if rf.impact_level == "चिंताजनक" else "🚨"
                        st.caption(f"{badge} **{rf.feature_name}** ({rf.observed_value}): {rf.explanation_hindi}")

                # Deep Learning sequence trajectory
                trajectory_label = "स्थिर (Stable)" if lang != "en" else "Stable"
                try:
                    trend_vals = [float(x.strip()) for x in bp_seq_str.split(",") if x.strip()]
                    if len(trend_vals) >= 2:
                        t_res = ComplicationPredictionService.predict_temporal_trajectory(trend_vals, lang=lang)
                        trajectory_label = t_res['trend_direction']
                        st.markdown("---")
                        st.markdown(f"{t('lbl_trajectory', lang)} **{trajectory_label}**")
                        st.caption(t_res['warning_message_hindi'])
                except Exception:
                    pass

                # Persist Prediction to Clinical Database for Hospital Staff
                target_pat_id = f"pat_{curr_u.id}"
                clinical_db.save_complication_prediction(
                    patient_id=target_pat_id,
                    risk_score=res.risk_score_percentage,
                    risk_tier=res.risk_tier.value,
                    systolic_bp=float(inp_sys),
                    diastolic_bp=float(inp_dia),
                    blood_sugar=float(inp_sugar),
                    spo2=float(inp_spo2),
                    adherence_pct=float(inp_adh),
                    trajectory=trajectory_label,
                    model_name=res.model_name
                )

                if res.emergency_dial_advised:
                    st.error(t("msg_emergency_detected", lang))

                st.caption(f"🔬 *Model: {res.model_name}* | {res.disclaimer}")
            except Exception as e:
                st.error(f"Error calculating risk: {str(e)}")

    st.markdown("---")

    # Part C: Mental Wellness Screener (Tele-MANAS 14416)
    with st.expander(t("mental_wellness_title", lang), expanded=False):
        st.markdown(t("mental_wellness_sub", lang))
        sleep_opts = ["अच्छी नींद (Good Sleep)", "परेशानी (Disturbed)", "अनिद्रा (Insomnia)"] if lang != "en" else ["Good Sleep", "Disturbed Sleep", "Insomnia / Sleepless"]
        stress_opts = ["सामान्य (Normal)", "हल्का तनाव (Mild Worry)", "गंभीर चिंता (Severe Anxiety)"] if lang != "en" else ["Normal", "Mild Worry", "Severe Anxiety"]
        mood_opts = ["प्रसन्न (Positive)", "सामान्य (Neutral)", "उदास (Low / Sad)"] if lang != "en" else ["Positive", "Neutral", "Low / Sad"]

        m_sleep = st.radio(t("lbl_sleep_quality", lang), sleep_opts, key="m_sleep_radio")
        m_stress = st.radio(t("lbl_stress_level", lang), stress_opts, key="m_stress_radio")
        m_mood = st.radio(t("lbl_mood", lang), mood_opts, key="m_mood_radio")

        if st.button(t("btn_check_wellness", lang), key="btn_check_mental"):
            m_res = mental_service.evaluate_mental_wellness(m_sleep, m_stress, m_mood, lang=lang)
            st.markdown(f"### {t('lbl_wellness_score', lang)}: **{m_res.wellness_score}%**")
            st.progress(m_res.wellness_score / 100.0)
            st.info(m_res.supportive_advice_hindi)

            if m_res.tele_manas_recommended:
                st.markdown(f"""
                <div style="background-color:#fce4ec; border-left:6px solid #c2185b; padding:12px; border-radius:12px; margin-top:10px;">
                    🌸 <b>{t('tele_manas_box_title', lang)}</b><br>
                    {t('tele_manas_box_desc', lang)}<br><br>
                    👉 <a href="tel:14416" style="background-color:#c2185b; color:white; padding:8px 14px; border-radius:8px; text-decoration:none; font-weight:bold;">
                    {t('tele_manas_call_btn', lang)}
                    </a>
                </div>
                """, unsafe_allow_html=True)


# -------------------------------------------------------------
# TAB 4: NEARBY CLINICS & DISEASE PREVENTION
# -------------------------------------------------------------
with tab_facilities:
    st.subheader(t("facilities_heading", lang))
    st.caption(t("facilities_sub", lang))

    user_locality = st.text_input(t("lbl_user_locality", lang), placeholder="e.g. Behror, Neemrana" if lang == "en" else "उदा. बहरोड़, नीमराना")

    col_map1, col_map2 = st.columns(2)
    with col_map1:
        phc_url = PreventionAndFacilitiesService.build_maps_search_url("Primary Health Centre PHC Hospital", user_locality)
        st.markdown(
            f'<a href="{phc_url}" target="_blank" style="text-decoration:none;">'
            f'<div style="background-color:#065f46; color:white; text-align:center; padding:12px; border-radius:12px; font-weight:bold; margin-bottom:10px;">'
            f'{t("maps_phc_btn", lang)}'
            f'</div></a>',
            unsafe_allow_html=True
        )

        chemist_url = PreventionAndFacilitiesService.build_maps_search_url("Medical Store Chemist Pharmacy", user_locality)
        st.markdown(
            f'<a href="{chemist_url}" target="_blank" style="text-decoration:none;">'
            f'<div style="background-color:#0f766e; color:white; text-align:center; padding:12px; border-radius:12px; font-weight:bold; margin-bottom:10px;">'
            f'{t("maps_chemist_btn", lang)}'
            f'</div></a>',
            unsafe_allow_html=True
        )

    with col_map2:
        ja_url = PreventionAndFacilitiesService.build_maps_search_url("Pradhan Mantri Jan Aushadhi Kendra", user_locality)
        st.markdown(
            f'<a href="{ja_url}" target="_blank" style="text-decoration:none;">'
            f'<div style="background-color:#c2410c; color:white; text-align:center; padding:12px; border-radius:12px; font-weight:bold; margin-bottom:10px;">'
            f'{t("maps_jan_btn", lang)}'
            f'</div></a>',
            unsafe_allow_html=True
        )

        dr_url = PreventionAndFacilitiesService.build_maps_search_url("Doctor Clinic", user_locality)
        st.markdown(
            f'<a href="{dr_url}" target="_blank" style="text-decoration:none;">'
            f'<div style="background-color:#1d4ed8; color:white; text-align:center; padding:12px; border-radius:12px; font-weight:bold; margin-bottom:10px;">'
            f'{t("maps_doctor_btn", lang)}'
            f'</div></a>',
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.subheader(t("heading_rural_prevention", lang))

    topics = PreventionAndFacilitiesService.get_prevention_topics()
    for topic in topics:
        p_title, p_sub, p_points = PreventionAndFacilitiesService.get_topic_display(topic, lang=lang)
        with st.expander(f"{topic['icon']} {p_title}", expanded=False):
            st.markdown(f"**{t('lbl_key_advice', lang)}** {p_sub}")
            for pt in p_points:
                st.write(f"• {pt}")
            
            if st.button(t("btn_read_aloud", lang), key=f"audio_prev_{topic['id']}"):
                with st.spinner(t("spinner_generating_audio", lang)):
                    audio_text = f"{p_title}. {p_sub}. " + " ".join(p_points)
                    aud = language_service.generate_speech_audio(audio_text, lang=lang)
                    if aud:
                        st.audio(aud, format="audio/mp3")


# -------------------------------------------------------------
# TAB 5: CHAT / QUESTIONS
# -------------------------------------------------------------
with tab_chat:
    st.subheader(t("chat_heading", lang))
    st.caption(t("chat_sub", lang))

    chat_service = PrescriptionChatService()

    if lang == "en":
        sample_questions = [
            "Should I take this medicine before or after meals?",
            "Can I take this medication on an empty stomach?",
            "What should I do if I miss a scheduled dose?",
            "Can I take this medicine at bedtime?"
        ]
    elif lang == "hinglish":
        sample_questions = [
            "Yeh dawai khane ke pehle leni hai ya baad me?",
            "Kya yeh dawai khali pet le sakte hain?",
            "Agar ek dose chhoot jaye toh kya karein?",
            "Kya yeh dawai raat ko sote waqt le sakte hain?"
        ]
    else:
        sample_questions = [
            "यह दवा खाने के पहले लेनी है या बाद में?",
            "क्या मुझे यह दवा बुखार में लेनी चाहिए?",
            "क्या यह दवा खाली पेट ले सकते हैं?",
            "क्या यह दवा रात को सोते समय ले सकते हैं?"
        ]

    opt_default = t("opt_select_or_type", lang)
    selected_sample = st.selectbox(t("lbl_sample_questions", lang), [opt_default] + sample_questions)
    user_input = st.text_input(t("lbl_user_question", lang))
    query_to_send = user_input if user_input.strip() else (selected_sample if selected_sample != opt_default else "")

    if st.button(t("chat_ask_btn", lang), key="btn_ask"):
        if not query_to_send:
            st.warning(t("msg_enter_question", lang))
        else:
            with st.spinner(t("spinner_chat_answer", lang)):
                answer = chat_service.ask_question(query_to_send, st.session_state.prescription)
                st.markdown(f"**{t('lbl_answer', lang)}**\n\n{answer}")


# -------------------------------------------------------------
# TAB 6: DOCTOR & HOSPITAL STAFF TREATMENT PORTAL
# -------------------------------------------------------------
with tab_portal:
    st.subheader(t("portal_heading", lang))
    st.caption(t("portal_sub", lang))

    # Notice of clinical purpose & consent
    st.markdown(f"""
    <div style="background-color:#e0f2fe; border-left:6px solid #0284c7; padding:12px 16px; border-radius:12px; margin-bottom:14px;">
        {t("portal_disha_notice", lang)}
    </div>
    """, unsafe_allow_html=True)

    # Patient Selector
    all_pats = clinical_db.list_all_patients()
    if not all_pats:
        st.info("डेटाबेस में फिलहाल कोई मरीज पंजीकृत नहीं है।" if lang != "en" else "No patients currently registered in database.")
    else:
        pat_display_map = {f"{p['name']} ({t('lbl_patient_age', lang).split('(')[0].strip()}: {p['age']}, ID: {p['id']})": p['id'] for p in all_pats}
        selected_display = st.selectbox(t("lbl_select_patient", lang), list(pat_display_map.keys()))
        selected_pat_id = pat_display_map[selected_display]
        selected_pat = clinical_db.get_patient(selected_pat_id)

        if selected_pat:
            col_p_info1, col_p_info2 = st.columns(2)
            with col_p_info1:
                st.markdown(f"{t('lbl_patient_name_card', lang)} **{selected_pat['name']}**")
                st.markdown(f"{t('lbl_age_gender', lang)} **{selected_pat['age']} | {selected_pat['gender']}**")
                st.markdown(f"{t('lbl_blood_group', lang)} **{selected_pat['blood_group']}**")
            with col_p_info2:
                consent_badge = t("lbl_consent_granted", lang) if selected_pat['consent_shared_treatment'] else t("lbl_consent_pending", lang)
                st.markdown(f"{t('lbl_treatment_consent', lang)} **{consent_badge}**")
                st.markdown(f"{t('lbl_emergency_contact', lang)} **{selected_pat['emergency_contact']}**")
                st.markdown(f"{t('lbl_record_id', lang)} `{selected_pat['id']}`")

            st.markdown("---")

            # Section A: Prescriptions & Medications
            st.markdown(t("heading_prescriptions", lang))
            pat_prescs = clinical_db.get_patient_prescriptions(selected_pat_id)
            if not pat_prescs:
                st.caption(t("lbl_no_prescriptions", lang))
            else:
                for p in pat_prescs:
                    with st.expander(f"📄 {p['prescription_date']} — {p['clinic_name']} ({p['doctor_name']})", expanded=True):
                        st.caption(f"Raw: {p['raw_text']}")
                        for m in p.get("verified_medicines", []):
                            st.markdown(f"• **{m.get('candidate_medicine_name', 'Medicine')}** — {m.get('dose_instruction_raw', '')} | {m.get('frequency_raw', '')} ({m.get('timing_raw', '')})")

            st.markdown("---")

            # Section B: Device Vitals
            st.markdown(t("heading_device_vitals", lang))
            pat_vitals = clinical_db.get_patient_vitals(selected_pat_id, limit=5)
            if not pat_vitals:
                st.caption(t("lbl_no_vitals", lang))
            else:
                col_v_a, col_v_b = st.columns(2)
                for i, v in enumerate(pat_vitals):
                    target_col = col_v_a if i % 2 == 0 else col_v_b
                    with target_col:
                        st.markdown(f"""
                        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:10px 14px; margin-bottom:8px;">
                            <div style="font-weight:bold; color:#1e293b;">{v['device_type']} ({v['metric_name']})</div>
                            <div style="font-size:1.35rem; font-weight:800; color:#047857;">{v['value']} {v['unit']}</div>
                            <div style="font-size:0.8rem; color:#64748b;">{v['timestamp']} • {v['status_flag']}</div>
                        </div>
                        """, unsafe_allow_html=True)

            st.markdown("---")

            # Section C: Adherence Rate & AI Risk Summary
            col_sum_adh, col_sum_ai = st.columns(2)
            with col_sum_adh:
                st.markdown(t("heading_adherence_col", lang))
                adh = clinical_db.get_patient_adherence_rate(selected_pat_id)
                st.markdown(f"**{t('lbl_adherence_rate', lang)}** **{adh['percentage']}%** ({adh['total_taken']} / {adh['total_scheduled']} {t('lbl_doses', lang)})")
                st.progress(adh['percentage'] / 100.0)

            with col_sum_ai:
                st.markdown(t("heading_ai_risk_col", lang))
                pred = clinical_db.get_latest_complication_prediction(selected_pat_id)
                if pred:
                    st.markdown(f"**{t('lbl_risk_score_field', lang)}** **{pred['risk_score']}%** ({pred['risk_tier']})")
                    st.caption(f"{t('lbl_trend_field', lang)} {pred.get('trajectory', 'Stable')} | {t('lbl_model_field', lang)} {pred.get('model_name')}")
                else:
                    st.caption(t("lbl_no_risk_yet", lang))

            st.markdown("---")

            # Section D: Doctor Clinical Note Input
            st.markdown(t("heading_add_clinical_note", lang))
            doc_note_text = st.text_area(t("lbl_clinical_observations", lang), placeholder=t("ph_clinical_observations", lang))
            col_triage_stat, col_triage_rec = st.columns(2)
            with col_triage_stat:
                triage_options = [
                    t("triage_normal", lang),
                    t("triage_followup", lang),
                    t("triage_urgent", lang)
                ]
                doc_triage = st.selectbox(t("lbl_triage_priority", lang), triage_options)
            with col_triage_rec:
                doc_action = st.text_input(t("lbl_recommendation_action", lang), placeholder=t("ph_recommendation_action", lang))

            if st.button(t("btn_save_clinical_note", lang), type="primary", key="btn_save_doc_note"):
                if doc_note_text.strip():
                    clinical_db.add_staff_clinical_note(
                        patient_id=selected_pat_id,
                        staff_id=curr_u.id,
                        staff_name=curr_u.name,
                        staff_role="Physician / Doctor" if curr_u.role == "doctor" else ("PHC Nurse / Staff" if curr_u.role == "staff" else "Medical Attendant"),
                        observation_notes=doc_note_text,
                        triage_status=doc_triage,
                        recommended_action=doc_action
                    )
                    st.success(t("msg_clinical_note_saved", lang))
                    st.rerun()
                else:
                    st.warning(t("msg_enter_clinical_note", lang))

            # Past Clinical Notes
            past_notes = clinical_db.get_staff_clinical_notes(selected_pat_id)
            if past_notes:
                st.markdown(t("heading_past_notes", lang))
                for n in past_notes[:4]:
                    st.markdown(f"""
                    <div style="background:#fefce8; border-left:4px solid #ca8a04; border-radius:10px; padding:10px 14px; margin-bottom:8px;">
                        <div style="font-weight:bold; color:#854d0e;">{n['staff_name']} ({n['staff_role']}) — <span style="font-size:0.85rem; color:#713f12;">{n['created_at']}</span></div>
                        <div style="font-size:0.95rem; color:#1e293b; margin-top:3px;">{n['observation_notes']}</div>
                        <div style="font-size:0.85rem; color:#475569; margin-top:2px;"><b>{t('lbl_triage', lang)}</b> {n['triage_status']} | <b>{t('lbl_advice', lang)}</b> {n['recommended_action'] or 'As directed'}</div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("---")

            # Section E: Export Clinical Summary Card (ABDM / PHC EHR JSON)
            summary_export = clinical_db.export_patient_clinical_summary(selected_pat_id)
            st.download_button(
                label=t("btn_export_clinical_summary", lang),
                data=json.dumps(summary_export, ensure_ascii=False, indent=2),
                file_name=f"SehatSaathi_Patient_{selected_pat_id}.json",
                mime="application/json"
            )


# -------------------------------------------------------------
# TAB 7: SETTINGS & INSTALLATION
# -------------------------------------------------------------
with tab_settings:
    st.subheader(t("settings_heading", lang))

    env_api_key = os.environ.get("GEMINI_API_KEY", "")
    key_status = t("status_configured", lang) if env_api_key else t("status_not_configured", lang)
    st.write(f"**{t('lbl_gemini_api_key', lang)}** {key_status}")

    custom_key = st.text_input(t("lbl_custom_api_key", lang), value=env_api_key, type="password")
    if custom_key:
        os.environ["GEMINI_API_KEY"] = custom_key

    st.session_state.demo_mode = st.toggle(t("toggle_demo_mode", lang), value=st.session_state.demo_mode)
    if st.session_state.demo_mode:
        st.info(t("info_demo_mode", lang))

    # Cross-Platform Installation Guide (iOS, Android, Desktop Web)
    with st.expander(t("expander_install_pwa", lang), expanded=True):
        if lang == "en":
            st.markdown("""
            **1. 🍏 iPhone / iPad (iOS Safari):**
            - Tap the **Share icon (📤)** at the bottom of Safari.
            - Scroll down and tap **'Add to Home Screen' (➕)**.
            - Sehat Saathi will open like a native app without address bar.

            **2. 🤖 Android (Chrome / Samsung Internet):**
            - Tap the **three dots menu (⋮)** in top-right corner.
            - Tap **'Install App'** or **'Add to Home Screen'**.

            **3. 💻 PC / Mac (Chrome / Edge / Safari):**
            - Click the **Install icon (⊕)** in the URL bar to run as a desktop app.
            """)
        elif lang == "hinglish":
            st.markdown("""
            **1. 🍏 iPhone / iPad (iOS Safari):**
            - Safari ke neeche **Share icon (📤)** par tap karein.
            - Neeche scroll karke **'Add to Home Screen' (➕)** dabayein.
            - Sehat Saathi native app ki tarah open ho jayega.

            **2. 🤖 Android (Chrome / Samsung Internet):**
            - Upar right corner me **three dots (⋮)** par tap karein.
            - **'Install App'** ya **'Add to Home Screen'** choose karein.

            **3. 💻 PC / Mac (Chrome / Edge / Safari):**
            - URL bar me bane **Install icon (⊕)** par click karein.
            """)
        else:
            st.markdown("""
            **1. 🍏 iPhone / iPad (iOS Safari):**
            - सफारी ब्राउज़र के नीचे **शेयर आइकन (📤)** पर टैप करें।
            - नीचे स्क्रॉल करें और **'Add to Home Screen' (➕)** चुनें।
            - सेहत साथी एक फोन ऐप की तरह बिना ब्राउज़र बार के खुलेगा।

            **2. 🤖 Android (Chrome / Samsung Internet):**
            - ऊपर दाईं ओर दिए गए **तीन बिंदुओं (⋮)** पर टैप करें।
            - **'ऐप इंस्टॉल करें' (Install App)** या **'होम स्क्रीन पर जोड़ें'** दबाएं।

            **3. 💻 PC / Mac (Chrome / Edge / Safari):**
            - यूआरएल बार में **इंस्टॉल आइकन (⊕)** पर क्लिक करके कंप्यूटर ऐप की तरह चलाएं।
            """)

    st.markdown("---")
    if st.button(t("btn_reset_all_data", lang)):
        LocalStorageAdapter().clear_all()
        st.success(t("msg_all_data_reset", lang))
        st.rerun()


# -------------------------------------------------------------
# APPLE-STYLE MINIMALIST FOOTER: Compliance & Helplines
# -------------------------------------------------------------
st.markdown(f"""
<div style="margin-top: 48px; padding: 24px 16px 18px 16px; border-top: 1px solid #e5e5ea; color: #86868b; font-size: 0.85rem; text-align: center; background: transparent;">
    <div style="display: flex; justify-content: center; gap: 14px; flex-wrap: wrap; margin-bottom: 10px; font-size: 0.82rem; font-weight: 500;">
        <span>{t('footer_compliance', lang)}</span>
    </div>
    <div style="margin-bottom: 10px; line-height: 1.6; font-size: 0.82rem;">
        {t('footer_helplines', lang)} 
        <a href="tel:108" style="color:#ff3b30; font-weight:600; text-decoration:none;">{t('footer_ambulance', lang)}</a> &nbsp;•&nbsp; 
        <a href="tel:112" style="color:#ff3b30; font-weight:600; text-decoration:none;">{t('footer_emergency', lang)}</a> &nbsp;•&nbsp; 
        <a href="tel:104" style="color:#0071e3; font-weight:600; text-decoration:none;">{t('footer_health_advice', lang)}</a> &nbsp;•&nbsp; 
        <a href="tel:14416" style="color:#ff2d55; font-weight:600; text-decoration:none;">{t('footer_tele_manas', lang)}</a>
    </div>
    <div style="font-size: 0.76rem; color: #a1a1a6;">
        {t('footer_copyright', lang)}
    </div>
</div>
""", unsafe_allow_html=True)
