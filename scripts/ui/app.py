import streamlit as st
import whisper
import os
import tempfile
import sys
import uuid
import matplotlib.pyplot as plt
from textblob import TextBlob
from wordcloud import WordCloud
import re

# Add parent directory to path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from topic_segmentation import TopicSegmenter
from audio_preprocessor import AudioPreprocessor

# -------------------- SETUP --------------------
st.set_page_config(
    page_title="EchoAI - Automated Podcast Transcription & Insights",
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
    # Return both full text and segments for timestamps
    return {
        "text": result["text"],
        "segments": result["segments"]
    }

def process_segments(transcript_data, algorithm="Similarity"):
    text = transcript_data["text"]
    raw_segments = transcript_data["segments"]
    
    # Select algorithm
    if algorithm == "Similarity (Fast)":
        segmented_texts = segmenter.segment_with_similarity(text)
    elif algorithm == "TextTiling (NLTK)":
        segmented_texts = segmenter.segment_with_texttiling(text)
    elif algorithm == "Embeddings (Advanced)":
        segmented_texts = segmenter.segment_with_embeddings(text)
    else:
        segmented_texts = segmenter.segment_with_similarity(text)
    
    # Enforce topic count adaptively based on audio length
    total_audio_duration = raw_segments[-1]["end"] if raw_segments else 0.0
    segmented_texts = segmenter.enforce_topic_count(segmented_texts, duration=total_audio_duration)
    
    # Map segmented texts back to timestamps
    processed = []
    current_raw_idx = 0
    
    for i, seg in enumerate(segmented_texts):
        content = seg["text"]
        
        # Determine start/end times
        start_time = None
        end_time = None
        
        if current_raw_idx < len(raw_segments):
            start_time = raw_segments[current_raw_idx]["start"]
            accumulated_text = ""
            while current_raw_idx < len(raw_segments):
                seg_text = raw_segments[current_raw_idx]["text"].strip()
                accumulated_text += " " + seg_text
                end_time = raw_segments[current_raw_idx]["end"]
                current_raw_idx += 1
                # Increase match sensitivity and ensure we don't skip too much
                if len(accumulated_text) >= len(content) * 0.85:
                    break
        
        # Ensure the last segment covers the end of the audio
        if i == len(segmented_texts) - 1:
            end_time = total_audio_duration

        # New Week 5 Analysis
        content = clean_text(content)
        keywords = segmenter.extract_keywords(content)
        raw_summary = segmenter.summarize(content)
        polished = polish_summary(raw_summary)
        sentiment_label, sentiment_score, sentiment_color = analyze_sentiment(content)
        
        # Generate context-aware title
        topic_title = segmenter.generate_title(content, keywords)
        
        processed.append({
            "id": i,
            "label": f"Topic {i+1}: {topic_title}",
            "title": topic_title,
            "text": content,
            "keywords": keywords,
            "summary": polished,
            "sentiment_label": sentiment_label,
            "sentiment_score": sentiment_score,
            "sentiment_color": sentiment_color,
            "start_time": start_time or 0.0,
            "end_time": end_time or 0.0
        })
    return processed

def generate_timeline(segments, selected_id=None):
    fig, ax = plt.subplots(figsize=(10, 2))
    
    # Calculate total duration
    if not segments:
        return fig
        
    total_duration = segments[-1]["end_time"]
    
    # Use a colormap
    cmap = plt.get_cmap("tab20")
    
    for i, seg in enumerate(segments):
        start = seg["start_time"]
        width = seg["end_time"] - start
        
        # Color: Highlight selected
        color = cmap(i % 20)
        alpha = 1.0 if (selected_id is None or seg["id"] == selected_id) else 0.3
        
        ax.barh(0, width, left=start, height=0.5, color=color, alpha=alpha, edgecolor='white')
        
        # Add label if space permits
        if width > total_duration * 0.05:
            ax.text(start + width/2, 0, f"T{i+1}", ha='center', va='center', color='white', fontweight='bold', fontsize=8)

    ax.set_xlim(0, total_duration)
    ax.set_ylim(-0.5, 0.5)
    ax.axis('off')
    plt.tight_layout()
    return fig

def format_timestamp(seconds):
    """
    Converts seconds to MM:SS format with leading zeros.
    """
    if seconds is None:
        return "UNKNOWN"
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"

def clean_text(text):
    """
    Cleans raw text to remove numeric artifacts and Whisper noise.
    """
    # Remove Whisper-specific noise artifacts like [Music], [Applause], or [00:00.000]
    cleaned = re.sub(r'\[.*?\]', '', text)
    # Remove repeated/stray Whisper artifacts (often short numbers like "2000 2000" or single digits at start)
    cleaned = re.sub(r'\b\d{1,4}\b\s+\b\d{1,4}\b', '', cleaned)
    cleaned = re.sub(r'^\d+\s+', '', cleaned, flags=re.MULTILINE)
    # General whitespace cleanup
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def analyze_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity  # -1.0 to 1.0
    
    # Scale -1.0..1.0 to 1..10
    score = round((polarity + 1) * 4.5 + 1, 1)
    
    if score <= 3.0:
        label = "NEGATIVE"
        color = "red"
    elif score <= 7.0:
        label = "NEUTRAL"
        color = "orange"
    else:
        label = "POSITIVE"
        color = "green"
        
    return label, score, color

def generate_wordcloud(keywords):
    if not keywords:
        return None
    # Use frequencies if keywords are just a list
    word_freq = {word: len(keywords) - i for i, word in enumerate(keywords)}
    wc = WordCloud(background_color="white", width=400, height=200).generate_from_frequencies(word_freq)
    return wc.to_array()

def polish_summary(summary):
    # Remove fillers
    fillers = [r"\buh\b", r"\bum\b", r"\byou know\b", r"\blike\b"]
    cleaned = summary
    for f in fillers:
        cleaned = re.sub(f, "", cleaned, flags=re.IGNORECASE)
    
    # Fix spacing and capitalization
    cleaned = cleaned.strip().capitalize()
    if not cleaned.endswith("."):
        cleaned += "."
        
    # Limit to 2-3 sentences (sent_tokenize is already in segmenter)
    sentences = segmenter.summarize(cleaned, num_sentences=3)
    return sentences

# -------------------- UI LAYOUT --------------------
st.title("🎙️ EchoAI - Automated Podcast Transcription & Insights")

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
                raw_transcript_data = transcribe_audio(processed_path)
                # Apply text cleaning to the full transcript
                cleaned_full_text = clean_text(raw_transcript_data["text"])
                st.session_state.transcript = cleaned_full_text
                # Keep raw segments for segmentation logic
                st.session_state.raw_transcript_data = {
                    "text": cleaned_full_text,
                    "segments": raw_transcript_data["segments"]
                }
            
            # Step 3: Segmentation
            with st.spinner("📌 Step 3: Performing Topic Segmentation..."):
                st.session_state.segments = process_segments(st.session_state.raw_transcript_data, algo_choice)
            
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
    st.subheader("2️⃣ Analysis Timeline")
    # Show interactive timeline
    selected_id = None
    if st.session_state.segments:
        # Find ID of selected radio option
        if 'selected_topic_label' in st.session_state:
            try:
                selected_id = next(s["id"] for s in st.session_state.segments if s["label"] == st.session_state.selected_topic_label)
            except StopIteration:
                pass
        
        fig = generate_timeline(st.session_state.segments, selected_id)
        st.pyplot(fig)
        plt.close(fig)

    st.subheader("📝 Full Transcription")
    with st.expander("📄 View Complete Transcript", expanded=False):
        st.text_area("Raw Text", st.session_state.transcript, height=200)

# 3. SEGMENTATION
if st.session_state.segments:
    st.divider()
    st.subheader("3️⃣ Topic Segmentation & Analysis")
    
    col_nav, col_content = st.columns([1, 3])
    
    with col_nav:
        st.markdown("**Topic List**")
        options = [s["label"] for s in st.session_state.segments]
        selected_label = st.radio("Select a Topic:", options, label_visibility="collapsed", key="selected_topic_label")
    
    selected_segment = next(s for s in st.session_state.segments if s["label"] == selected_label)
    
    with col_content:
        # 1. Topic Title & 2. Timestamp & Duration
        start_fmt = format_timestamp(selected_segment['start_time'])
        end_fmt = format_timestamp(selected_segment['end_time'])
        duration_sec = selected_segment['end_time'] - selected_segment['start_time']
        duration_fmt = format_timestamp(duration_sec)
        
        h_col1, h_col2 = st.columns([3, 1])
        with h_col1:
            st.markdown(f"#### Topic {selected_segment['id'] + 1}: {selected_segment['title']} ({start_fmt} – {end_fmt})")
            st.markdown(f"**Duration: {duration_fmt}**")
        with h_col2:
            st.markdown(f"<span style='color:{selected_segment['sentiment_color']}; font-weight:bold;'>{selected_segment['sentiment_label']} (Score: {selected_segment['sentiment_score']}/10)</span>", unsafe_allow_html=True)
            
        st.divider()
        
        # 3. Summary
        st.markdown("**Summary**")
        st.success(selected_segment['summary'])
            
        # 4. Keywords (Highlighted Box)
        st.markdown("**Keywords**")
        if selected_segment['keywords']:
            # Create a boxed container for keywords using custom CSS-like markdown
            kw_html = ""
            for kw in selected_segment['keywords']:
                kw_html += f"<span style='background-color: #f0f2f6; color: #31333f; padding: 4px 12px; border-radius: 16px; margin: 4px; display: inline-block; border: 1px solid #dfe1e5; font-weight: 500;'>{kw}</span>"
            
            st.markdown(
                f"<div style='background-color: #f8f9fb; border: 1px solid #e6e9ef; border-radius: 8px; padding: 16px; margin-bottom: 20px;'>{kw_html}</div>",
                unsafe_allow_html=True
            )
        else:
            st.info("No keywords identified for this segment.")

        # Optional: Word Cloud (Still valuable for visualization)
        with st.expander("☁️ View Topic Word Cloud", expanded=False):
            wc_img = generate_wordcloud(selected_segment['keywords'])
            if wc_img is not None:
                st.image(wc_img, use_container_width=True)

        # 5. Transcript
        st.markdown("**Transcript**")
        st.text_area("Segment Text", selected_segment["text"], height=250, key=f"txt_{selected_segment['id']}", label_visibility="collapsed")
