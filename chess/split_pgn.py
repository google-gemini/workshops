import os
import math

def split_pgn_by_games(input_file, num_chunks=8):
    """Split PGN file into chunks at game boundaries"""
    
    file_size = os.path.getsize(input_file)
    chunk_size = file_size // num_chunks
    
    print(f"📂 Splitting {input_file} ({file_size/1024**3:.1f}GB) into {num_chunks} chunks...")
    
    chunk_files = []
    current_chunk = 0
    current_size = 0
    
    # Open output file for first chunk
    output_file = f"mega-chunk-{current_chunk}.pgn"
    chunk_files.append(output_file)
    output = open(output_file, 'w', encoding='utf-8')
    
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        in_game = False
        
        for line in f:
            # Check if we're starting a new game
            if line.startswith('[Event '):
                # If we're over chunk size and not on last chunk, start new chunk
                if (current_size > chunk_size and 
                    current_chunk < num_chunks - 1 and 
                    not in_game):
                    
                    output.close()
                    print(f"   ✓ Chunk {current_chunk}: {current_size/1024**2:.0f}MB -> {output_file}")
                    
                    current_chunk += 1
                    current_size = 0
                    output_file = f"mega-chunk-{current_chunk}.pgn"
                    chunk_files.append(output_file)
                    output = open(output_file, 'w', encoding='utf-8')
                
                in_game = True
            
            # Check if game is ending (empty line after moves)
            elif line.strip() == '' and in_game:
                in_game = False
            
            output.write(line)
            current_size += len(line.encode('utf-8'))
    
    output.close()
    print(f"   ✓ Chunk {current_chunk}: {current_size/1024**2:.0f}MB -> {output_file}")
    print(f"\n📊 Created {len(chunk_files)} chunks:")
    
    for i, chunk_file in enumerate(chunk_files):
        size = os.path.getsize(chunk_file) / 1024**2
        print(f"   {chunk_file}: {size:.0f}MB")
    
    return chunk_files

if __name__ == "__main__":
    chunks = split_pgn_by_games("mega-2025.pgn", 8)
