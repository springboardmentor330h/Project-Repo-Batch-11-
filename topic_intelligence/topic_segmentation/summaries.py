"""
summaries.py — Abstractive Summary Generation with LLM
-------------------------------------------------------
Uses LLM with proper prompting to generate concise abstractive summaries.
"""

import re
from collections import Counter

# =========================
# CONFIG
# =========================

USE_LLM = True
MAX_SUMMARY_LENGTH = 200
MIN_SENTENCE_LENGTH = 20
LLM_MODEL_NAME = "google/flan-t5-base"


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

def clean_text_for_summary(text: str) -> str:
    """Clean and prepare text for summarization."""
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) > 800:
        text = text[:800]
    return text


def extract_key_points(text: str) -> str:
    """Extract key points from text for better summarization."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > MIN_SENTENCE_LENGTH]
    
    if not sentences:
        return text
    
    # Get key sentences (first, middle, important ones)
    key_sentences = []
    
    # Always include first sentence (intro)
    if sentences:
        key_sentences.append(sentences[0])
    
    # Find sentences with key indicator words
    indicator_words = ['benefit', 'advantage', 'important', 'key', 'main', 'feature', 
                       'offer', 'provide', 'include', 'such as', 'for example']
    
    for sent in sentences[1:]:
        sent_lower = sent.lower()
        if any(word in sent_lower for word in indicator_words):
            if sent not in key_sentences:
                key_sentences.append(sent)
                if len(key_sentences) >= 3:
                    break
    
    # If we need more, add from middle
    if len(key_sentences) < 3 and len(sentences) > 2:
        mid = len(sentences) // 2
        if sentences[mid] not in key_sentences:
            key_sentences.append(sentences[mid])
    
    return " ".join(key_sentences[:4])


# =========================
# LLM ABSTRACTIVE SUMMARY
# =========================

_llm = None

def generate_abstractive_summary(text: str) -> str:
    """
    Generate abstractive summary using LLM with proper prompting.
    """
    global _llm
    
    if not USE_LLM:
        return create_simple_summary(text)
    
    try:
        if _llm is None:
            from transformers import pipeline
            _llm = pipeline(
                "text2text-generation",
                model=LLM_MODEL_NAME,
                device=-1
            )
        
        cleaned_text = clean_text_for_summary(text)
        key_points = extract_key_points(cleaned_text)
        
        if not key_points or len(key_points) < 50:
            return create_simple_summary(text)
        
        # Improved prompt for better summarization
        prompt = f"Summarize this in one sentence: {key_points}"
        
        result = _llm(
            prompt,
            max_new_tokens=80,
            min_length=15,
            do_sample=False,
            num_beams=4
        )
        
        if not result or not result[0].get('generated_text'):
            return create_simple_summary(text)
        
        summary = result[0]['generated_text'].strip()
        
        # Clean up the summary
        summary = summary.strip('.,!? ')
        
        # Make first letter uppercase if needed
        if summary and len(summary) > 1:
            summary = summary[0].upper() + summary[1:]
        
        # Ensure proper ending
        if summary and not summary.endswith('.'):
            summary += '.'
        
        # Limit length
        if len(summary) > MAX_SUMMARY_LENGTH:
            summary = summary[:MAX_SUMMARY_LENGTH-3] + "..."
        
        return summary
        
    except Exception as e:
        print(f"LLM summarization failed: {e}")
        return create_simple_summary(text)


def create_simple_summary(text: str) -> str:
    """
    Create a meaningful summary by analyzing the content themes.
    """
    text = clean_text_for_summary(text)
    
    # Extract meaningful words
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    words = [w for w in words if w not in STOPWORDS]
    
    if not words:
        return "This segment contains audio content."
    
    # Count word frequencies to find themes
    word_freq = Counter(words)
    top_words = [word for word, _ in word_freq.most_common(5)]
    
    # Detect content type and create appropriate summary
    text_lower = text.lower()
    
    # Check for song/music content patterns
    music_indicators = ['love', 'heart', 'feel', 'baby', 'night', 'dream', 'want', 'need', 
                        'wanna', 'gonna', 'slave', 'master', 'yours', 'mine', 'forever']
    is_music = sum(1 for w in music_indicators if w in text_lower) >= 2
    
    if is_music:
        # Create a music-style summary
        themes = []
        if any(w in text_lower for w in ['love', 'heart', 'yours', 'mine']):
            themes.append('love and devotion')
        if any(w in text_lower for w in ['want', 'wanna', 'need', 'desire']):
            themes.append('desire and longing')
        if any(w in text_lower for w in ['slave', 'master', 'control']):
            themes.append('passion and intensity')
        if any(w in text_lower for w in ['night', 'dream', 'feel']):
            themes.append('emotions and feelings')
        
        if themes:
            return f"This segment contains song lyrics expressing {' and '.join(themes[:2])}."
        return "This segment contains song lyrics with emotional themes."
    
    # For spoken content, summarize key themes
    if len(top_words) >= 3:
        themes = f"{top_words[0]}, {top_words[1]}, and {top_words[2]}"
        return f"This segment discusses topics related to {themes}."
    elif len(top_words) >= 1:
        return f"This segment focuses on {top_words[0]} and related themes."
    else:
        return "This segment contains spoken audio content."


# =========================
# MAIN ENTRY
# =========================

def generate_summary(text: str, keywords=None) -> str:
    """
    Generate an abstractive summary from the text.
    
    Args:
        text: The text to summarize
        keywords: Optional keywords for context
        
    Returns:
        A concise abstractive summary string
    """
    if not text or len(text.strip()) < 20:
        return "This topic discusses key concepts from the audio."
    
    return generate_abstractive_summary(text)
