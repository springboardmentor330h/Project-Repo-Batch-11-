"""
topic_title_generator.py — Context-Aware Topic Title Generation
----------------------------------------------------------------
Generates concise, semantic, and human-readable topic titles
using LLM with proper prompting. Titles are limited to 8-10 words.
"""

import re
from collections import Counter

# =========================
# CONFIG
# =========================

USE_LLM = True
MAX_TITLE_WORDS = 10
MIN_TITLE_WORDS = 3
LLM_MODEL_NAME = "google/flan-t5-base"
UNKNOWN_TITLE = "UNKNOWN"

# =========================
# STOPWORDS
# =========================

STOPWORDS = {
    "the", "a", "an", "this", "that", "these", "those",
    "i", "you", "he", "she", "it", "we", "they", "them", "their", "our", "your",
    "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did",
    "can", "could", "may", "might", "must", "shall", "should", "will", "would",
    "and", "or", "but", "so", "because", "for", "with", "without",
    "from", "to", "in", "on", "at", "by", "of", "as", "about", "into", "over", "after",
    "now", "then", "here", "there", "okay", "alright", "yes", "no",
    "just", "like", "well", "also", "very", "basically", "actually",
}


# =========================
# UTILITIES
# =========================

def clean_text_for_title(text: str) -> str:
    """Clean and prepare text for title generation."""
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) > 500:
        text = text[:500]
    return text


def extract_key_concepts(text: str) -> list:
    """Extract key concepts from text for title generation."""
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    words = [w for w in words if w not in STOPWORDS]
    
    if not words:
        return []
    
    word_freq = Counter(words)
    return [word for word, _ in word_freq.most_common(5)]


def truncate_to_word_limit(title: str, max_words: int = MAX_TITLE_WORDS) -> str:
    """Truncate title to maximum word count."""
    words = title.split()
    if len(words) <= max_words:
        return title
    return " ".join(words[:max_words])


# =========================
# LLM TITLE GENERATION
# =========================

_llm = None


def generate_llm_title(text: str) -> str:
    """
    Generate a concise topic title using LLM.
    """
    global _llm
    
    try:
        if _llm is None:
            from transformers import pipeline
            _llm = pipeline(
                "text2text-generation",
                model=LLM_MODEL_NAME,
                device=-1
            )
        
        cleaned_text = clean_text_for_title(text)
        
        if not cleaned_text or len(cleaned_text) < 30:
            return create_fallback_title(text)
        
        # Improved prompt for better title generation
        prompt = f"What is this text about? Summarize in 5-7 words: {cleaned_text}"
        
        result = _llm(
            prompt,
            max_new_tokens=25,
            min_length=3,
            do_sample=False,
            num_beams=4
        )
        
        if not result or not result[0].get('generated_text'):
            return create_fallback_title(text)
        
        title = result[0]['generated_text'].strip()
        
        # Clean up the title
        title = title.strip('.,!?:;"\'')
        title = re.sub(r'^(title:|topic:|about:?)\s*', '', title, flags=re.IGNORECASE)
        
        # Capitalize first letter of each word
        title = title.title()
        
        # Enforce word limit
        title = truncate_to_word_limit(title)
        
        # Validate - if too short or generic, use fallback
        word_count = len(title.split())
        if word_count < MIN_TITLE_WORDS or 'and' in title.lower().split()[-1:]:
            return create_fallback_title(text)
        
        return title
        
    except Exception as e:
        print(f"LLM title generation failed: {e}")
        return create_fallback_title(text)


def create_fallback_title(text: str) -> str:
    """
    Create a fallback title by extracting the first meaningful phrase.
    """
    # Clean and get first sentence
    cleaned = clean_text_for_title(text)
    sentences = re.split(r'[.!?]', cleaned)
    
    if sentences:
        first_sent = sentences[0].strip()
        # Extract first 6-8 meaningful words
        words = first_sent.split()
        meaningful = [w for w in words if w.lower() not in STOPWORDS and len(w) > 1]
        
        if len(meaningful) >= 3:
            # Create title from first meaningful words
            title_words = meaningful[:6]
            title = ' '.join(w.title() for w in title_words)
            return truncate_to_word_limit(title)
    
    # Final fallback: extract theme from content
    key_concepts = extract_key_concepts(text)
    
    if not key_concepts:
        return "Audio Segment Content"
    
    # Create a more natural title
    if len(key_concepts) >= 2:
        title = f"{key_concepts[0].title()} and {key_concepts[1].title()} Theme"
    else:
        title = f"{key_concepts[0].title()} Content"
    
    return truncate_to_word_limit(title)


# =========================
# MAIN ENTRY
# =========================

def generate_topic_title(text: str, keywords: list = None) -> str:
    """
    Generate a context-aware topic title from the text.
    
    Args:
        text: The text to generate a title for
        keywords: Optional keywords for context
        
    Returns:
        A concise topic title (max 8-10 words) or UNKNOWN if ambiguous
    """
    if not text or len(text.strip()) < 20:
        return UNKNOWN_TITLE
    
    if USE_LLM:
        return generate_llm_title(text)
    else:
        return create_fallback_title(text)


def validate_topic_title(title: str) -> bool:
    """
    Validate that a topic title meets constraints.
    
    Args:
        title: The title to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not title or title == UNKNOWN_TITLE:
        return True  # UNKNOWN is valid for ambiguous content
    
    word_count = len(title.split())
    
    if word_count < MIN_TITLE_WORDS:
        return False
    
    if word_count > MAX_TITLE_WORDS:
        return False
    
    return True
