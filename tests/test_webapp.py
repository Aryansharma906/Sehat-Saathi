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


def test_demo_prescriptions_keep_the_ambiguity_flags():
    with client() as c:
        clear = c.post("/api/prescriptions/demo", json={"scenario": "clean"})
        unclear = c.post("/api/prescriptions/demo", json={"scenario": "ambiguous"})
        assert clear.status_code == unclear.status_code == 200
        assert clear.json()["prescription"]["medicines"]
        assert any(m["is_uncertain"] for m in unclear.json()["prescription"]["medicines"])
        assert c.post("/api/prescriptions/demo", json={"scenario": "invented"}).status_code == 400


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
        assert c.post("/api/wellness", json={"sleep":"Good Sleep","stress":"Normal","mood":"Positive","lang":"en"}).status_code == 200
        assert c.post("/api/progress", json={"feeling":"Much Better","adherence":"All Doses On Time","symptoms":"Fully Relieved","lang":"en"}).status_code == 200
        severe = c.post("/api/issues", json={"medicine_name":"Example","issue_type":"breathing difficulty","severity":"Severe"})
        assert severe.status_code == 200
        assert severe.json()["issue"]["is_severe_alert"] is True


def test_nearby_and_chat_routes_keep_safety_tripwires():
    with client() as c:
        places = c.get("/api/facilities?locality=Neemrana&radius=10")
        assert places.status_code == 200
        assert places.json()["nearest_facility"]
        answer = c.post("/api/chat", json={"question":"What illness do I have?"})
        assert answer.status_code == 200
        assert "निदान" in answer.json()["answer"] or "diagnosis" in answer.json()["answer"].lower()
        assert c.post("/api/chat", json={"question":""}).status_code == 422


def test_unknown_locality_never_returns_another_towns_facilities():
    with client() as c:
        places = c.get("/api/facilities?locality=Washington%20DC&radius=10")
        assert places.status_code == 200
        data = places.json()
        assert data["directory_status"] == "unavailable_for_location"
        assert data["facilities"] == []
        assert data["user_location"]["latitude"] is None


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
