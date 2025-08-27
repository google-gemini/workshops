# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import chess.pgn
import re
from pathlib import Path


def scan_nakamura_carlsen_games(pgn_file: str):
    """Scan for Nakamura, Hikaru (White) vs Carlsen, Magnus (Black) games"""
    
    games_found = []
    total_games_scanned = 0
    
    print(f"🔍 Scanning {pgn_file} for Nakamura, Hikaru vs Carlsen, Magnus games...")
    
    with open(pgn_file, encoding='utf-8', errors='ignore') as f:
        while True:
            game = chess.pgn.read_game(f)
            if game is None:
                break
                
            total_games_scanned += 1
            if total_games_scanned % 100000 == 0:
                print(f"   Scanned {total_games_scanned:,} games, found {len(games_found)} matches...")
            
            # Check for specific players
            white = game.headers.get("White", "")
            black = game.headers.get("Black", "")
            
            # Be specific about which Nakamura and Carlsen
            if ("Nakamura, Hikaru" in white and "Carlsen, Magnus" in black):
                # Extract commentary info
                has_commentary = analyze_game_commentary(game)
                
                game_info = {
                    "white": white,
                    "black": black,
                    "event": game.headers.get("Event"),
                    "date": game.headers.get("Date"),
                    "result": game.headers.get("Result"),
                    "eco": game.headers.get("ECO"),
                    "white_elo": game.headers.get("WhiteElo"),
                    "black_elo": game.headers.get("BlackElo"),
                    "ply_count": game.headers.get("PlyCount"),
                    "time_control": game.headers.get("TimeControl"),
                    "commentary_analysis": has_commentary
                }
                games_found.append(game_info)
                
                # Show progress
                print(f"   ✓ Found game #{len(games_found)}: {game_info['event']} ({game_info['date']}) - {game_info['result']}")
    
    print(f"\n📊 SCAN RESULTS:")
    print(f"   Total games scanned: {total_games_scanned:,}")
    print(f"   Nakamura vs Carlsen games: {len(games_found)}")
    
    return games_found


def analyze_game_commentary(game) -> dict:
    """Analyze what kind of commentary/annotations a game has"""
    
    commentary_info = {
        "has_text_comments": 0,
        "has_variations": 0, 
        "has_nag_annotations": 0,
        "sample_comments": []
    }
    
    # Walk through the game tree
    node = game
    move_count = 0
    
    while node.variations and move_count < 50:  # Don't scan entire long games
        node = node.variations[0]
        move_count += 1
        
        # Check for text comments
        if node.comment:
            commentary_info["has_text_comments"] += 1
            if len(commentary_info["sample_comments"]) < 3:
                # Clean up comment for display
                clean_comment = node.comment.strip().replace('\n', ' ')[:100]
                commentary_info["sample_comments"].append(clean_comment)
        
        # Check for variations (alternative lines)
        if len(node.variations) > 1:
            commentary_info["has_variations"] += 1
            
        # Check for NAG annotations ($1, $146, etc.)
        if node.nags:
            commentary_info["has_nag_annotations"] += len(node.nags)
    
    return commentary_info


if __name__ == "__main__":
    games = scan_nakamura_carlsen_games("mega-2025.pgn")
    
    if games:
        print(f"\n🎯 DETAILED ANALYSIS:")
        
        # Group by year
        by_year = {}
        for game in games:
            year = game["date"][:4] if game["date"] and len(game["date"]) >= 4 else "unknown"
            by_year.setdefault(year, []).append(game)
        
        print(f"\nGames by year:")
        for year in sorted(by_year.keys()):
            print(f"   {year}: {len(by_year[year])} games")
            
        # Analyze commentary quality
        games_with_text_comments = [g for g in games if g["commentary_analysis"]["has_text_comments"] > 0]
        games_with_variations = [g for g in games if g["commentary_analysis"]["has_variations"] > 0]
        games_with_nags = [g for g in games if g["commentary_analysis"]["has_nag_annotations"] > 0]
        
        print(f"\nCommentary analysis:")
        print(f"   Games with text comments: {len(games_with_text_comments)}")
        print(f"   Games with variations: {len(games_with_variations)}")
        print(f"   Games with NAG annotations: {len(games_with_nags)}")
        
        # Show results by game outcome
        results = {}
        for game in games:
            result = game["result"]
            results[result] = results.get(result, 0) + 1
        
        print(f"\nGame results:")
        for result, count in results.items():
            print(f"   {result}: {count} games")
            
        # Show different time controls
        time_controls = {}
        for game in games:
            tc = game["time_control"] or "unknown"
            time_controls[tc] = time_controls.get(tc, 0) + 1
            
        print(f"\nTime controls:")
        for tc, count in time_controls.items():
            print(f"   {tc}: {count} games")
        
        # Show sample games with best commentary
        print(f"\n📋 GAMES WITH MOST COMMENTARY:")
        
        # Sort by commentary richness
        rich_games = sorted(games, 
                          key=lambda g: (g["commentary_analysis"]["has_text_comments"] + 
                                       g["commentary_analysis"]["has_variations"] + 
                                       g["commentary_analysis"]["has_nag_annotations"]), 
                          reverse=True)
        
        for i, game in enumerate(rich_games[:10]):  # Show top 10
            commentary = game["commentary_analysis"]
            richness = commentary["has_text_comments"] + commentary["has_variations"] + commentary["has_nag_annotations"]
            
            print(f"\n{i+1}. {game['event']} ({game['date']}) - {game['result']}")
            print(f"   Richness score: {richness} (comments: {commentary['has_text_comments']}, variations: {commentary['has_variations']}, NAGs: {commentary['has_nag_annotations']})")
            print(f"   Elo: {game['white_elo']} vs {game['black_elo']}")
            print(f"   Time control: {game['time_control']}")
            print(f"   ECO: {game['eco']}")
            if commentary['sample_comments']:
                print(f"   Sample comment: {commentary['sample_comments'][0]}")
                
    else:
        print("❌ No Nakamura vs Carlsen games found!")
        print("   Double-check player name formatting in your PGN file")
