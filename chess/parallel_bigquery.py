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

import concurrent.futures
import glob
import os
import subprocess
import sys


def process_chunk(chunk_info):
  """Process one PGN chunk"""
  chunk_file, chunk_num, project_id, start_from = chunk_info

  print(
      f"🚀 Starting chunk {chunk_num}: {chunk_file} (start from game"
      f" {start_from})"
  )

  cmd = [
      "python",
      "pgn_to_bigquery_native.py",
      chunk_file,
      project_id,
      "999999999",  # max_games (unlimited)
      str(start_from) if start_from else "0",  # start_from
  ]

  try:
    result = subprocess.run(cmd, capture_output=False, text=True)  # No timeout

    if result.returncode == 0:
      print(f"✅ Chunk {chunk_num} completed successfully")
      return True, chunk_num, None
    else:
      error_msg = f"Chunk {chunk_num} failed: {result.stderr}"
      print(f"❌ {error_msg}")
      return False, chunk_num, error_msg

  except Exception as e:
    error_msg = f"Chunk {chunk_num} error: {str(e)}"
    print(f"❌ {error_msg}")
    return False, chunk_num, error_msg


def parallel_process_chunks(
    chunk_files, project_id, max_workers=8, start_from=0
):
  """Process all chunks in parallel"""

  chunk_info = [
      (chunk, i, project_id, start_from) for i, chunk in enumerate(chunk_files)
  ]

  print(
      f"🔄 Processing {len(chunk_files)} chunks with {max_workers} workers..."
  )
  print(f"   Each chunk will be uploaded to the same BigQuery table")
  print(f"   Note: First chunk replaces table, others append")

  successful_chunks = 0
  failed_chunks = []

  with concurrent.futures.ProcessPoolExecutor(
      max_workers=max_workers
  ) as executor:
    # Submit all tasks
    future_to_chunk = {
        executor.submit(process_chunk, chunk): chunk for chunk in chunk_info
    }

    # Process results as they complete
    for future in concurrent.futures.as_completed(future_to_chunk):
      success, chunk_num, error = future.result()

      if success:
        successful_chunks += 1
        print(
            f"📊 Progress: {successful_chunks}/{len(chunk_files)} chunks"
            " completed"
        )
      else:
        failed_chunks.append((chunk_num, error))

  print(f"\n📊 Final Results:")
  print(f"   ✅ Successful: {successful_chunks}/{len(chunk_files)} chunks")
  print(f"   ❌ Failed: {len(failed_chunks)} chunks")

  if failed_chunks:
    print(f"\n❌ Failed chunks:")
    for chunk_num, error in failed_chunks:
      print(f"   Chunk {chunk_num}: {error}")

  return successful_chunks == len(chunk_files)


if __name__ == "__main__":
  if len(sys.argv) < 2:
    print(
        "Usage: python parallel_bigquery.py <project_id> [max_workers]"
        " [start_from]"
    )
    print("Example: python parallel_bigquery.py project-0615388941 8 331000")
    sys.exit(1)

  project_id = sys.argv[1]
  max_workers = int(sys.argv[2]) if len(sys.argv) > 2 else 8
  start_from = int(sys.argv[3]) if len(sys.argv) > 3 else 0

  # Find chunk files
  chunks = sorted(glob.glob("mega-chunk-*.pgn"))

  if not chunks:
    print("❌ No chunk files found. Run split_pgn.py first!")
    print("   Expected files: mega-chunk-0.pgn, mega-chunk-1.pgn, etc.")
    sys.exit(1)

  print(f"📁 Found {len(chunks)} chunks:")
  total_size = 0
  for chunk in chunks:
    size = os.path.getsize(chunk) / 1024**2
    total_size += size
    print(f"   {chunk}: {size:.0f}MB")

  print(f"   Total size: {total_size/1024:.1f}GB")
  print(f"   Using {max_workers} parallel workers")

  success = parallel_process_chunks(chunks, project_id, max_workers, start_from)

  if success:
    print("\n🎉 All chunks processed successfully!")
    print("\nOptional cleanup:")
    print("   rm mega-chunk-*.pgn  # Remove chunk files to save disk space")
  else:
    print("\n❌ Some chunks failed - check errors above")
    print("   You may want to retry failed chunks individually")
