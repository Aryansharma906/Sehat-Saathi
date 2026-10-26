"""
Medicine Reference Service
Provides supporting Indian Essential Medicines data and optional RxNorm lookup.
Enforces Medical Safety Invariants (Rule 5, 6, 7).
"""

from typing import Optional, Dict, Any
import requests


# Curated dictionary of common Indian medications and generic formulations
INDIAN_MEDICINES_CATALOG: Dict[str, Dict[str, Any]] = {
    "paracetamol": {
        "generic_name": "Paracetamol (पैरासिटामोल)",
        "brand_examples": ["Dolo 650", "Calpol", "Crocin", "Pacimol"],
        "purpose_hindi": "बुखार कम करने और बदन दर्द/सिरदर्द से राहत पाने के लिए दी जाती है।",
        "standard_cautions_hindi": "एक दिन में 4 ग्राम से अधिक न लें। शराब के साथ न लें। यदि लिवर की समस्या हो तो डॉक्टर से सलाह लें।",
        "category": "Antipyretic / Analgesic (बुखार और दर्द की दवा)",
    },
    "dolo": {
        "generic_name": "Paracetamol 650mg (डोलो 650)",
        "brand_examples": ["Dolo 650", "Calpol 650"],
        "purpose_hindi": "तेज बुखार और शरीर दर्द को कम करने के लिए सामान्यतः उपयोग की जाती है।",
        "standard_cautions_hindi": "खाने के बाद लें। डॉक्टर द्वारा बताए गए अंतराल (6-8 घंटे) का पालन करें।",
        "category": "Antipyretic (बुखार निवारक)",
    },
    "amoxicillin": {
        "generic_name": "Amoxicillin (एमोक्सिसिलिन)",
        "brand_examples": ["Mox", "Novamox", "Amoxil"],
        "purpose_hindi": "जीवाणु (बैक्टीरिया) संक्रमण जैसे गले, कान या छाती के इन्फेक्शन को ठीक करने वाली एंटीबायोटिक दवा।",
        "standard_cautions_hindi": "डॉक्टर द्वारा बताया गया पूरा कोर्स पूरा करें, बीच में दवा बंद न करें।",
        "category": "Antibiotic (एंटीबायोटिक)",
    },
    "augmentin": {
        "generic_name": "Amoxicillin + Clavulanic Acid (ऑगमेंटिन)",
        "brand_examples": ["Augmentin 625", "Moxikind-CV", "Clavam 625"],
        "purpose_hindi": "गंभीर बैक्टीरिया इन्फेक्शन को रोकने वाली संयुक्त एंटीबायोटिक दवा।",
        "standard_cautions_hindi": "पेट की खराबी से बचने के लिए भोजन के साथ लें। पूरा कोर्स समाप्त करें।",
        "category": "Antibiotic (एंटीबायोटिक)",
    },
    "pantoprazole": {
        "generic_name": "Pantoprazole (पेंटोपेराज़ोल)",
        "brand_examples": ["Pan 40", "Pantocid", "Pantodac"],
        "purpose_hindi": "पेट में अत्यधिक गैस, सीने में जलन और एसिडिटी को कम करने के लिए।",
        "standard_cautions_hindi": "आमतौर पर सुबह खाली पेट (नाश्ते से 30 मिनट पहले) ली जाती है।",
        "category": "Antacid / PPI (एसिडिटी की दवा)",
    },
    "pan-d": {
        "generic_name": "Pantoprazole + Domperidone (पैन-डी)",
        "brand_examples": ["Pan-D", "Pantocid-D"],
        "purpose_hindi": "एसिडिटी के साथ मतली या उल्टी के अहसास को रोकने वाली दवा।",
        "standard_cautions_hindi": "सुबह खाली पेट ली जाती है। बिना डॉक्टर की सलाह के लगातार न लें।",
        "category": "Antacid + Antiemetic (गैस और उल्टी रोधक)",
    },
    "metformin": {
        "generic_name": "Metformin (मेटफॉर्मिन)",
        "brand_examples": ["Glycomet", "Gluconorm", "Obimet"],
        "purpose_hindi": "खून में शर्करा (शुगर/डायबिटीज) का स्तर नियंत्रित करने में मदद करती है।",
        "standard_cautions_hindi": "भोजन के साथ या भोजन के तुरंत बाद लें ताकि पेट खराब न हो।",
        "category": "Antidiabetic (शुगर नियंत्रक दवा)",
    },
    "cetirizine": {
        "generic_name": "Cetirizine (सिट्रीज़ीन)",
        "brand_examples": ["Cetzine", "Okacet", "Alerid"],
        "purpose_hindi": "एलर्जी, छींकें, नाक बहना या त्वचा में खुजली से आराम दिलाती है।",
        "standard_cautions_hindi": "इसे लेने से हल्की नींद या सुस्ती आ सकती है। गाड़ी चलाते समय सावधानी बरतें।",
        "category": "Antiallergic (एलर्जी की दवा)",
    },
    "azithromycin": {
        "generic_name": "Azithromycin (एज़िथ्रोमाइसिन)",
        "brand_examples": ["Azithral", "Azee", "Zady"],
        "purpose_hindi": "श्वसन तंत्र (गला, फेफड़े) और कान के संक्रमण के लिए एंटीबायोटिक।",
        "standard_cautions_hindi": "अक्सर दिन में एक बार ली जाती है। कोर्स अधूरा न छोड़ें।",
        "category": "Antibiotic (एंटीबायोटिक)",
    },
    "ors": {
        "generic_name": "Oral Rehydration Salts (ओआरएस)",
        "brand_examples": ["Electral", "Walyte", "Prolyte"],
        "purpose_hindi": "दस्त या उल्टी में शरीर में पानी और नमक की कमी (डिहाइड्रेशन) को पूरा करने वाला घोल।",
        "standard_cautions_hindi": "साफ पानी में सही अनुपात में घोलें। 24 घंटे के अंदर इस्तेमाल करें।",
        "category": "Rehydration / Electrolyte (इलेक्ट्रोलाइट घोल)",
    }
}


class MedicineReferenceService:
    """
    Looks up supporting reference knowledge for confirmed candidate medicines.
    Never overwrites prescription instructions (Rule 5 & 6).
    """

    @classmethod
    def lookup_medicine(cls, query_name: str) -> Optional[Dict[str, Any]]:
        """
        Looks up an Indian medicine candidate name in local curated knowledge base.
        """
        if not query_name:
            return None
        
        cleaned = query_name.strip().lower()
        
        # 1. Direct match or key in query
        for key, data in INDIAN_MEDICINES_CATALOG.items():
            if key in cleaned or cleaned in key:
                return data
            for brand in data.get("brand_examples", []):
                if brand.lower() in cleaned or cleaned in brand.lower():
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
            # Safe fallback: Network down or timeout does not block application
            pass
        return None
