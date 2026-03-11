# backend/summarization.py

from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import re


def generate_summary(text, num_sentences=3):
    """
    Generate extractive summary using TF-IDF sentence scoring
    """

    if not isinstance(text, str) or len(text.split()) < 40:
        return ""

    # Split into sentences
    sentence_pattern = re.compile(r'(?<=[.!?])\s+')
    sentences = sentence_pattern.split(text)

    if len(sentences) <= num_sentences:
        return text.strip()

    try:
        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = vectorizer.fit_transform(sentences)

        sentence_scores = tfidf_matrix.sum(axis=1)
        sentence_scores = np.array(sentence_scores).flatten()

        ranked_indices = np.argsort(sentence_scores)[::-1]
        top_indices = sorted(ranked_indices[:num_sentences])

        summary = " ".join([sentences[i] for i in top_indices])

        return summary.strip()

    except Exception as e:
        print("Summary error:", e)
        return ""