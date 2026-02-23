"""
Upload & Analyze Pipeline
Full NLP pipeline for user-uploaded audio files:
  Audio → Whisper Transcription → Sentence Split → Embedding Segmentation
  → BART Summarization → KeyBERT Keywords → TextBlob Sentiment
"""

import os
import tempfile
import whisper
import nltk
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import pipeline as hf_pipeline
from keybert import KeyBERT
from textblob import TextBlob

# Ensure NLTK data is available
nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)


# -----------------------------------------------
# LAZY MODEL LOADING (loaded once, cached in module)
# -----------------------------------------------

_whisper_model = None
_embed_model = None
_summarizer = None
_kw_model = None


def _get_whisper():
    global _whisper_model
    if _whisper_model is None:
        _whisper_model = whisper.load_model("base")
    return _whisper_model


def _get_embed_model():
    global _embed_model
    if _embed_model is None:
        _embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _embed_model


def _get_summarizer():
    global _summarizer
    if _summarizer is None:
        _summarizer = hf_pipeline(
            "summarization",
            model="facebook/bart-large-cnn",
            device=-1
        )
    return _summarizer


def _get_kw_model():
    global _kw_model
    if _kw_model is None:
        _kw_model = KeyBERT()
    return _kw_model


# -----------------------------------------------
# STEP 1: TRANSCRIBE AUDIO
# -----------------------------------------------

def transcribe_audio(audio_path):
    """Transcribe audio file using Whisper base model."""
    model = _get_whisper()
    result = model.transcribe(str(audio_path))
    return result["text"]


# -----------------------------------------------
# STEP 2: SENTENCE SPLITTING
# -----------------------------------------------

def split_sentences(text):
    """Split raw transcript into individual sentences using NLTK."""
    sentences = nltk.sent_tokenize(text)
    return [s.strip() for s in sentences if s.strip()]


# -----------------------------------------------
# STEP 3: EMBEDDING-BASED TOPIC SEGMENTATION
# -----------------------------------------------

def segment_by_embedding(sentences, sim_threshold=0.45, min_segment_len=3):
    """
    Group sentences into topic segments using sentence embeddings
    and cosine similarity.
    """
    if len(sentences) < 2:
        return [" ".join(sentences)]

    model = _get_embed_model()
    embeddings = model.encode(sentences)

    segments = []
    current = [sentences[0]]

    for i in range(len(sentences) - 1):
        sim = cosine_similarity(
            embeddings[i].reshape(1, -1),
            embeddings[i + 1].reshape(1, -1)
        )[0][0]

        if sim < sim_threshold and len(current) >= min_segment_len:
            segments.append(" ".join(current))
            current = []

        current.append(sentences[i + 1])

    if current:
        segments.append(" ".join(current))

    return segments


# -----------------------------------------------
# STEP 4: SUMMARIZATION
# -----------------------------------------------

def summarize_segment(text):
    """Summarize a segment using BART-large-CNN."""
    if len(text.strip()) < 40:
        return text.strip()

    summarizer = _get_summarizer()

    try:
        # Chunk if text is too long for the model
        max_input_length = 900
        chunks = [text[i:i + max_input_length]
                  for i in range(0, len(text), max_input_length)]

        summaries = []
        for chunk in chunks:
            if len(chunk.strip()) < 40:
                summaries.append(chunk.strip())
            else:
                result = summarizer(
                    chunk,
                    max_length=90,
                    min_length=20,
                    do_sample=False
                )
                summaries.append(result[0]["summary_text"])

        return " ".join(summaries)
    except Exception:
        return text[:150] + "..."


# -----------------------------------------------
# STEP 5: KEYWORD EXTRACTION
# -----------------------------------------------

def extract_keywords(text, top_n=5):
    """Extract top keywords from text using KeyBERT."""
    if len(text.strip()) < 20:
        return []

    kw_model = _get_kw_model()

    try:
        keywords = kw_model.extract_keywords(
            text,
            keyphrase_ngram_range=(1, 1),
            stop_words="english",
            top_n=top_n
        )
        return [kw[0] for kw in keywords]
    except Exception:
        return []


# -----------------------------------------------
# STEP 6: SENTIMENT ANALYSIS
# -----------------------------------------------

def analyze_sentiment(text):
    """Analyze sentiment using TextBlob. Returns (label, score)."""
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity

    if polarity > 0.1:
        label = "Positive"
    elif polarity < -0.1:
        label = "Negative"
    else:
        label = "Neutral"

    return label, round(polarity, 3)


# -----------------------------------------------
# FULL PIPELINE
# -----------------------------------------------

def run_full_pipeline(audio_path, progress_callback=None):
    """
    Run the complete analysis pipeline on an audio file.

    Args:
        audio_path: Path to the audio file
        progress_callback: Optional callable(stage_name, progress_float)

    Returns:
        dict with keys: transcript, segments (list of segment dicts)
    """

    def _progress(stage, value):
        if progress_callback:
            progress_callback(stage, value)

    # --- Stage 1: Transcription ---
    _progress("🎙️ Transcribing audio with Whisper...", 0.05)
    transcript = transcribe_audio(audio_path)
    _progress("🎙️ Transcription complete!", 0.25)

    # --- Stage 2: Sentence Splitting ---
    _progress("✂️ Splitting into sentences...", 0.30)
    sentences = split_sentences(transcript)
    _progress(f"✂️ Found {len(sentences)} sentences", 0.35)

    # --- Stage 3: Topic Segmentation ---
    _progress("🧠 Segmenting by topic...", 0.40)
    raw_segments = segment_by_embedding(sentences)
    _progress(f"🧠 Created {len(raw_segments)} segments", 0.50)

    # --- Stage 4–6: Per-segment analysis ---
    total_segs = len(raw_segments)
    result_segments = []

    for idx, seg_text in enumerate(raw_segments):
        seg_num = idx + 1
        base_progress = 0.50 + (0.45 * idx / max(total_segs, 1))

        # Summarize
        _progress(f"📝 Summarizing segment {seg_num}/{total_segs}...", base_progress)
        summary = summarize_segment(seg_text)

        # Keywords
        _progress(f"🔑 Extracting keywords for segment {seg_num}/{total_segs}...",
                  base_progress + 0.15 / max(total_segs, 1))
        keywords = extract_keywords(seg_text)

        # Sentiment
        sentiment_label, sentiment_score = analyze_sentiment(seg_text)

        result_segments.append({
            "id": seg_num,
            "title": seg_text[:80] + ("..." if len(seg_text) > 80 else ""),
            "text": seg_text,
            "summary": summary,
            "keywords": ", ".join(keywords) if keywords else "",
            "sentiment": sentiment_label,
            "sentiment_score": sentiment_score,
        })

    _progress("✅ Analysis complete!", 1.0)

    return {
        "transcript": transcript,
        "sentences": sentences,
        "segments": result_segments,
    }
