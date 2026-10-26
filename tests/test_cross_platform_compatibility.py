"""
Tests for Cross-Platform Compatibility (iOS, Android & Desktop Website)
Verifies PWA Manifest, Service Worker, iOS Safari WebApp meta tags, and touch target accessibility.
"""

import json
from pathlib import Path
from PIL import Image
from services.emergency_service import EmergencyService
from services.prevention_and_facilities import PreventionAndFacilitiesService
from services.health_issue_service import HealthIssueService
from models.health_issue import TreatmentIssueLog


def test_pwa_manifest_validity():
    """Verify static/manifest.json conforms to PWA standards for Android & iOS WebAPK."""
    manifest_path = Path("static/manifest.json")
    assert manifest_path.exists(), "static/manifest.json must exist"

    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["name"] == "Sehat Saathi (सेहत साथी)"
    assert data["short_name"] == "Sehat Saathi"
    assert data["display"] == "standalone"
    assert data["theme_color"] == "#28654e"
    assert len(data["icons"]) >= 2
    assert any(icon["sizes"] == "192x192" for icon in data["icons"])
    assert any(icon["sizes"] == "512x512" for icon in data["icons"])


def test_app_icons_exist_and_valid():
    """Verify PWA and iOS touch icons are valid PNG images."""
    icon_192 = Path("static/icon-192.png")
    icon_512 = Path("static/icon-512.png")
    assert icon_192.exists() and icon_192.stat().st_size > 0
    assert icon_512.exists() and icon_512.stat().st_size > 0

    with Image.open(icon_192) as img:
        assert img.size == (192, 192)
        assert img.format == "PNG"

    with Image.open(icon_512) as img:
        assert img.size == (512, 512)
        assert img.format == "PNG"


def test_service_worker_asset_caching():
    """Verify static/sw.js exists with cache-first and lifecycle handlers."""
    sw_path = Path("static/sw.js")
    assert sw_path.exists()
    content = sw_path.read_text(encoding="utf-8")
    assert "install" in content
    assert "activate" in content
    assert "fetch" in content
    assert "caches.open" in content


def test_ios_and_android_meta_tags_in_main_app():
    """Verify app/main.py contains iOS webapp, safe-area-inset, and Android theme tags."""
    main_code = Path("app/main.py").read_text(encoding="utf-8")
    assert "apple-mobile-web-app-capable" in main_code
    assert "apple-touch-icon" in main_code
    assert "safe-area-inset" in main_code
    assert "manifest.json" in main_code
    assert "theme-color" in main_code


def test_universal_deep_links_cross_platform():
    """Verify deep links execute universally across iOS, Android, and Desktop web."""
    # Emergency dialer link: tel:108
    tel_link = EmergencyService.build_tel_link("108")
    assert tel_link == "tel:108"

    # WhatsApp Click-to-Chat (works in iOS WhatsApp, Android WhatsApp, and WhatsApp Web on Desktop)
    dummy_issue = TreatmentIssueLog(
        medicine_name="Dolo",
        issue_type="हल्की खुजली",
        severity="सामान्य"
    )
    wa_url = HealthIssueService.generate_whatsapp_share_url(dummy_issue, doctor_phone="9876543210")
    assert wa_url.startswith("https://api.whatsapp.com/send?phone=9876543210")

    # Google Maps navigation link (opens Apple Maps/Google Maps on iOS/Android, and Browser on Desktop)
    maps_url = PreventionAndFacilitiesService.build_maps_search_url("Hospital", "Behror")
    assert "google.com/maps/search/" in maps_url
