
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


# Dark mode toggle + system preference detection
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# Sidebar toggle for dark mode
with st.sidebar:
    st.markdown("### Display Settings")
    st.session_state.dark_mode = st.checkbox(
        "Dark Mode",
        value=st.session_state.dark_mode,
        help="Toggle dark mode for better visibility"
    )

# Apply theme
theme = "dark" if st.session_state.dark_mode else "light"

# Custom CSS
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    * {{
        font-family: 'Inter', sans-serif !important;
    }}

    /* Root app container */
    [data-testid="stAppViewContainer"] {{
        background-color: {'#0f172a' if theme == 'dark' else '#f9fafb'};
        color: {'#e2e8f0' if theme == 'dark' else '#1e293b'};
    }}

    .main .block-container {{
        padding-top: 2.5rem !important;
        padding-bottom: 4rem !important;
        max-width: 1400px !important;
    }}

    /* Hero */
    .hero {{
        background: linear-gradient(135deg, {'#4f46e5' if theme == 'light' else '#6366f1'}, {'#7c3aed' if theme == 'light' else '#ec4899'});
        padding: 4.5rem 2rem;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin-bottom: 3.5rem;
        box-shadow: 0 12px 48px rgba(79, 70, 229, 0.18);
    }}
    .hero h1 {{
        font-size: 3.2rem;
        font-weight: 700;
        margin: 0 0 1.2rem;
        letter-spacing: -0.03em;
    }}
    .hero p {{
        font-size: 1.35rem;
        opacity: 0.94;
        max-width: 760px;
        margin: 0 auto;
        line-height: 1.5;
    }}

    /* Cards – semi-transparent in both modes */
    .card {{
        background: {'rgba(255, 255, 255, 0.88)' if theme == 'light' else 'rgba(30, 41, 59, 0.88)'} !important;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid {'rgba(255, 255, 255, 0.4)' if theme == 'light' else 'rgba(71, 85, 105, 0.5)'};
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.15);
        margin-bottom: 2rem;
        color: {'#1e293b' if theme == 'light' else '#e2e8f0'};
    }}

    .card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 14px 36px rgba(0,0,0,0.25);
    }}

    /* Titles */
    .section-title {{
        font-size: 1.85rem;
        font-weight: 700;
        color: {'#111827' if theme == 'light' else '#e2e8f0'};
        margin: 3rem 0 1.5rem 0;
        position: relative;
    }}
    .section-title:after {{
        content: '';
        position: absolute;
        bottom: -10px;
        left: 0;
        width: 70px;
        height: 4px;
        background: linear-gradient(90deg, #6366f1, #a855f7);
        border-radius: 2px;
    }}

    /* Badge & Keywords */
    .badge {{
        padding: 0.5rem 1.1rem;
        border-radius: 999px;
        font-size: 0.95rem;
        font-weight: 600;
        color: white;
        display: inline-block;
    }}
    .badge.positive  {{ background: #10b981; }}
    .badge.negative  {{ background: #ef4444; }}
    .badge.neutral   {{ background: #f59e0b; }}

    .keyword-row {{
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin: 1.2rem 0;
    }}
    .kw {{
        background: {'rgba(253, 224, 71, 0.4)' if theme == 'light' else 'rgba(253, 224, 71, 0.25)'};
        padding: 5px 14px;
        border-radius: 999px;
        font-size: 0.95rem;
        color: {'#1e293b' if theme == 'light' else '#e2e8f0'};
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: {'white' if theme == 'light' else '#1e293b'} !important;
        border-right: 1px solid {'#e5e7eb' if theme == 'light' else '#334155'};
    }}
    .sidebar-title {{
        font-size: 1.6rem;
        font-weight: 700;
        color: {'#111827' if theme == 'light' else '#e2e8f0'};
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid {'#e5e7eb' if theme == 'light' else '#334155'};
    }}

    /* Buttons in sidebar */
    .stButton > button {{
        border-radius: 10px !important;
        padding: 0.9rem 1.2rem !important;
        font-size: 1.05rem !important;
        font-weight: 500 !important;
        margin-bottom: 0.6rem !important;
        transition: all 0.2s;
        text-align: left !important;
        background: {'#6366f1' if theme == 'light' else '#6366f1'} !important;
        color: white !important;
    }}
    .stButton > button:hover {{
        background: {'#f3f4f6' if theme == 'light' else '#334155'} !important;
    }}

    .footer {{
        text-align: center;
        color: {'#6b7280' if theme == 'light' else '#94a3b8'};
        font-size: 0.95rem;
        margin: 6rem 0 3rem;
        padding-top: 2.5rem;
        border-top: 1px solid {'#e5e7eb' if theme == 'light' else '#334155'};
    }}

    /* Hide broken keyboard hints */
    .kbd, [data-testid*="kbd"], .keyboard-hint, .keyboard_* {{
        display: none !important;
    }}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# PATHS & CONSTANTS
# ─────────────────────────────────────────────────────────────
BASE_PATH = "/content/drive/MyDrive/podcast-project"
AUDIO_DIR = os.path.join(BASE_PATH, "data/test/audio_test")  # or audio_raw_week6 if you prefer
SEGMENT_DIR = os.path.join(BASE_PATH, "data/test/segments_test")
EST_SEGMENT_DURATION = 60   # Approx segment length

FEEDBACK_FORM_LINK = "https://docs.google.com/forms/d/e/1FAIpQLSeBEXeo9TC68qFct8JH0WwrxD7X2-W8zEc3iK7r9GlzOAspYQ/viewform?usp=sharing&ouid=106324761697289838053"

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
    st.markdown('<div class="sidebar-title">Test Podcast Topic Navigator</div>', unsafe_allow_html=True)

    pages = [
        ("home", "Dashboard"),
        ("search", "Search Content"),
        ("browse", "Test Episodes"),
        ("feedback", "Feedback")
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
    st.markdown("""
    <div class="hero">
        <h1>Test Podcast Topic Navigator</h1>
        <p>Use the 'Testing' page to browse and evaluate individual episodes.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Objectives</div>', unsafe_allow_html=True)

    objectives = [
        ("System Coverage Testing", "Test system on 5 diverse new podcasts."),
        ("Pipeline Quality Assessment", "Identify weaknesses in transcription, segmentation, summaries, keywords, sentiment."),
        ("User Interface & Navigation Review", "Evaluate UI behavior, audio navigation, usability."),
        ("User Feedback Collection", "Collect structured user feedback."),
        ("Logging & Incremental Improvements", "Find topics, names, phrases across all episodes."),
        ("Episode Timeline", "Log observations and propose small practical fixes.")
    ]

    cols = st.columns(3)
    for i, (title, desc) in enumerate(objectives):
        with cols[i % 3]:     # Distribute cards evenly
            st.markdown(f"""
            <div class="card">
                <h3>{title}</h3>
                <p>{desc}</p>
            </div>
            """, unsafe_allow_html=True)

    # At the very end of the home page content
    st.markdown('</div>', unsafe_allow_html=True)  # close home-container

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
            with st.expander(f"Episode {r['episode']} • Segment {r['segment']}"):
              col1, col2 = st.columns([3, 1])
              with col1:

                  # Title of Episodes
                  st.markdown(f"""
                  <h3 style="margin:0 0 1.2rem 0; color:#1e293b; font-weight:700;">
                      Episode {r['episode']}
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

# ─────────────────────────────────────────────────────────────
# BROWSE PAGE
# ─────────────────────────────────────────────────────────────
elif page == "browse":
    st.markdown('<div class="section-title">Test Episodes</div>', unsafe_allow_html=True)

    episode_list = sorted(df["episode"].unique())

    # Selectbox shows "Episode X - Title"
    ep = st.selectbox(
        "Choose an episode",
        episode_list,
        format_func=lambda x: f"Episode {x} "
    )

    df_ep = df[df["episode"] == ep]   # Filter data for selected episode

    # Timeline header
    st.markdown(f"""
    <div class="card">
        <div class="section-title">Timeline – Episode {ep} </div>
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
            Episode {r['episode']}
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

# ─────────────────────────────────────────────────────────────
# FEEDBACK FORM PAGE
# ─────────────────────────────────────────────────────────────
elif page == "feedback":
    st.markdown('<div class="section-title">Provide Your Feedback</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="feedback-box">
        <h3>Help us improve the system!</h3>
        <p>Your honest feedback is very valuable.</p>
        <p>Please take 2–3 minutes to fill out this short Google Form:</p>
        <p style="font-size:1.3rem; margin:1.5rem 0;">
            <a href="{FEEDBACK_FORM_LINK}" target="_blank">
                <strong>→ Open Feedback Form (Google Form)</strong>
            </a>
        </p>
        <p>Questions include:</p>
        <ul>
            <li>Overall rating (1–5)</li>
            <li>Ease of use & navigation</li>
            <li>Helpfulness of summaries & keywords</li>
            <li>Audio jumping accuracy</li>
            <li>Any bugs or confusing parts</li>
            <li>Suggestions for improvement</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Optional – Quick Notes Here")
    quick_feedback = st.text_area(
        "Quick thoughts / additional comments (optional)",
        height=120,
        placeholder="Example: The timeline is helpful but could show more details..."
    )

    if st.button("Save Quick Notes"):
        if quick_feedback.strip():
            st.success("Notes saved! You can copy them to your log or form.")
            st.write(quick_feedback)
        else:
            st.info("No notes entered – feel free to use the Google Form.")
# ─────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="footer">
    Test Podcast Topic Navigator • © Manasi Narkhede
</div>
""", unsafe_allow_html=True)
