import streamlit as st
import json

# Load combined transcript segments
with open("../week 1_3/combined_segments.json", "r", encoding="utf-8") as f:
    segments = json.load(f)

st.title("Podcast Transcript Navigation")

# Dropdown options
segment_titles = [seg["title"] for seg in segments]

selected_segment = st.selectbox("Select Transcript Segment", segment_titles)

# Display transcript text
for seg in segments:
    if seg["title"] == selected_segment:
        st.subheader("Transcript")
        st.write(seg["text"])
