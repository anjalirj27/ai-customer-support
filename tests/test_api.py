import httpx
import pytest
import pytest_asyncio

from app.core.database import get_db
from app.main import app
from app.services.agent_service import AgentService


@pytest_asyncio.fixture
async def client(session_factory, monkeypatch):
    async def override_get_db():
        async with session_factory() as session:
            yield session

    async def fake_process_message(self, message, conversation_history=None):
        return {
            "content": f"echo: {message}",
            "agent": "support",
            "tool_calls": None,
            "routing": {"selected_agent": "support", "confidence": 1.0, "reasoning": "test"},
        }

    monkeypatch.setattr(AgentService, "process_message", fake_process_message)
    app.dependency_overrides[get_db] = override_get_db

    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()


async def test_health(client):
    response = await client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


async def test_chat_roundtrip_and_message_count(client):
    first = await client.post("/api/chat/messages", json={"message": "  hello  "})
    assert first.status_code == 200
    body = first.json()
    assert body["content"] == "echo: hello"  # whitespace trimmed

    conversation_id = body["conversation_id"]
    second = await client.post(
        "/api/chat/messages",
        json={"message": "again", "conversation_id": conversation_id},
    )
    assert second.json()["conversation_id"] == conversation_id

    detail = await client.get(f"/api/chat/conversations/{conversation_id}")
    assert detail.status_code == 200
    assert [m["role"] for m in detail.json()["messages"]] == [
        "user", "assistant", "user", "assistant"
    ]

    listing = await client.get("/api/chat/conversations")
    assert listing.status_code == 200
    assert listing.json()[0]["message_count"] == 4


@pytest.mark.parametrize("payload", [{"message": ""}, {"message": "   "}, {}])
async def test_invalid_messages_are_rejected(client, payload):
    response = await client.post("/api/chat/messages", json=payload)
    assert response.status_code == 422
    assert response.json()["success"] is False


async def test_invalid_conversation_id_is_a_client_error(client):
    assert (await client.get("/api/chat/conversations/not-a-uuid")).status_code == 422
    bad = await client.post(
        "/api/chat/messages", json={"message": "hi", "conversation_id": "nope"}
    )
    assert bad.status_code == 422


async def test_unknown_conversation_returns_404(client):
    response = await client.get("/api/chat/conversations/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    assert response.json()["error"] == "Conversation not found"


async def test_delete_conversation(client):
    created = await client.post("/api/chat/messages", json={"message": "bye"})
    conversation_id = created.json()["conversation_id"]

    assert (await client.delete(f"/api/chat/conversations/{conversation_id}")).status_code == 200
    assert (await client.get(f"/api/chat/conversations/{conversation_id}")).status_code == 404


async def test_pagination_bounds(client):
    assert (await client.get("/api/chat/conversations?limit=0")).status_code == 422
    assert (await client.get("/api/chat/conversations?limit=1000")).status_code == 422
    assert (await client.get("/api/chat/conversations?offset=-1")).status_code == 422


async def test_agent_endpoints(client):
    listing = await client.get("/api/agents/")
    assert {a["name"] for a in listing.json()["agents"]} == {"support", "order", "billing"}

    assert (await client.get("/api/agents/order/capabilities")).status_code == 200
    assert (await client.get("/api/agents/unknown/capabilities")).status_code == 404


async def test_chat_is_rate_limited(client, monkeypatch):
    # The decorator limit is fixed at import time (20/minute by default)
    from app.core.config import settings

    statuses = [
        (await client.post("/api/chat/messages", json={"message": "hi"})).status_code
        for _ in range(settings.RATE_LIMIT_PER_MINUTE + 1)
    ]
    assert statuses[:-1] == [200] * settings.RATE_LIMIT_PER_MINUTE
    assert statuses[-1] == 429


async def test_unhandled_errors_do_not_leak_details(client, monkeypatch):
    async def boom(self, *args, **kwargs):
        raise RuntimeError("secret database password")

    monkeypatch.setattr("app.services.chat_service.ChatService.send_message", boom)
    response = await client.post("/api/chat/messages", json={"message": "hi"})

    assert response.status_code == 500
    assert "secret" not in response.text
