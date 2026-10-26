"""
Emergency Helplines and Calling Service for Rural Healthcare
Provides official Government of India emergency agency numbers with direct tel: protocol links.
"""

from typing import List, Dict, Any


EMERGENCY_AGENCIES: List[Dict[str, Any]] = [
    {
        "number": "108",
        "name_hindi": "आपातकालीन एम्बुलेंस (Ambulance - Medical Emergency)",
        "desc_hindi": "गंभीर बीमारी, दुर्घटना, सीने में दर्द या बेहोशी की स्थिति में 24 घंटे मुफ्त सरकारी एम्बुलेंस।",
        "color": "#d32f2f",  # Red
        "icon": "🚑"
    },
    {
        "number": "112",
        "name_hindi": "राष्ट्रीय आपातकालीन नंबर (All-in-One Emergency - 112)",
        "desc_hindi": "अखिल भारतीय एकीकृत हेल्पलाइन (पुलिस, एम्बुलेंस, फायर ब्रिगेड और आपदा प्रबंधन)।",
        "color": "#c2185b",  # Deep Rose
        "icon": "🚨"
    },
    {
        "number": "104",
        "name_hindi": "स्वास्थ्य सलाह हेल्पलाइन (Health Advice Helpline - 104)",
        "desc_hindi": "सरकारी डॉक्टरों से सीधे फोन पर प्राथमिक चिकित्सा सलाह और स्वास्थ्य जानकारी।",
        "color": "#1976d2",  # Blue
        "icon": "🩺"
    },
    {
        "number": "102",
        "name_hindi": "जननी शिशु एम्बुलेंस (Mother & Child Ambulance - 102)",
        "desc_hindi": "गर्भवती महिलाओं को प्रसव के लिए अस्पताल पहुंचाने और नवजात शिशु की मुफ्त एम्बुलेंस।",
        "color": "#388e3c",  # Green
        "icon": "👶"
    }
]


class EmergencyService:
    @classmethod
    def get_emergency_numbers(cls) -> List[Dict[str, Any]]:
        return EMERGENCY_AGENCIES

    @classmethod
    def build_tel_link(cls, phone_number: str) -> str:
        """
        Creates a clean tel: protocol link for native smartphone dialer invocation.
        """
        clean_num = phone_number.strip().replace(" ", "").replace("-", "")
        return f"tel:{clean_num}"
