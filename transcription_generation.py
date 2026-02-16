# transcription_generation.py

import whisper
from pathlib import Path
import json
import re

# ================= CONFIG =================
CHUNKS_DIR = Path("audio_chunks")
TRANSCRIPTS_DIR = Path("transcripts")
MODEL_SIZE = "base"   # tiny | base | small | medium
LANGUAGE = "en"
CHUNK_DURATION = 120  # 2 minutes in seconds (must match preprocessing)
# ==========================================

TRANSCRIPTS_DIR.mkdir(exist_ok=True)

print("Loading Whisper model...")
model = whisper.load_model(MODEL_SIZE)
print("Model loaded.\n")


# ------------------------------------------------------------
# Utility Functions
# ------------------------------------------------------------

def get_unique_filename(path: Path) -> Path:
    counter = 1
    original = path
    while path.exists():
        path = original.with_name(f"{original.stem}({counter}){original.suffix}")
        counter += 1
    return path


def numeric_sort_key(file_path: Path):
    match = re.search(r"(\d+)$", file_path.stem)
    return int(match.group(1)) if match else 0


def format_timestamp(seconds: float):
    """
    Convert seconds → SRT timestamp format HH:MM:SS,mmm
    """
    millis = int((seconds - int(seconds)) * 1000)
    seconds = int(seconds)
    hrs = seconds // 3600
    mins = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hrs:02}:{mins:02}:{secs:02},{millis:03}"


# ------------------------------------------------------------
# Core Transcription
# ------------------------------------------------------------

def transcribe_episode(episode_folder: Path):
    print(f"\nTranscribing episode: {episode_folder.name}")

    chunk_files = sorted(
        episode_folder.glob("*.wav"),
        key=numeric_sort_key
    )

    if not chunk_files:
        print("No chunk files found.")
        return

    all_segments = []
    full_text_blocks = []
    srt_entries = []
    segment_counter = 1

    for chunk_index, chunk_file in enumerate(chunk_files):
        print(f"   → Processing {chunk_file.name}")

        result = model.transcribe(
            str(chunk_file),
            fp16=False,
            language=LANGUAGE,
            temperature=0.0,
            condition_on_previous_text=False,
            beam_size=5
        )

        chunk_offset = chunk_index * CHUNK_DURATION

        for seg in result["segments"]:
            global_start = seg["start"] + chunk_offset
            global_end = seg["end"] + chunk_offset
            text = " ".join(seg["text"].strip().split())

            # JSON segment
            all_segments.append({
                "id": segment_counter,
                "start": round(global_start, 3),
                "end": round(global_end, 3),
                "text": text
            })

            # TXT block
            full_text_blocks.append(text)

            # SRT block
            srt_entries.append(
                f"{segment_counter}\n"
                f"{format_timestamp(global_start)} --> {format_timestamp(global_end)}\n"
                f"{text}\n"
            )

            segment_counter += 1

    # ------------------------------------------------------------
    # Save JSON (MASTER FILE)
    # ------------------------------------------------------------

    json_data = {
        "episode_name": episode_folder.name,
        "model": MODEL_SIZE,
        "language": LANGUAGE,
        "chunk_duration": CHUNK_DURATION,
        "total_segments": len(all_segments),
        "segments": all_segments
    }

    json_path = get_unique_filename(
        TRANSCRIPTS_DIR / f"{episode_folder.name}.json"
    )

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2)

    print(f"Saved JSON transcript: {json_path.name}")

    # ------------------------------------------------------------
    # Save TXT (Human readable)
    # ------------------------------------------------------------

    txt_path = get_unique_filename(
        TRANSCRIPTS_DIR / f"{episode_folder.name}.txt"
    )

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(full_text_blocks))

    print(f"Saved TXT transcript: {txt_path.name}")

    # ------------------------------------------------------------
    # Save SRT (Optional subtitle format)
    # ------------------------------------------------------------

    srt_path = get_unique_filename(
        TRANSCRIPTS_DIR / f"{episode_folder.name}.srt"
    )

    with open(srt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_entries))

    print(f"Saved SRT file: {srt_path.name}")


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def main():
    if not CHUNKS_DIR.exists():
        print("audio_chunks folder not found.")
        return

    episode_folders = [f for f in CHUNKS_DIR.iterdir() if f.is_dir()]

    if not episode_folders:
        print("No chunked episodes found.")
        return

    for episode in episode_folders:
        transcribe_episode(episode)


if __name__ == "__main__":
    main()
