import time
import re

def fast_text_scan_nakamura_carlsen(pgn_file):
    """Super fast text-only scan for Nakamura vs Carlsen"""
    
    print(f"🏃‍♂️ Fast text scan of {pgn_file} for Nakamura vs Carlsen...")
    
    games_found = 0
    total_lines = 0
    start_time = time.time()
    
    # Simple regex patterns
    nakamura_pattern = re.compile(r'\[White ".*Nakamura, Hikaru.*"\]')
    carlsen_pattern = re.compile(r'\[Black ".*Carlsen, Magnus.*"\]')
    
    current_game_headers = []
    has_nakamura = False
    
    with open(pgn_file, 'r', encoding='utf-8', errors='ignore') as f:
        for line_num, line in enumerate(f, 1):
            total_lines += 1
            
            # Progress every 1M lines
            if line_num % 1000000 == 0:
                elapsed = time.time() - start_time
                rate = line_num / elapsed
                print(f"   {line_num:,} lines in {elapsed:.1f}s ({rate:,.0f} lines/sec), found {games_found} games")
            
            # Check if we're starting a new game
            if line.startswith('[Event '):
                # Reset for new game
                current_game_headers = [line]
                has_nakamura = False
            elif line.startswith('[') and current_game_headers:
                # Accumulate headers
                current_game_headers.append(line)
                
                # Check for our players
                if nakamura_pattern.search(line):
                    has_nakamura = True
                elif carlsen_pattern.search(line) and has_nakamura:
                    # Found both! Extract game info
                    games_found += 1
                    
                    # Extract basic info from headers
                    event = "Unknown"
                    date = "Unknown" 
                    result = "Unknown"
                    
                    for header in current_game_headers:
                        if '[Event ' in header:
                            event = header.split('"')[1] if '"' in header else "Unknown"
                        elif '[Date ' in header:
                            date = header.split('"')[1] if '"' in header else "Unknown"
                        elif '[Result ' in header:
                            result = header.split('"')[1] if '"' in header else "Unknown"
                    
                    print(f"   ✓ Game #{games_found}: {event} ({date}) - {result}")
            
            elif line.strip() == '' or line.startswith('1.'):
                # End of headers, reset
                current_game_headers = []
                has_nakamura = False
    
    elapsed = time.time() - start_time
    rate = total_lines / elapsed
    
    print(f"\n📊 FAST SCAN RESULTS:")
    print(f"   Total lines scanned: {total_lines:,}")
    print(f"   Nakamura vs Carlsen games found: {games_found}")
    print(f"   Total time: {elapsed:.1f} seconds")
    print(f"   Scan rate: {rate:,.0f} lines/second")
    print(f"   File processing rate: {(11 * 1024**3) / elapsed / (1024**2):.1f} MB/second")

if __name__ == "__main__":
    fast_text_scan_nakamura_carlsen("../mega-2025.pgn")
