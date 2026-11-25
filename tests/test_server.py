import importlib

from cardgame import server


def test_health_returns_ok(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    module = importlib.reload(server)

    response = module.app.test_client().get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_app_starts_without_database_url(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    module = importlib.reload(server)

    assert module.app is not None
    assert module.DATABASE_URL is None
