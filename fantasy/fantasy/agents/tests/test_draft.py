import json

import pandas as pd
from src.agents import draft


SAMPLE_SLOTS = {
    "WR": 2,
    "TE": 1,
    "RB": 2,
    "QB": 1,
    "K": 1,
    "FLEX": 2,
    "DEF": 1,
    "BN": 5,
}

SAMPLE_DRAFT_ENDPOINT_RESPONSE = {
    "type": "snake",
    "status": "complete",
    "start_time": 1515700800000,
    "sport": "nfl",
    "settings": {
        "teams": 6,
        "slots_wr": 2,
        "slots_te": 1,
        "slots_rb": 2,
        "slots_qb": 1,
        "slots_k": 1,
        "slots_flex": 2,
        "slots_def": 1,
        "slots_bn": 5,
        "rounds": 15,
        "pick_timer": 120,
    },
    "season_type": "regular",
    "season": "2017",
    "metadata": {
        "scoring_type": "ppr",
        "name": "My Dynasty",
        "description": "",
    },
    "league_id": "257270637750382592",
    "last_picked": 1515700871182,
    "last_message_time": 1515700942674,
    "last_message_id": "257272036450111488",
    "draft_order": {"12345678": 1, "23434332": 2, "34567890": 3},
    "slot_to_roster_id": {"1": 10, "2": 3, "3": 5},
    "draft_id": "257270643320426496",
    "creators": None,
    "created": 1515700610526,
}

PLAYER_ROW_DATA = {
    "player_id": "12345678",
    "name": "Player Name",
    "team": "Team Name",
    "position": "TE",
    "injury": "No injury",
    "injury_risk": "Low injury risk",
    "status": "Active",
    "bio": "{'height': 6.5, 'weight': 150, 'age': 25, 'school': 'Stanford'}",
    "type": "2025_8_ppr",
    "fpts": 100.2,
    "adp": 1.6,
}

TEAM_ROW_DATA = {
    "team_name": "PHI",
    "adp": 1.2,
    "early_schedule_rank": 12,
    "consensus_projection": 10.2,
    "ceiling_projection": 1000.2,
    "win_total": 14,
    "pressure_rate": 32.2,
    "offseason_additions": ["Player Name"],
}

SAMPLE_PLAYER_DATA = {
    "player_id": "12345678",
    "name": "Player Name",
    "team": "Team Name",
    "position": "TE",
    "injury": "No injury",
    "injury_risk": "Low injury risk",
    "status": "Active",
    "bio": "{'height': 6.5, 'weight': 150, 'age': 25, 'school': 'Stanford'}",
    "type": "2025_8_ppr",
    "fpts": json.dumps({"ppr": 1.2, "half-ppr": 0.6, "standard": 0.0}),
    "adp": 1.6,
}

FILTER_PLAYER_DATA_DF_OUTPUT_BASE = {
    "player_id": [
        "12345678",
        "23434332",
        "34567890",
        "45678901",
    ],
    "name": [
        "Player Name",
        "Player Name",
        "Player Name",
        "Player Name",
    ],
    "team": [
        "Team Name",
        "Team Name",
        "Team Name",
        "Team Name",
    ],
    "position": [
        "TE",
        "TE",
        "TE",
        "TE",
    ],
    "injury": [
        "No injury",
        "No injury",
        "No injury",
        "No injury",
    ],
    "injury_risk": [
        "Low injury risk",
        "Low injury risk",
        "Low injury risk",
        "Low injury risk",
    ],
    "status": [
        "Active",
        "Active",
        "Active",
        "Active",
    ],
    "bio": [
        "{'height': 6.5, 'weight': 150, 'age': 25, 'school': 'Stanford'}",
        "{'height': 6.5, 'weight': 150, 'age': 25, 'school': 'Stanford'}",
        "{'height': 6.5, 'weight': 150, 'age': 25, 'school': 'Stanford'}",
        "{'height': 6.5, 'weight': 150, 'age': 25, 'school': 'Stanford'}",
    ],
    "type": [
        None,
        None,
        None,
        None,
    ],
    "fpts": [
        None,
        None,
        None,
        None,
    ],
    "adp": [
        1.6,
        1.6,
        1.6,
        None,
    ],
}

SAMPLE_LEAGUE_ENDPOINT_RESPONSE = {
    "name": "League Name",
    "status": "complete",
    "metadata": {},
    "settings": {
        "bench_lock": 0,
        "daily_waivers": 0,
        "daily_waivers_hour": 0,
        "draft_rounds": 3,
        "last_report": 13,
        "last_scored_leg": 16,
        "league_average_match": 0,
        "leg": 16,
        "max_keepers": 3,
        "num_teams": 12,
        "offseason_adds": 0,
        "pick_trading": 0,
        "playoff_teams": 6,
        "playoff_type": 0,
        "playoff_week_start": 14,
        "reserve_allow_doubtful": 0,
        "reserve_allow_out": 1,
        "reserve_allow_sus": 1,
        "reserve_slots": 1,
        "start_week": 2,
        "taxi_allow_vets": 0,
        "taxi_deadline": 0,
        "taxi_slots": 0,
        "taxi_years": 0,
        "trade_deadline": 10,
        "trade_review_days": 2,
        "type": 0,
        "waiver_budget": 100,
        "waiver_clear_days": 2,
        "waiver_day_of_week": 2,
        "waiver_type": 2,
        "was_auto_archived": 1,
    },
    "avatar": "efaefa889ae24046a53265a3c71b8b64",
    "company_id": None,
    "scoring_settings": {
        "sack": 1.0,
        "qb_hit": 0.0,
        "fgm_40_49": 4.0,
        "bonus_rec_yd_100": 0.0,
        "bonus_rush_yd_100": 0.0,
        "pass_int": -2.0,
        "pts_allow_0": 10.0,
        "bonus_pass_yd_400": 0.0,
        "pass_2pt": 2.0,
        "blk_kick_ret_yd": 0.0,
        "st_td": 6.0,
        "sack_yd": 0.0,
        "pr_td": 0.0,
        "rec_td": 6.0,
        "tkl_ast": 0.0,
        "fgm_30_39": 3.0,
        "kr_td": 0.0,
        "xpmiss": -1.0,
        "rush_td": 6.0,
        "fg_ret_yd": 0.0,
        "idp_tkl": 0.0,
        "fgm": 0.0,
        "idp_blk": 0.0,
        "rec_2pt": 2.0,
        "int_ret_yd": 0.0,
        "idp_tkl_solo": 0.0,
        "pass_att": 0.0,
        "st_fum_rec": 1.0,
        "ff": 1.0,
        "idp_int": 0.0,
        "fgmiss_30_39": -1.0,
        "rec": 1.0,
        "idp_safe": 0.0,
        "pts_allow_14_20": 1.0,
        "def_2pt": 0.0,
        "fgm_0_19": 3.0,
        "int": 2.0,
        "def_st_fum_rec": 0.0,
        "fum_lost": -2.0,
        "pts_allow_1_6": 7.0,
        "kr_yd": 0.0,
        "fgmiss_20_29": -1.0,
        "rush_att": 0.0,
        "st_tkl_solo": 0.0,
        "idp_sack": 0.0,
        "fgm_20_29": 3.0,
        "pts_allow_21_27": 0.0,
        "bonus_pass_yd_300": 0.0,
        "xpm": 1.0,
        "pass_sack": 0.0,
        "fgmiss_0_19": -1.0,
        "pass_cmp": 0.0,
        "tkl_loss": 0.0,
        "rush_2pt": 2.0,
        "def_pass_def": 0.0,
        "fum_rec": 2.0,
        "idp_pass_def": 0.0,
        "bonus_rec_yd_200": 0.0,
        "def_st_td": 0.0,
        "tkl": 0.0,
        "fgm_50p": 5.0,
        "def_td": 6.0,
        "idp_fum_rec": 0.0,
        "bonus_rush_yd_200": 0.0,
        "safe": 2.0,
        "pass_yd": 0.03999999910593033,
        "blk_kick": 2.0,
        "pass_td": 6.0,
        "tkl_solo": 0.0,
        "rush_yd": 0.10000000149011612,
        "pr_yd": 0.0,
        "fum": 0.0,
        "pts_allow_28_34": -1.0,
        "pts_allow_35p": -4.0,
        "rec_yd": 0.10000000149011612,
        "fum_ret_yd": 0.0,
        "def_st_ff": 0.0,
        "pts_allow_7_13": 4.0,
        "idp_ff": 0.0,
        "st_ff": 1.0,
        "idp_tkl_ast": 0.0,
    },
    "season": "2018",
    "season_type": "regular",
    "shard": 503,
    "sport": "nfl",
    "last_message_id": "451513482433523712",
    "last_author_avatar": "0b0c6764f4ca773e86260b43c1731dfe",
    "last_author_display_name": "Display Name 4",
    "last_author_id": "667279356739584",
    "last_author_is_bot": None,
    "last_message_attachment": None,
    "last_message_text_map": None,
    "last_message_time": 1562011712227,
    "last_pinned_message_id": "383149284520103936",
    "draft_id": "289646328508579840",
    "last_read_id": None,
    "league_id": "289646328504385536",
    "previous_league_id": "198946952535085056",
    "roster_positions": [
        "QB",
        "RB",
        "RB",
        "WR",
        "WR",
        "TE",
        "FLEX",
        "FLEX",
        "DEF",
        "BN",
        "BN",
        "BN",
        "BN",
        "BN",
        "BN",
    ],
    "bracket_id": 376175885998759936,
    "bracket_overrides_id": None,
    "group_id": None,
    "loser_bracket_id": 376175886011342848,
    "loser_bracket_overrides_id": None,
    "total_rosters": 12,
}

SAMPLE_LEAGUE_USERS_ENDPOINT_RESPONSE = [
    {
        "avatar": "cc12ec49965eb7856f84d71cf85306af",
        "display_name": "Display Name 1",
        "is_bot": None,
        "is_owner": True,
        "league_id": "289646328504385536",
        "metadata": {
            "allow_pn": "on",
            "mascot_item_type_id_leg_16": "dawg-pound",
            "mascot_item_type_id_leg_17": "dawg-pound",
            "mention_pn": "on",
            "player_nickname_update": "on",
            "team_name": "Team Name 1",
            "team_name_update": "on",
            "transaction_commissioner": "on",
            "transaction_free_agent": "on",
            "transaction_trade": "on",
            "transaction_waiver": "on",
            "user_message_pn": "on",
        },
        "settings": None,
        "user_id": "457511950237696",
    },
    {
        "avatar": "nfl_sf",
        "display_name": "Display Name 2",
        "is_bot": None,
        "is_owner": False,
        "league_id": "289646328504385536",
        "metadata": {
            "allow_pn": "off",
            "mention_pn": "on",
            "player_nickname_update": "off",
            "team_name_update": "off",
            "transaction_commissioner": "off",
            "transaction_free_agent": "off",
            "transaction_trade": "off",
            "transaction_waiver": "off",
            "user_message_pn": "off",
        },
        "settings": None,
        "user_id": "476735150112768",
    },
    {
        "avatar": "eefceb945b9159798eac0eb764d3fbc4",
        "display_name": "Display Name 3",
        "is_bot": None,
        "is_owner": False,
        "league_id": "289646328504385536",
        "metadata": {
            "allow_pn": "on",
            "mention_pn": "on",
            "player_nickname_update": "on",
            "team_name": "Team Name 3",
            "team_name_update": "on",
            "transaction_commissioner": "on",
            "transaction_free_agent": "on",
            "transaction_trade": "on",
            "transaction_waiver": "on",
            "user_message_pn": "off",
        },
        "settings": None,
        "user_id": "521611313037312",
    },
    {
        "avatar": "0b0c6764f4ca773e86260b43c1731dfe",
        "display_name": "Display Name 4",
        "is_bot": None,
        "is_owner": True,
        "league_id": "289646328504385536",
        "metadata": {
            "allow_pn": "on",
            "mention_pn": "on",
            "team_name": "Team Name 4",
        },
        "settings": None,
        "user_id": "667279356739584",
    },
    {
        "avatar": "9402d1b023f90e63d0c866c104869809",
        "display_name": "Display Name 5",
        "is_bot": None,
        "is_owner": True,
        "league_id": "289646328504385536",
        "metadata": {"allow_pn": "off", "mention_pn": "on"},
        "settings": None,
        "user_id": "720638189125632",
    },
    {
        "avatar": "1799db086bc5e636807a0ffe808dde3b",
        "display_name": "Display Name 6",
        "is_bot": None,
        "is_owner": False,
        "league_id": "289646328504385536",
        "metadata": {
            "allow_pn": "off",
            "mention_pn": "on",
            "player_nickname_update": "on",
            "team_name_update": "on",
            "transaction_commissioner": "on",
            "transaction_free_agent": "on",
            "transaction_trade": "on",
            "transaction_waiver": "on",
            "user_message_pn": "on",
        },
        "settings": None,
        "user_id": "3975968863961088",
    },
    {
        "avatar": "54c7be29a05648a0b156c6ec3ce6ffdf",
        "display_name": "Display Name 7",
        "is_bot": None,
        "is_owner": False,
        "league_id": "289646328504385536",
        "metadata": {
            "allow_pn": "on",
            "mention_pn": "on",
            "team_name": "Team Name 7",
        },
        "settings": None,
        "user_id": "31161755661385728",
    },
    {
        "avatar": "f41d6e80519da8a4fe532196a3bb34f4",
        "display_name": "Display Name 8",
        "is_bot": None,
        "is_owner": True,
        "league_id": "289646328504385536",
        "metadata": {
            "allow_pn": "on",
            "archived": "on",
            "mention_pn": "on",
            "team_name": "Team Name 8",
        },
        "settings": None,
        "user_id": "61960473868124160",
    },
    {
        "avatar": "47b27700aef00a569948cb77be68b54d",
        "display_name": "Display Name 9",
        "is_bot": None,
        "is_owner": False,
        "league_id": "289646328504385536",
        "metadata": {"allow_pn": "on", "mention_pn": "on"},
        "settings": None,
        "user_id": "76888557872365568",
    },
    {
        "avatar": "c99311341d58b4c50d6e0a6a6a0dfebf",
        "display_name": "Display Name 10",
        "is_bot": False,
        "is_owner": False,
        "league_id": "289646328504385536",
        "metadata": {
            "allow_pn": "off",
            "mascot_item_type_id_leg_16": "cheesehead",
            "mascot_item_type_id_leg_17": "cheesehead",
            "mention_pn": "on",
            "player_nickname_update": "on",
            "team_name": "Team Name 10",
            "team_name_update": "on",
            "transaction_commissioner": "on",
            "transaction_free_agent": "on",
            "transaction_trade": "on",
            "transaction_waiver": "on",
            "user_message_pn": "on",
        },
        "settings": None,
        "user_id": "189140835533586432",
    },
    {
        "avatar": "db7b742f6549b03367eb48ed1e328e5e",
        "display_name": "Display Name 11",
        "is_bot": False,
        "is_owner": False,
        "league_id": "289646328504385536",
        "metadata": {
            "allow_pn": "on",
            "mention_pn": "on",
            "player_nickname_update": "on",
            "team_name": "Team Name 11",
            "team_name_update": "on",
            "transaction_commissioner": "on",
            "transaction_free_agent": "on",
            "transaction_trade": "on",
            "transaction_waiver": "on",
            "user_message_pn": "on",
        },
        "settings": None,
        "user_id": "228297280283734016",
    },
    {
        "avatar": "a047e4610be938f0d2ceec22f5877f27",
        "display_name": "Display Name 12",
        "is_bot": False,
        "is_owner": False,
        "league_id": "289646328504385536",
        "metadata": {
            "allow_pn": "off",
            "mention_pn": "on",
            "team_name": "Team Name 12",
        },
        "settings": None,
        "user_id": "313952381563858944",
    },
    {
        "avatar": "740715586f5fecd032030346acf139c5",
        "display_name": "Display Name 13",
        "is_bot": False,
        "is_owner": False,
        "league_id": "289646328504385536",
        "metadata": {
            "allow_pn": "on",
            "mascot_message": "off",
            "mention_pn": "on",
            "player_nickname_update": "on",
            "team_name": "Team Name 13",
            "team_name_update": "on",
            "transaction_commissioner": "on",
            "transaction_free_agent": "on",
            "transaction_trade": "on",
            "transaction_waiver": "on",
            "user_message_pn": "on",
        },
        "settings": None,
        "user_id": "314278749690396672",
    },
    {
        "avatar": "fed35eef4b71cc48b383db68b9ef0c31",
        "display_name": "Display Name 14",
        "is_bot": False,
        "is_owner": False,
        "league_id": "289646328504385536",
        "metadata": {"allow_pn": "on", "mention_pn": "on"},
        "settings": None,
        "user_id": "380479821538410496",
    },
]


def get_player(**kwargs) -> draft.Player:
  player_row_data = PLAYER_ROW_DATA.copy()
  player_row_data.update(kwargs)
  player_type = player_row_data.get("type")
  adp_type = "" if pd.isna(player_type) else player_type.replace("_", " ")
  return draft.Player(
      player_id=player_row_data["player_id"],
      name=player_row_data["name"],
      team=player_row_data["team"],
      position=player_row_data["position"],
      adp_type=adp_type,
      injury=player_row_data["injury"],
      injury_risk=player_row_data["injury_risk"],
      status=player_row_data["status"],
      bio=player_row_data["bio"],
      adp=player_row_data["adp"],
      fpts=player_row_data["fpts"],
  )


def get_team(**kwargs) -> draft.Team:
  team_row_data = TEAM_ROW_DATA.copy()
  team_row_data.update(kwargs)
  return draft.Team(
      name=team_row_data["team_name"],
      adp=team_row_data["adp"],
      early_schedule_rank=team_row_data["early_schedule_rank"],
      consensus_projection=team_row_data["consensus_projection"],
      ceiling_projection=team_row_data["ceiling_projection"],
      win_total=team_row_data["win_total"],
      pressure_rate=team_row_data["pressure_rate"],
      offseason_additions=team_row_data["offseason_additions"],
  )


def get_player_data_series(**kwargs) -> pd.Series:
  sample_player_data = SAMPLE_PLAYER_DATA.copy()
  sample_player_data.update(kwargs)
  return pd.Series(sample_player_data)


def test_is_team():
  assert draft.is_team("PHI")
  assert not draft.is_team("12345678")


def test_draft_df_to_players():
  draft_obj = draft.Draft(
      SAMPLE_DRAFT_ENDPOINT_RESPONSE, player_id="667279356739584"
  )
  draft_obj.df_to_players(pd.DataFrame(PLAYER_ROW_DATA, index=[0]))
  assert len(draft_obj.player_id_to_player) == 1
  assert "12345678" in draft_obj.player_id_to_player
  assert draft_obj.player_id_to_player["12345678"].position == "TE"


def test_draft_df_to_teams():
  draft_obj = draft.Draft(
      SAMPLE_DRAFT_ENDPOINT_RESPONSE, player_id="667279356739584"
  )
  draft_obj.df_to_teams(pd.DataFrame(TEAM_ROW_DATA, index=[0]))
  assert len(draft_obj.team_id_to_team) == 1
  assert "PHI" in draft_obj.team_id_to_team
  assert draft_obj.team_id_to_team["PHI"].name == "PHI"


def test_player_lt():
  # Note this is flipped so that the highest fpts are first.
  player1 = get_player(fpts=5)
  player2 = get_player(fpts=50)
  assert player2 < player1


def test_team_roster_update_available_position():
  team_roster = draft.TeamRoster(SAMPLE_SLOTS)
  team_roster.update(get_player(position="WR"))
  assert team_roster.slots["WR"] == 1
  assert team_roster.slots["TE"] == 1
  assert team_roster.slots["FLEX"] == 2
  assert team_roster.slots["BN"] == 5
  assert len(team_roster.roster["WR"]) == 1
  assert team_roster.roster["TE"] == []
  assert team_roster.roster["FLEX"] == []
  assert team_roster.roster["BN"] == []


def test_team_roster_update_flex_position():
  team_roster = draft.TeamRoster(SAMPLE_SLOTS)
  team_roster.update(get_player(position="TE"))
  assert team_roster.slots["TE"] == 0
  assert team_roster.slots["FLEX"] == 2
  assert team_roster.slots["BN"] == 5
  team_roster.update(get_player(position="TE"))
  team_roster.update(get_player(position="TE"))
  assert team_roster.slots["FLEX"] == 0
  assert team_roster.slots["BN"] == 5
  team_roster.update(get_player(position="TE"))
  assert team_roster.slots["BN"] == 4
  assert len(team_roster.roster["FLEX"]) == 2
  assert len(team_roster.roster["BN"]) == 1


def test_team_roster_update_bench_position():
  team_roster = draft.TeamRoster(SAMPLE_SLOTS)
  team_roster.update(get_player(position="TE"))
  team_roster.update(get_player(position="TE"))
  team_roster.update(get_player(position="TE"))
  assert team_roster.slots["BN"] == 5
  team_roster.update(get_player(position="TE"))
  assert team_roster.slots["BN"] == 4


def test_team_roster_update_defense_position():
  team_roster = draft.TeamRoster(SAMPLE_SLOTS)
  assert team_roster.slots["DEF"] == 1
  team_roster.update(get_team(name="PHI"))
  assert team_roster.slots["DEF"] == 0
  assert len(team_roster.roster["DEF"]) == 1
  assert team_roster.roster["DEF"][0].name == "PHI"


def test_team_roster_undo_update():
  """Tests the undo_update method of the TeamRoster class."""
  team_roster = draft.TeamRoster(SAMPLE_SLOTS, superflex=True)

  # Add players to fill WR, then FLEX, then BN
  wr1 = get_player(player_id="wr1", position="WR")
  wr2 = get_player(player_id="wr2", position="WR")
  wr3 = get_player(player_id="wr3", position="WR")
  wr4 = get_player(player_id="wr4", position="WR")
  wr5 = get_player(player_id="wr5", position="WR")

  # 2 WR slots
  team_roster.update(wr1)
  team_roster.update(wr2)
  assert wr1 in team_roster.roster["WR"]
  assert wr2 in team_roster.roster["WR"]
  assert team_roster.slots["WR"] == 0

  # 2 FLEX slots
  team_roster.update(wr3)
  team_roster.update(wr4)
  assert wr3 in team_roster.roster["FLEX"]
  assert wr4 in team_roster.roster["FLEX"]
  assert team_roster.slots["FLEX"] == 0

  # 5 BN slots
  team_roster.update(wr5)
  assert wr5 in team_roster.roster["BN"]
  assert team_roster.slots["BN"] == 4

  # Undo in reverse order of addition
  team_roster.undo_update(wr5)
  assert wr5 not in team_roster.roster["BN"]
  assert team_roster.slots["BN"] == 5

  team_roster.undo_update(wr4)
  assert wr4 not in team_roster.roster["FLEX"]
  assert team_roster.slots["FLEX"] == 1

  team_roster.undo_update(wr3)
  assert wr3 not in team_roster.roster["FLEX"]
  assert team_roster.slots["FLEX"] == 2

  team_roster.undo_update(wr2)
  assert wr2 not in team_roster.roster["WR"]
  assert team_roster.slots["WR"] == 1

  team_roster.undo_update(wr1)
  assert wr1 not in team_roster.roster["WR"]
  assert team_roster.slots["WR"] == 2


def test_league_initialization():
  league_obj = draft.League(
      SAMPLE_LEAGUE_ENDPOINT_RESPONSE, SAMPLE_LEAGUE_USERS_ENDPOINT_RESPONSE
  )
  assert league_obj.league_id == "289646328504385536"
  assert league_obj.name == "League Name"
  assert len(league_obj.user_id_to_team_name) == 14
  assert league_obj.user_id_to_team_name["314278749690396672"] == "Team Name 13"
  assert (
      league_obj.user_id_to_team_name["380479821538410496"] == "Display Name 14"
  )


def test_draft_get_scoring_match():
  draft_obj = draft.Draft(
      SAMPLE_DRAFT_ENDPOINT_RESPONSE, player_id="667279356739584"
  )
  draft_obj.scoring_type = "ppr"
  assert draft_obj._get_scoring_match("ppr") == 1.0
  assert draft_obj._get_scoring_match("half-ppr") == 0.5
  assert draft_obj._get_scoring_match("standard") == 0.0
  assert draft_obj._get_scoring_match(None) == -float("inf")
  draft_obj.scoring_type = "half-ppr"
  assert draft_obj._get_scoring_match("ppr") == 0.25
  assert draft_obj._get_scoring_match("half-ppr") == 1.0
  assert draft_obj._get_scoring_match("standard") == 0.0
  assert draft_obj._get_scoring_match(None) == -float("inf")


def test_draft_get_team_match():
  draft_obj = draft.Draft(
      SAMPLE_DRAFT_ENDPOINT_RESPONSE, player_id="667279356739584"
  )
  draft_obj.num_teams = 13
  assert draft_obj._get_team_match(14) == 1.0
  assert draft_obj._get_team_match(13) == 2.0
  assert draft_obj._get_team_match(8) == -5.0
  assert draft_obj._get_team_match(None) == -float("inf")


def test_draft_filter_player_data_df():
  draft_obj = draft.Draft(
      SAMPLE_DRAFT_ENDPOINT_RESPONSE, player_id="667279356739584"
  )

  input_df = pd.DataFrame([
      get_player_data_series(player_id="12345678", type="2025_8_ppr"),
      get_player_data_series(player_id="23434332", type="2025_8_ppr"),
      get_player_data_series(player_id="34567890", type="2025_8_ppr"),
      get_player_data_series(player_id="12345678", type="2025_10_ppr"),
      get_player_data_series(player_id="23434332", type="2025_10_ppr"),
      get_player_data_series(player_id="23434332", type="2025_12_ppr"),
      get_player_data_series(player_id="12345678", type="2025_12_ppr"),
      get_player_data_series(player_id="23434332", type="2025_14_ppr"),
      get_player_data_series(player_id="12345678", type="2025_8_half-ppr"),
      get_player_data_series(player_id="23434332", type="2025_8_half-ppr"),
      get_player_data_series(player_id="12345678", type="2025_10_half-ppr"),
      get_player_data_series(player_id="12345678", type="2025_12_half-ppr"),
      get_player_data_series(player_id="23434332", type="2025_14_half-ppr"),
      get_player_data_series(player_id="23434332", type="2025_8_standard"),
      get_player_data_series(player_id="34567890", type="2025_8_standard"),
      get_player_data_series(player_id="45678901", type=None, adp=None),
  ])

  expected_dictionary = FILTER_PLAYER_DATA_DF_OUTPUT_BASE.copy()
  draft_obj.num_teams = 13

  draft_obj.scoring_type = "ppr"
  expected_dictionary.update({
      "type": [
          "2025_12_ppr",  # 12345678
          "2025_14_ppr",  # 23434332
          "2025_8_ppr",  # 34567890
          None,  # 45678901
      ],
      "fpts": [
          1.2,  # 12345678
          1.2,  # 23434332
          1.2,  # 34567890
          1.2,  # 45678901
      ],
  })
  expected_df = pd.DataFrame(expected_dictionary)
  actual_df = draft_obj.filter_player_data_df(input_df)
  pd.testing.assert_frame_equal(
      actual_df.reset_index(drop=True),
      expected_df.reset_index(drop=True),
      check_like=True,
  )

  draft_obj.scoring_type = "half-ppr"
  expected_dictionary.update({
      "type": [
          "2025_12_half-ppr",  # 12345678
          "2025_14_half-ppr",  # 23434332
          "2025_8_ppr",  # 34567890
          None,  # 45678901
      ],
      "fpts": [
          0.6,  # 12345678
          0.6,  # 23434332
          0.6,  # 34567890
          0.6,  # 45678901
      ],
  })
  expected_df = pd.DataFrame(expected_dictionary)
  actual_df = draft_obj.filter_player_data_df(input_df)
  pd.testing.assert_frame_equal(
      actual_df.reset_index(drop=True),
      expected_df.reset_index(drop=True),
      check_like=True,
  )

  draft_obj.scoring_type = "standard"
  expected_dictionary.update({
      "type": [
          "2025_12_half-ppr",  # 12345678
          "2025_8_standard",  # 23434332
          "2025_8_standard",  # 34567890
          None,  # 45678901
      ],
      "fpts": [
          0.0,  # 12345678
          0.0,  # 23434332
          0.0,  # 34567890
          0.0,  # 45678901
      ],
  })
  expected_df = pd.DataFrame(expected_dictionary)
  actual_df = draft_obj.filter_player_data_df(input_df)
  pd.testing.assert_frame_equal(
      actual_df.reset_index(drop=True),
      expected_df.reset_index(drop=True),
      check_like=True,
  )


def test_state_picks_till_my_next_turn_linear():
  draft_obj = draft.Draft(SAMPLE_DRAFT_ENDPOINT_RESPONSE, player_id="12345678")
  state = draft.State(draft_obj)
  draft_obj.draft_order_type = "linear"
  draft_obj.draft_order = {"12345678": 1, "23434332": 2, "34567890": 3}
  draft_obj.num_teams = 3

  draft_obj.my_player_id = "12345678"
  state.pick_no = 1
  result = state.picks_till_my_next_turn(state.pick_no)
  assert result[0] == 3
  assert result[1]
  state.pick_no = 2
  result = state.picks_till_my_next_turn(state.pick_no)
  assert result[0] == 2
  assert not result[1]
  state.pick_no = 3
  result = state.picks_till_my_next_turn(state.pick_no)
  assert result[0] == 1
  assert not result[1]
  state.pick_no = 4
  result = state.picks_till_my_next_turn(state.pick_no)
  assert result[0] == 3
  assert result[1]
  state.pick_no = 5
  result = state.picks_till_my_next_turn(state.pick_no)
  assert result[0] == 2
  assert not result[1]
  state.pick_no = 6
  result = state.picks_till_my_next_turn(state.pick_no)
  assert result[0] == 1
  assert not result[1]
  draft_obj.my_player_id = "23434332"
  state.pick_no = 1
  result = state.picks_till_my_next_turn(state.pick_no)
  assert result[0] == 1
  assert not result[1]
  state.pick_no = 2
  result = state.picks_till_my_next_turn(state.pick_no)
  assert result[0] == 3
  assert result[1]
  state.pick_no = 3
  result = state.picks_till_my_next_turn(state.pick_no)
  assert result[0] == 2
  assert not result[1]
  state.pick_no = 4
  result = state.picks_till_my_next_turn(state.pick_no)
  assert result[0] == 1
  assert not result[1]
  state.pick_no = 5
  result = state.picks_till_my_next_turn(state.pick_no)
  assert result[0] == 3
  assert result[1]
  state.pick_no = 6
  result = state.picks_till_my_next_turn(state.pick_no)
  assert result[0] == 2
  assert not result[1]
  draft_obj.my_player_id = "34567890"
  state.pick_no = 1
  result = state.picks_till_my_next_turn(state.pick_no)
  assert result[0] == 2
  assert not result[1]
  state.pick_no = 2
  result = state.picks_till_my_next_turn(state.pick_no)
  assert result[0] == 1
  assert not result[1]
  state.pick_no = 3
  result = state.picks_till_my_next_turn(state.pick_no)
  assert result[0] == 3
  assert result[1]
  state.pick_no = 4
  result = state.picks_till_my_next_turn(state.pick_no)
  assert result[0] == 2
  assert not result[1]
  state.pick_no = 5
  result = state.picks_till_my_next_turn(state.pick_no)
  assert result[0] == 1
  assert not result[1]
  state.pick_no = 6
  result = state.picks_till_my_next_turn(state.pick_no)
  assert result[0] == 3
  assert result[1]


def test_state_picks_till_my_next_turn_snake():
  draft_obj = draft.Draft(SAMPLE_DRAFT_ENDPOINT_RESPONSE, player_id="12345678")
  state = draft.State(draft_obj)
  draft_obj.draft_order_type = "snake"
  draft_obj.draft_order = {"12345678": 1, "23434332": 2, "34567890": 3}
  draft_obj.num_teams = 3

  draft_obj.my_player_id = "12345678"
  state.pick_no = 1
  result = state.picks_till_my_next_turn(state.pick_no)
  assert result[0] == 5
  assert result[1]
  state.pick_no = 2
  result = state.picks_till_my_next_turn(state.pick_no)
  assert result[0] == 4
  assert not result[1]
  state.pick_no = 3
  result = state.picks_till_my_next_turn(state.pick_no)
  assert result[0] == 3
  assert not result[1]
  state.pick_no = 4
  result = state.picks_till_my_next_turn(state.pick_no)
  assert result[0] == 2
  assert not result[1]
  state.pick_no = 5
  result = state.picks_till_my_next_turn(state.pick_no)
  assert result[0] == 1
  assert not result[1]
  state.pick_no = 6
  result = state.picks_till_my_next_turn(state.pick_no)
  assert result[0] == 1
  assert result[1]
  draft_obj.my_player_id = "23434332"
  state.pick_no = 1
  result = state.picks_till_my_next_turn(state.pick_no)
  assert result[0] == 1
  assert not result[1]
  state.pick_no = 2
  result = state.picks_till_my_next_turn(state.pick_no)
  assert result[0] == 3
  assert result[1]
  state.pick_no = 3
  result = state.picks_till_my_next_turn(state.pick_no)
  assert result[0] == 2
  assert not result[1]
  state.pick_no = 4
  result = state.picks_till_my_next_turn(state.pick_no)
  assert result[0] == 1
  assert not result[1]
  state.pick_no = 5
  result = state.picks_till_my_next_turn(state.pick_no)
  assert result[0] == 3
  assert result[1]
  state.pick_no = 6
  result = state.picks_till_my_next_turn(state.pick_no)
  assert result[0] == 2
  assert not result[1]
  draft_obj.my_player_id = "34567890"
  state.pick_no = 1
  result = state.picks_till_my_next_turn(state.pick_no)
  assert result[0] == 2
  assert not result[1]
  state.pick_no = 2
  result = state.picks_till_my_next_turn(state.pick_no)
  assert result[0] == 1
  assert not result[1]
  state.pick_no = 3
  result = state.picks_till_my_next_turn(state.pick_no)
  assert result[0] == 1
  assert result[1]
  state.pick_no = 4
  result = state.picks_till_my_next_turn(state.pick_no)
  assert result[0] == 5
  assert result[1]
  state.pick_no = 5
  result = state.picks_till_my_next_turn(state.pick_no)
  assert result[0] == 4
  assert not result[1]
  state.pick_no = 6
  result = state.picks_till_my_next_turn(state.pick_no)
  assert result[0] == 3
  assert not result[1]


def test_state_calculate_user_vbd_metrics():
  player_id = "667279356739584"
  sample_draft_endpoint_response = SAMPLE_DRAFT_ENDPOINT_RESPONSE.copy()
  sample_draft_endpoint_response["draft_order"] = {"667279356739584": 2}
  sample_draft_endpoint_response["type"] = "linear"
  sample_draft_endpoint_response["settings"]["teams"] = 3
  sample_draft_endpoint_response["settings"]["slots_wr"] = 1
  sample_draft_endpoint_response["settings"]["superflex"] = False
  draft_obj = draft.Draft(sample_draft_endpoint_response, player_id)

  player1 = get_player(player_id="p1", position="WR", fpts=90)
  player2 = get_player(player_id="p2", position="WR", fpts=100)
  player3 = get_player(player_id="p3", position="WR", fpts=70)
  player4 = get_player(player_id="p4", position="WR", fpts=80)
  player5 = get_player(player_id="p5", position="WR", fpts=60)
  players = [player1, player2, player3, player4, player5]
  draft_obj.player_id_to_player = {p.player_id: p for p in players}

  state = draft.State(draft_obj)
  assert len(state._fpts_available["WR"]) == 5

  state.calculate_user_vbd_metrics("WR")
  assert player1.vona == 0
  assert player1.vols == 10
  assert player1.vorp == 20
  assert player2.vona == 10
  assert player2.vols == 20
  assert player2.vorp == 30
  assert player3.vona == -20
  assert player3.vols == -10
  assert player3.vorp == 0
  assert player4.vona == -10
  assert player4.vols == 0
  assert player4.vorp == 10
  assert player5.vona == -30
  assert player5.vols == -20
  assert player5.vorp == -10

  state.process_pick({
      "player_id": "p2",
      "picked_by": "",
      "pick_no": 1,
      "round": 1,
  })
  assert player1.vona == 30
  assert player3.vona == 10
  assert player4.vona == 20
  assert player5.vona == 0


def test_state_process_and_undo_pick():
  """Tests processing and undoing a pick in the draft State."""
  player_id = "23434332"
  draft_obj = draft.Draft(SAMPLE_DRAFT_ENDPOINT_RESPONSE, player_id)
  player1 = get_player(
      player_id="p1", position="WR", fpts=90, vols=10, vona=10, vorp=10
  )
  draft_obj.player_id_to_player = {"p1": player1}
  draft_obj.player_ids = [player_id]
  state = draft.State(draft_obj)

  original_vbd_calc = state.calculate_user_vbd_metrics
  state.calculate_user_vbd_metrics = lambda pos: None

  pick_data = {
      "player_id": "p1",
      "picked_by": player_id,
      "pick_no": 1,
      "round": 1,
  }

  assert player1 in state._fpts_available["WR"]
  state.process_pick(pick_data)

  assert state.pick_no == 1
  assert state.current_round == 1
  assert player1 not in state._fpts_available["WR"]
  assert player1 in state.player_id_to_picks[player_id]

  state.calculate_user_vbd_metrics = original_vbd_calc
  # The values don't matter as much as checking that they are changed.
  player1.vona = -1
  player1.vols = -1
  player1.vorp = -1

  state.undo_pick(pick_data)
  assert player1 in state._fpts_available["WR"]
  assert player1 not in state.player_id_to_picks[player_id]
  # After undoing, metrics should be recalculated
  assert player1.vona != -1
