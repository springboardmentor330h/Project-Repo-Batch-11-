import streamlit as st
import whisper
import os
import tempfile
import sys
import uuid
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from textblob import TextBlob
import re
import nltk

# Add parent directory to path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from topic_segmentation import TopicSegmenter
from audio_preprocessor import AudioPreprocessor
from sentiment_engine import SentimentAnalyzer

# -------------------- SETUP --------------------
st.set_page_config(
    page_title="EchoAI - Automated Podcast Transcription & Insights",
    layout="wide"
)

# -------------------- LOAD RESOURCES --------------------
@st.cache_resource
def load_whisper():
    return whisper.load_model("tiny")

@st.cache_resource
def load_modules():
    return TopicSegmenter(), AudioPreprocessor()

whisper_model = load_whisper()
segmenter, preprocessor = load_modules()
sentiment_analyzer = SentimentAnalyzer()

# -------------------- FUNCTIONS --------------------
def transcribe_audio(audio_path):
    result = whisper_model.transcribe(audio_path)
    return {
        "text": result["text"],
        "segments": result["segments"]
    }

def clean_text(text):
    cleaned = re.sub(r'\[.*?\]', '', text)
    cleaned = re.sub(r'\b\d{1,4}\b\s+\b\d{1,4}\b', '', cleaned)
    cleaned = re.sub(r'^\d+\s+', '', cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def analyze_sentiment(text):
    res = sentiment_analyzer.analyze(text)
    label = res["label"]
    score = res["score"]
    
    if label == "POSITIVE":
        color = "green"
    elif label == "NEGATIVE":
        color = "red"
    else:
        color = "orange"
    return label, score, color

def generate_wordcloud(keywords):
    if not keywords: return None
    word_freq = {word: len(keywords) - i for i, word in enumerate(keywords)}
    wc = WordCloud(background_color="white", width=800, height=400).generate_from_frequencies(word_freq)
    return wc.to_array()

def format_timestamp(seconds):
    if seconds is None: return "00:00"
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"

def generate_timeline(segments, selected_id=None):
    fig, ax = plt.subplots(figsize=(10, 2))
    if not segments: return fig
    total_duration = segments[-1]["end_time"]
    cmap = plt.get_cmap("tab20")
    for i, seg in enumerate(segments):
        start = seg["start_time"]
        width = seg["end_time"] - start
        color = cmap(i % 20)
        alpha = 1.0 if (selected_id is None or seg["id"] == selected_id) else 0.3
        ax.barh(0, width, left=start, height=0.5, color=color, alpha=alpha, edgecolor='white')
        if width > total_duration * 0.05:
            ax.text(start + width/2, 0, f"T{i+1}", ha='center', va='center', color='white', fontweight='bold', fontsize=8)
    ax.set_xlim(0, total_duration)
    ax.set_ylim(-0.5, 0.5)
    ax.axis('off')
    plt.tight_layout()
    return fig

def process_segments(transcript_data, algorithm="Embeddings (Advanced)"):
    text = transcript_data["text"]
    raw_segments = transcript_data["segments"]
    
    if algorithm == "Similarity (Fast)":
        segmented_texts = segmenter.segment_with_similarity(text)
    elif algorithm == "TextTiling (NLTK)":
        segmented_texts = segmenter.segment_with_texttiling(text)
    else:
        segmented_texts = segmenter.segment_with_embeddings(text)
    
    total_duration = raw_segments[-1]["end"] if raw_segments else 0.0
    segmented_texts = segmenter.enforce_topic_count(segmented_texts, duration=total_duration)
    
    processed = []
    current_raw_idx = 0
    for i, seg in enumerate(segmented_texts):
        content = clean_text(seg["text"])
        start_time = raw_segments[current_raw_idx]["start"] if current_raw_idx < len(raw_segments) else 0.0
        
        # Match content to end time
        accumulated = ""
        end_time = start_time
        while current_raw_idx < len(raw_segments):
            accumulated += " " + raw_segments[current_raw_idx]["text"].strip()
            end_time = raw_segments[current_raw_idx]["end"]
            current_raw_idx += 1
            if len(accumulated) >= len(content) * 0.85: break
        
        if i == len(segmented_texts) - 1: end_time = total_duration
        
        keywords = segmenter.extract_keywords(content)
        summary = segmenter.summarize(content, num_sentences=2) 
        sentiment_label, sentiment_score, sentiment_color = analyze_sentiment(content)
        topic_title = segmenter.generate_title(content, keywords)
        
        processed.append({
            "id": i,
            "label": f"Topic {i+1}: {topic_title}",
            "title": topic_title,
            "text": content,
            "keywords": keywords,
            "summary": summary,
            "sentiment_label": sentiment_label,
            "sentiment_score": sentiment_score,
            "sentiment_color": sentiment_color,
            "start_time": start_time,
            "end_time": end_time
        })
    return processed

# -------------------- UI --------------------
st.title("🎙️ EchoAI - Automated Podcast Transcription & Insights")

with st.sidebar:
    st.header("⚙️ Settings")
    algo_choice = st.selectbox("Segmentation Algorithm", 
        ["Embeddings (Advanced)", "TextTiling (NLTK)", "Similarity (Fast)"], index=0)

if 'transcript' not in st.session_state: st.session_state.transcript = None
if 'segments' not in st.session_state: st.session_state.segments = []

st.subheader("1️⃣ Audio Input")
uploaded_audio = st.file_uploader("Upload audio file (MP3 / WAV / M4A)", type=["mp3", "wav", "m4a"])

if uploaded_audio:
    st.audio(uploaded_audio)
    if st.button("🚀 Start Auto-Pipeline"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_audio.name.split('.')[-1]}") as tmp:
            tmp.write(uploaded_audio.getvalue())
            raw_path = tmp.name
        processed_path = raw_path + "_processed.wav"
        try:
            with st.spinner("Processing..."):
                preprocessor.process(raw_path, processed_path)
                st.success("Preprocessing Done.")
                raw_data = transcribe_audio(processed_path)
                st.session_state.transcript = clean_text(raw_data["text"])
                st.session_state.segments = process_segments(raw_data, algo_choice)
                st.success("Pipeline Completed Successfully!")
        except Exception as e:
            st.error(f"Error: {e}")
        finally:
            if os.path.exists(raw_path): os.remove(raw_path)
            if os.path.exists(processed_path): os.remove(processed_path)

if st.session_state.transcript:
    st.divider()
    st.subheader("📝 Full Transcription")
    with st.expander("📄 View Complete Transcript", expanded=False):
        st.text_area("Raw Text", st.session_state.transcript, height=200, label_visibility="collapsed")

    st.subheader("2️⃣ Analysis Timeline")
    selected_id = None
    if st.session_state.segments:
        if 'selected_topic_label' in st.session_state:
            try:
                selected_id = next(s["id"] for s in st.session_state.segments if s["label"] == st.session_state.selected_topic_label)
            except: pass
        fig = generate_timeline(st.session_state.segments, selected_id)
        st.pyplot(fig)
        plt.close(fig)

    if st.session_state.segments:
        st.divider()
        st.subheader("3️⃣ Topic Segmentation & Analysis")
        col_nav, col_content = st.columns([1, 3])
        with col_nav:
            st.markdown("**Topic List**")
            options = [s["label"] for s in st.session_state.segments]
            selected_label = st.radio("Select Topic", options, label_visibility="collapsed", key="selected_topic_label")
        
        selected_segment = next(s for s in st.session_state.segments if s["label"] == selected_label)
        
        with col_content:
            st.markdown(f"#### {selected_segment['label']} ({format_timestamp(selected_segment['start_time'])} – {format_timestamp(selected_segment['end_time'])})")
            st.markdown(f"**Duration: {format_timestamp(selected_segment['end_time'] - selected_segment['start_time'])}**")
            st.markdown(f"<span style='color:{selected_segment['sentiment_color']}; float:right;'>Sentiment Analysis: **{selected_segment['sentiment_label']} ({selected_segment['sentiment_score']})**</span>", unsafe_allow_html=True)
            st.divider()
            
            st.markdown("**Summary**")
            st.success(selected_segment['summary'])
            
            st.markdown("**Keywords**")
            kw_html = "".join([f"<span style='background-color: #f0f2f6; color: #31333f; padding: 4px 12px; border-radius: 16px; margin: 4px; display: inline-block; border: 1px solid #dfe1e5;'>{kw}</span>" for kw in selected_segment['keywords']])
            st.markdown(f"<div style='background-color: #f8f9fb; padding: 10px; border-radius: 8px;'>{kw_html}</div>", unsafe_allow_html=True)
            
            with st.expander("☁️ View Topic Word Cloud", expanded=True):
                wc_img = generate_wordcloud(selected_segment['keywords'])
                if wc_img is not None: st.image(wc_img, use_container_width=True)
            
            st.markdown("**Transcript**")
            st.text_area("Segment Text", selected_segment["text"], height=200, label_visibility="collapsed")

