import os
import json

INPUT_DIR = "data/final_transcripts"
OUTPUT_DIR = "data/search"

os.makedirs(OUTPUT_DIR, exist_ok=True)

for file in os.listdir(INPUT_DIR):
    if not file.endswith("_merged.json"):
        continue

    with open(os.path.join(INPUT_DIR, file), "r", encoding="utf-8") as f:
        data = json.load(f)

    episode = data["episode"]
    segments = data["segments"]

    search_entries = []
    for seg in segments:
        search_entries.append({
            "start": seg["start"],
            "end": seg["end"],
            "text": seg["text"]
        })

    out_path = os.path.join(
        OUTPUT_DIR, episode + "_search.json"
    )

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "episode": episode,
            "entries": search_entries
        }, f, indent=2)

    print(f"✅ Search index created: {out_path}")

print("🎉 Search index generation completed.")
