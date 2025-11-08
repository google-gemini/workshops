"""Polls the Sleeper API for draft state updates.

This script is used to poll the Sleeper API for draft state updates. It is meant
to run in the background to create a queue of draft events.
"""

import asyncio
import logging
from typing import Any, Dict, List
import aiohttp
import aiolimiter
from common import constants


class AsyncPoller:
  """Polls the Sleeper API for draft state updates."""

  def __init__(
      self,
      draft_id: str,
      max_rate: int = 1000,  # Sleeper API allows 1000 requests per minute.
      timeout_seconds: int = 10,
  ):
    if max_rate <= 0:
      raise ValueError(f"`max_rate` must be positive. Got: {max_rate}")

    self.previous_state: List[Dict[str, Any]] = []
    self.endpoint = f"{constants.SLEEPER_API_BASE_URL}/draft/{draft_id}/picks"
    self.rate_limiter = aiolimiter.AsyncLimiter(max_rate, time_period=60)
    self.timeout = aiohttp.ClientTimeout(timeout_seconds)

  async def run(
      self,
      session: aiohttp.ClientSession,
      event_queue: asyncio.Queue[Dict[str, Any]],
  ) -> None:
    """Continuously polls the Sleeper API, respecting the rate limit."""
    logging.debug(
        "Polling for draft state updates. Endpoint: %s",
        self.endpoint,
    )
    while True:
      data = await self._poll(session)
      await self._process_data(event_queue, data)
      await asyncio.sleep(0.05)

  async def _process_data(
      self, queue: asyncio.Queue[Dict[str, Any]], data: List[Dict[str, Any]]
  ) -> None:
    """Processes the data from the Sleeper API and adds it to the queue."""
    if data is None:
      return

    if data != self.previous_state:
      prev_num_picks = len(self.previous_state)
      new_picks = data[prev_num_picks:]
      if new_picks:
        logging.debug("Found %d new draft picks.", len(new_picks))
        for pick in new_picks:
          await queue.put(pick)

    self.previous_state = data

  async def _poll(self, session):
    """Performs a single rate-limited poll to the API endpoint.

    Args:
        session: The aiohttp.ClientSession to use for making the request.

    Returns:
        A list of pick dictionaries on success, or None on error/timeout.
    """
    await self.rate_limiter.acquire()
    try:
      async with session.get(self.endpoint, timeout=self.timeout) as resp:
        resp.raise_for_status()
        return await resp.json()
    except asyncio.TimeoutError:
      logging.info("Request to %s timed out.", self.endpoint)
      return None
    except aiohttp.ClientError as e:
      logging.exception("An error occurred during polling: %s", e)
      return None
