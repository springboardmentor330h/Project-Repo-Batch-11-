# backend/topic_segmentation_embeddings.py

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


def segment_topics_embeddings(
    sentences,
    model_name="all-MiniLM-L6-v2",
    min_blocks_per_topic=3,
    similarity_drop_percentile=20
):
    """
    Segments text into topic blocks using embeddings.
    sentences: list of sentence strings
    """

    if not sentences or len(sentences) < 3:
        return sentences

    try:
        model = SentenceTransformer(model_name)
        embeddings = model.encode(sentences)

        similarities = []
        for i in range(len(embeddings) - 1):
            sim = cosine_similarity(
                embeddings[i].reshape(1, -1),
                embeddings[i + 1].reshape(1, -1)
            )[0][0]
            similarities.append(sim)

        if not similarities:
            return sentences

        threshold = np.percentile(similarities, similarity_drop_percentile)

        segments = []
        current_segment = [sentences[0]]

        for i, sim in enumerate(similarities):
            if sim < threshold and len(current_segment) >= min_blocks_per_topic:
                segments.append(" ".join(current_segment))
                current_segment = []

            current_segment.append(sentences[i + 1])

        if current_segment:
            segments.append(" ".join(current_segment))

        return segments

    except Exception as e:
        print("Topic segmentation error:", e)
        return sentences