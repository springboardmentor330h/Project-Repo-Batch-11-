import whisper
import os
import json
from pathlib import Path

# -----------------------------
# CONFIG — WEEK 6 TESTING MODE
# -----------------------------

RAW_AUDIO_DIR = Path("data/raw_audio/genre2_news")
OUT_DIR = Path("data/transcripts/genre2_news")

OUT_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------
# LOAD MODEL
# -----------------------------

print("🎙️ Loading Whisper model...")
model = whisper.load_model("base")

# -----------------------------
# TRANSCRIBE FILES
# -----------------------------

audio_files = [
    f for f in RAW_AUDIO_DIR.iterdir()
    if f.suffix.lower() in [".wav", ".mp3", ".m4a"]
]

print(f"📂 Found {len(audio_files)} audio files for testing")

for audio_path in audio_files:

    out_file = audio_path.stem + ".json"
    out_path = OUT_DIR / out_file

    # Skip already done
    if out_path.exists():
        print(f"⏩ Skipping already transcribed: {audio_path.name}")
        continue

    print(f"📝 Transcribing: {audio_path.name}")

    result = model.transcribe(str(audio_path))

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

print("✅ News genre transcription completed.")
