"""Tests for the bridgetos.schema module."""

from datetime import datetime, timezone

import pytest

from bridgetos import Observation, ObservationContent, ObservationContext, ToolCall


def test_observation_minimum_fields():
    obs = Observation(
        agent_id="a",
        content=ObservationContent(text="hello"),
    )
    wire = obs.to_wire()
    assert wire["agent_id"] == "a"
    assert wire["content"]["text"] == "hello"
    assert wire["schema_version"] == "1.0"
    assert "timestamp" in wire


def test_observation_with_tool_calls():
    obs = Observation(
        agent_id="a",
        content=ObservationContent(
            text="ok",
            tool_calls=[ToolCall(name="lookup", arguments={"id": 1})],
        ),
    )
    wire = obs.to_wire()
    assert wire["content"]["tool_calls"][0]["name"] == "lookup"
    assert wire["content"]["tool_calls"][0]["arguments"] == {"id": 1}


def test_observation_rejects_extra_fields():
    with pytest.raises(Exception):
        Observation(
            agent_id="a",
            content=ObservationContent(text="hi"),
            unknown_field="oops",
        )


def test_observation_explicit_timestamp():
    ts = datetime(2026, 5, 1, 18, 0, tzinfo=timezone.utc)
    obs = Observation(
        agent_id="a",
        timestamp=ts,
        content=ObservationContent(text="hi"),
    )
    wire = obs.to_wire()
    assert wire["timestamp"].startswith("2026-05-01T18:00:00")


def test_context_optional():
    obs = Observation(
        agent_id="a",
        content=ObservationContent(text="hi"),
        context=ObservationContext(task_type="support", framework="langchain"),
    )
    wire = obs.to_wire()
    assert wire["context"]["task_type"] == "support"
    assert wire["context"]["framework"] == "langchain"
