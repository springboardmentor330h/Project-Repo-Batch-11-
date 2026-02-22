import streamlit as st
import sys
import json
import subprocess
import io
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
from wordcloud import WordCloud

# Set up project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
UI_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

# Detect venv Python path (for subprocess calls)
VENV_PYTHON = PROJECT_ROOT / "venv" / "Scripts" / "python.exe"
if not VENV_PYTHON.exists():
    # Fallback to sys.executable if venv not found
    VENV_PYTHON = Path(sys.executable)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from language_adaptation.translator import translate_auto
from language_adaptation.romanizer import romanize_text
from textblob import TextBlob

PIPELINE_OUTPUT = PROJECT_ROOT / "outputs" / "pipeline_output.json"
SEGMENTED_OUTPUT = PROJECT_ROOT / "outputs" / "segmented_output.json"
CONFIG_FILE = PROJECT_ROOT / "config.json"


def generate_wordcloud(keywords, topic_id=None):
    """
    Generate a word cloud image from existing keywords for a specific topic.
    Uses keyword position to determine weight (earlier keywords = higher weight).
    
    Args:
        keywords: List of keyword strings from topic data
        topic_id: Topic number for labeling the word cloud
    
    Returns:
        BytesIO image buffer or None if no keywords
    """
    if not keywords or len(keywords) == 0:
        return None
    
    # Create frequency dict based on keyword position
    # First keyword gets highest weight, decreasing for subsequent keywords
    word_freq = {}
    for i, keyword in enumerate(keywords):
        # Weight: first keyword = len(keywords), last = 1
        weight = len(keywords) - i
        word_freq[keyword] = weight
    
    try:
        # Generate word cloud with dark text for visibility
        wc = WordCloud(
            width=600,
            height=250,
            background_color='white',
            colormap='viridis',
            max_words=50,
            min_font_size=10,
            max_font_size=70,
            prefer_horizontal=0.9
        ).generate_from_frequencies(word_freq)
        
        # Create figure with title for topic label
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.imshow(wc, interpolation='bilinear')
        ax.axis('off')
        
        # Add topic label as title
        if topic_id is not None:
            ax.set_title(f"Topic {topic_id} - Keyword Word Cloud", fontsize=14, fontweight='bold', pad=10, color='#333333')
        
        plt.tight_layout()
        
        # Convert to image bytes
        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format='PNG', dpi=100, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        img_buffer.seek(0)
        return img_buffer
    except Exception:
        return None

# Load configuration
def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        # Return default configuration
        return {
            "security": {
                "max_file_size_mb": 100,
                "allowed_file_types": [".mp3", ".wav"],
                "enable_input_sanitization": True
            },
            "ui": {
                "max_topics_display": 50
            }
        }

CONFIG = load_config()

st.set_page_config(
    page_title="LEXARA",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if "processed_file" not in st.session_state:
    st.session_state.processed_file = None
if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = False
if "selected_topic" not in st.session_state:
    st.session_state.selected_topic = None

st.markdown("""
<style>
    /* === ADAPTIVE UI STYLING === */
    
    /* Base app background */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
    }
    
    /* === DARK BOX STYLING (HIGHEST PRIORITY) === */
    /* Black background boxes with WHITE text */
    .content-box,
    .transcript-box,
    .topic-box,
    .info-box,
    .metric-box,
    .step-header,
    .sub-header {
        background: #1a1a1a !important;
        color: #ffffff !important;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 1px solid #333333;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    
    /* WHITE text for ALL children inside dark boxes - HIGHEST SPECIFICITY */
    .stApp .content-box,
    .stApp .content-box *,
    .stApp .content-box p,
    .stApp .content-box span,
    .stApp .content-box h1,
    .stApp .content-box h2,
    .stApp .content-box h3,
    .stApp .transcript-box,
    .stApp .transcript-box *,
    .stApp .transcript-box p,
    .stApp .transcript-box span,
    .stApp .topic-box,
    .stApp .topic-box *,
    .stApp .topic-box p,
    .stApp .topic-box span,
    .stApp .info-box,
    .stApp .info-box *,
    .stApp .info-box p,
    .stApp .info-box span,
    .stApp .metric-box,
    .stApp .metric-box *,
    .stApp .metric-box p,
    .stApp .metric-box span,
    .stApp .step-header,
    .stApp .step-header *,
    .stApp .step-header h2,
    .stApp .sub-header,
    .stApp .sub-header * {
        color: #ffffff !important;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #cccccc !important;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 1.4rem;
        font-weight: 700;
        color: #ffffff !important;
    }
    
    /* === LIGHT BACKGROUND AREAS (DEFAULT) === */
    /* Black text on light backgrounds - LOWER PRIORITY */
    .stApp .stMarkdown,
    .stApp .element-container,
    .stApp p,
    .stApp span,
    .stApp label,
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
    [data-testid="stMarkdownContainer"] {
        font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }
    
    /* === BUTTONS === */
    .stButton button {
        color: #ffffff !important;
    }
    
    /* === KEYWORD TAGS === */
    .keyword-tag {
        display: inline-block;
        background: #2196F3;
        color: #ffffff !important;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        margin: 0.3rem;
        font-size: 0.9rem;
        font-weight: 600;
    }
    
    /* === SENTIMENT COLORS (white text) === */
    .sentiment-positive { 
        background-color: #4CAF50; 
        color: #ffffff !important;
    }
    .sentiment-neutral { 
        background-color: #FF9800; 
        color: #ffffff !important;
    }
    .sentiment-negative { 
        background-color: #F44336; 
        color: #ffffff !important;
    }
    
    /* === SEGMENT BLOCKS === */
    .segment-block {
        height: 40px;
        border-radius: 6px;
        margin: 5px 2px;
        display: inline-block;
        cursor: pointer;
        text-align: center;
        line-height: 40px;
        color: #ffffff !important;
        font-weight: 500;
        font-size: 12px;
    }
    
    /* === MAIN HEADER === */
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
    
    /* === TRANSLATION BOX === */
    .translation-box {
        background: #1a1a1a !important;
        padding: 2rem;
        border-radius: 12px;
        border-left: 5px solid #4caf50;
        margin: 1.5rem 0;
        font-size: 1.1rem;
        line-height: 2;
        color: #ffffff !important;
        text-align: justify;
    }
    
    .stApp .translation-box,
    .stApp .translation-box * {
        color: #ffffff !important;
    }
    
    .localization-box {
        background: #1a1a1a !important;
        padding: 2rem;
        border-radius: 12px;
        border-left: 5px solid #ff9800;
        margin: 1.5rem 0;
        font-size: 1.1rem;
        line-height: 2;
        color: #ffffff !important;
        text-align: justify;
    }
    
    .stApp .localization-box,
    .stApp .localization-box * {
        color: #ffffff !important;
    }
    
    .keyword-tag {
        display: inline-block;
        background: #1976d2;
        color: #ffffff !important;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        margin: 0.3rem;
        font-size: 0.9rem;
        font-weight: 600;
    }
    
    /* === EXPANDER STYLING (Fix Text Overlap) === */
    /* Ensure expander headers render as block-level elements */
    [data-testid="stExpander"] {
        margin-bottom: 1rem;
    }
    
    [data-testid="stExpander"] summary {
        display: flex !important;
        align-items: center !important;
        padding: 0.75rem 1rem !important;
        font-weight: 500 !important;
        line-height: 1.5 !important;
        white-space: normal !important;
        word-wrap: break-word !important;
    }
    
    [data-testid="stExpander"] summary span {
        display: inline-block !important;
        position: relative !important;
    }
    
    /* Topic container spacing */
    [data-testid="stExpander"] > div {
        padding: 1rem !important;
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

    /* === EXPAND/COLLAPSE SYMBOL REPLACEMENT === */
    /* Hide ALL default Streamlit expander icons (SVG, Material Icons text, icon spans) */
    [data-testid="stExpander"] summary svg,
    [data-testid="stExpander"] summary [data-testid="stIconMaterial"],
    [data-testid="stExpander"] summary .material-icons,
    [data-testid="stExpander"] summary [class*="icon"],
    [data-testid="stExpander"] details summary svg,
    [data-testid="stExpander"] header svg,
    [data-testid="stExpanderToggleIcon"] {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        height: 0 !important;
        overflow: hidden !important;
        font-size: 0 !important;
    }
    
    /* Inject ▼ for expanded state */
    [data-testid="stExpander"][open] summary::before,
    details[open] > summary::before {
        content: "▼ " !important;
        font-size: 0.9rem;
        margin-right: 0.25rem;
        font-family: sans-serif !important;
    }
    
    /* Inject ▶ for collapsed state */
    [data-testid="stExpander"]:not([open]) summary::before,
    details:not([open]) > summary::before {
        content: "▶ " !important;
        font-size: 0.9rem;
        margin-right: 0.25rem;
        font-family: sans-serif !important;
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

st.markdown('<div class="main-header">🎧 LEXARA</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Automated Podcast Transcription & Insights | 3D Visualization | Multi-Language Support</div>',
    unsafe_allow_html=True
)

st.markdown("""
<div style="background: #f8f9fa; padding: 1.25rem; border-radius: 12px; margin-bottom: 2rem; border: 1px solid #dee2e6;">
    <p style="margin: 0; color: #1a1a1a; font-size: 1rem; text-align: center; font-weight: 500;">
        Transform your audio content with AI-powered transcription, context-aware topic titles, and interactive 3D visualization.
    </p>
</div>
""", unsafe_allow_html=True)

def format_duration(seconds):
    """Convert seconds to MM:SS format"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


def get_sentiment_color(sentiment):
    """Get color class for sentiment"""
    if sentiment == "POSITIVE":
        return "sentiment-positive"
    elif sentiment == "NEGATIVE":
        return "sentiment-negative"
    else:
        return "sentiment-neutral"


def render_timeline(data):
    """Render interactive timeline visualization as a matplotlib horizontal bar graph"""
    if not data or "topics" not in data:
        st.error("ERROR_STATE: No timeline data available")
        return
    
    # === CRITICAL: Sort topics by start time to ensure chronological order ===
    topics = sorted(data["topics"], key=lambda t: t.get("start", 0))
    
    if not topics:
        st.error("ERROR_STATE: No topics found")
        return
    
    # Assign deterministic display IDs based on sorted order
    for idx, topic in enumerate(topics):
        topic["_display_id"] = idx + 1
    
    # Get total duration
    total_duration = max(topic.get("end", 0) for topic in topics)
    if total_duration <= 0:
        st.error("ERROR_STATE: Invalid timeline data - no valid duration found")
        return
    
    # Segment colors (data-driven)
    SEGMENT_COLORS = ['#2196F3', '#4CAF50', '#FF9800', '#9C27B0', '#00BCD4', '#E91E63', '#3F51B5', '#009688']
    
    st.markdown("<h3 style='color:#000000;'>Interactive Timeline</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:#000000;'>Click a topic button below to view details</p>", unsafe_allow_html=True)
    
    # === MATPLOTLIB BAR GRAPH VISUALIZATION ===
    fig, ax = plt.subplots(figsize=(14, 1.5))
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#e0e0e0')
    
    # Calculate minimum width needed for text (about 5% of total duration)
    min_label_width = total_duration * 0.05
    
    # Draw each topic segment as a horizontal bar (in sorted order)
    for i, topic in enumerate(topics):
        topic_display_id = topic.get("_display_id", i + 1)
        start = topic.get("start", 0)
        end = topic.get("end", 0)
        duration = end - start
        color = SEGMENT_COLORS[i % len(SEGMENT_COLORS)]
        
        # Draw the bar segment
        ax.barh(y=0, width=duration, left=start, height=0.5, color=color, edgecolor='white', linewidth=0.5)
        
        # Only add label if segment is wide enough to avoid overlap
        if duration >= min_label_width:
            mid_point = start + duration / 2
            ax.text(mid_point, 0, f"T{topic_display_id}", ha='center', va='center', fontsize=8, fontweight='bold', color='white')
    
    # Configure axes
    ax.set_xlim(0, total_duration)
    ax.set_ylim(-0.5, 0.5)
    ax.set_yticks([])
    ax.set_xlabel("Time (seconds)", fontsize=10, color='#000000')
    ax.tick_params(axis='x', colors='#000000')
    
    # Add time markers
    ax.set_xticks([0, total_duration / 4, total_duration / 2, 3 * total_duration / 4, total_duration])
    ax.set_xticklabels([format_duration(0), format_duration(total_duration / 4), 
                        format_duration(total_duration / 2), format_duration(3 * total_duration / 4),
                        format_duration(total_duration)])
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    plt.tight_layout()
    
    # Render the figure using st.pyplot (NOT raw code)
    st.pyplot(fig)
    plt.close(fig)
    
    # === LEGEND ===
    st.markdown("<p style='color:#000000; font-weight:bold;'>Legend:</p>", unsafe_allow_html=True)
    legend_cols = st.columns(min(len(topics), 4))
    for i, topic in enumerate(topics):
        topic_display_id = topic.get("_display_id", i + 1)
        col_idx = i % min(len(topics), 4)
        start = topic.get("start", 0)
        end = topic.get("end", 0)
        with legend_cols[col_idx]:
            color = SEGMENT_COLORS[i % len(SEGMENT_COLORS)]
            st.markdown(f"<span style='display:inline-block;width:12px;height:12px;background:{color};border-radius:2px;margin-right:6px;'></span><span style='color:#000000;'>Topic {topic_display_id} ({format_duration(start)} - {format_duration(end)})</span>", unsafe_allow_html=True)
    
    # === TOPIC SELECTION BUTTONS ===
    st.markdown("<p style='color:#000000; font-weight:bold;'>Select a topic:</p>", unsafe_allow_html=True)
    cols = st.columns(len(topics))
    for i, (col, topic) in enumerate(zip(cols, topics)):
        topic_display_id = topic.get("_display_id", i + 1)
        with col:
            is_selected = (st.session_state.selected_topic == i)
            btn_type = "primary" if is_selected else "secondary"
            if st.button(f"Topic {topic_display_id}", key=f"topic-select-btn-{i}", type=btn_type, width='stretch'):
                st.session_state.selected_topic = i
                st.rerun()
    
    # Display selected topic details
    if st.session_state.selected_topic is not None and 0 <= st.session_state.selected_topic < len(topics):
        selected_topic = topics[st.session_state.selected_topic]
        st.markdown("---")
        display_topic_details(selected_topic)


def sanitize_input(text):
    """Basic input sanitization"""
    if not text:
        return ""
    # Remove potentially dangerous characters
    return str(text).replace("<", "&lt;").replace(">", "&gt;")


def scale_sentiment_score(polarity_score):
    """
    Convert sentiment polarity score to 1-10 scale
    Input range: -1.0 to +1.0
    Output range: 1 to 10
    Formula: scaled = ((polarity + 1) / 2) * 9 + 1
    """
    try:
        polarity = float(polarity_score)
        # Clamp to valid range
        polarity = max(-1.0, min(1.0, polarity))
        # Scale from [-1, 1] to [1, 10]
        scaled = ((polarity + 1) / 2) * 9 + 1
        return round(scaled, 1)
    except (ValueError, TypeError):
        return "UNKNOWN"


def display_topic_details(topic):
    """Display detailed information for a selected topic with security measures"""
    # Use _display_id for consistent labeling (falls back to topic_id + 1)
    topic_display_id = topic.get("_display_id", topic.get("topic_id", 0) + 1)
    st.markdown(f"<h3 style='color:#000000;'>Topic {topic_display_id}</h3>", unsafe_allow_html=True)
    
    # Summary with sanitization
    st.markdown("<p style='color:#000000; font-weight:bold;'>Summary</p>", unsafe_allow_html=True)
    summary = sanitize_input(topic.get("summary", "No summary available"))
    st.markdown(f"<div class='transcript-box'>{summary}</div>", unsafe_allow_html=True)
    
    # Keywords with sanitization
    keywords = topic.get("keywords", [])
    if keywords:
        st.markdown("<p style='color:#000000; font-weight:bold;'>Keywords</p>", unsafe_allow_html=True)
        keyword_html = ""
        for keyword in keywords:
            safe_keyword = sanitize_input(keyword)
            keyword_html += f"<span class='keyword-tag'>{safe_keyword}</span>"
        st.markdown(keyword_html, unsafe_allow_html=True)
    
    # Sentiment with 1-10 scaling
    if "sentiment" in topic and topic["sentiment"]:
        sentiment = topic["sentiment"]
        raw_score = topic.get("sentiment_score", 0)
        scaled_score = scale_sentiment_score(raw_score)
        color_class = get_sentiment_color(sentiment)
        st.markdown(f"<p style='color:#000000;'><strong>Sentiment:</strong> <span class='{color_class}'>{sentiment}</span> (Score: {scaled_score}/10)</p>", unsafe_allow_html=True)
    
    # Full text with sanitization
    st.markdown("<p style='color:#000000; font-weight:bold;'>Transcript</p>", unsafe_allow_html=True)
    full_text = sanitize_input(topic.get("text", ""))
    st.markdown(f"<div class='transcript-box'>{full_text}</div>", unsafe_allow_html=True)

st.markdown("---")

st.markdown('<div class="step-header"><h2> Upload Audio</h2></div>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    max_size = CONFIG["security"]["max_file_size_mb"] * 1024 * 1024
    
    audio_file = st.file_uploader(
        f"Upload your podcast audio file (MP3 or WAV, max {CONFIG['security']['max_file_size_mb']}MB)",
        type=["mp3", "wav"],
        help="Select an audio file to transcribe and analyze"
    )
    
    # File size validation
    if audio_file and audio_file.size > max_size:
        st.error(f"❌ File too large! Maximum size is {CONFIG['security']['max_file_size_mb']}MB. Your file is {audio_file.size / 1024 / 1024:.1f}MB.")
        audio_file = None

if audio_file and st.session_state.processed_file != audio_file.name:
    st.session_state.processed_file = None
    st.session_state.data_loaded = False
    # Clean up old outputs (with error handling)
    try:
        if PIPELINE_OUTPUT.exists():
            PIPELINE_OUTPUT.unlink()
    except PermissionError:
        pass  # File in use, skip cleanup
    try:
        if SEGMENTED_OUTPUT.exists():
            SEGMENTED_OUTPUT.unlink()
    except PermissionError:
        pass  # File in use, skip cleanup

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
    
    # Language selection for transcription
    st.markdown("<br>", unsafe_allow_html=True)
    source_languages = {
        "auto": "🔍 Auto-Detect (Default)",
        "en": "🇬🇧 English",
        "te": "🇮🇳 Telugu (తెలుగు)",
        "hi": "🇮🇳 Hindi (हिंदी)",
        "ta": "🇮🇳 Tamil (தமிழ்)",
        "ml": "🇮🇳 Malayalam (മലയാളം)",
        "kn": "🇮🇳 Kannada (ಕನ್ನಡ)",
        "bn": "🇮🇳 Bengali (বাংলা)",
        "mr": "🇮🇳 Marathi (मराठी)",
        "gu": "🇮🇳 Gujarati (ગુજરાતી)",
        "pa": "🇮🇳 Punjabi (ਪੰਜਾਬੀ)",
        "ur": "🇵🇰 Urdu (اردو)",
        "ar": "🇸🇦 Arabic (العربية)",
        "ru": "🇷🇺 Russian (Русский)",
        "zh": "🇨🇳 Chinese (中文)",
        "ja": "🇯🇵 Japanese (日本語)",
        "ko": "🇰🇷 Korean (한국어)",
    }
    selected_source_lang = st.selectbox(
        "🎤 Source Language (Select if auto-detect fails)",
        options=list(source_languages.keys()),
        format_func=lambda x: source_languages[x],
        index=0,
        help="Select the language spoken in the audio. Use this if auto-detect gives wrong results."
    )
    
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
                    [str(VENV_PYTHON), str(PROJECT_ROOT / "pipeline" / "pipeline_core.py"), str(audio_path), selected_source_lang],
                    cwd=str(PROJECT_ROOT),
                    capture_output=True,
                    text=True
                    # No timeout - allow unlimited time for model download + processing
                )
                
                if result.returncode != 0:
                    st.error(f"Pipeline error: {result.stderr}")
                    st.session_state.processing = False
                else:
                    # Step 2: Run topic segmentation directly as a module
                    st.info("Step 2/2: Segmenting topics...")
                    result2 = subprocess.run(
                        [str(VENV_PYTHON), "-m", "topic_intelligence.topic_segmentation.topic_segmentation_core", 
                         str(PIPELINE_OUTPUT)],
                        cwd=str(PROJECT_ROOT),
                        capture_output=True,
                        text=True
                        # No timeout for segmentation
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

# === CRITICAL: Sort topics by start time to ensure chronological order ===
# This prevents mixed/out-of-order topic rendering
topics = sorted(topics, key=lambda t: t.get("start", 0))

# Assign deterministic topic IDs based on sorted order
for idx, topic in enumerate(topics):
    topic["_display_id"] = idx + 1  # 1-indexed for display

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
st.markdown('<div class="step-header"><h2>Interactive Timeline</h2></div>', unsafe_allow_html=True)

# Display interactive timeline
render_timeline(segmented_data)

# === 3D VISUALIZATION SECTION ===
st.markdown("---")
st.markdown('<div class="step-header"><h2>🎬 3D Topic Visualization</h2></div>', unsafe_allow_html=True)

st.markdown("""
<div style="background: #e3f2fd; padding: 1.25rem; border-radius: 10px; margin-bottom: 1.5rem; border-left: 4px solid #2196F3;">
    <p style="margin: 0; color: #1565c0; font-size: 1.05rem; font-weight: 600;">Interactive 3D View: Explore topic flow with animated nodes and connections.</p>
</div>
""", unsafe_allow_html=True)

# Initialize 3D toggle state
if '3d_enabled' not in st.session_state:
    st.session_state['3d_enabled'] = False

col_3d_1, col_3d_2 = st.columns([1, 4])
with col_3d_1:
    if st.button("🔮 Toggle 3D View", type="primary"):
        st.session_state['3d_enabled'] = not st.session_state['3d_enabled']
        st.rerun()

with col_3d_2:
    status = "ON ✅" if st.session_state['3d_enabled'] else "OFF ⭕"
    st.markdown(f"<p style='color:#333333; padding-top: 0.5rem;'>3D Visualization: <strong>{status}</strong></p>", unsafe_allow_html=True)

if st.session_state['3d_enabled']:
    # Load animation data from segmented output
    animation_data = segmented_data.get("3D_Animation_Output", [])
    
    if animation_data:
        import streamlit.components.v1 as components
        import json
        
        # Read and inject the 3D visualization HTML
        viz_html_path = UI_DIR / "visualization" / "3d_visualization.html"
        try:
            with open(viz_html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Inject animation data
            data_script = f"<script>window.animationData = {json.dumps(animation_data)};</script>"
            html_content = html_content.replace('</head>', f'{data_script}</head>')
            
            components.html(html_content, height=500, scrolling=False)
            
            # Show animation summary
            total_duration = sum(d.get('Visual_Metadata', {}).get('duration', 0) for d in animation_data)
            st.markdown(f"<p style='color:#333333; text-align: center;'>📊 {len(animation_data)} topic nodes | ⏱️ Total duration: {total_duration:.0f}s</p>", unsafe_allow_html=True)
        except FileNotFoundError:
            st.warning("3D visualization file not found. Please ensure the installation is complete.")
    else:
        st.info("No animation data available. Re-process audio to generate 3D visualization.")


st.markdown("---")
st.markdown('<div class="step-header"><h2> Topic Segmentation</h2></div>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])
with col1:
    st.info(f"**{len(topics)}** topics identified in this audio")
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
    # Use the deterministic _display_id for consistent labeling
    topic_display_id = topic.get("_display_id", idx + 1)
    topic_start = topic.get("start", 0)
    topic_end = topic.get("end", 0)
    topic_duration = topic_end - topic_start
    # Get topic title (new LEXARA feature)
    topic_title = topic.get('topic_title', f'Topic {topic_display_id}')
    topic_summary = topic.get('summary', 'No summary available')
    
    # Create unique key for this topic container based on sorted index
    topic_key = f"topic_container_{idx}"
    
    # Expander header with topic title
    time_range = f"{format_duration(topic_start)} - {format_duration(topic_end)}"
    expander_title = f"{topic_title}  |  {time_range}"
    
    with st.expander(expander_title, expanded=(idx == 0)):
        # === TOPIC CONTAINER START ===
        # All content below is bound to this specific topic
        
        # 1. TIME METRICS
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-box">
                <p class="metric-label">Start Time</p>
                <p class="metric-value">{format_duration(topic_start)}</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-box">
                <p class="metric-label">End Time</p>
                <p class="metric-value">{format_duration(topic_end)}</p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-box">
                <p class="metric-label">Duration</p>
                <p class="metric-value">{format_duration(topic_duration)}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 2. SUMMARY
        st.markdown("### Summary")
        st.markdown(f'<div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; border-left: 3px solid #667eea; margin-bottom: 1.5rem; color: #1a1a1a; font-size: 1rem; text-align: justify;">{topic_summary}</div>', unsafe_allow_html=True)
        
        # 3. SENTIMENT (with 1-10 scaling)
        if "sentiment" in topic and topic["sentiment"]:
            sentiment = topic["sentiment"]
            raw_score = topic.get("sentiment_score", 0)
            scaled_score = scale_sentiment_score(raw_score)
            color_class = get_sentiment_color(sentiment)
            st.markdown("### Sentiment Analysis")
            st.markdown(f'<div class="{color_class}" style="padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem; text-align: center; font-weight: 600;">{sentiment} (Score: {scaled_score}/10)</div>', unsafe_allow_html=True)
        
        # 4. KEYWORDS
        keywords = topic.get("keywords", [])
        if keywords:
            st.markdown("### Keywords")
            keyword_html = "".join([f'<span class="keyword-tag">{kw}</span>' for kw in keywords])
            st.markdown(f'<div style="margin-bottom: 1.5rem;">{keyword_html}</div>', unsafe_allow_html=True)
            
            # 4.1 WORD CLOUD (uses existing keywords only - separate for each topic)
            st.markdown(f"### Topic {topic_display_id} - Word Cloud")
            wordcloud_img = generate_wordcloud(keywords, topic_id=topic_display_id)
            if wordcloud_img:
                st.image(wordcloud_img, width='stretch')
            else:
                st.info("Unable to generate word cloud for this topic.")
        
        # 5. TRANSCRIPT
        st.markdown("### Transcript")
        sentences = topic.get("sentences", [])
        if sentences:
            topic_transcript = " ".join(s.get("text", "") for s in sentences)
            
            if topic_transcript.strip():
                st.markdown(f'<div class="topic-box">{topic_transcript}</div>', unsafe_allow_html=True)
            else:
                st.warning("⚠️ No transcript available for this topic.")
        else:
            st.warning("⚠️ No sentences found for this topic.")
        
        # === TOPIC CONTAINER END ===

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
            topic_display_id = topic.get("_display_id", idx + 1)
            sentences = topic.get("sentences", [])
            topic_text = " ".join(s.get("text", "") for s in sentences)
            
            if topic_text.strip():
                try:
                    translated = translate_auto(topic_text, "en", LANGUAGES[target_lang])
                    st.markdown(f"**Topic {topic_display_id}:**")
                    st.markdown(f'<div class="translation-box">{translated}</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Translation error for Topic {topic_display_id}: {str(e)}")

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
            topic_display_id = topic.get("_display_id", idx + 1)
            sentences = topic.get("sentences", [])
            topic_text = " ".join(s.get("text", "") for s in sentences)
            
            if topic_text.strip():
                try:
                    # Use the target_lang selected in the Translation section
                    translated = translate_auto(topic_text, "en", LANGUAGES[target_lang])
                    romanized = romanize_text(translated, LANGUAGES[target_lang])
                    
                    st.markdown(f"**Topic {topic_display_id}:**")
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
                    st.error(f"Romanization error for Topic {topic_display_id}: {str(e)}")

st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; color: #666666;">
    <p><strong>🎧 LEXARA</strong>: Automated Podcast Transcription & Insights</p>
    <p style="font-size: 0.875rem;">Powered by Whisper | Transformers | Three.js | Streamlit</p>
    <p style="font-size: 0.75rem; margin-top: 0.5rem;">
        © 2026 / Author: Potheesh Vignesh K.™
    </p>
</div>
""", unsafe_allow_html=True)
