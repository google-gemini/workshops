from datetime import datetime
import json
import sys
import chess.pgn
from google.cloud import bigquery


def parse_date(date_str):
  """Convert PGN date to YYYY-MM-DD format"""
  if not date_str or date_str == "????.??.??":
    return None

  # Replace ? with 01, but be careful about malformed dates
  date_str = date_str.replace("?", "01")

  try:
    if "." in date_str:
      parts = date_str.split(".")
      if len(parts) == 3:
        year, month, day = parts
        # Validate components
        if len(year) == 4 and year.isdigit() and 1400 <= int(year) <= 2030:
          if month.isdigit() and 1 <= int(month) <= 12:
            if day.isdigit() and 1 <= int(day) <= 31:
              return f"{year}-{month.zfill(2)}-{day.zfill(2)}"

    if "-" in date_str and len(date_str) == 10:  # Already in YYYY-MM-DD format
      parts = date_str.split("-")
      if len(parts) == 3:
        year, month, day = parts
        if len(year) == 4 and year.isdigit() and 1400 <= int(year) <= 2030:
          if month.isdigit() and 1 <= int(month) <= 12:
            if day.isdigit() and 1 <= int(day) <= 31:
              return date_str

    # Just year
    if (
        len(date_str) == 4
        and date_str.isdigit()
        and 1400 <= int(date_str) <= 2030
    ):
      return f"{date_str}-01-01"

  except:
    pass

  return None


def analyze_pgn_commentary(game):
  """Analyze commentary in PGN game"""
  stats = {
      "has_comments": False,
      "comment_count": 0,
      "has_variations": False,
      "variation_count": 0,
      "has_nags": False,
      "nag_count": 0,
      "sample_comments": [],
  }

  try:
    node = game
    while node.variations:
      node = node.variations[0]

      if node.comment:
        stats["has_comments"] = True
        stats["comment_count"] += 1
        if len(stats["sample_comments"]) < 2:
          clean_comment = node.comment.strip().replace("\n", " ")[:200]
          stats["sample_comments"].append(clean_comment)

      if len(node.variations) > 1:
        stats["has_variations"] = True
        stats["variation_count"] += len(node.variations) - 1

      if node.nags:
        stats["has_nags"] = True
        stats["nag_count"] += len(node.nags)
  except:
    pass

  return stats


def stream_pgn_to_bigquery(
    pgn_file,
    project_id,
    dataset_id="chess_games",
    table_id="games",
    max_games=None,
    start_from=0,
):
  """Stream PGN directly to BigQuery using native Python SDK"""

  print(f"🔄 Streaming {pgn_file} to BigQuery using native Python SDK...")
  if start_from > 0:
    print(f"   📍 Starting from game {start_from:,}")

  # Initialize BigQuery client
  client = bigquery.Client(project=project_id)
  table_ref = f"{project_id}.{dataset_id}.{table_id}"
  table = client.get_table(table_ref)

  print(f"   ✓ Connected to BigQuery table: {table_ref}")

  games_processed = 0
  games_skipped = 0
  rows_to_insert = []
  batch_size = 1000  # BigQuery recommends batches of ~1000 rows
  total_inserted = 0

  try:
    with open(pgn_file, "r", encoding="utf-8", errors="ignore") as pgn_in:

      while games_processed < (max_games or 999999999):
        try:
          game = chess.pgn.read_game(pgn_in)
          if game is None:
            break  # End of file

          games_processed += 1
          
          # Skip games until we reach start_from
          if games_processed <= start_from:
            games_skipped += 1
            if games_skipped % 10000 == 0:
              print(f"   ⏩ Skipped {games_skipped:,} games...")
            continue

          # Extract headers and create row
          headers = game.headers
          commentary_stats = analyze_pgn_commentary(game)

          row = {
              "id": f"game_{games_processed + start_from}",
              "white_player": headers.get("White"),
              "black_player": headers.get("Black"),
              "event": headers.get("Event"),
              "site": headers.get("Site"),
              "date": parse_date(headers.get("Date")),
              "round": headers.get("Round"),
              "result": headers.get("Result"),
              "eco": headers.get("ECO"),
              "white_elo": (
                  int(headers.get("WhiteElo"))
                  if headers.get("WhiteElo")
                  and headers.get("WhiteElo").isdigit()
                  else None
              ),
              "black_elo": (
                  int(headers.get("BlackElo"))
                  if headers.get("BlackElo")
                  and headers.get("BlackElo").isdigit()
                  else None
              ),
              "time_control": headers.get("TimeControl"),
              "ply_count": (
                  int(headers.get("PlyCount"))
                  if headers.get("PlyCount")
                  and headers.get("PlyCount").isdigit()
                  else None
              ),
              "pgn_text": str(game),
              "commentary_stats": json.dumps(commentary_stats),
              "source_title": headers.get("SourceTitle"),
              "event_date": parse_date(headers.get("EventDate")),
          }

          rows_to_insert.append(row)

          # Insert batch when we hit batch_size
          if len(rows_to_insert) >= batch_size:
            print(
                f"   📤 Inserting batch of {len(rows_to_insert)} rows (games"
                f" {total_inserted+1}-{total_inserted+len(rows_to_insert)})..."
            )

            errors = client.insert_rows_json(table, rows_to_insert)

            if errors:
              print(f"   ❌ Insertion errors: {errors}")
              return False
            else:
              total_inserted += len(rows_to_insert)
              print(
                  "   ✅ Batch inserted successfully. Total:"
                  f" {total_inserted:,} games"
              )

            rows_to_insert = []  # Reset batch

          # Progress update
          if games_processed % 5000 == 0:
            print(
                f"   📊 Progress: {games_processed:,} games processed,"
                f" {total_inserted:,} inserted"
            )

        except Exception as e:
          print(f"   ⚠️ Error processing game {games_processed}: {e}")
          continue

      # Insert final batch if any rows remain
      if rows_to_insert:
        print(f"   📤 Inserting final batch of {len(rows_to_insert)} rows...")
        errors = client.insert_rows_json(table, rows_to_insert)

        if errors:
          print(f"   ❌ Final batch errors: {errors}")
          return False
        else:
          total_inserted += len(rows_to_insert)
          print(f"   ✅ Final batch inserted successfully")

    print(f"\n✅ Successfully streamed to BigQuery!")
    print(f"   Processed: {games_processed:,} games")
    print(f"   Inserted: {total_inserted:,} records")

    return True

  except Exception as e:
    print(f"❌ Error streaming to BigQuery: {e}")
    return False


if __name__ == "__main__":
  if len(sys.argv) < 3:
    print(
        "Usage: python pgn_to_bigquery_native.py <pgn_file> <project_id>"
        " [max_games] [start_from]"
    )
    sys.exit(1)

  pgn_file = sys.argv[1]
  project_id = sys.argv[2]
  max_games = int(sys.argv[3]) if len(sys.argv) > 3 else None
  start_from = int(sys.argv[4]) if len(sys.argv) > 4 else 0

  print(f"Configuration:")
  print(f"  PGN file: {pgn_file}")
  print(f"  Project: {project_id}")
  print(f"  Max games: {max_games or 'all'}")
  print(f"  Start from game: {start_from}")
  print(f"  Method: Native BigQuery Python SDK")

  success = stream_pgn_to_bigquery(pgn_file, project_id, max_games=max_games, start_from=start_from)

  if not success:
    sys.exit(1)
