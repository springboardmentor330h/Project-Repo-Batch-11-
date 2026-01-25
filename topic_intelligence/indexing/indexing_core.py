import json
import sys
from pathlib import Path


def build_index(input_path: str) -> dict:
    input_path = Path(input_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "topics" in data:
        return data

    if "segments" not in data:
        raise ValueError("Input JSON must contain 'segments' or 'topics'")

    topics = [
        {
            "topic_id": 0,
            "title": "Main Topic",
            "segments": data["segments"]
        }
    ]

    indexed = {
        "audio_file": data.get("audio_file"),
        "language_detected": data.get("language_detected"),
        "topics": topics
    }

    return indexed


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python indexing_core.py <segmented_output.json>")
        sys.exit(1)

    input_file = sys.argv[1]
    result = build_index(input_file)

    output_path = "indexed_output.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Indexed output saved to {output_path}")
