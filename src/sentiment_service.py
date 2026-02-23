from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class SentimentAnalyzer:
    def __init__(self):
        """
        Initializes the VADER sentiment analyzer.
        VADER is specifically attuned to sentiments expressed in social media and conversation.
        """
        self.analyzer = SentimentIntensityAnalyzer()

    def analyze_segment(self, text):
        """
        Analyzes a segment of text and returns a sentiment label and score.
        """
        if not text or len(text.strip()) == 0:
            return {"label": "Neutral", "score": 0.0}

        scores = self.analyzer.polarity_scores(text)
        compound_score = scores['compound']

        # VADER compound score thresholds:
        # positive sentiment: compound score >= 0.05
        # neutral sentiment: (compound score > -0.05) and (compound score < 0.05)
        # negative sentiment: compound score <= -0.05
        
        if compound_score >= 0.05:
            label = "Positive"
        elif compound_score <= -0.05:
            label = "Negative"
        else:
            label = "Neutral"

        return {
            "label": label,
            "score": round(compound_score, 4)
        }

if __name__ == "__main__":
    # Test
    analyzer = SentimentAnalyzer()
    test_texts = [
        "I love this podcast! It's so insightful and positive.",
        "This is a total disaster. I hate how this turned out.",
        "Today we are talking about the weather in Seattle."
    ]
    
    for text in test_texts:
        result = analyzer.analyze_segment(text)
        print(f"Text: {text}\nResult: {result}\n")
