import json
import sys
from google.cloud import bigquery


def test_bigquery_data(
    project_id, dataset_id="chess_games", table_id="games", limit=5
):
  """Test what data is actually stored in BigQuery"""

  print(f"🔍 Testing BigQuery data...")
  print(f"   Project: {project_id}")
  print(f"   Table: {project_id}.{dataset_id}.{table_id}")
  print(f"   Records to show: {limit}")

  try:
    client = bigquery.Client(project=project_id)
    table_ref = f"{project_id}.{dataset_id}.{table_id}"

    # Test 1: Count total records
    count_query = f"SELECT COUNT(*) as total_games FROM `{table_ref}`"
    count_results = client.query(count_query)
    total_games = list(count_results)[0].total_games
    print(f"\n📊 Total games in database: {total_games:,}")

    # Test 2: Sample records with key fields
    sample_query = f"""
        SELECT 
            id, white_player, black_player, event, date, result,
            white_elo, black_elo, eco, time_control,
            commentary_stats
        FROM `{table_ref}` 
        LIMIT {limit}
        """

    print(f"\n📋 Sample records:")
    results = client.query(sample_query)

    for i, row in enumerate(results, 1):
      print(f"\n{i}. Game ID: {row.id}")
      print(
          f"   Players: {row.white_player} ({row.white_elo}) vs"
          f" {row.black_player} ({row.black_elo})"
      )
      print(f"   Event: {row.event}")
      print(f"   Date: {row.date}")
      print(f"   Result: {row.result}")
      print(f"   ECO: {row.eco}")
      print(f"   Time Control: {row.time_control}")

      # Parse and display commentary stats
      if row.commentary_stats:
        try:
          # BigQuery JSON columns are automatically parsed to Python dicts
          commentary = (
              row.commentary_stats
              if isinstance(row.commentary_stats, dict)
              else json.loads(row.commentary_stats)
          )
          print(
              f"   Commentary: {commentary['comment_count']} comments,"
              f" {commentary['variation_count']} variations"
          )
          if commentary["sample_comments"]:
            print(
                "   Sample comment:"
                f" {commentary['sample_comments'][0][:100]}..."
            )
        except (json.JSONDecodeError, KeyError, TypeError) as e:
          print(f"   Commentary: {str(row.commentary_stats)[:100]}...")
      else:
        print(f"   Commentary: None")

    # Test 3: Check for specific player matchups
    print(f"\n🔍 Searching for Nakamura vs Carlsen games...")
    nakamura_carlsen_query = f"""
        SELECT COUNT(*) as nakamura_vs_carlsen
        FROM `{table_ref}`
        WHERE white_player LIKE '%Nakamura, Hikaru%' 
          AND black_player LIKE '%Carlsen, Magnus%'
        """

    nc_results = client.query(nakamura_carlsen_query)
    nc_count = list(nc_results)[0].nakamura_vs_carlsen
    print(f"   Found {nc_count} Nakamura (White) vs Carlsen (Black) games")

    # Test 4: Show data types and schema info
    print(f"\n🗂️ Data type verification:")
    schema_query = f"""
        SELECT 
            COUNT(CASE WHEN date IS NOT NULL THEN 1 END) as valid_dates,
            COUNT(CASE WHEN white_elo IS NOT NULL THEN 1 END) as valid_white_elos,
            COUNT(CASE WHEN black_elo IS NOT NULL THEN 1 END) as valid_black_elos,
            COUNT(CASE WHEN commentary_stats IS NOT NULL THEN 1 END) as has_commentary
        FROM `{table_ref}`
        """

    schema_results = client.query(schema_query)
    schema_row = list(schema_results)[0]

    print(f"   Valid dates: {schema_row.valid_dates}/{total_games}")
    print(f"   Valid White ELOs: {schema_row.valid_white_elos}/{total_games}")
    print(f"   Valid Black ELOs: {schema_row.valid_black_elos}/{total_games}")
    print(f"   Has commentary: {schema_row.has_commentary}/{total_games}")

    # Test 5: Sample PGN text (truncated)
    print(f"\n📝 Sample PGN data:")
    pgn_query = f"""
        SELECT pgn_text 
        FROM `{table_ref}` 
        WHERE pgn_text IS NOT NULL 
        LIMIT 1
        """

    pgn_results = client.query(pgn_query)
    for row in pgn_results:
      pgn_sample = (
          row.pgn_text[:300] + "..."
          if len(row.pgn_text) > 300
          else row.pgn_text
      )
      print(f"   {pgn_sample}")
      break

    print(f"\n✅ BigQuery data test completed!")
    return True

  except Exception as e:
    print(f"❌ Error testing BigQuery data: {e}")
    return False


if __name__ == "__main__":
  if len(sys.argv) < 2:
    print("Usage: python test_bigquery_data.py <project_id> [limit]")
    print("Example: python test_bigquery_data.py project-0615388941 10")
    sys.exit(1)

  project_id = sys.argv[1]
  limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5

  print(f"Configuration:")
  print(f"  Project ID: {project_id}")
  print(f"  Sample limit: {limit}")

  success = test_bigquery_data(project_id, limit=limit)

  if not success:
    sys.exit(1)
