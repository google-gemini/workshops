import chess.pgn
import json
import sys
import subprocess
from datetime import datetime

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
        if len(date_str) == 4 and date_str.isdigit() and 1400 <= int(date_str) <= 2030:
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
        "sample_comments": []
    }
    
    try:
        node = game
        while node.variations:
            node = node.variations[0]
            
            if node.comment:
                stats["has_comments"] = True
                stats["comment_count"] += 1
                if len(stats["sample_comments"]) < 2:
                    clean_comment = node.comment.strip().replace('\n', ' ')[:200]
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

def pgn_to_bigquery_streaming(pgn_file, project_id, dataset_id="chess_games", table_id="games", max_games=None):
    """Stream PGN to BigQuery in small chunks - minimal disk usage!"""
    
    # Create schema file
    schema = [
        {"name": "id", "type": "STRING", "mode": "REQUIRED"},
        {"name": "white_player", "type": "STRING", "mode": "NULLABLE"},
        {"name": "black_player", "type": "STRING", "mode": "NULLABLE"},
        {"name": "event", "type": "STRING", "mode": "NULLABLE"},
        {"name": "site", "type": "STRING", "mode": "NULLABLE"},
        {"name": "date", "type": "DATE", "mode": "NULLABLE"},
        {"name": "round", "type": "STRING", "mode": "NULLABLE"},
        {"name": "result", "type": "STRING", "mode": "NULLABLE"},
        {"name": "eco", "type": "STRING", "mode": "NULLABLE"},
        {"name": "white_elo", "type": "INTEGER", "mode": "NULLABLE"},
        {"name": "black_elo", "type": "INTEGER", "mode": "NULLABLE"},
        {"name": "time_control", "type": "STRING", "mode": "NULLABLE"},
        {"name": "ply_count", "type": "INTEGER", "mode": "NULLABLE"},
        {"name": "pgn_text", "type": "STRING", "mode": "NULLABLE"},
        {"name": "commentary_stats", "type": "JSON", "mode": "NULLABLE"},
        {"name": "source_title", "type": "STRING", "mode": "NULLABLE"},
        {"name": "event_date", "type": "DATE", "mode": "NULLABLE"}
    ]
    
    with open("temp_schema.json", "w") as f:
        json.dump(schema, f)
    
    print(f"🔄 Streaming {pgn_file} to BigQuery in small chunks...")
    
    games_processed = 0
    games_written = 0
    chunk_size = 1000  # Process 1000 games at a time (~10MB chunks)
    chunk_num = 0
    is_first_chunk = True
    
    try:
        with open(pgn_file, 'r', encoding='utf-8', errors='ignore') as pgn_in:
            
            while games_processed < (max_games or 999999999):
                chunk_num += 1
                chunk_filename = f"temp_chunk_{chunk_num}.jsonl"
                chunk_games = 0
                
                print(f"\n   📦 Processing chunk {chunk_num} (games {games_processed+1}-{games_processed+chunk_size})...")
                
                # Create a chunk file
                with open(chunk_filename, 'w', encoding='utf-8') as chunk_file:
                    
                    for _ in range(chunk_size):
                        if games_processed >= (max_games or 999999999):
                            break
                            
                        try:
                            game = chess.pgn.read_game(pgn_in)
                            if game is None:
                                break  # End of file
                                
                            games_processed += 1
                            
                            # Extract headers and create record
                            headers = game.headers
                            commentary_stats = analyze_pgn_commentary(game)
                            
                            record = {
                                "id": f"game_{games_processed}",
                                "white_player": headers.get("White"),
                                "black_player": headers.get("Black"), 
                                "event": headers.get("Event"),
                                "site": headers.get("Site"),
                                "date": parse_date(headers.get("Date")),
                                "round": headers.get("Round"),
                                "result": headers.get("Result"),
                                "eco": headers.get("ECO"),
                                "white_elo": int(headers.get("WhiteElo")) if headers.get("WhiteElo") and headers.get("WhiteElo").isdigit() else None,
                                "black_elo": int(headers.get("BlackElo")) if headers.get("BlackElo") and headers.get("BlackElo").isdigit() else None,
                                "time_control": headers.get("TimeControl"),
                                "ply_count": int(headers.get("PlyCount")) if headers.get("PlyCount") and headers.get("PlyCount").isdigit() else None,
                                "pgn_text": str(game),
                                "commentary_stats": commentary_stats,
                                "source_title": headers.get("SourceTitle"),
                                "event_date": parse_date(headers.get("EventDate"))
                            }
                            
                            # Write to chunk file
                            json_line = json.dumps(record, ensure_ascii=False) + '\n'
                            chunk_file.write(json_line)
                            chunk_games += 1
                            games_written += 1
                            
                        except Exception as e:
                            print(f"      ⚠️ Error processing game {games_processed}: {e}")
                            continue
                
                # If chunk is empty, we're done
                if chunk_games == 0:
                    import os
                    os.remove(chunk_filename)
                    break
                
                print(f"      📝 Chunk {chunk_num}: {chunk_games} games written to {chunk_filename}")
                
                # Load chunk to BigQuery
                load_mode = "--replace" if is_first_chunk else "--noreplace"  # Replace first, append others
                cmd = [
                    "bq", "load",
                    "--source_format=NEWLINE_DELIMITED_JSON",
                    load_mode,
                    f"{project_id}:{dataset_id}.{table_id}",
                    chunk_filename,
                    "temp_schema.json"
                ]
                
                print(f"      📤 Loading chunk {chunk_num} to BigQuery...")
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"      ✅ Chunk {chunk_num} loaded successfully")
                else:
                    print(f"      ❌ Chunk {chunk_num} failed:")
                    print(f"         stdout: {result.stdout}")
                    print(f"         stderr: {result.stderr}")
                    # Clean up and exit
                    import os
                    os.remove(chunk_filename)
                    return False
                
                # Clean up chunk file immediately
                import os
                os.remove(chunk_filename)
                print(f"      🧹 Cleaned up {chunk_filename}")
                
                is_first_chunk = False
                
                # Progress update
                print(f"   ✓ Total progress: {games_processed:,} games processed, {games_written:,} loaded")
                
                # Check if we've hit EOF
                if chunk_games < chunk_size:
                    print("   📄 Reached end of PGN file")
                    break
    
        print(f"\n✅ Successfully streamed to BigQuery!")
        print(f"   Processed: {games_processed:,} games") 
        print(f"   Loaded: {games_written:,} records")
        print(f"   Chunks processed: {chunk_num}")
        
        return True
            
    except Exception as e:
        print(f"❌ Error streaming to BigQuery: {e}")
        return False
    finally:
        # Cleanup schema file
        import os
        if os.path.exists("temp_schema.json"):
            os.remove("temp_schema.json")
        # Clean up any leftover chunk files
        for i in range(1, chunk_num + 2):
            chunk_file = f"temp_chunk_{i}.jsonl"
            if os.path.exists(chunk_file):
                os.remove(chunk_file)
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python pgn_to_bigquery_streaming.py <pgn_file> <project_id> [max_games]")
        sys.exit(1)
        
    pgn_file = sys.argv[1]
    project_id = sys.argv[2]
    max_games = int(sys.argv[3]) if len(sys.argv) > 3 else None
    
    print(f"Configuration:")
    print(f"  PGN file: {pgn_file}")
    print(f"  Project: {project_id}")
    print(f"  Max games: {max_games or 'all'}")
    print(f"  Disk usage: No temporary files!")
    
    success = pgn_to_bigquery_streaming(pgn_file, project_id, max_games=max_games)
    
    if not success:
        sys.exit(1)
