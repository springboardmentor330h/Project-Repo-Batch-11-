import os
import json

TRANS_DIR = "data/transcripts"
OUT_DIR = "data/final_transcripts"

os.makedirs(OUT_DIR, exist_ok=True)

episodes = {}

# Process JSON transcripts (from whisper_transcribe_with_timestamps.py)
for file in os.listdir(TRANS_DIR):
    if not file.endswith(".json"):
        continue

    # Extract episode ID (assuming format episode_chunk_N.json)
    episode_id = file.split("_chunk_")[0]

    if episode_id not in episodes:
        episodes[episode_id] = []

    with open(os.path.join(TRANS_DIR, file), "r", encoding="utf-8") as f:
        data = json.load(f)

    # Offset timestamps if we have chunk metadata (future enhancement)
    # For now, we assume they are already relative or managed
    episodes[episode_id].extend(data["segments"])

# Sort and save merged transcripts
for ep, segments in episodes.items():
    segments_sorted = sorted(segments, key=lambda x: x["start"])

    merged = {
        "episode": ep,
        "segments": segments_sorted
    }

    out_path = os.path.join(OUT_DIR, f"{ep}_merged.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2)

    print(f"Merged transcript created: {out_path}")

print("✅ All transcripts merged successfully")
