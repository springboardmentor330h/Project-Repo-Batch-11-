#!/usr/bin/env python3
"""
Run the full pipeline (preprocess → transcribe → segment + enrich) for all
audio files in audio_input/, without the Streamlit frontend.

Skips steps whose outputs already exist:
- If transcript JSON exists (e.g. transcripts/<episode>.json or <episode>(1).json)
  → skip preprocessing + transcription
- If segments_runtime/<episode>/segments.json exists → skip segmentation + enrichment

Usage (from project root):
  python run_pipeline.py

Place audio files (.mp3, .wav, .m4a) in audio_input/ before running.
"""

import json
import sys
from pathlib import Path

# Paths (must match app_alt and audio_preprocessing)
INPUT_DIR = Path("audio_input")
CHUNKS_DIR = Path("audio_chunks")
TRANSCRIPTS_DIR = Path("transcripts")
SEGMENTS_DIR = Path("segments_runtime")

SUPPORTED_EXTENSIONS = {".mp3", ".wav", ".m4a"}


def get_transcript_path_for_episode(episode_name: str) -> Path | None:
    """Return path to existing transcript JSON for this episode, if any."""
    exact = TRANSCRIPTS_DIR / f"{episode_name}.json"
    if exact.exists():
        return exact
    # e.g. episode_name(1).json from get_unique_filename
    for p in TRANSCRIPTS_DIR.glob(f"{episode_name}*.json"):
        if p.stem.startswith(episode_name):
            return p
    return None


def main():
    INPUT_DIR.mkdir(exist_ok=True)
    TRANSCRIPTS_DIR.mkdir(exist_ok=True)
    SEGMENTS_DIR.mkdir(exist_ok=True)

    from audio_preprocessing import process_file
    from transcription_generation import transcribe_episode
    from app_alt import build_segments_from_json

    files = [
        f
        for f in INPUT_DIR.iterdir()
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
    ]
    if not files:
        print("No audio files found in audio_input/. Add .mp3, .wav, or .m4a files.")
        sys.exit(0)

    print(f"Found {len(files)} audio file(s) in audio_input/.\n")

    for i, file_path in enumerate(sorted(files), 1):
        episode_name = file_path.stem
        print(f"[{i}/{len(files)}] {file_path.name}")

        # ---- Step 1: Transcript (preprocess + transcribe if needed) ----
        json_path = get_transcript_path_for_episode(episode_name)
        if json_path is None:
            print("  → Preprocessing...")
            process_file(file_path)
            print("  → Transcribing...")
            transcribe_episode(CHUNKS_DIR / episode_name)
            json_path = get_transcript_path_for_episode(episode_name)
            if json_path is None:
                print("  ⚠ Transcript JSON not found after transcription; skipping.")
                continue
            print(f"  → Transcript: {json_path.name}")
        else:
            print("  → Using existing transcript.")

        # ---- Step 2: Segments (segment + enrich if needed) ----
        seg_dir = SEGMENTS_DIR / episode_name
        seg_path = seg_dir / "segments.json"
        if seg_path.exists():
            print("  → Using existing segments.")
            continue

        print("  → Segmenting + enriching (keywords, summary, title, sentiment)...")
        try:
            segments, total_duration = build_segments_from_json(str(json_path))
        except Exception as e:
            print(f"  ⚠ Segmentation failed: {e}")
            continue

        if not segments:
            print("  ⚠ No segments produced; skipping.")
            continue

        seg_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "episode_name": episode_name,
            "source_transcript": str(json_path),
            "total_duration": total_duration,
            "n_segments": len(segments),
            "segments": segments,
        }
        with open(seg_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print(f"  → Saved {len(segments)} segments to {seg_path}")

    print("\nDone.")


if __name__ == "__main__":
    main()
