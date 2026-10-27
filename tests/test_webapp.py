"""Contract checks for the browser-first app and its safety-critical actions."""

from starlette.testclient import TestClient

from webapp import main as web


def client():
    return TestClient(web.app)


def test_browser_shell_and_static_assets_are_served():
    with client() as c:
        page = c.get("/")
        assert page.status_code == 200
        assert "Care, clearly" in page.text
        assert c.get("/assets/app.css").status_code == 200
        assert c.get("/assets/app.js").status_code == 200
        assert c.get("/illustrations/care-companion.svg").status_code == 200
        assert c.get("/illustrations/manifest.json").status_code == 200
        assert c.get("/api/health").json()["status"] == "ok"
        script = c.get("/assets/app.js").text
        assert "127.0.0.1:7738" not in script
        assert "agent log" not in script


def test_overview_and_resources_are_serializable():
    with client() as c:
        overview = c.get("/api/overview")
        resources = c.get("/api/resources")
        assert overview.status_code == 200
        assert isinstance(overview.json()["reminders"], list)
        assert overview.json()["emergency"]
        assert resources.status_code == 200
        assert resources.json()["prevention"]
        assert resources.json()["medicines"]


def test_local_data_directory_can_be_redirected_without_touching_repo_data(tmp_path, monkeypatch):
    from services.storage_config import get_data_dir

    target = tmp_path / "isolated-health-data"
    monkeypatch.setenv("SEHAT_DATA_DIR", str(target))
    assert get_data_dir() == target.resolve()
    assert not target.exists()


def test_demo_prescriptions_keep_the_ambiguity_flags():
    with client() as c:
        clear = c.post("/api/prescriptions/demo", json={"scenario": "clean"})
        unclear = c.post("/api/prescriptions/demo", json={"scenario": "ambiguous"})
        assert clear.status_code == unclear.status_code == 200
        assert clear.json()["prescription"]["medicines"]
        assert any(m["is_uncertain"] for m in unclear.json()["prescription"]["medicines"])
        assert c.post("/api/prescriptions/demo", json={"scenario": "invented"}).status_code == 400


def test_live_scan_without_gemini_key_fails_clearly_without_fabricating_medicines(monkeypatch):
    from io import BytesIO
    from PIL import Image, ImageDraw

    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    image = Image.new("RGB", (600, 450), "#d0d0d0")
    draw = ImageDraw.Draw(image)
    for y in range(50, 400, 45):
        draw.line((40, y, 550, y), fill="#101010", width=5)
    image_bytes = BytesIO()
    image.save(image_bytes, format="JPEG")
    with client() as c:
        response = c.post("/api/prescriptions/scan", files={"prescription": ("sample.jpg", image_bytes.getvalue(), "image/jpeg")})

    assert response.status_code == 200
    prescription = response.json()["prescription"]
    assert prescription["medicines"] == []
    assert prescription["unresolved_fields"] == ["GEMINI_API_KEY"]


def test_sample_prescription_to_confirmed_reminder_flow_is_end_to_end(tmp_path, monkeypatch):
    from storage.persistence import LocalStorageAdapter

    monkeypatch.setattr(web, "reminders", web.ReminderService(LocalStorageAdapter(tmp_path / "schedules.json")))
    with client() as c:
        sample = c.post("/api/prescriptions/demo", json={"scenario": "clean"}).json()["prescription"]
        medicine = sample["medicines"][0]
        assert medicine["user_confirmed"] is False
        medicine["user_confirmed"] = True

        created = c.post("/api/reminders", json={
            "medicine": medicine,
            "prescription_id": sample["id"],
            "prescription_date": sample["prescription_date"],
        })

        assert created.status_code == 200
        assert len(created.json()["created"]) == 1
        reminder = created.json()["created"][0]
        assert reminder["medicine_name"] == medicine["candidate_medicine_name"]
        assert reminder["source_prescription_id"] == sample["id"]
        overview = c.get("/api/overview").json()
        assert overview["reminders"][0]["id"] == reminder["id"]


def test_confirmed_prescription_explanation_supports_selected_languages():
    medicine = {
        "raw_medicine_name": "Tab Dolo 650",
        "candidate_medicine_name": "Dolo 650",
        "dose_instruction_raw": "1 tablet",
        "frequency_raw": "OD",
        "timing_raw": "After food",
        "user_confirmed": True,
    }
    with client() as c:
        hindi = c.post("/api/prescriptions/explanation", json={"medicine": medicine, "lang": "hi"})
        english = c.post("/api/prescriptions/explanation", json={"medicine": medicine, "lang": "en"})
        unconfirmed = c.post("/api/prescriptions/explanation", json={"medicine": {**medicine, "user_confirmed": False}})
        invalid_language = c.post("/api/prescriptions/explanation", json={"medicine": medicine, "lang": ["hi"]})
    assert hindi.status_code == english.status_code == 200
    assert hindi.json()["language"] == "hi"
    assert "दवा का नाम" in hindi.json()["explanation"]
    assert "Medicine Name" in english.json()["explanation"]
    assert unconfirmed.status_code == 409
    assert invalid_language.status_code == 422


def test_confirmed_prescription_audio_returns_audio_and_fails_clearly(monkeypatch):
    medicine = {
        "raw_medicine_name": "Tab Example",
        "candidate_medicine_name": "Example",
        "dose_instruction_raw": "1 tablet",
        "frequency_raw": "OD",
        "timing_raw": "After food",
        "user_confirmed": True,
    }
    monkeypatch.setattr(web.language, "generate_speech_audio", lambda text, lang="hi": b"audio-data")
    with client() as c:
        response = c.post("/api/prescriptions/audio", json={"medicine": medicine, "lang": "en"})
        unconfirmed = c.post("/api/prescriptions/audio", json={"medicine": {**medicine, "user_confirmed": False}})
        monkeypatch.setattr(web.language, "generate_speech_audio", lambda text, lang="hi": None)
        unavailable = c.post("/api/prescriptions/audio", json={"medicine": medicine, "lang": "en"})
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/mpeg"
    assert response.content == b"audio-data"
    assert unconfirmed.status_code == 409
    assert unavailable.status_code == 503


def test_unconfirmed_medicine_cannot_create_a_reminder(tmp_path, monkeypatch):
    monkeypatch.setattr(web, "reminders", web.ReminderService(web.reminders.storage.__class__(tmp_path / "schedules.json")))
    medicine = {"raw_medicine_name": "Tab Example", "candidate_medicine_name": "Example", "dose_instruction_raw": "1 tablet", "frequency_raw": "OD", "timing_raw": "After food", "user_confirmed": False}
    with client() as c:
        response = c.post("/api/reminders", json={"medicine": medicine})
        assert response.status_code == 409
        medicine["user_confirmed"] = True
        medicine["frequency_raw"] = "SOS / as needed"
        assert c.post("/api/reminders", json={"medicine": medicine}).status_code == 422
        assert web.reminders.get_all_reminders() == []


def test_explicitly_confirmed_reminders_can_be_managed_without_touching_user_data(tmp_path, monkeypatch):
    from storage.persistence import LocalStorageAdapter

    monkeypatch.setattr(web, "reminders", web.ReminderService(LocalStorageAdapter(tmp_path / "schedules.json")))
    medicine = {"raw_medicine_name": "Tab Example", "candidate_medicine_name": "Example", "dose_instruction_raw": "1 tablet", "frequency_raw": "OD", "timing_raw": "After food", "user_confirmed": True}
    with client() as c:
        created = c.post("/api/reminders", json={"medicine": medicine})
        assert created.status_code == 200
        reminder_id = created.json()["created"][0]["id"]
        assert c.post(f"/api/reminders/{reminder_id}/time", json={"time":"19:30"}).status_code == 200
        assert web.reminders.get_all_reminders()[0].reminder_time == "19:30"
        assert c.post(f"/api/reminders/{reminder_id}/time", json={"time":"25:80"}).status_code == 422
        assert c.post(f"/api/reminders/{reminder_id}/taken", json={}).status_code == 200
        assert web.reminders.get_all_reminders()[0].taken_today is True
        assert c.post(f"/api/reminders/{reminder_id}/toggle", json={}).json()["result"] is False
        assert c.post(f"/api/reminders/{reminder_id}/delete", json={}).status_code == 200
        assert web.reminders.get_all_reminders() == []


def test_custom_reminder_times_reject_invalid_or_empty_values(tmp_path, monkeypatch):
    from storage.persistence import LocalStorageAdapter

    monkeypatch.setattr(web, "reminders", web.ReminderService(LocalStorageAdapter(tmp_path / "schedules.json")))
    medicine = {
        "raw_medicine_name": "Tab Example",
        "candidate_medicine_name": "Example",
        "dose_instruction_raw": "1 tablet",
        "frequency_raw": "OD",
        "timing_raw": "After food",
        "user_confirmed": True,
    }
    with client() as c:
        for times in (["99:99"], ["08:00", "08:00"], [], ["08:00", "20:00"]):
            response = c.post("/api/reminders", json={"medicine": medicine, "times": times})
            assert response.status_code == 422
        assert web.reminders.get_all_reminders() == []

        medicine["frequency_raw"] = "BD"
        created = c.post("/api/reminders", json={"medicine": medicine, "times": ["07:30", "19:45"]})
        assert created.status_code == 200
        assert [item["reminder_time"] for item in created.json()["created"]] == ["07:30", "19:45"]


def test_vitals_checkins_and_issue_logging_use_service_validations(tmp_path, monkeypatch):
    from services.device_data_service import DeviceDataService
    from services.health_issue_service import HealthIssueService
    from services.mental_health_service import MentalHealthService
    from services.progress_tracker_service import ProgressTrackerService

    monkeypatch.setattr(web, "vitals", DeviceDataService(tmp_path / "vitals.json"))
    monkeypatch.setattr(web, "wellness", MentalHealthService(tmp_path / "wellness.json"))
    monkeypatch.setattr(web, "progress", ProgressTrackerService(tmp_path / "progress.json"))
    monkeypatch.setattr(web, "issues", HealthIssueService(tmp_path / "issues.json"))
    with client() as c:
        reading = c.post("/api/vitals", json={"device_type":"Oximeter","metric_name":"SpO2","value":"89","unit":"%"})
        assert reading.status_code == 200
        assert "Critical" in reading.json()["reading"]["status_flag"]
        assert c.post("/api/vitals", json={"metric_name":"SpO2"}).status_code == 422
        invalid_reading = c.post("/api/vitals", json={"device_type":"Oximeter","metric_name":"SpO2","value":"unknown","unit":"%"})
        assert invalid_reading.status_code == 422
        assert len(web.vitals.get_all_readings()) == 1
        assert c.post("/api/wellness", json={"sleep":"Good Sleep","stress":"Normal","mood":"Positive","lang":"en"}).status_code == 200
        assert c.post("/api/progress", json={"feeling":"Much Better","adherence":"All Doses On Time","symptoms":"Fully Relieved","lang":"en"}).status_code == 200
        severe = c.post("/api/issues", json={"medicine_name":"Example","issue_type":"breathing difficulty","severity":"Severe"})
        assert severe.status_code == 200
        assert severe.json()["issue"]["is_severe_alert"] is True


def test_nearby_and_chat_routes_support_symptoms_and_validate_language(monkeypatch):
    from services.chat_service import PrescriptionChatService

    monkeypatch.setattr(web, "chat", PrescriptionChatService(api_key=""))
    with client() as c:
        places = c.get("/api/facilities?locality=Neemrana&radius=10")
        assert places.status_code == 200
        assert places.json()["nearest_facility"]
        answer = c.post("/api/chat", json={"question":"I have severe lower back pain"})
        assert answer.status_code == 200
        assert "muscle or joint strain" in answer.json()["answer"]
        assert "First, have you noticed new leg weakness or numbness" in answer.json()["answer"]
        hindi_answer = c.post("/api/chat", json={"question":"What illness do I have?","lang":"hi"})
        assert hindi_answer.status_code == 200
        assert "लक्षण" in hindi_answer.json()["answer"]
        assert c.post("/api/chat", json={"question":"A question","lang":"fr"}).status_code == 422
        assert c.post("/api/chat", json={"question":""}).status_code == 422


def test_unknown_locality_uses_live_geocoder_without_substituting_a_pilot_town(monkeypatch):
    monkeypatch.setattr(
        web.OpenStreetMapFacilityService,
        "search",
        classmethod(lambda cls, **kwargs: {
            "latitude": None,
            "longitude": None,
            "facilities": [],
            "status": "location_not_found",
            "notice": "OpenStreetMap could not find this town or city in India.",
        }),
    )
    with client() as c:
        places = c.get("/api/facilities?locality=Washington%20DC&radius=10")
        assert places.status_code == 200
        data = places.json()
        assert data["directory_status"] == "location_not_found"
        assert data["facilities"] == []
        assert data["user_location"]["latitude"] is None


def test_quick_city_outside_pilot_returns_live_osm_places(monkeypatch):
    from urllib.parse import parse_qs, urlparse

    monkeypatch.setattr(
        web.OpenStreetMapFacilityService,
        "search",
        classmethod(lambda cls, **kwargs: {
            "latitude": 28.4089,
            "longitude": 77.3178,
            "facilities": [{
                "id": "osm_node_123",
                "name_hindi": "Sample Pharmacy",
                "name_en": "Sample Pharmacy",
                "category": "chemist",
                "category_label": "PHARMACY",
                "locality": "Faridabad",
                "address": "Sample Road, Faridabad",
                "latitude": 28.409,
                "longitude": 77.318,
                "phone": None,
                "timing": "Hours not listed",
                "services": [],
                "distance_miles": 0.02,
                "distance_km": 0.03,
                "directions_url": "https://www.openstreetmap.org/directions",
                "source": "OpenStreetMap",
                "source_url": "https://www.openstreetmap.org/node/123",
            }],
            "status": "live_openstreetmap",
            "notice": "Community-mapped OpenStreetMap listings; details may be incomplete or out of date.",
        }),
    )
    with client() as c:
        response = c.get("/api/facilities?locality=Faridabad&radius=10")
        assert response.status_code == 200
        data = response.json()
        assert data["total_found"] == 1
        assert data["directory_status"] == "live_openstreetmap"
        assert data["facilities"][0]["source"] == "OpenStreetMap"
        maps_query = parse_qs(urlparse(data["fallback_maps_query"]).query)["query"][0]
        assert "28.4089,77.3178" in maps_query
        assert "Pharmacy" in maps_query


def test_live_provider_failure_keeps_google_maps_fallback(monkeypatch):
    import requests

    def unavailable(cls, **kwargs):
        raise requests.Timeout("provider timed out")

    monkeypatch.setattr(web.OpenStreetMapFacilityService, "search", classmethod(unavailable))
    with client() as c:
        response = c.get("/api/facilities?locality=Faridabad&radius=10")
    assert response.status_code == 200
    data = response.json()
    assert data["directory_status"] == "live_provider_unavailable"
    assert data["facilities"] == []
    assert "temporarily unavailable" in data["directory_notice"]
    assert "Faridabad" in data["fallback_maps_query"]


def test_production_startup_is_blocked_until_required_controls_exist(monkeypatch):
    import pytest

    monkeypatch.setenv("SEHAT_ENV", "production")
    with pytest.raises(RuntimeError, match="Production startup is disabled"):
        with TestClient(web.app):
            pass


def test_prototype_scope_is_explicit_in_home_and_overview():
    with client() as c:
        assert "Research prototype" in c.get("/").text
        scope = c.get("/api/overview").json()["service_scope"]
        assert scope["production_ready"] is False
        assert "Neemrana" in scope["region"]


def test_json_body_size_limit_rejects_large_request():
    with client() as c:
        response = c.post("/api/chat", content=b" " * (64 * 1024 + 1), headers={"content-type": "application/json"})
        assert response.status_code == 413


def test_public_demo_blocks_personal_data_writes(monkeypatch):
    monkeypatch.setattr(web, "PUBLIC_DEMO", True)
    with client() as c:
        assert c.post("/api/vitals", json={"device_type":"Monitor","metric_name":"BP","value":"120/80","unit":"mmHg"}).status_code == 403
        assert c.post("/api/chat", json={"question":"A private health question"}).status_code == 403
        assert c.post("/api/prescriptions/scan", files={"prescription":("private.jpg",b"not-an-image","image/jpeg")}).status_code == 403


def test_public_demo_allows_only_synthetic_prescription_examples(monkeypatch):
    monkeypatch.setattr(web, "PUBLIC_DEMO", True)
    with client() as c:
        sample = c.post("/api/prescriptions/demo", json={"scenario":"clean"})
        assert sample.status_code == 200
        assert sample.json()["demo"] is True
        assert sample.json()["prescription"]["medicines"]
        assert c.get("/api/health").headers["cache-control"] == "no-store"


def test_private_test_mode_requires_basic_auth_and_allows_writes(monkeypatch):
    import base64

    monkeypatch.setattr(web, "PRIVATE_TEST", True)
    monkeypatch.setattr(web, "PUBLIC_DEMO", False)
    monkeypatch.setattr(web, "TEST_ACCESS_PASSWORD", "test-only-secret")
    credentials = base64.b64encode(b"tester:test-only-secret").decode("ascii")
    with client() as c:
        unauthenticated = c.get("/api/health")
        authenticated = c.get("/api/health", headers={"Authorization": f"Basic {credentials}"})
        write_response = c.post(
            "/api/vitals",
            json={"device_type": "Monitor", "metric_name": "BP", "value": "120/80", "unit": "mmHg"},
            headers={"Authorization": f"Basic {credentials}"},
        )
    assert unauthenticated.status_code == 401
    assert "Basic" in unauthenticated.headers["www-authenticate"]
    assert authenticated.status_code == 200
    assert authenticated.headers["cache-control"] == "no-store"
    assert write_response.status_code == 200


def test_private_test_mode_refuses_startup_without_password(monkeypatch):
    import pytest

    monkeypatch.setattr(web, "PRIVATE_TEST", True)
    monkeypatch.setattr(web, "APP_MODE", "test")
    monkeypatch.setattr(web, "TEST_ACCESS_PASSWORD", "")
    monkeypatch.setenv("SEHAT_ENV", "test")
    with pytest.raises(RuntimeError, match="SEHAT_TEST_ACCESS_PASSWORD is required"):
        with TestClient(web.app):
            pass


def test_facilities_and_overview_support_auto_gps_coordinates_and_manual_input():
    with client() as c:
        # 1. Auto GPS coordinates near Neemrana (27.989, 76.388)
        gps_res = c.get("/api/facilities?lat=27.989&lon=76.388&radius=10")
        assert gps_res.status_code == 200
        gps_data = gps_res.json()
        assert gps_data["user_location"]["source"] == "gps"
        assert gps_data["user_location"]["latitude"] == 27.989
        assert gps_data["user_location"]["longitude"] == 76.388
        assert "Near Neemrana" in gps_data["user_location"]["locality"]
        assert gps_data["total_found"] == 7

        # 2. Overview endpoint with GPS coordinates
        ov_res = c.get("/api/overview?lat=27.8876&lon=76.2818")
        assert ov_res.status_code == 200
        ov_nearby = ov_res.json()["nearby"]
        assert ov_nearby["user_location"]["source"] == "gps"
        assert "Near Behror" in ov_nearby["user_location"]["locality"]
        assert ov_nearby["total_found"] == 7

        # 3. Manual "lat, lon" string in locality parameter
        manual_coord_res = c.get("/api/facilities?locality=26.9124,%2075.7873&radius=10")
        assert manual_coord_res.status_code == 200
        mc_data = manual_coord_res.json()
        assert mc_data["user_location"]["latitude"] == 26.9124
        assert "Near Jaipur" in mc_data["user_location"]["locality"]
        assert mc_data["total_found"] == 3

        # 4. Invalid coordinates rejected with HTTP 400
        assert c.get("/api/facilities?lat=999&lon=76.388").status_code == 400
        assert c.get("/api/facilities?lat=27.989").status_code == 400
