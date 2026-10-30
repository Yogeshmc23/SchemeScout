from unittest.mock import AsyncMock

from app import main


def test_health(client):
    assert client.get("/api/health").json()["status"] == "ok"


def test_profile_roundtrip(client, profile):
    response = client.post("/api/profile", json=profile.model_dump())
    assert response.status_code == 200
    assert response.json() == profile.model_dump()


def test_validation_does_not_echo_private_input(client):
    response = client.post("/api/profile", json={"state": "x", "password": "sensitive-value"})
    assert response.status_code == 422
    assert "sensitive-value" not in response.text


def test_database_missing_returns_actionable_error(client, monkeypatch):
    monkeypatch.setattr(main.db, "pool", None)
    response = client.get("/api/scholarships")
    assert response.status_code == 503
    assert "DATABASE_URL" in response.text


def test_discover_requires_profile(client):
    response = client.post("/api/discover", json={"mode": "DISCOVER", "query": "engineering scholarships"})
    assert response.status_code == 422


def test_small_query_rejected(client):
    assert client.post("/api/search", json={"query": "a"}).status_code == 422


def test_body_size_limit(client):
    response = client.post("/api/profile", content=b"x" * 262145)
    assert response.status_code == 413
    assert len(response.headers["X-Request-ID"]) == 32


def test_client_cannot_forge_official_match(client, profile, scholarship):
    response = client.post("/api/match", json={"profile": profile.model_dump(), "scholarships": [scholarship.model_dump(mode="json")]})
    assert response.status_code == 200
    assert response.json()[0]["status"] == "NEEDS_INFORMATION"


def test_chat_endpoint_contract(client, monkeypatch):
    monkeypatch.setattr(main.db, "health", AsyncMock())
    monkeypatch.setattr(main.db, "list", AsyncMock(return_value=[]))
    response = client.post("/api/chat", json={"query": "Explain documents"})
    assert response.status_code == 200
    assert response.json()["mode"] == "CHAT"
    assert "cannot verify" in response.json()["summary"]


def test_request_correlation_header(client):
    response = client.get("/api/health")
    assert len(response.headers["X-Request-ID"]) == 32


def test_openapi_contracts(client):
    schema = client.get("/openapi.json").json()
    assert "/api/discover" in schema["paths"]
    assert "Profile" in schema["components"]["schemas"]


def test_openapi_through_frontend_paths(client):
    assert client.get("/api/docs").status_code == 200
    assert client.get("/api/openapi.json").status_code == 200


def test_expensive_requests_are_capacity_limited(client, monkeypatch):
    class BusySemaphore:
        async def acquire(self):
            raise TimeoutError()

        def release(self):
            raise AssertionError("Unacquired slot must not be released")
    monkeypatch.setattr(main, "slots", BusySemaphore())
    response = client.post("/api/search", json={"query": "scholarships"})
    assert response.status_code == 429
    assert len(response.headers["X-Request-ID"]) == 32
    assert client.get("/api/health").status_code == 200


def test_stored_eligibility_uses_database_records(client, monkeypatch, profile, scholarship):
    monkeypatch.setattr(main.db, "list", AsyncMock(return_value=[scholarship]))
    response = client.post("/api/eligibility", json=profile.model_dump())
    assert response.status_code == 200
    assert response.json()[0]["status"] == "ELIGIBLE"
    main.db.list.assert_awaited_once()
