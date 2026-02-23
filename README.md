# 🎙️ AudioInsight
### AI-Powered Podcast Transcription & Analysis Pipeline

> An end-to-end system that takes raw audio and produces fully searchable transcripts, auto-detected topics, keyword summaries, sentiment analysis, and analytics — built with Whisper, TextTiling NLP, and Streamlit.

---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [How to Run](#how-to-run)
- [Pipeline Explained](#pipeline-explained)
- [Configuration & Settings](#configuration--settings)
- [Output & Downloads](#output--downloads)
- [Module Reference](#module-reference)
- [Requirements](#requirements)
- [Known Issues & Tips](#known-issues--tips)

---

## Project Overview

AudioInsight is an 8-week AI capstone project that automates the full lifecycle of podcast analysis:

1. Upload or download an audio file
2. Preprocess the audio (noise reduction, chunking)
3. Transcribe using OpenAI Whisper
4. Clean the transcript (remove fillers, merge sentences)
5. Segment into topics using TextTiling NLP
6. Extract keywords using TF-IDF
7. Generate summaries per topic
8. Compute analytics (WPM, readability, sentiment, vocabulary)
9. Visualise everything in an interactive Streamlit dashboard

The system supports multiple segmentation algorithms and includes an evaluation framework to compare their performance.

---

## Features

| Feature | Description |
|---|---|
| 🎤 Whisper Transcription | Multi-model support: tiny, base, small, medium, large |
| 🗂️ Topic Segmentation | TextTiling NLP with configurable block size |
| 🔑 Keyword Extraction | TF-IDF with bigram support, filler word filtering |
| 📝 Auto Summaries | TextRank-lite extractive summarisation per topic |
| 💭 Sentiment Analysis | Timeline chart using TextBlob |
| ☁️ Word Cloud | Visual frequency map of most-used terms |
| 📊 Analytics | WPM, readability scores, vocabulary diversity |
| 🔍 Transcript Search | Keyword search with timestamp and topic labels |
| 📥 Export | Plain text, timestamped, topics report, full JSON |
| 🔗 URL Download | Fetch audio directly from a URL |

---

## Project Structure

```
Audio_Transcription_Project/
│
├── src/                          # All source code
│   ├── app.py                    # Streamlit web application (main entry point)
│   │
│   ├── audio_preprocessing.py    # Audio cleaning, noise reduction, chunking
│   ├── transcribe.py             # Whisper ASR transcription engine
│   ├── trancript_cleaner.py      # Sentence merging & filler word removal
│   │
│   ├── algorithim.py             # Algorithm 1: Cosine similarity segmentation
│   ├── algorithim2.py            # Algorithm 2: TextTiling segmentation (used in app)
│   ├── algorithim3.py            # Algorithm 3: Embedding-based segmentation
│   │
│   ├── evaluate.py               # SegmentationEvaluator, KeywordExtractor, SummaryGenerator
│   ├── analytics.py              # TranscriptAnalytics: WPM, readability, sentiment
│   ├── compare.py                # Side-by-side algorithm comparison
│   │
│   ├── url_downloader.py         # Download audio from URL with retry logic
│   ├── download_audio.py         # Bulk CSV-based audio downloader
│   ├── data_storage.py           # Local transcript storage and indexing
│   └── setup.py                  # Environment setup and dependency check
│
├── output/                       # Generated transcripts and analysis results
│   ├── topics/
│   ├── transcripts/
│   └── transcripts_cleaned/
│
├── dataset/                      # Raw audio files
├── venv/                         # Python virtual environment
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

---

## Installation

### 1. Clone / Download the project

```bash
cd Audio_Transcription_Project
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Install system dependency (FFmpeg)

FFmpeg is required by Whisper to decode audio files.

**Windows:**
```bash
winget install ffmpeg
# or download from https://ffmpeg.org/download.html and add to PATH
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt install ffmpeg
```

### 5. (Optional) Install extras

```bash
# For word cloud in Analytics tab
pip install wordcloud matplotlib

# For readability scores
pip install textstat

# For sentiment analysis
pip install textblob
python -m textblob.download_corpora
```

---

## How to Run

```bash
# Make sure your virtual environment is active
cd src
streamlit run app.py
```

The app will open at `http://localhost:8501` in your browser.

---

## Pipeline Explained

```
Audio File
    │
    ▼
┌─────────────────────┐
│  1. Preprocess      │  Noise reduction, normalisation, chunking into segments
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│  2. Transcribe      │  Whisper ASR converts speech to text with timestamps
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│  3. Clean           │  Merge Whisper segments into sentences, remove filler words
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│  4. Segment         │  TextTiling detects topic boundaries by lexical cohesion
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│  5. Keywords        │  TF-IDF extracts meaningful keywords per topic segment
│     & Summaries     │  TextRank-lite generates a 2-sentence summary per topic
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│  6. Analytics       │  WPM, vocabulary diversity, readability, sentiment timeline
└─────────────────────┘
    │
    ▼
  Dashboard (Streamlit)
```

### How TextTiling Works

TextTiling segments text by measuring **lexical cohesion** between blocks of sentences. When vocabulary shifts significantly between adjacent blocks, it signals a topic boundary. The **block size** slider in the sidebar controls how many sentences per block — smaller = more sensitive, more topics detected.

- **Block size 3–5** → High sensitivity, many topics (best for varied podcasts)
- **Block size 6–12** → Balanced (good default)
- **Block size 13–20** → Low sensitivity, fewer broad topics (best for focused talks)

---

## Configuration & Settings

All settings are available in the **sidebar** of the app before running the pipeline.

| Setting | Options | Description |
|---|---|---|
| **Whisper Model** | tiny, base, small, medium, large | Larger = better accuracy, slower |
| **Audio Language** | en, es, fr, de, ... auto | Language of the audio. `auto` = Whisper detects it |
| **Topic Sensitivity** | Slider 3–20 | Block size for TextTiling. Smaller = more topics |

### Model Speed vs. Accuracy

| Model | Speed | Accuracy | Best For |
|---|---|---|---|
| tiny | ⚡ Fastest | Basic | Quick testing |
| base | ✅ Fast | Good | General use (recommended) |
| small | 🔍 Medium | Better | Higher accuracy |
| medium | 🎯 Slow | High | Professional use |
| large | 💎 Very slow | Best | Maximum quality |

---

## Output & Downloads

After analysis, five tabs are available:

| Tab | Contents |
|---|---|
| 📄 Transcript | Full colour-coded transcript with topic sections and timestamps |
| 📚 Topics & Summaries | Topic cards with summaries, keywords, duration, sentiment |
| 📈 Analytics | Word cloud, top words bar chart, WPM, readability, sentiment timeline, topic split pie chart |
| 🔍 Search | Keyword search across the full transcript with highlighted results |
| 📥 Download | Export in 4 formats (see below) |

### Export Formats

| File | Contents |
|---|---|
| `_transcript.txt` | Plain text transcript, no timestamps |
| `_timestamped.txt` | Every sentence with `[MM:SS]` timecode |
| `_topics.txt` | Topics, keywords and summaries in readable format |
| `_report.json` | Full structured data — all topics, analytics, evaluation scores |

---

## Module Reference

### `audio_preprocessing.py` — `AudioPreprocessor`
Handles noise reduction, audio normalisation and chunking of long files into manageable segments. Outputs processed `.wav` files and chunk metadata with start times.

### `transcribe.py` — `AudioTranscriber`
Wraps OpenAI Whisper. Loads the model once, transcribes each chunk, and returns segments with corrected timestamps using chunk offset metadata.

### `trancript_cleaner.py` — `TranscriptCleaner`
Merges short Whisper segments into full sentences. Removes filler words (`um`, `uh`, `like`, `you know`, etc.) in conservative or aggressive mode.

### `algorithim2.py` — `TextTilingSegmenter`
Main segmentation algorithm used in the app. Implements TextTiling:
- Builds vocabulary blocks from sentences
- Computes lexical cohesion scores between adjacent blocks
- Smooths scores and detects valleys as topic boundaries
- Provides `get_topic_label()` and `analyze_sentiment()` helpers

### `evaluate.py` — `SegmentationEvaluator`, `KeywordExtractor`, `SummaryGenerator`

**SegmentationEvaluator**: Scores segmentation quality (0–10) based on topic count, duration balance, and sentence distribution. Provides human-readable feedback.

**KeywordExtractor**: TF-IDF with bigrams (`ngram_range=(1,2)`), filler word blocklist of 60+ terms, `sublinear_tf=True`. Falls back to frequency-based extraction for single-segment audio.

**SummaryGenerator**: TextRank-lite extractive summariser. Scores sentences by keyword density, position bonus, and length. Filters out sign-off lines (`"thanks for listening"`, `"see you next week"`, etc.).

### `analytics.py` — `TranscriptAnalytics`
Computes:
- **Basic**: word count, sentence count, duration
- **Speaking**: WPM, average sentence duration, pause time
- **Vocabulary**: unique words, diversity ratio, hapax legomena, top 10 words
- **Readability**: Flesch-Kincaid Grade, Flesch Reading Ease, Gunning Fog (requires `textstat`)
- **Sentiment**: polarity timeline using TextBlob

### `url_downloader.py` — `URLDownloader`
Downloads audio from direct URLs with retry logic, MIME type validation, and progress callbacks. Supports MP3, WAV, M4A, FLAC, OGG, WEBM.

### `compare.py`
Runs all three segmentation algorithms on the same transcript and compares results side by side — useful for evaluating which algorithm performs best on different audio types.

### `data_storage.py`
Lightweight local database for storing and indexing transcription results. Supports search, export, and cleanup. Uses metadata/data separation for fast listing.

---

## Requirements

```
streamlit
openai-whisper
torch
librosa
soundfile
noisereduce
pyloudnorm
sentence-transformers
scikit-learn
nltk
textblob
textstat
plotly
pandas
requests
wordcloud
matplotlib
```

Full list in `requirements.txt`.

**System:** FFmpeg must be installed and available on `PATH`.

---

## Known Issues & Tips

**Only 1 topic detected?**
Reduce the Topic Sensitivity slider in the sidebar to 3–5 and re-run. This is the most common issue with short audio files.

**Pipeline is slow?**
Use the `tiny` or `base` Whisper model for testing. Larger models can take 5–10× longer.

**Word cloud not showing?**
Install: `pip install wordcloud matplotlib`

**Readability scores missing?**
Install: `pip install textstat`

**Sentiment timeline empty?**
Install: `pip install textblob` then run `python -m textblob.download_corpora`

**File upload limit?**
Streamlit's default upload limit is 200 MB. For larger files, use the URL downloader or increase the limit in `.streamlit/config.toml`:
```toml
[server]
maxUploadSize = 500
```

**Typo in filename `trancript_cleaner.py`?**
Yes — this is intentional. The filename is preserved as-is to avoid breaking imports across the project.

---

## Tech Stack

| Component | Technology |
|---|---|
| UI Framework | Streamlit |
| Speech-to-Text | OpenAI Whisper |
| Topic Segmentation | TextTiling (custom implementation) |
| Keyword Extraction | scikit-learn TF-IDF |
| Sentiment Analysis | TextBlob |
| Visualisation | Plotly, Matplotlib, WordCloud |
| Audio Processing | librosa, noisereduce, soundfile |
| Embeddings (Algo 3) | sentence-transformers (MiniLM) |

---

*AudioInsight — AI Automated Podcast Transcription · Capstone Project*
