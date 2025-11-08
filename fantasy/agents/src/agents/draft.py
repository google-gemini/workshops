"""This file contains all the classes that represent the draft state.

The Draft class represents the on-going draft. It contains the draft order,
the player IDs, the season, the scoring type, the rounds, the slots, and the
team needs. This should be eventually also hold the draft state, which will
contain information about the picks and the player stats.
"""

import dataclasses
import datetime
import json
import logging
from typing import Any, Dict, Tuple
from common import constants
from common import enums
from common import utils
import pandas as pd
import sortedcontainers

SortedList = sortedcontainers.SortedList

_TEAM_IDS = frozenset(
    {member.value for member in enums.Teams.__members__.values()}
)


def is_team(player_id: str) -> bool:
  """Returns true if the player ID is a team ID."""
  return player_id in _TEAM_IDS


def pick_no_to_round(pick_no: int, num_teams: int) -> int:
  """Converts a pick number to a round number."""
  return (pick_no - 1) // num_teams + 1  # 1-based indexing


def pick_no_to_pick_no_in_round(pick_no: int, num_teams: int) -> int:
  """Converts a pick number to a pick number in the current round."""
  return ((pick_no - 1) % num_teams) + 1  # 1-based indexing


def pick_no_in_round_to_pick_no(
    pick_no_in_round: int, round_num: int, num_teams: int
) -> int:
  """Converts a pick number in the current round to a pick number."""
  return (round_num - 1) * num_teams + pick_no_in_round


@dataclasses.dataclass
class Team:
  """Represents a team in the draft."""

  name: str
  adp: float
  early_schedule_rank: int
  consensus_projection: float
  ceiling_projection: float
  win_total: float
  pressure_rate: float
  offseason_additions: list[str]

  def __hash__(self) -> int:
    """Makes the object hashable for use in sets and dicts."""
    return hash(self.name)

  def to_minimal_dict(self) -> Dict[str, Any]:
    """Returns a minimal representation of the team."""
    return {"name": self.name}

  def to_full_dict(self) -> Dict[str, Any]:
    """Returns a full representation of the team."""
    return {
        "name": self.name,
        "adp": f"{self.adp:.2f}",
        "early_schedule_rank": self.early_schedule_rank,
        "consensus_projection": f"{self.consensus_projection:.2f}",
        "ceiling_projection": f"{self.ceiling_projection:.2f}",
        "win_total": f"{self.win_total:.2f}",
        "pressure_rate": f"{self.pressure_rate:.2f}",
        "offseason_additions": self.offseason_additions,
    }


@dataclasses.dataclass(eq=False)
class Player:
  """Represents a player in the draft."""

  player_id: str
  name: str
  team: str
  position: str
  adp_type: str
  injury: str
  injury_risk: str
  status: str
  bio: str
  adp: float
  fpts: float
  vols: float = 0.0
  vona: float = 0.0
  vorp: float = 0.0

  def __lt__(self, other: "Player") -> bool:
    """Compares two Player objects for sorting.

    Sorts by fpts (descending). If fpts are tied, it uses the player_id as a
    stable, unique tie-breaker. This creates a true total ordering.

    Args:
      other: The other Player object to compare against.

    Returns:
      True if this player should come before 'other' in a descending sort
      based on fpts, or ascending based on player_id if fpts are equal.
    """
    if self.fpts != other.fpts:
      return self.fpts > other.fpts  # Descending sort by fpts
    return self.player_id < other.player_id

  def __eq__(self, other: "Player") -> bool:
    """Two players are equal if and only if they have the same ID."""
    return self.player_id == other.player_id

  def __hash__(self) -> int:
    """Makes the object hashable for use in sets and dicts."""
    return hash(self.player_id)

  def to_minimal_dict(self) -> Dict[str, Any]:
    """Returns a minimal representation of the player."""
    return {
        "name": self.name,
        "position": self.position,
        "team": self.team,
        "fpts": f"{self.fpts:.2f}",
        "injury_risk": self.injury_risk,
    }

  def to_full_dict(self) -> Dict[str, Any]:
    """Returns a full representation of the player."""
    player_data = {
        "name": self.name,
        "team": self.team,
        "status": f"{self.status} (Injury: {self.injury})",
        "injury_risk": self.injury_risk,
        "fpts": f"{self.fpts:.2f}",
        "vona": f"{self.vona:.2f}",
        "vols": f"{self.vols:.2f}",
        "vorp": f"{self.vorp:.2f}",
    }

    if self.adp:
      player_data["adp"] = f"{self.adp:.2f} ({self.adp_type})"

    return player_data


class TeamRoster:
  """Represents an individual's roster for a draft.

  All positions are uppercase ("WR", "TE", "RB", "QB", "K", "FLEX", "DEF", "BN")
  """

  def __init__(self, slots: dict[str, int], superflex: bool = False):
    self.slots = slots.copy()
    self.roster: dict[str, list[Player | Team]] = {
        pos: [] for pos in (*self.slots, "BN")
    }

    self.flex_eligible = ["TE", "WR", "RB"] + (["QB"] if superflex else [])

  def update(self, entity: Player | Team) -> None:
    """Greedily updates the team needs for a given position."""

    def _add_entity_to_roster(slot_key: str) -> None:
      """Helper function to add an entity to a specific slot."""
      self.slots[slot_key] -= 1
      self.roster[slot_key].append(entity)

    if isinstance(entity, Team):
      if self.slots.get("DEF", 0) > 0:
        _add_entity_to_roster("DEF")
        return
      raise ValueError("No available slots for defense.")

    pos = entity.position.upper().strip()
    for slot in self.slots:
      if slot == pos and self.slots[slot] > 0:
        _add_entity_to_roster(slot)
        return

    if self.slots.get("FLEX", 0) > 0 and pos in self.flex_eligible:
      _add_entity_to_roster("FLEX")
      return

    if self.slots.get("BN", 0) > 0:
      _add_entity_to_roster("BN")
      return

    logging.warning(
        "No available slots for player %s in position %s.",
        entity.name,
        entity.position,
    )

  def undo_update(self, entity: Player | Team) -> None:
    """Reverts the addition of a player or team to the roster."""

    def _attempt_removal(slot_key: str, entity: Player | Team) -> bool:
      """Helper function to attempt removing an entity from a specific slot."""
      if slot_key in self.roster and entity in self.roster.get(slot_key, []):
        self.roster[slot_key].remove(entity)
        if slot_key in self.slots:
          self.slots[slot_key] += 1
        return True
      return False

    if isinstance(entity, Team):
      if _attempt_removal("DEF", entity):
        return
      raise ValueError(f"Team {entity.name} not found on roster in DEF slot.")

    if _attempt_removal("BN", entity):
      return

    pos = entity.position.upper().strip()

    if pos in self.flex_eligible and _attempt_removal("FLEX", entity):
      return

    if _attempt_removal(pos, entity):
      return

    raise ValueError(f"Player {entity.name} not found on roster for undo.")


class League:
  """Represents a league."""

  def __init__(
      self, league_data: dict[str, Any], users_data: list[dict[str, Any]]
  ):
    self.league_id = league_data["league_id"]
    self.name = league_data["name"]

    self.user_id_to_team_name: dict[str, str] = {}
    for user_data in users_data:
      user_id = user_data["user_id"]
      user_name = user_data.get(
          "display_name", user_data.get("username", user_id)
      )
      metadata = user_data.get("metadata", {})
      team_name = metadata.get("team_name", user_name)
      self.user_id_to_team_name[user_id] = team_name


class Draft:
  """Represents an on-going draft."""

  def __init__(
      self,
      data: dict[str, Any],
      player_id: str,
      superflex: bool = False,
      year: int | None = None,
  ):
    # Assumes that draft order is already assigned.
    self.draft_order: dict[str, int] = data["draft_order"]  # 1-based indexing
    initial_player_ids = list(self.draft_order.keys())

    self.draft_order_type = data["type"]
    if self.draft_order_type not in ["linear", "snake"]:
      raise ValueError(f"Unsupported draft order type: {self.draft_order_type}")

    scoring_map = {"std": "standard"}
    raw_type = data["metadata"]["scoring_type"].lower()
    self.scoring_type = scoring_map.get(raw_type, raw_type)
    self.game_modes = constants.GAME_MODES
    if self.scoring_type not in self.game_modes:
      raise ValueError(f"Unsupported scoring type: {self.scoring_type}")

    settings = data["settings"]
    self.num_rounds = settings.get("rounds")
    self.num_teams = settings.get("teams") or len(initial_player_ids)

    num_bots = self.num_teams - len(initial_player_ids)
    if num_bots > 0:
      occupied_positions = set(self.draft_order.values())
      available_positions = sorted(
          list(set(range(1, self.num_teams + 1)) - occupied_positions)
      )

      for i in range(num_bots):
        draft_position = available_positions[i]
        bot_id = f"Team {draft_position}"
        self.draft_order[bot_id] = draft_position

      self.player_ids = [
          pid
          for pid, _ in sorted(
              self.draft_order.items(), key=lambda item: item[1]
          )
      ]
    else:
      self.player_ids = initial_player_ids

    self.slots = {
        key.replace("slots_", "").upper(): value
        for key, value in settings.items()
        if key.startswith("slots_")
    }

    self.superflex = superflex
    self.my_player_id = str(player_id)
    self.year = year or datetime.datetime.now().year

    self.player_id_to_player = {}
    self.team_id_to_team = {}

  def initialize(self) -> None:
    """Converts SQLite tables to in-memory representations of players and teams."""
    conn = utils.connect_to_sqlite()
    players_df = utils.read_df_from_sqlite(
        conn, constants.PLAYER_DATA_TABLE_NAME
    )
    teams_df = utils.read_df_from_sqlite(
        conn, constants.TEAM_DEFENSE_TABLE_NAME
    )
    utils.close_sqlite_connection(conn)

    if players_df is None or players_df.empty:
      raise ValueError("No player data found in SQLite database.")
    if teams_df is None or teams_df.empty:
      raise ValueError("No team data found in SQLite database.")

    players_df = self.filter_player_data_df(players_df)
    self.df_to_players(players_df)
    self.df_to_teams(teams_df)

  def _get_scoring_match(self, scoring_type) -> float:
    if pd.isna(scoring_type):
      return -float("inf")

    if scoring_type == self.scoring_type:
      return 1.0
    elif scoring_type == "half-ppr":
      return 0.5  # Prioritize half-ppr, it's closer to our scoring type
    elif scoring_type == "ppr" and self.scoring_type == "half-ppr":
      return 0.25  # Prioritize ppr over standard, since it considers receptions
    else:
      return 0.0

  def _get_team_match(self, team_count) -> float:
    if pd.isna(team_count):
      return -float("inf")

    if team_count == self.num_teams:
      return 2.0
    elif team_count > self.num_teams:
      return 1 / (team_count - self.num_teams)
    else:  # team_count < our_team_count
      return team_count - self.num_teams

  def filter_player_data_df(self, df: pd.DataFrame) -> pd.DataFrame:
    """Filters the player data DataFrame to the current draft."""
    parsed_df = df.copy()
    parsed_df["fpts"] = parsed_df["fpts"].apply(
        lambda x: 0 if pd.isna(x) else json.loads(x).get(self.scoring_type, 0)
    )
    parsed_cols = parsed_df["type"].str.split("_", expand=True)

    parsed_df["parsed_team_count"] = pd.to_numeric(
        parsed_cols.get(1, pd.Series(dtype="object")), errors="coerce"
    )
    parsed_df["parsed_scoring_type"] = parsed_cols.get(
        2, pd.Series(dtype="object")
    ).reindex(parsed_df.index)

    parsed_df["scoring_match"] = parsed_df["parsed_scoring_type"].apply(
        self._get_scoring_match
    )
    parsed_df["team_match"] = parsed_df["parsed_team_count"].apply(
        self._get_team_match
    )

    parsed_df.sort_values(
        by=["player_id", "scoring_match", "team_match"],
        ascending=[True, False, False],
        inplace=True,
    )

    best_entries_df = parsed_df.drop_duplicates(
        subset=["player_id"], keep="first"
    )

    return best_entries_df.drop(
        columns=[
            "parsed_team_count",
            "parsed_scoring_type",
            "scoring_match",
            "team_match",
        ]
    )

  def df_to_players(self, df: pd.DataFrame) -> None:
    """Converts a DataFrame of player data to a list of Player objects."""
    for row in df.itertuples():
      player = Player(
          player_id=row.player_id,
          name=row.name,
          team=row.team,
          position=row.position,
          adp_type="" if pd.isna(row.type) else row.type.replace("_", " "),
          injury=row.injury,
          injury_risk=row.injury_risk,
          status=row.status,
          bio=row.bio,
          adp=row.adp,
          fpts=row.fpts,
      )
      self.player_id_to_player[player.player_id] = player

  def df_to_teams(self, df: pd.DataFrame) -> None:
    """Converts a DataFrame of team data to a list of Team objects."""
    for row in df.itertuples():
      team = Team(
          name=row.team_name,
          adp=row.adp,
          early_schedule_rank=row.early_schedule_rank,
          consensus_projection=row.consensus_projection,
          ceiling_projection=row.ceiling_projection,
          win_total=row.win_total,
          pressure_rate=row.pressure_rate,
          offseason_additions=row.offseason_additions,
      )
      self.team_id_to_team[team.name] = team


class State:
  """Represents the current state of the draft."""

  def __init__(
      self,
      draft: Draft,
  ):
    self.draft = draft
    self.pick_no = 0

    self.drafted_team_names: set[str] = set()
    self.player_id_to_team_roster: dict[str, TeamRoster] = {}
    self.player_id_to_picks: dict[str, set[Player | Team]] = {}
    for player_id in self.draft.player_ids:
      self.player_id_to_picks[player_id] = set()
      self.player_id_to_team_roster[player_id] = TeamRoster(
          self.draft.slots, self.draft.superflex
      )

    self._fpts_available: dict[str, SortedList] = {}
    for player in self.draft.player_id_to_player.values():
      if player.position not in self._fpts_available:
        self._fpts_available[player.position] = SortedList()
      self._fpts_available[player.position].add(player)

    self.calculate_user_vbd_metrics()

  @property
  def current_round(self) -> int:
    """Derives the current round number from the last completed pick."""
    return pick_no_to_round(self.pick_no, self.draft.num_teams)

  @property
  def next_pick_number(self) -> int:
    """The number of the pick that is about to happen."""
    return self.pick_no + 1

  @property
  def next_pick_round(self) -> int:
    """The round number of the pick that is about to happen."""
    return pick_no_to_round(self.next_pick_number, self.draft.num_teams)

  def _get_pick_context(
      self, pick_data: dict[str, Any]
  ) -> Tuple[Player | Team, str]:
    """Helper to find the entity and picker for a given pick."""
    picked_entity_id = pick_data["player_id"]
    pick_number = pick_data["pick_no"]
    picked_by = pick_data["picked_by"]

    if not picked_by:  # Bot account
      round_num = pick_data["round"]
      pick_in_round_idx = (pick_number - 1) % self.draft.num_teams
      if (
          self.draft.draft_order_type == "snake" and round_num % 2 == 0
      ):  # Reverse order
        picker_index = self.draft.num_teams - 1 - pick_in_round_idx
      else:
        picker_index = pick_in_round_idx
      picked_by = self.draft.player_ids[picker_index]

    if is_team(picked_entity_id):
      picked_entity: Team = self.draft.team_id_to_team[picked_entity_id]
    else:
      picked_entity: Player = self.draft.player_id_to_player[picked_entity_id]

    return picked_entity, picked_by

  def process_pick(self, pick_data: dict[str, Any]) -> None:
    """Handles the state after a pick is made.

    Args:
      pick_data: A dictionary containing the details of the pick to process,
        including "player_id", "picked_by", "pick_no", and "round".
    """
    self.pick_no = max(self.pick_no, pick_data["pick_no"])
    picked_entity, picked_by = self._get_pick_context(pick_data)

    if isinstance(picked_entity, Team):
      if picked_entity.name not in self.drafted_team_names:
        self.drafted_team_names.add(picked_entity.name)
    elif isinstance(picked_entity, Player):
      if picked_entity in self._fpts_available[picked_entity.position]:
        self._fpts_available[picked_entity.position].remove(picked_entity)
        self.calculate_user_vbd_metrics(picked_entity.position)

    self.player_id_to_team_roster[picked_by].update(picked_entity)
    self.player_id_to_picks[picked_by].add(picked_entity)

  def undo_pick(self, pick_data: dict[str, Any]) -> None:
    """Reverts the state change from a pick. Keeps the pick_no the same.

    Args:
      pick_data: A dictionary containing the details of the pick to undo,
        including "player_id", "picked_by", "pick_no", and "round".
    """
    picked_entity, picked_by = self._get_pick_context(pick_data)
    if isinstance(picked_entity, Team):
      if picked_entity.name in self.drafted_team_names:
        self.drafted_team_names.remove(picked_entity.name)
    elif isinstance(picked_entity, Player):
      if picked_entity not in self._fpts_available[picked_entity.position]:
        self._fpts_available[picked_entity.position].add(picked_entity)
        self.calculate_user_vbd_metrics(picked_entity.position)

    self.player_id_to_team_roster[picked_by].undo_update(picked_entity)
    self.player_id_to_picks[picked_by].remove(picked_entity)

  def picks_till_my_next_turn(self, pick_no: int) -> Tuple[int, bool]:
    """Returns (picks_until_next_turn, is_my_turn_now) based on a given pick number.

    Args:
        pick_no: The pick number (1-based) to calculate from. This is the
          "current pick" for the context of the calculation.
    """
    if pick_no < 0:
      raise ValueError(f"Invalid pick number: {pick_no}")

    my_draft_position = self.draft.draft_order[self.draft.my_player_id]
    if pick_no == 0:
      return (my_draft_position - 1, my_draft_position == 1)

    num_teams = self.draft.num_teams
    current_pick_in_round = pick_no_to_pick_no_in_round(pick_no, num_teams)

    if self.draft.draft_order_type == "linear":
      if current_pick_in_round < my_draft_position:
        return (my_draft_position - current_pick_in_round, False)
      else:
        return (
            num_teams - current_pick_in_round + my_draft_position,
            current_pick_in_round == my_draft_position,
        )

    elif self.draft.draft_order_type == "snake":
      current_round = pick_no_to_round(pick_no, num_teams)
      if current_round % 2 == 1:
        my_position_in_current_round = my_draft_position
      else:
        my_position_in_current_round = num_teams - my_draft_position + 1

      if (current_round + 1) % 2 == 1:
        my_position_in_next_round = my_draft_position
      else:
        my_position_in_next_round = num_teams - my_draft_position + 1

      # Case 1: My turn is still in this round
      if current_pick_in_round < my_position_in_current_round:
        return (my_position_in_current_round - current_pick_in_round, False)

      # Case 2: My turn has already passed in this round
      else:
        picks_left_in_this_round = num_teams - current_pick_in_round
        return (
            picks_left_in_this_round + my_position_in_next_round,
            current_pick_in_round == my_position_in_current_round,
        )

  def calculate_user_vbd_metrics(self, position: str | None = None) -> None:
    """Calculates player's VBD metrics from the user's perspective."""
    positions = [position] if position else constants.OFFENSIVE_POSITIONS
    picks_till_my_next_turn = self.picks_till_my_next_turn(
        self.next_pick_number
    )[0]

    for position in positions:
      available_players = self._fpts_available.get(position)
      if available_players:
        picks_left_for_position = sum(
            tn.slots.get(position, 0)
            for tn in self.player_id_to_team_roster.values()
        )

        na_fpts = (
            available_players[picks_till_my_next_turn].fpts
            if 0 <= picks_till_my_next_turn < len(available_players)
            else 0
        )
        ls_fpts = (
            available_players[picks_left_for_position - 1].fpts
            if 0 <= (picks_left_for_position - 1) < len(available_players)
            else 0
        )
        rp_fpts = (
            available_players[picks_left_for_position].fpts
            if 0 <= picks_left_for_position < len(available_players)
            else 0
        )

        for player in available_players:
          player.vona = player.fpts - na_fpts
          player.vols = player.fpts - ls_fpts
          player.vorp = player.fpts - rp_fpts

  def get_draft_data(self) -> Dict[str, Any]:
    """Generates a dictionary containing the current state of the draft."""
    # Draft position
    pick_in_round = pick_no_to_pick_no_in_round(
        self.next_pick_number,
        self.draft.num_teams,
    )
    current_draft_position = f"{self.next_pick_round}.{pick_in_round}"

    # Roster and slots left
    my_team_roster = self.player_id_to_team_roster[self.draft.my_player_id]
    roster_dict = {
        position: [entity.to_minimal_dict() for entity in entities]
        for position, entities in my_team_roster.roster.items()
    }
    slots_left = {
        key: value for key, value in my_team_roster.slots.items() if value > 0
    }

    # Available players and teams
    available_players = {
        position: [player.to_full_dict() for player in players[:10]]
        for position, players in self._fpts_available.items()
    }
    available_teams = {
        team_name: team.to_full_dict()
        for team_name, team in self.draft.team_id_to_team.items()
        if team_name not in self.drafted_team_names
    }

    return {
        "superflex": self.draft.superflex,
        "current_draft_position": current_draft_position,
        "slots_left": slots_left,
        "roster": roster_dict,
        "available_players": available_players,
        "available_teams": available_teams,
    }
