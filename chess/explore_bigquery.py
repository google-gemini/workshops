import json
import sys
from typing import List, Dict, Any, Optional
from google.cloud import bigquery


class ChessGameExplorer:
    """Explore and analyze the chess games BigQuery database"""
    
    def __init__(self, project_id: str, dataset_id: str = "chess_games", table_id: str = "games"):
        self.client = bigquery.Client(project=project_id)
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.table_id = table_id
        self.table_ref = f"{project_id}.{dataset_id}.{table_id}"
        
    def quick_nakamura_carlsen_count(self) -> Dict[str, int]:
        """Get count of Nakamura, Hikaru vs Carlsen, Magnus games"""
        
        print("🔍 Searching for Nakamura vs Carlsen games...")
        print(f"   Database: {self.table_ref}")
        
        search_patterns = {
            "Nakamura (W) vs Carlsen (B)": 
                "(white_player = 'Nakamura, Hikaru' AND black_player = 'Carlsen, Magnus')",
            "Carlsen (W) vs Nakamura (B)": 
                "(white_player = 'Carlsen, Magnus' AND black_player = 'Nakamura, Hikaru')",
            "Total (both colors)": 
                """(white_player = 'Nakamura, Hikaru' AND black_player = 'Carlsen, Magnus')
                   OR 
                   (white_player = 'Carlsen, Magnus' AND black_player = 'Nakamura, Hikaru')"""
        }
        
        results = {}
        
        for description, condition in search_patterns.items():
            count_query = f"""
                SELECT COUNT(*) as count 
                FROM `{self.table_ref}` 
                WHERE {condition}
            """
            
            try:
                query_results = self.client.query(count_query)
                count = list(query_results)[0].count
                results[description] = count
                print(f"   {description}: {count} games")
            except Exception as e:
                print(f"   {description}: ERROR - {e}")
                results[description] = -1
        
        total_unique = results.get("Total (both colors)", 0)
        print(f"\n📊 Total Nakamura vs Carlsen games: {total_unique}")
        
        return results
    
    def sample_nakamura_carlsen_games(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get sample games between Nakamura, Hikaru and Carlsen, Magnus"""
        
        print(f"\n📋 Sample Nakamura vs Carlsen games (limit: {limit}):")
        
        sample_query = f"""
            SELECT 
                id, white_player, black_player, event, date, result,
                white_elo, black_elo, eco, time_control,
                commentary_stats, pgn_text
            FROM `{self.table_ref}` 
            WHERE (white_player = 'Nakamura, Hikaru' AND black_player = 'Carlsen, Magnus')
               OR (white_player = 'Carlsen, Magnus' AND black_player = 'Nakamura, Hikaru')
            ORDER BY date DESC
            LIMIT {limit}
        """
        
        games = []
        
        try:
            results = self.client.query(sample_query)
            
            for i, row in enumerate(results, 1):
                game_data = {
                    'id': row.id,
                    'white_player': row.white_player,
                    'black_player': row.black_player,
                    'event': row.event,
                    'date': row.date,
                    'result': row.result,
                    'white_elo': row.white_elo,
                    'black_elo': row.black_elo,
                    'eco': row.eco,
                    'time_control': row.time_control,
                    'commentary_stats': row.commentary_stats,
                    'pgn_length': len(row.pgn_text) if row.pgn_text else 0
                }
                
                games.append(game_data)
                
                print(f"\n{i}. Game ID: {row.id}")
                print(f"   Players: {row.white_player} ({row.white_elo}) vs {row.black_player} ({row.black_elo})")
                print(f"   Event: {row.event}")
                print(f"   Date: {row.date}")
                print(f"   Result: {row.result}")
                print(f"   ECO: {row.eco}")
                print(f"   Time Control: {row.time_control}")
                
                # Commentary analysis
                if row.commentary_stats:
                    try:
                        commentary = (
                            row.commentary_stats 
                            if isinstance(row.commentary_stats, dict) 
                            else json.loads(row.commentary_stats)
                        )
                        print(f"   Commentary: {commentary.get('comment_count', 0)} comments, {commentary.get('variation_count', 0)} variations")
                        sample_comments = commentary.get('sample_comments', [])
                        if sample_comments:
                            print(f"   Sample: {sample_comments[0][:100]}...")
                    except (json.JSONDecodeError, KeyError, TypeError):
                        print(f"   Commentary: {str(row.commentary_stats)[:100]}...")
                else:
                    print("   Commentary: None")
                
                print(f"   PGN length: {len(row.pgn_text) if row.pgn_text else 0} chars")
        
        except Exception as e:
            print(f"❌ Error fetching sample games: {e}")
        
        return games
    
    def analyze_game_quality(self, games: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the quality of games for vector database inclusion"""
        
        print(f"\n🔬 Analyzing game quality for {len(games)} games:")
        
        quality_metrics = {
            'total_games': len(games),
            'with_commentary': 0,
            'high_elo_games': 0,  # Both players > 2600
            'recent_games': 0,    # 2020 or later
            'tournament_games': 0,  # Major events
            'classical_games': 0,   # Longer time controls
        }
        
        high_quality_games = []
        
        for game in games:
            # Check commentary
            if game.get('commentary_stats'):
                try:
                    commentary = (
                        game['commentary_stats'] 
                        if isinstance(game['commentary_stats'], dict) 
                        else json.loads(game['commentary_stats'])
                    )
                    if commentary.get('comment_count', 0) > 0:
                        quality_metrics['with_commentary'] += 1
                except:
                    pass
            
            # Check ELO ratings
            white_elo = game.get('white_elo', 0) or 0
            black_elo = game.get('black_elo', 0) or 0
            if white_elo > 2600 and black_elo > 2600:
                quality_metrics['high_elo_games'] += 1
            
            # Check date
            game_date = game.get('date')
            if game_date and str(game_date).startswith(('2020', '2021', '2022', '2023', '2024', '2025')):
                quality_metrics['recent_games'] += 1
            
            # Check event type
            event = game.get('event', '').lower()
            if any(keyword in event for keyword in ['world', 'candidates', 'championship', 'grand']):
                quality_metrics['tournament_games'] += 1
            
            # Check time control (rough heuristic for classical)
            time_control = game.get('time_control', '')
            if time_control and ('1800' in time_control or '3600' in time_control or '7200' in time_control):
                quality_metrics['classical_games'] += 1
            
            # High quality game criteria
            quality_score = 0
            if game.get('commentary_stats'): quality_score += 2
            if white_elo > 2700 and black_elo > 2700: quality_score += 2
            if str(game_date).startswith(('2022', '2023', '2024', '2025')): quality_score += 1
            if any(keyword in event for keyword in ['world', 'candidates']): quality_score += 2
            
            if quality_score >= 3:
                high_quality_games.append({**game, 'quality_score': quality_score})
        
        for metric, value in quality_metrics.items():
            percentage = (value / len(games) * 100) if len(games) > 0 else 0
            print(f"   {metric}: {value} ({percentage:.1f}%)")
        
        print(f"\n⭐ High quality games (score >= 3): {len(high_quality_games)}")
        for game in sorted(high_quality_games, key=lambda x: x['quality_score'], reverse=True)[:5]:
            print(f"   Score {game['quality_score']}: {game['white_player']} vs {game['black_player']}, {game['event']}, {game['date']}")
        
        return {
            'metrics': quality_metrics,
            'high_quality_games': high_quality_games
        }
    
    def search_by_event(self, event_patterns: List[str], limit: int = 50) -> List[Dict[str, Any]]:
        """Search for games by event patterns"""
        
        print(f"\n🏆 Searching games by events: {event_patterns}")
        
        # Build OR conditions for events
        event_conditions = []
        for pattern in event_patterns:
            event_conditions.append(f"UPPER(event) LIKE '%{pattern.upper()}%'")
        
        event_where = " OR ".join(event_conditions)
        
        query = f"""
            SELECT id, white_player, black_player, event, date, result, white_elo, black_elo
            FROM `{self.table_ref}` 
            WHERE ({event_where})
              AND ((white_player = 'Nakamura, Hikaru' AND black_player = 'Carlsen, Magnus')
                   OR (white_player = 'Carlsen, Magnus' AND black_player = 'Nakamura, Hikaru'))
            ORDER BY date DESC
            LIMIT {limit}
        """
        
        games = []
        
        try:
            results = self.client.query(query)
            
            for row in results:
                games.append({
                    'id': row.id,
                    'white_player': row.white_player,
                    'black_player': row.black_player,
                    'event': row.event,
                    'date': row.date,
                    'result': row.result,
                    'white_elo': row.white_elo,
                    'black_elo': row.black_elo
                })
            
            print(f"   Found {len(games)} games")
            for game in games:
                print(f"   {game['date']}: {game['white_player']} vs {game['black_player']}, {game['event']}")
        
        except Exception as e:
            print(f"❌ Error searching by event: {e}")
        
        return games

    def exhaustive_nakamura_white_analysis(self) -> Dict[str, Any]:
        """Analyze ALL Nakamura (White) vs Carlsen (Black) games"""
        
        print("📊 EXHAUSTIVE ANALYSIS: Nakamura (White) vs Carlsen (Black)")
        print(f"   Database: {self.table_ref}")
        
        query = f"""
            SELECT 
                id, white_player, black_player, event, date, result,
                white_elo, black_elo, eco, time_control,
                commentary_stats, pgn_text
            FROM `{self.table_ref}` 
            WHERE white_player = 'Nakamura, Hikaru' 
              AND black_player = 'Carlsen, Magnus'
            ORDER BY date DESC
        """
        
        games = []
        
        try:
            results = self.client.query(query)
            
            for row in results:
                game_data = {
                    'id': row.id,
                    'white_player': row.white_player,
                    'black_player': row.black_player,
                    'event': row.event,
                    'date': row.date,
                    'result': row.result,
                    'white_elo': row.white_elo,
                    'black_elo': row.black_elo,
                    'eco': row.eco,
                    'time_control': row.time_control,
                    'commentary_stats': row.commentary_stats,
                    'pgn_length': len(row.pgn_text) if row.pgn_text else 0
                }
                games.append(game_data)
            
            print(f"\n📋 Loaded {len(games)} games for exhaustive analysis")
            
            # Run comprehensive quality analysis
            quality_analysis = self.analyze_game_quality(games)
            
            return {
                'games': games,
                'quality_analysis': quality_analysis
            }
        
        except Exception as e:
            print(f"❌ Error in exhaustive analysis: {e}")
            return {}

    def list_all_tournaments(self) -> List[Dict[str, Any]]:
        """List every tournament where Nakamura (W) played Carlsen (B)"""
        
        print("🏆 ALL TOURNAMENTS: Nakamura (White) vs Carlsen (Black)")
        print(f"   Database: {self.table_ref}")
        
        query = f"""
            SELECT 
                event, 
                COUNT(*) as game_count,
                MIN(date) as first_game,
                MAX(date) as last_game,
                STRING_AGG(result, ', ' ORDER BY date) as results,
                AVG(white_elo) as avg_nakamura_elo,
                AVG(black_elo) as avg_carlsen_elo,
                COUNT(CASE WHEN commentary_stats IS NOT NULL THEN 1 END) as games_with_commentary
            FROM `{self.table_ref}` 
            WHERE white_player = 'Nakamura, Hikaru' 
              AND black_player = 'Carlsen, Magnus'
            GROUP BY event
            ORDER BY game_count DESC, last_game DESC
        """
        
        tournaments = []
        
        try:
            results = self.client.query(query)
            
            print(f"\n📋 Tournament Breakdown:")
            for i, row in enumerate(results, 1):
                tournament_data = {
                    'event': row.event,
                    'game_count': row.game_count,
                    'first_game': row.first_game,
                    'last_game': row.last_game,
                    'results': row.results,
                    'avg_nakamura_elo': round(row.avg_nakamura_elo) if row.avg_nakamura_elo else None,
                    'avg_carlsen_elo': round(row.avg_carlsen_elo) if row.avg_carlsen_elo else None,
                    'games_with_commentary': row.games_with_commentary
                }
                
                tournaments.append(tournament_data)
                
                print(f"\n{i}. {row.event}")
                print(f"   Games: {row.game_count}")
                print(f"   Period: {row.first_game} to {row.last_game}")
                print(f"   Results: {row.results}")
                print(f"   Avg ELOs: Nakamura {tournament_data['avg_nakamura_elo']}, Carlsen {tournament_data['avg_carlsen_elo']}")
                print(f"   Commentary: {row.games_with_commentary}/{row.game_count} games")
                
                # Calculate win statistics
                results_list = row.results.split(', ') if row.results else []
                nakamura_wins = results_list.count('1-0')
                draws = results_list.count('1/2-1/2') 
                carlsen_wins = results_list.count('0-1')
                print(f"   Score: Nakamura {nakamura_wins}, Draws {draws}, Carlsen {carlsen_wins}")
            
            total_tournaments = len(tournaments)
            total_games = sum(t['game_count'] for t in tournaments)
            total_commentary = sum(t['games_with_commentary'] for t in tournaments)
            
            print(f"\n📊 SUMMARY:")
            print(f"   Total tournaments: {total_tournaments}")
            print(f"   Total games: {total_games}")
            print(f"   Games with commentary: {total_commentary} ({total_commentary/total_games*100:.1f}%)")
            
            return tournaments
        
        except Exception as e:
            print(f"❌ Error listing tournaments: {e}")
            return []

    def enumerate_commentary_games(self) -> List[Dict[str, Any]]:
        """Show every game with commentary and sample text"""
        
        print("💬 ALL GAMES WITH COMMENTARY: Nakamura (White) vs Carlsen (Black)")
        print(f"   Database: {self.table_ref}")
        
        query = f"""
            SELECT 
                date, event, result, commentary_stats, pgn_text,
                white_elo, black_elo, eco
            FROM `{self.table_ref}` 
            WHERE white_player = 'Nakamura, Hikaru' 
              AND black_player = 'Carlsen, Magnus'
              AND commentary_stats IS NOT NULL
            ORDER BY date DESC
        """
        
        commentary_games = []
        
        try:
            results = self.client.query(query)
            
            print(f"\n📋 Games with Commentary:")
            for i, row in enumerate(results, 1):
                game_data = {
                    'date': row.date,
                    'event': row.event,
                    'result': row.result,
                    'white_elo': row.white_elo,
                    'black_elo': row.black_elo,
                    'eco': row.eco,
                    'commentary_stats': row.commentary_stats,
                    'pgn_text': row.pgn_text
                }
                
                commentary_games.append(game_data)
                
                print(f"\n{i}. {row.date} - {row.event}")
                print(f"   Result: {row.result} (ELOs: {row.white_elo} vs {row.black_elo})")
                print(f"   Opening: {row.eco}")
                
                # Parse and display commentary stats
                try:
                    commentary = (
                        row.commentary_stats 
                        if isinstance(row.commentary_stats, dict) 
                        else json.loads(row.commentary_stats)
                    )
                    
                    comment_count = commentary.get('comment_count', 0)
                    variation_count = commentary.get('variation_count', 0)
                    sample_comments = commentary.get('sample_comments', [])
                    
                    print(f"   Commentary: {comment_count} comments, {variation_count} variations")
                    
                    # Show sample comments
                    if sample_comments:
                        print(f"   Sample comments:")
                        for j, comment in enumerate(sample_comments[:3], 1):  # Show up to 3 samples
                            comment_preview = comment[:100] + "..." if len(comment) > 100 else comment
                            print(f"     {j}. {comment_preview}")
                    
                except (json.JSONDecodeError, KeyError, TypeError) as e:
                    print(f"   Commentary: {str(row.commentary_stats)[:100]}...")
            
            total_commentary_games = len(commentary_games)
            print(f"\n📊 SUMMARY:")
            print(f"   Total games with commentary: {total_commentary_games}")
            
            if commentary_games:
                # Calculate commentary statistics
                total_comments = 0
                total_variations = 0
                
                for game in commentary_games:
                    try:
                        commentary = (
                            game['commentary_stats'] 
                            if isinstance(game['commentary_stats'], dict) 
                            else json.loads(game['commentary_stats'])
                        )
                        total_comments += commentary.get('comment_count', 0)
                        total_variations += commentary.get('variation_count', 0)
                    except:
                        pass
                
                avg_comments = total_comments / total_commentary_games
                avg_variations = total_variations / total_commentary_games
                
                print(f"   Average comments per game: {avg_comments:.1f}")
                print(f"   Average variations per game: {avg_variations:.1f}")
                print(f"   Total commentary annotations: {total_comments} comments, {total_variations} variations")
            
            return commentary_games
        
        except Exception as e:
            print(f"❌ Error enumerating commentary games: {e}")
            return []

    def list_all_games(self) -> List[Dict[str, Any]]:
        """Enumerate every single Nakamura (W) vs Carlsen (B) game"""
        
        print("🎯 ALL GAMES: Nakamura (White) vs Carlsen (Black)")
        print(f"   Database: {self.table_ref}")
        
        query = f"""
            SELECT 
                ROW_NUMBER() OVER (ORDER BY date DESC) as game_num,
                date, event, result, white_elo, black_elo, eco, 
                time_control, commentary_stats IS NOT NULL as has_commentary,
                id
            FROM `{self.table_ref}` 
            WHERE white_player = 'Nakamura, Hikaru' 
              AND black_player = 'Carlsen, Magnus'
            ORDER BY date DESC
        """
        
        all_games = []
        
        try:
            results = self.client.query(query)
            
            print(f"\n📋 Complete Game List:")
            for row in results:
                game_data = {
                    'game_num': row.game_num,
                    'id': row.id,
                    'date': row.date,
                    'event': row.event,
                    'result': row.result,
                    'white_elo': row.white_elo,
                    'black_elo': row.black_elo,
                    'eco': row.eco,
                    'time_control': row.time_control,
                    'has_commentary': row.has_commentary
                }
                
                all_games.append(game_data)
                
                # Format display
                result_symbol = {
                    '1-0': '✅',  # Nakamura win
                    '0-1': '❌',  # Carlsen win  
                    '1/2-1/2': '⚖️'  # Draw
                }.get(row.result, '❓')
                
                commentary_symbol = '💬' if row.has_commentary else '📝'
                
                print(f"   {row.game_num:3d}. {row.date} | {result_symbol} {row.result} | "
                      f"{row.eco} | {commentary_symbol} | {row.event}")
            
            total_games = len(all_games)
            
            # Calculate summary statistics
            nakamura_wins = sum(1 for g in all_games if g['result'] == '1-0')
            draws = sum(1 for g in all_games if g['result'] == '1/2-1/2')
            carlsen_wins = sum(1 for g in all_games if g['result'] == '0-1')
            commentary_games = sum(1 for g in all_games if g['has_commentary'])
            
            print(f"\n📊 COMPLETE SUMMARY:")
            print(f"   Total games: {total_games}")
            print(f"   Nakamura (White) wins: {nakamura_wins} ({nakamura_wins/total_games*100:.1f}%)")
            print(f"   Draws: {draws} ({draws/total_games*100:.1f}%)")
            print(f"   Carlsen (Black) wins: {carlsen_wins} ({carlsen_wins/total_games*100:.1f}%)")
            print(f"   Games with commentary: {commentary_games} ({commentary_games/total_games*100:.1f}%)")
            
            # Recent vs historical performance
            recent_games = [g for g in all_games if str(g['date']).startswith(('2023', '2024', '2025'))]
            if recent_games:
                recent_nakamura_wins = sum(1 for g in recent_games if g['result'] == '1-0')
                recent_total = len(recent_games)
                print(f"   Recent performance (2023+): {recent_nakamura_wins}/{recent_total} "
                      f"({recent_nakamura_wins/recent_total*100:.1f}% for Nakamura)")
            
            return all_games
        
        except Exception as e:
            print(f"❌ Error listing all games: {e}")
            return []

    def export_commentary_games_to_pgn(self, output_file: str = "nakamura_carlsen_commentary.pgn") -> int:
        """Export all Nakamura (White) vs Carlsen (Black) commentary games to PGN file"""
        
        print("📁 EXPORTING COMMENTARY GAMES TO PGN")
        print(f"   Database: {self.table_ref}")
        print(f"   Output file: {output_file}")
        
        query = f"""
            SELECT 
                pgn_text, date, event, result
            FROM `{self.table_ref}` 
            WHERE white_player = 'Nakamura, Hikaru' 
              AND black_player = 'Carlsen, Magnus'
              AND commentary_stats IS NOT NULL
              AND pgn_text IS NOT NULL
            ORDER BY date DESC
        """
        
        games_exported = 0
        
        try:
            results = self.client.query(query)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                print(f"\n📋 Exporting games:")
                for row in results:
                    if row.pgn_text and row.pgn_text.strip():
                        f.write(row.pgn_text)
                        f.write('\n\n')  # Add space between games
                        games_exported += 1
                        print(f"   {games_exported}. {row.date} - {row.event} ({row.result})")
            
            print(f"\n📊 EXPORT SUMMARY:")
            print(f"   Games exported: {games_exported}")
            print(f"   Output file: {output_file}")
            print(f"   File size: ~{self._get_file_size_mb(output_file):.1f} MB")
            print(f"   Ready for build_database.py processing!")
            
            return games_exported
        
        except Exception as e:
            print(f"❌ Error exporting commentary games: {e}")
            return 0
    
    def _get_file_size_mb(self, file_path: str) -> float:
        """Helper to get file size in MB"""
        try:
            import os
            return os.path.getsize(file_path) / (1024 * 1024)
        except:
            return 0.0


def main():
    """Main function for command-line usage"""
    
    if len(sys.argv) < 2:
        print("Usage: python explore_bigquery.py <project_id> [command]")
        print("Commands:")
        print("  count            - Get quick count of Nakamura vs Carlsen games")
        print("  sample           - Get sample games with details")
        print("  analyze          - Analyze game quality (50 games)")
        print("  events           - Search by major events")
        print("  exhaustive       - Full analysis of ALL Nakamura (W) vs Carlsen (B) games")
        print("  tournaments      - List every tournament they played in")
        print("  commentary       - Show all games with commentary")
        print("  all-games        - Enumerate every single game")
        print("  export-commentary - Export commentary games to PGN file")
        sys.exit(1)
    
    project_id = sys.argv[1]
    command = sys.argv[2] if len(sys.argv) > 2 else "count"
    
    print(f"🚀 Chess Game Explorer")
    print(f"   Project: {project_id}")
    print(f"   Command: {command}")
    
    explorer = ChessGameExplorer(project_id)
    
    if command == "count":
        results = explorer.quick_nakamura_carlsen_count()
    
    elif command == "sample":
        games = explorer.sample_nakamura_carlsen_games(limit=10)
        if games:
            quality_analysis = explorer.analyze_game_quality(games)
    
    elif command == "analyze":
        games = explorer.sample_nakamura_carlsen_games(limit=50)  # Get more for analysis
        if games:
            quality_analysis = explorer.analyze_game_quality(games)
    
    elif command == "events":
        # Search major events
        major_events = ["World Championship", "Candidates", "Grand Prix", "World Cup", "Sinquefield"]
        games = explorer.search_by_event(major_events)
        if games:
            quality_analysis = explorer.analyze_game_quality(games)
    
    elif command == "exhaustive":
        results = explorer.exhaustive_nakamura_white_analysis()
    
    elif command == "tournaments":
        tournaments = explorer.list_all_tournaments()
    
    elif command == "commentary":
        commentary_games = explorer.enumerate_commentary_games()
    
    elif command == "all-games":
        all_games = explorer.list_all_games()
    
    elif command == "export-commentary":
        games_exported = explorer.export_commentary_games_to_pgn()
        if games_exported > 0:
            print(f"🎉 Successfully exported {games_exported} commentary games!")
            print(f"📁 Next step: poetry run python build_database.py nakamura_carlsen_commentary.pgn 2000")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
    
    print(f"\n✅ Exploration completed!")


if __name__ == "__main__":
    main()
