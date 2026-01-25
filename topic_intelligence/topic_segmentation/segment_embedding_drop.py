from typing import List, Dict
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


_MODEL = SentenceTransformer("all-MiniLM-L6-v2")


def segment_embedding_drop(
    sentences: List[Dict],
    drop_threshold: float = 0.15
) -> List[Dict]:

    if not sentences:
        return []

    texts = [s["text"] for s in sentences]
    embeddings = _MODEL.encode(texts)

    similarities = []
    for i in range(1, len(embeddings)):
        sim = cosine_similarity(
            [embeddings[i - 1]],
            [embeddings[i]]
        )[0][0]
        similarities.append(sim)

    similarities = np.array(similarities)

    topics = []
    topic_id = 0

    current_topic = {
        "topic_id": topic_id,
        "start": sentences[0]["start"],
        "end": sentences[0]["end"],
        "segments": [sentences[0]],
        "algorithm": "embedding_drop"
    }

    for i in range(1, len(sentences)):
        drop = similarities[i - 2] - similarities[i - 1] if i > 1 else 0

        if drop > drop_threshold:
            topics.append(current_topic)
            topic_id += 1
            current_topic = {
                "topic_id": topic_id,
                "start": sentences[i]["start"],
                "end": sentences[i]["end"],
                "segments": [sentences[i]],
                "algorithm": "embedding_drop"
            }
        else:
            current_topic["segments"].append(sentences[i])
            current_topic["end"] = sentences[i]["end"]

    topics.append(current_topic)
    return topics
