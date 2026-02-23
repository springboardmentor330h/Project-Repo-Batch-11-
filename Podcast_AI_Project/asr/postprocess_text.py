import json
import os
from pathlib import Path
import re

# -----------------------------
# PATHS
# -----------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

TRANSCRIPTS_DIR = BASE_DIR / "data" / "transcripts"
OUTPUT_DIR = BASE_DIR / "data" / "processed_text"

OUTPUT_DIR.mkdir(exist_ok=True)

print("🧹 Starting transcript post-processing...")

# -----------------------------
# CLEAN FUNCTION
# -----------------------------

def clean_text(text: str) -> str:
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    text = text.strip()
    return text


# -----------------------------
# PROCESS ALL GENRES
# -----------------------------

total_files = 0

for genre_folder in TRANSCRIPTS_DIR.iterdir():

    if not genre_folder.is_dir():
        continue

    print(f"\n📂 Processing genre: {genre_folder.name}")

    out_genre_dir = OUTPUT_DIR / genre_folder.name
    out_genre_dir.mkdir(exist_ok=True)

    for file in genre_folder.glob("*.json"):

        print("➡ Cleaning:", file.name)

        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Whisper format
        text = data.get("text", "")

        if not text:
            print("⚠ Empty transcript:", file.name)
            continue

        cleaned = clean_text(text)

        out_path = out_genre_dir / file.with_suffix(".txt").name

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(cleaned)

        total_files += 1

print("\n✅ Post-processing completed.")
print(f"📊 Total transcripts cleaned: {total_files}")
