# pages/01_upload_audio.py

import streamlit as st
from utils import *          
from pathlib import Path

# Base directory 
BASE_DIR = Path(r"D:\Audio app")

LOGO_PATH = BASE_DIR / "data" / "images" / "logo.png"

# ---------------------------------------------------------------
# THEME & PAGE CONFIGURATION 
# ---------------------------------------------------------------

# Render global sidebar (logo + dark mode toggle)
dark_mode = render_global_sidebar(LOGO_PATH)

apply_theme(dark_mode)

st.set_page_config(
    page_title="Castly",          
    page_icon=LOGO_PATH,          
    layout="wide",                
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------------
# PAGE HEADER
# ---------------------------------------------------------------

st.title("Upload Audio")
st.subheader("Upload any audio file to transcribe & analyze")

# ---------------------------------------------------------------
# AUDIO UPLOAD SECTION
# ---------------------------------------------------------------

# File uploader (Supported audio formats)
audio_file = st.file_uploader(
    "Upload podcast episode",
    type=["mp3", "wav", "m4a", "ogg"]
)

quick_demo = st.checkbox(
    "Quick Demo: Process only first 10 minutes",
    value=True
)

if quick_demo:
    st.info("Only the first 10 minutes will be processed ")

# ---------------------------------------------------------------
# AUDIO PROCESSING PIPELINE
# ---------------------------------------------------------------

if audio_file is not None:

    # Store uploaded audio bytes in session state (persistent across reruns)
    if "uploaded_audio_bytes" not in st.session_state:
        st.session_state.uploaded_audio_bytes = audio_file.read()

    # Automatically detect audio title (from metadata or filename)
    title = get_audio_title(
        BytesIO(st.session_state.uploaded_audio_bytes),
        audio_file.name
    )

    st.session_state.title = title
    st.info(f"**Detected title:** {title}")

    # Process button (triggers full pipeline)
    if st.button("Process Audio", type="primary"):

        if "uploaded_audio_bytes" not in st.session_state or not st.session_state.uploaded_audio_bytes:
            st.error("No audio bytes saved – re-upload the file")
            st.stop()

        # Convert stored bytes into BytesIO object
        audio_bytes = BytesIO(st.session_state.uploaded_audio_bytes)
        audio_bytes.seek(0)

        if quick_demo:
            audio_bytes = trim_audio_if_needed(audio_bytes, True)
            audio_bytes.seek(0)

        # -------------------- TRANSCRIPTION & SEGMENTATION --------------------
        with st.spinner("Processing..."):

            # Step 1: Speech-to-text transcription
            sentences = transcribe_audio(audio_bytes)

            # Step 2: Group sentences into logical segments
            raw_segments = create_segments(sentences)

        # Container for fully processed segment data
        processed_segments = []

        # Progress bar 
        progress = st.progress(0)
        total_segs = len(raw_segments) or 1


        # -------------------- NLP ENRICHMENT PER SEGMENT --------------------

        for i, seg_group in enumerate(raw_segments, 1):

            full_text = " ".join(s["text"] for s in seg_group)
            full_text_romanized = " ".join(s["romanized"] for s in seg_group)
            language = st.session_state.get("detected_language", "en")

            start = seg_group[0]["start"]

            summary = generate_summary(full_text)

            keywords = get_keywords(full_text)

            score = SENTIMENT_ANALYZER.polarity_scores(full_text)["compound"]

            # Sentiment classification thresholds
            sentiment = (
                "Positive" if score >= 0.05
                else "Negative" if score <= -0.05
                else "Neutral"
            )

            processed_segments.append({
                "segment_id": i,
                "start_sec": round(start, 1),
                "end_sec": round(seg_group[-1]["end"], 1),
                "text": full_text,
                "full_text_romanized": full_text_romanized,
                "language": language,
                "summary": summary,
                "keywords": keywords,
                "sentiment": sentiment,
                "sentiment_score": round(score, 2)
            })

            progress.progress(i / total_segs)

        # -------------------- SAVE RESULTS TO SESSION STATE --------------------

        st.session_state.segments = processed_segments
        st.session_state.df = pd.DataFrame(processed_segments)
        st.session_state.processed = True

        # Extract embedded podcast cover image
        st.session_state.cover_base64 = extract_cover_art(
            BytesIO(st.session_state.uploaded_audio_bytes),
            audio_file.name
        )

        st.success("Processing complete! Go to 'Search Segments' or 'Browse Segments'.")
        detected_lang = st.session_state.get("detected_language", "en")
        st.info(f"Detected Language: {detected_lang.upper()}")

        # -------------------- TRANSCRIPT DOWNLOAD OPTIONS --------------------

        if st.session_state.df is not None:

            # Create formatted transcript string
            full_transcript = "\n\n".join(
                f"[{row['start_sec']:.1f}s - {row['end_sec']:.1f}s] "
                f"{row['sentiment']} | {row['summary']}\n"
                f"Keywords: {', '.join(row['keywords'])}\n"
                f"{row['text']}\n"
                for _, row in st.session_state.df.iterrows()
            )

            # TXT download button
            st.download_button(
                label="Download Full Transcript (TXT)",
                data=full_transcript,
                file_name=f"{st.session_state.title.replace(' ', '_')}_transcript.txt",
                mime="text/plain"
            )

            # JSON structured export
            json_data = st.session_state.df.to_json(
                orient="records",
                indent=2
            )

            st.download_button(
                label="Download Full Transcript (JSON)",
                data=json_data,
                file_name=f"{st.session_state.title.replace(' ', '_')}_transcript.json",
                mime="application/json"
            )

# ---------------------------------------------------------------
# QUICK PREVIEW SECTION 
# ---------------------------------------------------------------

# Show preview only if processing completed
if st.session_state.get("processed", False):

    st.markdown("### Quick Preview – First Segment")

    if st.session_state.get("segments") and len(st.session_state.segments) > 0:

        # Display first processed segment
        first = st.session_state.segments[0]

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**Summary:** {first['summary']}")
            st.markdown(f"**Keywords:** {', '.join(first['keywords'])}")

        with col2:
            st.markdown(
                f"**Sentiment:** {first['sentiment']} "
                f"({first['sentiment_score']})"
            )

    else:
        # Error fallback if transcription failed
        st.warning("No segments generated – transcription may have failed.")

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")
st.caption("Castly – Turn hours of audio into minutes of insight • © Manasi Narkhede")
