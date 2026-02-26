# pages/02_search.py

import streamlit as st
import pandas as pd
import json
import re
from pathlib import Path
from io import BytesIO

from wordcloud import WordCloud
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from utils import *

# ============================================================
# PROJECT PATH CONFIGURATION 
# ============================================================
BASE_DIR = Path(r"D:\Audio app")
LOGO_PATH = BASE_DIR / "data" / "images" / "logo.png"

# Render sidebar and apply theme
dark_mode = render_global_sidebar(LOGO_PATH)
apply_theme(dark_mode)

st.set_page_config(
    page_title="Castly",
    page_icon=LOGO_PATH,
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Search Segments")

# ============================================================
# LOCAL DATA PATHS 
# ============================================================

SEGMENT_DIR = Path(r"D:\Audio app\data\segmented_outputs")
AUDIO_DIR   = Path(r"D:\Audio app\data\audio_raw")
IMAGE_DIR   = Path(r"D:\Audio app\data\episode_images")
CSV_PATH    = Path(r"D:\Audio app\data\transcripts_raw_truncated\episode_info_clean_200.csv")

analyzer = SentimentIntensityAnalyzer()

# ============================================================
# GLOBAL CSS STYLING (Badges + Cards + Keywords)
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
# LOAD EPISODE TITLES 
# ============================================================

@st.cache_data
def load_episode_titles():
    """
    Loads episode number → title mapping from CSV file.
    Cached to avoid repeated disk I/O.
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
    Returns episode title given episode number.
    Falls back to generic label if not found.
    """
    return episode_titles.get(str(ep), f"Episode {ep}")


# ============================================================
# EPISODE IMAGE HELPER
# ============================================================

def get_episode_image_path(ep):
    """
    Searches for episode cover image in multiple formats.
    Returns first match if exists.
    """
    for ext in [".jpg", ".jpeg", ".png", ".JPG", ".PNG"]:
        img_path = IMAGE_DIR / f"{ep}{ext}"
        if img_path.exists():
            return img_path
    return None


# ============================================================
# MODE TOGGLE (Library vs Uploaded Audio)
# ============================================================

use_library = st.checkbox(
    "Search across This American Life library",
    help="When checked, searches the pre-processed dataset"
)
df = None

# ============================================================
# LIBRARY MODE (Preprocessed Dataset)
# ============================================================

if use_library:

    @st.cache_data
    def load_library_data():
        """
        Loads all segmented JSON files from library.
        Extracts summary, keywords, transcript preview,
        sentiment score, and timestamps.
        """
        rows = []

        if not SEGMENT_DIR.exists():
            return pd.DataFrame()

        for f in SEGMENT_DIR.glob("*.json"):
            try:
                data = json.load(open(f, encoding="utf-8"))

                # Extract episode number from ID
                ep_match = re.search(r"\d+", data.get("episode_id", ""))
                ep_num = int(ep_match.group()) if ep_match else 0

                for seg in data.get("segments", []):
                    text = seg.get("text_preview", "")

                    # Compute sentiment dynamically
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

            except Exception as e:
                st.warning(f"Error loading {f.name}: {e}")

        return pd.DataFrame(rows)

    df = load_library_data()

    if df.empty:
        st.error("No valid segments found in library.")
        st.stop()


# ============================================================
# UPLOADED AUDIO MODE
# ============================================================

else:
    # Ensure user processed audio first
    if not st.session_state.get("processed", False):
        st.warning("Process an audio file first on Upload page.")
        st.stop()

    df = st.session_state.df

# ============================================================
# SEARCH INPUT
# ============================================================

query = st.text_input(
    "Search podcast content",
    placeholder="Search summaries, keywords or transcript..."
)

if query.strip():

    q = query.lower()

    # Boolean mask across summary, transcript, and keywords
    mask = (
        df["summary"].str.lower().str.contains(q, na=False) |
        df["text"].str.lower().str.contains(q, na=False) |
        df["keywords"].apply(
            lambda kws: any(q in k.lower() for k in kws) if kws else False
        )
    )

    results = df[mask]

    if results.empty:
        st.info("No matching segments found.")
    else:
        st.subheader(f"Found {len(results)} matching segments")
      
        # -------------------- LIBRARY RESULTS RENDERING --------------------
        if use_library:

            for _, r in results.iterrows():

                ep_num = r["episode"]
                ep_title = get_episode_title(ep_num)

                with st.expander(
                    f"Episode {ep_num} - {ep_title} • Segment {r['segment']}"
                ):

                    col1, col2 = st.columns([3,1])

                    with col1:

                        # Summary
                        st.markdown(f"""
                        <div class="card">
                            <h4>Summary</h4>
                            <p>{r['summary']}</p>
                            <span class="badge {r['sentiment'].lower()}">
                                {r['sentiment']} ({r['sentiment_score']:.2f})
                            </span>
                        </div>
                        """, unsafe_allow_html=True)

                        # Keyword 
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

                    with col2:
                        # Word cloud
                        if r["keywords"]:
                            wc = WordCloud(width=300, height=200)
                            wc.generate(" ".join(r["keywords"]))
                            buf = BytesIO()
                            wc.to_image().save(buf, format="PNG")
                            buf.seek(0)
                            st.image(buf, width='stretch')

                        # Audio playback starting at segment timestamp
                        audio_path = AUDIO_DIR / f"{ep_num}.mp3"
                        if audio_path.exists():
                            st.audio(str(audio_path),
                                     start_time=int(r["start_sec"]))

                        # Episode cover image
                        img_path = get_episode_image_path(ep_num)
                        if img_path:
                            st.image(str(img_path),
                                     width='stretch',
                                     caption=f"Episode {ep_num} - {ep_title}")

        # -------------------- UPLOADED RESULTS RENDERING --------------------
        else:

            for _, r in results.iterrows():

                with st.expander(
                    f"Segment {r['segment_id']} – {r['sentiment']}"
                ):

                    col1, col2 = st.columns([3,1])

                    with col1:
                        st.write("### Summary")
                        st.write(r["summary"])

                        st.write("### Keywords")
                        st.write(", ".join(r["keywords"]))

                        st.write("### Transcript")
                        st.markdown(
                            highlight_keywords(r["text"], r["keywords"]),
                            unsafe_allow_html=True
                        )
                        # Show romanized version if non-English
                        if r.get("language") and r["language"] != "en":
                            st.write("### Romanized (English Script)")
                            st.write(r["full_text_romanized"])

                        st.write(f"{r['start_sec']:.1f}s – {r['end_sec']:.1f}s")

                    with col2:

                        # Word cloud
                        if r["keywords"]:
                            wc = WordCloud(width=300, height=200)
                            wc.generate(" ".join(r["keywords"]))
                            buf = BytesIO()
                            wc.to_image().save(buf, format="PNG")
                            buf.seek(0)
                            st.image(buf, width='stretch')

                        # Extract 90-second audio preview clip
                        if "uploaded_audio_bytes" in st.session_state:
                            clip_io = extract_segment_clip(
                                BytesIO(st.session_state.uploaded_audio_bytes),
                                start_sec=int(r["start_sec"]),
                                duration_sec=90
                            )

                            if clip_io.getvalue():
                                st.audio(clip_io, format="audio/mp3")
                            else:
                                st.info("Could not extract clip.")

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")
st.caption("Castly – Turn hours of audio into minutes of insight • © Manasi Narkhede")
