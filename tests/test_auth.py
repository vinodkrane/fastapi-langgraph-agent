from app.core.security import verify_api_key


def test_verify_api_key_accepts_development_placeholder(monkeypatch):
    monkeypatch.setattr("app.core.security.settings.api_key", "configured-api-key")

    assert verify_api_key("change-me-dev-api-key") is True
