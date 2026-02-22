from typing import List, Dict
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

_MODEL = SentenceTransformer("all-MiniLM-L6-v2")


def segment_mixed_language(
    segments: List[Dict],
    base_threshold: float = 0.75,
    language_penalty: float = 0.15
) -> List[Dict]:

    texts = [s["text"] for s in segments]
    embeddings = _MODEL.encode(texts)

    topics = []
    topic_id = 0

    current = {
        "topic_id": topic_id,
        "start": segments[0]["start"],
        "end": segments[0]["end"],
        "segments": [segments[0]],
        "algorithm": "mixed_language"
    }

    for i in range(1, len(segments)):
        sim = cosine_similarity(
            [embeddings[i - 1]],
            [embeddings[i]]
        )[0][0]

        if segments[i]["language"] != segments[i - 1]["language"]:
            sim -= language_penalty

        if sim < base_threshold:
            topics.append(current)
            topic_id += 1
            current = {
                "topic_id": topic_id,
                "start": segments[i]["start"],
                "end": segments[i]["end"],
                "segments": [segments[i]],
                "algorithm": "mixed_language"
            }
        else:
            current["segments"].append(segments[i])
            current["end"] = segments[i]["end"]

    topics.append(current)
    return topics
