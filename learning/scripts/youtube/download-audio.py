#!/usr/bin/env python3
"""
Download audio from YouTube video

Usage:
  uv run scripts/youtube/download-audio.py kCc8FmEb1nY
  uv run scripts/youtube/download-audio.py kCc8FmEb1nY --output karpathy-gpt.mp3
"""

import argparse
import subprocess
from pathlib import Path


def download_audio(video_id: str, output_path: str | None = None) -> Path:
    """Download audio from YouTube video as MP3"""
    
    # Default output path
    if output_path is None:
        output_dir = Path.cwd() / "youtube" / video_id
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(output_dir / "audio.mp3")
    
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    
    print(f"📹 Downloading audio from: {video_url}")
    print(f"💾 Output: {output_path}\n")
    
    # Run yt-dlp
    subprocess.run([
        "yt-dlp",
        "-x",  # Extract audio
        "--audio-format", "mp3",
        "--audio-quality", "0",  # Best quality
        video_url,
        "-o", output_path,
    ], check=True)
    
    output_file = Path(output_path)
    
    if output_file.exists():
        size_mb = output_file.stat().st_size / (1024 * 1024)
        print(f"\n✅ Downloaded: {output_file}")
        print(f"📊 Size: {size_mb:.1f} MB")
        return output_file
    else:
        raise FileNotFoundError(f"Expected output file not found: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Download audio from YouTube")
    parser.add_argument("video_id", help="YouTube video ID (e.g., kCc8FmEb1nY)")
    parser.add_argument("-o", "--output", help="Output file path (default: youtube/{video_id}/audio.mp3)")
    
    args = parser.parse_args()
    
    try:
        output_file = download_audio(args.video_id, args.output)
        print(f"\n🎉 Success! Audio ready for transcription.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
