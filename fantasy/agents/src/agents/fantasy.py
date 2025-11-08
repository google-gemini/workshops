"""Manages the lifecycle and real-time state of a fantasy football draft session.

This module contains the DraftManager class, which is responsible for handling
all aspects of a single fantasy draft on behalf of a user connected to the
server. Upon initialization, it fetches the complete draft, league, and user
details from the Sleeper API to build an initial state model. During an active
draft, it runs a continuous asynchronous poller to detect new picks in
real-time. When a pick is detected, the DraftManager updates its internal state,
saves the new draft board as a JSON artifact for the agent's context and updates
the agent's session state (e.g., `is_my_turn`).
"""

import asyncio
import json
import logging
from typing import Any, Dict, List
import aiohttp
from common import constants
from common import utils
from google.genai import types
from . import draft
from . import sleeper_poller


class DraftManager:
  """Manages the state and API polling for a single fantasy draft."""

  def __init__(self, connection):
    self.connection = connection
    self.user_id = connection.user_id
    self.draft_id = connection.draft_id
    self.league_id = connection.league_id
    self.superflex = connection.superflex

    self.state_obj: draft.State | None = None
    self.league_obj: draft.League | None = None
    self.draft_obj: draft.Draft | None = None
    self.event_queue: asyncio.Queue = asyncio.Queue()
    self.speculative_picks: Dict[int, Dict[str, Any]] = (
        {}
    )  # {pick_no: pick_data}

  async def initialize(self) -> None:
    """Perform asynchronous setup like fetching initial draft data."""
    logging.info("🏈 Initializing DraftManager for user %s...", self.user_id)
    async with aiohttp.ClientSession() as session:
      league_data = await utils.make_async_request(
          f"/league/{self.league_id}", session
      )
      league_users = await utils.make_async_request(
          f"/league/{self.league_id}/users", session
      )
      self.league_obj = draft.League(league_data, league_users)

      draft_data = await utils.make_async_request(
          f"/draft/{self.draft_id}", session
      )
      self.draft_obj = draft.Draft(
          draft_data,
          self.user_id,
          self.superflex,
      )
      team_names = [
          self.league_obj.user_id_to_team_name.get(pid, pid)
          for pid in self.draft_obj.draft_order.keys()
      ]
      await self.connection.update_state(
          "add_team_names",
          {"team_names": team_names},
      )
      self.draft_obj.initialize()
      self.state_obj = draft.State(self.draft_obj)

      logging.info(
          "✅ DraftManager initialized successfully for user %s.", self.user_id
      )

      await self._update_adk_state_and_artifact()

  async def _update_adk_state_and_artifact(self) -> None:
    """Uploads the current draft state as an artifact and updates the session state."""
    if not self.state_obj:
      return

    # 1. Upload the draft data artifact to ADK
    draft_data = self.state_obj.get_draft_data()
    artifact_part = types.Part.from_bytes(
        data=json.dumps(draft_data).encode("utf-8"),
        mime_type="application/json",
    )
    await self.connection.upload_artifact(
        artifact_part, constants.DRAFT_DATA_FILE_NAME
    )

    # 2. Update the 'is_my_turn' and 'pick_no' flags in the ADK session state
    # Since the pick has been made yet, the current pick is the next one.
    is_my_turn = self.state_obj.picks_till_my_next_turn(
        self.state_obj.next_pick_number
    )[1]
    await self.connection.update_state(
        invocation_id="pick_state_update",
        state_delta={
            "is_my_turn": is_my_turn,
            "pick_no": self.state_obj.next_pick_number,
        },
    )

  async def add_speculative_pick(self, pick_data: Dict[str, Any]):
    """Adds a speculative pick to the state from a non-poller source like vision."""
    if not self.state_obj or not self.draft_obj:
      return

    # Convert external per-round picks (Vision) to internal overall picks.
    pick_no_in_round = int(pick_data["pick_no"])
    round_num = int(pick_data["round"])
    pick_no = draft.pick_no_in_round_to_pick_no(
        pick_no_in_round, round_num, self.draft_obj.num_teams
    )

    if (
        pick_no > self.state_obj.pick_no
        and pick_no not in self.speculative_picks
    ):
      pick_data["pick_no"] = pick_no
      logging.info(
          "Adding speculative pick %s for user %s: %s",
          pick_no,
          self.user_id,
          pick_data,
      )
      self.speculative_picks[pick_no] = pick_data
      self.state_obj.process_pick(pick_data)
      await self._update_adk_state_and_artifact()

  async def _handle_speculative_correction(
      self, pick_data: Dict[str, Any]
  ) -> bool:
    """Checks a new pick against speculative picks and handles corrections.

    Args:
        pick_data: A dictionary containing the details of the new pick from the
          poller.

    Returns:
        bool: True if the pick is a new pick, False otherwise.
    """
    if not self.draft_obj or not self.state_obj:
      return False

    pick_no = pick_data["pick_no"]  # This is the overall pick number.
    if pick_no not in self.speculative_picks:
      return True

    speculative_pick = self.speculative_picks.get(pick_data["pick_no"])
    if speculative_pick["player_id"] == pick_data["player_id"]:
      logging.info(
          "Speculative pick %s confirmed by poller for user %s.",
          pick_no,
          self.user_id,
      )
      del self.speculative_picks[pick_no]
      return False

    pick_no_in_round = draft.pick_no_to_pick_no_in_round(
        pick_no, self.draft_obj.num_teams
    )
    pick_data["pick_no"] = pick_no_in_round
    pick_data["wrongly_announced_player"] = speculative_pick["player_name"]

    self.state_obj.undo_pick(speculative_pick)
    self.connection.add_to_state_array(
        "add_corrected_vision_pick",
        "corrected_vision_picks",
        [pick_data],
    )
    return False

  def _transform_pick_data(self, pick_data: Dict[str, Any]) -> Dict[str, Any]:
    """Transforms a pick data dictionary from the poller to the format expected by the agent."""
    if (
        self.draft_obj is None
        or self.state_obj is None
        or self.league_obj is None
    ):
      return None

    player_id = pick_data["player_id"]
    if draft.is_team(player_id):
      entity = self.draft_obj.team_id_to_team.get(player_id)
    else:
      entity = self.draft_obj.player_id_to_player.get(player_id)

    if not entity:
      logging.warning(
          "Could not find entity for player ID %s in draft %s. This probably"
          " means that you need to rerun the ingestion job.",
          player_id,
          self.draft_id,
      )
      return None

    pick_no_in_round = draft.pick_no_to_pick_no_in_round(
        pick_data["pick_no"], self.draft_obj.num_teams
    )
    picker_id = pick_data["picked_by"]
    for pid, picks_set in self.state_obj.player_id_to_picks.items():
      if entity in picks_set:
        picker_id = pid
        break
    picked_by = self.league_obj.user_id_to_team_name.get(picker_id, picker_id)

    return {
        "player_id": player_id,
        "player_name": entity.name,
        "picked_by": picked_by,
        "round": int(pick_data["round"]),
        "pick_no": pick_no_in_round,
        "position": "DEF" if draft.is_team(player_id) else entity.position,
        "team": player_id if draft.is_team(player_id) else entity.team,
    }

  async def process_picks(self) -> None:
    """Processes events from the event queue."""
    if not self.state_obj or not self.draft_obj or not self.league_obj:
      return

    while True:
      pick = await self.event_queue.get()
      logging.info(
          "Processing new pick from poller for user %s: %s", self.user_id, pick
      )

      is_new_pick = await self._handle_speculative_correction(pick)
      if is_new_pick:
        self.state_obj.process_pick(pick)
        agent_formatted_pick = self._transform_pick_data(pick)
        if agent_formatted_pick:
          await self.connection.add_to_state_array(
              "add_pick_from_poller",
              "picks_from_poller",
              [agent_formatted_pick],
          )
        await self._update_adk_state_and_artifact()
      self.event_queue.task_done()

  async def get_tasks(self) -> List[asyncio.Task[None]]:
    """Returns the long-running tasks for this manager to be run by asyncio."""
    poller = sleeper_poller.AsyncPoller(self.draft_id)
    polling_session = aiohttp.ClientSession()

    return [
        asyncio.create_task(poller.run(polling_session, self.event_queue)),
        asyncio.create_task(self.process_picks()),
    ]
