import pandas as pd
import pytest
from src.common import utils


@pytest.fixture(scope="module")
def db_connection():
  """Fixture to set up and tear down a temporary in-memory database."""
  conn = utils.connect_to_sqlite(":memory:")
  yield conn
  utils.close_sqlite_connection(conn)


def test_write_and_read_df(db_connection):
  """Test writing a DataFrame to the database and reading it back."""
  df = pd.DataFrame({
      "id": [1, 2, 3],
      "name": ["Alice", "Bob", "Charlie"],
      "value": [10.1, 20.2, 30.3],
  })
  table_name = "test_table"
  utils.write_df_to_sqlite(db_connection, df, table_name)
  actual_df = utils.read_df_from_sqlite(db_connection, table_name)
  pd.testing.assert_frame_equal(df, actual_df)


def test_read_df_from_sqlite_returns_none_if_table_does_not_exist(
    db_connection,
):
  """Test that reading from a non-existent table returns None."""
  table_name = "non_existent_table"
  actual_df = utils.read_df_from_sqlite(
      db_connection,
      table_name,
  )
  assert actual_df is None
