"""
Comprehensive Indian Healthcare & Drug Database (NLEM & Jan Aushadhi Reference)
Grounds prescription extraction in official Indian healthcare standards (MoHFW / CDSCO / PMBI).
Enforces Medical Safety Invariants (Rule 5, 6, 7).
"""

from typing import Optional, Dict, Any, List
import requests


# Official Indian National List of Essential Medicines (NLEM) & Jan Aushadhi Reference Catalog
# Covers the top primary-care medicines prescribed across Indian PHCs, CHCs, and rural clinics.
INDIAN_HEALTHCARE_DRUG_DATABASE: Dict[str, Dict[str, Any]] = {
    # ---------------- Antipyretics & Analgesics (बुखार और दर्द निवारक) ----------------
    "paracetamol": {
        "generic_name": "Paracetamol (पैरासिटामोल)",
        "strengths_available": ["500 mg", "650 mg", "120 mg/5ml syrup"],
        "brand_examples": ["Dolo 650", "Calpol", "Crocin", "Pacimol", "P-650", "Pyrigesic"],
        "nlem_listed": True,
        "jan_aushadhi_available": True,
        "therapeutic_class": "Antipyretic / Analgesic (बुखार और दर्द निवारक)",
        "purpose_hindi": "बुखार उतारने और सिरदर्द, बदन दर्द से राहत दिलाने के लिए दी जाती है।",
        "standard_cautions_hindi": "दिन में 4 ग्राम (4000mg) से अधिक न लें। दो खुराकों के बीच कम से कम 6 घंटे का अंतर रखें। खाली पेट न लें यदि पेट में जलन हो।",
        "food_instruction_hindi": "भोजन या नाश्ते के बाद लें।"
    },
    "dolo": {
        "generic_name": "Paracetamol 650mg (डोलो 650 / पैरासिटामोल)",
        "strengths_available": ["650 mg"],
        "brand_examples": ["Dolo 650", "Calpol 650"],
        "nlem_listed": True,
        "jan_aushadhi_available": True,
        "therapeutic_class": "Antipyretic (बुखार निवारक)",
        "purpose_hindi": "तेज बुखार और शरीर दर्द को कम करने के लिए दी जाती है।",
        "standard_cautions_hindi": "दिन में 3 बार से अधिक बिना डॉक्टर की सलाह के न लें।",
        "food_instruction_hindi": "भोजन के बाद पानी के साथ लें।"
    },
    "ibuprofen": {
        "generic_name": "Ibuprofen (आइबुप्रोफेन)",
        "strengths_available": ["200 mg", "400 mg"],
        "brand_examples": ["Brufen", "Ibugesic"],
        "nlem_listed": True,
        "jan_aushadhi_available": True,
        "therapeutic_class": "NSAID (सूजन और दर्द निवारक)",
        "purpose_hindi": "जोड़ों के दर्द, दांत दर्द और सूजन को कम करने वाली दवा।",
        "standard_cautions_hindi": "खाली पेट बिल्कुल न लें। पेट में अल्सर या एसिडिटी होने पर सावधानी बरतें।",
        "food_instruction_hindi": "भोजन के तुरंत बाद लें।"
    },
    "combiflam": {
        "generic_name": "Ibuprofen (400mg) + Paracetamol (325mg) (कॉम्बीफ्लेम)",
        "strengths_available": ["Fixed Dose Combination"],
        "brand_examples": ["Combiflam", "Ibugesic Plus", "Flexon"],
        "nlem_listed": False,
        "jan_aushadhi_available": True,
        "therapeutic_class": "Analgesic Combination (दर्द और सूजन की संयुक्त दवा)",
        "purpose_hindi": "तेज दर्द, मोच, दांत दर्द और मांसपेशियों के खिंचाव के लिए।",
        "standard_cautions_hindi": "खाली पेट न लें। यदि पेट में जलन हो तो डॉक्टर से एंटासिड के बारे में पूछें।",
        "food_instruction_hindi": "भोजन के बाद भरपूर पानी के साथ लें।"
    },

    # ---------------- Antacids & Gastrointestinal (पेट और एसिडिटी की दवाएं) ----------------
    "pantoprazole": {
        "generic_name": "Pantoprazole (पेंटोपेराज़ोल)",
        "strengths_available": ["40 mg"],
        "brand_examples": ["Pan 40", "Pantocid", "Pantodac", "Protium"],
        "nlem_listed": True,
        "jan_aushadhi_available": True,
        "therapeutic_class": "Proton Pump Inhibitor (एसिडिटी और गैस नियंत्रक)",
        "purpose_hindi": "पेट में अत्यधिक एसिड बनना, सीने में जलन और पेट के छालों (अल्सर) से बचाव के लिए।",
        "standard_cautions_hindi": "गोली को चबाएं या तोड़ें नहीं, सीधे निगलें।",
        "food_instruction_hindi": "सुबह खाली पेट, नाश्ते से 30 से 45 मिनट पहले लें।"
    },
    "pan-d": {
        "generic_name": "Pantoprazole (40mg) + Domperidone (30mg) (पैन-डी)",
        "strengths_available": ["SR Capsule"],
        "brand_examples": ["Pan-D", "Pantocid-D", "Pantosec-D"],
        "nlem_listed": False,
        "jan_aushadhi_available": True,
        "therapeutic_class": "Antacid + Antiemetic (गैस और उल्टी/मतली रोधक)",
        "purpose_hindi": "पेट में भारी गैस के साथ उल्टी या मतली का अहसास होने पर राहत देती है।",
        "standard_cautions_hindi": "कैप्सूल को साबुत निगलें। बिना डॉक्टर की सलाह के लंबे समय तक न लें।",
        "food_instruction_hindi": "सुबह उठकर खाली पेट, नाश्ते से आधा घंटा पहले।"
    },
    "omeprazole": {
        "generic_name": "Omeprazole (ओमेप्राज़ोल)",
        "strengths_available": ["20 mg"],
        "brand_examples": ["Omez", "Ocid", "Omee"],
        "nlem_listed": True,
        "jan_aushadhi_available": True,
        "therapeutic_class": "Antacid (एसिडिटी निवारक)",
        "purpose_hindi": "पेट में जलन, खट्टी डकार और गैस से राहत दिलाने के लिए।",
        "standard_cautions_hindi": "पानी के साथ साबुत लें।",
        "food_instruction_hindi": "सुबह नाश्ते से पहले खाली पेट।"
    },
    "ranitidine": {
        "generic_name": "Ranitidine / Famotidine (एसिडिटी टैबलेट)",
        "strengths_available": ["150 mg", "20 mg"],
        "brand_examples": ["Rantac", "Aciloc", "Famocid"],
        "nlem_listed": True,
        "jan_aushadhi_available": True,
        "therapeutic_class": "H2 Blocker (पेट में गैस कम करने वाली दवा)",
        "purpose_hindi": "पेट में जलन और भोजन न पचने की समस्या को कम करती है।",
        "standard_cautions_hindi": "डॉक्टर द्वारा बताए गए समय पर लें।",
        "food_instruction_hindi": "खाने से पहले या डॉक्टर के निर्देशानुसार।"
    },

    # ---------------- Antibiotics (एंटीबायोटिक दवाएं) ----------------
    "amoxicillin": {
        "generic_name": "Amoxicillin (एमोक्सिसिलिन)",
        "strengths_available": ["250 mg", "500 mg", "125 mg/5ml syrup"],
        "brand_examples": ["Novamox", "Mox", "Amoxil"],
        "nlem_listed": True,
        "jan_aushadhi_available": True,
        "therapeutic_class": "Broad Spectrum Penicillin Antibiotic",
        "purpose_hindi": "गले, कान, छाती या दांतों में बैक्टीरिया के इन्फेक्शन को खत्म करने वाली दवा।",
        "standard_cautions_hindi": "⚠️ डॉक्टर द्वारा बताया गया पूरा कोर्स (जैसे 5 दिन) पूरा करें, भले ही आप पहले ही ठीक महसूस करने लगें।",
        "food_instruction_hindi": "भोजन के साथ या बाद में लें।"
    },
    "augmentin": {
        "generic_name": "Amoxicillin + Clavulanic Acid (ऑगमेंटिन / मोक्सीकाइंड-सीवी)",
        "strengths_available": ["625 mg", "375 mg", "1000 mg"],
        "brand_examples": ["Augmentin 625", "Moxikind-CV 625", "Clavam 625", "Sensiclav"],
        "nlem_listed": True,
        "jan_aushadhi_available": True,
        "therapeutic_class": "Beta-lactamase Inhibitor Antibiotic",
        "purpose_hindi": "गंभीर बैक्टीरिया इन्फेक्शन (फेफड़े, त्वचा, मूत्र मार्ग या घाव) को ठीक करने वाली शक्तिशाली दवा।",
        "standard_cautions_hindi": "⚠️ पेट की खराबी से बचने के लिए भोजन के साथ लें। बीच में दवा न छोड़ें।",
        "food_instruction_hindi": "भोजन के बीच में या तुरंत बाद लें।"
    },
    "azithromycin": {
        "generic_name": "Azithromycin (एज़िथ्रोमाइसिन)",
        "strengths_available": ["250 mg", "500 mg"],
        "brand_examples": ["Azithral", "Azee", "Zady", "Azax"],
        "nlem_listed": True,
        "jan_aushadhi_available": True,
        "therapeutic_class": "Macrolide Antibiotic",
        "purpose_hindi": "गले में खराश, टॉन्सिल, खांसी और फेफड़ों के संक्रमण के लिए।",
        "standard_cautions_hindi": "आमतौर पर दिन में केवल एक बार निर्धारित समय पर ली जाती है। 3 से 5 दिन का कोर्स पूरा करें।",
        "food_instruction_hindi": "भोजन से 1 घंटा पहले या भोजन के 2 घंटे बाद।"
    },
    "ciprofloxacin": {
        "generic_name": "Ciprofloxacin (सिप्रोफ्लोक्सासिन)",
        "strengths_available": ["250 mg", "500 mg"],
        "brand_examples": ["Ciplox", "Cifran", "Ciprobid"],
        "nlem_listed": True,
        "jan_aushadhi_available": True,
        "therapeutic_class": "Fluoroquinolone Antibiotic",
        "purpose_hindi": "पेट के इन्फेक्शन (दस्त/पेचिश) और यूरिन इन्फेक्शन के लिए।",
        "standard_cautions_hindi": "दवा लेते समय खूब सारा पानी पिएं। दूध या दही के साथ तुरंत न लें।",
        "food_instruction_hindi": "भोजन के 2 घंटे बाद।"
    },

    # ---------------- Antiallergic & Respiratory (एलर्जी और खांसी की दवाएं) ----------------
    "cetirizine": {
        "generic_name": "Cetirizine (सिट्रीज़ीन)",
        "strengths_available": ["10 mg", "5 mg/5ml"],
        "brand_examples": ["Cetzine", "Okacet", "Alerid", "Zyrtec"],
        "nlem_listed": True,
        "jan_aushadhi_available": True,
        "therapeutic_class": "Antihistamine (एंटी-एलर्जिक)",
        "purpose_hindi": "छींकें, बहती नाक, आंखों में खुजली और त्वचा की एलर्जी से आराम दिलाने के लिए।",
        "standard_cautions_hindi": "इसे लेने से नींद या सुस्ती आ सकती है। गाड़ी चलाते समय या भारी काम करते समय सावधानी रखें।",
        "food_instruction_hindi": "रात को सोते समय लेना सबसे बेहतर होता है।"
    },
    "levocetirizine": {
        "generic_name": "Levocetirizine (लेवोसिट्रीज़ीन)",
        "strengths_available": ["5 mg"],
        "brand_examples": ["Levocet", "Teczine", "1-AL"],
        "nlem_listed": True,
        "jan_aushadhi_available": True,
        "therapeutic_class": "Second-generation Antihistamine",
        "purpose_hindi": "एलर्जी, पराग कणों से छींकें और त्वचा पर पित्ती (hives) के इलाज के लिए।",
        "standard_cautions_hindi": "शाम या रात के समय लें।",
        "food_instruction_hindi": "भोजन के साथ या बिना भोजन।"
    },
    "montelukast": {
        "generic_name": "Montelukast + Levocetirizine (मोंटेलुकास्ट संयुक्त)",
        "strengths_available": ["10mg / 5mg"],
        "brand_examples": ["Montair-LC", "Montek-LC", "Telekast-L"],
        "nlem_listed": False,
        "jan_aushadhi_available": True,
        "therapeutic_class": "Antiallergic & Bronchodilator",
        "purpose_hindi": "एलर्जी वाली खांसी, सांस लेने में हल्की रुकावट और रात की छींकों के लिए।",
        "standard_cautions_hindi": "रात को सोते समय लें।",
        "food_instruction_hindi": "रात के भोजन के बाद।"
    },

    # ---------------- Chronic Conditions (डायबिटीज, बीपी और हृदय) ----------------
    "metformin": {
        "generic_name": "Metformin (मेटफॉर्मिन)",
        "strengths_available": ["500 mg", "850 mg", "1000 mg", "SR 500mg"],
        "brand_examples": ["Glycomet", "Gluconorm", "Obimet", "Cetapin"],
        "nlem_listed": True,
        "jan_aushadhi_available": True,
        "therapeutic_class": "Biguanide Antidiabetic (शुगर नियंत्रक)",
        "purpose_hindi": "टाइप 2 डायबिटीज (शुगर) के मरीजों में रक्त शर्करा का स्तर सामान्य रखने के लिए।",
        "standard_cautions_hindi": "खाली पेट न लें ताकि पेट में गैस या दर्द न हो। दवा का समय नियमित रखें।",
        "food_instruction_hindi": "भोजन के साथ या भोजन के तुरंत बाद लें।"
    },
    "amlodipine": {
        "generic_name": "Amlodipine (एम्लोडिपिन)",
        "strengths_available": ["2.5 mg", "5 mg", "10 mg"],
        "brand_examples": ["Amlong", "Amlip", "Stamlo"],
        "nlem_listed": True,
        "jan_aushadhi_available": True,
        "therapeutic_class": "Calcium Channel Blocker (रक्तचाप / बीपी नियंत्रक)",
        "purpose_hindi": "हाई ब्लड प्रेशर (उच्च रक्तचाप) को नियंत्रित करने और दिल की सुरक्षा के लिए।",
        "standard_cautions_hindi": "रोजाना एक ही समय पर लें। बिना डॉक्टर से पूछे अचानक दवा बंद न करें।",
        "food_instruction_hindi": "सुबह नाश्ते के बाद या डॉक्टर के निर्देशानुसार।"
    },
    "telmisartan": {
        "generic_name": "Telmisartan (टेल्मिसार्टन)",
        "strengths_available": ["20 mg", "40 mg", "80 mg"],
        "brand_examples": ["Telma", "Telmikind", "Telsartan"],
        "nlem_listed": True,
        "jan_aushadhi_available": True,
        "therapeutic_class": "ARB (उच्च रक्तचाप की दवा)",
        "purpose_hindi": "हाई ब्लड प्रेशर को कम रखने और गुर्दे व दिल की सुरक्षा के लिए।",
        "standard_cautions_hindi": "नियमित रूप से रक्तचाप नापते रहें।",
        "food_instruction_hindi": "रोजाना सुबह निश्चित समय पर।"
    },

    # ---------------- Rehydration & Essential Minerals (ओआरएस और खनिज) ----------------
    "ors": {
        "generic_name": "Oral Rehydration Salts (ओआरएस / इलेक्ट्रोलाइट घोल)",
        "strengths_available": ["WHO Formula Sachet (21.8g)"],
        "brand_examples": ["Electral", "Walyte", "Prolyte", "Jan Aushadhi ORS"],
        "nlem_listed": True,
        "jan_aushadhi_available": True,
        "therapeutic_class": "Oral Rehydration Solution (जीवन रक्षक घोल)",
        "purpose_hindi": "दस्त, उल्टी या तेज धूप से शरीर में पानी और नमक की कमी (डिहाइड्रेशन) को पूरा करने के लिए।",
        "standard_cautions_hindi": "1 पैकेट को पूरे 1 लीटर साफ पीने के पानी में अच्छी तरह घोलें। 24 घंटे के बाद बचा हुआ घोल फेंक दें।",
        "food_instruction_hindi": "दिनभर में घूंट-घूंट करके पिएं।"
    },
    "zinc": {
        "generic_name": "Zinc Sulphate (जिंक सल्फेट)",
        "strengths_available": ["20 mg tablet", "20 mg/5ml syrup"],
        "brand_examples": ["Zinconia", "Zinconorm"],
        "nlem_listed": True,
        "jan_aushadhi_available": True,
        "therapeutic_class": "Essential Trace Mineral",
        "purpose_hindi": "बच्चों में दस्त की तीव्रता कम करने और आंतों की ताकत बढ़ाने के लिए।",
        "standard_cautions_hindi": "दस्त रुकने के बाद भी 14 दिन तक देना जारी रखें।",
        "food_instruction_hindi": "मां के दूध या पानी के साथ घोलकर।"
    }
}


class MedicineReferenceService:
    """
    Looks up supporting reference knowledge from official Indian Healthcare standards
    (NLEM & Jan Aushadhi generic catalog) and secondary RxNorm mappings.
    Never alters doctor prescription instructions (Rule 5 & 6).
    """

    @classmethod
    def lookup_medicine(cls, query_name: str) -> Optional[Dict[str, Any]]:
        """
        Looks up an Indian medicine brand or generic name in the Indian Healthcare Database.
        """
        if not query_name:
            return None
        
        cleaned = query_name.strip().lower()
        
        # 1. Exact or partial key match
        for key, data in INDIAN_HEALTHCARE_DRUG_DATABASE.items():
            if key == cleaned or key in cleaned or cleaned in key:
                return data
            for brand in data.get("brand_examples", []):
                brand_clean = brand.lower()
                if brand_clean in cleaned or cleaned in brand_clean:
                    return data
                    
        return None

    @classmethod
    def query_rxnorm_rxcui(cls, drug_name: str, timeout_sec: int = 3) -> Optional[str]:
        """
        Optional secondary query to NLM RxNorm for RxCUI identifier.
        Fails safely if offline or timeout. Does not crash app.
        """
        try:
            url = f"https://rxnav.nlm.nih.gov/REST/rxcui.json?name={requests.utils.quote(drug_name)}"
            resp = requests.get(url, timeout=timeout_sec)
            if resp.status_code == 200:
                data = resp.json()
                id_group = data.get("idGroup", {})
                rxnorm_ids = id_group.get("rxnormId", [])
                if rxnorm_ids:
                    return rxnorm_ids[0]
        except Exception:
            pass
        return None

    @classmethod
    def get_essential_medicines_summary(cls) -> List[Dict[str, str]]:
        """
        Returns a simplified list of essential medicines for educational reference.
        """
        summary = []
        for key, data in INDIAN_HEALTHCARE_DRUG_DATABASE.items():
            summary.append({
                "generic": data["generic_name"],
                "purpose": data["purpose_hindi"],
                "class": data["therapeutic_class"]
            })
        return summary
