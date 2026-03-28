import streamlit as st
import os
import json
import glob
import matplotlib.pyplot as plt
from wordcloud import WordCloud

st.set_page_config(page_title="Podcast Transcript Navigation", layout="wide")

st.title("🎙️ Podcast Transcript Navigation")

# -----------------------------
# LOAD ALL JSON FILES
# -----------------------------

# All episode json files
transcript_files = glob.glob("transcripts/*.json")

# Episode 5 combined file
combined_file = "week_5/combined_segments.json"

all_files = transcript_files.copy()

if os.path.exists(combined_file):
    all_files.append(combined_file)

file_options = [os.path.basename(f) for f in all_files]

if not file_options:
    st.error("No JSON files found!")
    st.stop()

# -----------------------------
# EPISODE SELECT
# -----------------------------

selected_file_name = st.selectbox("Select Podcast Episode", file_options)

selected_file_path = None
for f in all_files:
    if os.path.basename(f) == selected_file_name:
        selected_file_path = f
        break

with open(selected_file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# -----------------------------
# HANDLE DIFFERENT JSON FORMATS
# -----------------------------

if isinstance(data, list):
    segments = data
elif isinstance(data, dict) and "segments" in data:
    segments = data["segments"]
else:
    segments = [data]

# -----------------------------
# SEGMENT SELECT
# -----------------------------

titles = []
for i, seg in enumerate(segments):
    if "title" in seg:
        titles.append(seg["title"])
    else:
        titles.append(f"segment_{i}")

selected_title = st.selectbox("Select Segment", titles)

selected_segment = segments[titles.index(selected_title)]

# -----------------------------
# DISPLAY CONTENT
# -----------------------------

col1, col2 = st.columns(2)

with col1:
    st.subheader("📜 Transcript")
    st.write(selected_segment.get("text", "No transcript available"))

    st.subheader("📝 Summary")
    st.write(selected_segment.get("summary", "No summary available"))

with col2:
    st.subheader("😊 Sentiment")
    st.info(selected_segment.get("sentiment", "Not Available"))

    st.subheader("🔑 Keywords")
    keywords = selected_segment.get("keywords", [])
    if keywords:
        st.write(", ".join(keywords))
    else:
        st.write("No keywords available")

# -----------------------------
# WORD CLOUD
# -----------------------------

st.subheader("☁️ Keyword Word Cloud")

if keywords:
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(" ".join(keywords))
    fig, ax = plt.subplots()
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)
else:
    st.write("No keywords for word cloud")

# -----------------------------
# TIMELINE VISUALIZATION
# -----------------------------

st.subheader("📊 Timeline")

segment_index = titles.index(selected_title)

# Assume each chunk is 120 seconds (2 minutes)
chunk_duration = 120  

start = segment_index * chunk_duration
end = start + chunk_duration

st.write(f"Start: {start} sec")
st.write(f"End: {end} sec")
