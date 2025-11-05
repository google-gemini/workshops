"""General-purpose utility functions.

This file contains a collection of small, reusable functions used throughout the
project to perform common tasks and avoid code duplication.
"""

import logging
import os
import sqlite3
from typing import Any, Dict
import aiohttp
import pandas as pd
import requests
from . import constants


def make_request(
    url: str, session: requests.Session | None = None
) -> Dict[str, Any]:
  """Make a sync request.

  Args:
      url: The API endpoint to request
      session: The requests session to use for the request

  Returns:
      The JSON response from the API

  Raises:
      Exception: If the request fails
  """
  logging.debug("Making request to %s", url)

  try:
    response = session.get(url) if session else requests.get(url)
    response.raise_for_status()
    return response.json()
  except requests.exceptions.RequestException as e:
    logging.exception("Error making request to %s: %s", url, e)
    raise Exception(f"Failed to fetch data from API: {e}") from e


async def make_async_request(
    endpoint: str, session: aiohttp.ClientSession
) -> Dict[str, Any]:
  """Make an async request to the Sleeper API.

  Args:
      endpoint: The API endpoint to request
      session: The aiohttp session to use for the request

  Returns:
      The JSON response from the API

  Raises:
      Exception: If the request fails
  """
  url = f"{constants.SLEEPER_API_BASE_URL}{endpoint}"
  logging.debug("Making async request to %s", url)

  try:
    async with session.get(url) as resp:
      resp.raise_for_status()
      return await resp.json()
  except aiohttp.ClientError as e:
    logging.exception("Error making request to %s: %s", url, e)
    raise Exception(f"Failed to fetch data from Sleeper API: {e}") from e


def connect_to_sqlite(path: str | None = None) -> sqlite3.Connection:
  """Connect to a SQLite database."""
  if path is None:
    path = os.environ.get(
        "DB_PATH_IN_CONTAINER",
        os.environ.get("DB_PATH_ON_HOST", "/app/db/fantasy_ingestion.sqlite"),
    )

  try:
    conn = sqlite3.connect(path)
    logging.debug("Connected to SQLite database at %s", path)
    return conn
  except sqlite3.Error as e:
    logging.exception("Failed to connect to SQLite database: %s", e)
    raise


def read_df_from_sqlite(
    conn: sqlite3.Connection,
    table_name: str,
) -> pd.DataFrame | None:
  """Read a DataFrame from a SQLite database."""
  try:
    logging.debug("Reading DataFrame from SQLite database...")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,),
    )
    if cursor.fetchone():
      logging.debug("Table %s found in SQLite database.", table_name)
      sanitized_table_name = table_name.replace('"', '""')
      df = pd.read_sql_query(f'SELECT * FROM "{sanitized_table_name}"', conn)
      logging.debug("Read DataFrame from SQLite database.")
      return df
    else:
      logging.debug("Table %s not found in SQLite database.", table_name)
      return None
  except sqlite3.Error as e:
    logging.exception("Failed to read DataFrame from SQLite database: %s", e)
    raise


def write_df_to_sqlite(
    conn: sqlite3.Connection, df: pd.DataFrame, table_name: str
) -> None:
  """Write a DataFrame to a SQLite database."""
  try:
    logging.debug("Writing DataFrame to SQLite database...")
    df.to_sql(name=table_name, con=conn, if_exists="replace", index=False)
    logging.debug("Saved DataFrame to SQLite database.")
  except sqlite3.Error as e:
    logging.exception("Failed to write DataFrame to SQLite database: %s", e)
    raise


def close_sqlite_connection(conn: sqlite3.Connection) -> None:
  """Close a SQLite connection."""
  try:
    logging.debug("Closing SQLite connection...")
    conn.close()
    logging.debug("Closed SQLite connection.")
  except sqlite3.Error as e:
    logging.exception("Failed to close SQLite connection: %s", e)
    raise
