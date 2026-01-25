import os
import json
import streamlit as st

# -----------------------------
# CONFIG
# -----------------------------
DATA_DIR = "output_kws_summaries/json_updated"

st.set_page_config(
    page_title="Podcast Transcript Navigator",
    layout="wide"
)

st.title("🎧 Podcast Transcript Navigation")
st.caption("Select a topic to instantly jump to that part of the transcript")

# -----------------------------
# LOAD EPISODE FILES
# -----------------------------
@st.cache_data
def load_episode_files(data_dir):
    return sorted([
        f for f in os.listdir(data_dir)
        if f.endswith(".json")
    ])

episode_files = load_episode_files(DATA_DIR)

if not episode_files:
    st.error("No episode JSON files found.")
    st.stop()

# -----------------------------
# LOAD TITLES FOR DROPDOWN
# -----------------------------
@st.cache_data
def load_episode_titles(data_dir, files):
    title_to_file = {}
    for fname in files:
        path = os.path.join(data_dir, fname)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            title = data.get("title", fname)
            title_to_file[title] = fname
    return title_to_file

title_to_file = load_episode_titles(DATA_DIR, episode_files)

# -----------------------------
# EPISODE SELECTOR (TITLE-BASED)
# -----------------------------
selected_title = st.selectbox(
    "🎙️ Select Podcast Episode",
    options=list(title_to_file.keys())
)

episode_file = title_to_file[selected_title]
episode_path = os.path.join(DATA_DIR, episode_file)

with open(episode_path, "r", encoding="utf-8") as f:
    episode_data = json.load(f)

segments = episode_data.get("segments", [])
title = episode_data.get("title", "Unknown Episode")

st.markdown(f"### {title}")
st.markdown("---")

if not segments:
    st.warning("No segments found for this episode.")
    st.stop()

# -----------------------------
# BUILD SEGMENT LABELS
# -----------------------------
def build_segment_label(seg):
    summary = seg.get("summary", "").strip()
    keywords = seg.get("keywords", [])

    if summary:
        label = summary[:70] + ("..." if len(summary) > 70 else "")
    elif keywords:
        label = ", ".join(keywords[:3])
    else:
        label = f"Segment {seg['segment_id']}"

    return f"Segment {seg['segment_id']}: {label}"

labels = [build_segment_label(s) for s in segments]

# -----------------------------
# SEGMENT DROPDOWN
# -----------------------------
selected_index = st.selectbox(
    "📌 Select Topic Segment",
    options=list(range(len(labels))),
    format_func=lambda i: labels[i]
)

selected_segment = segments[selected_index]

# -----------------------------
# DISPLAY SELECTED SEGMENT
# -----------------------------
st.markdown("---")
st.subheader(f"📄 Segment {selected_segment['segment_id']}")

meta1, meta2, meta3 = st.columns(3)
meta1.metric("Start sentence", selected_segment["start_sentence"])
meta2.metric("End sentence", selected_segment["end_sentence"])
meta3.metric("Word count", selected_segment["num_words"])

if selected_segment.get("keywords"):
    st.markdown(
        "**Keywords:** " + ", ".join(selected_segment["keywords"])
    )

st.text_area(
    "Transcript Text",
    selected_segment["text"],
    height=450
)

st.caption("⬆ Choose another segment from the dropdown to jump instantly.")
