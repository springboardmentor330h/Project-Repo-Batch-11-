import streamlit as st
import sys
import json
import subprocess
from pathlib import Path

# Set up project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
UI_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from language_adaptation.translator import translate_auto
from language_adaptation.romanizer import romanize_text

PIPELINE_OUTPUT = PROJECT_ROOT / "outputs" / "pipeline_output.json"
SEGMENTED_OUTPUT = PROJECT_ROOT / "outputs" / "segmented_output.json"

st.set_page_config(
    page_title="Podcast AI",
    page_icon="audio_spectrum",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if "processed_file" not in st.session_state:
    st.session_state.processed_file = None
if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = False

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
    }
    
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    .sub-header {
        background: #f0f4f8;
        color: #1a1a1a;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        font-weight: 500;
        border: 1px solid #cbd5e0;
    }
    
    .step-header {
        background: #e8eaf6;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 2rem 0 1.5rem 0;
        border-left: 5px solid #5c6bc0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }
    
    .step-header h2 {
        margin: 0;
        color: #3949ab;
        font-size: 1.8rem;
        font-weight: 700;
    }
    
    .transcript-box {
        background: #ffffff;
        padding: 2rem;
        border-radius: 12px;
        border-left: 5px solid #667eea;
        margin: 1.5rem 0;
        font-size: 1.1rem;
        line-height: 2;
        color: #212121;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        text-align: justify;
    }
    
    .topic-box {
        background: #ffffff;
        padding: 1.75rem;
        border-radius: 12px;
        border: 2px solid #e0e0e0;
        margin: 1.25rem 0;
        font-size: 1.05rem;
        line-height: 1.9;
        color: #212121;
        text-align: justify;
    }
    
    .translation-box {
        background: #e8f5e9;
        padding: 2rem;
        border-radius: 12px;
        border-left: 5px solid #4caf50;
        margin: 1.5rem 0;
        font-size: 1.1rem;
        line-height: 2;
        color: #212121;
        text-align: justify;
    }
    
    .localization-box {
        background: #fff3e0;
        padding: 2rem;
        border-radius: 12px;
        border-left: 5px solid #ff9800;
        margin: 1.5rem 0;
        font-size: 1.1rem;
        line-height: 2;
        color: #212121;
        text-align: justify;
    }
    
    .keyword-tag {
        display: inline-block;
        background: #1976d2;
        color: #ffffff;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        margin: 0.3rem;
        font-size: 0.9rem;
        font-weight: 600;
    }
    
    .metric-box {
        background: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        border: 2px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .metric-label {
        color: #666666 !important;
        font-size: 0.875rem;
        margin: 0;
    }
    
    .metric-value {
        color: #1a1a1a !important;
        font-size: 1.5rem;
        font-weight: 600;
        margin: 0.5rem 0 0 0;
    }
    
    /* Make file uploader background white */
    [data-testid="stFileUploader"] {
        background-color: #ffffff !important;
    }
    
    [data-testid="stFileUploader"] section {
        background-color: #ffffff !important;
    }
    
    [data-testid="stFileUploadDropzone"] {
        background-color: #ffffff !important;
        border: 2px dashed #e0e0e0 !important;
    }
    
    /* Make selectbox background white */
    [data-testid="stSelectbox"] {
        background-color: #ffffff !important;
    }
    
    [data-testid="stSelectbox"] > div {
        background-color: #ffffff !important;
    }
    
    [data-baseweb="select"] {
        background-color: #ffffff !important;
    }
    
    /* Browse files button text white */
    [data-testid="stFileUploader"] button {
        color: #ffffff !important;
    }
    
    [data-testid="stFileUploadDropzone"] button {
        color: #ffffff !important;
    }
    
    /* Make file uploader text VISIBLE (dark text) */
    [data-testid="stFileUploadDropzone"] {
        color: #1a1a1a !important;
    }
    
    [data-testid="stFileUploadDropzone"] span {
        color: #1a1a1a !important;
    }
    
    [data-testid="stFileUploadDropzone"] p {
        color: #1a1a1a !important;
    }
    
    [data-testid="stFileUploadDropzone"] small {
        color: #666666 !important;
    }
    
    [data-testid="stFileUploadDropzone"] div {
        color: #1a1a1a !important;
    }
    
    /* File uploader label text */
    [data-testid="stFileUploader"] label {
        color: #1a1a1a !important;
    }
    
    [data-testid="stFileUploader"] label span {
        color: #1a1a1a !important;
    }
    
    /* Make all text inside file uploader area visible */
    [data-testid="stFileUploader"] * {
        color: #1a1a1a !important;
    }
    
    /* But keep button text white */
    [data-testid="stFileUploader"] button,
    [data-testid="stFileUploader"] button * {
        color: #ffffff !important;
    }
    
    /* Fix expander text visibility */
    [data-testid="stExpander"] {
        background-color: #ffffff !important;
    }
    
    [data-testid="stExpander"] * {
        color: #1a1a1a !important;
    }
    
    [data-testid="stExpander"] summary {
        color: #1a1a1a !important;
    }
    
    [data-testid="stExpander"] summary span {
        color: #1a1a1a !important;
    }
    
    [data-testid="stExpander"] p,
    [data-testid="stExpander"] span,
    [data-testid="stExpander"] div {
        color: #1a1a1a !important;
    }
    
    /* Fix topic-box text */
    .topic-box {
        color: #1a1a1a !important;
    }
    
    .topic-box * {
        color: #1a1a1a !important;
    }
    
    /* Fix translation-box text */
    .translation-box {
        color: #1a1a1a !important;
    }
    
    .translation-box * {
        color: #1a1a1a !important;
    }
    
    /* Fix localization-box text */
    .localization-box {
        color: #1a1a1a !important;
    }
    
    .localization-box * {
        color: #1a1a1a !important;
    }
    
    /* Fix selectbox text visibility */
    [data-testid="stSelectbox"] * {
        color: #1a1a1a !important;
    }
    
    [data-testid="stSelectbox"] label {
        color: #1a1a1a !important;
    }
    
    [data-baseweb="select"] * {
        color: #1a1a1a !important;
    }
    
    /* Markdown headings inside expanders */
    [data-testid="stExpander"] h1,
    [data-testid="stExpander"] h2,
    [data-testid="stExpander"] h3,
    [data-testid="stExpander"] h4 {
        color: #1a1a1a !important;
    }
    
    /* Keyword tags should stay visible */
    .keyword-tag {
        color: #ffffff !important;
        background: #1976d2 !important;
    }

</style>
""", unsafe_allow_html=True)

LANGUAGES = {
    "English": "en",
    "Telugu": "te",
    "Hindi": "hi",
    "Tamil": "ta",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Bengali": "bn",
    "Marathi": "mr",
    "Urdu": "ur",
    "Arabic": "ar",
    "Russian": "ru",
}

st.markdown('<div class="main-header">Podcast AI</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Intelligent Audio Analysis | Topic Segmentation | Multi-Language Support</div>',
    unsafe_allow_html=True
)

st.markdown("""
<div style="background: #f8f9fa; padding: 1.25rem; border-radius: 12px; margin-bottom: 2rem; border: 1px solid #dee2e6;">
    <p style="margin: 0; color: #1a1a1a; font-size: 1rem; text-align: center; font-weight: 500;">
        Transform your audio content with AI-powered transcription, intelligent topic segmentation, and seamless translation.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

st.markdown('<div class="step-header"><h2> Upload Audio</h2></div>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    audio_file = st.file_uploader(
        "Upload your podcast audio file (MP3 or WAV)",
        type=["mp3", "wav"],
        help="Select an audio file to transcribe and analyze"
    )

if audio_file and st.session_state.processed_file != audio_file.name:
    st.session_state.processed_file = None
    st.session_state.data_loaded = False
    if PIPELINE_OUTPUT.exists():
        PIPELINE_OUTPUT.unlink()
    if SEGMENTED_OUTPUT.exists():
        SEGMENTED_OUTPUT.unlink()

with col2:
    if audio_file:
        st.markdown("""
        <div style="background: #d1fae5; padding: 1rem; border-radius: 10px; border-left: 4px solid #22c55e;">
            <p style="margin: 0; color: #065f46; font-weight: 600;">File Loaded</p>
            <p style="margin: 0.5rem 0 0 0; color: #047857; font-size: 0.95rem;">""" + audio_file.name + """</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-box" style="margin-top: 1rem;">
            <p class="metric-label">File Size</p>
            <p class="metric-value">{audio_file.size / 1024 / 1024:.2f} MB</p>
        </div>
        """, unsafe_allow_html=True)
if audio_file is None:
    # Reset state if user removes the file
    st.session_state.processed_file = None
    st.session_state.data_loaded = False
    
if audio_file:
    # Only verify we have the SAME file
    if st.session_state.processed_file != audio_file.name:
        # New file uploaded, different from the one we processed
        st.session_state.data_loaded = False
        
    audio_path = DATA_DIR / audio_file.name
    with open(audio_path, "wb") as f:
        f.write(audio_file.getbuffer())
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.audio(str(audio_path), format="audio/mp3")
    
    # Initialize processing state if needed
    if "processing" not in st.session_state:
        st.session_state.processing = False
    
    if st.button("🚀 Process Audio", type="primary", use_container_width=True):
        st.session_state.processing = True
    
    if st.session_state.processing:
        with st.spinner("Processing audio... This may take a few minutes."):
            try:
                # Step 1: Run pipeline_core for transcription
                st.info("Step 1/2: Transcribing audio...")
                result = subprocess.run(
                    [sys.executable, str(PROJECT_ROOT / "pipeline" / "pipeline_core.py"), str(audio_path)],
                    cwd=str(PROJECT_ROOT),
                    capture_output=True,
                    text=True,
                    timeout=600
                )
                
                if result.returncode != 0:
                    st.error(f"Pipeline error: {result.stderr}")
                    st.session_state.processing = False
                else:
                    # Step 2: Run topic segmentation directly as a module
                    st.info("Step 2/2: Segmenting topics...")
                    result2 = subprocess.run(
                        [sys.executable, "-m", "topic_intelligence.topic_segmentation.topic_segmentation_core", 
                         str(PIPELINE_OUTPUT)],
                        cwd=str(PROJECT_ROOT),
                        capture_output=True,
                        text=True,
                        timeout=300
                    )
                    
                    if result2.returncode != 0:
                        st.error(f"Segmentation error: {result2.stderr}")
                        st.session_state.processing = False
                    else:
                        st.session_state.processed_file = audio_file.name
                        st.session_state.data_loaded = True
                        st.session_state.processing = False
                        st.success("✅ Audio processed successfully!")
                        st.rerun()
                        
            except subprocess.TimeoutExpired:
                st.error("Processing timed out. Please try with a shorter audio file.")
                st.session_state.processing = False
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.session_state.processing = False

if not st.session_state.data_loaded:
    # Don't show old data if we haven't loaded data for CURRENT file
    if not audio_file:
         st.info("👋 Upload an audio file to get started!")
         st.stop()
    elif SEGMENTED_OUTPUT.exists() and st.session_state.processed_file == audio_file.name:
        # We have a file, and the output exists on disk AND matches current file name
        st.session_state.data_loaded = True
    else:
        # File uploaded but not processed yet
        st.stop()

try:
    with open(SEGMENTED_OUTPUT, "r", encoding="utf-8") as f:
        segmented_data = json.load(f)
except FileNotFoundError:
    st.warning("⚠️ No processed data found. Please upload and process an audio file.")
    st.stop()
except json.JSONDecodeError:
    st.error("❌ Error reading processed data. Please reprocess the audio file.")
    st.stop()

topics = segmented_data.get("topics", [])

if not topics:
    st.warning("⚠️ No topics found in the processed data.")
    st.stop()

full_transcript = " ".join(
    " ".join(s.get("text", "") for s in topic.get("sentences", []))
    for topic in topics
)

st.markdown("---")
st.markdown('<div class="step-header"><h2> Full Transcript</h2></div>', unsafe_allow_html=True)

if full_transcript:
    if full_transcript.strip():
        st.markdown(f'<div class="transcript-box">{full_transcript}</div>', unsafe_allow_html=True)
    else:
        st.warning("⚠️ Full transcript is empty.")
else:
    st.warning("⚠️ No transcript available.")

st.markdown("---")
st.markdown('<div class="step-header"><h2> Topic Segmentation</h2></div>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])
with col1:
    st.info(f"📊 **{len(topics)}** topics identified in this audio")
with col2:
    st.markdown(f"""
    <div class="metric-box">
        <p class="metric-label">Total Topics</p>
        <p class="metric-value">{len(topics)}</p>
        <p style="margin: 0.25rem 0 0 0; color: #10b981; font-size: 0.875rem;">Segmented</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

for idx, topic in enumerate(topics):
    with st.expander(f"📌 **Topic {idx + 1}** — {topic.get('summary', 'No summary')[:70]}...", expanded=(idx == 0)):
        
        start_time = topic.get("start", 0)
        end_time = topic.get("end", 0)
        duration = end_time - start_time
        
        st_str = f"{start_time:.1f}s"
        et_str = f"{end_time:.1f}s"
        dur_str = f"{duration:.1f}s"
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-box">
                <p class="metric-label">Start Time</p>
                <p class="metric-value">{st_str}</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-box">
                <p class="metric-label">End Time</p>
                <p class="metric-value">{et_str}</p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-box">
                <p class="metric-label">Duration</p>
                <p class="metric-value">{dur_str}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("### 📝 Summary")
        summary_text = topic.get('summary', 'No summary available')
        st.markdown(f'<div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; border-left: 3px solid #667eea; margin-bottom: 1.5rem; color: #1a1a1a; font-size: 1rem; text-align: justify;">{summary_text}</div>', unsafe_allow_html=True)
        
        keywords = topic.get("keywords", [])
        if keywords:
            st.markdown("### 🔑 Keywords")
            keyword_html = "".join([f'<span class="keyword-tag">{kw}</span>' for kw in keywords])
            st.markdown(f'<div style="margin-bottom: 1.5rem;">{keyword_html}</div>', unsafe_allow_html=True)
        
        st.markdown("### 📄 Transcript")
        sentences = topic.get("sentences", [])
        if sentences:
            topic_transcript = " ".join(s.get("text", "") for s in sentences)
            
            if topic_transcript.strip():
                st.markdown(f'<div class="topic-box">{topic_transcript}</div>', unsafe_allow_html=True)
            else:
                st.warning("⚠️ No transcript available for this topic.")
        else:
            st.warning("⚠️ No sentences found for this topic.")

st.markdown("---")
st.markdown('<div class="step-header"><h2> Translation</h2></div>', unsafe_allow_html=True)

st.markdown("""
<div style="background: #d1fae5; padding: 1.25rem; border-radius: 10px; margin-bottom: 1.5rem; border-left: 4px solid #22c55e;">
    <p style="margin: 0; color: #065f46; font-size: 1.05rem; font-weight: 600;">Translation Feature: Select a target language and translate all topic transcripts.</p>
</div>
""", unsafe_allow_html=True)

target_lang = st.selectbox(
    "Select Target Language",
    list(LANGUAGES.keys()),
    index=0
)

if st.button("Translate All Topics", type="primary"):
    with st.spinner("Translating..."):
        st.markdown("### Translated Transcripts (" + target_lang + ")")
        
        for idx, topic in enumerate(topics):
            sentences = topic.get("sentences", [])
            topic_text = " ".join(s.get("text", "") for s in sentences)
            
            if topic_text.strip():
                try:
                    translated = translate_auto(topic_text, "en", LANGUAGES[target_lang])
                    st.markdown(f"**Topic {idx + 1}:**")
                    st.markdown(f'<div class="translation-box">{translated}</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Translation error for Topic {idx + 1}: {str(e)}")

st.markdown("---")
st.markdown('<div class="step-header"><h2> Localization (Romanization)</h2></div>', unsafe_allow_html=True)

st.markdown("""
<div style="background: #fff3e0; padding: 1.25rem; border-radius: 10px; margin-bottom: 1.5rem; border-left: 4px solid #ff9800;">
    <p style="margin: 0; color: #e65100; font-size: 1.05rem; font-weight: 600;">Localization Feature: Convert translations to romanized text for easier reading.</p>
</div>
""", unsafe_allow_html=True)

if st.button("Romanize Translations", type="primary"):
    with st.spinner("Romanizing..."):
        st.markdown(f"### Romanized Transcripts ({target_lang})")
        
        for idx, topic in enumerate(topics):
            sentences = topic.get("sentences", [])
            topic_text = " ".join(s.get("text", "") for s in sentences)
            
            if topic_text.strip():
                try:
                    # Use the target_lang selected in the Translation section
                    translated = translate_auto(topic_text, "en", LANGUAGES[target_lang])
                    romanized = romanize_text(translated, LANGUAGES[target_lang])
                    
                    st.markdown(f"**Topic {idx + 1}:**")
                    st.markdown(f"""
                    <div style="margin-bottom: 1rem;">
                        <strong>Translation ({target_lang}):</strong>
                        <div class="translation-box" style="margin-top: 0.5rem;">{translated}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div>
                        <strong>Romanization:</strong>
                        <div class="localization-box" style="margin-top: 0.5rem;">{romanized}</div>
                    </div>
                    <hr style="margin: 2rem 0;">
                    """, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"Romanization error for Topic {idx + 1}: {str(e)}")

st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; color: #666666;">
    <p>Podcast AI</p>
    <p style="font-size: 0.875rem;">Powered by Whisper | Transformers | Streamlit</p>
</div>
""", unsafe_allow_html=True)
