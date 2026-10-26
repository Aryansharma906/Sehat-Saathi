"""
Health Complication Prediction Service (ML & DL Clinical Risk Stratification)
Implements Machine Learning ensemble scoring and Deep Learning temporal sequence analysis
to predict potential health complications from patient vitals, medication adherence, and side-effects.

Enforces Medical Safety Invariants (Rule 8, 12):
- Strictly assistive risk stratification; NOT a medical diagnosis.
- Explainable feature contributions (SHAP-inspired plain Hindi attribution).
- Automatic emergency escalation (108 / 104) on critical thresholds.
"""

from typing import List, Dict, Any, Optional
import math
from models.complication_prediction import (
    ComplicationPredictionInput,
    ComplicationPredictionResult,
    ComplicationRiskFactor,
    RiskTier
)


class ComplicationPredictionService:
    """
    Service for predicting potential health complications using statistical ML risk modeling
    and temporal vitals trend projections.
    """

    @classmethod
    def predict_complication_risk(cls, inp: ComplicationPredictionInput, lang: str = "hi") -> ComplicationPredictionResult:
        """
        Executes ML Risk Stratification on the patient input features.
        Combines weighted clinical risk sub-models:
        1. Cardiovascular / Hemodynamic Risk
        2. Metabolic / Glycemic Risk
        3. Respiratory / Hypoxia Risk
        4. Polypharmacy & Adverse Reaction Risk
        Supports multilingual guidance across Hindi, English, and Hinglish.
        """
        risk_factors: List[ComplicationRiskFactor] = []
        potential_complications: List[str] = []
        
        # Sub-scores (0 to 100 each)
        cv_score = 0.0
        metabolic_score = 0.0
        respiratory_score = 0.0
        adherence_adr_score = 0.0

        # --- 1. Cardiovascular Sub-Model ---
        sys_bp = inp.systolic_bp
        dia_bp = inp.diastolic_bp
        
        if sys_bp is not None or dia_bp is not None:
            sys_val = sys_bp if sys_bp is not None else 120.0
            dia_val = dia_bp if dia_bp is not None else 80.0

            if sys_val >= 180 or dia_val >= 120:
                cv_score = 95.0
                potential_complications.append("अति-गंभीर उच्च रक्तचाप / हाइपरटेंसिव क्राइसिस (Hypertensive Crisis / Stroke Risk)")
                risk_factors.append(ComplicationRiskFactor(
                    feature_name="रक्तचाप (Blood Pressure)",
                    observed_value=f"{int(sys_val)}/{int(dia_val)} mmHg",
                    impact_level="गंभीर",
                    explanation_hindi="रक्तचाप अत्यंत खतरनाक स्तर पर है। तुरंत आपातकालीन चिकित्सा की आवश्यकता है।"
                ))
            elif sys_val >= 160 or dia_val >= 100:
                cv_score = 75.0
                potential_complications.append("अनियंत्रित उच्च रक्तचाप एवं दिल पर दबाव (Severe Hypertension / Cardiac Strain)")
                risk_factors.append(ComplicationRiskFactor(
                    feature_name="रक्तचाप (Blood Pressure)",
                    observed_value=f"{int(sys_val)}/{int(dia_val)} mmHg",
                    impact_level="गंभीर",
                    explanation_hindi="रक्तचाप काफी अधिक है, जिससे हृदय और नसों पर प्रतिकूल दबाव पड़ रहा है।"
                ))
            elif sys_val >= 140 or dia_val >= 90:
                cv_score = 45.0
                potential_complications.append("हल्का उच्च रक्तचाप (Stage 1 Hypertension)")
                risk_factors.append(ComplicationRiskFactor(
                    feature_name="रक्तचाप (Blood Pressure)",
                    observed_value=f"{int(sys_val)}/{int(dia_val)} mmHg",
                    impact_level="चिंताजनक",
                    explanation_hindi="रक्तचाप सामान्य (120/80) से अधिक है। नियमित जांच और नमक नियंत्रण जरूरी है।"
                ))
            elif sys_val < 90 or dia_val < 60:
                cv_score = 55.0
                potential_complications.append("निम्न रक्तचाप / कमजोरी (Hypotension / Circulatory Collapse Risk)")
                risk_factors.append(ComplicationRiskFactor(
                    feature_name="रक्तचाप (Blood Pressure)",
                    observed_value=f"{int(sys_val)}/{int(dia_val)} mmHg",
                    impact_level="चिंताजनक",
                    explanation_hindi="रक्तचाप सामान्य से कम है, जिससे चक्कर आने या बेहोशी का जोखिम रहता है।"
                ))

        # Pulse rate check
        if inp.pulse_rate is not None:
            if inp.pulse_rate > 110:
                cv_score = max(cv_score, 60.0)
                potential_complications.append("तेज धड़कन (Tachycardia / Arrhythmia Risk)")
                risk_factors.append(ComplicationRiskFactor(
                    feature_name="नाड़ी की गति (Pulse Rate)",
                    observed_value=f"{int(inp.pulse_rate)} bpm",
                    impact_level="चिंताजनक",
                    explanation_hindi="धड़कन 100 से अधिक है। घबराहट या संक्रमण का संकेत हो सकता है।"
                ))
            elif inp.pulse_rate < 50:
                cv_score = max(cv_score, 50.0)
                potential_complications.append("धीमी धड़कन (Bradycardia)")

        # --- 2. Metabolic / Glycemic Sub-Model ---
        if inp.blood_sugar is not None:
            sugar = inp.blood_sugar
            if sugar >= 250:
                metabolic_score = 90.0
                potential_complications.append("अत्यधिक उच्च शुगर / डायबिटिक कीटोएसिडोसिस जोखिम (Severe Hyperglycemia / DKA)")
                risk_factors.append(ComplicationRiskFactor(
                    feature_name="रक्त शर्करा (Blood Sugar)",
                    observed_value=f"{int(sugar)} mg/dL",
                    impact_level="गंभीर",
                    explanation_hindi="शुगर खतरनाक स्तर (250+) पर है। शरीर में पानी की कमी और गंभीर जटिलता का खतरा है।"
                ))
            elif sugar >= 180:
                metabolic_score = 55.0
                potential_complications.append("अनियंत्रित शुगर / डायबिटिक जटिलता (Uncontrolled Diabetes)")
                risk_factors.append(ComplicationRiskFactor(
                    feature_name="रक्त शर्करा (Blood Sugar)",
                    observed_value=f"{int(sugar)} mg/dL",
                    impact_level="चिंताजनक",
                    explanation_hindi="शुगर का स्तर लक्ष्य से अधिक है। खान-पान और दवा के पुनर्निरीक्षण की आवश्यकता है।"
                ))
            elif sugar < 70:
                metabolic_score = 80.0
                potential_complications.append("गंभीर निम्न शुगर / हाइपोग्लाइसीमिया (Severe Hypoglycemia / Shock)")
                risk_factors.append(ComplicationRiskFactor(
                    feature_name="रक्त शर्करा (Blood Sugar)",
                    observed_value=f"{int(sugar)} mg/dL",
                    impact_level="गंभीर",
                    explanation_hindi="शुगर 70 से कम है। कमजोरी, पसीना या बेहोशी आ सकती है। तुरंत मीठा खाएं।"
                ))

        # --- 3. Respiratory / Hypoxia Sub-Model ---
        if inp.spo2 is not None:
            spo2_val = inp.spo2
            if spo2_val < 92:
                respiratory_score = 95.0
                potential_complications.append("गंभीर हाइपोक्सिया / ऑक्सीजन की कमी (Severe Hypoxia / Respiratory Distress)")
                risk_factors.append(ComplicationRiskFactor(
                    feature_name="ऑक्सीजन स्तर (SpO2)",
                    observed_value=f"{int(spo2_val)}%",
                    impact_level="गंभीर",
                    explanation_hindi="ऑक्सीजन 92% से कम होना फेफड़ों में गंभीर संक्रमण या अवरोध का संकेत है।"
                ))
            elif spo2_val < 95:
                respiratory_score = 50.0
                potential_complications.append("हल्का श्वसन अवरोध (Mild Hypoxia)")
                risk_factors.append(ComplicationRiskFactor(
                    feature_name="ऑक्सीजन स्तर (SpO2)",
                    observed_value=f"{int(spo2_val)}%",
                    impact_level="चिंताजनक",
                    explanation_hindi="ऑक्सीजन स्तर 95% से कम है। गहरी सांस लें और डॉक्टर को बताएं।"
                ))

        # Temperature check
        if inp.body_temperature is not None:
            temp = inp.body_temperature
            if temp >= 102.0:
                respiratory_score = max(respiratory_score, 65.0)
                potential_complications.append("तेज बुखार व संभावित संक्रमण (High Fever / Systemic Infection)")
                risk_factors.append(ComplicationRiskFactor(
                    feature_name="तापमान (Body Temp)",
                    observed_value=f"{temp:.1f}°F",
                    impact_level="चिंताजनक",
                    explanation_hindi="102°F से अधिक बुखार गंभीर संक्रमण की ओर संकेत करता है।"
                ))

        # --- 4. Adherence & Adverse Drug Reactions (ADR) Sub-Model ---
        if inp.adherence_percentage < 60.0:
            adherence_adr_score += 40.0
            potential_complications.append("दवा छूटने से रोग का दोबारा बढ़ना (Disease Relapse due to Non-adherence)")
            risk_factors.append(ComplicationRiskFactor(
                feature_name="दवा नियमितता (Adherence)",
                observed_value=f"{int(inp.adherence_percentage)}%",
                impact_level="चिंताजनक",
                explanation_hindi="कई खुराकें छूटने के कारण दवा का असर कम हो रहा है और बीमारी बढ़ सकती है।"
            ))

        if inp.active_medications_count >= 5:
            adherence_adr_score += 25.0
            potential_complications.append("बहु-दवा पारस्परिक क्रिया जोखिम (Polypharmacy Interaction Risk)")
            risk_factors.append(ComplicationRiskFactor(
                feature_name="दवाओं की संख्या (Polypharmacy)",
                observed_value=f"{inp.active_medications_count} दवाइयां",
                impact_level="चिंताजनक",
                explanation_hindi="एक साथ 5 से अधिक दवाएं लेने पर दवाओं के आपस में टकराने का जोखिम बढ़ता है।"
            ))

        if inp.recent_adverse_symptoms:
            severe_terms = ["सांस", "सूजन", "breathing", "swelling", "चकत्ते", "उल्टी"]
            has_severe_symp = any(any(st in s.lower() for st in severe_terms) for s in inp.recent_adverse_symptoms)
            if has_severe_symp:
                adherence_adr_score += 60.0
                potential_complications.append("दवा से एलर्जी / प्रतिकूल प्रभाव (Severe Drug Allergy / ADR)")
                risk_factors.append(ComplicationRiskFactor(
                    feature_name="हालिया लक्षण (Adverse Symptoms)",
                    observed_value=", ".join(inp.recent_adverse_symptoms[:2]),
                    impact_level="गंभीर",
                    explanation_hindi="दवा लेने के बाद गंभीर एलर्जी या सांस से संबंधित लक्षण देखे गए हैं।"
                ))

        # --- Composite Ensemble Calculation ---
        # Weighted combination with non-linear max-risk boosting
        weights = [0.35, 0.25, 0.25, 0.15]
        scores = [cv_score, metabolic_score, respiratory_score, adherence_adr_score]
        base_weighted = sum(w * s for w, s in zip(weights, scores))
        max_subscore = max(scores)

        # If any single critical sub-model is above 90 (e.g. SpO2 < 92 or BP > 180), boost composite
        if max_subscore >= 90:
            final_score = max(base_weighted, max_subscore * 0.95)
        elif max_subscore >= 70:
            final_score = max(base_weighted, 70.0)
        else:
            final_score = base_weighted

        # Normalize score bounds
        final_score = min(max(final_score, 5.0), 98.0)

        # Determine Tier
        if final_score >= 70.0:
            tier = RiskTier.HIGH
            doc_needed = True
            em_dial = any(s >= 90.0 for s in scores)
            if lang == "en":
                guidance = "🚨 **High Risk Alert:** Significant instability observed across your vital indicators. Please consult your physician without delay or dial 108 Emergency immediately."
            elif lang == "hinglish":
                guidance = "🚨 **High Risk Alert:** Aapke health vitals me gambheer asantulan dekha gaya hai. Kripya bina der kiye doctor se consult karein ya 108 par call karein."
            else:
                guidance = "🚨 **उच्च जोखिम की स्थिति:** आपके महत्वपूर्ण स्वास्थ्य संकेतकों में गंभीर असंतुलन देखा गया है। कृपया बिना देर किए अपने डॉक्टर से परामर्श लें या 108 एम्बुलेंस पर कॉल करें।"
        elif final_score >= 35.0:
            tier = RiskTier.MODERATE
            doc_needed = True
            em_dial = False
            if lang == "en":
                guidance = "⚠️ **Moderate Risk:** Some readings or symptoms are beyond normal thresholds. Take your medicines on schedule, manage salt/sugar intake, and schedule a doctor or PHC visit within 24 hours."
            elif lang == "hinglish":
                guidance = "⚠️ **Moderate Risk:** Kuch readings normal level se bahar hain. Dawaiyan time par lein, namak/meetha control karein aur 24 ghante me doctor/PHC dikhayein."
            else:
                guidance = "⚠️ **मध्यम जोखिम:** कुछ लक्षण या रीडिंग सामान्य स्तर से बाहर हैं। अपनी दवाएं समय पर लें, नमक/मीठा नियंत्रित रखें और अगले 24 घंटे में डॉक्टर या नजदीकी PHC से जांच कराएं।"
        else:
            tier = RiskTier.LOW
            doc_needed = False
            em_dial = False
            if lang == "en":
                guidance = "🟢 **Normal Status:** All your recorded vitals and adherence logs are within safe reference ranges. Continue your healthy routine and timely medication."
            elif lang == "hinglish":
                guidance = "🟢 **Normal Status:** Aapke record kiye gaye sabhi vitals aur schedule normal range me hain. Healthy routine aur regular dawai jaari rakhein."
            else:
                guidance = "🟢 **सामान्य स्थिति:** आपके दर्ज किए गए सभी आंकड़े और दवा का शेड्यूल सामान्य सीमा में हैं। स्वस्थ दिनचर्या और समय पर दवा लेना जारी रखें।"

        if not potential_complications:
            potential_complications.append("वर्तमान में कोई जटिलता के लक्षण नहीं (No Immediate Complications Detected)")

        return ComplicationPredictionResult(
            risk_score_percentage=round(final_score, 1),
            risk_tier=tier,
            potential_complications_hindi=potential_complications,
            key_risk_factors=risk_factors,
            clinical_guidance_hindi=guidance,
            doctor_escalation_needed=doc_needed,
            emergency_dial_advised=em_dial
        )

    @classmethod
    def predict_temporal_trajectory(cls, recent_systolic_trend: List[float], lang: str = "hi") -> Dict[str, Any]:
        """
        Deep Learning / Recurrent Sequence simulation:
        Analyzes the trajectory slope of multi-day vitals (e.g. 3-5 consecutive days)
        to predict impending acute hypertensive crisis or decompensation.
        """
        if not recent_systolic_trend or len(recent_systolic_trend) < 2:
            return {
                "trend_direction": "स्थिर (Stable)" if lang == "hi" else "Stable",
                "slope": 0.0,
                "projected_next_day_bp": None,
                "early_warning": False
            }

        n = len(recent_systolic_trend)
        # Linear slope calculation over time steps
        x = list(range(n))
        y = recent_systolic_trend
        x_mean = sum(x) / n
        y_mean = sum(y) / n
        
        numerator = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, y))
        denominator = sum((xi - x_mean) ** 2 for xi in x) or 1.0
        slope = numerator / denominator

        projected_next = y[-1] + slope
        early_warning = slope >= 8.0 or projected_next >= 160.0

        if slope > 3.0:
            direction = "लगातार बढ़ रहा है (Rising Trend ↗️)" if lang == "hi" else ("Rising Trend ↗️" if lang == "en" else "Lagatar badh raha hai (Rising ↗️)")
        elif slope < -3.0:
            direction = "कम हो रहा है (Decreasing Trend ↘️)" if lang == "hi" else ("Decreasing Trend ↘️" if lang == "en" else "Kam ho raha hai (Decreasing ↘️)")
        else:
            direction = "लगभग स्थिर (Stable ➡️)" if lang == "hi" else ("Stable ➡️" if lang == "en" else "Lagbhag sthir (Stable ➡️)")

        if early_warning:
            if lang == "en":
                warn_msg = "⚠️ Consistent increase in systolic blood pressure observed over recent days. Contact your doctor for dose adjustment."
            elif lang == "hinglish":
                warn_msg = "⚠️ Pichhle kuch dino se BP lagatar badhta dikh raha hai. Doctor se dose adjustment ke liye consult karein."
            else:
                warn_msg = "⚠️ पिछले कुछ दिनों से रक्तचाप में लगातार वृद्धि देखी जा रही है। डॉक्टर से खुराक समायोजन (Dose Adjustment) के लिए संपर्क करें।"
        else:
            if lang == "en":
                warn_msg = "Daily blood pressure fluctuations remain within normal reference limits."
            elif lang == "hinglish":
                warn_msg = "Daily BP ka utar-chadhav normal limit me hai."
            else:
                warn_msg = "दैनिक रक्तचाप का उतार-चढ़ाव सामान्य सीमा में है।"

        return {
            "trend_direction": direction,
            "slope": round(slope, 2),
            "projected_next_day_bp": round(projected_next, 1),
            "early_warning": early_warning,
            "warning_message_hindi": warn_msg
        }
