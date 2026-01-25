import os
import json
import re

INPUT_DIR = "asr/output"
OUTPUT_DIR = "nlp_preprocessing/output"

FILLER_WORDS = [
    "uh", "um", "hmm", "ah", "er", "you know", "like"
]


def clean_text(text):
    text = text.lower()

    for filler in FILLER_WORDS:
        text = re.sub(rf"\b{filler}\b", "", text)

    text = re.sub(r"\s+", " ", text).strip()

    return text


def process_transcript(filename):
    input_path = os.path.join(INPUT_DIR, filename)
    output_path = os.path.join(OUTPUT_DIR, filename)

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    cleaned_segments = []

    for segment in data.get("segments", []):
        cleaned_segments.append({
            "start": segment["start"],
            "end": segment["end"],
            "text": clean_text(segment["text"])
        })

    output_data = {
        "language": data.get("language"),
        "segments": cleaned_segments
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)

    print(f"🧹 Cleaned transcript saved: {output_path}")


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for file in os.listdir(INPUT_DIR):
        if file.endswith(".json"):
            process_transcript(file)
