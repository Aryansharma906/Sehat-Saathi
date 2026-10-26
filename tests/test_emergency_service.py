"""
Unit Tests for Emergency Helplines and Tel: Calling Links
"""

import pytest
from services.emergency_service import EmergencyService


def test_emergency_numbers_catalog():
    agencies = EmergencyService.get_emergency_numbers()
    assert len(agencies) >= 4

    numbers = [a["number"] for a in agencies]
    assert "108" in numbers  # Ambulance
    assert "112" in numbers  # Unified emergency
    assert "104" in numbers  # Health advice
    assert "102" in numbers  # Janani Shishu express

    for a in agencies:
        assert "name_hindi" in a
        assert "name_en" in a
        assert "desc_hindi" in a
        assert "desc_en" in a
        assert "icon" in a
        assert a["color"].startswith("#")


def test_build_tel_link():
    assert EmergencyService.build_tel_link("108") == "tel:108"
    assert EmergencyService.build_tel_link("112") == "tel:112"
    assert EmergencyService.build_tel_link(" 104 - 00 ") == "tel:10400"
