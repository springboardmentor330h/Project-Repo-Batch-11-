"""
styles.py — Shared CSS Styles for LEXARA UI
-----------------------------------------------
This module provides shared style constants and CSS utilities
for consistent styling across the LEXARA application.
"""

# UI Color Palette
COLORS = {
    "primary": "#667eea",
    "secondary": "#764ba2",
    "success": "#4CAF50",
    "warning": "#FF9800",
    "error": "#F44336",
    "info": "#2196F3",
    "dark": "#1a1a1a",
    "light": "#f5f7fa",
    "text_dark": "#1a1a1a",
    "text_light": "#ffffff",
}

# Segment colors for timeline visualization
SEGMENT_COLORS = [
    '#2196F3',  # Blue
    '#4CAF50',  # Green
    '#FF9800',  # Orange
    '#9C27B0',  # Purple
    '#00BCD4',  # Cyan
    '#E91E63',  # Pink
    '#3F51B5',  # Indigo
    '#009688',  # Teal
]

# CSS class definitions (for reference)
CSS_CLASSES = {
    "content_box": "content-box",
    "transcript_box": "transcript-box",
    "topic_box": "topic-box",
    "info_box": "info-box",
    "metric_box": "metric-box",
    "step_header": "step-header",
    "sub_header": "sub-header",
    "keyword_tag": "keyword-tag",
    "translation_box": "translation-box",
    "localization_box": "localization-box",
}

# Sentiment color classes
SENTIMENT_CLASSES = {
    "POSITIVE": "sentiment-positive",
    "NEUTRAL": "sentiment-neutral",
    "NEGATIVE": "sentiment-negative",
}


def get_sentiment_class(sentiment: str) -> str:
    """Get the CSS class for a sentiment value."""
    return SENTIMENT_CLASSES.get(sentiment.upper(), "sentiment-neutral")


def get_segment_color(index: int) -> str:
    """Get a segment color by index (cycles through available colors)."""
    return SEGMENT_COLORS[index % len(SEGMENT_COLORS)]
