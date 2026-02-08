# EchoAI - Automated Podcast Transcription & Insights

**A production-ready tool for transforming raw audio into structured, searchable, and analyzed text with topical segments and sentiment insights.**

## Problem Statement
In the digital age, audio content (podcasts, meetings, lectures) is abundant but opaque. Searching for specific information within an hour-long audio file is time-consuming. Traditional transcription services often provide a wall of text without structure, making it difficult to identify key topics or navigate to relevant sections.

## Core Purpose
EchoAI exists to bridge the gap between raw audio and actionable knowledge. By automating transcription, topic segmentation, and sentiment analysis, it allows users to instantly navigate, understand, and extract value from long-form audio content.

## Target Users
- **Podcasters & Creators**: To generate show notes, chapters, and social media clips.
- **Researchers & Journalists**: To quickly find quotes and analyze sentiment in interviews.
- **Students & Educators**: To turn recorded lectures into structured study materials.
- **Business Professionals**: To archive and analyze meeting minutes.

---

## Key Features

### 1. Automated Transcription
- **What it does**: Converts speech to text using OpenAI's Whisper model.
- **Why**: Provides a high-accuracy text baseline for all downstream analysis.
- **Constraints**: Performance depends on hardware (CPU/GPU); "Tiny" model is used by default for speed.

### 2. Intelligent Topic Segmentation
- **What it does**: Automatically breaks down long transcripts into distinct topics using three selectable algorithms:
    - **Similarity (Fast)**: Uses TF-IDF and Cosine Similarity.
    - **TextTiling (NLTK)**: A classic NLP approach for text subdivision.
    - **Embeddings (Advanced)**: Uses Sentence-BERT (SBERT) for semantic understanding (requires higher compute).
- **Why**: Allows users to see "Chapters" of the conversation rather than a continuous wall of text.

### 3. Sentiment Analysis & Visualization
- **What it does**: Analyzes the emotional tone of each segment (Positive, Neutral, Negative) and provides a score (1-10).
- **Why**: Helps identify emotionally charged moments or conflict points in discussions.

### 4. Keyword Extraction & Word Clouds
- **What it does**: Identifies the most significant words in each segment and visualizes them.
- **Why**: Provides an at-a-glance summary of what a specific segment is about.

### 5. Interactive Timeline
- **What it does**: Renders a visual timeline of the audio, color-coded by topic.
- **Why**: Enables rapid navigation to specific parts of the audio file.

---

## System Capabilities

### What the System CAN Do
- Transcribe MP3, WAV, and M4A audio files.
- Denoise and normalize audio before processing to improve accuracy.
- Segment text based on semantic shifts in the conversation.
- Generate titles and summaries for each segment.
- Export structured data (visualized in UI).

### What the System CANNOT Do
- Real-time streaming transcription (it is a batch processing tool).
- Speaker Diarization (identifying *who* is speaking is not currently implemented).
- Translation (currently focused on English transcription).

### Intentional Limitations
- **Model Size**: Defaults to Whisper "Tiny" and "MiniLM" for compatibility with standard CPUs.
- **File Size**: Uploads are subject to Streamlit's default file limit (usually 200MB) unless configured otherwise.

---

## Architecture Overview

**Application Type**: Single Page Application (SPA) powered by Streamlit (Python).

### Data Flow
1.  **Input**: User uploads an audio file via the Streamlit UI.
2.  **Preprocessing**: `AudioPreprocessor` normalizes volume and reduces noise using `noisereduce`.
3.  **Processing**:
    -   **Whisper Engine**: Transcribes audio to raw text with timestamps.
    -   **TopicSegmenter**: Analyzes the text to find topic boundaries using the selected algorithm.
    -   **Analysis Engine**: Computes sentiment (`TextBlob`) and extracts keywords (`Scikit-learn`).
4.  **Output**: Interactive UI displays the timeline, transcript, and insights.

---

## Tech Stack

### Frontend
- **Framework**: [Streamlit](https://streamlit.io/)
- **Visualization**: [Matplotlib](https://matplotlib.org/) (Timeline), [WordCloud](https://github.com/amueller/word_cloud)

### Backend (Logic & Processing)
- **Language**: Python 3.8+
- **Audio Processing**: [Librosa](https://librosa.org/), [SoundFile](https://pysoundfile.readthedocs.io/), [Noisereduce](https://github.com/timsainb/noisereduce)
- **General Utilities**: NumPy, SciPy, Tqdm

### AI / ML
- **ASR (Speech-to-Text)**: [OpenAI Whisper](https://github.com/openai/whisper)
- **NLP & Segmentation**: [NLTK](https://www.nltk.org/), [Scikit-learn](https://scikit-learn.org/)
- **Embeddings**: [Sentence-Transformers](https://www.sbert.net/) (Hugging Face)
- **Sentiment**: [TextBlob](https://textblob.readthedocs.io/)

### Storage
- **Ephemeral**: Temporary files for audio processing.
- **Local**: `data/` directory for transcripts and segmented outputs (if running batch scripts).

---

## Installation & Setup

### Prerequisites
- **Python 3.8** or higher
- **FFmpeg**: Required for audio processing.
    - *Windows*: `choco install ffmpeg` or download binaries.
    - *Mac*: `brew install ffmpeg`
    - *Linux*: `sudo apt install ffmpeg`

### 1. Clone the Repository
```bash
git clone https://github.com/MydhiliAlladi/Project-Repo-Batch-11-.git
cd Project-Repo-Batch-11-
```

### 2. Create a Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Download NLTK Data (Optional - Auto-handled)
The application will attempt to download necessary NLTK data (`punkt`, `stopwords`) automatically. To do it manually:
```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
```

---

## Running the Project

### Start the Application
Execute the Streamlit app from the project root:

```bash
streamlit run scripts/ui/app.py
```

### Usage Steps
1.  Open the URL provided in the terminal (usually `http://localhost:8501`).
2.  **Upload Audio**: Drag and drop an MP3 or WAV file into the sidebar uploader.
3.  **Select Algorithm**: Choose between "Similarity", "TextTiling", or "Embeddings".
4.  **Start Pipeline**: Click "Start Auto-Pipeline".
5.  **Explore**:
    -   Click on timeline bars to jump to specific topics.
    -   View sentiment scores and keywords for each segment.
    -   Read the full transcript.

---

## Project Structure

```
Project-Repo-Batch-11-/
│
├── data/                   # Data storage for transcripts and audio
├── scripts/                # Core logic and processing scripts
│   ├── ui/                 # Frontend code
│   │   ├── app.py          # Main Streamlit Application entry point
│   │   └── verify_logic.py # UI Logic verification script
│   ├── audio_preprocessor.py # Denoising and normalization logic
│   ├── topic_segmentation.py # Core algorithms for segmentation
│   ├── transcribe.py       # Batch transcription script
│   └── ...                 # Helper utilities (split, merge, test)
│
├── requirements.txt        # Python dependency list
├── LICENSE                 # MIT License
└── README.md               # Project Documentation
```

---

## Security & Privacy Notes

- **Local Processing**: All audio processing, transcription, and analysis happen **locally** on your machine. No audio is sent to third-party cloud APIs.
- **Data Retention**: Uploaded files are stored in temporary directories and are processed in-session. They are not permanently stored unless specifically configured in batch scripts.
- **Privacy**: Because it runs locally, it is suitable for processing sensitive or private internal meetings.

---

## Limitations & Known Constraints

- **Performance**: Transcription speed is directly proportional to your CPU/GPU power. On older CPUs, transcribing an hour of audio may take 10-20 minutes.
- **Memory Usage**: The "Embeddings" segmentation algorithm loads a Transformer model into memory, which requires ~1GB RAM.
- **Speaker Identification**: The system treats the audio as a single stream of speech; it does not distinguish between different speakers.

---

## Author / Maintainer

**Name**: springboardmentor330h
**Role**: Lead Developer
**Tech Focus**: NLP, Audio Processing, Streamlit Development

---

## Acknowledgements

- **OpenAI**: For the Whisper model.
- **Streamlit**: For the rapid application development framework.
- **NLTK & Scikit-learn Builders**: For the foundational NLP tools.
