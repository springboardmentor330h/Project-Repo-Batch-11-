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
        
        # Expert-level explanatory summary prompt
        prompt = f"Explain the core concept discussed in this text in a structured, expert-level paragraph. Include contextual depth and specific details: {key_points}"
        
        result = _llm(
            prompt,
            max_new_tokens=150,
            min_length=30,
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
    Create a unique extractive summary directly from the segment's transcript.
    No templates — summary is derived purely from the segment's own spoken content.
    """
    text = clean_text_for_summary(text)
    
    if not text or len(text.strip()) < 30:
        return "Brief audio segment."
    
    # Split into real sentences from the transcript
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 15]
    
    if not sentences:
        # If no proper sentences, take the first chunk of text directly
        words = text.split()
        if len(words) > 10:
            return ' '.join(words[:25]).strip() + '.'
        return text.strip() + '.'
    
    # Filler patterns to remove from transcript speech
    filler_pattern = re.compile(
        r'\b(you know|right|okay|basically|so|like|well|all right|'
        r'um|uh|I mean|let\'s see|let me|gonna|gotta)\b[,]?\s*',
        re.IGNORECASE
    )
    
    # Score each sentence by informativeness (content word density)
    scored_sentences = []
    for sent in sentences:
        # Clean fillers
        cleaned = filler_pattern.sub('', sent).strip()
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        if len(cleaned) < 15:
            continue
        
        # Score by content word density — more unique content words = more informative
        content_words = [w.lower() for w in cleaned.split() 
                        if w.lower() not in STOPWORDS and len(w) > 2]
        unique_content = set(content_words)
        
        # Higher score for more unique content words and moderate length
        word_count = len(cleaned.split())
        score = len(unique_content) * 3 + min(word_count, 20)
        
        # Penalize very short or very generic sentences
        if word_count < 5:
            score -= 10
        
        scored_sentences.append((score, cleaned))
    
    if not scored_sentences:
        # Direct fallback: use first sentence from transcript
        first = filler_pattern.sub('', sentences[0]).strip()
        first = re.sub(r'\s+', ' ', first).strip()
        if first:
            return first[0].upper() + first[1:] + ('.' if not first.endswith('.') else '')
        return sentences[0].strip() + '.'
    
    # Sort by score, pick top 2-3 most informative distinct sentences
    scored_sentences.sort(key=lambda x: x[0], reverse=True)
    
    selected = []
    for _, sent in scored_sentences:
        # Skip near-duplicates (sentences that start the same way)
        if selected and any(sent[:25].lower() == s[:25].lower() for s in selected):
            continue
        selected.append(sent)
        if len(selected) >= 3:
            break
    
    # Build the final summary from selected transcript sentences
    parts = []
    for sent in selected:
        # Ensure proper capitalization and punctuation
        sent = sent[0].upper() + sent[1:] if sent else sent
        if sent and not sent.endswith('.'):
            sent += '.'
        parts.append(sent)
    
    return ' '.join(parts)


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
