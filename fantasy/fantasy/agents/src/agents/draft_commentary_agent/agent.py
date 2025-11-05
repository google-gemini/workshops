"""Primary conversational agent for the Fantasy Draft Companion.

This module defines the root agent responsible for user interaction. It handles
the overall conversation flow, coordinates between specialized sub-agents and
tools, and acts as the main interface for the user.
"""

import asyncio
import json
import logging
import re
from typing import Any, AsyncGenerator, Optional, Tuple

from google.adk import models
from google.adk import tools
from google.adk.agents import live_request_queue
from google.adk.agents import llm_agent
from google.genai import client as genai_client
from google.genai import types as genai_types
from rapidfuzz import process
from src.agents.autopick_agent import agent as autopick_agent
from src.agents.recommendation_agent import agent as recommendation_agent

from . import draft_tools
from . import prompts


class DraftTracker:
  """Encapsulates all draft state and logic for deduplication and corrections."""

  def __init__(self, tool_context: tools.tool_context.ToolContext):
    self.state = tool_context.state
    self.state.setdefault("team_names", [])
    self.state.setdefault("processed_draft_positions", [])
    self.state.setdefault("drafted_player_ids", [])

  @property
  def team_names(self) -> list[str]:
    return self.state.get("team_names", [])

  def get_draft_position(self, pick_data: dict[str, Any]) -> Tuple[int, int]:
    """Returns the draft position tuple (round, pick) for a given pick data."""
    return (int(pick_data["round"]), int(pick_data["pick_no"]))

  def add_pick_if_new(
      self, player_data: dict[str, Any], threshold: float = 90.0
  ) -> Optional[dict[str, Any]]:
    """Validates, enriches, and adds a new pick if it's not a duplicate.

    Args:
      player_data: A dictionary containing the player's draft information.
      threshold: The minimum score for a team name fuzzy match to be accepted.

    Returns:
      The validated pick data if it's new, otherwise None.
    """
    required_keys = [
        "player_id",
        "player_name",
        "picked_by",
        "round",
        "pick_no",
    ]
    if not all(player_data.get(k) is not None for k in required_keys):
      logging.warning(
          "Skipping pick with missing required data: %s", player_data
      )
      return None

    draft_pos = self.get_draft_position(player_data)
    player_id = player_data["player_id"]

    if (
        player_id in self.state["drafted_player_ids"]
        or draft_pos in self.state["processed_draft_positions"]
    ):
      return None

    if self.team_names:
      best_match = process.extractOne(player_data["picked_by"], self.team_names)
      if best_match and best_match[1] >= threshold:
        player_data["picked_by"] = best_match[0]
      else:
        logging.warning(
            "Hallucination detected: Team name '%s' not recognized. Skipping"
            " pick %s.",
            player_data["picked_by"],
            draft_pos,
        )
        return None

    self.state["processed_draft_positions"].append(draft_pos)
    self.state["drafted_player_ids"].append(player_id)

    return player_data

  def undo_pick(self, player_data: dict[str, Any]) -> None:
    """Reverts a pick in the tracker's state, used for corrections."""
    draft_pos = self.get_draft_position(player_data)
    player_id = player_data["player_id"]

    if draft_pos in self.state["processed_draft_positions"]:
      self.state["processed_draft_positions"].remove(draft_pos)
    if player_id and player_id in self.state["drafted_player_ids"]:
      self.state["drafted_player_ids"].remove(player_id)

    logging.info(
        "Reverted pick state for pos %s / player %s", draft_pos, player_id
    )


async def monitor_fantasy_platform_picks(
    tool_context: tools.tool_context.ToolContext,
) -> AsyncGenerator[str, None]:
  """Monitors the fantasy platform for new picks and corrections.

  This is a long-running tool that watches for confirmed picks from the Sleeper
  poller and any corrections that need to be made to speculative picks.

  Yields:
      str: A JSON string of newly confirmed draft picks.
  """
  tracker = DraftTracker(tool_context)

  while True:
    # Process Confirmed Picks
    poller_picks = tool_context.state.get("picks_from_poller", [])
    if poller_picks:
      num_to_process = len(poller_picks)
      newly_confirmed_picks = []

      for pick in list(poller_picks):
        new_pick_data = tracker.add_pick_if_new(pick)
        if new_pick_data:
          newly_confirmed_picks.append(new_pick_data)

      if newly_confirmed_picks:
        yield json.dumps(newly_confirmed_picks)

      current_poller_picks = tool_context.state.get("picks_from_poller", [])
      tool_context.state["picks_from_poller"] = current_poller_picks[
          num_to_process:
      ]

    # Process Corrections
    corrected_picks = tool_context.state.get("corrected_vision_picks", [])
    if corrected_picks:
      num_to_process = len(corrected_picks)
      picks_to_correct = []
      for pick_data in list(corrected_picks):
        tracker.undo_pick(pick_data)
        pick_data["is_correction"] = True
        picks_to_correct.append(pick_data)

      if picks_to_correct:
        yield json.dumps(picks_to_correct)

      current_corrected_picks = tool_context.state.get(
          "corrected_vision_picks", []
      )
      tool_context.state["corrected_vision_picks"] = current_corrected_picks[
          num_to_process:
      ]

    await asyncio.sleep(0.3)


async def _get_latest_image_from_stream(
    input_stream: live_request_queue.LiveRequestQueue,
) -> Optional[genai_types.Part]:
  """Gets an image from the input stream."""
  last_valid_req = None
  while input_stream._queue.qsize() != 0:  # pylint: disable=protected-access
    live_req = await input_stream.get()
    if live_req.content and live_req.content.parts:
      image_part = next(
          (
              part
              for part in live_req.content.parts
              if part.inline_data and part.inline_data.mime_type == "image/jpeg"
          ),
          None,
      )
      if image_part:
        last_valid_req = image_part
  return last_valid_req


def _transform_raw_pick_data(
    raw_player_data: dict[str, Any],
) -> Optional[Tuple[Tuple[int, int], dict[str, Any]]]:
  """Transforms raw vision model output into structured player data."""
  player_name = raw_player_data.get("player_name")
  draft_pos_str = raw_player_data.get("draft_position")
  pos_team = raw_player_data.get("pos_team")
  picked_by = raw_player_data.get("picked_by")

  if not all((player_name, draft_pos_str, pos_team, picked_by)):
    logging.warning(
        "Skipping incomplete player data from model: %s", raw_player_data
    )
    return None

  pos_parts = pos_team.split("-", 1)
  position = pos_parts[0].strip() if pos_parts else None
  team = pos_parts[1].strip() if len(pos_parts) > 1 else None

  match = re.match(r"(\d+)\.(\d+)", position)
  if not match:
    return None
  round_and_pick = (int(match.group(1)), int(match.group(2)))

  try:
    player_id, _ = draft_tools.get_player_id_fuzzy_search(
        player_name, position=position, team_abbreviation=team
    )
  except ValueError as e:
    logging.warning("Could not find player ID for '%s': %s", player_name, e)
    return None

  round_num, pick_num = round_and_pick
  processed_data = {
      "player_id": player_id,
      "player_name": player_name,
      "picked_by": picked_by,
      "round": round_num,
      "pick_no": pick_num,
      "position": position,
      "team": team,
  }
  return (round_and_pick, processed_data)


async def monitor_vision_picks(
    input_stream: live_request_queue.LiveRequestQueue,
    tool_context: tools.tool_context.ToolContext,
) -> AsyncGenerator[str, None]:
  """Monitors the video stream for new fantasy draft picks.

  This is a long-running tool that continuously watches for new images of the
  draft board. When it detects a player who hasn't been seen before, it yields
  that player's draft information as a speculative pick.

  Yields:
      str: A stream of newly drafted player information as JSON strings.
  """
  tracker = DraftTracker(tool_context)
  client = genai_client.Client(
      vertexai=False,
      http_options=genai_types.HttpOptions(
          retry_options=genai_types.HttpRetryOptions(
              initial_delay=1, attempts=3
          )
      ),
  )
  response_schema = genai_types.Schema(
      type=genai_types.Type.ARRAY,
      items=genai_types.Schema(
          type=genai_types.Type.OBJECT,
          properties={
              "player_name": genai_types.Schema(type=genai_types.Type.STRING),
              "draft_position": genai_types.Schema(
                  type=genai_types.Type.STRING
              ),
              "picked_by": genai_types.Schema(type=genai_types.Type.STRING),
              "pos_team": genai_types.Schema(type=genai_types.Type.STRING),
          },
          required=["player_name", "draft_position", "picked_by", "pos_team"],
      ),
  )
  vision_config = genai_types.GenerateContentConfig(
      temperature=0.0,
      response_mime_type="application/json",
      response_schema=response_schema,
      system_instruction=prompts.VISION_SYSTEM_INSTRUCTION.format(
          team_names=",".join(tracker.team_names)
      ),
      candidate_count=2,
  )

  async def _generate_and_process_picks(
      image: genai_types.Part,
  ) -> list[Tuple[Tuple[int, int], dict[str, Any]]]:
    """Generates and processes picks from an image."""
    response = await client.aio.models.generate_content(
        model="gemini-2.5-flash",
        contents=genai_types.Content(
            role="user",
            parts=[
                image,
                genai_types.Part.from_text(text=prompts.VISION_PROMPT_TEXT),
            ],
        ),
        config=vision_config,
    )

    if not response.candidates:
      logging.warning("Model response received, but it contains no candidates.")
      return []

    visible_players_per_candidate = []
    for candidate in response.candidates:
      if candidate.finish_reason.name != "STOP":
        logging.warning(
            "Model finished for reason '%s', not 'STOP'. Skipping.",
            candidate.finish_reason.name,
        )
        return []

      response_text = candidate.content.parts[0].text
      if not response_text:
        return []

      try:
        transformed_visible_players_data = []
        response_json = json.loads(response_text)
        for raw_data in response_json:
          transformed_data = _transform_raw_pick_data(raw_data)
          if transformed_data:
            transformed_visible_players_data.append(transformed_data)

        visible_players_per_candidate.append(transformed_visible_players_data)
      except json.JSONDecodeError as e:
        logging.error(
            "Failed to decode JSON from model response: %s. Error: %s",
            response_text,
            e,
        )
        return []

    picks_per_candidate = []
    for transformed_visible_players_data in visible_players_per_candidate:
      picks_per_candidate.append({
          pick[1]["player_id"]: pick
          for pick in transformed_visible_players_data
      })

    if not picks_per_candidate:
      return []

    intersection_player_ids = set(picks_per_candidate[0].keys())
    for i in range(1, len(picks_per_candidate)):
      intersection_player_ids &= set(picks_per_candidate[i].keys())

    return [
        picks_per_candidate[0][player_id]
        for player_id in intersection_player_ids
    ]

  while True:
    image_part = await _get_latest_image_from_stream(input_stream)
    if image_part:
      valid_picks_with_pos = await _generate_and_process_picks(image_part)
      valid_picks_with_pos.sort(key=lambda x: x[0])
      newly_drafted_this_batch = []
      for _, processed_player_data in valid_picks_with_pos:
        new_pick_data = tracker.add_pick_if_new(processed_player_data)
        if new_pick_data:
          newly_drafted_this_batch.append(new_pick_data)
          tool_context.state.setdefault(
              "speculative_picks_from_vision", []
          ).append(new_pick_data)

      if newly_drafted_this_batch:
        yield json.dumps(newly_drafted_this_batch)

    await asyncio.sleep(0.3)


draft_commentary_agent = llm_agent.LlmAgent(
    model=models.Gemini(
        model="gemini-live-2.5-flash-preview",
        retry_options=genai_types.HttpRetryOptions(initial_delay=1, attempts=3),
        speech_config=genai_types.SpeechConfig(
            voice_config=genai_types.VoiceConfig(
                prebuilt_voice_config=genai_types.PrebuiltVoiceConfig(
                    voice_name="Kore",
                )
            )
        ),
    ),
    name="draft_commentary_agent",
    description="The main conversational agent and fantasy draft commentator.",
    instruction=prompts.DRAFT_COMMENTARY_AGENT_SYSTEM_INSTRUCTION,
    tools=[
        tools.agent_tool.AgentTool(
            agent=autopick_agent.autopick_agent, skip_summarization=True
        ),
        tools.agent_tool.AgentTool(
            agent=recommendation_agent.recommendation_agent
        ),
        tools.FunctionTool(func=draft_tools.get_draft_structure),
        tools.FunctionTool(func=draft_tools.get_player_id_fuzzy_search),
        tools.FunctionTool(func=draft_tools.get_player_info),
        tools.FunctionTool(func=draft_tools.get_team_info),
        tools.FunctionTool(func=draft_tools.monitor_autopick),
        tools.FunctionTool(func=draft_tools.play_sound_effect),
        tools.FunctionTool(func=draft_tools.stop_streaming),
        tools.google_search,
        tools.FunctionTool(func=monitor_fantasy_platform_picks),
        monitor_vision_picks,
    ],
)

root_agent = draft_commentary_agent
