import os
import json

TRANSCRIPT_DIR = "data/transcripts"
OUTPUT_FILE = "data/final_transcript.txt"

all_text = []

for file in sorted(os.listdir(TRANSCRIPT_DIR)):
    if file.endswith(".json"):
        path = os.path.join(TRANSCRIPT_DIR, file)

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        text = data.get("text", "")
        all_text.append(text.strip())

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(all_text))

print("Final transcript created at:", OUTPUT_FILE)
