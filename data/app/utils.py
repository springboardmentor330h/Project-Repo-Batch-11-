# app/utils.py

import streamlit as st
import os
import re
import json
from io import BytesIO
from pathlib import Path
import base64

import pandas as pd
import numpy as np
import torch

# AUDIO PROCESSING IMPORTS
from pydub import AudioSegment
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3
from mutagen.mp3 import MP3
import unidecode


# NLP / MODEL IMPORTS
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sentence_transformers import SentenceTransformer, util
from faster_whisper import WhisperModel

# VISUALIZATION
from wordcloud import WordCloud
import plotly.graph_objects as go

# DOWNLOAD NLTK DATA
nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)
nltk.download("stopwords", quiet=True)

# ============================================================
# GLOBAL MODELS
# ============================================================

@st.cache_resource
def load_whisper_model():
    """
    Loads Whisper speech-to-text model.
    Uses GPU if available, otherwise CPU.
    Cached to prevent reloading on every rerun.
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    return WhisperModel("tiny", device=device)

@st.cache_resource
def load_embedder():
    """
    Loads Sentence-BERT model for embeddings.
    Used for segmentation, summarization, and keyword ranking.
    """
    return SentenceTransformer("all-MiniLM-L6-v2")

@st.cache_resource
def load_sentiment_analyzer():
    """
    Loads VADER sentiment analyzer.
    """
    return SentimentIntensityAnalyzer()

# Instantiate global models once
WHISPER_MODEL = load_whisper_model()
EMBEDDER = load_embedder()
SENTIMENT_ANALYZER = load_sentiment_analyzer()

# ============================================================
# GLOBAL SIDEBAR
# ============================================================

def render_global_sidebar(logo_path: Path):
    """
    Renders shared sidebar across all pages.
    Includes: Logo, Dark mode toggle
    """
    with st.sidebar:

        if logo_path.exists():
            st.image(logo_path, width=180)
        else:
            st.markdown("## 🎙️ Castly")

        if "dark_mode" not in st.session_state:
            st.session_state.dark_mode = False

        st.session_state.dark_mode = st.toggle(
            "Dark Mode",
            value=st.session_state.dark_mode,
            key="global_dark_toggle"
        )

        st.divider()

    return st.session_state.dark_mode

# ============================================================
# APPLY THEME
# ============================================================

def apply_theme(dark_mode: bool):

    if dark_mode:
        bg = "#0f172a"          
        text = "#e2e8f0"        
        card = "#1e293b"        
        sidebar_bg = "#111827"  
        border = "#334155"      
        muted = "#94a3b8"       # Secondary text
    else:
        bg = "#f9fafb"
        text = "#1e293b"
        card = "white"
        sidebar_bg = "#ffffff"
        border = "#e5e7eb"
        muted = "#6b7280"

    # Custom CSS
    st.markdown(f"""
    <style>

    /* Main app */
    [data-testid="stAppViewContainer"] {{
        background-color: {bg};
        color: {text};
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: {sidebar_bg} !important;
        border-right: 1px solid {border};
    }}

    /* Cards */
    .card {{
        background: {card};
        border-radius: 14px;
        padding: 1.5rem;
        border: 1px solid {border};
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
        margin-bottom: 1.5rem;
    }}

    /* Feature cards */
    .feature-card {{
        height: 220px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }}

    /* Headings */
    h1, h2, h3, h4 {{
        color: {text} !important;
    }}

    /* Muted text */
    p {{
        color: {muted};
    }}

    /* Buttons */
    .stButton > button {{
        border-radius: 10px;
        border: 1px solid {border};
    }}

    /* Inputs */
    .stTextInput input,
    .stSelectbox div[data-baseweb="select"] {{
        background-color: {card} !important;
        color: {text} !important;
    }}

    /* Expanders */
    div[data-testid="stExpander"] {{
        background-color: {card};
        border: 1px solid {border};
        border-radius: 12px;
    }}

    /* Divider */
    hr {{
        border-color: {border};
    }}

    footer {{
        visibility: hidden;
    }}

    </style>
    """, unsafe_allow_html=True)

# ============================================================
# AUDIO HELPERS
# ============================================================

def get_audio_title(audio_bytes: BytesIO, filename: str) -> str:
    """
    Extracts title metadata from MP3.
    Falls back to filename if metadata unavailable.
    """
    title = Path(filename).stem.replace("_", " ").title()
    try:
        tmp = "temp_title.mp3"
        audio_bytes.seek(0)
        with open(tmp, "wb") as f:
            f.write(audio_bytes.read())

        audio = MP3(tmp)
        tags = EasyID3(tmp)
        title = tags.get("title", [title])[0]

        os.remove(tmp)
    except:
        pass

    return title

# AUDIO TRIMMING
def trim_audio_if_needed(audio_bytes, quick_demo):
    """
    If quick demo mode enabled,
    trims audio to first 10 minutes.
    """

    if not quick_demo:
        return audio_bytes

    st.info("Trimming to first 10 minutes...")

    audio_bytes.seek(0)  # Reset pointer before processing

    input_size = len(audio_bytes.getvalue())

    try:
        audio = AudioSegment.from_file(audio_bytes)
        audio = audio[:10 * 60 * 1000]  # Slice first 10 minutes
        trimmed = BytesIO()
        audio.export(trimmed, format="wav")
        trimmed.seek(0)
        trimmed_size = len(trimmed.getvalue())
        st.write(f"Trimmed size: {trimmed_size} bytes")
        return trimmed
    except Exception as e:
        st.error(f"Trim failed: {e}")
        audio_bytes.seek(0)
        return audio_bytes

def extract_cover_art(audio_bytes: BytesIO, filename: str) -> str:
    """
    Extracts embedded album art (APIC frame).
    Returns base64 image string if available.
    """
    try:
        tmp = "temp_cover.mp3"
        audio_bytes.seek(0)
        with open(tmp, "wb") as f:
            f.write(audio_bytes.read())

        tags = ID3(tmp)
        for tag in tags.values():
            if tag.FrameID == "APIC":
                mime = tag.mime
                data = tag.data
                base64_img = base64.b64encode(data).decode("utf-8")
                os.remove(tmp)
                return f"data:{mime};base64,{base64_img}"

        os.remove(tmp)
    except:
        pass

    return None


@st.cache_data
def extract_segment_clip(audio_bytes: BytesIO, start_sec: float, duration_sec: int = 90):
    """
    Extracts short audio clip for preview playback.
    Default duration: 90 seconds.
    """
    audio_bytes.seek(0)
    try:
        audio = AudioSegment.from_file(audio_bytes)
        start_ms = int(start_sec * 1000)
        end_ms = min(start_ms + duration_sec * 1000, len(audio))

        clip = audio[start_ms:end_ms]
        buffer = BytesIO()
        clip.export(buffer, format="mp3")
        buffer.seek(0)
        return buffer
    except:
        return BytesIO()

# ============================================================
# TRANSCRIPTION
# ============================================================

def transcribe_audio(audio_bytes: BytesIO):
    """
    Runs Whisper transcription.
    Adds language detection + romanization.
    """

    tmp = "temp_upload.wav"
    audio_bytes.seek(0)

    with open(tmp, "wb") as f:
        f.write(audio_bytes.read())

    segments, info = WHISPER_MODEL.transcribe(tmp)
    os.remove(tmp)

    detected_lang = info.language.lower()

    # Store detected language globally
    st.session_state.detected_language = detected_lang

    sentences = []

    for seg in segments:
        text = seg.text.strip()
        sents = sent_tokenize(text)

        duration = (seg.end - seg.start) / max(len(sents), 1)
        current_time = seg.start

        for s in sents:

            romanized = (
                unidecode.unidecode(s)
                if detected_lang != "en"
                else s
            )

            sentences.append({
                "text": s,
                "romanized": romanized,
                "language": detected_lang,
                "start": current_time,
                "end": current_time + duration
            })

            current_time += duration

    return sentences

# ============================================================
# SEGMENTATION
# ============================================================

def create_segments(sentences, threshold=0.65, min_segment_size=3):
    """
    Groups sentences into topic-based segments.
    Uses cosine similarity between embeddings.
    """
    if not sentences:
        return []

    texts = [s["text"] for s in sentences]
    embeddings = EMBEDDER.encode(texts, convert_to_tensor=True)

    segments = []
    current_segment = [sentences[0]]
    current_embeddings = [embeddings[0]]

    for i in range(1, len(sentences)):

        segment_mean = torch.mean(torch.stack(current_embeddings), dim=0)
        similarity = util.cos_sim(segment_mean, embeddings[i])[0][0].item()

        if similarity < threshold and len(current_segment) >= min_segment_size:
            segments.append(current_segment)
            current_segment = [sentences[i]]
            current_embeddings = [embeddings[i]]
        else:
            current_segment.append(sentences[i])
            current_embeddings.append(embeddings[i])

    if current_segment:
        segments.append(current_segment)

    return segments

# ============================================================
# ENRICHMENT
# ============================================================

def generate_summary(text: str, max_sentences=3):
    """
    Extractive summarization using embedding similarity
    between sentence vectors and document centroid.
    """
    sentences = sent_tokenize(text)

    if len(sentences) <= max_sentences:
        return text

    sentence_embeddings = EMBEDDER.encode(sentences, convert_to_tensor=True)
    document_embedding = torch.mean(sentence_embeddings, dim=0)

    scores = util.cos_sim(document_embedding, sentence_embeddings)[0]
    ranked = sorted(zip(sentences, scores.tolist()), key=lambda x: x[1], reverse=True)

    top_sentences = [s for s, _ in ranked[:max_sentences]]

    # Preserve original order
    final_summary = [s for s in sentences if s in top_sentences]

    return " ".join(final_summary)

def get_keywords(text: str, top_n=6):
    """
    Extracts top semantic keywords.
    Ranks candidate words via embedding similarity.
    """
    words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    stop = set(stopwords.words("english"))
    candidates = list(set([w for w in words if w not in stop]))

    if not candidates:
        return []

    segment_embedding = EMBEDDER.encode(text, convert_to_tensor=True)
    word_embeddings = EMBEDDER.encode(candidates, convert_to_tensor=True)

    scores = util.cos_sim(segment_embedding, word_embeddings)[0]
    ranked = sorted(zip(candidates, scores.tolist()), key=lambda x: x[1], reverse=True)

    return [w for w, _ in ranked[:top_n]]

def highlight_keywords(text: str, keywords: list):
    """
    Wraps keywords in HTML span for UI highlighting.
    """
    if not keywords:
        return text

    for kw in keywords:
        text = re.sub(
            rf"\b({re.escape(kw)})\b",
            r"<span class='kw'>\1</span>",
            text,
            flags=re.IGNORECASE
        )
    return text

# ============================================================
# LIBRARY HELPERS
# ============================================================

def load_library_data(segment_dir: Path) -> pd.DataFrame:
    """
    Loads all episode JSON files and returns
    a flattened DataFrame (one row per segment).
    Computes sentiment dynamically.
    """
    rows = []

    if not segment_dir.exists():
        return pd.DataFrame()

    for f in segment_dir.glob("*.json"):
        try:
            data = json.load(open(f, encoding="utf-8"))
            ep_match = re.search(r"\d+", data.get("episode_id", ""))
            ep_num = int(ep_match.group()) if ep_match else 0

            for seg in data.get("segments", []):
                text = seg.get("text_preview", "")
                score = SENTIMENT_ANALYZER.polarity_scores(text)["compound"]

                sentiment = (
                    "Positive" if score >= 0.05 else
                    "Negative" if score <= -0.05 else
                    "Neutral"
                )

                start = seg.get("start_time_sec", 0.0)
                duration = seg.get("duration_sec", 60)

                rows.append({
                    "episode": ep_num,
                    "segment": seg.get("segment_id", 0),
                    "summary": seg.get("summary", ""),
                    "keywords": seg.get("keywords", []),
                    "text": text,
                    "start_sec": start,
                    "end_sec": start + duration,
                    "sentiment": sentiment,
                    "sentiment_score": round(score, 2)
                })

        except:
            pass

    return pd.DataFrame(rows)

def load_episode_titles(csv_path: Path):
    """Returns episode_number → title mapping."""
    try:
        df_titles = pd.read_csv(csv_path)
        df_titles["episode_number"] = df_titles["episode_number"].astype(str)
        return dict(zip(df_titles["episode_number"], df_titles["title"]))
    except:
        return {}

def get_episode_image_path(image_dir: Path, episode: int):
    """Returns episode cover image path if available."""
    for ext in [".jpg", ".jpeg", ".png", ".JPG", ".PNG"]:
        img = image_dir / f"{episode}{ext}"
        if img.exists():
            return img
    return None

def get_audio_path(audio_dir: Path, episode: int):
    """Returns episode audio file path if available."""
    for ext in [".mp3", ".m4a", ".wav"]:
        path = audio_dir / f"{episode}{ext}"
        if path.exists():
            return path
    return None

# ============================================================
# TIMELINE HELPER
# ============================================================

def create_timeline_plot(df: pd.DataFrame):
    """
    Creates horizontal bar timeline of segments.
    Sentiment determines color.
    """
    fig = go.Figure()

    colors = {
        "Positive": "#10b981",
        "Negative": "#ef4444",
        "Neutral": "#f59e0b"
    }

    for _, r in df.iterrows():
        duration = (r["end_sec"] - r["start_sec"]) / 60

        fig.add_trace(go.Bar(
            x=[duration],
            y=["Timeline"],
            base=[r["start_sec"] / 60],
            orientation="h",
            marker_color=colors.get(r["sentiment"], "#94a3b8"),
            showlegend=False
        ))

    fig.update_layout(
        height=160,
        xaxis_title="Time (minutes)",
        yaxis_visible=False
    )

    return fig
