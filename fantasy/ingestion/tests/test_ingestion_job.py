import asyncio
import json
from unittest import mock
import pandas as pd
import pytest
import requests
from src.ingestion import ingestion_job


@pytest.fixture
def mock_genai_client(monkeypatch):
  """Mocks the genai.Client class."""
  mock_client_cls = mock.MagicMock()
  mock_client_instance = mock_client_cls.return_value
  monkeypatch.setattr(ingestion_job.genai, "Client", mock_client_cls)
  return mock_client_instance


@pytest.fixture
def mock_player_data():
  return pd.DataFrame({
      "player_id": ["1"],
      "name": ["Player One"],
      "team": ["TEN"],
      "position": ["QB"],
      "status": ["Active"],
      "injury": [None],
      "bio": [None],
  })


@pytest.fixture
def mock_adp_data():
  return pd.DataFrame({
      "name": ["Player One"],
      "team": ["TEN"],
      "position": ["QB"],
      "adp": [1.0],
      "type": ["2025_1_standard"],
  })


@pytest.fixture
def mock_player_stats_data():
  return pd.DataFrame({
      "name": ["Player One"],
      "team": ["TEN"],
      "position": ["QB"],
      "injury_risk": ["low"],
      "fpts": [
          json.dumps({"standard": 300.0, "half-ppr": 300.0, "ppr": 300.0})
      ],
  })


def test_get_all_nfl_players_returns_correct_df(mock_genai_client):
  mock_json_data = {
      "525": {
          "years_exp": 15,
          "hashtag": "#morgancox-NFL-TEN-46",
          "rotowire_id": 7075,
          "swish_id": 334132,
          "search_rank": 9999999,
          "stats_id": None,
          "birth_city": None,
          "practice_participation": None,
          "depth_chart_position": "K",
          "birth_country": None,
          "birth_state": None,
          "active": True,
          "fantasy_data_id": 11008,
          "number": 46,
          "college": "Tennessee",
          "age": 39,
          "metadata": {
              "channel_id": "1113708831713554432",
              "rookie_year": "2010",
          },
          "sport": "nfl",
          "search_last_name": "cox",
          "injury_body_part": None,
          "injury_status": None,
          "weight": "233",
          "status": "Active",
          "player_id": "525",
          "first_name": "Morgan",
          "search_full_name": "morgancox",
          "last_name": "Cox",
          "rotoworld_id": None,
          "oddsjam_id": "37F0275372F8",
          "opta_id": None,
          "team": "TEN",
          "fantasy_positions": ["K"],
          "team_changed_at": None,
          "practice_description": None,
          "gsis_id": "00-0027557",
          "high_school": "Evangelical Christian (TN)",
          "competitions": [],
          "full_name": "Morgan Cox",
          "news_updated": 1741672561055,
          "position": "K",
          "sportradar_id": "513df09d-7d3a-44a8-873c-34f2fe46326b",
          "depth_chart_order": None,
          "team_abbr": None,
          "birth_date": "1986-04-26",
          "injury_start_date": None,
          "pandascore_id": None,
          "search_first_name": "morgan",
          "espn_id": 13848,
          "injury_notes": None,
          "height": "76",
          "yahoo_id": 24362,
      },
      "7585": {
          "years_exp": 4,
          "hashtag": "#davismills-NFL-HOU-10",
          "rotowire_id": 15542,
          "swish_id": 1060311,
          "search_rank": 369,
          "stats_id": None,
          "birth_city": None,
          "practice_participation": None,
          "depth_chart_position": "QB",
          "birth_country": None,
          "birth_state": None,
          "active": True,
          "fantasy_data_id": None,
          "number": 10,
          "college": "Stanford",
          "age": 26,
          "metadata": {
              "channel_id": "1113708785672679424",
              "rookie_year": "2021",
          },
          "sport": "nfl",
          "search_last_name": "mills",
          "injury_body_part": None,
          "injury_status": None,
          "weight": "225",
          "status": "Active",
          "player_id": "7585",
          "first_name": "Davis",
          "search_full_name": "davismills",
          "last_name": "Mills",
          "rotoworld_id": None,
          "oddsjam_id": "5E1061D78154",
          "opta_id": None,
          "team": "HOU",
          "fantasy_positions": ["QB"],
          "team_changed_at": None,
          "practice_description": None,
          "gsis_id": None,
          "high_school": "Greater Atlanta Christian School (GA)",
          "competitions": [],
          "full_name": "Davis Mills",
          "news_updated": 1754786155494,
          "position": "QB",
          "sportradar_id": "7d51fab7-2d52-4d19-a021-19a123af0d10",
          "depth_chart_order": 2,
          "team_abbr": None,
          "birth_date": "1998-10-21",
          "injury_start_date": None,
          "pandascore_id": None,
          "search_first_name": "davis",
          "espn_id": None,
          "injury_notes": None,
          "height": "76",
          "yahoo_id": None,
      },
  }

  mock_session = mock.create_autospec(requests.Session, instance=True)
  mock_response = mock.MagicMock(spec=requests.Response)
  mock_response.status_code = 200
  mock_response.json.return_value = mock_json_data
  mock_session.get.return_value = mock_response
  ingestion_instance = ingestion_job.Ingestion(session=mock_session)

  expected_df = pd.DataFrame({
      "player_id": ["525", "7585"],
      "name": ["Morgan Cox", "Davis Mills"],
      "team": ["TEN", "HOU"],
      "position": ["K", "QB"],
      "status": ["Active", "Active"],
      "injury": [
          json.dumps({"injury_status": None, "injury_body_part": None}),
          json.dumps({"injury_status": None, "injury_body_part": None}),
      ],
      "bio": [
          json.dumps({
              "height": "76",
              "weight": "233",
              "age": 39,
              "years_exp": 15,
              "college": "Tennessee",
              "high_school": "Evangelical Christian (TN)",
              "rookie_year": "2010",
          }),
          json.dumps({
              "height": "76",
              "weight": "225",
              "age": 26,
              "years_exp": 4,
              "college": "Stanford",
              "high_school": "Greater Atlanta Christian School (GA)",
              "rookie_year": "2021",
          }),
      ],
  })
  actual_df = ingestion_instance.get_all_nfl_players()
  mock_session.get.assert_called_once_with(
      "https://api.sleeper.app/v1/players/nfl"
  )
  pd.testing.assert_frame_equal(
      expected_df.sort_values(by="name"),
      actual_df.sort_values(by="name"),
      check_like=True,
  )


def test_get_all_nfl_players_filters_out_inactive_players(mock_genai_client):
  mock_json_data = {
      "525": {
          "years_exp": 15,
          "hashtag": "#morgancox-NFL-TEN-46",
          "rotowire_id": 7075,
          "swish_id": 334132,
          "search_rank": 9999999,
          "stats_id": None,
          "birth_city": None,
          "practice_participation": None,
          "depth_chart_position": "K",
          "birth_country": None,
          "birth_state": None,
          "active": False,  # Modified to False
          "fantasy_data_id": 11008,
          "number": 46,
          "college": "Tennessee",
          "age": 39,
          "metadata": {
              "channel_id": "1113708831713554432",
              "rookie_year": "2010",
          },
          "sport": "nfl",
          "search_last_name": "cox",
          "injury_body_part": None,
          "injury_status": None,
          "weight": "233",
          "status": "Active",
          "player_id": "525",
          "first_name": "Morgan",
          "search_full_name": "morgancox",
          "last_name": "Cox",
          "rotoworld_id": None,
          "oddsjam_id": "37F0275372F8",
          "opta_id": None,
          "team": "TEN",
          "fantasy_positions": ["K"],
          "team_changed_at": None,
          "practice_description": None,
          "gsis_id": "00-0027557",
          "high_school": "Evangelical Christian (TN)",
          "competitions": [],
          "full_name": "Morgan Cox",
          "news_updated": 1741672561055,
          "position": "K",
          "sportradar_id": "513df09d-7d3a-44a8-873c-34f2fe46326b",
          "depth_chart_order": None,
          "team_abbr": None,
          "birth_date": "1986-04-26",
          "injury_start_date": None,
          "pandascore_id": None,
          "search_first_name": "morgan",
          "espn_id": 13848,
          "injury_notes": None,
          "height": "76",
          "yahoo_id": 24362,
      },
      "7585": {
          "years_exp": 4,
          "hashtag": "#davismills-NFL-HOU-10",
          "rotowire_id": 15542,
          "swish_id": 1060311,
          "search_rank": 369,
          "stats_id": None,
          "birth_city": None,
          "practice_participation": None,
          "depth_chart_position": "QB",
          "birth_country": None,
          "birth_state": None,
          "active": True,
          "fantasy_data_id": None,
          "number": 10,
          "college": "Stanford",
          "age": 26,
          "metadata": {
              "channel_id": "1113708785672679424",
              "rookie_year": "2021",
          },
          "sport": "nfl",
          "search_last_name": "mills",
          "injury_body_part": None,
          "injury_status": None,
          "weight": "225",
          "status": "Active",
          "player_id": "7585",
          "first_name": "Davis",
          "search_full_name": "davismills",
          "last_name": "Mills",
          "rotoworld_id": None,
          "oddsjam_id": "5E1061D78154",
          "opta_id": None,
          "team": None,  # Modified this to None
          "fantasy_positions": ["QB"],
          "team_changed_at": None,
          "practice_description": None,
          "gsis_id": None,
          "high_school": "Greater Atlanta Christian School (GA)",
          "competitions": [],
          "full_name": "Davis Mills",
          "news_updated": 1754786155494,
          "position": "QB",
          "sportradar_id": "7d51fab7-2d52-4d19-a021-19a123af0d10",
          "depth_chart_order": 2,
          "team_abbr": None,
          "birth_date": "1998-10-21",
          "injury_start_date": None,
          "pandascore_id": None,
          "search_first_name": "davis",
          "espn_id": None,
          "injury_notes": None,
          "height": "76",
      },
  }

  mock_session = mock.create_autospec(requests.Session, instance=True)
  mock_response = mock.MagicMock(spec=requests.Response)
  mock_response.status_code = 200
  mock_response.json.return_value = mock_json_data
  mock_session.get.return_value = mock_response
  ingestion_instance = ingestion_job.Ingestion(session=mock_session)

  actual_df = ingestion_instance.get_all_nfl_players()
  assert len(actual_df) == 0
  mock_session.get.assert_called_once_with(
      "https://api.sleeper.app/v1/players/nfl"
  )


def test_get_adps_returns_correct_df(mock_genai_client):
  teams = [8, 10]
  game_modes = ["PPR", "Half-PPR"]
  year = 2025
  url = "https://fantasyfootballcalculator.com/api/v1/adp/{}?teams={}&year={}"

  # Empty dataframe
  expected_df = pd.DataFrame({})
  endpoint_to_data = {}
  for game_mode in game_modes:
    for team in teams:
      endpoint_to_data[url.format(game_mode.lower(), team, year)] = {
          "status": "Success",
          "meta": {
              "type": game_mode,
              "teams": team,
              "rounds": 1,
              "total_drafts": 9185,
              "start_date": "2025-08-20",
              "end_date": "2025-08-27",
          },
          "players": [
              {
                  "player_id": 5177,
                  "name": "Ja'Marr Chase",
                  "position": "WR",
                  "team": "CIN",
                  "adp": 1.5,
                  "adp_formatted": "1.02",
                  "times_drafted": 2284,
                  "high": 1,
                  "low": 5,
                  "stdev": 0.8,
                  "bye": 10,
              },
              {
                  "player_id": 5670,
                  "name": "Bijan Robinson",
                  "position": "RB",
                  "team": "ATL",
                  "adp": 2.1,
                  "adp_formatted": "1.02",
                  "times_drafted": 1652,
                  "high": 1,
                  "low": 5,
                  "stdev": 0.8,
                  "bye": 5,
              },
          ],
      }
      df = pd.DataFrame({
          "name": ["Ja'Marr Chase", "Bijan Robinson"],
          "team": ["CIN", "ATL"],
          "position": ["WR", "RB"],
          "adp": [1.5, 2.1],
          "type": [
              f"{year}_{team}_{game_mode.lower()}",
              f"{year}_{team}_{game_mode.lower()}",
          ],
      })
      expected_df = pd.concat([expected_df, df])

  def mock_get_side_effect(url):
    mock_response = mock.MagicMock(spec=requests.Response)
    mock_response.status_code = 200
    if url not in endpoint_to_data:
      mock_response.status_code = 500
    mock_response.json.return_value = endpoint_to_data[url]
    return mock_response

  mock_session = mock.create_autospec(requests.Session, instance=True)
  mock_session.get.side_effect = mock_get_side_effect

  ingestion_instance = ingestion_job.Ingestion(session=mock_session)
  ingestion_instance.year = 2025
  ingestion_instance.teams = teams
  ingestion_instance.game_modes = [
      game_mode.lower() for game_mode in game_modes
  ]

  actual_df = ingestion_instance.get_adps()
  pd.testing.assert_frame_equal(
      expected_df.reset_index(drop=True),
      actual_df.reset_index(drop=True),
      check_like=True,
  )

  expected_calls = []
  for game_mode in game_modes:
    for team in teams:
      expected_calls.append(
          mock.call(url.format(game_mode.lower(), team, year))
      )
  mock_session.get.assert_has_calls(expected_calls, any_order=True)


def test_clean_text():
  assert ingestion_job.clean_text("Morgan Cox") == "morgan cox"
  assert ingestion_job.clean_text("Morgan C'ox") == "morgan cox"
  assert ingestion_job.clean_text("MORGAN COX") == "morgan cox"


def test_robust_merge_exact_match():
  df_1 = pd.DataFrame({
      "name": ["Morgan Cox", "Davis Mills"],
      "team": ["TEN", "HOU"],
      "position": ["K", "QB"],
  })
  df_2 = pd.DataFrame({
      "name": ["Davis Mills", "Morgan Cox"],
      "team": ["HOU", "TEN"],
  })
  actual_df = ingestion_job.robust_merge(df_1, df_2, "name")
  expected_df = pd.DataFrame({
      "name": ["Morgan Cox", "Davis Mills"],
      "position": ["K", "QB"],
      "team": ["TEN", "HOU"],
  })
  pd.testing.assert_frame_equal(expected_df, actual_df, check_like=True)


def test_robust_merge_clean_text_match():
  df_1 = pd.DataFrame({
      "name": ["Morgan Cox", "Davis Mills"],
      "team": ["TEN", "HOU"],
      "position": ["K", "QB"],
  })
  df_2 = pd.DataFrame({
      "name": ["Davis M'ills", "Morgan Cox"],
      "team": ["HOU", "TEN"],
  })
  actual_df = ingestion_job.robust_merge(df_1, df_2, "name")
  expected_df = pd.DataFrame({
      "name": ["Morgan Cox", "Davis Mills"],
      "position": ["K", "QB"],
      "team": ["TEN", "HOU"],
  })
  pd.testing.assert_frame_equal(expected_df, actual_df, check_like=True)


def test_robust_merge_additional_join_keys_exact_match():
  df_1 = pd.DataFrame({
      "name": ["Morgan Cox", "Davis Mills"],
      "team": ["TEN", "HOU"],
      "position": ["K", "QB"],
  })
  df_2 = pd.DataFrame({
      "name": ["Davis M'ills", "Morgan Cox"],
      "team": ["HOU", "TEN"],
  })
  actual_df = ingestion_job.robust_merge(df_1, df_2, "name", ["team"])
  expected_df = pd.DataFrame({
      "name": ["Morgan Cox", "Davis Mills"],
      "team": ["TEN", "HOU"],
      "position": ["K", "QB"],
  })
  pd.testing.assert_frame_equal(expected_df, actual_df, check_like=True)


def test_robust_merge_additional_join_keys_clean_text_match():
  df_1 = pd.DataFrame({
      "name": ["Morgan Cox", "Davis Mills"],
      "team": ["TEN", "HOU"],
      "position": ["K", "QB"],
  })
  df_2 = pd.DataFrame({
      "name": ["Davis M'ills", "Morgan Cox"],
      "team": ["HOU", "TEN"],
  })
  actual_df = ingestion_job.robust_merge(df_1, df_2, "name", ["team"])
  expected_df = pd.DataFrame({
      "name": ["Morgan Cox", "Davis Mills"],
      "team": ["TEN", "HOU"],
      "position": ["K", "QB"],
  })
  pd.testing.assert_frame_equal(expected_df, actual_df, check_like=True)


def test_robust_merge_additional_join_keys_disambiguation():
  df_1 = pd.DataFrame({
      "name": ["Morgan Cox", "Davis Mills"],
      "team": ["TEN", "HOU"],
      "position": ["K", "QB"],
  })
  df_2 = pd.DataFrame({
      "name": ["Davis M'ills", "Morgan Cox", "Davis M'ills"],
      "team": ["HOU", "TEN", "NYG"],
  })
  actual_df = ingestion_job.robust_merge(df_1, df_2, "name", ["team"])
  expected_df = pd.DataFrame({
      "name": ["Morgan Cox", "Davis Mills"],
      "team": ["TEN", "HOU"],
      "position": ["K", "QB"],
  })
  pd.testing.assert_frame_equal(expected_df, actual_df, check_like=True)


def test_robust_merge_multiple_matches():
  df_1 = pd.DataFrame({
      "name": ["Morgan Cox", "Davis Mills", "Davis Mills", "Morgan Cox"],
      "team": ["TEN", "HOU", "HOU", "NYG"],
      "position": ["K", "QB", "QB", "RB"],
  })
  df_2 = pd.DataFrame({
      "name": ["Morgan Cox", "Davis Mills"],
      "team": ["TEN", "HOU"],
      "adp": [1.5, 2.1],
  })
  expected_df = pd.DataFrame({
      "name": ["Morgan Cox", "Davis Mills", "Davis Mills", "Morgan Cox"],
      "team": ["TEN", "HOU", "HOU", "NYG"],
      "position": ["K", "QB", "QB", "RB"],
      "adp": [1.5, 2.1, 2.1, None],
  })
  actual_df = ingestion_job.robust_merge(df_1, df_2, "name", ["team"])
  pd.testing.assert_frame_equal(
      expected_df.sort_values(by=["name", "team"]).reset_index(drop=True),
      actual_df.sort_values(by=["name", "team"]).reset_index(drop=True),
      check_like=True,
  )


def test_robust_merge_left_merge():
  df_1 = pd.DataFrame({
      "name": [
          "Morgan Cox",
          "D'avis Mills",
          "James McGill",
          "John Mc'Donald",
      ],
      "team": ["TEN", "HOU", "NYG", "NYG"],
      "position": ["K", "QB", "RB", "RB"],
      "college": [
          "Tennessee",
          "Stanford",
          "The University of Texas",
          "New York University",
      ],
  })
  df_2 = pd.DataFrame({
      "name": ["Davis Mills", "Morgan Cox", "Davis M'ills"],
      "team": ["HOU", "TEN", "NYG"],
      "adp": [1.5, 2.1, 3.1],
  })
  actual_df = (
      ingestion_job.robust_merge(df_1, df_2, "name", ["team"])
      .sort_values(by=["name"])
      .reset_index(drop=True)
  )
  expected_df = (
      pd.DataFrame({
          "name": [
              "Morgan Cox",
              "D'avis Mills",
              "James McGill",
              "John Mc'Donald",
          ],
          "team": ["TEN", "HOU", "NYG", "NYG"],
          "position": ["K", "QB", "RB", "RB"],
          "college": [
              "Tennessee",
              "Stanford",
              "The University of Texas",
              "New York University",
          ],
          "adp": [2.1, 1.5, None, None],
      })
      .sort_values(by=["name"])
      .reset_index(drop=True)
  )
  pd.testing.assert_frame_equal(expected_df, actual_df, check_like=True)


def test_structured_output_to_player_data_df(mock_genai_client):
  ingestion_instance = ingestion_job.Ingestion()
  structured_outputs = [
      {
          "name": "Player One",
          "team": "TEN",
          "position": "QB",
          "projected_fantasy_points_standard": 300.0,
          "projected_fantasy_points_ppr": 300.0,
          "injury_risk": "low",
      },
      {
          "name": "Player Two",
          "team": "HOU",
          "position": "RB",
          "projected_fantasy_points_standard": 200.0,
          "projected_fantasy_points_ppr": 250.0,
      },
      {
          "name": "Player Three",
          "team": "NYG",
          "position": "WR",
          "projected_fantasy_points_standard": 150.0,
      },
  ]
  expected_df = pd.DataFrame([
      {
          "name": "Player One",
          "team": "TEN",
          "position": "QB",
          "injury_risk": "low",
          "fpts": json.dumps({
              "standard": 300.0,
              "half-ppr": 300.0,
              "ppr": 300.0,
          }),
      },
      {
          "name": "Player Two",
          "team": "HOU",
          "position": "RB",
          "injury_risk": None,
          "fpts": json.dumps({
              "standard": 200.0,
              "half-ppr": 225.0,
              "ppr": 250.0,
          }),
      },
      {
          "name": "Player Three",
          "team": "NYG",
          "position": "WR",
          "injury_risk": None,
          "fpts": json.dumps({
              "standard": 150.0,
              "half-ppr": 150.0,
              "ppr": 150.0,
          }),
      },
  ])
  actual_df = ingestion_instance.structured_output_to_player_data_df(
      structured_outputs
  )
  pd.testing.assert_frame_equal(expected_df, actual_df, check_like=True)


def test_grounded_search(mock_genai_client):
  ingestion_instance = ingestion_job.Ingestion()
  entities = pd.DataFrame({
      "name": ["Player One", "Player Two"],
      "team": ["TEN", "HOU"],
      "position": ["QB", "RB"],
      "injury": [None, None],
  })
  prompt_system_instruction = "System instruction"
  prompt_user_template = "Player: {name} ({position}, {team})"

  mock_responses = [mock.Mock(), mock.Mock()]
  mock_responses[0].text = "Response for Player One"
  mock_responses[1].text = "Response for Player Two"
  mock_genai_client.models.generate_content.side_effect = mock_responses

  actual_results = ingestion_instance.grounded_search(
      entities,
      prompt_system_instruction,
      prompt_user_template,
      cols_to_include=["name", "team", "position"],
      max_workers=1,
  )

  assert actual_results, [
      "Response for Player One" == "Response for Player Two"
  ]
  assert mock_genai_client.models.generate_content.call_count == 2

  calls = mock_genai_client.models.generate_content.call_args_list
  assert "Player: Player One (QB, TEN)" == calls[0].kwargs["contents"][0].text
  assert "Player: Player Two (RB, HOU)" == calls[1].kwargs["contents"][0].text


def test_to_structured_output(mock_genai_client):
  ingestion_instance = ingestion_job.Ingestion()
  responses = ["Response 1", "Response 2"]

  mock_llm_responses = [mock.Mock(), mock.Mock()]
  mock_llm_responses[0].text = (
      '{"name": "Player One", "team": "TEN", "position": "QB",'
      ' "projected_fantasy_points_standard": 300.0,'
      ' "projected_fantasy_points_ppr": 300.0}'
  )
  mock_llm_responses[1].text = (
      '{"name": "Player Two", "team": "HOU", "position": "RB",'
      ' "projected_fantasy_points_standard": 200.0,'
      ' "projected_fantasy_points_ppr": 250.0}'
  )
  mock_genai_client.models.generate_content.side_effect = mock_llm_responses

  actual_results = ingestion_instance.to_structured_output(
      responses, ingestion_job.PlayerData, max_workers=1
  )

  expected_results = [
      json.loads(mock_llm_responses[0].text),
      json.loads(mock_llm_responses[1].text),
  ]
  assert actual_results == expected_results
  assert mock_genai_client.models.generate_content.call_count == 2


def test_run_player_data_ingestion(
    mock_genai_client,
    mock_player_data,
    mock_adp_data,
    mock_player_stats_data,
):
  with (
      mock.patch.object(
          ingestion_job.Ingestion,
          "get_all_nfl_players",
          return_value=mock_player_data,
      ) as mock_get_all_nfl_players,
      mock.patch.object(
          ingestion_job.Ingestion, "get_adps", return_value=mock_adp_data
      ) as mock_get_adps,
      mock.patch.object(
          ingestion_job.Ingestion,
          "grounded_search",
          return_value=["Grounded search response"],
      ) as mock_grounded_search,
      mock.patch.object(
          ingestion_job.Ingestion,
          "to_structured_output",
          return_value=[{
              "name": "Player One",
              "team": "TEN",
              "position": "QB",
              "projected_fantasy_points_standard": 300.0,
              "projected_fantasy_points_ppr": 300.0,
              "injury_risk": "low",
          }],
      ) as mock_to_structured_output,
      mock.patch.object(
          ingestion_job.Ingestion,
          "structured_output_to_player_data_df",
          return_value=mock_player_stats_data,
      ) as mock_structured_output_to_player_data_df,
  ):
    ingestion_instance = ingestion_job.Ingestion()
    result_df = asyncio.run(
        ingestion_job.run_player_data_ingestion(ingestion_instance)
    )

    mock_get_all_nfl_players.assert_called_once()
    mock_get_adps.assert_called_once()
    mock_grounded_search.assert_called_once()
    mock_to_structured_output.assert_called_once()
    mock_structured_output_to_player_data_df.assert_called_once()

    assert "adp" in result_df.columns
    assert len(result_df) == 1
    assert result_df.iloc[0]["name"] == "Player One"


def test_run_team_defense_ingestion(mock_genai_client):
  with (
      mock.patch.object(
          ingestion_job.Ingestion,
          "grounded_search",
          return_value=["Grounded search response"],
      ) as mock_grounded_search,
      mock.patch.object(
          ingestion_job.Ingestion,
          "to_structured_output",
          return_value=[{
              "team_name": "TEN",
              "adp": 1.0,
              "early_schedule_rank": 1,
              "consensus_projection": 100.0,
              "ceiling_projection": 120.0,
              "win_total": 10.0,
              "pressure_rate": 0.3,
              "offseason_additions": [],
          }],
      ) as mock_to_structured_output,
  ):
    ingestion_instance = ingestion_job.Ingestion()
    result_df = asyncio.run(
        ingestion_job.run_team_defense_ingestion(ingestion_instance)
    )

    mock_grounded_search.assert_called_once()
    mock_to_structured_output.assert_called_once()
    assert len(result_df) == 1
    assert result_df.iloc[0]["team_name"] == "TEN"
