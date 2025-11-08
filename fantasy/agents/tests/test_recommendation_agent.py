from unittest.mock import AsyncMock, MagicMock

import pytest
from src.agents.recommendation_agent import agent as recommendation_agent


@pytest.mark.asyncio
async def test_get_draft_data():
  tool_context = MagicMock()
  tool_context.state = {"draft_data_file_name": "draft.json"}

  mock_artifact = MagicMock()
  mock_artifact.inline_data.data = '{"round": 1}'.encode("utf-8")
  tool_context.load_artifact = AsyncMock(return_value=mock_artifact)

  data = await recommendation_agent.get_draft_data(tool_context)
  assert "<draft_data>" in data
  assert '{"round": 1}' in data


@pytest.mark.asyncio
async def test_get_draft_data_no_file_name():
  tool_context = MagicMock()
  tool_context.state = {}
  with pytest.raises(
      ValueError, match="No draft data file name found in state."
  ):
    await recommendation_agent.get_draft_data(tool_context)


@pytest.mark.asyncio
async def test_get_draft_data_no_artifact():
  tool_context = MagicMock()
  tool_context.state = {"draft_data_file_name": "draft.json"}
  tool_context.load_artifact = AsyncMock(return_value=None)

  with pytest.raises(
      ValueError, match="No draft data found in latest state artifact"
  ):
    await recommendation_agent.get_draft_data(tool_context)
