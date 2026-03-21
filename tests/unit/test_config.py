import pytest

from src.config import get_settings


def test_get_settings_default_environment(monkeypatch):
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    get_settings.cache_clear()

    settings = get_settings()

    assert settings.app_env == "development"


def test_get_settings_production_requires_secret(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("JWT_SECRET_KEY", "change-me-in-production")
    get_settings.cache_clear()

    with pytest.raises(RuntimeError):
        get_settings()

    get_settings.cache_clear()
