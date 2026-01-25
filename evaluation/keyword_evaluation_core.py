

import json
from pathlib import Path
from collections import Counter
from itertools import combinations
import math


def normalize(text: str) -> str:
    return text.lower()


def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def summary_coverage(keywords, summary):
    summary_norm = normalize(summary)
    hits = [k for k in keywords if k in summary_norm]
    return round(len(hits) / max(len(keywords), 1), 3)


def topic_distinctiveness(topic_keywords):
    scores = {}
    for i, j in combinations(topic_keywords.keys(), 2):
        sim = jaccard(
            set(topic_keywords[i]),
            set(topic_keywords[j])
        )
        scores.setdefault(i, []).append(sim)
        scores.setdefault(j, []).append(sim)

    distinctiveness = {}
    for k, sims in scores.items():
        distinctiveness[k] = round(1 - (sum(sims) / len(sims)), 3)

    return distinctiveness


def keyword_diversity(all_keywords):
    total = len(all_keywords)
    unique = len(set(all_keywords))
    return round(unique / max(total, 1), 3)


def evaluate(segmented_path: Path):
    with open(segmented_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    topics = data.get("topics", [])

    report = {
        "total_topics": len(topics),
        "topics": [],
        "global": {}
    }

    topic_keywords_map = {}
    all_keywords_flat = []

    for idx, topic in enumerate(topics):
        keywords = topic.get("keywords", [])
        summary = topic.get("summary", "")

        topic_keywords_map[idx] = keywords
        all_keywords_flat.extend(keywords)

        topic_report = {
            "topic_id": idx,
            "keyword_count": len(keywords),
            "summary_coverage": summary_coverage(keywords, summary),
            "flags": []
        }

        if len(keywords) == 0:
            topic_report["flags"].append("EMPTY_KEYWORDS")

        if len(keywords) < 4:
            topic_report["flags"].append("LOW_KEYWORD_COUNT")

        if len(set(keywords)) < len(keywords):
            topic_report["flags"].append("DUPLICATE_KEYWORDS")

        report["topics"].append(topic_report)

    report["global"]["keyword_diversity"] = keyword_diversity(all_keywords_flat)
    report["global"]["topic_distinctiveness"] = topic_distinctiveness(topic_keywords_map)

    return report


if __name__ == "__main__":
    input_path = Path("outputs/segmented_output.json")
    output_path = Path("evaluation/keyword_quality_report.json")

    if not input_path.exists():
        raise FileNotFoundError("segmented_output.json not found")

    report = evaluate(input_path)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("[SUCCESS] Keyword quality report generated:")
    print(f"   {output_path}")
