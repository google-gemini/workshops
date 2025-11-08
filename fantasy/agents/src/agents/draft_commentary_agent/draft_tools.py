"""Non-pick-stream-related tools for a draft commentary agent.

This Python file provides all the non-streaming support tools for a draft
commentary agent. It includes functions to fetch team and player data, which the
agent uses for context. It also has a mechanism to track the auto-pick status
for accurate commentary. Essential for presentation, it manages sound effects
and retrieves the overall draft structure (like rules and rounds). Finally, it
contains the necessary function to stop the commentary stream. Essentially, this
file is the agent's core support and control module, separate from the real-time
pick processing.
"""

import asyncio
from functools import lru_cache
import re
from typing import Any, AsyncGenerator, Optional, Tuple

from common import constants
from common import enums
from common import utils
from google.adk import tools
import pandas as pd
from rapidfuzz import fuzz
from rapidfuzz import process


draft_structure: Optional[str] = None
SOUND_EFFECTS = frozenset(
    {member.value for member in enums.SoundEffects.__members__.values()}
)


@lru_cache(maxsize=None)
def _load_df(table_name: str, index_column: str) -> pd.DataFrame:
  """Loads and caches a dataframe from a SQLite database.

  Args:
    table_name (str): The name of the table to load.
    index_column (str): The name of the column to use as the index.

  Returns:
    A dataframe containing the data from the SQLite database.
  """
  conn = utils.connect_to_sqlite()
  df = utils.read_df_from_sqlite(conn, table_name)
  utils.close_sqlite_connection(conn)
  if df is None or df.empty:
    raise ValueError(f"No data found in SQLite database for {table_name}.")
  df.set_index(index_column, inplace=True)
  return df


def get_player_id_fuzzy_search(
    player_name: str,
    position: Optional[str],
    team_abbreviation: Optional[str],
    threshold: float = 15.0,
) -> Tuple[str, str]:
  """Finds the closest matching player for a given name and returns their ID.

  Use this tool when you have a player's name but need their unique 'player_id'
  to use other tools like 'get_player_info'. It uses the optional parameters
  position and team as tie-breakers for players with similar names.

  Args:
      player_name (str): The full name of the player to search for. Handles
        minor misspellings.
      position (str, optional): The position abbreviation of the player ('K',
        'RB', 'QB', 'TE', 'WR')
      team_abbreviation (str, optional): The team abbreviation of the player's
        professional team ('ARI', 'ATL', 'BAL', 'BUF', 'CAR', 'CHI', 'CIN',
        'CLE', 'DAL', 'DEN', 'DET', 'GB', 'HOU', 'IND', 'JAX', 'KC', 'LV',
        'LAC', 'LAR', 'MIA', 'MIN', 'NE', 'NO', 'NYG', 'NYJ', 'PHI', 'PIT',
        'SF', 'SEA', 'TB', 'TEN', 'WAS')

  Returns:
      tuple[str, str]: The unique player_id (e.g., '1047') of the best matching
      player and the player's name as it appears in the database.
  """
  df = _load_df(constants.PLAYER_DATA_TABLE_NAME, constants.PLAYER_ID_COLUMN)

  best_matches = process.extract(
      query=player_name, choices=df["name"], scorer=fuzz.WRatio, limit=10
  )
  if not best_matches:
    raise ValueError(f"No player found matching the name '{player_name}'.")

  top_score = best_matches[0][1]
  top_candidates = [
      match for match in best_matches if top_score - match[1] <= threshold
  ]

  if len(top_candidates) == 1:
    best_candidate_name = top_candidates[0][0]
  else:
    candidate_names = [name for name, _, _ in top_candidates]
    candidate_df = df[df["name"].isin(candidate_names)]
    initial_check = re.match(r"^(\w)\.", player_name)
    candidate_scores = {name: score for name, score, _ in top_candidates}

    def get_tie_break_score(candidate_name: str) -> float:
      player_row = candidate_df[candidate_df["name"] == candidate_name].iloc[0]
      score = candidate_scores[candidate_name] / 100.0
      if initial_check and candidate_name.upper().startswith(
          initial_check.group(1).upper()
      ):
        score += 1.5
      if position and player_row["position"] == position:
        score += 1
      if team_abbreviation and player_row["team"] == team_abbreviation:
        score += 1
      return score

    best_candidate_name = max(candidate_names, key=get_tie_break_score)

  player_id = str(df[df["name"] == best_candidate_name].index[0])
  return player_id, best_candidate_name


def get_player_info(player_id: str) -> Optional[dict[str, Any]]:
  """Retrieves detailed statistics and information for a specific player.

  Args:
    player_id (str): The unique numerical identifier for the player.

  Returns:
    dict[str, Any]: A dictionary containing the player's information, such as
    name, team, position, biography, projections, and injury risks, or None if
    the player is not found.
  """
  df = _load_df(constants.PLAYER_DATA_TABLE_NAME, constants.PLAYER_ID_COLUMN)
  if player_id not in df.index:
    return None
  player_info = df.loc[player_id].drop(labels=["adp", "type"], errors="ignore")
  return player_info.to_dict()


def get_team_info(team_abbreviation: str) -> dict[str, Any]:
  """Retrieves defensive projections and information for a specific NFL team.

  Args:
    team_abbreviation (str): The team's abbreviation (ARI, ATL, BAL, BUF, CAR,
      CHI, CIN, CLE, DAL, DEN, DET, GB, HOU, IND, JAX, KC, LV, LAC, LAR, MIA,
      MIN, NE, NO, NYG, NYJ, PHI, PIT, SF, SEA, TB, TEN, WAS)

  Returns:
    dict[str, Any]: A dictionary containing a team's defensive information, such
      as team name, average draft position (ADP), early schedule rank,
      consensus/floor/ceiling projections, projected wins, pressure rate, and
      offseason additions.
  """
  df = _load_df(constants.TEAM_DEFENSE_TABLE_NAME, constants.TEAM_NAME_COLUMN)
  team_info = df.loc[team_abbreviation.upper().strip()]
  return team_info.to_dict()


def get_draft_structure(tool_context: tools.tool_context.ToolContext) -> str:
  """Fetches the static configuration for the draft.

  Returns:
      (str): A string representation of the draft settings and structure,
             including details like pick time, draft status, round count, and
             draft type.
  """
  global draft_structure
  if not draft_structure:
    draft_id = tool_context.state.get("draft_id")
    if not draft_id:
      raise ValueError("Draft ID is not set.")
    draft_structure = str(
        utils.make_request(f"{constants.SLEEPER_API_BASE_URL}/draft/{draft_id}")
    )

  return draft_structure


async def monitor_autopick(
    tool_context: tools.tool_context.ToolContext,
) -> AsyncGenerator[str, None]:
  """A continuous monitor that manages the autopick process.

  This function runs as a background process. When autopick is enabled,
  it periodically triggers based on the current configuration.

  Yields:
    A message (str) instructing the system to make a pick. If a strategy
    has been set, the message will specify the strategy to be used.
  """
  last_autopick_pick_no = 0

  while True:
    current_pick_no = tool_context.state.get("pick_no", 0)
    if (
        tool_context.state.get("autopick_enabled")
        and tool_context.state.get("is_my_turn", False)
        and current_pick_no > last_autopick_pick_no
    ):
      if tool_context.state.get("autopick_count") is not None:
        tool_context.state["autopick_count"] -= 1
        if tool_context.state.get("autopick_count") <= 0:
          tool_context.state["autopick_enabled"] = False

      prompt_text = "Please recommend a single pick."
      if tool_context.state.get("autopick_strategy"):
        prompt_text += "Use the following strategy: " + tool_context.state.get(
            "autopick_strategy"
        )

      last_autopick_pick_no = current_pick_no
      yield prompt_text

    await asyncio.sleep(0.5)


def stop_streaming(function_name: str) -> None:  # pylint: disable=unused-argument
  """Stop a long-running streaming tool.

  Args:
    function_name (str): The name of the streaming function to stop.
  """
  pass


# TODO: Use enums.SoundEffects once supported by ADK.
def play_sound_effect(
    sound_effect: str,
    tool_context: tools.tool_context.ToolContext,
) -> None:
  """Plays a sound effect for the user.

  Args:
    sound_effect (str): The sound effect to play ('chime', 'applause', 'intro',
      'boo', 'gasp')
  """
  if "sound_effects" not in tool_context.state:
    tool_context.state["sound_effects"] = []

  if sound_effect in SOUND_EFFECTS:
    tool_context.state["sound_effects"].append(sound_effect)
