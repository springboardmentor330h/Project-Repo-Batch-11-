
from typing import List, Dict
import numpy as np


def evaluate_segmentation(topics: List[Dict]) -> Dict:
    if not topics:
        return {"error": "No topics to evaluate"}

    segment_lengths = []
    confidences = []

    for topic in topics:
        segment_lengths.append(len(topic["segments"]))
        conf = topic.get("boundary_confidence")
        if conf is not None:
            confidences.append(conf)

    metrics = {
        "num_topics": len(topics),
        "avg_segments_per_topic": round(np.mean(segment_lengths), 2),
        "std_segments_per_topic": round(np.std(segment_lengths), 2),
        "avg_boundary_confidence": round(np.mean(confidences), 3) if confidences else None,
        "min_boundary_confidence": round(min(confidences), 3) if confidences else None,
        "max_boundary_confidence": round(max(confidences), 3) if confidences else None
    }

    return metrics


if __name__ == "__main__":
    import json, sys

    if len(sys.argv) != 2:
        print("Usage: python evaluation_segmentation_core.py <segmented_json>")
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        data = json.load(f)

    topics = data.get("topics", [])
    results = evaluate_segmentation(topics)

    print(json.dumps(results, indent=2))
