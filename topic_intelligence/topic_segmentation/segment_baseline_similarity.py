from typing import List, Dict
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

MIN_TOPIC_DURATION = 25.0
SIMILARITY_DROP_THRESHOLD = 0.15


def segment_by_similarity(
    segments: List[Dict],
    embeddings: np.ndarray,
    similarity_threshold: float = 0.6,
) -> List[Dict]:

    if not segments or len(segments) <= 1:
        return _build_single_topic(segments)

    similarities = cosine_similarity(embeddings[:-1], embeddings[1:]).flatten()

    boundaries = []
    current_topic_start = segments[0]["start"]
    previous_similarity = similarities[0]

    for i, similarity in enumerate(similarities):
        current_time = segments[i + 1]["start"]
        topic_duration = current_time - current_topic_start
        similarity_drop = previous_similarity - similarity

        if topic_duration < MIN_TOPIC_DURATION:
            previous_similarity = similarity
            continue

        if similarity_drop < SIMILARITY_DROP_THRESHOLD:
            previous_similarity = similarity
            continue

        if similarity < similarity_threshold:
            boundaries.append(i + 1)
            current_topic_start = current_time

        previous_similarity = similarity

    topics = _build_topics_from_boundaries(segments, boundaries)

    topics = merge_short_topics(topics)

    return topics


def _build_single_topic(segments: List[Dict]) -> List[Dict]:
    return [{
        "topic_id": 0,
        "start": segments[0]["start"],
        "end": segments[-1]["end"],
        "segments": segments
    }]


def _build_topics_from_boundaries(
    segments: List[Dict],
    boundaries: List[int]
) -> List[Dict]:
    topics = []
    start_idx = 0
    topic_id = 0

    for boundary in boundaries:
        topic_segments = segments[start_idx:boundary]
        topics.append({
            "topic_id": topic_id,
            "start": topic_segments[0]["start"],
            "end": topic_segments[-1]["end"],
            "segments": topic_segments
        })
        topic_id += 1
        start_idx = boundary

    topic_segments = segments[start_idx:]
    topics.append({
        "topic_id": topic_id,
        "start": topic_segments[0]["start"],
        "end": topic_segments[-1]["end"],
        "segments": topic_segments
    })

    return topics


def merge_short_topics(
    topics: List[Dict],
    min_duration: float = MIN_TOPIC_DURATION
) -> List[Dict]:

    if not topics:
        return topics

    merged = [topics[0]]

    for topic in topics[1:]:
        duration = topic["end"] - topic["start"]

        if duration < min_duration:
            merged[-1]["segments"].extend(topic["segments"])
            merged[-1]["end"] = topic["end"]
        else:
            merged.append(topic)

    for idx, topic in enumerate(merged):
        topic["topic_id"] = idx

    return merged
