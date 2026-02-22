from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def segment_tfidf_lexical(
    sentences: List[Dict],
    threshold: float = 0.35
) -> List[Dict]:

    if not sentences:
        return []

    texts = [s["text"] for s in sentences]

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        min_df=1
    )

    tfidf = vectorizer.fit_transform(texts)

    topics = []
    topic_id = 0

    current_topic = {
        "topic_id": topic_id,
        "start": sentences[0]["start"],
        "end": sentences[0]["end"],
        "segments": [sentences[0]],
        "algorithm": "tfidf_lexical"
    }

    for i in range(1, len(sentences)):
        sim = cosine_similarity(
            tfidf[i - 1],
            tfidf[i]
        )[0][0]

        if sim < threshold:
            topics.append(current_topic)
            topic_id += 1
            current_topic = {
                "topic_id": topic_id,
                "start": sentences[i]["start"],
                "end": sentences[i]["end"],
                "segments": [sentences[i]],
                "algorithm": "tfidf_lexical"
            }
        else:
            current_topic["segments"].append(sentences[i])
            current_topic["end"] = sentences[i]["end"]

    topics.append(current_topic)
    return topics
