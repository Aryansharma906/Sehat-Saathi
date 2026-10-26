"""
Unit Tests for Comprehensive Internationalization (i18n) & Multilingual Coverage
Verifies that all screen labels, cards, dialogs, guidance, and summaries dynamically
and accurately support Hindi ('hi'), English ('en'), and Hinglish ('hinglish').
"""

import pytest
from services.i18n import TRANSLATIONS, t
from services.language_service import SimpleHindiLanguageService
from services.complication_prediction_service import ComplicationPredictionService
from services.mental_health_service import MentalHealthService
from services.progress_tracker_service import ProgressTrackerService
from services.prevention_and_facilities import PreventionAndFacilitiesService
from models.prescription import Prescription, MedicineInstruction, ExtractionStatus
from models.complication_prediction import ComplicationPredictionInput


def test_i18n_dictionary_completeness():
    """All translation entries must define non-empty strings for 'hi', 'en', and 'hinglish'."""
    assert len(TRANSLATIONS) >= 80, "Expected at least 80 localized keys covering all screens"
    
    for key, lang_dict in TRANSLATIONS.items():
        assert "hi" in lang_dict, f"Missing 'hi' translation for key '{key}'"
        assert "en" in lang_dict, f"Missing 'en' translation for key '{key}'"
        assert "hinglish" in lang_dict, f"Missing 'hinglish' translation for key '{key}'"
        
        assert len(lang_dict["hi"].strip()) > 0, f"Empty 'hi' translation for key '{key}'"
        assert len(lang_dict["en"].strip()) > 0, f"Empty 'en' translation for key '{key}'"
        assert len(lang_dict["hinglish"].strip()) > 0, f"Empty 'hinglish' translation for key '{key}'"


def test_t_helper_fallback_and_language_selection():
    """t() returns correct language translation, falls back to 'hi', and falls back to key if unknown."""
    # 1. Standard key across 3 languages
    assert "दवा" in t("card_reminders_title", "hi")
    assert "Medicines" in t("card_reminders_title", "en")
    assert "Dawaiyan" in t("card_reminders_title", "hinglish")

    # 2. Key for emergency button
    assert "108" in t("btn_emergency_108", "en")
    assert "108" in t("btn_emergency_108", "hi")

    # 3. Fallback for unknown key
    assert t("non_existent_key_12345", "en") == "non_existent_key_12345"


def test_language_service_multilingual_explanation():
    """SimpleHindiLanguageService must produce appropriate explanations in hi, en, and hinglish."""
    svc = SimpleHindiLanguageService()
    med = MedicineInstruction(
        raw_medicine_name="Tab Paracetamol 500mg",
        candidate_medicine_name="Paracetamol",
        dose_instruction_raw="1 tablet",
        frequency_raw="Twice daily",
        timing_raw="After Food",
        is_uncertain=False
    )
    presc = Prescription(
        raw_text="Rx Paracetamol 500mg",
        extraction_status=ExtractionStatus.SUCCESS,
        medicines=[med]
    )

    # 1. Hindi
    hi_exp = svc.explain_medicine(med, lang="hi")
    assert "दवा का नाम:" in hi_exp
    hi_sum = svc.explain_prescription_summary(presc, lang="hi")
    assert "नमस्ते" in hi_sum

    # 2. English
    en_exp = svc.explain_medicine(med, lang="en")
    assert "Medicine Name:" in en_exp
    assert "Dosage:" in en_exp
    en_sum = svc.explain_prescription_summary(presc, lang="en")
    assert "Hello" in en_sum
    assert "confirmed medicines" in en_sum

    # 3. Hinglish
    hing_exp = svc.explain_medicine(med, lang="hinglish")
    assert "Dawai ka Naam:" in hing_exp
    hing_sum = svc.explain_prescription_summary(presc, lang="hinglish")
    assert "Namaste" in hing_sum
    assert "prescription me kul" in hing_sum


def test_complication_prediction_multilingual_guidance():
    """Complication prediction guidance and trajectories reflect selected language."""
    inp = ComplicationPredictionInput(
        age=60,
        systolic_bp=170.0,
        diastolic_bp=102.0,
        blood_sugar=180.0,
        spo2=96.0,
        adherence_percentage=65.0
    )

    # English guidance
    res_en = ComplicationPredictionService.predict_complication_risk(inp, lang="en")
    assert "Risk" in res_en.clinical_guidance_hindi or "Alert" in res_en.clinical_guidance_hindi
    assert "physician" in res_en.clinical_guidance_hindi.lower() or "108" in res_en.clinical_guidance_hindi

    # Hindi guidance
    res_hi = ComplicationPredictionService.predict_complication_risk(inp, lang="hi")
    assert "जोखिम" in res_hi.clinical_guidance_hindi

    # Hinglish guidance
    res_hing = ComplicationPredictionService.predict_complication_risk(inp, lang="hinglish")
    assert "Risk" in res_hing.clinical_guidance_hindi or "vitals" in res_hing.clinical_guidance_hindi

    # Trajectory in English vs Hindi
    traj_en = ComplicationPredictionService.predict_temporal_trajectory([130, 140, 155], lang="en")
    assert "Rising" in traj_en["trend_direction"]
    traj_hi = ComplicationPredictionService.predict_temporal_trajectory([130, 140, 155], lang="hi")
    assert "बढ़ रहा है" in traj_hi["trend_direction"]


def test_mental_health_multilingual():
    """Mental wellness screener returns customized compassionate advice in each language."""
    svc = MentalHealthService()
    
    # English
    res_en = svc.evaluate_mental_wellness("Good Sleep", "Normal", "Positive", lang="en")
    assert "mental wellness is excellent" in res_en.supportive_advice_hindi.lower()
    assert res_en.wellness_score >= 75

    # Hinglish
    res_hing = svc.evaluate_mental_wellness("Achhi Neend", "Samanya", "Khush", lang="hinglish")
    assert "bahut accha hai" in res_hing.supportive_advice_hindi.lower()
    assert res_hing.wellness_score >= 75

    # Hindi
    res_hi = svc.evaluate_mental_wellness("अच्छी नींद", "सामान्य", "प्रसन्न", lang="hi")
    assert "मानसिक संतुलन" in res_hi.supportive_advice_hindi
    assert res_hi.wellness_score >= 75


def test_progress_tracker_multilingual():
    """Health progress check-in returns advice according to language."""
    svc = ProgressTrackerService()

    # English
    res_en = svc.evaluate_checkin(
        "😊 बहुत आराम है (Feeling Much Better)",
        "✅ हां, सभी खुराक समय पर लीं (All Doses on Time)",
        "🟢 लक्षण लगभग खत्म हो चुके हैं (Fully Relieved)",
        lang="en"
    )
    assert "recovery progress is great" in res_en.recommendation_hindi.lower()
    assert res_en.recovery_score == 100

    # Hinglish
    res_hing = svc.evaluate_checkin(
        "😊 बहुत आराम है (Feeling Much Better)",
        "✅ हां, सभी खुराक समय पर लीं (All Doses on Time)",
        "🟢 लक्षण लगभग खत्म हो चुके हैं (Fully Relieved)",
        lang="hinglish"
    )
    assert "health progress bahut accha hai" in res_hing.recommendation_hindi.lower()

    # Hindi
    res_hi = svc.evaluate_checkin(
        "😊 बहुत आराम है (Feeling Much Better)",
        "✅ हां, सभी खुराक समय पर लीं (All Doses on Time)",
        "🟢 लक्षण लगभग खत्म हो चुके हैं (Fully Relieved)",
        lang="hi"
    )
    assert "स्वास्थ्य सुधार बहुत अच्छा है" in res_hi.recommendation_hindi


def test_prevention_topics_multilingual_display():
    """Prevention topics supply localized titles and action points for each language."""
    topics = PreventionAndFacilitiesService.get_prevention_topics()
    assert len(topics) >= 4
    
    first_topic = topics[0]
    
    # English
    t_en, s_en, pts_en = PreventionAndFacilitiesService.get_topic_display(first_topic, lang="en")
    assert "Mosquito" in t_en or "Dengue" in t_en
    assert "Prevent stagnant water" in s_en
    assert len(pts_en) >= 3

    # Hinglish
    t_hing, s_hing, pts_hing = PreventionAndFacilitiesService.get_topic_display(first_topic, lang="hinglish")
    assert "Machhar" in t_hing or "Dengue" in t_hing
    assert "Paani" in s_hing

    # Hindi
    t_hi, s_hi, pts_hi = PreventionAndFacilitiesService.get_topic_display(first_topic, lang="hi")
    assert "मच्छर" in t_hi
    assert "पानी जमा न होने दें" in s_hi
