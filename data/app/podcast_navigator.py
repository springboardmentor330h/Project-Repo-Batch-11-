# app/podcast_navigator.py
# Main Entry – Castly Dashboard

import streamlit as st
from pathlib import Path

from utils import render_global_sidebar, apply_theme

# ============================================================
# BASE PATH
# ============================================================

BASE_DIR = Path(r"D:\Audio app")
LOGO_PATH = BASE_DIR / "data" / "images" / "logo.png"

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Castly",
    page_icon=LOGO_PATH,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# HIDE DEFAULT STREAMLIT APP TITLE
# ============================================================

st.markdown("""
<style>
[data-testid="stSidebarNav"] > div:first-child {
    display: none;
}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ============================================================
# GLOBAL SIDEBAR + THEME (Shared Across Pages)
# ============================================================

dark_mode = render_global_sidebar(LOGO_PATH)
apply_theme(dark_mode)

# ============================================================
# HERO SECTION (CENTERED)
# ============================================================

st.markdown("""
<div style="text-align:center; padding: 3rem 0 2rem 0;">
    <h1 style="font-size:3rem; margin-bottom:0.5rem;">
        Welcome to Castly
    </h1>
    <p style="font-size:1.25rem; opacity:0.85;">
        Turn hours of audio into minutes of insight.
    </p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# DESCRIPTION
# ============================================================

st.markdown("""
**Castly** is an AI-powered podcast navigation system that:

- Automatically transcribes audio  
- Segments content into meaningful topics  
- Extracts keywords  
- Generates summaries  
- Detects sentiment  
- Enables direct segment-level navigation  
""")

# ============================================================
# CORE FEATURES (Equal Height Cards)
# ============================================================

st.markdown("### Core Features")

features = [
    ("Smart Topic Segmentation",
     "Divide long podcasts into meaningful ~60-second segments using semantic similarity."),
    ("Keyword & Summary Extraction",
     "Automatically extract top keywords and generate concise segment summaries."),
    ("Sentiment Analysis",
     "Detect emotional tone per segment: Positive, Neutral, or Negative."),
    ("Search Across Episodes",
     "Find topics, names, or phrases instantly across your entire podcast library."),
    ("Interactive Timeline",
     "Visual overview of sentiment distribution and segment positioning."),
    ("Direct Audio Navigation",
     "Jump directly to any segment inside the episode.")
]

cols = st.columns(3)

for i, (title, desc) in enumerate(features):
    with cols[i % 3]:
        st.markdown(f"""
        <div class="card feature-card">
            <h4>{title}</h4>
            <p>{desc}</p>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# QUICK ACTION BUTTONS
# ============================================================

st.markdown("### Get Started")

colA, colB = st.columns(2)

with colA:
    if st.button("Upload New Audio", use_container_width=True):
        st.switch_page("pages/01_upload_audio.py")

with colB:
    if st.button("Explore Library", use_container_width=True):
        st.switch_page("pages/04_library.py")

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")
st.caption("Castly – Turn hours of audio into minutes of insight • © Manasi Narkhede")
