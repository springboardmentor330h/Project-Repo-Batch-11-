import streamlit as st
import json
import os
import re

# ---------------- CONFIG ----------------
DATA_PATH = "outputs"   # folder containing JSON files

st.set_page_config(page_title="Podcast Topic Explorer", layout="wide")

# ---------------- DARK THEME STYLE ----------------
st.markdown("""
<style>
html, body, [class*="css"] {
    background-color: #0e1117;
    color: white;
}
.title{
    font-size:40px;
    font-weight:700;
}
.subtitle{
    font-size:18px;
    color:#9aa4b2;
    margin-bottom:30px;
}
.card{
    background:#161b22;
    padding:20px;
    border-radius:15px;
    margin-bottom:20px;
}
.segment-title{
    font-size:20px;
    font-weight:600;
    color:#58a6ff;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HELPERS ----------------
def load_json(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_ids():
    ids = []
    for file in os.listdir(DATA_PATH):
        m = re.search(r"_(\d+)\.json", file)
        if m:
            ids.append(m.group(1))
    return sorted(list(set(ids)))


# -------- AUTO PODCAST TITLE FROM CONTENT --------
def generate_title(pid):
    summaries = load_json(f"{DATA_PATH}/final_summaries_{pid}.json")
    keywords = load_json(f"{DATA_PATH}/final_keywords_{pid}.json")

    text = ""

    if isinstance(summaries, dict) and summaries:
        text += " ".join(list(summaries.values())[:2])

    if isinstance(keywords, dict) and keywords:
        first = list(keywords.values())[0]
        if isinstance(first, list):
            text += " " + " ".join(first[:5])

    words = [w.capitalize() for w in text.split() if len(w) > 4][:6]

    if not words:
        return f"Talk {pid}"

    return " ".join(words)


# -------- SEGMENT TITLE FROM TEXT --------
def segment_title(text):
    words = [w.capitalize() for w in text.split() if len(w) > 4][:4]
    if not words:
        return "Segment"
    return " ".join(words)


# ---------------- HEADER ----------------
st.markdown('<div class="title">🎧 Podcast Topic Explorer</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-Powered Podcast Transcription & Topic Segmentation</div>', unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
ids = extract_ids()
title_map = {generate_title(pid): pid for pid in ids}

selected_title = st.sidebar.selectbox("Choose a Talk", list(title_map.keys()))
pid = title_map[selected_title]

search_query = st.sidebar.text_input("🔎 Search inside podcast")

# ---------------- LOAD FILES ----------------
segments = load_json(f"{DATA_PATH}/segments_{pid}.json")
summaries = load_json(f"{DATA_PATH}/final_summaries_{pid}.json")
keywords = load_json(f"{DATA_PATH}/final_keywords_{pid}.json")
sentiments = load_json(f"{DATA_PATH}/final_sentiment_{pid}.json")

# ---------------- SEGMENT SELECTOR ----------------
st.markdown('<div class="card">', unsafe_allow_html=True)

if isinstance(segments, list):
    seg_ids = list(range(len(segments)))
else:
    seg_ids = list(segments.keys())

selected_segment = st.selectbox("Select Segment", seg_ids)

# ---------------- GET SEGMENT DATA ----------------
if isinstance(segments, list):
    seg = segments[int(selected_segment)]
    text = seg["text"]
else:
    seg = segments[selected_segment]
    text = seg

title = segment_title(text)

# ---------------- DISPLAY SEGMENT ----------------
st.markdown(f'<div class="segment-title">{title}</div>', unsafe_allow_html=True)

# search highlight
if search_query:
    text = re.sub(
        f"({search_query})",
        r"<mark style='background:#facc15;color:black'>\1</mark>",
        text,
        flags=re.IGNORECASE,
    )

st.markdown(text, unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ---------------- SUMMARY ----------------
if summaries:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Summary")
    val = summaries[str(selected_segment)] if isinstance(summaries, dict) else summaries[int(selected_segment)]
    st.write(val)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- KEYWORDS ----------------
if keywords:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Keywords")

    kws = keywords[str(selected_segment)] if isinstance(keywords, dict) else keywords[int(selected_segment)]

    cols = st.columns(len(kws))
    for i, k in enumerate(kws):
        cols[i].button(k)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- SENTIMENT ----------------
if sentiments:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Sentiment")

    s = sentiments[str(selected_segment)] if isinstance(sentiments, dict) else sentiments[int(selected_segment)]

    label = s["label"] if isinstance(s, dict) else s
    score = s.get("score", 0.5) if isinstance(s, dict) else 0.5

    st.progress(float(score))
    st.write(label)
    st.markdown("</div>", unsafe_allow_html=True)