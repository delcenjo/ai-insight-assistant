from fastapi.testclient import TestClient

from assistant.api import app

client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_chat_requires_api_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    response = client.post("/chat", json={"message": "What is the vacation policy?"})
    assert response.status_code == 503
