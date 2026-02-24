import os
import json
from pathlib import Path
from collections import Counter
import re

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import altair as alt

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from audio_preprocessing import process_file as preprocess_file
from transcription_generation import transcribe_episode
from keywords_and_summaries import (
    extract_keywords_tfidf,
    build_segment_title,
    normalize_text,
    summarize_t5,
)
from add_sentiment import get_sentiment


# ==========================================
# CONFIG & CUSTOM TITLES
# ==========================================
INPUT_DIR = Path("audio_input")
CHUNKS_DIR = Path("audio_chunks")
TRANSCRIPTS_DIR = Path("transcripts")
SEGMENTS_DIR = Path("segments_runtime")

MODEL_NAME = "all-MiniLM-L6-v2"

# --- CUSTOM DISPLAY NAMES ---
# Map your filenames (without .json) to the nice title you want to see.
# EDIT THIS LIST WITH YOUR REAL PODCAST NAMES
EPISODE_TITLES = {
    "001a81a9-b741-5565-a93b-70084cc13984":"Habit Coach Podcast: Phone Addiction",
    "49f4c57d-8abe-5b2d-8b9f-a11cba38f47e":"Habit Coach Podcast: Seven Minute Exercise",
    "4f3d84ad-0e27-5cee-a811-979277546fbe":"Habit Coach Podcast: Self Help",
    "GlobalNewsPodcast-20260212-ClimateBoostAsChinasCO2EmissionsFall":"Global News Podcast: Climate Boost As China's CO2 Emissions Fall",
    "Habit_Coach_Podcast_Voting":"Habit Coach Podcast: Voting",
    "Taylor_Swift_-_Taylor_Swift_-_Blank_Space_(mp3.pm)":"Taylor Swift: Blank Space",
    "c3bf2f21-028c-5fea-9d6d-3dc7cee00f84":"Habit Coach Podcast: Muscular Body",
    "f462fed1-9372-5097-be9a-74449e678f77":"Habit Coach Podcast: Asset or Liability",
    "podcast001_TRdL6ZzWBS0.resampled":"Lex Fridman: podcast001",
    "podcast002_TPXTmVdlyoc.resampled":"Lex Fridman: podcast002",
    "podcast008_aSyZvBrPAyk.resampled":"Lex Fridman: podcast008",
    "podcast011__VPxEcT_Adc.resampled":"Lex Fridman: podcast011",
    "podcast019_kD5yc1LQrpQ.resampled":"Lex Fridman: podcast019",
    "podcast021_Z_LhPMhkEdw.resampled":"Lex Fridman: podcast021",
    "podcast023_QDN6xvhAw94.resampled":"Lex Fridman: podcast023",
    "podcast036_HYsLTNXMl1Q.resampled":"Lex Fridman: podcast036",
    "podcast039_SGSOCuByo24.resampled":"Lex Fridman: podcast039"
    # If a file isn't listed here, it will just show the filename nicely formatted
}

# =======================
# HELPERS
# =======================

def format_dropdown_label(option):
    """
    Custom formatter for the dropdown.
    1. Checks if a custom title exists in EPISODE_TITLES.
    2. If not, auto-formats the filename.
    3. Keeps 'Add New' as is.
    """
    if option == "➕ Add New Episode...":
        return option
    
    # CHECK FOR CUSTOM NAME
    if option in EPISODE_TITLES:
        return EPISODE_TITLES[option]
    
    # Fallback: just make the filename look nice (lex_fridman -> Lex Fridman)
    return option.replace("_", " ").replace("-", " ").title()


def summary_has_repetition(summary: str) -> bool:
    """Check if the summary has repeating trigrams (looping error)."""
    if not summary:
        return False
    words = summary.lower().split()
    trigrams = [" ".join(words[i : i + 3]) for i in range(len(words) - 2)]
    if not trigrams:
        return False
    counts = Counter(trigrams)
    return any(v > 2 for v in counts.values())

def format_time(seconds: float) -> str:
    """Convert seconds to mm:ss format."""
    seconds = max(0.0, float(seconds))
    m = int(seconds // 60)
    s = int(round(seconds % 60))
    return f"{m:02d}:{s:02d}"

# =======================
# SEGMENTATION LOGIC
# =======================
SENT_SPLIT_RE = r'(?<=[\.\?\!])\s+|\n+'

@st.cache_resource
def load_embedding_model():
    return SentenceTransformer(MODEL_NAME)

@st.cache_resource
def load_t5_model():
    """Load local T5 model."""
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    local_dir = "models/t5-small"
    tokenizer = AutoTokenizer.from_pretrained(local_dir, local_files_only=True)
    model = AutoModelForSeq2SeqLM.from_pretrained(local_dir, local_files_only=True)
    model.eval()
    return model, tokenizer

def split_into_sentences(text: str):
    if not isinstance(text, str) or text.strip() == "":
        return []
    pieces = [s.strip() for s in re.split(SENT_SPLIT_RE, text) if s and s.strip()]
    return pieces

def word_count(text: str) -> int:
    return len(text.split())

def compute_text_similarities(texts, model):
    if len(texts) < 2:
        return np.array([], dtype=float)
    embeddings = model.encode(texts, show_progress_bar=False)
    sims = []
    for i in range(len(embeddings) - 1):
        sim = cosine_similarity(
            embeddings[i].reshape(1, -1),
            embeddings[i + 1].reshape(1, -1)
        )[0][0]
        sims.append(float(sim))
    return np.array(sims, dtype=float)

def detect_boundaries_from_sims(sims, auto_k: float = 1.0):
    boundaries = [0]
    if sims.size == 0:
        return boundaries
    sims_mean = float(np.mean(sims))
    sims_std = float(np.std(sims))
    threshold = max(0.0, sims_mean - auto_k * sims_std)
    for i, s in enumerate(sims):
        if s < threshold:
            boundaries.append(i + 1)
    return boundaries

def build_segments_from_units(units, boundaries):
    segments = []
    for seg_id, start_idx in enumerate(boundaries):
        if seg_id + 1 < len(boundaries):
            end_idx = boundaries[seg_id + 1] - 1
        else:
            end_idx = len(units) - 1
        unit_slice = units[start_idx:end_idx + 1]
        seg_text = " ".join(u.get("text", "") for u in unit_slice).strip()
        if not seg_text:
            continue
        segments.append({
            "segment_id": seg_id,
            "start_unit": start_idx,
            "end_unit": end_idx,
            "start_time": float(unit_slice[0]["start"]),
            "end_time": float(unit_slice[-1]["end"]),
            "text": seg_text,
            "num_words": word_count(seg_text)
        })
    return segments

def enrich_segments(segments):
    t5_model = None
    t5_tokenizer = None
    try:
        t5_model, t5_tokenizer = load_t5_model()
    except Exception:
        pass

    for seg in segments:
        raw_text = normalize_text(seg.get("text", ""))
        kws = extract_keywords_tfidf(raw_text, top_k=10)
        seg["keywords"] = kws

        summary = ""
        if t5_model and t5_tokenizer:
            try:
                summary = summarize_t5(t5_model, t5_tokenizer, raw_text)
            except Exception:
                pass
        
        if not summary:
            sents = split_into_sentences(raw_text)
            summary = " ".join(sents[:2]) if sents else raw_text[:200]
        
        seg["summary"] = summary
        
        title = build_title_from_summary(summary, max_chars=60)
        if not title:
            title = build_segment_title(kws, summary, max_words=3)
        seg["title"] = title

        score, label = get_sentiment(raw_text)
        seg["sentiment_score"] = score
        seg["sentiment_label"] = label
    return segments

# =======================
# UI HELPERS
# =======================

def render_timeline(segments, total_duration: float):
    if not segments:
        st.info("Timeline not available.")
        return
    rows = []
    for seg in segments:
        rows.append({
            "segment": f"S{seg['segment_id']}",
            "start": float(seg.get("start_time", 0.0)),
            "end": float(seg.get("end_time", 0.0)),
            "sentiment": seg.get("sentiment_label", "Neutral"),
            "title": seg.get("title", ""),
            "start_label": format_time(seg.get("start_time", 0.0)),
            "end_label": format_time(seg.get("end_time", 0.0)),
        })
    df = pd.DataFrame(rows)
    timeline = (
        alt.Chart(df)
        .mark_bar(height=30)
        .encode(
            x=alt.X("start:Q", axis=alt.Axis(title="Time (mm:ss)", labelExpr="floor(datum.value/60) + ':' + (datum.value % 60 < 10 ? '0' : '') + (datum.value % 60)")),
            x2="end:Q",
            color=alt.Color("sentiment:N", scale=alt.Scale(domain=["Positive", "Neutral", "Negative"], range=["#4CAF50", "#FFC107", "#F44336"])),
            tooltip=["segment", "sentiment", "title", alt.Tooltip("start_label:N", title="Start"), alt.Tooltip("end_label:N", title="End")],
        )
        .properties(height=90)
    )
    st.altair_chart(timeline, use_container_width=True)

DISPLAY_STOPWORDS = {"yeah", "oh", "okay", "right", "know", "thing", "et", "cetera"}

def clean_keywords_for_display(keywords):
    return [kw for kw in keywords if kw.lower() not in DISPLAY_STOPWORDS]

def render_keyword_cloud(keywords):
    from wordcloud import WordCloud
    if not keywords:
        st.info("No keywords available.")
        return
    freq = {kw: 1 for kw in keywords}
    wc = WordCloud(width=600, height=300, background_color="white").generate_from_frequencies(freq)
    fig, ax = plt.subplots()
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)

def build_title_from_summary(summary: str, max_chars: int = 60) -> str:
    if not isinstance(summary, str): return ""
    s = summary.strip().replace("\n", " ")
    if not s: return ""
    sentences = re.split(r"(?<=[.!?])\s+", s)
    first = sentences[0].strip() if sentences else s
    if len(first) > max_chars:
        cut = first[:max_chars]
        if " " in cut: cut = cut.rsplit(" ", 1)[0]
        first = cut
    if first: first = first[0].upper() + first[1:]
    return first

@st.cache_data
def build_segments_from_json(json_transcript_path_str: str):
    with open(json_transcript_path_str, "r", encoding="utf-8") as f:
        data = json.load(f)
    units = data.get("segments", [])
    if not units: return [], 0.0
    units = sorted(units, key=lambda u: u.get("start", 0.0))
    total_duration = float(units[-1].get("end", 0.0))
    texts = [u.get("text", "") for u in units]
    model = load_embedding_model()
    sims = compute_text_similarities(texts, model)
    boundaries = detect_boundaries_from_sims(sims, auto_k=1.0)
    segments = build_segments_from_units(units, boundaries)
    segments = enrich_segments(segments)
    return segments, total_duration

# =======================
# MAIN APP
# =======================
def main():
    st.set_page_config(page_title="Automated Podcast Transcription", layout="wide")
    st.title("Automated Podcast Transcription and Topic Segmentation")
    st.caption("Upload an audio file → preprocessing → transcription → segmentation → keywords, summaries, sentiment → navigate by segments.")

    # 1. UNIFIED LIBRARY & UPLOAD LOGIC
    TRANSCRIPTS_DIR.mkdir(exist_ok=True)
    existing_files = sorted([f.stem for f in TRANSCRIPTS_DIR.glob("*.json")])
    options = existing_files + ["➕ Add New Episode..."]
    
    if "selected_episode" not in st.session_state:
        st.session_state.selected_episode = options[0] if existing_files else "➕ Add New Episode..."
    
    if st.session_state.selected_episode not in options:
        st.session_state.selected_episode = "➕ Add New Episode..."

    # UNIFIED DROPDOWN WITH CUSTOM NAMES
    selected_option = st.selectbox(
        "Select an Episode from Library:", 
        options,
        index=options.index(st.session_state.selected_episode),
        format_func=format_dropdown_label
    )

    episode_name = ""
    
    if selected_option == "➕ Add New Episode...":
        uploaded = st.file_uploader("Upload New Audio (MP3/WAV)", type=["mp3", "wav", "m4a"])
        if not uploaded:
            st.info("Upload a podcast/audio file to start processing.")
            return

        INPUT_DIR.mkdir(exist_ok=True)
        file_path = INPUT_DIR / uploaded.name
        with open(file_path, "wb") as f:
            f.write(uploaded.read())
        
        episode_name = file_path.stem
        if (TRANSCRIPTS_DIR / f"{episode_name}.json").exists():
            st.warning(f"'{episode_name}' already exists! Switching to it...")
            st.session_state.selected_episode = episode_name
            st.rerun()    
    else:
        episode_name = selected_option
        file_path = None 

    json_transcript_path = TRANSCRIPTS_DIR / f"{episode_name}.json"

    # 2. PROCESSING PIPELINE
    if not json_transcript_path.exists():
        if file_path is None:
             st.error("File path missing for processing.")
             return
        with st.status("Processing New Episode...", expanded=True) as status:
            st.write("1. Preprocessing audio...")
            preprocess_file(file_path)
            episode_chunk_dir = CHUNKS_DIR / episode_name
            st.write("2. Running Whisper transcription...")
            transcribe_episode(episode_chunk_dir)
            status.update(label="Processing Complete!", state="complete", expanded=False)
        
        if json_transcript_path.exists():
            st.session_state.selected_episode = episode_name
            st.rerun()
        else:
             st.error("Transcript JSON was not created.")
             return

    # 3. SEGMENTATION & ENRICHMENT
    SEGMENTS_DIR.mkdir(exist_ok=True)
    episode_seg_dir = SEGMENTS_DIR / episode_name
    episode_seg_dir.mkdir(exist_ok=True)
    segments_json_path = episode_seg_dir / "segments.json"

    if segments_json_path.exists():
        with open(segments_json_path, "r", encoding="utf-8") as f:
            seg_payload = json.load(f)
        segments = seg_payload.get("segments", [])
        total_duration = float(seg_payload.get("total_duration", segments[-1]["end_time"] if segments else 0.0))
    else:
        with st.spinner("Computing semantic similarities and segmenting transcript..."):
            segments, total_duration = build_segments_from_json(str(json_transcript_path))
        if not segments:
            st.error("Segmentation produced no segments.")
            return
        seg_payload = {
            "episode_name": episode_name,
            "source_transcript": str(json_transcript_path),
            "total_duration": total_duration,
            "n_segments": len(segments),
            "segments": segments,
        }
        with open(segments_json_path, "w", encoding="utf-8") as f:
            json.dump(seg_payload, f, ensure_ascii=False, indent=2)

    st.success(f"Loaded {len(segments)} segments.")

    # 4. VISUALIZATION
    st.markdown("### Timeline")
    render_timeline(segments, total_duration)

    # 5. EXPLORATION & SEARCH (Week 4 Req)
    st.markdown("### Explore Segments")
    search_query = st.text_input("Search Transcripts or Keywords", "").lower()

    display_segments = []
    for s in segments:
        # Micro-segment filter (Week 6 Req)
        if s.get("num_words", 0) < 15:
            continue
        # Search filter (Week 4 Req)
        if search_query:
            content = (s.get("title", "") + " " + s.get("summary", "") + " " + " ".join(s.get("keywords", []))).lower()
            if search_query not in content:
                continue
        display_segments.append(s)

    if not display_segments:
        st.warning("No matching segments found.")
        return

    # 6. NAVIGATION
    if "seg_index" not in st.session_state:
        st.session_state.seg_index = 0
    st.session_state.seg_index = min(st.session_state.seg_index, len(display_segments) - 1)

    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        if st.button("⬅ Previous") and st.session_state.seg_index > 0:
            st.session_state.seg_index -= 1
    with c3:
        if st.button("Next ➡") and st.session_state.seg_index < len(display_segments) - 1:
            st.session_state.seg_index += 1

    labels = [f"S{seg['segment_id']}: {seg.get('title','Segment')[:70]}" for seg in display_segments]
    st.session_state.seg_index = st.selectbox(
        "Select Segment",
        range(len(labels)),
        index=st.session_state.seg_index,
        format_func=lambda i: labels[i],
    )

    seg = display_segments[st.session_state.seg_index]

    # 7. DETAILS
    st.subheader(f"{seg.get('title', 'Segment')}")
    col1, col2, col3 = st.columns(3)
    col1.metric("Start", format_time(seg.get("start_time", 0.0)))
    col2.metric("End", format_time(seg.get("end_time", 0.0)))
    col3.metric("Duration", f"{(float(seg.get('end_time', 0.0)) - float(seg.get('start_time', 0.0))):.1f}s")

    st.markdown(f"**Sentiment:** {seg.get('sentiment_label', 'Neutral')} ({seg.get('sentiment_score', 0.0):.2f})")
    
    st.markdown("### Keywords")
    keywords = clean_keywords_for_display(seg.get("keywords", []))
    if keywords:
        st.write(", ".join(keywords))
        render_keyword_cloud(keywords)

    st.markdown("### Summary")
    summary_text = seg.get("summary", "")
    if summary_has_repetition(summary_text):
        st.warning("⚠️ Loop detected. Showing text excerpt.")
        st.write(seg.get("text", "")[:300] + "...")
    else:
        st.write(summary_text)

    # --- UPDATED TRANSCRIPT SECTION WITH VISUAL HIGHLIGHTING ---
    st.markdown("### Transcript")
    
    # Get the text
    transcript_text = seg.get("text", "")
    
    # Apply Highlighting if search is active
    if search_query:
        # Use Regex to replace "word" with "<mark>word</mark>" (Yellow Highlight)
        # re.IGNORECASE makes it find "Quantum" even if you typed "quantum"
        # We escape search_query to safely handle special chars
        # We use a lambda to preserve the original casing of the matched text
        pattern = re.compile(re.escape(search_query), re.IGNORECASE)
        transcript_text = pattern.sub(lambda m: f"<mark>{m.group(0)}</mark>", transcript_text)

    # Render as Scrollable Markdown (looks like a text box but supports colors)
    st.markdown(
        f"""
        <div style="height: 350px; overflow-y: scroll; border: 1px solid #ccc; padding: 10px; border-radius: 5px; background-color: #f0f2f6;">
            {transcript_text}
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()