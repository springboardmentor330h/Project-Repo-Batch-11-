from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import List, Dict
import numpy as np

_MODEL = SentenceTransformer("all-MiniLM-L6-v2")

MIN_SEGMENTS_PER_TOPIC = 3
SMOOTHING_WINDOW = 2
SIM_THRESHOLD = 0.55


def _smooth(values, window=2):
    smoothed = []
    for i in range(len(values)):
        start = max(0, i - window)
        end = min(len(values), i + window + 1)
        smoothed.append(sum(values[start:end]) / (end - start))
    return smoothed


def _extract_keywords(texts, top_k=5):
    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=1000
    )
    tfidf = vectorizer.fit_transform(texts)
    scores = np.asarray(tfidf.sum(axis=0)).ravel()
    indices = scores.argsort()[::-1][:top_k]
    features = vectorizer.get_feature_names_out()
    return [features[i] for i in indices]


def segment(segments: List[Dict]) -> List[Dict]:
    if not segments:
        return []

    texts = [s["text"] for s in segments]
    embeddings = _MODEL.encode(texts)

    sims = [
        cosine_similarity(
            [embeddings[i - 1]],
            [embeddings[i]]
        )[0][0]
        for i in range(1, len(segments))
    ]

    sims = _smooth(sims, SMOOTHING_WINDOW)

    topics = []
    current = [segments[0]]

    topic_id = 0

    for i, sim in enumerate(sims, start=1):
        if sim < SIM_THRESHOLD and len(current) >= MIN_SEGMENTS_PER_TOPIC:
            keywords = _extract_keywords([s["text"] for s in current])
            topics.append({
                "topic_id": topic_id,
                "segments": current,
                "keywords": keywords
            })
            topic_id += 1
            current = [segments[i]]
        else:
            current.append(segments[i])

    if current:
        keywords = _extract_keywords([s["text"] for s in current])
        topics.append({
            "topic_id": topic_id,
            "segments": current,
            "keywords": keywords
        })

    return topics
