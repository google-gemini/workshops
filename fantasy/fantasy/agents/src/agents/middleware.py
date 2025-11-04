"""FastAPI server for the Fantasy Draft Companion.

This FastAPI server is used to serve the Python client and manage bidirectional
communication between the client and the agent.
"""

import asyncio
import base64
import json
import logging
from typing import Any, AsyncGenerator
import warnings
from common import constants
import fastapi
from google.adk import runners
from google.adk.agents import live_request_queue as live_request_queue_lib
from google.adk.agents import run_config as run_config_lib
from google.adk.events import event as adk_event
from google.adk.events import event_actions
from google.genai import types as genai_types
from src.agents.draft_commentary_agent import agent
from . import fantasy

FastAPI = fastapi.FastAPI
WebSocket = fastapi.WebSocket


logging.basicConfig(
    level=getattr(logging, "INFO"),
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")


class AgentConnection:
  """Manages the connection and communication between the agent and the client."""

  def __init__(
      self,
      websocket: WebSocket,
      user_id: str,
      league_id: str,
      draft_id: str,
      superflex: bool,
      is_audio: bool,
  ):
    self.websocket = websocket
    self.session_id = draft_id
    self.live_events: AsyncGenerator[adk_event.Event, None] | None = None
    self.live_request_queue: live_request_queue_lib.LiveRequestQueue | None = (
        None
    )

    self.user_id = user_id
    self.league_id = league_id
    self.draft_id = draft_id
    self.superflex = superflex
    self.is_audio = is_audio

    self.draft_manager = fantasy.DraftManager(self)

  async def connect(self):
    """Accepts the WebSocket connection and starts an agent session."""
    await self.websocket.accept()
    logging.info(
        "Client #%s connected, audio mode: %s", self.user_id, self.is_audio
    )
    self.runner = runners.InMemoryRunner(
        app_name=constants.APP_NAME, agent=agent.draft_commentary_agent
    )
    self.session = await self.runner.session_service.create_session(
        app_name=constants.APP_NAME,
        user_id=self.user_id,
        session_id=self.session_id,
        state={
            "autopick_enabled": False,
            "autopick_count": None,
            "autopick_strategy": None,
            "corrected_vision_picks": [],
            "draft_data_file_name": constants.DRAFT_DATA_FILE_NAME,
            "draft_id": self.draft_id,
            "is_my_turn": False,
            "pick_no": 0,
            "picks_from_poller": [],
            "sound_effects": [],
            "speculative_picks_from_vision": [],
            "team_names": [],
        },
    )

    modality = (
        genai_types.MediaModality.AUDIO
        if self.is_audio
        else genai_types.MediaModality.TEXT
    )
    run_config = run_config_lib.RunConfig(
        response_modalities=[modality],
        session_resumption=genai_types.SessionResumptionConfig(),
    )

    self.live_request_queue = live_request_queue_lib.LiveRequestQueue()
    self.live_events = self.runner.run_live(
        session=self.session,
        user_id=self.user_id,
        session_id=self.session_id,
        live_request_queue=self.live_request_queue,
        run_config=run_config,
    )

    await self.draft_manager.initialize()

  async def update_state(
      self,
      invocation_id: str,
      state_delta: dict[str, Any],
      role: str = "system",
  ) -> None:
    """Updates the session state with the given delta.

    Args:
      invocation_id: The ID of the invocation triggering this state update.
      state_delta: A dictionary containing the state changes.
      role: The role of the entity making the update (default: "system").
    """
    state_update_event = adk_event.Event(
        invocation_id=invocation_id,
        author=role,
        actions=event_actions.EventActions(state_delta=state_delta),
    )
    await self.runner.session_service.append_event(
        self.session,
        state_update_event,
    )
    logging.debug(
        "[UPDATE STATE %s]: Updated %s to %s.",
        self.user_id,
        state_delta.keys(),
        state_delta.values(),
    )

  async def add_to_state_array(
      self,
      invocation_id: str,
      array_name: str,
      new_items: list[Any],
      role: str = "system",
  ) -> None:
    """Adds new items to an array in the session state.

    Args:
      invocation_id: The ID of the invocation triggering this state update.
      array_name: The name of the array to add to.
      new_items: The items to add to the array.
      role: The role of the entity making the update (default: "system").
    """
    current_items = self.session.state.get(array_name, [])
    updated_items = current_items + new_items
    await self.update_state(
        invocation_id=invocation_id,
        state_delta={array_name: updated_items},
        role=role,
    )

  async def upload_artifact(
      self,
      artifact_part: genai_types.Part,
      filename: str,
  ) -> None:
    """Uploads the given artifact part to ADK."""
    version = await self.runner.artifact_service.save_artifact(
        app_name=self.runner.app_name,
        user_id=self.user_id,
        session_id=self.session_id,
        filename=filename,
        artifact=artifact_part,
    )
    logging.debug(
        "[UPLOAD ARTIFACT %s]: Saved artifact version: %s to %s.",
        self.user_id,
        version,
        filename,
    )

  async def _agent_to_client_messaging(self):
    """Sends messages from the agent to the client."""
    try:
      async for event in self.live_events:
        if event.turn_complete or event.interrupted:
          message = {
              "turn_complete": event.turn_complete,
              "interrupted": event.interrupted,
          }
          await self.websocket.send_text(json.dumps(message))
          logging.debug("[AGENT TO CLIENT %s]: %s", self.user_id, message)
          continue

        part: genai_types.Part | None = (
            event.content and event.content.parts and event.content.parts[0]
        )
        if not part:
          continue

        is_audio = (
            part.inline_data
            and part.inline_data.mime_type
            and part.inline_data.mime_type.startswith("audio/pcm")
        )
        if is_audio:
          audio_data = part.inline_data and part.inline_data.data
          if audio_data:
            message = {
                "mime_type": "audio/pcm",
                "data": base64.b64encode(audio_data).decode("ascii"),
            }
            await self.websocket.send_text(json.dumps(message))
            logging.debug(
                "[AGENT TO CLIENT %s]: audio/pcm: %s bytes.",
                self.user_id,
                len(audio_data),
            )
        elif part.text and event.partial:
          message = {
              "mime_type": "text/plain",
              "data": part.text,
          }
          await self.websocket.send_text(json.dumps(message))
          logging.debug(
              "[AGENT TO CLIENT %s]: text/plain: %s", self.user_id, message
          )
    except Exception as e:  # pylint: disable=broad-exception-caught
      logging.exception(
          "[AGENT TO CLIENT %s]: Exception in agent_to_client_messaging: %s",
          self.user_id,
          e,
      )
      raise

  def _client_to_agent_messaging_text_implementation(self, data: str):
    """Sends text messages from the client to the agent."""
    content = genai_types.Content(
        role="user", parts=[genai_types.Part.from_text(text=data)]
    )
    self.live_request_queue.send_content(content=content)
    logging.debug("[CLIENT TO AGENT %s]: text/plain: %s", self.user_id, data)

  async def _client_to_agent_messaging(self):
    """Sends messages from the client to the agent."""
    try:
      while True:
        message_json = await self.websocket.receive_text()
        message = json.loads(message_json)
        mime_type = message["mime_type"]
        data = message["data"]

        if mime_type == "text/plain":
          self._client_to_agent_messaging_text_implementation(data)
          logging.debug(
              "[CLIENT TO AGENT %s]: text/plain: %s", self.user_id, data
          )
        elif mime_type == "audio/pcm":
          decoded_data = base64.b64decode(data)
          self.live_request_queue.send_realtime(
              genai_types.Blob(data=decoded_data, mime_type=mime_type)
          )
          logging.debug(
              "[CLIENT TO AGENT %s]: audio/pcm: %s bytes.",
              self.user_id,
              len(decoded_data),
          )
        elif mime_type == "image/jpeg":
          decoded_data = base64.b64decode(data)
          self.live_request_queue.send_content(
              content=genai_types.Content(
                  role="user",
                  parts=[
                      genai_types.Part.from_bytes(
                          data=decoded_data, mime_type=mime_type
                      )
                  ],
              )
          )
          logging.debug(
              "[CLIENT TO AGENT %s]: image/jpeg: %s bytes.",
              self.user_id,
              len(decoded_data),
          )
        else:
          logging.error(
              "[CLIENT TO AGENT %s]: Mime type not supported: %s",
              self.user_id,
              mime_type,
          )
          raise ValueError(f"Mime type not supported: {mime_type}")
    except Exception as e:  # pylint: disable=broad-exception-caught
      logging.exception(
          "[CLIENT TO AGENT %s]: Exception in client_to_agent_messaging: %s",
          self.user_id,
          e,
      )
      raise

  async def _state_to_client_messaging(self):
    """Checks session state for new commands and relays them to the client."""
    try:
      while True:
        await asyncio.sleep(0.1)

        sound_effects_to_play = self.session.state.get("sound_effects", [])

        if sound_effects_to_play:
          num_to_process = len(sound_effects_to_play)
          if self.is_audio:
            logging.info(
                "Found %d sound effect(s) in session state for #%s. Relaying"
                " command to client.",
                num_to_process,
                self.user_id,
            )

            for sound_id in sound_effects_to_play:
              command_message = {
                  "command_type": "play_audio",
                  "sound_id": sound_id,
                  "mime_type": "text/plain",
              }
              await self.websocket.send_text(json.dumps(command_message))
              logging.debug(
                  "[STATE TO CLIENT %s]: Command sent: %s",
                  self.user_id,
                  command_message,
              )
          else:
            logging.info(
                "Found %d sound effect(s) in session state for #%s. Audio is"
                " disabled, clearing state.",
                num_to_process,
                self.user_id,
            )
          current_sound_effects = self.session.state.get("sound_effects", [])
          updated_sound_effects = current_sound_effects[num_to_process:]
          await self.update_state(
              invocation_id="clear_played_sound_effects",
              state_delta={"sound_effects": updated_sound_effects},
          )

    except Exception as e:  # pylint: disable=broad-exception-caught
      logging.exception(
          "[STATE TO CLIENT %s]: Exception in state_to_client_messaging: %s",
          self.user_id,
          e,
      )
      raise

  async def _process_vision_picks_task(self):
    """Monitors state for vision picks and processes them."""
    while True:
      await asyncio.sleep(0.5)
      vision_picks = self.session.state.get("speculative_picks_from_vision", [])
      if vision_picks:
        num_to_process = len(vision_picks)
        logging.info(
            "Processing %d speculative picks from vision.", num_to_process
        )
        for pick_data in vision_picks:
          try:
            await self.draft_manager.add_speculative_pick(pick_data)
          except (ValueError, KeyError) as e:
            logging.warning(
                "Failed to process vision pick: %s. Error: %s", pick_data, e
            )
            continue

        current_vision_picks = self.session.state.get(
            "speculative_picks_from_vision", []
        )
        updated_vision_picks = current_vision_picks[num_to_process:]
        await self.update_state(
            "clear_processed_vision_picks",
            {"speculative_picks_from_vision": updated_vision_picks},
        )

  async def run(self):
    """Runs the bidirectional messaging tasks."""
    agent_to_client_task = asyncio.create_task(
        self._agent_to_client_messaging()
    )
    client_to_agent_task = asyncio.create_task(
        self._client_to_agent_messaging()
    )
    state_to_client_task = asyncio.create_task(
        self._state_to_client_messaging()
    )
    process_vision_task = asyncio.create_task(self._process_vision_picks_task())
    draft_manager_tasks = await self.draft_manager.get_tasks()

    self._client_to_agent_messaging_text_implementation(
        "Enable the autopick, vision, and fantasy platform monitors."
    )  # Ensure that all monitors are enabled.

    tasks = [
        agent_to_client_task,
        client_to_agent_task,
        state_to_client_task,
        process_vision_task,
    ] + draft_manager_tasks
    done, pending = await asyncio.wait(
        tasks, return_when=asyncio.FIRST_EXCEPTION
    )

    for task in pending:
      task.cancel()

    for task in done:
      if task.exception():
        raise task.exception()

  async def close(self):
    """Closes the connection and cleans up agent resources."""
    if self.live_request_queue:
      self.live_request_queue.close()

    if self.session and self.runner:
      try:
        await self.runner.session_service.delete_session(
            app_name=constants.APP_NAME,
            user_id=self.user_id,
            session_id=self.session_id,
        )
      except Exception as e:  # pylint: disable=broad-exception-caught
        logging.exception(
            "Failed to delete ADK session #%s: %s", self.user_id, e
        )

    logging.info("Connection #%s closed.", self.user_id)


app = FastAPI()


@app.get("/")
async def root():
  """Root endpoint."""
  return {"message": "Welcome to the Fantasy Football Draft Companion!"}


@app.websocket("/ws/{user_id}/{league_id}/{draft_id}/{superflex}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str,
    league_id: str,
    draft_id: str,
    superflex: bool,
    is_audio: str,
):
  """Client websocket endpoint."""
  connection = AgentConnection(
      websocket, user_id, league_id, draft_id, superflex, is_audio == "true"
  )

  try:
    await connection.connect()
    await connection.run()
  except fastapi.WebSocketDisconnect:
    logging.info("Client #%s WebSocket disconnected gracefully.", user_id)
  except Exception as e:  # pylint: disable=broad-exception-caught
    logging.exception(
        "Error in WebSocket connection for user %s: %s",
        user_id,
        e,
        exc_info=True,
    )
  finally:
    await connection.close()
