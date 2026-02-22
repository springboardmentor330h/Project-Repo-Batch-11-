import json
import sys
from pathlib import Path


def evaluate_indexed_output(input_path: str) -> dict:
    input_path = Path(input_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "topics" not in data:
        raise ValueError("Input JSON does not contain 'topics'")

    total_segments = 0
    translated_segments = 0
    romanized_segments = 0

    length_ratios = []
    warnings = []

    for topic in data["topics"]:
        for seg in topic.get("segments", []):
            total_segments += 1

            text = seg.get("text", "").strip()
            translation = seg.get("translation", "").strip()
            romanized = seg.get("romanized", "").strip()

            if translation:
                translated_segments += 1
            else:
                warnings.append(f"Missing translation at segment {seg.get('segment_id')}")

            if romanized:
                romanized_segments += 1
            else:
                warnings.append(f"Missing romanization at segment {seg.get('segment_id')}")

            if text and translation:
                ratio = len(translation) / max(len(text), 1)
                length_ratios.append(ratio)

                if ratio < 0.5 or ratio > 2.0:
                    warnings.append(
                        f"Length anomaly at segment {seg.get('segment_id')} (ratio={ratio:.2f})"
                    )

    avg_ratio = round(sum(length_ratios) / max(len(length_ratios), 1), 3)

    report = {
        "coverage": {
            "total_segments": total_segments,
            "translation_coverage": round(translated_segments / max(total_segments, 1), 3),
            "romanization_coverage": round(romanized_segments / max(total_segments, 1), 3)
        },
        "length_stats": {
            "average_ratio": avg_ratio,
            "total_checked": len(length_ratios)
        },
        "segmentation": {
            "total_topics": len(data["topics"]),
            "avg_segments_per_topic": round(
                total_segments / max(len(data["topics"]), 1), 2
            )
        },
        "warnings": warnings
    }

    return report


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python evaluation_core.py <indexed_output.json>")
        sys.exit(1)

    input_file = sys.argv[1]
    evaluation = evaluate_indexed_output(input_file)

    output_path = "evaluation_report.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(evaluation, f, indent=2, ensure_ascii=False)

    print(f"Evaluation report saved to {output_path}")
