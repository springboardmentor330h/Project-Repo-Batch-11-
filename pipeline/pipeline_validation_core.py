import json
import sys
from pathlib import Path


REQUIRED_TOP_LEVEL_KEYS = {
    "audio_file": str,
    "language_detected": str,
    "topics": list
}

REQUIRED_TOPIC_KEYS = {
    "topic_id": int,
    "segments": list
}

REQUIRED_SEGMENT_KEYS = {
    "start": (int, float),
    "end": (int, float),
    "text": str,
    "translation": str,
    "romanized": str
}


def validate_schema(data: dict) -> None:
    for key, expected_type in REQUIRED_TOP_LEVEL_KEYS.items():
        if key not in data:
            raise ValueError(f"Missing top-level key: {key}")
        if not isinstance(data[key], expected_type):
            raise TypeError(f"Key '{key}' must be {expected_type}")

    for topic in data["topics"]:
        for key, expected_type in REQUIRED_TOPIC_KEYS.items():
            if key not in topic:
                raise ValueError(f"Topic missing key: {key}")
            if not isinstance(topic[key], expected_type):
                raise TypeError(f"Topic key '{key}' must be {expected_type}")

        for seg in topic["segments"]:
            for key, expected_type in REQUIRED_SEGMENT_KEYS.items():
                if key not in seg:
                    raise ValueError(f"Segment missing key: {key}")
                if not isinstance(seg[key], expected_type):
                    raise TypeError(f"Segment key '{key}' must be {expected_type}")


def validate_file(input_path: str) -> None:
    input_path = Path(input_path)

    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {input_path}")

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    validate_schema(data)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python pipeline_validation_core.py <indexed_output.json>")
        sys.exit(1)

    input_file = sys.argv[1]
    validate_file(input_file)

    print("[ok] Pipeline schema validation passed")
