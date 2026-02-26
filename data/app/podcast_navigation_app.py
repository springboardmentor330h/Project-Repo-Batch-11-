
# ─────────────────────────────────────────────────────────────
# IMPORTS
# ─────────────────────────────────────────────────────────────
import streamlit as st    # Streamlit UI framework
import json
import os
import re
from io import BytesIO    # In-memory image buffer

import pandas as pd
import plotly.graph_objects as go   # Interactive timeline visualization

from wordcloud import WordCloud   # Keyword visualization
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer  # Sentiment scoring

# ─────────────────────────────────────────────────────────────
# LOAD EPISODE TITLES FROM CSV
# ─────────────────────────────────────────────────────────────
try:
    episodes_csv_path = "/content/drive/MyDrive/podcast-project/data/transcripts_raw_truncated/episode_info_clean_200.csv"
    episode_df = pd.read_csv(episodes_csv_path)

    # Convert episode number to string
    episode_df["episode_number"] = episode_df["episode_number"].astype(str)

    # Create dictionary: episode_number → title
    episode_titles = dict(zip(episode_df["episode_number"], episode_df["title"]))

    # st.success("Episode titles loaded successfully from CSV!")

except FileNotFoundError:
    st.warning("Episode titles CSV not found. Using fallback 'Episode X'.")
    episode_titles = {} # Empty fallback dictionary
except KeyError as e:
    st.error(f"CSV loading failed: missing column {e}")
    episode_titles = {} # Schema error
except Exception as e:
    st.error(f"Error loading episode titles: {e}")
    episode_titles = {}

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG & STYLES
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Podcast Topic Navigator",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Default page state
if "page" not in st.session_state:
    st.session_state.page = "home"

# Custom CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    * {
        font-family: 'Inter', sans-serif !important;
    }

    .stApp {
        background-color: #f9fafb;
    }

    .main .block-container {
        padding-top: 2.5rem !important;
        padding-bottom: 4rem !important;
        max-width: 1400px !important;
    }

    /* Home-only background */
    .home-bg .stApp {
        background:
            linear-gradient(rgba(0,0,0,0.28), rgba(0,0,0,0.28)),
            url("https://www.thisamericanlife.org/sites/default/files/styles/about/public/about/about-wren_mcdonald-credit.jpg?itok=5nQqSXOZ");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }

    /* Default background for other pages */
    .stApp {
        background-color: #f9fafb;
    }

    /* Hero - original purple gradient */
    .hero {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        padding: 4.5rem 2rem;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin-bottom: 3.5rem;
        box-shadow: 0 12px 48px rgba(79, 70, 229, 0.18);
        position: relative;
        z-index: 1;
    }
    .hero h1 {
        font-size: 3.2rem;
        font-weight: 700;
        margin: 0 0 1.2rem;
        letter-spacing: -0.03em;
    }
    .hero p {
        font-size: 1.35rem;
        opacity: 0.94;
        max-width: 760px;
        margin: 0 auto;
        line-height: 1.5;
    }

    /* Cards */
    .card {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 6px 20px rgba(0,0,0,0.07);
        border: 1px solid #f0f0f5;
        transition: all 0.25s ease;
        margin-bottom: 2rem;
        position: relative;
        z-index: 1;
    }
    .card:hover {
        transform: translateY(-4px);
        box-shadow: 0 14px 36px rgba(0,0,0,0.12);
    }

    /* Titles */
    .section-title {
        font-size: 1.85rem;
        font-weight: 700;
        color: #111827;
        margin: 3rem 0 1.5rem 0;
        position: relative;
    }
    .section-title:after {
        content: '';
        position: absolute;
        bottom: -10px;
        left: 0;
        width: 70px;
        height: 4px;
        background: linear-gradient(90deg, #6366f1, #a855f7);
        border-radius: 2px;
    }

    /* Badge & Keywords */
    .badge {
        padding: 0.5rem 1.1rem;
        border-radius: 999px;
        font-size: 0.95rem;
        font-weight: 600;
        color: white;
        display: inline-block;
    }
    .badge.positive  { background: #10b981; }
    .badge.negative  { background: #ef4444; }
    .badge.neutral   { background: #f59e0b; }

    .keyword-row {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin: 1.2rem 0;
    }
    .kw {
        background: rgba(253, 224, 71, 0.4);
        padding: 5px 14px;
        border-radius: 999px;
        font-size: 0.95rem;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: white !important;
        border-right: 1px solid #e5e7eb;
    }
    .sidebar-title {
        font-size: 1.6rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #e5e7eb;
    }

    /* Buttons in sidebar */
    .stButton > button {
        border-radius: 10px !important;
        padding: 0.9rem 1.2rem !important;
        font-size: 1.05rem !important;
        font-weight: 500 !important;
        margin-bottom: 0.6rem !important;
        transition: all 0.2s;
        text-align: left !important;
    }
    .stButton > button[kind="primary"] {
        background: #6366f1 !important;
        color: white !important;
    }
    .stButton > button:hover {
        background: #f3f4f6 !important;
    }

    .footer {
        text-align: center;
        color: #6b7280;
        font-size: 0.95rem;
        margin: 6rem 0 3rem;
        padding-top: 2.5rem;
        border-top: 1px solid #e5e7eb;
    }

    /* Fix arrow / keyboard placeholder issue */
    .kbd, [data-testid*="kbd"], .keyboard-hint, .stMarkdownContainer > span.kbd {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# PATHS & CONSTANTS
# ─────────────────────────────────────────────────────────────
BASE_PATH = "/content/drive/MyDrive/podcast-project"
SEGMENT_DIR = os.path.join(BASE_PATH, "data/segmented_outputs")
AUDIO_DIR = os.path.join(BASE_PATH, "data/audio_raw")
EST_SEGMENT_DURATION = 60   # Approx segment length

SENTIMENT_COLOR = {
    "Positive": "#10b981",  # Green for positive sentiment
    "Negative": "#ef4444",  # Red for negative sentiment
    "Neutral": "#f59e0b"    # Yellow for neutral sentiment
}

# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────
def polish_summary(s):
    if not s:
        return ""   # Return empty if summary missing

    fillers = r"\b(um|uh|you know|like|so|basically|kind of|right|yeah|just)\b"
    s = re.sub(fillers, "", s, flags=re.I)    # Remove fillers
    s = re.sub(r"\s+", " ", s).strip()        # Normalize spaces
    if not s:
        return ""

    s = s[0].upper() + s[1:] if s else ""       # Capitalize first letter
    sentences = re.split(r'(?<=[.!?])\s+', s)   # Split into sentences
    result = " ".join(sentences[:3])            # Keep first 3 sentences

    if len(sentences) > 3:
        result += "..."                         # Add ellipsis if truncated

    if not result.endswith(('.', '!', '?')):
        result += "."
    return result

def highlight_keywords(text, keywords):
    if not text or not keywords:
        return text or ""                       # Return text if nothing to highlight

    for k in keywords:
        text = re.sub(rf"\b({re.escape(k)})\b",       # Match keyword
                      r"<span class='kw'>\1</span>",  # Wrap with highlight span
                      text,
                      flags=re.I)
    return text

def find_audio_file(episode):
    for ext in [".mp3", ".m4a", ".wav"]:
        path = os.path.join(AUDIO_DIR, f"{episode}{ext}")
        if os.path.exists(path):
            return path   # Return first matching file
    return None

def get_episode_title(ep_num):
    ep_str = str(ep_num)  # convert to string
    return episode_titles.get(ep_str, f"Episode {ep_num}")

def get_episode_image_path(ep_num):
    ep_str = str(ep_num)

    image_folder = "/content/drive/MyDrive/podcast-project/data/episode_images"

    possible_extensions = [".jpg", ".jpeg", ".png", ".JPG", ".PNG"]

    for ext in possible_extensions:
        path = os.path.join(image_folder, f"{ep_str}{ext}")
        if os.path.exists(path):
            print(f"Image found: {path}")
            return path     # Return image if found
        else:
            print(f"Not found: {path}")

    print(f"No image found for episode {ep_str}")
    return None

# ─────────────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    if not os.path.exists(SEGMENT_DIR):
        st.error(f"Segment directory not found: {SEGMENT_DIR}")
        return pd.DataFrame()

    analyzer = SentimentIntensityAnalyzer()   # Initialize sentiment model
    rows = []                                 # Store processed segments

    for f in os.listdir(SEGMENT_DIR):
        if f.endswith("_segment.json"):
            try:
                ep = json.load(open(os.path.join(SEGMENT_DIR, f), encoding='utf-8'))
                ep_num_match = re.search(r"\d+", ep.get("episode_id", ""))  # Extract episode number
                ep_num = int(ep_num_match.group()) if ep_num_match else 0

                for seg in ep.get("segments", []):
                    text = seg.get("text_preview", "")                    # Segment transcript
                    score = analyzer.polarity_scores(text)["compound"]    # Sentiment score
                    sentiment = (
                        "Positive" if score >= 0.05 else
                        "Negative" if score <= -0.05 else
                        "Neutral"
                    )
                    start = seg.get("start_time_sec", 0.0)  # Segment start time

                    rows.append({
                        "episode": ep_num,
                        "segment": int(seg.get("segment_id", 0)),
                        "summary": seg.get("summary", ""),
                        "polished_summary": polish_summary(seg.get("summary", "")),
                        "keywords": seg.get("keywords", []),
                        "text": text,
                        "start": start,
                        "end": start + EST_SEGMENT_DURATION,
                        "sentences": seg.get("num_sentences", 0),
                        "sentiment": sentiment,
                        "sentiment_score": round(score, 2)
                    })
            except Exception as e:
                st.warning(f"Error loading {f}: {str(e)}")    # File-level error handling

    if not rows:
        return pd.DataFrame()

    return pd.DataFrame(rows).sort_values(["episode", "segment"])


# ─────────────────────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────────────────────
with st.spinner("Loading podcast segments..."):
    df = load_data()                         # Load cached data

if df.empty:
    st.error("No valid segment data found. Please check your data folder.")  # Stop if empty
    st.stop()

# ─────────────────────────────────────────────────────────────
# SIDEBAR – buttons
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-title">Podcast Topic Navigator</div>', unsafe_allow_html=True)

    pages = [
        ("home", "Dashboard"),
        ("search", "Search Content"),
        ("browse", "Browse Episodes"),
        ("help", "Help & About")
    ]

    for key, label in pages:
        is_active = st.session_state.page == key          # Check active page
        if st.button(
            label=label,
            key=f"nav_{key}",
            use_container_width=True,
            type="primary" if is_active else "secondary", # Highlight active page
            disabled=is_active                            # Disable current page button
        ):
            st.session_state.page = key                   # Update page state
            st.rerun()                                    # Rerun app

    st.divider()
    st.caption("Dataset Overview")
    st.metric("Episodes", df["episode"].nunique())
    st.metric("Segments", len(df))
    st.metric("Unique Keywords", len(set(k for kws in df["keywords"] for k in kws)))  # Count unique keywords

page = st.session_state.page    # Current page selector

# ─────────────────────────────────────────────────────────────
# HOME PAGE
# ─────────────────────────────────────────────────────────────
if page == "home":

    st.markdown(
        """
        <script>
        document.body.classList.add("home-bg");
        </script>
        """,
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="hero">
        <h1>Podcast Topic Navigator</h1>
        <p>Transform long-form podcasts into searchable, actionable insights</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Core Features</div>', unsafe_allow_html=True)

    features = [
        ("Smart Topic Segmentation", "Episodes divided into meaningful ~60-second topic segments."),
        ("Keyword & Summary Extraction", "Key topics and concise summaries for every segment."),
        ("Sentiment Analysis", "Positive / negative / neutral tone detection per segment."),
        ("Direct Audio Navigation", "Jump straight to any segment in the audio."),
        ("Powerful Search", "Find topics, names, phrases across all episodes."),
        ("Episode Timeline", "Visual overview with color-coded sentiment bars.")
    ]

    cols = st.columns(3)
    for i, (title, desc) in enumerate(features):
        with cols[i % 3]:     # Distribute cards evenly
            st.markdown(f"""
            <div class="card">
                <h3>{title}</h3>
                <p>{desc}</p>
            </div>
            """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# SEARCH PAGE
# ─────────────────────────────────────────────────────────────
elif page == "search":
    st.markdown('<div class="section-title">Search Topics</div>', unsafe_allow_html=True)

    q = st.text_input(
        label="Search podcast content",
        placeholder="Search summaries, keywords or transcript...",
        label_visibility="collapsed"
    )

    if q.strip():               # Proceed if query is not empty
        q_lower = q.lower()     # Normalize query

        mask = (
            df["polished_summary"].str.lower().str.contains(q_lower, na=False) |
            df["text"].str.lower().str.contains(q_lower, na=False) |
            df["keywords"].apply(lambda kws: any(q_lower in k.lower() for k in kws) if kws else False)
        )
        res = df[mask]          # Filter matching segments

        st.subheader(f"Found {len(res)} matching segments")

        for _, r in res.iterrows():
            with st.expander(f"Episode {r['episode']} - {get_episode_title(r['episode'])} • Segment {r['segment']}"):
              col1, col2 = st.columns([3, 1])
              with col1:

                  # Title of Episodes
                  st.markdown(f"""
                  <h3 style="margin:0 0 1.2rem 0; color:#1e293b; font-weight:700;">
                      Episode {r['episode']} - {get_episode_title(r['episode'])}
                  </h3>
                  """, unsafe_allow_html=True)

                  st.markdown(f"""
                  <div class="card">
                      <div class="section-title">Summary</div>
                      <p>{r['polished_summary']}</p>
                      <span class="badge {r['sentiment'].lower()}">{r['sentiment']} ({r['sentiment_score']:.2f})</span>
                  </div>
                  """, unsafe_allow_html=True)

                  st.markdown(f"""
                  <div class="card">
                      <div class="section-title">Keywords</div>
                      <div class="keyword-row">
                          {''.join(f"<span class='kw'>{k}</span>" for k in r['keywords'])}
                      </div>
                  </div>
                  """, unsafe_allow_html=True)

                  st.markdown(f"""
                  <div class="card">
                      <div class="section-title">Transcript Preview</div>
                      {highlight_keywords(r['text'], r['keywords'])}
                      <p class="meta">Sentences: {r['sentences']} • {r['start']:.1f}s – {r['end']:.1f}s</p>
                  </div>
                  """, unsafe_allow_html=True)

              with col2:
                  # Keyword Cloud
                  if r["keywords"]:
                      wc = WordCloud(width=300, height=200, background_color="white")   # WordCloud config
                      wc.generate(" ".join(r["keywords"]))                              # Generate cloud
                      buf = BytesIO()                                                   # Buffer image
                      wc.to_image().save(buf, format="PNG")
                      buf.seek(0)                                                       # Reset pointer to start
                      st.image(buf, width="stretch")
                  else:
                      st.info("No keywords")

                  # Add Audio of Episode
                  audio_path = find_audio_file(r["episode"])                            # Locate audio
                  if audio_path:
                      st.audio(audio_path, start_time=int(r["start"]))                  # Play from timestamp
                  else:
                      st.info("Audio not available")

                  # Load cover image of Episodes
                  image_path = get_episode_image_path(r["episode"])
                  if image_path:
                      st.image(image_path, width="stretch", caption=get_episode_title(r["episode"]))
                  else:
                      st.caption(f"No cover image for {get_episode_title(r['episode'])}")


# ─────────────────────────────────────────────────────────────
# BROWSE PAGE
# ─────────────────────────────────────────────────────────────
elif page == "browse":
    st.markdown('<div class="section-title">Browse Episodes</div>', unsafe_allow_html=True)

    episode_list = sorted(df["episode"].unique())

    # Selectbox shows "Episode X - Title"
    ep = st.selectbox(
        "Choose an episode",
        episode_list,
        format_func=lambda x: f"Episode {x} - {get_episode_title(x)}"
    )

    df_ep = df[df["episode"] == ep]   # Filter data for selected episode

    # Timeline header
    st.markdown(f"""
    <div class="card">
        <div class="section-title">Timeline – Episode {ep} - {get_episode_title(ep)}</div>
    </div>
    """, unsafe_allow_html=True)

    fig = go.Figure()   # Initialize Plotly figure
    for _, r in df_ep.iterrows():
        fig.add_trace(go.Bar(
            x=[EST_SEGMENT_DURATION / 60],          # Segment duration (minutes)
            y=[" "],                                # Single horizontal bar
            base=[r["start"] / 60],                 # Start time offset
            orientation="h",                        # Horizontal orientation
            marker=dict(color=SENTIMENT_COLOR[r["sentiment"]]),
            hovertemplate=f"<b>Segment {r['segment']}</b><br>Sentiment: {r['sentiment']}<br>Start: {r['start']/60:.1f} min<extra></extra>",
            showlegend=False
        ))

    fig.update_layout(
        height=140,
        xaxis_title="Time (minutes)",
        yaxis_visible=False,
        margin=dict(l=20, r=20, t=10, b=40),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig, width="stretch")    # Render timeline

    seg = st.selectbox("Select Segment", df_ep["segment"].tolist(), format_func=lambda x: f"Segment {x}")

    r = df_ep[df_ep["segment"] == seg].iloc[0]        # Get selected segment row

    col1, col2 = st.columns([3, 1])

    with col1:
        # Title of Episodes
        st.markdown(f"""
        <h3 style="margin:0 0 1.2rem 0; color:#1e293b; font-weight:700;">
            Episode {r['episode']} - {get_episode_title(r['episode'])}
        </h3>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="card">
            <div class="section-title">Summary</div>
            <p>{r['polished_summary']}</p>
            <span class="badge {r['sentiment'].lower()}">{r['sentiment']} ({r['sentiment_score']:.2f})</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="card">
            <div class="section-title">Keywords</div>
            <div class="keyword-row">
                {''.join(f"<span class='kw'>{k}</span>" for k in r['keywords'])}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="card">
            <div class="section-title">Transcript Preview</div>
            {highlight_keywords(r['text'], r['keywords'])}
            <p class="meta">Sentences: {r['sentences']} • {r['start']:.1f}s – {r['end']:.1f}s</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # Keyword Cloud
        if r["keywords"]:
            wc = WordCloud(width=300, height=200, background_color="white")
            wc.generate(" ".join(r["keywords"]))
            buf = BytesIO()
            wc.to_image().save(buf, format="PNG")
            buf.seek(0)
            st.image(buf, width="stretch")
        else:
            st.info("No keywords")

        # Add Audio
        audio_path = find_audio_file(r["episode"])
        if audio_path:
            st.audio(audio_path, start_time=int(r["start"]))
        else:
            st.info("Audio file not found")

        # Load cover image of Episodes
        image_path = get_episode_image_path(r["episode"])
        if image_path:
            st.image(image_path, width="stretch", caption=get_episode_title(r["episode"]))
        else:
            st.caption(f"No cover image for {get_episode_title(r['episode'])}")

# ─────────────────────────────────────────────────────────────
# HELP PAGE
# ─────────────────────────────────────────────────────────────
elif page == "help":
    st.markdown('<div class="section-title">Help & Getting Started</div>', unsafe_allow_html=True)

    st.markdown("### Quick Start Guide")
    st.markdown("""
    - **Dashboard** — overview and features
    - **Search Content** — find topics, names, phrases across all episodes
    - **Browse Episodes** — explore one episode segment-by-segment with timeline
    - Audio player starts at the selected segment
    """)

    st.markdown("### Tips")
    st.markdown("""
    - Green = positive, red = negative, yellow = neutral sentiment
    - Keywords appear highlighted in yellow in transcript preview
    - Timeline bars show sentiment distribution
    """)

    st.markdown("### Troubleshooting")
    st.markdown("""
    - Audio not playing? Check files in `data/audio_raw`
    - No data? Verify JSON files in `data/segmented_outputs`
    """)

# ─────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="footer">
    Podcast Topic Navigator • © Manasi Narkhede
</div>
""", unsafe_allow_html=True)
