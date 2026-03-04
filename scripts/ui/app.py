import streamlit as st
import whisper
import os
import tempfile
import sys
import uuid

# Add parent directory to path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from topic_segmentation import TopicSegmenter
from audio_preprocessor import AudioPreprocessor

# -------------------- SETUP --------------------
st.set_page_config(
    page_title="Audio Analysis App",
    layout="wide"
)

# -------------------- LOAD RESOURCES --------------------
@st.cache_resource
def load_whisper():
    return whisper.load_model("tiny")  # Fast & CPU-safe

@st.cache_resource
def load_modules():
    return TopicSegmenter(), AudioPreprocessor()

whisper_model = load_whisper()
segmenter, preprocessor = load_modules()

# -------------------- FUNCTIONS --------------------
def transcribe_audio(audio_path):
    result = whisper_model.transcribe(audio_path)
    return result["text"]

def process_segments(text, algorithm="Similarity"):
    # Select algorithm
    if algorithm == "Similarity (Fast)":
        segments = segmenter.segment_with_similarity(text)
    elif algorithm == "TextTiling (NLTK)":
        segments = segmenter.segment_with_texttiling(text)
    elif algorithm == "Embeddings (Advanced)":
        segments = segmenter.segment_with_embeddings(text)
    else:
        segments = segmenter.segment_with_similarity(text)
    
    # Optional: Enforce topic count if needed (e.g. 5 to 15)
    # segments = segmenter.enforce_topic_count(segments, min_topics=5, max_topics=15)
    
    # Add metadata
    processed = []
    for i, seg in enumerate(segments):
        content = seg["text"]
        keywords = segmenter.extract_keywords(content)
        summary = segmenter.summarize(content)
        processed.append({
            "id": i,
            "label": f"Topic {i+1}: {summary[:40]}...",
            "text": content,
            "keywords": keywords,
            "summary": summary
        })
    return processed

# -------------------- UI LAYOUT --------------------
st.title("🎙️ Automated Podcast Transcription & Analysis")
st.markdown("### Workflow: Input ➡ Preprocessing ➡ Transcription ➡ Segmentation")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    algo_choice = st.selectbox(
        "Segmentation Algorithm",
        ["Embeddings (Advanced)", "TextTiling (NLTK)", "Similarity (Fast)"],
        index=0,
        help="Embeddings use AI (Sentence-BERT) to understand the meaning of the text for smart segmentation."
    )
    st.info("System automatically preprocesses audio (Denoise & Normalize) before transcription.")

# State Management
if 'last_uploaded_file' not in st.session_state:
    st.session_state.last_uploaded_file = None
if 'transcript' not in st.session_state:
    st.session_state.transcript = None
if 'segments' not in st.session_state:
    st.session_state.segments = []

# 1. AUDIO INPUT
st.subheader("1️⃣ Audio Input")
uploaded_audio = st.file_uploader(
    "Upload audio file (MP3 / WAV / M4A)",
    type=["mp3", "wav", "m4a"],
    key="file_uploader"
)

if uploaded_audio is not None:
    # Check if it's a new file
    if uploaded_audio.name != st.session_state.last_uploaded_file:
        st.session_state.last_uploaded_file = uploaded_audio.name
        st.session_state.transcript = None
        st.session_state.segments = []
        # st.rerun() # Removed unnecessary rerun here to allow first interaction

    st.audio(uploaded_audio, format='audio/mp3')

    # Trigger Pipeline
    if st.button("🚀 Start Auto-Pipeline"):
        # Save original to temp
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_audio.name.split('.')[-1]}") as tmp:
            tmp.write(uploaded_audio.getvalue())
            raw_path = tmp.name
        
        processed_path = raw_path + "_processed.wav"

        try:
            # Step 1: Preprocessing
            with st.spinner("⚙️ Step 1: Preprocessing Audio (Denoising & Normalizing)..."):
                preprocessor.process(raw_path, processed_path)
                st.success("Preprocessing Done.")

            # Step 2: Transcription
            with st.spinner("📝 Step 2: Generating Full Transcription..."):
                st.session_state.transcript = transcribe_audio(processed_path)
            
            # Step 3: Segmentation
            with st.spinner("📌 Step 3: Performing Topic Segmentation..."):
                st.session_state.segments = process_segments(st.session_state.transcript, algo_choice)
            
            st.success("Pipeline Completed Successfully!")
            
        except Exception as e:
            st.error(f"Error during processing: {e}")
        finally:
            # Cleanup
            if os.path.exists(raw_path):
                os.remove(raw_path)
            if os.path.exists(processed_path):
                os.remove(processed_path)

# 2. FULL TRANSCRIPTION
if st.session_state.transcript:
    st.divider()
    st.subheader("2️⃣ Full Transcription")
    with st.expander("📄 View Complete Transcript", expanded=True):
        st.text_area("Raw Text", st.session_state.transcript, height=200)

# 3. SEGMENTATION
if st.session_state.segments:
    st.divider()
    st.subheader("3️⃣ Topic Segmentation & Analysis")
    
    col_nav, col_content = st.columns([1, 3])
    
    with col_nav:
        st.markdown("**Topic List**")
        options = [s["label"] for s in st.session_state.segments]
        selected_label = st.radio("Select a Topic:", options, label_visibility="collapsed")
    
    selected_segment = next(s for s in st.session_state.segments if s["label"] == selected_label)
    
    with col_content:
        st.markdown(f"#### {selected_segment['label']}")
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            st.info(f"**Keywords**: {', '.join(selected_segment['keywords'])}")
        with m_col2:
            st.success(f"**Summary**: {selected_segment['summary']}")
            
        st.text_area("Segment Text", selected_segment["text"], height=250, key=f"txt_{selected_segment['id']}")
