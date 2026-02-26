# pages/03_browse.py

import streamlit as st
import pandas as pd
import json
import re
from pathlib import Path
from io import BytesIO

# Visualization + NLP
import plotly.graph_objects as go
from wordcloud import WordCloud
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from utils import *

# ------------------------------------------------------------
# PROJECT PATH CONFIGURATION
# ------------------------------------------------------------

BASE_DIR = Path(r"D:\Audio app")
LOGO_PATH = BASE_DIR / "data" / "images" / "logo.png"

# Apply global sidebar and theme
dark_mode = render_global_sidebar(LOGO_PATH)
apply_theme(dark_mode)

# Page configuration
st.set_page_config(
    page_title="Castly",
    page_icon=LOGO_PATH,
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Browse Segments")

# ============================================================
# LOCAL DATA PATHS
# ============================================================

SEGMENT_DIR = Path(r"D:\Audio app\data\segmented_outputs")
AUDIO_DIR   = Path(r"D:\Audio app\data\audio_raw")
IMAGE_DIR   = Path(r"D:\Audio app\data\episode_images")
CSV_PATH    = Path(r"D:\Audio app\data\transcripts_raw_truncated\episode_info_clean_200.csv")

# Initialize VADER sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# ============================================================
# GLOBAL CSS STYLING
# ============================================================

st.markdown("""
<style>
.badge {
    padding: 0.35rem 0.9rem;
    border-radius: 999px;
    font-weight: 600;
    color: white;
}
.badge.positive { background: #10b981; }
.badge.negative { background: #ef4444; }
.badge.neutral  { background: #f59e0b; }

.kw {
    background: rgba(253,224,71,0.6);
    padding: 3px 10px;
    border-radius: 999px;
}

.keyword-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.card {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    margin-bottom: 1.5rem;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# LOAD EPISODE TITLES (CACHED)
# ============================================================

@st.cache_data
def load_episode_titles():
    """
    Loads episode_number → title mapping.
    Cached to reduce repeated file reads.
    """
    try:
        df_titles = pd.read_csv(CSV_PATH)
        df_titles["episode_number"] = df_titles["episode_number"].astype(str)
        return dict(zip(df_titles["episode_number"], df_titles["title"]))
    except:
        return {}

episode_titles = load_episode_titles()

def get_episode_title(ep):
    """
    Returns episode title by episode number.
    """
    return episode_titles.get(str(ep), f"Episode {ep}")

# ============================================================
# EPISODE IMAGE HELPER
# ============================================================

def get_episode_image_path(ep):
    """
    Searches for available episode cover image
    across common image extensions.
    """
    for ext in [".jpg", ".jpeg", ".png", ".JPG", ".PNG"]:
        img_path = IMAGE_DIR / f"{ep}{ext}"
        if img_path.exists():
            return img_path
    return None

# ============================================================
# MODE TOGGLE (Library vs Uploaded)
# ============================================================

use_library = st.checkbox(
    "Browse from This American Life library"
)

df = None

# ============================================================
# LIBRARY MODE
# ============================================================

if use_library:

    @st.cache_data
    def load_library_data():
        """
        Loads all segmented episode JSON files.
        Computes sentiment dynamically and builds
        a unified DataFrame for browsing.
        """
        rows = []

        if not SEGMENT_DIR.exists():
            return pd.DataFrame()

        for f in SEGMENT_DIR.glob("*.json"):
            try:
                data = json.load(open(f, encoding="utf-8"))

                # Extract episode number from episode_id
                ep_match = re.search(r"\d+", data.get("episode_id", ""))
                ep_num = int(ep_match.group()) if ep_match else 0

                for seg in data.get("segments", []):
                    text = seg.get("text_preview", "")

                    # Sentiment computation
                    score = analyzer.polarity_scores(text)["compound"]
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

            except Exception:
                pass

        return pd.DataFrame(rows)

    df = load_library_data()

    if df.empty:
        st.error("No library data found.")
        st.stop()

    episode_list = sorted(df["episode"].unique())

    ep = st.selectbox(
        "Choose an episode",
        episode_list,
        format_func=lambda x: f"Episode {x} - {get_episode_title(x)}"
    )

    df_ep = df[df["episode"] == ep]

# ============================================================
# UPLOADED AUDIO MODE
# ============================================================

else:
    if not st.session_state.get("processed", False):
        st.warning("Process an audio file first on Upload page.")
        st.stop()

    df_ep = st.session_state.df

# ============================================================
# TIMELINE VISUALIZATION (Plotly)
# ============================================================

st.markdown("### Timeline")

fig = go.Figure()

# Sentiment → color mapping
SENTIMENT_COLOR = {
    "Positive": "#10b981",
    "Negative": "#ef4444",
    "Neutral": "#f59e0b"
}

# Create horizontal stacked bars representing timeline segments
for _, r in df_ep.iterrows():

    duration_min = (r["end_sec"] - r["start_sec"]) / 60

    fig.add_trace(go.Bar(
        x=[duration_min],
        y=["Timeline"],
        base=[r["start_sec"] / 60],
        orientation="h",
        marker_color=SENTIMENT_COLOR.get(r["sentiment"], "#94a3b8"),
        hovertemplate=f"""
        <b>Segment {r.get('segment', r.get('segment_id', '?'))}</b><br>
        Sentiment: {r['sentiment']}<br>
        Start: {r['start_sec']/60:.1f} min
        <extra></extra>
        """,
        showlegend=False
    ))

fig.update_layout(
    height=160,
    xaxis_title="Time (minutes)",
    yaxis_visible=False,
    margin=dict(l=20, r=20, t=10, b=40),
)

st.plotly_chart(fig, width='stretch')

# ============================================================
# SEGMENT SELECTOR
# ============================================================

segment_col = "segment" if use_library else "segment_id"

seg = st.selectbox(
    "Select Segment",
    df_ep[segment_col].tolist(),
    format_func=lambda x: f"Segment {x}"
)

r = df_ep[df_ep[segment_col] == seg].iloc[0]

col1, col2 = st.columns([3,1])

# ============================================================
# LEFT COLUMN (Summary + Keyword + Transcript)
# ============================================================

with col1:

    if use_library:
        st.markdown(f"""
        <h2>
            Episode {r['episode']} - {get_episode_title(r['episode'])}
        </h2>
        """, unsafe_allow_html=True)

    # Summary card
    st.markdown(f"""
    <div class="card">
        <h4>Summary</h4>
        <p>{r['summary']}</p>
        <span class="badge {r['sentiment'].lower()}">
            {r['sentiment']} ({r['sentiment_score']:.2f})
        </span>
    </div>
    """, unsafe_allow_html=True)

    # Keyword chips
    if r["keywords"]:
        st.markdown(f"""
        <div class="card">
            <h4>Keywords</h4>
            <div class="keyword-row">
                {''.join(f"<span class='kw'>{k}</span>" for k in r['keywords'])}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Transcript preview with highlighted keywords
    st.markdown(f"""
    <div class="card">
        <h4>Transcript Preview</h4>
        {highlight_keywords(r['text'], r['keywords'])}
        <p>{r['start_sec']:.1f}s – {r['end_sec']:.1f}s</p>
    </div>
    """, unsafe_allow_html=True)

    # Romaized version for non-English text
    if r.get("language") and r["language"] != "en":
        st.markdown("### Romanized (English Script)")
        st.write(r["full_text_romanized"])


# ============================================================
# RIGHT COLUMN (WordCloud + Audio + CoverImage)
# ============================================================

with col2:

    # Word Cloud
    if r["keywords"]:
        wc = WordCloud(width=300, height=200, background_color="white")
        wc.generate(" ".join(r["keywords"]))
        buf = BytesIO()
        wc.to_image().save(buf, format="PNG")
        buf.seek(0)
        st.image(buf, width='stretch')

    # Audio playback
    if use_library:
        audio_path = AUDIO_DIR / f"{r['episode']}.mp3"
        if audio_path.exists():
            st.audio(str(audio_path),
                     start_time=int(r["start_sec"]))
    else:
        if "uploaded_audio_bytes" in st.session_state:
            clip_io = extract_segment_clip(
                BytesIO(st.session_state.uploaded_audio_bytes),
                start_sec=int(r["start_sec"]),
                duration_sec=90
            )
            if clip_io.getvalue():
                st.audio(clip_io, format="audio/mp3")

    # Episode cover image
    if use_library:
        img_path = get_episode_image_path(r["episode"])
        if img_path:
            st.image(
                str(img_path),
                width='stretch',
                caption=f"Episode {r['episode']} - {get_episode_title(r['episode'])}"
            )

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")
st.caption("Castly – Turn hours of audio into minutes of insight • © Manasi Narkhede")
