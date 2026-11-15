import pytest

from app.agents.router_agent import parse_routing_decision


def test_parses_plain_json():
    result = parse_routing_decision('{"agent": "order", "confidence": 0.9, "reasoning": "tracking"}')
    assert result == {"agent": "order", "confidence": 0.9, "reasoning": "tracking"}


@pytest.mark.parametrize("fence", ["```json\n{body}\n```", "```\n{body}\n```"])
def test_strips_markdown_fences(fence):
    body = '{"agent": "billing", "confidence": 0.8, "reasoning": "refund"}'
    assert parse_routing_decision(fence.format(body=body))["agent"] == "billing"


@pytest.mark.parametrize("raw", ["not json", "", None, "[1, 2]", '"order"'])
def test_falls_back_to_support_on_bad_output(raw):
    result = parse_routing_decision(raw)
    assert result["agent"] == "support"
    assert result["confidence"] == 0.5


def test_unknown_agent_falls_back_to_support():
    assert parse_routing_decision('{"agent": "sales"}')["agent"] == "support"


def test_agent_name_is_normalised():
    assert parse_routing_decision('{"agent": " Order "}')["agent"] == "order"


@pytest.mark.parametrize("value,expected", [(5, 1.0), (-1, 0.0), ("abc", 0.5), (None, 0.5)])
def test_confidence_is_clamped(value, expected):
    import json

    result = parse_routing_decision(json.dumps({"agent": "order", "confidence": value}))
    assert result["confidence"] == expected
