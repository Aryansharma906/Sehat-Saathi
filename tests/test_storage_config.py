from pathlib import Path

from services.storage_config import PROJECT_ROOT, get_data_dir


def test_data_dir_defaults_to_repository_data(monkeypatch):
    monkeypatch.delenv("SEHAT_DATA_DIR", raising=False)
    assert get_data_dir() == PROJECT_ROOT / "data"


def test_data_dir_uses_configured_absolute_directory(tmp_path, monkeypatch):
    configured = tmp_path / "isolated records"
    monkeypatch.setenv("SEHAT_DATA_DIR", str(configured))
    assert get_data_dir() == configured.resolve()
    assert not configured.exists()


def test_data_dir_expands_home_directory(monkeypatch):
    monkeypatch.setenv("SEHAT_DATA_DIR", "~/sehat-saathi-test-data")
    assert get_data_dir() == (Path.home() / "sehat-saathi-test-data").resolve()
