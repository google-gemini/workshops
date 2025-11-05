from unittest.mock import MagicMock, patch
import pandas as pd
import pytest
from src.agents.draft_commentary_agent import draft_tools


@pytest.fixture
def mock_player_df():
  return pd.DataFrame({
      "player_id": ["1", "2", "3", "4", "5"],
      "name": [
          "Travis Kelce",
          "Travis Etienne",
          "Joe Mixon",
          "T.J. Watt",
          "T.J. Hockenson",
      ],
      "position": ["TE", "RB", "RB", "LB", "TE"],
      "team": ["KC", "JAX", "CIN", "PIT", "MIN"],
      "adp": [1.1, 2.2, 3.3, 4.4, 5.5],
      "type": [
          "2025_12_ppr",
          "2025_12_ppr",
          "2025_12_ppr",
          "2025_12_ppr",
          "2025_12_ppr",
      ],
  }).set_index("player_id")


@patch("src.agents.draft_commentary_agent.draft_tools._load_df")
def test_get_player_id_fuzzy_search(mock_load_df, mock_player_df):
  mock_load_df.return_value = mock_player_df

  player_id, player_name = draft_tools.get_player_id_fuzzy_search(
      player_name="Travis Kelce", position=None, team_abbreviation=None
  )
  assert player_id == "1"
  assert player_name == "Travis Kelce"

  # Test with tie-breaker by position
  player_id, player_name = draft_tools.get_player_id_fuzzy_search(
      player_name="Travis", position="RB", team_abbreviation=None
  )
  assert player_id == "2"
  assert player_name == "Travis Etienne"

  # Test with tie-breaker by initial
  player_id, player_name = draft_tools.get_player_id_fuzzy_search(
      player_name="T. Hockenson", position="TE", team_abbreviation="MIN"
  )
  assert player_id == "5"
  assert player_name == "T.J. Hockenson"

  # Test with misspelling
  player_id, player_name = draft_tools.get_player_id_fuzzy_search(
      player_name="Travis Kelc", position=None, team_abbreviation=None
  )
  assert player_id == "1"
  assert player_name == "Travis Kelce"


@patch("src.agents.draft_commentary_agent.draft_tools._load_df")
def test_get_player_info(mock_load_df, mock_player_df):
  mock_player_df["bio"] = ""
  mock_player_df["injury"] = ""
  mock_player_df["injury_risk"] = ""
  mock_player_df["status"] = ""
  mock_player_df["fpts"] = 0.0

  mock_load_df.return_value = mock_player_df
  info = draft_tools.get_player_info("1")
  assert info["name"] == "Travis Kelce"
  assert "adp" not in info
  assert "type" not in info


@pytest.fixture
def mock_team_df():
  return pd.DataFrame({
      "team_name": ["KC", "JAX"],
      "adp": [1, 2],
      "early_schedule_rank": [1, 2],
      "consensus_projection": [1, 2],
      "ceiling_projection": [1, 2],
      "win_total": [1, 2],
      "pressure_rate": [1, 2],
      "offseason_additions": [[], []],
  }).set_index("team_name")


@patch("src.agents.draft_commentary_agent.draft_tools._load_df")
def test_get_team_info(mock_load_df, mock_team_df):
  mock_load_df.return_value = mock_team_df
  info = draft_tools.get_team_info("KC")
  assert info["adp"] == 1


def test_play_sound_effect():
  tool_context = MagicMock()
  tool_context.state = {}
  draft_tools.play_sound_effect("chime", tool_context)
  assert "chime" in tool_context.state["sound_effects"]
  draft_tools.play_sound_effect("bad_sound", tool_context)
  assert "bad_sound" not in tool_context.state["sound_effects"]
