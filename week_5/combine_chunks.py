import json
import os

input_folder = "../week 1_3/transcripts"
output_file = "../week 1_3/combined_segments.json"

segments = []

# Read all chunk files
for filename in sorted(os.listdir(input_folder)):
    if filename.endswith(".json"):
        file_path = os.path.join(input_folder, filename)

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

            segments.append({
                "title": filename.replace(".json", ""),
                "text": data.get("text", str(data))
            })

# Save combined file
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(segments, f, indent=2)

print("Combined transcript saved as combined_segments.json")
