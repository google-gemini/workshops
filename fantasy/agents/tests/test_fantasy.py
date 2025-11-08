from unittest.mock import AsyncMock, MagicMock

import pytest
from src.agents import draft
from src.agents import fantasy


@pytest.fixture
def mock_connection():
  """Provides a mock connection object for testing."""
  conn = MagicMock()
  conn.user_id = "test_user"
  conn.draft_id = "test_draft"
  conn.league_id = "test_league"
  conn.superflex = False
  conn.upload_artifact = AsyncMock()
  conn.update_state = AsyncMock()
  conn.session = MagicMock()
  conn.session.state.get.return_value = []
  return conn


@pytest.mark.asyncio
async def test_add_speculative_pick(mock_connection):
  """Tests adding a speculative pick to the DraftManager."""
  draft_manager = fantasy.DraftManager(mock_connection)

  draft_manager.state_obj = MagicMock(spec=draft.State)
  draft_manager.draft_obj = MagicMock(spec=draft.Draft)
  draft_manager.state_obj.get_draft_data.return_value = {}
  draft_manager.state_obj.picks_till_my_next_turn.return_value = (1, True)

  # Configure mocks
  draft_manager.state_obj.round = 2
  draft_manager.state_obj.pick_no = 15
  draft_manager.draft_obj.num_teams = 12

  pick_data = {"round": "1", "pick_no": "1", "player_id": "123"}

  # Test adding a stale pick by round
  await draft_manager.add_speculative_pick(pick_data)
  draft_manager.state_obj.process_pick.assert_not_called()

  # Test adding a stale pick by pick_no
  draft_manager.state_obj.round = 1
  draft_manager.state_obj.pick_no = 2
  pick_data_stale_pick_no = {"round": "1", "pick_no": "2", "player_id": "123"}
  await draft_manager.add_speculative_pick(pick_data_stale_pick_no)
  draft_manager.state_obj.process_pick.assert_not_called()

  # Test adding a valid pick
  draft_manager.state_obj.round = 1
  draft_manager.state_obj.pick_no = 1
  pick_data_valid = {"round": "1", "pick_no": "2", "player_id": "456"}
  await draft_manager.add_speculative_pick(pick_data_valid)

  draft_manager.state_obj.process_pick.assert_called_once()
  call_args = draft_manager.state_obj.process_pick.call_args[0][0]
  assert call_args["pick_no"] == 2

  assert 2 in draft_manager.speculative_picks
  assert draft_manager.speculative_picks[2]["player_id"] == "456"

  # Test adding a duplicate speculative pick
  draft_manager.state_obj.process_pick.reset_mock()
  await draft_manager.add_speculative_pick(pick_data_valid)
  draft_manager.state_obj.process_pick.assert_not_called()
