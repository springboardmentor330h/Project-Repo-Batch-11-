# backend/sentiment_analysis.py

from textblob import TextBlob


def analyze_sentiment(
    input_data,
    positive_threshold=0.1,
    negative_threshold=-0.1
):
    """
    Perform sentiment analysis on text.
    Returns: Positive / Negative / Neutral
    """

    if not isinstance(input_data, str):
        return "Neutral"

    text = input_data.strip()

    if not text:
        return "Neutral"

    try:
        polarity = TextBlob(text).sentiment.polarity

        if polarity > positive_threshold:
            return "Positive"
        elif polarity < negative_threshold:
            return "Negative"
        else:
            return "Neutral"

    except Exception as e:
        print("Sentiment error:", e)
        return "Neutral"