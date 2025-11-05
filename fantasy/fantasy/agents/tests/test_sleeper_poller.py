import asyncio
import json
import pytest
from src.agents import sleeper_poller


SAMPLE_DATA = json.loads("""
    [
        {
            "draft_id":"257270643320426496","draft_slot":1,"is_keeper":null,
            "metadata":{
                "first_name":"David",
                "injury_status":"Out",
                "last_name":"Johnson",
                "news_updated":"1513007102037",
                "number":"31",
                "player_id":"2391",
                "position":"RB",
                "sport":"nfl",
                "status":"Injured Reserve",
                "team":"ARI"
              },
            "pick_no":1,
            "picked_by":"200837482281963520",
            "player_id":"2391",
            "reactions":null,
            "roster_id":1,
            "round":1
          },
        {
            "draft_id":"257270643320426496","draft_slot":2,"is_keeper":null,
            "metadata":{
                "first_name":"Le'Veon",
                "injury_status":"",
                "last_name":"Bell",
                "news_updated":"1515698101257",
                "number":"26",
                "player_id":"1408",
                "position":"RB",
                "sport":"nfl",
                "status":"Active",
                "team":"PIT"
              },
            "pick_no":2,
            "picked_by":"199042945356140544",
            "player_id":"1408",
            "reactions":null,
            "roster_id":2,
            "round":1
        }
    ]
    """)

SAMPLE_DRAFT_ID = "257270643320426496"
MAX_RATE = 60


@pytest.mark.asyncio
async def test_run_updates_event_queue():
  poller = sleeper_poller.AsyncPoller(SAMPLE_DRAFT_ID, MAX_RATE)
  event_queue = asyncio.Queue()
  await poller._process_data(event_queue, SAMPLE_DATA)
  assert len(SAMPLE_DATA) == event_queue.qsize()


@pytest.mark.asyncio
async def test_run_updates_previous_state_on_new_data():
  poller = sleeper_poller.AsyncPoller(SAMPLE_DRAFT_ID, MAX_RATE)
  event_queue = asyncio.Queue()
  await poller._process_data(event_queue, SAMPLE_DATA)
  assert poller.previous_state is not None


@pytest.mark.asyncio
async def test_only_adds_new_picks_to_event_queue():
  poller = sleeper_poller.AsyncPoller(SAMPLE_DRAFT_ID, MAX_RATE)
  event_queue = asyncio.Queue()
  await poller._process_data(event_queue, SAMPLE_DATA[:1])
  assert event_queue.qsize() == 1
  await poller._process_data(event_queue, SAMPLE_DATA)
  assert event_queue.qsize() == 2
