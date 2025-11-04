"""The ingestion pipeline for fantasy player data.

This file contains the ingestion pipeline for fantasy player data. It
retrieves player data from the Sleeper API, Fantasy Football Calculator, and
Gemini, augments the data with fantasy football stats, and stores the data in a
SQLite database. This binary will run on a cron job to ensure that the player
and defense data is up-to-date.
"""

import asyncio
import concurrent.futures
import datetime
import json
import logging
import re
import string
from typing import Any, Optional

from common import constants
from common import enums
from common import utils
from google import genai
import numpy as np
import pandas as pd
import pydantic
import requests

from . import prompts


Field = pydantic.Field
types = genai.types

logging.basicConfig(
    level="INFO", format="%(asctime)s - %(levelname)s - %(message)s"
)


class DefenseData(pydantic.BaseModel):
  """Comprehensive Pydantic model for an NFL team's defense data."""

  team_name: enums.Teams = Field(..., description="Team's abbreviation.")
  adp: float = Field(..., description="Team's Average Draft Position.")
  early_schedule_rank: int = Field(
      ..., description="Team's early schedule rank."
  )
  consensus_projection: float = Field(
      ..., description="Team's consensus projection."
  )
  ceiling_projection: float = Field(
      ..., description="Team's ceiling projection."
  )
  win_total: float = Field(
      0.0,
      description=(
          "The projected number of wins for the team, based on Vegas odds."
      ),
  )
  pressure_rate: float = Field(
      0.0,
      description=(
          "The percentage of plays where the defense generates pressure on the"
          " quarterback."
      ),
  )
  offseason_additions: list[str] = Field(
      default_factory=list,
      description=(
          "A list of significant defensive players added in the offseason via"
          " the draft or free agency."
      ),
  )


class PlayerData(pydantic.BaseModel):
  """Comprehensive Pydantic model for an NFL player's data."""

  name: str = Field(..., description="Player's first and last name.")
  team: enums.Teams = Field(..., description="Player's team abbreviation.")
  position: enums.Positions = Field(
      ..., description="Player's primary position (e.g., QB, RB, WR, K)."
  )
  projected_fantasy_points_standard: float = Field(
      ..., description="Player's projected fantasy points (Non-PPR/Standard)."
  )
  projected_fantasy_points_ppr: float = Field(
      ..., description="Player's projected fantasy points (PPR)."
  )
  injury_risk: Optional[str] = Field(
      "",
      description=(
          "String representing the player's injury risk (e.g., 'low', 'medium',"
          " 'high')."
      ),
  )


class Ingestion:
  """Ingestion class for player data."""

  def __init__(self, session: Optional[requests.Session] = None):
    self.client = genai.Client(
        http_options=types.HttpOptions(
            retry_options=types.HttpRetryOptions(initial_delay=6, attempts=10)
        ),
    )
    self.session = session or requests.Session()

    self.game_modes = constants.GAME_MODES
    self.teams = [
        8,
        10,
        12,
        14,
    ]  # Number of teams supported by Fantasy Football Calculator
    self.year = datetime.datetime.now().year

  def get_all_nfl_players(self) -> pd.DataFrame:
    """Get all NFL players from the Sleeper API."""

    def _filter_draftable_positions(positions):
      if positions is None:
        return []
      return [pos for pos in positions if pos in constants.OFFENSIVE_POSITIONS]

    data = utils.make_request(
        f"{constants.SLEEPER_API_BASE_URL}/players/nfl", self.session
    )
    df = pd.DataFrame.from_dict(data, orient="index")
    df["fantasy_positions"] = df["fantasy_positions"].apply(
        _filter_draftable_positions
    )
    draftable_players = df[
        df["team"].notna()
        & (df["sport"] == "nfl")
        & df["active"]
        & (df["fantasy_positions"].str.len() > 0)
        & (
            df["metadata"].apply(
                lambda x: isinstance(x, dict) and x.get("rookie_year")
            )
        )
    ].copy()

    mask = ~draftable_players["position"].isin(constants.OFFENSIVE_POSITIONS)
    if mask.any():
      draftable_players.loc[mask, "position"] = draftable_players.loc[
          mask, "fantasy_positions"
      ].str[0]

    draftable_players["name"] = (
        draftable_players["first_name"] + " " + draftable_players["last_name"]
    )
    # There exists some outdated data where OAK is still used instead of LV.
    draftable_players["team"] = draftable_players["team"].replace("OAK", "LV")
    draftable_players["rookie_year"] = draftable_players["metadata"].apply(
        lambda metadata: metadata["rookie_year"] if metadata else None
    )
    bio_cols = [
        "height",
        "weight",
        "age",
        "years_exp",
        "college",
        "high_school",
        "rookie_year",
    ]
    draftable_players["bio"] = [
        json.dumps(row)
        for row in draftable_players[bio_cols].to_dict(orient="records")
    ]
    injury_cols = ["injury_status", "injury_body_part"]
    draftable_players["injury"] = [
        json.dumps(row)
        for row in draftable_players[injury_cols].to_dict(orient="records")
    ]
    final_df = draftable_players[[
        "player_id",
        "name",
        "team",
        "position",
        "status",
        "injury",
        "bio",
    ]].reset_index(drop=True)
    logging.info("Found %d draftable players.", len(final_df))
    return final_df

  def get_adps(self) -> pd.DataFrame:
    """Get all ADPs for the given teams and game modes using thread pool."""
    url_template = f"{constants.FANTASY_FOOTBALL_CALCULATOR_BASE_URL}/adp/{{}}?teams={{}}&year={{}}"
    endpoints = []
    for game_mode in self.game_modes:
      for team in self.teams:
        endpoint = url_template.format(game_mode, team, self.year)
        endpoints.append(endpoint)

    final_column_names = ["name", "team", "position", "adp", "type"]
    dtypes_mapping = {
        "name": "object",
        "team": "object",
        "position": "object",
        "adp": "float64",
        "type": "object",
    }

    def fetch_adp(endpoint: str) -> Optional[pd.DataFrame]:
      logging.debug("Fetching ADPs for %s", endpoint)

      empty_result_df = pd.DataFrame(columns=final_column_names).astype(
          dtypes_mapping
      )

      data = utils.make_request(endpoint, self.session)
      if data["status"] == "Success":
        meta, players_list = data["meta"], data["players"]
        if not players_list:
          logging.warning("No players found for %s", endpoint)
          return empty_result_df

        meta["type"] = meta["type"].lower().replace("non-ppr", "standard")
        df = pd.DataFrame.from_dict(players_list)
        df["type"] = f'{self.year}_{meta["teams"]}_{meta["type"]}'

        # Special case: Match Sleeper API to Fantasy Football Calculator.
        df["position"] = df["position"].replace("PK", "K")
        df["name"] = (
            df["name"]
            .str.strip()
            .str.replace("Marquise Brown", "Hollywood Brown", regex=False)
        )

        return df[final_column_names]
      else:
        logging.warning("Failed to fetch ADPs for %s", endpoint)
        return empty_result_df

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
      results = executor.map(fetch_adp, endpoints)
    final_df = pd.concat(
        [result for result in results if result is not None], ignore_index=True
    ).reset_index(drop=True)
    if not final_df.empty and "name" in final_df.columns:
      final_df = final_df[final_df["name"].apply(clean_text) != ""].reset_index(
          drop=True
      )
    logging.info("Found %d ADPs.", len(final_df))
    return final_df

  def structured_output_to_player_data_df(
      self, structured_outputs: list[dict[str, Any]]
  ) -> pd.DataFrame:
    """Convert structured output responses to a DataFrame."""
    rows = []
    for data in structured_outputs:
      try:
        standard_fpts = data.pop("projected_fantasy_points_standard")
        ppr_fpts = data.pop("projected_fantasy_points_ppr", standard_fpts)
        rows.append({
            "name": data.pop("name"),
            "team": data.pop("team"),
            "position": data.pop("position"),
            "injury_risk": data.pop("injury_risk", None),
            "fpts": json.dumps({
                "standard": standard_fpts,
                "half-ppr": (ppr_fpts + standard_fpts) / 2.0,
                "ppr": ppr_fpts,
            }),
        })
      except KeyError as e:
        logging.exception(
            "Failed to process structured output (%s): %s", data, e
        )
        continue

    df = pd.DataFrame(rows)
    if not df.empty and "name" in df.columns:
      df = df[df["name"].apply(clean_text) != ""].reset_index(drop=True)
    logging.info("Player data DataFrame has %d rows.", len(df))
    return df

  def grounded_search(
      self,
      entities: pd.DataFrame,
      prompt_system_instruction: str,
      prompt_user_template: str,
      cols_to_include: list[str] = None,
      max_workers: int = 2,
      model: str = "gemini-2.5-flash",
  ) -> list[str]:
    """Performs a grounded search using the GenAI API.

    Args:
      entities: A DataFrame where each row represents an entity to search for.
      prompt_system_instruction: The system instruction for the GenAI model.
      prompt_user_template: A template string for the user prompt, which will be
        formatted with each entity's data.
      cols_to_include: An optional list of columns from `entities` to include in
        the prompt formatting.
      max_workers: The max number of threads to use for concurrent API calls.
      model: The name of the GenAI model to use.

    Returns:
      A list of strings, where each string is the response from the grounded
      search for each entity.
    """
    if cols_to_include:
      entities = entities[cols_to_include].copy()

    config = types.GenerateContentConfig(
        system_instruction=prompt_system_instruction,
        tools=[types.Tool(google_search=types.GoogleSearch())],
    )
    queries = [
        prompt_user_template.format(**entity._asdict())
        for entity in entities.itertuples(index=False)
    ]

    def fetch_data(query: str) -> Optional[str]:
      response = self.client.models.generate_content(
          model=model,
          contents=[types.Part(text=query)],
          config=config,
      )
      return response.text

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=max_workers
    ) as executor:
      results = list(executor.map(fetch_data, queries))
    logging.info("Fetched %d grounded search responses.", len(results))
    return results

  def to_structured_output(
      self,
      responses: list[str],
      pydantic_model: pydantic.BaseModel,
      model: str = "gemini-2.5-flash-lite",
      max_workers: int = 3,
  ) -> list[dict[str, Any]]:
    """Convert grounded search responses to structured output."""
    config = types.GenerateContentConfig(
        system_instruction=prompts.STRUCTURED_OUTPUT_SYSTEM_INSTRUCTION.format(
            pydantic_model.model_json_schema()
        ),
        response_mime_type="application/json",
        response_schema=pydantic_model,
    )
    queries = [
        prompts.STRUCTURED_OUTPUT_USER_PROMPT.format(response)
        for response in responses
    ]

    def convert_response(query: str) -> Optional[str]:
      response = self.client.models.generate_content(
          model=model,
          contents=[types.Part(text=query)],
          config=config,
      )
      return response.text

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=max_workers
    ) as executor:
      structured_outputs = executor.map(convert_response, queries)
    results = []
    for structured_output in structured_outputs:
      try:
        if structured_output and structured_output.strip():
          clean_output = structured_output
          if "```" in clean_output:
            match = re.search(r"\{.*\}", clean_output, re.DOTALL)
            if match:
              clean_output = match.group(0)
          results.append(json.loads(clean_output))
        else:
          logging.warning("Skipping empty structured output response.")
      except json.JSONDecodeError as e:
        logging.exception(
            "Failed to parse structured output (%s): %s", structured_output, e
        )
        continue
    logging.info("Converted %d responses to structured output.", len(results))
    return results


def clean_text(s: str) -> str:
  """Lowercases, removes punctuation (except space), and strips whitespace."""
  if pd.isna(s):
    return ""
  text = str(s).strip()
  if text.lower() == "none":
    return ""
  text = re.sub(r" (Jr|Sr|\b[IVXLCDM]+\b)\.?$", "", text, flags=re.IGNORECASE)
  return (
      text.lower().translate(str.maketrans("", "", string.punctuation)).strip()
  )


def robust_merge(
    df_1: pd.DataFrame,
    df_2: pd.DataFrame,
    key: str,
    additional_join_keys: Optional[list[str]] = None,
) -> pd.DataFrame:
  """Merges two DataFrames on a key, handling fuzzy matches and disambiguation.

  This function performs a left merge on a standardized version of the join
  keys,
  which are lowercased and stripped of punctuation. This ensures all rows from
  `df_1` are kept. For one-to-many matches, it uses `additional_join_keys`
  to select the single best match. Column conflicts are resolved using
  `combine_first`.

  Args:
      df_1 (pd.DataFrame): The primary DataFrame.
      df_2 (pd.DataFrame): The secondary DataFrame.
      key (str): The common join key.
      additional_join_keys (Optional[list[str]]): Tie-breaker keys for
        disambiguation.

  Returns:
      pd.DataFrame: The merged DataFrame.

  Raises:
      ValueError: If a join key is missing from either DataFrame.
  """
  if additional_join_keys is None:
    additional_join_keys = []

  for k in [key] + additional_join_keys:
    if k not in df_1.columns or k not in df_2.columns:
      raise ValueError(f'Key "{k}" not found in one of the DataFrames')

  suffixes = ("_df1", "_df2")
  df1, df2 = df_1.copy(), df_2.copy()
  df1["_id1"], df2["_id2"] = np.arange(len(df1)), np.arange(len(df2))

  df1["_clean_key"] = df1[key].apply(clean_text)
  df2["_clean_key"] = df2[key].apply(clean_text)

  clean_additional_keys = [f"_{k}_clean" for k in additional_join_keys]
  for k in additional_join_keys:
    df1[f"_{k}_clean"] = df1[k].apply(clean_text)
    df2[f"_{k}_clean"] = df2[k].apply(clean_text)

  on_keys = ["_clean_key"] + clean_additional_keys

  merged_df = pd.merge(
      df1,
      df2,
      left_on=on_keys,
      right_on=on_keys,
      how="left",
      suffixes=suffixes,
  )

  unmatched_df2_names = df2[
      ~df2["_id2"].isin(merged_df["_id2"].dropna().unique())
  ]["name"].tolist()
  if unmatched_df2_names:
    logging.warning(
        "The following players were not matched: %s", unmatched_df2_names
    )

  if merged_df["_id1"].duplicated().any():
    scores = np.zeros(len(merged_df), dtype=int)
    for k in additional_join_keys:
      col1, col2 = f"{k}{suffixes[0]}", f"{k}{suffixes[1]}"
      if col1 in merged_df and col2 in merged_df:
        scores += (
            merged_df[col1].notna() & (merged_df[col1] == merged_df[col2])
        ).to_numpy(dtype=int)

    merged_df["_tiebreaker_score"] = scores
    idx = merged_df.groupby("_id1")["_tiebreaker_score"].idxmax()
    merged_df = merged_df.loc[idx]

  final_df = merged_df.copy()

  for col in final_df.columns:
    if col.endswith(suffixes[0]):
      base_name = col[: -len(suffixes[0])]
      if base_name in df_2.columns:
        col_df2 = f"{base_name}{suffixes[1]}"
        final_df[base_name] = final_df[col].combine_first(final_df[col_df2])
      else:
        final_df[base_name] = final_df[col]

  cols_to_drop = [
      c
      for c in final_df.columns
      if c.startswith("_") or c.endswith(suffixes[0]) or c.endswith(suffixes[1])
  ]
  return final_df.drop(columns=cols_to_drop, errors="ignore")


def save_to_sqlite(df: pd.DataFrame, table_name: str) -> None:
  """Save the player data DataFrame to SQLite."""
  conn = None
  try:
    conn = utils.connect_to_sqlite()
    utils.write_df_to_sqlite(conn, df, table_name)
    logging.info("Successfully wrote data to SQLite.")
  except Exception as e:
    logging.exception("Failed to write data to SQLite: %s", e)
    raise
  finally:
    if conn:
      utils.close_sqlite_connection(conn)


async def run_player_data_ingestion(
    ingestion_instance: Ingestion,
) -> pd.DataFrame:
  """Run the player data ingestion pipeline."""
  logging.info("Running player data ingestion...")

  players_df = await asyncio.to_thread(ingestion_instance.get_all_nfl_players)
  adps_df = await asyncio.to_thread(ingestion_instance.get_adps)
  grounded_search_responses = await asyncio.to_thread(
      ingestion_instance.grounded_search,
      players_df.assign(year=ingestion_instance.year),
      prompts.PLAYER_GROUNDED_SEARCH_SYSTEM_INSTRUCTION.format(
          ingestion_instance.year, PlayerData.model_json_schema()
      ),
      prompts.PLAYER_GROUNDED_SEARCH_USER_PROMPT,
      cols_to_include=["year", "position", "name", "team"],
      max_workers=7,
      model="gemini-2.5-flash",
  )
  structured_output = await asyncio.to_thread(
      ingestion_instance.to_structured_output,
      grounded_search_responses,
      pydantic_model=PlayerData,
      model="gemini-2.5-flash-lite",
      max_workers=8,
  )
  player_stats_df = await asyncio.to_thread(
      ingestion_instance.structured_output_to_player_data_df,
      structured_output,
  )

  key = "name"
  additional_join_keys = ["team", "position"]
  augmented_players_stats_df = robust_merge(
      players_df,
      player_stats_df,
      key,
      additional_join_keys,
  )
  logging.info(
      "Augmented players stats DataFrame has %d rows.",
      len(augmented_players_stats_df),
  )
  player_data_df = robust_merge(
      augmented_players_stats_df,
      adps_df,
      key,
      additional_join_keys,
  )
  logging.info(
      "Player data DataFrame has %d rows.",
      len(player_data_df),
  )
  return player_data_df


async def run_team_defense_ingestion(
    ingestion_instance: Ingestion,
) -> pd.DataFrame:
  """Run the team defense ingestion pipeline."""
  team_abbreviations = list(enums.Teams.__members__.values())
  grounded_search_responses = await asyncio.to_thread(
      ingestion_instance.grounded_search,
      pd.DataFrame({"team": team_abbreviations}).assign(
          year=ingestion_instance.year
      ),
      prompts.TEAM_GROUNDED_SEARCH_SYSTEM_INSTRUCTION.format(
          DefenseData.model_json_schema()
      ),
      prompts.TEAM_GROUNDED_SEARCH_USER_PROMPT,
      cols_to_include=["year", "team"],
      max_workers=7,
      model="gemini-2.5-flash",
  )
  structured_output = await asyncio.to_thread(
      ingestion_instance.to_structured_output,
      grounded_search_responses,
      pydantic_model=DefenseData,
      model="gemini-2.5-flash-lite",
      max_workers=8,
  )

  for item in structured_output:
    if "offseason_additions" in item and isinstance(
        item["offseason_additions"], list
    ):
      item["offseason_additions"] = json.dumps(item["offseason_additions"])

  logging.info(structured_output)
  final_df = pd.DataFrame(structured_output)
  logging.info(
      "Team defense DataFrame has %d rows. Expected %d rows.",
      len(final_df),
      len(team_abbreviations),
  )
  return final_df


async def run() -> None:
  """Run the ingestion pipeline."""
  ingestion_instance = Ingestion()

  player_data_df = await run_player_data_ingestion(ingestion_instance)
  await asyncio.to_thread(
      save_to_sqlite, player_data_df, constants.PLAYER_DATA_TABLE_NAME
  )

  team_defense_df = await run_team_defense_ingestion(ingestion_instance)
  await asyncio.to_thread(
      save_to_sqlite, team_defense_df, constants.TEAM_DEFENSE_TABLE_NAME
  )


if __name__ == "__main__":
  asyncio.run(run())
