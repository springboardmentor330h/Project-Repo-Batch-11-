import os
import json
import re
import streamlit as st
import pandas as pd
import altair as alt
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter

# -----------------------------
# CONFIG
# -----------------------------
DATA_DIR = "output_kws_summaries/json_with_sentiment"
MIN_WORDS_PER_SEGMENT = 15

DISPLAY_STOPWORDS = {
    "yeah", "oh", "okay", "right", "know", "thing", "et", "cetera"
}

st.set_page_config(
    page_title="Podcast Topic Timeline",
    layout="wide"
)

st.title("🎧 Podcast Topic Timeline")
st.caption(
    "Visual timeline of podcast topics. "
    "Block width ∝ segment length (word count). "
    "Color indicates sentiment."
)

# -----------------------------
# HELPERS
# -----------------------------
def polish_summary(summary: str) -> str:
    if not summary:
        return "No summary available."

    summary = re.sub(
        r"\b(um|uh|you know|i mean)\b",
        "",
        summary,
        flags=re.IGNORECASE
    )
    summary = re.sub(r"\s+", " ", summary).strip()

    summary = summary[0].upper() + summary[1:] if summary else summary
    sentences = re.split(r"(?<=[.!?])\s+", summary)
    return " ".join(sentences[:3])


def summary_has_repetition(summary: str) -> bool:
    words = summary.lower().split()
    trigrams = [" ".join(words[i:i+3]) for i in range(len(words) - 2)]
    counts = Counter(trigrams)
    return any(v > 2 for v in counts.values())


def clean_keywords(keywords):
    return [kw for kw in keywords if kw.lower() not in DISPLAY_STOPWORDS]


def render_keyword_cloud(keywords):
    if not keywords:
        st.info("No keywords available.")
        return

    freq = {kw: 1 for kw in keywords}
    wc = WordCloud(
        width=600,
        height=300,
        background_color="white"
    ).generate_from_frequencies(freq)

    fig, ax = plt.subplots()
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)


# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_episode_files(data_dir):
    return sorted([f for f in os.listdir(data_dir) if f.endswith(".json")])


@st.cache_data
def load_episode_titles(data_dir, files):
    mapping = {}
    for fname in files:
        with open(os.path.join(data_dir, fname), "r", encoding="utf-8") as f:
            data = json.load(f)
            mapping[data.get("title", fname)] = fname
    return mapping


episode_files = load_episode_files(DATA_DIR)[:10]
title_to_file = load_episode_titles(DATA_DIR, episode_files)

selected_title = st.selectbox(
    "🎙️ Select Podcast Episode",
    options=list(title_to_file.keys())
)

with open(os.path.join(DATA_DIR, title_to_file[selected_title]), "r", encoding="utf-8") as f:
    episode_data = json.load(f)

segments = [
    s for s in episode_data.get("segments", [])
    if s["num_words"] >= MIN_WORDS_PER_SEGMENT
]

if not segments:
    st.warning("No usable segments found.")
    st.stop()

st.markdown(f"### {episode_data.get('title', 'Unknown Episode')}")
st.markdown("---")

# -----------------------------
# SESSION STATE
# -----------------------------
if "seg_index" not in st.session_state:
    st.session_state.seg_index = 0

# -----------------------------
# TIMELINE
# -----------------------------
cursor = 0
rows = []

for seg in segments:
    rows.append({
        "segment": f"S{seg['segment_id']}",
        "start": cursor,
        "end": cursor + seg["num_words"],
        "sentiment": seg.get("sentiment_label", "Neutral"),
        "summary": polish_summary(seg.get("summary", ""))
    })
    cursor += seg["num_words"]

df = pd.DataFrame(rows)

timeline = (
    alt.Chart(df)
    .mark_bar(height=30)
    .encode(
        x="start:Q",
        x2="end:Q",
        color=alt.Color(
            "sentiment:N",
            scale=alt.Scale(
                domain=["Positive", "Neutral", "Negative"],
                range=["#4CAF50", "#FFC107", "#F44336"]
            )
        ),
        tooltip=["segment", "sentiment", "summary"]
    )
    .properties(height=90)
)

st.altair_chart(timeline, use_container_width=True)
st.markdown("---")

# -----------------------------
# NAVIGATION CONTROLS
# -----------------------------
c1, c2, c3 = st.columns([1, 2, 1])

with c1:
    if st.button("⬅ Previous") and st.session_state.seg_index > 0:
        st.session_state.seg_index -= 1

with c3:
    if st.button("Next ➡") and st.session_state.seg_index < len(segments) - 1:
        st.session_state.seg_index += 1

labels = [
    f"S{seg['segment_id']}: {polish_summary(seg.get('summary',''))[:70]}"
    for seg in segments
]

st.session_state.seg_index = st.selectbox(
    "📌 Jump to Segment",
    range(len(labels)),
    index=st.session_state.seg_index,
    format_func=lambda i: labels[i]
)

selected_segment = segments[st.session_state.seg_index]

# -----------------------------
# SEGMENT DISPLAY
# -----------------------------
st.markdown("---")
st.subheader(f"📄 Segment {selected_segment['segment_id']}")

m1, m2, m3 = st.columns(3)
m1.metric("Start sentence", selected_segment["start_sentence"])
m2.metric("End sentence", selected_segment["end_sentence"])
m3.metric("Word count", selected_segment["num_words"])

st.markdown("### 📝 Summary")
summary = polish_summary(selected_segment.get("summary", ""))

if summary_has_repetition(summary):
    st.warning("Summary repetition detected. Showing transcript instead.")
    st.text_area("Transcript", selected_segment["text"], height=200)
else:
    st.write(summary)

st.markdown("### 🔑 Keywords")
keywords = clean_keywords(selected_segment.get("keywords", []))
if keywords:
    st.write(", ".join(keywords))
    render_keyword_cloud(keywords)
else:
    st.info("No meaningful keywords.")

st.markdown("### 😊 Sentiment")
st.markdown(
    f"**{selected_segment.get('sentiment_label','Unknown')}** "
    f"(score: {selected_segment.get('sentiment_score',0.0):.2f})"
)

st.markdown("### 📜 Transcript")
st.text_area("", selected_segment["text"], height=400)

st.caption(
    "Week 6 iteration: navigation buttons, micro-segment filtering, "
    "keyword cleanup, and summary quality checks applied."
)
