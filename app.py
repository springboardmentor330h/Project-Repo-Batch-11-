import os
import json
import re
import streamlit as st
import pandas as pd
import altair as alt
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# -----------------------------
# CONFIG
# -----------------------------
DATA_DIR = "output_kws_summaries/json_with_sentiment"

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
    """
    Light, rule-based cleanup:
    - remove filler words
    - normalize spacing
    - capitalize
    - keep max 2–3 sentences
    """
    if not summary:
        return "No summary available."

    summary = re.sub(
        r"\b(um|uh|you know|i mean)\b",
        "",
        summary,
        flags=re.IGNORECASE
    )
    summary = re.sub(r"\s+", " ", summary).strip()

    if summary:
        summary = summary[0].upper() + summary[1:]

    sentences = re.split(r"(?<=[.!?])\s+", summary)
    return " ".join(sentences[:3])


def render_keyword_cloud(keywords):
    if not keywords:
        st.info("No keywords available for this segment.")
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
# LOAD EPISODE FILES
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
            title = data.get("title", fname)
            mapping[title] = fname
    return mapping


episode_files = load_episode_files(DATA_DIR)
if not episode_files:
    st.error("No episode JSON files found.")
    st.stop()

title_to_file = load_episode_titles(DATA_DIR, episode_files)

# -----------------------------
# EPISODE SELECTOR
# -----------------------------
selected_title = st.selectbox(
    "🎙️ Select Podcast Episode",
    options=list(title_to_file.keys())
)

episode_path = os.path.join(DATA_DIR, title_to_file[selected_title])
with open(episode_path, "r", encoding="utf-8") as f:
    episode_data = json.load(f)

segments = episode_data.get("segments", [])
if not segments:
    st.warning("No segments found for this episode.")
    st.stop()

st.markdown(f"### {episode_data.get('title', 'Unknown Episode')}")
st.markdown("---")

# ============================================================
# 🧭 VISUAL TIMELINE (WEEK 5 CORE)
# ============================================================
timeline_rows = []
cursor = 0

for seg in segments:
    timeline_rows.append({
        "segment": f"S{seg['segment_id']}",
        "start": cursor,
        "end": cursor + seg["num_words"],
        "sentiment": seg.get("sentiment_label", "Neutral"),
        "summary": polish_summary(seg.get("summary", ""))
    })
    cursor += seg["num_words"]

df = pd.DataFrame(timeline_rows)

color_scale = alt.Scale(
    domain=["Positive", "Neutral", "Negative"],
    range=["#4CAF50", "#FFC107", "#F44336"]
)

timeline_chart = (
    alt.Chart(df)
    .mark_bar(height=28)
    .encode(
        x=alt.X("start:Q", title="Podcast Progress (word-based)", axis=alt.Axis(grid=False)),
        x2="end:Q",
        y=alt.value(0),
        color=alt.Color("sentiment:N", scale=color_scale, legend=alt.Legend(title="Sentiment")),
        tooltip=[
            alt.Tooltip("segment:N", title="Segment"),
            alt.Tooltip("sentiment:N", title="Sentiment"),
            alt.Tooltip("summary:N", title="Summary")
        ],
    )
    .properties(height=80)
)

st.altair_chart(timeline_chart, use_container_width=True)
st.markdown("---")

# ============================================================
# SEGMENT SELECTION
# ============================================================
def build_segment_label(seg):
    s = polish_summary(seg.get("summary", ""))
    return f"S{seg['segment_id']}: {s[:70]}{'...' if len(s) > 70 else ''}"

labels = [build_segment_label(s) for s in segments]

selected_index = st.selectbox(
    "📌 Select Topic Segment",
    options=list(range(len(labels))),
    format_func=lambda i: labels[i]
)

selected_segment = segments[selected_index]

# ============================================================
# SEGMENT DETAILS (FORMATTED)
# ============================================================
with st.container():
    st.subheader(f"📄 Segment {selected_segment['segment_id']}")

    m1, m2, m3 = st.columns(3)
    m1.metric("Start sentence", selected_segment["start_sentence"])
    m2.metric("End sentence", selected_segment["end_sentence"])
    m3.metric("Word count", selected_segment["num_words"])

    st.markdown("### 📝 Summary")
    st.write(polish_summary(selected_segment.get("summary", "")))

    st.markdown("### 🔑 Keywords")
    keywords = selected_segment.get("keywords", [])
    if keywords:
        st.write(", ".join(keywords))
        render_keyword_cloud(keywords)
    else:
        st.info("No keywords available.")

    st.markdown("### 😊 Sentiment")
    sentiment_label = selected_segment.get("sentiment_label", "Unknown")
    sentiment_score = selected_segment.get("sentiment_score", 0.0)

    color_map = {
        "Positive": "green",
        "Neutral": "orange",
        "Negative": "red"
    }

    st.markdown(
        f"<span style='color:{color_map.get(sentiment_label, 'black')};"
        f"font-weight:bold'>{sentiment_label}</span> "
        f"(score: {sentiment_score:.2f})",
        unsafe_allow_html=True
    )

    st.markdown("### 📜 Transcript")
    st.text_area("", selected_segment["text"], height=400)

st.caption(
    "Timeline gives a high-level overview; dropdown enables precise navigation."
)
