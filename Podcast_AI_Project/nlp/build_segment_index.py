import os
import json
from pathlib import Path

# -----------------------------
# PATH CONFIG
# -----------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_TEXT_DIR = BASE_DIR / "data" / "processed_text"

SUMMARY_DIR = BASE_DIR / "results" / "summaries"
KEYWORD_FILE = BASE_DIR / "results" / "visualizations" / "segment_keywords.csv"

SEGMENT_OUT = BASE_DIR / "results" / "segments_final.json"

os.makedirs(SEGMENT_OUT.parent, exist_ok=True)

# -----------------------------
# LOAD OPTIONAL DATA
# -----------------------------

summary_map = {}

if SUMMARY_DIR.exists():
    for f in SUMMARY_DIR.glob("*.json"):
        with open(f, "r", encoding="utf-8") as fp:
            data = json.load(fp)
            summary_map.update(data)

# -----------------------------
# BUILD SEGMENTS
# -----------------------------

segments = []
global_id = 1

print("📥 Loading cleaned transcripts...")

for genre_folder in sorted(PROCESSED_TEXT_DIR.iterdir()):

    if not genre_folder.is_dir():
        continue

    genre = genre_folder.name
    print(f"\n📂 Processing genre: {genre}")

    for txt_file in sorted(genre_folder.glob("*.txt")):

        with open(txt_file, "r", encoding="utf-8") as f:
            text = f.read().strip()

        if not text:
            continue

        # ---------
        # SIMPLE SPLIT INTO PARAGRAPH SEGMENTS
        # ---------

        raw_chunks = [c.strip() for c in text.split("\n\n") if c.strip()]

        for chunk in raw_chunks:

            seg = {
                "id": global_id,
                "genre": genre,
                "source_file": txt_file.name,
                "title": chunk[:80] + "...",
                "text": chunk,
                "summary": "",
                "keywords": "",
                "sentiment": "neutral",
                "sentiment_score": 0.0,
            }

            # attach summary if exists
            if str(global_id) in summary_map:
                seg["summary"] = summary_map[str(global_id)]

            segments.append(seg)
            global_id += 1


print(f"\n📊 Total segments created: {len(segments)}")

# -----------------------------
# SAVE FINAL INDEX
# -----------------------------

with open(SEGMENT_OUT, "w", encoding="utf-8") as f:
    json.dump(segments, f, indent=2, ensure_ascii=False)

print(f"\n✅ Final segment index saved to: {SEGMENT_OUT}")
