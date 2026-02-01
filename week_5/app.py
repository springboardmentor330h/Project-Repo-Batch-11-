import os
import json
import streamlit as st

st.title("Podcast Transcript Navigation")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

json_path = os.path.join(
    BASE_DIR,
    "..",
    "week _1_3",          
    "combined_segments.json"
)

if not os.path.exists(json_path):
    st.error(f"File not found: {json_path}")
    st.stop()

with open(json_path, "r", encoding="utf-8") as f:
    segments = json.load(f)


titles = [seg["title"] for seg in segments]
selected_title = st.selectbox("Select Transcript Segment", titles)

selected_segment = next(seg for seg in segments if seg["title"] == selected_title)

st.subheader("Transcript")
st.write(selected_segment["text"])

if "keywords" in selected_segment:
    st.subheader("Keywords")
    st.write(", ".join(selected_segment["keywords"]))

if "sentiment" in selected_segment:
    st.subheader("Sentiment")
    st.write(selected_segment["sentiment"])
