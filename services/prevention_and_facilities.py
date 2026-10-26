"""
Environmental Health, Disease Prevention, and Nearby Facility Locator Service
Provides MoHFW/NHM-aligned community disease prevention tips and navigation links for rural facilities.
Enforces Medical Safety Invariants (Rule 8: Educational prevention only, no diagnosis).
"""

from typing import List, Dict, Any, Optional
import urllib.parse


# National Health Mission (NHM) & MoHFW aligned rural health & environmental prevention guides
PREVENTION_TOPICS: List[Dict[str, Any]] = [
    {
        "id": "mosquito",
        "icon": "🦟",
        "title_hindi": "मच्छर जनित रोग (डेंगू, मलेरिया, चिकनगुनिया)",
        "subtitle": "पानी जमा न होने दें, मच्छरों से बचाव रखें",
        "action_points": [
            "घर के आसपास, कूलर, पुराने टायर या बर्तनों में 3 दिन से अधिक रुका हुआ पानी न रहने दें।",
            "सोते समय मच्छरदानी (Mosquito Net) का प्रयोग करें, विशेषकर बच्चों और बुजुर्गों के लिए।",
            "सुबह और शाम के समय पूरी बांह के कपड़े पहनें।",
            "यदि 2 दिन से अधिक तेज बुखार, ठंड लगना या आंखों के पीछे दर्द हो, तो तुरंत नजदीकी स्वास्थ्य केंद्र (PHC) में खून की जांच कराएं।"
        ]
    },
    {
        "id": "waterborne",
        "icon": "💧",
        "title_hindi": "दूषित पानी और पेट के रोग (दस्त, टाइफाइड, हैजा, पीलिया)",
        "subtitle": "स्वच्छ उबला पानी पिएं, डिहाइड्रेशन से बचें",
        "action_points": [
            "पीने का पानी हमेशा उबालकर या साफ कपड़े/फिल्टर से छानकर पिएं।",
            "दस्त या उल्टी होने पर तुरंत ओआरएस (ORS) घोल या नमक-चीनी-नींबू पानी शुरू करें ताकि शरीर में पानी की कमी न हो।",
            "बासी या खुला रखा हुआ भोजन न खाएं, हमेशा ताजा और ढका हुआ खाना खाएं।",
            "पानी के मटके या बर्तन को हमेशा ढककर रखें और निकालने के लिए डंडी वाले लोटे का इस्तेमाल करें।"
        ]
    },
    {
        "id": "respiratory_clean_air",
        "icon": "🌬️",
        "title_hindi": "धुआं और फेफड़ों की सुरक्षा (खांसी, दमा, सांस की तकलीफ)",
        "subtitle": "चूल्हे के धुएं से बचाव और हवादार रसोई",
        "action_points": [
            "रसोई में चूल्हा जलाते समय खिड़की खुली रखें ताकि धुआं आसानी से बाहर निकल सके।",
            "घर के अंदर बीड़ी, सिगरेट या तंबाकू का सेवन बिल्कुल न करें; इसका धुआं बच्चों और बुजुर्गों के फेफड़ों को नुकसान पहुंचाता है।",
            "खेतों में पराली या सूखा कचरा जलाने वाले धुएं से बुजुर्गों को दूर रखें।",
            "लगातार 2 हफ्ते से अधिक खांसी या बलगम होने पर टीबी (TB) की मुफ्त जांच के लिए सरकारी स्वास्थ्य केंद्र जाएं।"
        ]
    },
    {
        "id": "hygiene",
        "icon": "🧼",
        "title_hindi": "व्यक्तिगत स्वच्छता (हाथ धोना और संक्रमण से बचाव)",
        "subtitle": "बीमारियों को फैलने से रोकने का सबसे सरल उपाय",
        "action_points": [
            "शौच के बाद और भोजन करने या पकाने से पहले हमेशा साबुन और साफ पानी से कम से कम 20 सेकंड तक हाथ धोएं।",
            "बच्चों के नाखून छोटे और साफ रखें।",
            "घाव या खरोंच लगने पर उस पर गोबर या मिट्टी न लगाएं; साफ पानी से धोकर पट्टी बांधें और टिटनेस का टीका लगवाएं।"
        ]
    }
]


# Default representative Primary Health Centre / Community Health Centre coordinates
# Used for in-app map rendering and testing.
SAMPLE_HEALTH_FACILITIES: List[Dict[str, Any]] = [
    {
        "name": "प्राथमिक स्वास्थ्य केंद्र (Primary Health Centre - PHC)",
        "type": "सरकारी अस्पताल (Govt Health Centre)",
        "services": "मुफ्त परामर्श, जरूरी दवाएं, मलेरिया/खून जांच, टीकाकरण",
        "timing": "सुबह 8:00 से दोपहर 2:00 बजे",
        "latitude": 26.9124,
        "longitude": 75.7873
    },
    {
        "name": "सामुदायिक स्वास्थ्य केंद्र (Community Health Centre - CHC)",
        "type": "बड़ा सरकारी अस्पताल (Sub-district Hospital)",
        "services": "24 घंटे इमरजेंसी, प्रसव सुविधा, डॉक्टर और विशेषज्ञ",
        "timing": "24 घंटे उपलब्ध (Emergency 24x7)",
        "latitude": 26.9220,
        "longitude": 75.8010
    },
    {
        "name": "प्रधानमंत्री जन औषधि केंद्र (Pradhan Mantri Jan Aushadhi Kendra)",
        "type": "सस्ती जेनेरिक दवा की दुकान (Affordable Generic Pharmacy)",
        "services": "50% से 90% तक कम कीमत पर प्रमाणित जेनेरिक दवाएं",
        "timing": "सुबह 9:00 से रात 8:00 बजे",
        "latitude": 26.9050,
        "longitude": 75.7950
    },
    {
        "name": "स्थानीय मेडिकल स्टोर व केमिस्ट (Local Medical Store / Pharmacy)",
        "type": "निजी दवा की दुकान (Retail Chemist)",
        "services": "सभी ब्रांडेड दवाएं, ओटीसी उत्पाद, इंजेक्शन व सर्जिकल सामान",
        "timing": "सुबह 8:00 से रात 10:00 बजे",
        "latitude": 26.9180,
        "longitude": 75.7910
    }
]


# Guidance for safely purchasing medicines online in India (Drugs & Cosmetics Act compliant)
ONLINE_ORDERING_STEPS: Dict[str, Any] = {
    "title_hindi": "घर बैठे ऑनलाइन दवा मंगवाने का सुरक्षित तरीका",
    "disclaimer_hindi": "⚠️ सेहत साथी खुद दवाइयां नहीं बेचता है। भारतीय दवा कानूनों (Drugs & Cosmetics Act) के अनुसार डॉक्टर के वैध पर्चे के बिना कोई भी ऐप या दुकान शेड्यूल H दवाएं नहीं बेच सकती।",
    "steps": [
        {
            "step_num": 1,
            "title": "पर्चे की साफ तस्वीर रखें (Keep Clear Prescription)",
            "desc": "पर्चे पर डॉक्टर का नाम, रजिस्ट्रेशन नंबर, तारीख और मरीज का नाम साफ दिखना चाहिए। ऑनलाइन ऐप बिना पर्चे के एंटीबायोटिक या बीपी/शुगर की दवाएं नहीं भेजते।"
        },
        {
            "step_num": 2,
            "title": "विश्वसनीय ऐप या स्थानीय केमिस्ट का चुनाव करें (Choose Trusted Channel)",
            "desc": "ग्रामीण क्षेत्रों में नजदीकी केमिस्ट के व्हाट्सएप पर पर्चा भेजकर होम डिलीवरी लेना सबसे तेज और आसान होता है। या आधिकारिक 'जन औषधि सुगम' (Jan Aushadhi Sugam) ऐप, Tata 1mg, Apollo 24/7, या Netmeds का उपयोग करें।"
        },
        {
            "step_num": 3,
            "title": "दवा प्राप्त होने पर 3 जरूरी जांच (Check Upon Delivery)",
            "desc": "1. दवा के पत्ते की सील बंद हो। 2. एक्सपायरी तारीख (Expiry Date) बची हो। 3. दवा का नाम और पावर (mg) आपके पर्चे से मिलती हो।"
        }
    ],
    "trusted_platforms": [
        {"name": "जन औषधि सुगम (सरकारी पोर्टल)", "url": "https://janaushadhi.gov.in/"},
        {"name": "Tata 1mg (दवा डिलीवरी)", "url": "https://www.1mg.com/"},
        {"name": "Apollo Pharmacy 24/7", "url": "https://www.apollopharmacy.in/"},
        {"name": "Netmeds", "url": "https://www.netmeds.com/"}
    ]
}


class PreventionAndFacilitiesService:
    """
    Provides community disease prevention guidance, zero-friction map navigation,
    and safe online pharmacy guidance.
    """

    @classmethod
    def get_online_ordering_guide(cls) -> Dict[str, Any]:
        return ONLINE_ORDERING_STEPS

    @classmethod
    def get_prevention_topics(cls) -> List[Dict[str, Any]]:
        return PREVENTION_TOPICS

    @classmethod
    def get_sample_facilities(cls) -> List[Dict[str, Any]]:
        return SAMPLE_HEALTH_FACILITIES

    @classmethod
    def build_maps_search_url(cls, search_query: str, user_location: Optional[str] = None) -> str:
        """
        Builds a universal Google Maps search URL that works on mobile and web
        without requiring paid API keys or exposing user tokens.
        """
        query_text = search_query.strip()
        if user_location and user_location.strip():
            query_text += f" in {user_location.strip()}"
        else:
            query_text += " near me"
        
        encoded = urllib.parse.quote(query_text)
        return f"https://www.google.com/maps/search/?api=1&query={encoded}"
