from typing import List, Dict
from collections import Counter
import math
import re


def _tokenize(text: str) -> List[str]:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    return text.split()


def _cosine(counter_a: Counter, counter_b: Counter) -> float:
    intersection = set(counter_a) & set(counter_b)
    numerator = sum(counter_a[x] * counter_b[x] for x in intersection)

    sum_a = sum(v ** 2 for v in counter_a.values())
    sum_b = sum(v ** 2 for v in counter_b.values())
    denominator = math.sqrt(sum_a) * math.sqrt(sum_b)

    if denominator == 0:
        return 0.0

    return numerator / denominator


def segment(
    segments: List[Dict],
    window_size: int = 2,
    threshold: float = 0.25
) -> List[Dict]:
   
    if len(segments) <= window_size:
        return [{"topic_id": 0, "segments": segments}]

    topics = []
    topic_id = 0
    current = {
        "topic_id": topic_id,
        "segments": segments[:window_size]
    }

    for i in range(window_size, len(segments)):
        left_text = " ".join(
            s["text"] for s in segments[i - window_size:i]
        )
        right_text = segments[i]["text"]

        left_tokens = _tokenize(left_text)
        right_tokens = _tokenize(right_text)

        sim = _cosine(
            Counter(left_tokens),
            Counter(right_tokens)
        )

        if sim < threshold:
            topics.append(current)
            topic_id += 1
            current = {
                "topic_id": topic_id,
                "segments": [segments[i]]
            }
        else:
            current["segments"].append(segments[i])

    topics.append(current)
    return topics