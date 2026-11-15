import json
from types import SimpleNamespace

from app.agents.order_agent import OrderAgent
from app.agents.base_agent import FALLBACK_ERROR_MESSAGE


def tool_call(name, arguments, call_id="call_1"):
    return SimpleNamespace(id=call_id, function=SimpleNamespace(name=name, arguments=arguments))


def completion(content=None, tool_calls=None):
    message = SimpleNamespace(content=content, tool_calls=tool_calls)
    return SimpleNamespace(choices=[SimpleNamespace(message=message)])


class FakeClient:
    """Minimal stand-in for the OpenAI client that replays canned completions"""

    def __init__(self, *responses):
        self._responses = list(responses)
        self.calls = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    async def _create(self, **kwargs):
        self.calls.append(kwargs)
        response = self._responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


async def test_plain_response(db):
    agent = OrderAgent(db)
    agent.ai_client = FakeClient(completion("Hello!"))

    result = await agent.process("hi")

    assert result["content"] == "Hello!"
    assert result["tool_calls"] is None


async def test_empty_model_response_gets_fallback_text(db):
    agent = OrderAgent(db)
    agent.ai_client = FakeClient(completion(None))

    assert (await agent.process("hi"))["content"]


async def test_provider_error_is_not_leaked_to_user(db):
    agent = OrderAgent(db)
    agent.ai_client = FakeClient(RuntimeError("401 invalid api key gsk_secret"))

    result = await agent.process("hi")

    assert result["content"] == FALLBACK_ERROR_MESSAGE
    assert "gsk_secret" not in result["content"]


async def test_tool_call_round_trip(db):
    agent = OrderAgent(db)
    client = FakeClient(
        completion(tool_calls=[tool_call("fetch_order_details", json.dumps({"order_number": "NOPE"}))]),
        completion("I couldn't find that order."),
    )
    agent.ai_client = client

    result = await agent.process("where is NOPE?")

    assert result["content"] == "I couldn't find that order."
    assert result["tool_calls"] == [
        {"tool": "fetch_order_details", "arguments": {"order_number": "NOPE"}}
    ]
    tool_message = client.calls[1]["messages"][-1]
    assert tool_message["role"] == "tool"
    assert json.loads(tool_message["content"])["success"] is False


async def test_bad_tool_calls_become_tool_errors_not_crashes(db):
    agent = OrderAgent(db)
    tools = agent.get_tools()

    unknown = await agent._execute_tool_call(tool_call("does_not_exist", "{}"), tools)
    assert "not found" in unknown["message"]["content"]

    invalid_json = await agent._execute_tool_call(tool_call("fetch_order_details", "{oops"), tools)
    assert "Invalid tool arguments" in invalid_json["message"]["content"]

    not_an_object = await agent._execute_tool_call(tool_call("fetch_order_details", "[1]"), tools)
    assert "Invalid tool arguments" in not_an_object["message"]["content"]

    wrong_args = await agent._execute_tool_call(
        tool_call("fetch_order_details", json.dumps({"bogus": 1})), tools
    )
    assert "Invalid tool arguments" in wrong_args["message"]["content"]
