from typing import List, Dict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def segment(
    segments: List[Dict],
    window_size: int = 3,
    threshold: float = 0.25
) -> List[Dict]:

    if len(segments) <= window_size:
        return [{
            "topic_id": 0,
            "segments": segments
        }]

    texts = [s["text"] for s in segments]

    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=5000
    )

    tfidf = vectorizer.fit_transform(texts)

    topics = []
    topic_id = 0

    current = {
        "topic_id": topic_id,
        "segments": segments[:window_size]
    }

    for i in range(window_size, len(segments)):
        prev_window = tfidf[i - window_size : i]
        next_window = tfidf[i : i + window_size]

        prev_vec = np.asarray(prev_window.mean(axis=0)).reshape(1, -1)
        next_vec = np.asarray(next_window.mean(axis=0)).reshape(1, -1)

        sim = cosine_similarity(prev_vec, next_vec)[0][0]

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
