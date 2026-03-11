# backend/keyword_extraction.py

import re
from sklearn.feature_extraction.text import TfidfVectorizer


def clean_text_for_keywords(text):
    """
    Remove timestamps, numbers, and unwanted tokens
    """

    # Remove timestamp patterns like [8.80 - 14.48]
    text = re.sub(r"\[\d+(\.\d+)?\s*-\s*\d+(\.\d+)?\]", " ", text)

    # Remove standalone numbers
    text = re.sub(r"\b\d+\b", " ", text)

    # Remove decimal numbers
    text = re.sub(r"\b\d+\.\d+\b", " ", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def extract_keywords(input_data, max_keywords=10):
    """
    Extract meaningful TF-IDF keywords from text.
    Returns list of clean keywords.
    """

    if not isinstance(input_data, str):
        return []

    text = input_data.strip()

    if len(text.split()) < 30:
        return []

    try:
        # 🔥 Clean timestamps & numbers first
        text = clean_text_for_keywords(text)

        vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=50,
            token_pattern=r"\b[a-zA-Z]{3,}\b"  # only real words (min 3 letters)
        )

        tfidf = vectorizer.fit_transform([text])
        scores = tfidf.toarray()[0]
        feature_names = vectorizer.get_feature_names_out()

        # Sort by score
        sorted_indices = scores.argsort()[::-1]
        top_keywords = [
            feature_names[i]
            for i in sorted_indices[:max_keywords]
            if scores[i] > 0
        ]

        return top_keywords

    except Exception as e:
        print("Keyword extraction error:", e)
        return []