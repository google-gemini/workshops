from unittest.mock import MagicMock

from src.agents.autopick_agent import agent as autopick_agent


def test_enable_autopick():
  tool_context = MagicMock()
  tool_context.state = {}
  autopick_agent.enable_autopick(tool_context)
  assert tool_context.state["autopick_enabled"]


def test_disable_autopick():
  tool_context = MagicMock()
  tool_context.state = {
      "autopick_enabled": True,
      "autopick_count": 5,
      "autopick_strategy": "some strategy",
  }
  autopick_agent.disable_autopick(tool_context)
  assert not tool_context.state["autopick_enabled"]
  assert tool_context.state["autopick_count"] is None
  assert tool_context.state["autopick_strategy"] is None


def test_set_autopick_count():
  tool_context = MagicMock()
  tool_context.state = {"autopick_enabled": False}
  autopick_agent.set_autopick_count(5, tool_context)
  assert tool_context.state["autopick_enabled"]
  assert tool_context.state["autopick_count"] == 5


def test_set_autopick_for_all_remaining_picks():
  tool_context = MagicMock()
  tool_context.state = {"autopick_enabled": False, "autopick_count": 5}
  autopick_agent.set_autopick_for_all_remaining_picks(tool_context)
  assert tool_context.state["autopick_enabled"]
  assert tool_context.state["autopick_count"] is None


def test_set_autopick_strategy():
  tool_context = MagicMock()
  tool_context.state = {}
  strategy = "best player available"
  autopick_agent.set_autopick_strategy(strategy, tool_context)
  assert tool_context.state["autopick_strategy"] == strategy
