"""
Sehat Saathi (सेहत साथी) — Main Streamlit Application
AI-assisted prescription reader, medication companion, and rural healthcare assistant.
Designed as a local research prototype for rural India and older adults. Profile forms
do not authenticate users or verify clinician credentials.
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
import uuid
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
from services.proximity_service import ProximityLocationService, haversine_distance_miles

# Instantiate core services
language_service = SimpleHindiLanguageService()
reminder_service = ReminderService()
device_service = DeviceDataService()
issue_service = HealthIssueService()
tracker_service = ProgressTrackerService()
mental_service = MentalHealthService()
clinical_db = ClinicalDatabaseService()


# Streamlit Page Configuration
st.set_page_config(
    page_title="Sehat Saathi | सेहत साथी",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize Session State
if "app_lang" not in st.session_state:
    st.session_state.app_lang = "hi"
if "current_user" not in st.session_state:
    # Blank guest patient - asks user for their real data without pre-filling fake records
    st.session_state.current_user = AuthService.create_blank_user(role="patient")
if "prescription" not in st.session_state:
    st.session_state.prescription = None
if "image_bytes" not in st.session_state:
    st.session_state.image_bytes = None
if "confirmed_medicines" not in st.session_state:
    st.session_state.confirmed_medicines = []
if "demo_mode" not in st.session_state:
    st.session_state.demo_mode = False if os.environ.get("GEMINI_API_KEY") else True
if "large_font_mode" not in st.session_state:
    st.session_state.large_font_mode = False
if "nav_ctrl" not in st.session_state:
    st.session_state.nav_ctrl = 0
if "open_emergency_drawer" not in st.session_state:
    st.session_state.open_emergency_drawer = False
if "active_view" not in st.session_state:
    st.session_state.active_view = "screen"
if "user_locality" not in st.session_state:
    st.session_state.user_locality = "Neemrana"

# Ensure active profile exists in database if user has entered their details
curr_u = st.session_state.current_user
if curr_u.name.strip():
    clinical_db.upsert_user(curr_u.model_dump())
    if curr_u.role == "patient":
        curr_pat_id = f"pat_{curr_u.id}"
        if not clinical_db.get_patient(curr_pat_id):
            clinical_db.upsert_patient({
                "id": curr_pat_id,
                "user_id": curr_u.id,
                "name": curr_u.name,
                "age": curr_u.age or 0,
                "gender": curr_u.gender or "",
                "blood_group": curr_u.blood_group or "",
                "emergency_contact": curr_u.emergency_contact or (curr_u.phone or ""),
                "consent_shared_treatment": 1
            })


# Custom CSS & PWA Meta for Cross-Platform Compatibility (iOS, Android & Desktop Web)
st.markdown("""
<!-- PWA & Mobile WebApp Compatibility Tags -->
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Sehat Saathi">
<meta name="mobile-web-app-capable" content="yes">
<meta name="theme-color" content="#0d9488">
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
    /* Sehat Saathi visual system */
    :root {
        --hai-bg: #f8fafc;
        --hai-card: #ffffff;
        --hai-text: #0f172a;
        --hai-subtext: #64748b;
        --hai-teal: #0d9488;
        --hai-blue: #2563eb;
        --hai-indigo: #4f46e5;
        --hai-sky: #0284c7;
        --hai-rose: #e11d48;
        --hai-border: #e2e8f0;
    }

    html, body, [class*="css"], .stApp {
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Inter", "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
        background-color: #f8fafc !important;
        background-image:
            radial-gradient(at 0% 0%, rgba(13, 148, 136, 0.08) 0px, transparent 50%),
            radial-gradient(at 100% 0%, rgba(37, 99, 235, 0.08) 0px, transparent 50%),
            radial-gradient(at 50% 100%, rgba(14, 165, 233, 0.05) 0px, transparent 50%) !important;
        color: #0f172a !important;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        letter-spacing: -0.012em;
        -webkit-tap-highlight-color: transparent !important;
        touch-action: manipulation;
    }

    /* Floating HealthAI Assistant Card Container (Desktop Web vs Native Mobile) */
    @media (min-width: 769px) {
        .main {
            max-width: 960px !important;
            margin: 24px auto !important;
            background: #ffffff !important;
            border-radius: 26px !important;
            box-shadow: 0 20px 45px -10px rgba(15, 23, 42, 0.07), 0 4px 16px rgba(15, 23, 42, 0.03) !important;
            padding: 32px 38px !important;
            border: 1px solid rgba(226, 232, 240, 0.85) !important;
        }
    }
    @media (max-width: 768px) {
        .main {
            max-width: 100% !important;
            margin: 0 !important;
            padding: 8px 12px 60px 12px !important;
            background: #ffffff !important;
            border-radius: 0 0 20px 20px !important;
            box-shadow: none !important;
            border: none !important;
        }
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 2rem !important;
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }
        body {
            padding-top: env(safe-area-inset-top, 0px);
            padding-bottom: env(safe-area-inset-bottom, 20px);
            padding-left: env(safe-area-inset-left, 0px);
            padding-right: env(safe-area-inset-right, 0px);
        }
        /* Mobile Touch Sizing (Prevents iOS Safari auto-zoom) */
        input, select, textarea, .stTextInput input, .stNumberInput input {
            font-size: 16px !important;
            min-height: 46px !important;
            border-radius: 14px !important;
        }
        .stSelectbox div[data-baseweb="select"] {
            min-height: 46px !important;
            border-radius: 14px !important;
        }
    }

    /* Modern Glassmorphic Brand Navbar */
    .apple-header {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 20px;
        border: 1px solid rgba(226, 232, 240, 0.9);
        padding: 16px 22px;
        margin-bottom: 16px;
        box-shadow: 0 4px 16px rgba(15, 23, 42, 0.04);
    }
    @media (max-width: 768px) {
        .apple-header {
            padding: 12px 14px !important;
            border-radius: 16px !important;
            margin-bottom: 12px !important;
        }
        .apple-header h1 {
            font-size: 1.25rem !important;
        }
        .apple-header p {
            font-size: 0.78rem !important;
        }
        .hai-hero-banner {
            border-radius: 18px !important;
            padding: 16px 18px !important;
            margin-bottom: 14px !important;
        }
        .hai-hero-banner h2 {
            font-size: 1.32rem !important;
        }
        .hai-hero-banner p {
            font-size: 0.85rem !important;
        }
    }

    /* Swipeable Segmented Control Navigation Tabs on Mobile */
    @media (max-width: 768px) {
        div[data-testid="stSegmentedControl"] {
            display: flex !important;
            flex-wrap: nowrap !important;
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch !important;
            scrollbar-width: none !important;
            gap: 6px !important;
            padding: 5px 6px !important;
            background: #f1f5f9 !important;
            border-radius: 16px !important;
        }
        div[data-testid="stSegmentedControl"]::-webkit-scrollbar {
            display: none !important;
        }
        div[data-testid="stSegmentedControl"] [data-baseweb="radio"],
        div[data-testid="stSegmentedControl"] button {
            flex: 0 0 auto !important;
            white-space: nowrap !important;
            padding: 8px 14px !important;
            font-size: 0.86rem !important;
            border-radius: 12px !important;
        }
    }

    /* Segmented Control Navigation Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: #f1f5f9;
        padding: 5px;
        border-radius: 980px;
        border: 1px solid #e2e8f0;
        margin-bottom: 22px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 42px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 980px;
        color: #64748b;
        font-size: 0.94rem;
        font-weight: 500;
        padding: 6px 16px;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
        border: none !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        color: #0f172a !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08) !important;
        font-weight: 600 !important;
    }

    /* Primary CTA Buttons with Native Tactile Tap Response */
    .stButton>button {
        width: 100%;
        border-radius: 980px !important;
        font-size: 1.05rem !important;
        padding: 0.72rem 1.4rem !important;
        font-weight: 600 !important;
        min-height: 48px !important;
        border: none !important;
        background: linear-gradient(135deg, #0d9488 0%, #2563eb 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.25) !important;
        transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1) !important;
        letter-spacing: -0.01em;
    }
    .stButton>button:hover {
        transform: translateY(-2px) scale(1.01) !important;
        box-shadow: 0 8px 22px rgba(37, 99, 235, 0.35) !important;
    }
    .stButton>button:active, a:active {
        transform: scale(0.97) !important;
        filter: brightness(0.95);
    }

    /* View Switcher Segmented Buttons */
    div[class*="st-key-view_tab_"] button {
        border-radius: 980px !important;
        min-height: 42px !important;
        font-size: 0.94rem !important;
        font-weight: 600 !important;
    }

    /* HealthAI Assistant Bento Action Hub Buttons */
    div[class*="st-key-hub_btn_"] button {
        height: 120px !important;
        min-height: 120px !important;
        border-radius: 20px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        text-align: center !important;
        white-space: pre-wrap !important;
        line-height: 1.35 !important;
        padding: 12px 14px !important;
        border: none !important;
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.08) !important;
        transition: transform 0.22s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.22s cubic-bezier(0.16, 1, 0.3, 1) !important;
        cursor: pointer !important;
    }
    div[class*="st-key-hub_btn_"] button p {
        font-size: 0.98rem !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        line-height: 1.35 !important;
        margin: 0 !important;
        white-space: pre-wrap !important;
    }
    div[class*="st-key-hub_btn_"]:hover button {
        transform: translateY(-3px) scale(1.02) !important;
    }
    div[class*="st-key-hub_btn_scan"] button {
        background: linear-gradient(135deg, #059669 0%, #0d9488 100%) !important;
        box-shadow: 0 6px 20px rgba(13, 148, 136, 0.3) !important;
    }
    div[class*="st-key-hub_btn_reminders"] button {
        background: linear-gradient(135deg, #2563eb 0%, #4f46e5 100%) !important;
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.3) !important;
    }
    div[class*="st-key-hub_btn_vitals"] button {
        background: linear-gradient(135deg, #0284c7 0%, #06b6d4 100%) !important;
        box-shadow: 0 6px 20px rgba(2, 132, 199, 0.3) !important;
    }
    div[class*="st-key-hub_btn_emergency"] button {
        background: linear-gradient(135deg, #e11d48 0%, #ef4444 100%) !important;
        box-shadow: 0 6px 20px rgba(225, 29, 72, 0.3) !important;
    }

    /* 2x2 Bento Action Hub Grid on Mobile Phones */
    @media (max-width: 768px) {
        div[data-testid="stHorizontalBlock"]:has(div[class*="st-key-hub_btn_"]) {
            display: grid !important;
            grid-template-columns: 1fr 1fr !important;
            gap: 10px !important;
        }
        div[data-testid="stHorizontalBlock"]:has(div[class*="st-key-hub_btn_"]) > div {
            width: 100% !important;
            margin: 0 !important;
        }
        div[class*="st-key-hub_btn_"] button {
            min-height: 94px !important;
            height: auto !important;
            padding: 10px 8px !important;
            border-radius: 16px !important;
        }
        div[class*="st-key-hub_btn_"] button p {
            font-size: 0.86rem !important;
            line-height: 1.25 !important;
        }
    }

    /* HealthAI Metric Summary Tiles */
    div[class*="st-key-tile_btn_"] button {
        height: 104px !important;
        min-height: 104px !important;
        background: #ffffff !important;
        border: 1.5px solid #e2e8f0 !important;
        border-radius: 18px !important;
        padding: 10px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        text-align: center !important;
        white-space: pre-wrap !important;
        line-height: 1.3 !important;
        box-shadow: 0 2px 10px rgba(15, 23, 42, 0.03) !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
        cursor: pointer !important;
    }
    div[class*="st-key-tile_btn_"] button p {
        font-size: 0.92rem !important;
        color: #0f172a !important;
        font-weight: 600 !important;
        line-height: 1.3 !important;
        margin: 0 !important;
        white-space: pre-wrap !important;
    }
    div[class*="st-key-tile_btn_"]:hover button {
        background: #f8fafc !important;
        border-color: #2563eb !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(37, 99, 235, 0.12) !important;
    }

    /* 2x2 Metric Summary Grid on Mobile Phones */
    @media (max-width: 768px) {
        div[data-testid="stHorizontalBlock"]:has(div[class*="st-key-tile_btn_"]) {
            display: grid !important;
            grid-template-columns: 1fr 1fr !important;
            gap: 10px !important;
        }
        div[data-testid="stHorizontalBlock"]:has(div[class*="st-key-tile_btn_"]) > div {
            width: 100% !important;
            margin: 0 !important;
        }
        div[class*="st-key-tile_btn_"] button {
            min-height: 88px !important;
            height: auto !important;
            padding: 8px !important;
            border-radius: 16px !important;
        }
        div[class*="st-key-tile_btn_"] button p {
            font-size: 0.82rem !important;
            line-height: 1.25 !important;
        }
    }
    div[class*="st-key-tile_btn_"]:active button {
        transform: scale(0.98) !important;
    }

    /* Emergency Calling Buttons */
    div[class*="st-key-emg_call_"] a {
        color: #ffffff !important;
        border-radius: 14px !important;
        font-weight: 700 !important;
        font-size: 0.98rem !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.12) !important;
        transition: transform 0.18s ease, filter 0.18s ease !important;
        text-align: center !important;
        padding: 11px 14px !important;
        min-height: 46px !important;
    }
    div[class*="st-key-emg_call_"]:hover a {
        transform: translateY(-2px) !important;
        filter: brightness(1.08) !important;
    }
    div[class*="st-key-emg_call_108"] a { background: #d32f2f !important; }
    div[class*="st-key-emg_call_102"] a { background: #e65100 !important; }
    div[class*="st-key-emg_call_112"] a { background: #b71c1c !important; }
    div[class*="st-key-emg_call_104"] a { background: #1565c0 !important; }
    div[class*="st-key-emg_call_14416"] a { background: #4a148c !important; }
    div[class*="st-key-emg_call_1091"] a { background: #ad1457 !important; }

    /* Map Navigation Buttons */
    div[class*="st-key-link_maps_"] a {
        color: #ffffff !important;
        border-radius: 14px !important;
        font-weight: 700 !important;
        font-size: 0.98rem !important;
        padding: 12px 14px !important;
        min-height: 48px !important;
        text-align: center !important;
        margin-bottom: 8px !important;
        border: none !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1) !important;
        transition: transform 0.18s ease, filter 0.18s ease !important;
    }
    div[class*="st-key-link_maps_"]:hover a {
        transform: translateY(-2px) !important;
        filter: brightness(1.08) !important;
    }
    div[class*="st-key-link_maps_phc"] a { background: #065f46 !important; }
    div[class*="st-key-link_maps_chemist"] a { background: #0f766e !important; }
    div[class*="st-key-link_maps_jan"] a { background: #c2410c !important; }
    div[class*="st-key-link_maps_dr"] a { background: #1d4ed8 !important; }

    /* WhatsApp & Tele-MANAS CTA Buttons */
    div[class*="st-key-link_wa_share"] a {
        background: #25D366 !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1.02rem !important;
        border-radius: 14px !important;
        padding: 12px 16px !important;
        min-height: 48px !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(37,211,102,0.28) !important;
        transition: transform 0.18s ease !important;
        text-align: center !important;
        margin-bottom: 14px !important;
    }
    div[class*="st-key-link_wa_share"]:hover a {
        transform: translateY(-2px) scale(1.01) !important;
        filter: brightness(1.05) !important;
    }
    div[class*="st-key-link_tele_manas"] a {
        background: #c2185b !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 10px 14px !important;
    }

    /* Subtle Alert & Notice Cards */
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
        background-color: #f0fdf4;
        border-left: 5px solid #0d9488;
        padding: 12px 18px;
        border-radius: 16px;
        font-size: 0.95rem;
        margin-bottom: 14px;
        color: #115e59;
        border-top: 1px solid rgba(13, 148, 136, 0.15);
        border-right: 1px solid rgba(13, 148, 136, 0.15);
        border-bottom: 1px solid rgba(13, 148, 136, 0.15);
    }
    .due-badge {
        background-color: #ef4444;
        color: white;
        padding: 3px 9px;
        border-radius: 980px;
        font-weight: 700;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# A coherent visual layer for the complete care journey. The rules below intentionally
# keep Streamlit's native controls and the existing navigation/state model intact.
st.markdown("""
<style>
    :root {
        --ss-ink: #183b36;
        --ss-muted: #667b75;
        --ss-green: #177a63;
        --ss-green-dark: #105847;
        --ss-mint: #e8f4ed;
        --ss-paper: #f5f7f2;
        --ss-line: #dce7df;
        --ss-card: #ffffff;
        --ss-coral: #b64c3d;
        --ss-shadow: 0 12px 34px rgba(24, 59, 54, .075);
    }
    html, body, [class*="css"], .stApp {
        color: var(--ss-ink) !important;
        background: var(--ss-paper) !important;
        background-image: radial-gradient(ellipse at 90% 0%, rgba(217,235,219,.55), transparent 32%) !important;
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
        letter-spacing: 0 !important;
    }
    [data-testid="stAppViewContainer"] { background: transparent !important; }
    .main {
        max-width: 1180px !important;
        margin: 18px auto 30px !important;
        padding: 26px 34px 42px !important;
        background: rgba(255,255,255,.82) !important;
        border: 1px solid rgba(220,231,223,.9) !important;
        border-radius: 30px !important;
        box-shadow: 0 20px 60px rgba(33,69,58,.08) !important;
    }
    .block-container { max-width: 1120px !important; padding-top: 1rem !important; }
    h1, h2, h3, h4 { color: var(--ss-ink) !important; letter-spacing: -.035em !important; }
    h1 { font-size: clamp(1.65rem, 3vw, 2.2rem) !important; }
    h2 { font-size: clamp(1.45rem, 2.4vw, 1.9rem) !important; }
    h3 { font-size: 1.3rem !important; }
    p, label, .stCaption, [data-testid="stMarkdownContainer"] { color: inherit; }
    .apple-header {
        border: 1px solid var(--ss-line) !important;
        border-radius: 22px !important;
        background: rgba(255,255,255,.88) !important;
        box-shadow: 0 4px 18px rgba(24,59,54,.04) !important;
        padding: 15px 20px !important;
    }
    .apple-header h1 { color: var(--ss-ink) !important; background: none !important; -webkit-text-fill-color: var(--ss-ink) !important; }
    .hai-hero-banner {
        background: radial-gradient(ellipse at 84% 24%, rgba(255,255,255,.13), transparent 34%), linear-gradient(118deg, #143f36 0%, #1e5b49 62%, #39785e 100%) !important;
        border: 0 !important;
        border-radius: 26px !important;
        padding: 28px 32px !important;
        box-shadow: 0 20px 42px rgba(23,92,70,.22) !important;
        min-height: 300px;
        position: relative !important;
        overflow: hidden !important;
    }
    .hai-hero-banner::after { content: ""; position: absolute; width: 310px; height: 310px; border: 1px solid rgba(241,248,237,.12); border-radius: 50%; right: 9%; top: -150px; pointer-events: none; }
    .hero-layout { display: grid; grid-template-columns: minmax(0, 1.1fr) minmax(290px, .9fr); align-items: center; gap: 12px; position: relative; z-index: 1; }
    .hero-copy { position: relative; z-index: 2; }
    .hero-copy h2 { max-width: 600px; font-size: clamp(1.8rem,3.1vw,2.65rem) !important; letter-spacing: -.045em !important; line-height: 1.16 !important; }
    .hero-copy p { max-width: 600px !important; font-size: 1rem !important; }
    .hero-art { width: 100%; max-width: 440px; justify-self: end; margin: -10px 0 -14px; filter: drop-shadow(0 12px 18px rgba(11,47,37,.16)); animation: companion-float 6s ease-in-out infinite; }
    @keyframes companion-float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-7px); } }
    @media (prefers-reduced-motion: reduce) { .hero-art { animation: none; } * { scroll-behavior: auto !important; transition-duration: .01ms !important; } }
    div[data-testid="stSegmentedControl"] {
        border: 1px solid var(--ss-line) !important;
        background: #edf3ee !important;
        border-radius: 17px !important;
        padding: 5px !important;
        gap: 4px !important;
    }
    div[data-testid="stSegmentedControl"] button {
        border-radius: 12px !important;
        min-height: 44px !important;
        color: #526b63 !important;
        font-weight: 650 !important;
    }
    div[data-testid="stSegmentedControl"] button[aria-checked="true"] {
        background: white !important;
        color: var(--ss-green-dark) !important;
        box-shadow: 0 2px 9px rgba(26,67,54,.11) !important;
    }
    .stButton > button, .stLinkButton > a, [data-testid="stLinkButton"] a {
        border-radius: 14px !important;
        min-height: 48px !important;
        font-weight: 650 !important;
        letter-spacing: 0 !important;
        transition: transform .18s ease, box-shadow .18s ease, background .18s ease !important;
    }
    .stButton > button[kind="primary"] { background: var(--ss-green) !important; border: 1px solid var(--ss-green) !important; box-shadow: 0 5px 14px rgba(23,122,99,.18) !important; }
    .stButton > button[kind="secondary"] { background: white !important; color: var(--ss-ink) !important; border: 1px solid var(--ss-line) !important; box-shadow: none !important; }
    .stButton > button:hover, .stLinkButton > a:hover { transform: translateY(-2px) !important; box-shadow: var(--ss-shadow) !important; }
    div[class*="st-key-hub_btn_"] button {
        min-height: 136px !important;
        height: 100% !important;
        border-radius: 20px !important;
        border: 1px solid var(--ss-line) !important;
        background: white !important;
        color: var(--ss-ink) !important;
        box-shadow: 0 6px 18px rgba(24,59,54,.05) !important;
        white-space: pre-wrap !important;
        line-height: 1.45 !important;
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 18px !important;
    }
    div[class*="st-key-hub_btn_"] button p { color: var(--ss-ink) !important; font-size: 1rem !important; font-weight: 650 !important; }
    div[class*="st-key-hub_btn_scan"] button { background: var(--ss-mint) !important; border-color: #c9e0d0 !important; }
    div[class*="st-key-hub_btn_reminders"] button { background: #eff3fa !important; border-color: #d9e1ed !important; }
    div[class*="st-key-hub_btn_vitals"] button { background: #f3f2ec !important; border-color: #e3e0d2 !important; }
    div[class*="st-key-hub_btn_emergency"] button { background: #fff1ed !important; border-color: #f2d2c9 !important; color: #873d34 !important; }
    div[class*="st-key-tile_btn_"] button {
        min-height: 112px !important;
        border: 1px solid var(--ss-line) !important;
        border-radius: 18px !important;
        background: white !important;
        box-shadow: 0 4px 14px rgba(24,59,54,.04) !important;
        color: var(--ss-ink) !important;
    }
    div[class*="st-key-tile_btn_"] button p { color: var(--ss-ink) !important; font-weight: 650 !important; }
    div[class*="st-key-tile_btn_"]:hover button { border-color: #a8cbb6 !important; background: #fbfdfb !important; }
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: var(--ss-line) !important;
        border-radius: 18px !important;
        background: white !important;
        box-shadow: 0 5px 16px rgba(24,59,54,.035) !important;
    }
    [data-testid="stExpander"] { border: 1px solid var(--ss-line) !important; border-radius: 16px !important; background: white !important; }
    [data-baseweb="input"] > div, [data-baseweb="select"] > div, textarea {
        border-radius: 13px !important;
        border-color: #cbdad0 !important;
        background: white !important;
    }
    [data-testid="stAlert"] { border-radius: 15px !important; }
    .disclaimer-banner { background: #f0f5ee !important; color: #405c4f !important; border: 1px solid #dce9dc !important; border-left: 4px solid #6b9b76 !important; border-radius: 14px !important; }
    .uncertain-card { border-radius: 14px !important; }
    .confirmed-card { border-radius: 14px !important; }
    @media (max-width: 768px) {
        .main { margin: 0 !important; padding: 12px 14px 34px !important; border-radius: 0 0 20px 20px !important; box-shadow: none !important; }
        .block-container { padding: 12px 0.35rem 2rem !important; }
        .apple-header { border-radius: 17px !important; padding: 12px !important; }
        .hai-hero-banner { border-radius: 20px !important; padding: 22px 20px !important; min-height: 0 !important; }
        .hero-layout { grid-template-columns: 1fr; gap: 0; }
        .hero-art { max-width: 270px; justify-self: center; margin: -2px auto -20px; }
        div[class*="st-key-hub_btn_"] button { min-height: 105px !important; padding: 13px !important; border-radius: 17px !important; }
        div[class*="st-key-tile_btn_"] button { min-height: 92px !important; }
        div[data-testid="stSegmentedControl"] { overflow-x: auto !important; flex-wrap: nowrap !important; }
    }
</style>
""", unsafe_allow_html=True)


# -------------------------------------------------------------
# TOP NAVBAR: Apple Glassmorphic Header + User Identity + Language Selection
# -------------------------------------------------------------
lang = st.session_state.app_lang
u_role_badge = t("role_doctor", lang) if curr_u.role == "doctor" else (t("role_staff", lang) if curr_u.role == "staff" else t("role_patient", lang))
disp_name = curr_u.name.split('(')[0].strip() if curr_u.name.strip() else t('lbl_unregistered_guest', lang)
st.markdown(f"""
<div class="apple-header" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
    <div style="display: flex; align-items: center; gap: 14px;">
        <div style="background: #e8f4ed; width: 48px; height: 48px; border-radius: 16px; display: flex; align-items: center; justify-content: center; font-size: 1.6rem; border: 1px solid #cfe3d4;">
            🩺
        </div>
        <div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <h1 style="margin: 0; font-size: 1.6rem; font-weight: 800; letter-spacing: -0.03em; color: #183b36;">सेहत साथी</h1>
                <span style="font-size: 1.1rem; color: #667b75; font-weight: 600;">Sehat Saathi</span>
            </div>
            <p style="margin: 2px 0 0 0; font-size: 0.88rem; color: #64748b; font-weight: 500;">{t('app_tagline', lang)}</p>
        </div>
    </div>
    <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
        <a href="tel:108" style="background: linear-gradient(135deg, #ef4444, #dc2626); color:white; padding:7px 15px; border-radius:980px; font-size:0.84rem; font-weight:700; text-decoration:none; display:inline-flex; align-items:center; gap:6px; box-shadow:0 3px 12px rgba(239,68,68,0.35); transition:all 0.2s ease;">
            {t('btn_emergency_108', lang)}
        </a>
        <span style="background: #f1f5f9; border: 1px solid #cbd5e1; padding: 6px 13px; border-radius: 980px; font-size: 0.82rem; font-weight: 600; color: #0f172a;">
            {u_role_badge}: {disp_name}
        </span>
        <span style="background: #f0fdf4; border: 1px solid #86efac; padding: 6px 13px; border-radius: 980px; font-size: 0.82rem; font-weight: 600; color: #166534; display:inline-flex; align-items:center; gap:4px;">
            <span style="width:7px; height:7px; border-radius:50%; background:#22c55e;"></span>
            {t('status_active', lang)}
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# Navigation Menu, User Authentication, Language Selector & Accessibility Bar
col_menu, col_user_bar, col_lang, col_a11y = st.columns([1.8, 2.8, 1.8, 1.4])

with col_menu:
    with st.popover(t("btn_menu", lang), help="Open navigation menu"):
        st.markdown(f"#### {t('menu_title', lang)}")
        if st.button(f"📊 {t('nav_dashboard', lang)}", key="menu_item_dash", use_container_width=True):
            st.session_state.active_view = "dashboard"
            st.rerun()
        st.markdown("---")
        if st.button(f"📸 {t('tab_scan', lang)}", key="menu_item_scan", use_container_width=True):
            st.session_state.nav_ctrl = 0
            st.session_state.active_view = "screen"
            st.rerun()
        if st.button(f"⏰ {t('tab_reminders', lang)}", key="menu_item_reminders", use_container_width=True):
            st.session_state.nav_ctrl = 1
            st.session_state.active_view = "screen"
            st.rerun()
        if st.button(f"🩺 {t('tab_vitals', lang)}", key="menu_item_vitals", use_container_width=True):
            st.session_state.nav_ctrl = 2
            st.session_state.active_view = "screen"
            st.rerun()
        if st.button(f"🏥 {t('tab_facilities', lang)}", key="menu_item_facilities", use_container_width=True):
            st.session_state.nav_ctrl = 3
            st.session_state.active_view = "screen"
            st.rerun()
        if st.button(f"💬 {t('tab_chat', lang)}", key="menu_item_chat", use_container_width=True):
            st.session_state.nav_ctrl = 4
            st.session_state.active_view = "screen"
            st.rerun()
        if st.button(f"👨‍⚕️ {t('tab_doctor_portal', lang)}", key="menu_item_portal", use_container_width=True):
            st.session_state.nav_ctrl = 5
            st.session_state.active_view = "screen"
            st.rerun()
        if st.button(f"⚙️ {t('tab_settings', lang)}", key="menu_item_settings", use_container_width=True):
            st.session_state.nav_ctrl = 6
            st.session_state.active_view = "screen"
            st.rerun()

with col_user_bar:
    with st.popover(t("account_popover_btn", lang), help="Local demo profile settings; no sign-in is available"):
        st.markdown(f"#### {t('user_signin_title', lang)}")
        st.caption(t("user_signin_caption", lang))

        # This repository does not implement an OAuth callback, verified identity,
        # or a secure session. Do not send users to Google's consent page with a
        # placeholder client ID: it looks like sign-in but cannot complete.
        st.info(
            "Google sign-in is not available in this prototype. No account is created, "
            "and profile data is stored only in the local development database."
        )

        st.markdown(f"**{t('quick_role_select', lang)}**")
        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            if st.button(t("btn_role_pat", lang), key="btn_role_pat", type="primary" if curr_u.role == "patient" else "secondary"):
                st.session_state.current_user = AuthService.create_blank_user("patient")
                st.rerun()
        with col_r2:
            if st.button(t("btn_role_doc", lang), key="btn_role_doc", type="primary" if curr_u.role == "doctor" else "secondary"):
                st.session_state.current_user = AuthService.create_blank_user("doctor")
                st.rerun()
        with col_r3:
            if st.button(t("btn_role_staff", lang), key="btn_role_staff", type="primary" if curr_u.role == "staff" else "secondary"):
                st.session_state.current_user = AuthService.create_blank_user("staff")
                st.rerun()

        st.markdown("---")
        st.markdown(f"**{t('login_mobile_abha_header', lang)}**")

        if curr_u.role == "doctor":
            st.warning(
                "Doctor profile entry is a local demo only. This app does not verify "
                "medical registration, authenticate clinicians, or protect the doctor portal. "
                "Do not enter real clinician or patient information."
            )
            st.markdown(f"*{t('lbl_doctor_profile_hdr', lang)}*")
            d_name = st.text_input(t("lbl_doctor_name", lang), value=curr_u.name, key="inp_doc_name")
            d_license = st.text_input(t("lbl_medical_license", lang), value=curr_u.medical_license_no or "", key="inp_doc_license")
            d_spec = st.text_input(t("lbl_specialization", lang), value=curr_u.specialization or "", key="inp_doc_spec")
            d_hosp = st.text_input(t("lbl_hospital_clinic", lang), value=curr_u.hospital_clinic or "", key="inp_doc_hosp")
            d_qual = st.text_input(t("lbl_qualification", lang), value=curr_u.qualification or "", key="inp_doc_qual")
            d_phone = st.text_input(t("lbl_doctor_phone", lang), value=curr_u.phone or "", key="inp_doc_phone")

            if st.button(t("btn_save_profile", lang), key="btn_save_user_prof"):
                new_u = AuthService.create_custom_user(
                    name=d_name,
                    email=curr_u.email,
                    phone=d_phone,
                    role="doctor",
                    medical_license_no=d_license,
                    specialization=d_spec,
                    hospital_clinic=d_hosp,
                    qualification=d_qual,
                    user_id=curr_u.id
                )
                st.session_state.current_user = new_u
                clinical_db.upsert_user(new_u.model_dump())
                st.success(t("msg_profile_saved", lang))
                st.rerun()

        elif curr_u.role == "staff":
            st.markdown(f"*{t('lbl_staff_profile_hdr', lang)}*")
            s_name = st.text_input(t("lbl_staff_name", lang), value=curr_u.name, key="inp_staff_name")
            s_desig = st.text_input(t("lbl_staff_designation", lang), value=curr_u.staff_designation or "", key="inp_staff_desig")
            s_empid = st.text_input(t("lbl_employee_id", lang), value=curr_u.employee_id or "", key="inp_staff_empid")
            s_ward = st.text_input(t("lbl_department_ward", lang), value=curr_u.department_ward or "", key="inp_staff_ward")
            s_hosp = st.text_input(t("lbl_hospital_clinic", lang), value=curr_u.hospital_clinic or "", key="inp_staff_hosp")
            s_phone = st.text_input(t("lbl_staff_phone", lang), value=curr_u.phone or "", key="inp_staff_phone")

            if st.button(t("btn_save_profile", lang), key="btn_save_user_prof"):
                new_u = AuthService.create_custom_user(
                    name=s_name,
                    email=curr_u.email,
                    phone=s_phone,
                    role="staff",
                    staff_designation=s_desig,
                    employee_id=s_empid,
                    department_ward=s_ward,
                    hospital_clinic=s_hosp,
                    user_id=curr_u.id
                )
                st.session_state.current_user = new_u
                clinical_db.upsert_user(new_u.model_dump())
                st.success(t("msg_profile_saved", lang))
                st.rerun()

        else: # patient
            st.markdown(f"*{t('lbl_patient_profile_hdr', lang)}*")
            p_name = st.text_input(t("lbl_patient_name", lang), value=curr_u.name, key="inp_pat_name")
            col_p_a, col_p_g = st.columns(2)
            with col_p_a:
                p_age = st.number_input(t("lbl_patient_age_inp", lang), min_value=0, max_value=120, value=curr_u.age or 0, key="inp_pat_age")
            with col_p_g:
                gender_opts = ["पुरुष (Male)", "महिला (Female)", "अन्य (Other)"]
                g_idx = 0
                if curr_u.gender in gender_opts:
                    g_idx = gender_opts.index(curr_u.gender)
                p_gender = st.selectbox(t("lbl_patient_gender", lang), gender_opts, index=g_idx, key="inp_pat_gender")

            bg_opts = ["--", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
            b_idx = 0
            if curr_u.blood_group in bg_opts:
                b_idx = bg_opts.index(curr_u.blood_group)
            p_blood = st.selectbox(t("lbl_patient_blood_group", lang), bg_opts, index=b_idx, key="inp_pat_blood")

            p_phone = st.text_input(t("lbl_mobile_optional", lang), value=curr_u.phone or "", key="inp_pat_phone")
            p_abha = st.text_input(t("lbl_abha_optional", lang), value=curr_u.abha_id or "", placeholder="उदा. 91-1234-5678-9012" if lang != "en" else "e.g. 91-1234-5678-9012", key="inp_pat_abha")
            p_emg = st.text_input(t("lbl_emergency_contact_inp", lang), value=curr_u.emergency_contact or "", key="inp_pat_emg")
            p_addr = st.text_input(t("lbl_patient_address", lang), value=curr_u.address or "", key="inp_pat_addr")

            if st.button(t("btn_save_profile", lang), key="btn_save_user_prof"):
                new_u = AuthService.create_custom_user(
                    name=p_name,
                    email=curr_u.email,
                    phone=p_phone,
                    abha_id=p_abha,
                    role="patient",
                    age=int(p_age) if p_age > 0 else None,
                    gender=p_gender,
                    blood_group=p_blood if p_blood != "--" else None,
                    emergency_contact=p_emg,
                    address=p_addr,
                    user_id=curr_u.id
                )
                st.session_state.current_user = new_u
                clinical_db.upsert_user(new_u.model_dump())
                pat_id = f"pat_{new_u.id}"
                clinical_db.upsert_patient({
                    "id": pat_id,
                    "user_id": new_u.id,
                    "name": new_u.name,
                    "age": new_u.age or 0,
                    "gender": new_u.gender or "",
                    "blood_group": new_u.blood_group or "",
                    "emergency_contact": new_u.emergency_contact or (new_u.phone or ""),
                    "consent_shared_treatment": 1
                })
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


# Sehat Saathi care hero
st.markdown(f"""
<div class="hai-hero-banner">
  <div class="hero-layout">
    <div class="hero-copy">
      <div style="display:inline-flex;align-items:center;gap:8px;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.19);padding:7px 13px;border-radius:999px;font-size:.82rem;font-weight:650;color:#e3f4df;margin-bottom:17px;">
        <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#b8df94;box-shadow:0 0 12px #b8df94;"></span>
        {t('hero_badge', lang)}
      </div>
      <h2 style="margin:0 0 10px;color:#fff;">{t('hero_headline', lang)}</h2>
      <p style="margin:0 0 19px;color:#e1eee6;line-height:1.65;">{t('hero_sub', lang)}</p>
      <div style="display:flex;gap:8px;flex-wrap:wrap;font-size:.79rem;">
        <span style="background:rgba(255,255,255,.10);border:1px solid rgba(255,255,255,.16);padding:7px 11px;border-radius:999px;color:#f3f8f3;font-weight:600;">{t('hero_chip_ocr', lang)}</span>
        <span style="background:rgba(255,255,255,.10);border:1px solid rgba(255,255,255,.16);padding:7px 11px;border-radius:999px;color:#f3f8f3;font-weight:600;">{t('hero_chip_reminders', lang)}</span>
        <span style="background:rgba(255,255,255,.10);border:1px solid rgba(255,255,255,.16);padding:7px 11px;border-radius:999px;color:#f3f8f3;font-weight:600;">{t('hero_chip_vitals', lang)}</span>
        <span style="background:rgba(255,255,255,.10);border:1px solid rgba(255,255,255,.16);padding:7px 11px;border-radius:999px;color:#f3f8f3;font-weight:600;">{t('hero_chip_clinics', lang)}</span>
      </div>
    </div>
    <img class="hero-art" src="/app/static/care-companion.svg" alt="Sehat Saathi care companion illustration" />
  </div>
</div>
""", unsafe_allow_html=True)

# Dynamic counts for home cards
all_current_reminders = reminder_service.get_all_reminders()
active_rem_count = len([r for r in all_current_reminders if r.enabled])
recent_vitals_count = len(device_service.get_all_readings())

# 4 Apple Health-Style Action Cards (Interactive Visual Home Hub)
col_c1, col_c2, col_c3, col_c4 = st.columns(4)

with col_c1:
    if st.button(f"📸 {t('card_scan_title', lang)}\n\n{t('card_scan_desc', lang)}", key="hub_btn_scan", use_container_width=True):
        st.session_state.nav_ctrl = 0
        st.session_state.active_view = "screen"
        st.rerun()

with col_c2:
    if st.button(f"⏰ {t('card_reminders_title', lang)}\n\n{active_rem_count} {t('card_reminders_desc', lang)}", key="hub_btn_reminders", use_container_width=True):
        st.session_state.nav_ctrl = 1
        st.session_state.active_view = "screen"
        st.rerun()

with col_c3:
    if st.button(f"🩺 {t('card_vitals_title', lang)}\n\n{recent_vitals_count} {t('card_vitals_desc', lang)}", key="hub_btn_vitals", use_container_width=True):
        st.session_state.nav_ctrl = 2
        st.session_state.active_view = "screen"
        st.rerun()

with col_c4:
    if st.button(f"🚨 {t('card_emergency_title', lang)}\n\n{t('card_emergency_desc', lang)}", key="hub_btn_emergency", use_container_width=True):
        st.session_state.open_emergency_drawer = not st.session_state.get("open_emergency_drawer", False)
        st.rerun()

# Feature: Apple Health-Style Summary Tile Banner
target_pat_id = f"pat_{curr_u.id}"
pat_vitals_summary = clinical_db.get_patient_vitals(target_pat_id, limit=4)
bp_val = "--"
bp_status = t("tile_no_data", lang)
spo2_val = "--"
spo2_status = t("tile_no_data", lang)
sugar_val = "--"
sugar_status = t("tile_no_data", lang)

for pv in pat_vitals_summary:
    m_name = pv.get("metric_name", "")
    if "रक्तचाप" in m_name or "BP" in m_name or "Blood Pressure" in m_name:
        bp_val = f"{pv['value']} {pv['unit']}"
        bp_status = pv.get("status_flag", t("tile_bp_status", lang))
    elif "SpO2" in m_name or "ऑक्सीजन" in m_name:
        spo2_val = f"{pv['value']}{pv['unit']}"
        spo2_status = pv.get("status_flag", t("tile_spo2_status", lang))
    elif "Sugar" in m_name or "शुगर" in m_name:
        sugar_val = f"{pv['value']} {pv['unit']}"
        sugar_status = pv.get("status_flag", t("tile_sugar_status", lang))

adh_stat = clinical_db.get_patient_adherence_rate(target_pat_id)
if adh_stat['total_scheduled'] == 0:
    adh_pct_str = "--"
    adh_sub = t("tile_no_reminders_yet", lang)
else:
    adh_pct_str = f"{adh_stat['percentage']}%"
    adh_sub = f"⭐ {adh_stat['total_taken']} {t('tile_doses_taken', lang)}"

col_t1, col_t2, col_t3, col_t4 = st.columns(4)
with col_t1:
    if st.button(f"💓 {t('tile_bp_title', lang)}\n{bp_val}\n● {bp_status}", key="tile_btn_bp", use_container_width=True):
        st.session_state.nav_ctrl = 2
        st.session_state.active_view = "screen"
        st.rerun()
with col_t2:
    if st.button(f"🫁 {t('tile_spo2_title', lang)}\n{spo2_val}\n● {spo2_status}", key="tile_btn_spo2", use_container_width=True):
        st.session_state.nav_ctrl = 2
        st.session_state.active_view = "screen"
        st.rerun()
with col_t3:
    if st.button(f"🩸 {t('tile_sugar_title', lang)}\n{sugar_val}\n● {sugar_status}", key="tile_btn_sugar", use_container_width=True):
        st.session_state.nav_ctrl = 2
        st.session_state.active_view = "screen"
        st.rerun()
with col_t4:
    if st.button(f"💊 {t('tile_adherence_title', lang)}\n{adh_pct_str}\n{adh_sub}", key="tile_btn_adh", use_container_width=True):
        st.session_state.nav_ctrl = 1
        st.session_state.active_view = "screen"
        st.rerun()

# Safety Disclaimer (Rule 12)
st.markdown(f'<div class="disclaimer-banner">{t("safety_disclaimer", lang)}</div>', unsafe_allow_html=True)

# Persistent 1-Tap Emergency Calling Bar (India Emergency Agencies)
with st.expander(t("emergency_drawer_title", lang), expanded=st.session_state.get("open_emergency_drawer", False)):
    st.markdown(t("emergency_instruction", lang))
    agencies = EmergencyService.get_emergency_numbers()
    col_em1, col_em2 = st.columns(2)
    for idx, ag in enumerate(agencies):
        target_col = col_em1 if idx % 2 == 0 else col_em2
        with target_col:
            tel_link = EmergencyService.build_tel_link(ag.get("number", "108"))
            label_text = ag.get("name_en", ag.get("name_hindi", "Emergency")) if lang == "en" else ag.get("name_hindi", "आपातकालीन")
            ag_icon = ag.get("icon", "🚨")
            ag_num = ag.get("number", "108")
            st.link_button(
                f"{ag_icon} {label_text} ({ag_num})",
                tel_link,
                use_container_width=True,
                key=f"emg_call_{ag_num}",
            )


# -------------------------------------------------------------
# MAIN NAVIGATION: Apple Segmented Control Bar
# -------------------------------------------------------------
nav_labels = [
    f"📸 {t('tab_scan', lang)}",
    f"⏰ {t('tab_reminders', lang)}",
    f"🩺 {t('tab_vitals', lang)}",
    f"🏥 {t('tab_facilities', lang)}",
    f"💬 {t('tab_chat', lang)}",
    f"👨‍⚕️ {t('tab_doctor_portal', lang)}",
    f"⚙️ {t('tab_settings', lang)}"
]

if "target_nav_ctrl" in st.session_state:
    st.session_state.nav_ctrl = st.session_state.pop("target_nav_ctrl")

chosen_tab = st.segmented_control(
    "Navigation",
    options=list(range(len(nav_labels))),
    format_func=lambda i: nav_labels[i],
    key="nav_ctrl",
    label_visibility="collapsed"
)
active_tab = st.session_state.nav_ctrl if st.session_state.nav_ctrl is not None else 0

# Synchronize segmented_control tab changes with screen view
if "last_nav_ctrl" not in st.session_state:
    st.session_state.last_nav_ctrl = active_tab
elif st.session_state.last_nav_ctrl != active_tab:
    st.session_state.active_view = "screen"
    st.session_state.last_nav_ctrl = active_tab

# View Switcher Bar (Dashboard vs Dedicated Screen)
col_vmode1, col_vmode2 = st.columns([1, 1])
with col_vmode1:
    if st.button("📊 " + t("nav_dashboard", lang), key="view_tab_dashboard", type="primary" if st.session_state.get("active_view") == "dashboard" else "secondary", use_container_width=True):
        st.session_state.active_view = "dashboard"
        st.rerun()
with col_vmode2:
    if st.button("📱 " + nav_labels[active_tab], key="view_tab_screen", type="primary" if st.session_state.get("active_view", "screen") == "screen" else "secondary", use_container_width=True):
        st.session_state.active_view = "screen"
        st.rerun()

# -------------------------------------------------------------
# DASHBOARD VIEW: Summary Overview, 10-Mile Proximity Spotlight & Modules Grid
# -------------------------------------------------------------
if st.session_state.get("active_view") == "dashboard":
    st.subheader(f"📊 {t('nav_dashboard', lang)}")
    st.caption(t("hero_sub", lang))

    # 1. Proximity Radar Spotlight (< 10 Miles)
    dash_locality = st.session_state.get("user_locality", "Neemrana")
    dash_prox = ProximityLocationService.find_facilities_within_proximity(
        locality=dash_locality,
        max_radius_miles=10.0
    )
    dash_nearest = dash_prox.get("nearest_facility")

    if dash_nearest:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%); border: 2px solid #059669; border-radius: 20px; padding: 20px 24px; margin-bottom: 22px; box-shadow: 0 6px 20px rgba(5, 150, 105, 0.12);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 8px;">
                <span style="background: #059669; color: white; padding: 4px 12px; border-radius: 980px; font-size: 0.82rem; font-weight: 700;">
                    {t('spotlight_badge', lang)}
                </span>
                <span style="font-size: 0.95rem; font-weight: 700; color: #065f46;">
                    📍 {dash_nearest['distance_miles']} miles away ({dash_nearest['distance_km']} km)
                </span>
            </div>
            <h3 style="margin: 0 0 6px 0; color: #064e3b; font-size: 1.35rem; font-weight: 800;">
                {dash_nearest['name_en'] if lang == 'en' else dash_nearest['name_hindi']}
            </h3>
            <p style="margin: 0 0 4px 0; font-size: 0.92rem; color: #047857; font-weight: 600;">
                {dash_nearest['category_label']} • {dash_nearest['address']}
            </p>
            <p style="margin: 0 0 12px 0; font-size: 0.86rem; color: #374151;">
                ⏰ <b>{dash_nearest['timing']}</b>
            </p>
        </div>
        """, unsafe_allow_html=True)

        col_d_call, col_d_dir, col_d_more = st.columns([1, 1, 1.2])
        with col_d_call:
            st.link_button(
                f"📞 {t('btn_call_support', lang)} ({dash_nearest['phone']})",
                dash_nearest['tel_url'],
                use_container_width=True,
                key="dash_spotlight_call"
            )
        with col_d_dir:
            st.link_button(
                f"🗺️ {t('btn_maps_directions', lang)}",
                dash_nearest['directions_url'],
                use_container_width=True,
                key="dash_spotlight_dir"
            )
        with col_d_more:
            if st.button(f"🏥 {t('tab_facilities', lang)} →", key="dash_open_fac_btn", use_container_width=True):
                st.session_state.target_nav_ctrl = 3
                st.session_state.active_view = "screen"
                st.rerun()

    st.markdown("---")
    st.markdown(f"#### {t('dashboard_services_title', lang)}")

    # 2. Comprehensive Health Modules Grid
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        with st.container(border=True):
            st.markdown(f"**📸 {t('tab_scan', lang)}**")
            st.caption(t("card_scan_desc", lang))
            if st.button(f"{t('lbl_open_screen', lang)}", key="grid_btn_scan", use_container_width=True):
                st.session_state.target_nav_ctrl = 0
                st.session_state.active_view = "screen"
                st.rerun()

        with st.container(border=True):
            st.markdown(f"**⏰ {t('tab_reminders', lang)}**")
            st.caption(f"{active_rem_count} {t('card_reminders_desc', lang)}")
            if st.button(f"{t('lbl_open_screen', lang)}", key="grid_btn_rem", use_container_width=True):
                st.session_state.target_nav_ctrl = 1
                st.session_state.active_view = "screen"
                st.rerun()

        with st.container(border=True):
            st.markdown(f"**🩺 {t('tab_vitals', lang)}**")
            st.caption(f"{recent_vitals_count} {t('card_vitals_desc', lang)}")
            if st.button(f"{t('lbl_open_screen', lang)}", key="grid_btn_vit", use_container_width=True):
                st.session_state.target_nav_ctrl = 2
                st.session_state.active_view = "screen"
                st.rerun()

    with col_m2:
        with st.container(border=True):
            st.markdown(f"**🏥 {t('tab_facilities', lang)}**")
            st.caption(f"{dash_prox['total_found']} {t('status_active', lang)} (< 10 miles)")
            if st.button(f"{t('lbl_open_screen', lang)}", key="grid_btn_fac", use_container_width=True):
                st.session_state.target_nav_ctrl = 3
                st.session_state.active_view = "screen"
                st.rerun()

        with st.container(border=True):
            st.markdown(f"**💬 {t('tab_chat', lang)}**")
            st.caption(t("chat_sub", lang))
            if st.button(f"{t('lbl_open_screen', lang)}", key="grid_btn_chat", use_container_width=True):
                st.session_state.target_nav_ctrl = 4
                st.session_state.active_view = "screen"
                st.rerun()

        with st.container(border=True):
            st.markdown(f"**👨‍⚕️ {t('tab_doctor_portal', lang)}**")
            st.caption(t("portal_sub", lang))
            if st.button(f"{t('lbl_open_screen', lang)}", key="grid_btn_portal", use_container_width=True):
                st.session_state.target_nav_ctrl = 5
                st.session_state.active_view = "screen"
                st.rerun()

is_dashboard_active = st.session_state.get("active_view") == "dashboard"

if not is_dashboard_active:
    col_ret1, col_ret2 = st.columns([1.5, 2.5])
    with col_ret1:
        if st.button(t("btn_back_to_dashboard", lang), key="btn_return_dashboard"):
            st.session_state.active_view = "dashboard"
            st.rerun()
    with col_ret2:
        st.markdown(f"**📱 {nav_labels[active_tab]}**")

# -------------------------------------------------------------
# TAB 1: SCAN & PROCESS PRESCRIPTION
# -------------------------------------------------------------
if active_tab == 0 and not is_dashboard_active:
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
elif active_tab == 1 and not is_dashboard_active:
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
        st.link_button(
            f"📲 {t('share_wa_btn', lang)}",
            f"https://api.whatsapp.com/send?text={encoded_text}",
            use_container_width=True,
            key="link_wa_share"
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
elif active_tab == 2 and not is_dashboard_active:
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
            dev_lower = dev_choice.lower()
            if "oximeter" in dev_lower or "ऑक्सी" in dev_lower or "spo2" in dev_lower:
                v_metric = "SpO2"
                v_unit = "%"
                v_hint = "e.g. 98"
            elif "bp" in dev_lower or "रक्तचाप" in dev_lower or "pressure" in dev_lower:
                v_metric = "Blood Pressure"
                v_unit = "mmHg"
                v_hint = "e.g. 120/80"
            elif "gluco" in dev_lower or "ग्लूको" in dev_lower or "sugar" in dev_lower or "शुगर" in dev_lower:
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
                <div style="background-color:#fce4ec; border-left:6px solid #c2185b; padding:12px; border-radius:12px; margin-top:10px; margin-bottom:8px;">
                    🌸 <b>{t('tele_manas_box_title', lang)}</b><br>
                    {t('tele_manas_box_desc', lang)}
                </div>
                """, unsafe_allow_html=True)
                st.link_button(
                    f"📞 {t('tele_manas_call_btn', lang)} (14416)",
                    "tel:14416",
                    use_container_width=True,
                    key="link_tele_manas"
                )


# -------------------------------------------------------------
# TAB 4: NEARBY CLINICS & 10-MILE PROXIMITY RADAR
# -------------------------------------------------------------
elif active_tab == 3 and not is_dashboard_active:
    st.subheader(t("facilities_heading", lang))
    st.caption(t("facilities_sub", lang))

    col_loc1, col_loc2 = st.columns([2, 1])
    with col_loc1:
        user_locality = st.text_input(
            t("lbl_user_locality", lang),
            value=st.session_state.get("user_locality", "Neemrana"),
            placeholder="e.g. Behror, Neemrana, Alwar" if lang == "en" else "उदा. बहरोड़, नीमराना, अलवर",
            key="inp_user_locality"
        )
        st.session_state.user_locality = user_locality
    with col_loc2:
        max_radius = st.slider(
            t("lbl_radius_filter", lang),
            min_value=1.0,
            max_value=25.0,
            value=10.0,
            step=1.0,
            key="proximity_radius_slider"
        )

    # Category selector
    cat_options = [
        ("all", t("opt_all_facilities", lang)),
        ("clinic", t("opt_clinics_only", lang)),
        ("chemist", t("opt_chemists_only", lang)),
        ("jan_aushadhi", t("opt_jan_aushadhi_only", lang))
    ]
    chosen_cat_tuple = st.selectbox(
        t("lbl_category_filter", lang),
        cat_options,
        format_func=lambda x: x[1],
        key="fac_cat_filter"
    )
    chosen_cat = chosen_cat_tuple[0]

    # Run 10-Mile Proximity Search
    prox_res = ProximityLocationService.find_facilities_within_proximity(
        locality=user_locality,
        max_radius_miles=max_radius,
        category=chosen_cat
    )

    nearest = prox_res.get("nearest_facility")

    # 1. Spotlight Card for Nearest Facility (< 10 Miles)
    if nearest:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%); border: 2px solid #059669; border-radius: 18px; padding: 18px 22px; margin-bottom: 20px; box-shadow: 0 4px 16px rgba(5, 150, 105, 0.12);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 8px;">
                <span style="background: #059669; color: white; padding: 4px 12px; border-radius: 980px; font-size: 0.82rem; font-weight: 700;">
                    {t('spotlight_badge', lang)}
                </span>
                <span style="font-size: 0.95rem; font-weight: 700; color: #065f46;">
                    📍 {nearest['distance_miles']} miles away ({nearest['distance_km']} km)
                </span>
            </div>
            <h3 style="margin: 0 0 6px 0; color: #064e3b; font-size: 1.3rem; font-weight: 800;">
                {nearest['name_en'] if lang == 'en' else nearest['name_hindi']}
            </h3>
            <p style="margin: 0 0 4px 0; font-size: 0.9rem; color: #047857; font-weight: 600;">
                {nearest['category_label']} • {nearest['address']}
            </p>
            <p style="margin: 0 0 12px 0; font-size: 0.85rem; color: #374151;">
                ⏰ <b>{nearest['timing']}</b>
            </p>
        </div>
        """, unsafe_allow_html=True)

        col_spot_call, col_spot_dir = st.columns(2)
        with col_spot_call:
            st.link_button(
                f"📞 {t('btn_call_support', lang)} ({nearest['phone']})",
                nearest['tel_url'],
                use_container_width=True,
                key="btn_spotlight_call"
            )
        with col_spot_dir:
            st.link_button(
                f"🗺️ {t('btn_maps_directions', lang)}",
                nearest['directions_url'],
                use_container_width=True,
                key="btn_spotlight_dir"
            )
        st.markdown("---")

    # 2. List of all verified facilities within proximity
    fac_list = prox_res.get("facilities", [])
    if fac_list:
        st.markdown(f"#### 📍 {t('facilities_heading', lang)} (< {int(max_radius)} miles): {len(fac_list)} {t('status_active', lang)}")
        for idx, f_item in enumerate(fac_list):
            f_name = f_item['name_en'] if lang == 'en' else f_item['name_hindi']
            with st.expander(f"📍 {f_item['distance_miles']} mi — {f_name} ({f_item['category_label']})", expanded=(idx == 0)):
                st.markdown(f"**{t('lbl_address_village', lang)}** {f_item['address']}")
                st.markdown(f"**समय (Timing):** {f_item['timing']}")
                if f_item.get("services"):
                    st.markdown(f"**{t('services_offered', lang)}**")
                    for s_item in f_item["services"]:
                        st.write(f"• {s_item}")

                col_fc_call, col_fc_dir = st.columns(2)
                with col_fc_call:
                    st.link_button(
                        f"📞 Call {f_item['phone']}",
                        f_item['tel_url'],
                        use_container_width=True,
                        key=f"fac_call_{f_item['id']}"
                    )
                with col_fc_dir:
                    st.link_button(
                        f"🗺️ Directions",
                        f_item['directions_url'],
                        use_container_width=True,
                        key=f"fac_dir_{f_item['id']}"
                    )
    else:
        st.info(t("msg_no_facilities_found", lang))

    st.markdown("---")
    st.markdown(f"**🌐 Google Maps Live Search ({user_locality}):**")

    # Universal Google Maps Buttons (Preserves keys for backwards compatibility)
    col_map1, col_map2 = st.columns(2)
    with col_map1:
        phc_url = PreventionAndFacilitiesService.build_maps_search_url("Primary Health Centre PHC Hospital", user_locality)
        st.link_button(
            f"🏥 {t('maps_phc_btn', lang)}",
            phc_url,
            use_container_width=True,
            key="link_maps_phc"
        )

        chemist_url = PreventionAndFacilitiesService.build_maps_search_url("Medical Store Chemist Pharmacy", user_locality)
        st.link_button(
            f"💊 {t('maps_chemist_btn', lang)}",
            chemist_url,
            use_container_width=True,
            key="link_maps_chemist"
        )

    with col_map2:
        ja_url = PreventionAndFacilitiesService.build_maps_search_url("Pradhan Mantri Jan Aushadhi Kendra", user_locality)
        st.link_button(
            f"🏛️ {t('maps_jan_btn', lang)}",
            ja_url,
            use_container_width=True,
            key="link_maps_jan"
        )

        dr_url = PreventionAndFacilitiesService.build_maps_search_url("Doctor Clinic", user_locality)
        st.link_button(
            f"👨‍⚕️ {t('maps_doctor_btn', lang)}",
            dr_url,
            use_container_width=True,
            key="link_maps_dr"
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
elif active_tab == 4 and not is_dashboard_active:
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
elif active_tab == 5 and not is_dashboard_active:
    if curr_u.role == "doctor":
        st.subheader(t("portal_doctor_heading", lang))
        st.caption(f"🩺 {curr_u.name or 'Doctor'} • {curr_u.medical_license_no or 'NMC Reg Pending'} • {curr_u.specialization or 'General Medicine'} • {curr_u.hospital_clinic or 'Hospital/CHC'}")
    elif curr_u.role == "staff":
        st.subheader(t("portal_staff_heading", lang))
        st.caption(f"🏥 {curr_u.name or 'Staff'} • {curr_u.staff_designation or 'Healthcare Staff'} • {curr_u.employee_id or 'ID Pending'} • {curr_u.department_ward or 'OPD / Ward'}")
    else:
        st.subheader(t("portal_patient_heading", lang))
        st.caption(f"👤 {curr_u.name or 'Patient'} • {curr_u.phone or 'Contact'} • {t('portal_sub', lang)}")

    # Notice of clinical purpose & consent
    st.markdown(f"""
    <div style="background-color:#e0f2fe; border-left:6px solid #0284c7; padding:12px 16px; border-radius:12px; margin-bottom:14px;">
        {t("portal_disha_notice", lang)}
    </div>
    """, unsafe_allow_html=True)

    # Patient Selector & Dynamic Registration
    all_pats = clinical_db.list_all_patients()
    if not all_pats:
        st.markdown(f"""
        <div style="background:#f8fafc; border:1.5px dashed #cbd5e1; border-radius:18px; padding:20px; text-align:center; margin-bottom:16px;">
            <div style="font-size:2.2rem; margin-bottom:6px;">📋</div>
            <div style="font-size:1.15rem; font-weight:700; color:#1e293b;">{t('portal_no_patients_title', lang)}</div>
            <div style="font-size:0.9rem; color:#64748b; margin-top:4px;">{t('portal_no_patients_desc', lang)}</div>
        </div>
        """, unsafe_allow_html=True)

        col_act1, col_act2 = st.columns([1, 1])
        with col_act2:
            if st.button("⚡ त्वरित डेमो मरीज डेटा जोड़ें (Quick Sample Patient)", key="btn_quick_sample_patient"):
                new_pid = f"pat_{uuid.uuid4().hex[:8]}"
                new_uid = f"user_{uuid.uuid4().hex[:8]}"
                clinical_db.upsert_user({
                    "id": new_uid,
                    "name": "राम अवतार (Ram Avtar)",
                    "role": "patient",
                    "phone": "9876543210",
                    "age": 62,
                    "gender": "पुरुष (Male)",
                    "blood_group": "B+",
                    "emergency_contact": "9876500000",
                    "address": "गाँव माजरा, नीमराना"
                })
                clinical_db.upsert_patient({
                    "id": new_pid,
                    "user_id": new_uid,
                    "name": "राम अवतार (Ram Avtar)",
                    "age": 62,
                    "gender": "पुरुष (Male)",
                    "blood_group": "B+",
                    "emergency_contact": "9876500000",
                    "consent_shared_treatment": 1
                })
                clinical_db.save_vital(new_pid, "डिजिटल बीपी मॉनिटर", "रक्तचाप (Blood Pressure)", "135/86", "mmHg", "सामान्य (Normal)")
                clinical_db.record_adherence(new_pid, "Amlodipine 5mg", "1 गोली", "सुबह", "08:00", taken_status=True)
                st.success("डेमो मरीज पंजीकृत! (Sample patient ready for review)")
                st.rerun()

        with st.form("reg_first_patient_form"):
            st.markdown(f"#### {t('form_reg_patient_title', lang)}")
            col_np1, col_np2 = st.columns(2)
            with col_np1:
                np_name = st.text_input(t("lbl_patient_name", lang), key="np_name_init")
                np_age = st.number_input(t("lbl_patient_age_inp", lang), min_value=1, max_value=120, value=45, key="np_age_init")
                np_gender = st.selectbox(t("lbl_patient_gender", lang), ["पुरुष (Male)", "महिला (Female)", "अन्य (Other)"], key="np_gender_init")
            with col_np2:
                np_blood = st.selectbox(t("lbl_patient_blood_group", lang), ["B+", "A+", "O+", "AB+", "B-", "A-", "O-", "AB-"], key="np_blood_init")
                np_phone = st.text_input(t("lbl_mobile_optional", lang), key="np_phone_init")
                np_emg = st.text_input(t("lbl_emergency_contact_inp", lang), key="np_emg_init")
            np_complaint = st.text_input(t("lbl_chief_complaint", lang), placeholder=t("ph_chief_complaint", lang), key="np_comp_init")
            np_addr = st.text_input(t("lbl_address_village", lang), placeholder=t("ph_address_village", lang), key="np_addr_init")

            if st.form_submit_button(t("btn_register_patient_modal", lang), type="primary"):
                if np_name.strip():
                    new_pid = f"pat_{uuid.uuid4().hex[:8]}"
                    new_uid = f"user_{uuid.uuid4().hex[:8]}"
                    clinical_db.upsert_user({
                        "id": new_uid,
                        "name": np_name,
                        "role": "patient",
                        "phone": np_phone,
                        "age": int(np_age),
                        "gender": np_gender,
                        "blood_group": np_blood,
                        "emergency_contact": np_emg,
                        "address": np_addr
                    })
                    clinical_db.upsert_patient({
                        "id": new_pid,
                        "user_id": new_uid,
                        "name": np_name,
                        "age": int(np_age),
                        "gender": np_gender,
                        "blood_group": np_blood,
                        "emergency_contact": np_emg,
                        "consent_shared_treatment": 1
                    })
                    if np_complaint.strip():
                        clinical_db.add_staff_clinical_note(
                            patient_id=new_pid,
                            staff_id=curr_u.id,
                            staff_name=curr_u.name or "Healthcare Provider",
                            staff_role="Physician / Doctor" if curr_u.role == "doctor" else ("PHC Nurse / Staff" if curr_u.role == "staff" else "Attending Staff"),
                            observation_notes=f"Initial registration chief complaint: {np_complaint}",
                            triage_status="सामान्य फॉलो-अप (Follow-up Required)",
                            recommended_action="Baseline clinical checkup and routine monitoring"
                        )
                    st.success(t("patient_registered_success", lang))
                    st.rerun()
                else:
                    st.warning("कृपया मरीज का नाम दर्ज करें।" if lang != "en" else "Please enter the patient's name.")
    else:
        with st.expander(t("portal_register_patient_btn", lang), expanded=False):
            with st.form("reg_additional_patient_form"):
                st.markdown(f"#### {t('form_reg_patient_title', lang)}")
                col_ap1, col_ap2 = st.columns(2)
                with col_ap1:
                    ap_name = st.text_input(t("lbl_patient_name", lang), key="ap_name")
                    ap_age = st.number_input(t("lbl_patient_age_inp", lang), min_value=1, max_value=120, value=45, key="ap_age")
                    ap_gender = st.selectbox(t("lbl_patient_gender", lang), ["पुरुष (Male)", "महिला (Female)", "अन्य (Other)"], key="ap_gender")
                with col_ap2:
                    ap_blood = st.selectbox(t("lbl_patient_blood_group", lang), ["B+", "A+", "O+", "AB+", "B-", "A-", "O-", "AB-"], key="ap_blood")
                    ap_phone = st.text_input(t("lbl_mobile_optional", lang), key="ap_phone")
                    ap_emg = st.text_input(t("lbl_emergency_contact_inp", lang), key="ap_emg")
                ap_complaint = st.text_input(t("lbl_chief_complaint", lang), placeholder=t("ph_chief_complaint", lang), key="ap_comp")
                ap_addr = st.text_input(t("lbl_address_village", lang), placeholder=t("ph_address_village", lang), key="ap_addr")

                if st.form_submit_button(t("btn_register_patient_modal", lang), type="primary"):
                    if ap_name.strip():
                        new_pid = f"pat_{uuid.uuid4().hex[:8]}"
                        new_uid = f"user_{uuid.uuid4().hex[:8]}"
                        clinical_db.upsert_user({
                            "id": new_uid,
                            "name": ap_name,
                            "role": "patient",
                            "phone": ap_phone,
                            "age": int(ap_age),
                            "gender": ap_gender,
                            "blood_group": ap_blood,
                            "emergency_contact": ap_emg,
                            "address": ap_addr
                        })
                        clinical_db.upsert_patient({
                            "id": new_pid,
                            "user_id": new_uid,
                            "name": ap_name,
                            "age": int(ap_age),
                            "gender": ap_gender,
                            "blood_group": ap_blood,
                            "emergency_contact": ap_emg,
                            "consent_shared_treatment": 1
                        })
                        if ap_complaint.strip():
                            clinical_db.add_staff_clinical_note(
                                patient_id=new_pid,
                                staff_id=curr_u.id,
                                staff_name=curr_u.name or "Healthcare Provider",
                                staff_role="Physician / Doctor" if curr_u.role == "doctor" else ("PHC Nurse / Staff" if curr_u.role == "staff" else "Attending Staff"),
                                observation_notes=f"Initial registration chief complaint: {ap_complaint}",
                                triage_status="सामान्य फॉलो-अप (Follow-up Required)",
                                recommended_action="Baseline clinical checkup and routine monitoring"
                            )
                        st.success(t("patient_registered_success", lang))
                        st.rerun()
                    else:
                        st.warning("कृपया मरीज का नाम दर्ज करें।" if lang != "en" else "Please enter the patient's name.")

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
elif active_tab == 6 and not is_dashboard_active:
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
# HEALTHAI ASSISTANT FOOTER: Compliance, Helplines & Credits
# -------------------------------------------------------------
st.markdown(f"""
<div style="margin-top: 48px; padding: 26px 18px 20px 18px; border-top: 1px solid #e2e8f0; color: #64748b; font-size: 0.85rem; text-align: center; background: transparent;">
    <div style="margin-bottom: 12px; line-height: 1.6; font-size: 0.84rem; display: flex; justify-content: center; align-items: center; gap: 12px; flex-wrap: wrap;">
        <span style="font-weight: 700; color: #0f172a;">{t('footer_helplines', lang)}</span>
        <a href="tel:108" style="background:#fef2f2; border:1px solid #fecaca; color:#dc2626; padding:3px 10px; border-radius:980px; font-weight:700; text-decoration:none; font-size:0.8rem;">🚨 {t('footer_ambulance', lang)} (108)</a>
        <a href="tel:112" style="background:#fef2f2; border:1px solid #fecaca; color:#dc2626; padding:3px 10px; border-radius:980px; font-weight:700; text-decoration:none; font-size:0.8rem;">🛡️ {t('footer_emergency', lang)} (112)</a>
        <a href="tel:104" style="background:#eff6ff; border:1px solid #bfdbfe; color:#2563eb; padding:3px 10px; border-radius:980px; font-weight:700; text-decoration:none; font-size:0.8rem;">📞 {t('footer_health_advice', lang)} (104)</a>
        <a href="tel:14416" style="background:#fdf2f8; border:1px solid #fbcfe8; color:#db2777; padding:3px 10px; border-radius:980px; font-weight:700; text-decoration:none; font-size:0.8rem;">🌸 {t('footer_tele_manas', lang)} (14416)</a>
    </div>
    <div style="display: flex; justify-content: center; gap: 14px; flex-wrap: wrap; margin-bottom: 8px; font-size: 0.8rem; font-weight: 500; color: #94a3b8;">
        <span>🔒 ABHA & DISHA Compliant</span> • <span>⚡ Powered by Google Gemini AI</span> • <span>🏥 Ayushman Bharat Digital Mission (ABDM)</span>
    </div>
    <div style="font-size: 0.76rem; color: #94a3b8; margin-top: 4px;">
        HealthAI Assistant • सेहत साथी © 2026 • Dedicated to Accessible Rural & Urban Healthcare
    </div>
</div>
""", unsafe_allow_html=True)
