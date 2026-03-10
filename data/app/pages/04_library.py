# pages/04_library.py

import streamlit as st
import os
import json
from utils import render_global_sidebar, apply_theme
from pathlib import Path

# ============================================================
# PROJECT PATH CONFIGURATION
# ============================================================

BASE_DIR = Path(r"D:\Audio app")
LOGO_PATH = BASE_DIR / "data" / "images" / "logo.png"

# Render global sidebar (logo + theme toggle)
dark_mode = render_global_sidebar(LOGO_PATH)
apply_theme(dark_mode)

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Castly",
    page_icon=LOGO_PATH,
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("This American Life Library")
st.markdown("Pre-processed podcast episodes – ready to explore")

# ============================================================
# LIBRARY DIRECTORY VALIDATION
# ============================================================

library_dir = "D:\\Audio app\\data\\segmented_outputs"

if not os.path.exists(library_dir):
    st.error(f"Library folder not found: {library_dir}")
    st.stop()

# ============================================================
# COUNT AVAILABLE EPISODES
# ============================================================

# List only JSON files (each file represents one episode)
episode_files = [
    f for f in os.listdir(library_dir)
    if f.endswith(".json")
]

total_episodes = len(episode_files)

# Stop execution if no processed episodes found
if total_episodes == 0:
    st.info("No pre-processed episodes found in the library folder.")
    st.stop()


# ============================================================
# DATA OVERVIEW SECTION
# ============================================================

st.subheader("Data Overview")

# Create responsive metric layout
col1, col2, col3 = st.columns([1.2, 1.5, 1.2])

with col1:
    st.metric("Total Episodes", total_episodes)

with col2:
    st.metric("Source Dataset", "This American Life")

with col3:
    st.metric("Total Processing Time", "~15 hours")

st.markdown("---")

# ============================================================
# DATASET DESCRIPTION
# ============================================================

st.markdown(f"""
**Dataset Highlights**  
- **Source**: This American Life podcast archive  
- **Number of episodes**: {total_episodes}  
- **Total audio duration**: ~150 hours  
- **Average episode length**: 45–60 minutes  
- **Output format**: JSON per episode (segments, timestamps, keywords, summaries, sentiment)  
- **Purpose**: Used for testing transcription, segmentation, summarization, and UI features  
""")

st.markdown("---")

# ============================================================
# NAVIGATION SECTION
# ============================================================

st.subheader("Explore the App")

# Navigation columns
col_search, col_browse = st.columns(2)


# ---- Search Navigation ----
with col_search:
    st.markdown("**Search Across Segments**")
    st.caption("Find specific topics, keywords, or phrases in processed podcasts")

    if st.button("Go to Search Segments", use_container_width=True):
        st.switch_page("D:\\Audio app\\data\\app\\pages\\02_search.py")


# ---- Browse Navigation ----
with col_browse:
    st.markdown("**Browse Episodes & Segments**")
    st.caption("View detailed timelines, word clouds, summaries, and jump to audio moments")

    if st.button("Go to Browse Episodes", use_container_width=True):
        st.switch_page("D:\\Audio app\\data\\app\\pages\\03_browse.py")

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")
st.caption("Castly – Turn hours of audio into minutes of insight • © Manasi Narkhede")
