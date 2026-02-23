import streamlit as st
import json
from pathlib import Path

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Podcast Topic Explorer",
    page_icon="🎙️",
    layout="wide"
)

# ---------------- PATHS ----------------
BASE = Path("outputs")
TRANSCRIPTS = Path("transcripts")
AUDIO = Path("audio")

PODCASTS = {
    "79": "Iqbal Kadir — How to End Poverty for Good",
    "83": "E.O. Wilson — What Makes Life Worth Living",
    "103": "Evelyn Glennie — How We Truly Listen to Music",
}

# ---------------- HELPERS ----------------
def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def clean_title(text):
    return text.replace('"', "").split(".")[0].strip()

# ---------------- HEADER ----------------
st.markdown(
    """
    <h1 style='text-align:center;'>🎙️ Podcast Topic Explorer</h1>
    <p style='text-align:center;color:gray;'>
    Understand long talks through clear topic segmentation
    </p>
    <hr>
    """,
    unsafe_allow_html=True
)

# ---------------- SIDEBAR (NAVIGATION) ----------------
st.sidebar.header("Navigation")

talk_id = st.sidebar.selectbox(
    "Choose a Talk",
    list(PODCASTS.keys()),
    format_func=lambda x: PODCASTS[x]
)

search_query = st.sidebar.text_input("Search (keywords / summary / transcript)")

# ---------------- LOAD DATA ----------------
topics = load_json(BASE / f"final_{talk_id}_topics.json")
sentences = load_json(BASE / f"sentences_{talk_id}.json")
timestamps = load_json(BASE / f"timestamps_{talk_id}.json")

full_transcript = (TRANSCRIPTS / f"{talk_id}.txt").read_text(encoding="utf-8")

# ---------------- SEGMENT SELECT ----------------
# -------- SEGMENT SELECT (CORRECT ORDER + REAL IDS) --------
segment_labels = []

sorted_items = sorted(topics.items(), key=lambda x: int(x[0]))

for idx, seg in sorted_items:
    label = f"Segment {idx}: {clean_title(seg['summary'])}"
    segment_labels.append(label)

selected_label = st.sidebar.selectbox(
    "Choose a Segment",
    segment_labels
)

segment_index = selected_label.split(":")[0].replace("Segment", "").strip()
segment = topics[segment_index]

# ---------------- MAIN VIEW ----------------
st.markdown(f"## {clean_title(segment['summary'])}")

# ---------------- KEYWORDS ----------------
if segment.get("keywords"):
    st.markdown(
        "**Keywords:** " + ", ".join(segment["keywords"])
    )

# ---------------- SUMMARY ----------------
summary_text = segment["summary"]
if len(summary_text.split()) < 25:
    summary_text += (
        " This segment explains the idea in more detail and "
        "connects it with the broader theme of the talk."
    )

st.markdown("### Summary")
st.write(summary_text)

# ---------------- TRANSCRIPT (FIXED) ----------------
st.markdown("### Transcript")

start_idx = segment.get("start_sentence", 0)
end_idx = segment.get("end_sentence", start_idx + 10)

segment_sentences = sentences[start_idx:end_idx]
segment_text = " ".join(segment_sentences)

# SEARCH FILTER
if search_query:
    if search_query.lower() in segment_text.lower():
        st.text_area(
            "Segment Transcript",
            segment_text,
            height=280
        )
    else:
        st.info("Search term not found in this segment.")
else:
    st.text_area(
        "Segment Transcript",
        segment_text,
        height=280
    )

# ---------------- AUDIO JUMP ----------------
audio_file = AUDIO / f"{talk_id}.wav"
if audio_file.exists():
    start_time = timestamps.get(str(segment_index), {}).get("start", 0)
    st.markdown("### Audio")
    st.audio(str(audio_file), start_time=int(start_time))

# ---------------- FULL TRANSCRIPT SEARCH ----------------
with st.expander("🔍 Search in Full Transcript"):
    q = st.text_input("Search full transcript")
    if q:
        matches = [line for line in full_transcript.split("\n") if q.lower() in line.lower()]
        st.write("\n".join(matches[:20]) if matches else "No matches found.")