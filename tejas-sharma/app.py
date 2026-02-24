import streamlit as st
import os
import re
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Podcast Transcript Navigator",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- STYLES ----------------
st.markdown("""
<style>
.block-container { padding-top: 2rem; }

.segment-item {
    padding: 0.65rem 0.75rem;
    margin-bottom: 0.35rem;
    background-color: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 6px;
}

.segment-active {
    background-color: rgba(99,102,241,0.18);
    border-left: 4px solid #6366f1;
}

.section-title {
    font-size: 0.75rem;
    letter-spacing: 0.14em;
    opacity: 0.55;
    margin-bottom: 0.6rem;
}

.transcript-box {
    background-color: rgba(255,255,255,0.04);
    border-radius: 10px;
    padding: 1.6rem;
    line-height: 1.75;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HELPERS ----------------
def extract_chunk_index(filename):
    return int(filename.split("_chunk_")[1].split(".")[0])

def polish_summary(text):
    if not text:
        return ""
    fillers = ["um", "you know", "like"]
    for f in fillers:
        text = re.sub(rf"\b{f}\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip()
    sentences = re.split(r'(?<=[.!?]) +', text)[:3]
    return " ".join(s.capitalize() for s in sentences)

# ---------------- SENTIMENT ----------------
sentiment_analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment(text):
    score = sentiment_analyzer.polarity_scores(text)["compound"]
    if score >= 0.05:
        return "Positive", score
    elif score <= -0.05:
        return "Negative", score
    return "Neutral", score

# ---------------- PATHS ----------------
SEGMENT_DIR = "results/advanced_segments"
SUMMARY_DIR = "results/summaries"
KEYWORD_DIR = "results/embedding_results/keywords"

CUSTOM_STOPWORDS = {
    "data","today","looking","feel","feeling",
    "episode","podcast","host","welcome",
    "content","talking","people"
}

def load_summary(idx):
    path = os.path.join(SUMMARY_DIR, f"Podcast1_chunk_{idx}_summary.txt")
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return polish_summary(f.read().strip())

def load_keywords(idx):
    path = os.path.join(KEYWORD_DIR, f"Podcast1_chunk_{idx}_keywords.txt")
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [
            line.strip().lower()
            for line in f.readlines()
            if line.strip() and "keywords" not in line.lower()
        ]

# ---------------- LOAD SEGMENTS (DEDUPLICATED) ----------------
segments = {}
for file in sorted(os.listdir(SEGMENT_DIR), key=extract_chunk_index):
    if not file.endswith(".txt"):
        continue

    idx = extract_chunk_index(file)

    # ✅ Ignore duplicate chunk files
    if idx in segments:
        continue

    with open(os.path.join(SEGMENT_DIR, file), "r", encoding="utf-8") as f:
        transcript = f.read().strip()

    sentiment_label, sentiment_score = analyze_sentiment(transcript)

    segments[idx] = {
        "id": idx,
        "label": f"Segment {idx + 1}",
        "transcript": transcript,
        "summary": load_summary(idx),
        "sentiment_label": sentiment_label,
        "sentiment_score": sentiment_score,
        "keywords": load_keywords(idx)
    }

segments = list(segments.values())

# ---------------- HEADER ----------------
st.title("🎙️ Podcast Transcript Navigator")
st.caption("Milestone 3 · Visualization and Detail Enhancements")

# ---------------- STATE ----------------
if "selected_id" not in st.session_state:
    st.session_state.selected_id = segments[0]["id"]

# ---------------- LAYOUT ----------------
left, right = st.columns([1.3, 3.7])

# ---------------- LEFT PANEL (SCROLLABLE, YOUR UI) ----------------
with left:
    st.markdown("<div class='section-title'>SEGMENTS</div>", unsafe_allow_html=True)

    with st.container(height=520):
        for seg in segments:
            active = seg["id"] == st.session_state.selected_id
            css = "segment-item segment-active" if active else "segment-item"

            st.markdown(f"<div class='{css}'>", unsafe_allow_html=True)

            if st.button(
                seg["label"],
                key=f"seg_{seg['id']}_{hash(seg['transcript'])}"
            ):
                st.session_state.selected_id = seg["id"]

            st.markdown("</div>", unsafe_allow_html=True)

# ---------------- RIGHT PANEL ----------------
selected_seg = next(s for s in segments if s["id"] == st.session_state.selected_id)

with right:
    st.markdown("<div class='section-title'>TITLE</div>", unsafe_allow_html=True)
    st.subheader(selected_seg["label"])

    st.markdown("<div class='section-title'>SUMMARY</div>", unsafe_allow_html=True)
    st.write(selected_seg["summary"] or "Summary not available.")

    st.markdown("<div class='section-title'>SENTIMENT</div>", unsafe_allow_html=True)
    icon = {"Positive": "🟢", "Neutral": "🟡", "Negative": "🔴"}
    st.markdown(
        f"**{icon[selected_seg['sentiment_label']]} {selected_seg['sentiment_label']}** "
        f"(score: `{selected_seg['sentiment_score']:.2f}`)"
    )

    st.markdown("<div class='section-title'>KEYWORDS</div>", unsafe_allow_html=True)
    if selected_seg["keywords"]:
        wc = WordCloud(
            width=600,
            height=220,
            background_color="white",
            colormap="Blues",
            stopwords=CUSTOM_STOPWORDS,
            max_words=25,
            collocations=False
        ).generate(" ".join(selected_seg["keywords"]))

        fig, ax = plt.subplots(figsize=(5.5, 2.2))
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)
    else:
        st.info("No keywords available.")

    st.markdown("<div class='section-title'>TRANSCRIPT</div>", unsafe_allow_html=True)
    st.markdown(
    f"<div class='transcript-box'>{selected_seg['transcript']}</div>",
        unsafe_allow_html=True
    )
#v