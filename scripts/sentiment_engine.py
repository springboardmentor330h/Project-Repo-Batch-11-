from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

class SentimentAnalyzer:
    def __init__(self):
        try:
            nltk.data.find('sentiment/vader_lexicon')
        except LookupError:
            nltk.download('vader_lexicon', quiet=True)
        self.sia = SentimentIntensityAnalyzer()

    def analyze(self, text):
        """
        Calculates sentiment based on strict rules:
        - Uses VADER for emotional intensity.
        - Maps compound score (-1 to +1) to 1-10 scale.
        - Strict Categories: 1-4 (Negative), 5 (Neutral), 6-10 (Positive).
        """
        if not text:
            return {"label": "NEUTRAL", "score": 5.0}

        # VADER compound score is between -1.0 and 1.0
        scores = self.sia.polarity_scores(text)
        s = scores['compound']

        # Logic for 1-10 scale mapping:
        # - s = -1 => score = 1
        # - s = 0 => score = 5
        # - s = +1 => score = 10
        if s > 0:
            # Positive: 6-10 range
            # Note: s * 5 would map 1.0 to 5.0. 5 + 5 = 10.
            # Smallest positive s (e.g. 0.05) would be 5.25.
            # We ensure it's at least 6.0 if s > 0 as per "Positive results must fall between 6-10"
            normalized_score = round(max(6.0, 5 + (s * 5)), 1)
            label = "POSITIVE"
        elif s < 0:
            # Negative: 1-4 range
            # Note: s * 4 would map -1.0 to -4.0. 5 - 4 = 1.
            # Largest negative s (e.g. -0.05) would be 4.8.
            # We ensure it's at most 4.0 if s < 0 as per "Negative results must fall between 1-4"
            normalized_score = round(min(4.0, 5 + (s * 4)), 1)
            label = "NEGATIVE"
        else:
            # Neutral: exactly 5
            normalized_score = 5.0
            label = "NEUTRAL"
            
        return {
            "label": label,
            "score": normalized_score,
            "compound": s
        }
