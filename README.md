# 🎧 LEXARA: Automated Podcast Transcription & Insights

LEXARA is a powerful AI-driven platform that transforms raw audio content into structured, actionable insights. By leveraging advanced NLP models and real-time 3D visualization, it automates transcription, topic segmentation, title generation, and cross-language translation.

## 🚀 Key Features

### 1. **Intelligent Transcription**
-   Uses **OpenAI's Whisper Small** model (244M params) for high-accuracy speech-to-text.
-   **Native Language Transcription**: Automatically transcribes in the original language (Telugu, Hindi, Tamil, etc.) rather than translating to English.
-   **Manual Language Selection**: Override auto-detection when needed for songs with heavy background music.
-   Handles various accents, music, and audio conditions effectively.

### 2. **Topic Segmentation with Context-Aware Titles**
-   Automatically divides audio into coherent topic segments.
-   **Generates semantic topic titles** (max 8-10 words) for each segment.
-   Uses semantic analysis to detect topic shifts and speaker changes.
-   Topics are displayed in **chronological order** by start time.
-   Labels ambiguous boundaries as **UNKNOWN** for enterprise safety.

### 3. **Interactive Timeline Visualization**
-   **Horizontal Bar Graph**: Visualizes podcast segments as a proportional bar graph using **Matplotlib**.
-   **Color-Coded Segments**: Each topic has a distinct color for easy identification.
-   **Click-to-Navigate**: Select any topic button to view its full details.
-   **Time Markers**: Shows start/end times on the timeline axis.

### 4. **3D Animation Layer**
-   **Real-Time Visualization**: Represents podcast structure and topic flow in 3D.
-   **Animated Topic Nodes**: Each segment is a distinct 3D node/scene.
-   **Timestamp Synchronization**: Animations sync with transcript timestamps.
-   **Responsive Behavior**: Adapts dynamically as new segments are detected.
-   Powered by **Three.js** for WebGL rendering.

### 5. **Sentiment Analysis**
-   **Scaled Scoring**: Sentiment displayed on a user-friendly **1-10 scale**.
-   **Color-Coded Labels**: Positive (green), Neutral (orange), Negative (red).
-   Uses **TextBlob** for sentiment polarity detection.

### 6. **Abstractive Summarization**
-   Generates concise, human-readable summaries for each topic.
-   Follows a consistent *"This topic is about..."* format using **Flan-T5** and custom prompting.

### 7. **Multi-Language Translation**
-   **Supports 10+ Languages**: Including Telugu, Hindi, Tamil, Kannada, Malayalam, Bengali, Marathi, Urdu, Arabic, Russian, and more.
-   **Smart Chunking**: Handles long transcripts (>10,000 characters) without truncation.
-   Powered by **`deep-translator`** (Google Translate backend).

### 8. **Localization (Romanization)**
-   **Readable Script**: Converts non-English translations into readable English characters.
-   **Standardized Format**: Uses **IAST** via **`indic-transliteration`** for phonetically accurate readability.
-   **Dual Display**: Shows both original script and romanized text side-by-side.

### 9. **Large File Support**
-   Optimized for large podcast episodes.
-   Supports file uploads up to **4GB**.
-   Scalable to long-form audio (>2 hours).

### 10. **Keyword Word Clouds**
-   **Visual Keyword Representation**: Each topic displays a word cloud of its keywords.
-   **Importance-Based Sizing**: Keywords are sized based on TF-IDF importance.
-   Powered by **`wordcloud`** library.

---

## 📊 Output Formats

### Transcription_Output
```
- Segment_ID: seg_001
- Start_Time: 00:00
- End_Time: 02:45
- Topic_Title: "Introduction to Virtual Assistant Opportunities"
- Transcript_Text: "Welcome to today's episode..."
```

### 3D_Animation_Output
```
- Segment_ID: seg_001
- Animation_Type: topic_transition
- Animation_State: active
- Sync_Timestamp: 00:00
- Visual_Metadata: {node_color, node_size, position}
```

---

## 🛠️ Tech Stack

-   **Frontend**: [Streamlit](https://streamlit.io/)
-   **3D Visualization**: [Three.js](https://threejs.org/)
-   **Visualization**: [Matplotlib](https://matplotlib.org/)
-   **AI/ML Models**: 
    -   Transcription: `openai/whisper` (Medium model - 769M params)
    -   Summarization: `google/flan-t5-base`
    -   Translation: `deep-translator`
    -   Romanization: `indic-transliteration`
    -   Sentiment: `textblob`
    -   Embeddings: `sentence-transformers`
    -   Word Clouds: `wordcloud`
-   **Backend Logic**: Python

---

## 📦 Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/your-username/project-repo-batch-11.git
    cd project-repo-batch-11
    ```

2.  **Set Up Virtual Environment** (Recommended)
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\Activate
    
    # Mac/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```
    *Note: Ensure you have `ffmpeg` installed on your system for audio processing.*

4.  **Configuration** (Optional)
    -   Upload limits are configured in `.streamlit/config.toml`. Default is **4GB**.

---

## 🏃‍♂️ Usage

1.  **Run the Application**
    ```bash
    streamlit run ui/app.py
    ```

2.  **Upload Audio**
    -   Click "Browse files" and select your MP3 or WAV file.
    -   The app will display the file name and size.

3.  **Process Audio**
    -   Click **"🚀 Process Audio"**.
    -   The system will transcribe, segment, and generate topic titles. This may take a few minutes depending on file size.

4.  **Explore Insights**
    -   **Topics**: View segmented topics with context-aware titles, start/end times, and summaries.
    -   **3D Visualization**: Toggle the 3D view to see animated topic flow.
    -   **Transcript**: Read the full transcript or topic-specific segments.
    -   **Keywords**: See extracted key terms for each topic.

5.  **Translation & Romanization**
    -   Select a target language under the **Translation** section.
    -   Click **"Translate All Topics"** to see the text in target script.
    -   Click **"Romanize Translations"** for readable English version.

---

## 📁 Project Structure

```
├── .streamlit/             # Streamlit configuration
│   └── config.toml         # Upload limits, theme settings
├── config.json             # Security, UI, and animation configuration
├── data/                   # Storage for uploaded audio files
├── language_adaptation/    # Translation and Romanization modules
│   ├── translator.py       # Deep Translator logic with chunking
│   └── romanizer.py        # Indic Transliteration logic
├── outputs/                # JSON outputs (segments, transcripts)
├── pipeline/               # Core pipeline orchestration
│   └── pipeline_core.py    # Audio processing pipeline
├── topic_intelligence/     # Topic modeling and segmentation
│   ├── animation/          # 3D animation state generation
│   │   ├── animation_state.py
│   │   └── animation_schema.py
│   ├── output_schemas.py   # Structured output definitions
│   └── topic_segmentation/
│       ├── summaries.py    # Abstractive summarization
│       ├── topic_title_generator.py  # Context-aware titles
│       └── topic_segmentation_core.py
├── ui/                     # Streamlit frontend application
│   ├── app.py              # Main UI entry point
│   ├── components/         # UI components
│   └── visualization/      # 3D visualization HTML
│       └── 3d_visualization.html
└── requirements.txt        # Project dependencies
```

---

## 📋 Public Feedback

### Test Case 1: Music (Noise Environment Check)

| Metric | Result |
|--------|--------|
| **Name** | I wanna be you'r |
| **Genre** | Music |
| **Duration** | 4 mins |
| **Transcription Quality** | 10/10 (accurate lyrics) |
| **Topic Segmentation** | 2 segments |
| **Segment Durations** | 1:50, 1:16 |
| **Interactive Timestamp Bar** | ✅ Working |
| **Visual Bar Graph** | ✅ Working |
| **Summarization** | ✅ Perfect |
| **Keywords** | ✅ Good |
| **Word Cloud** | ✅ Working |
| **Translation** | ✅ Telugu translation working |
| **Localization** | ✅ Telugu tune with English letters working |
| **Overall Score** | **9/10** |

---

### Test Case 2: Political Podcast

| Metric | Result |
|--------|--------|
| **Name** | Broadcast-3PoliticallyPearShaped |
| **Genre** | Political Podcast |
| **Duration** | 10 mins |
| **Transcription Quality** | 10/10 |
| **Topic Segmentation** | 10 segments |
| **Segment Durations** | 1:11 \| 0:54 \| 1:15 \| ... |
| **Interactive Timestamp Bar** | ✅ Working |
| **Summarization** | ✅ Perfect |
| **Keywords** | ✅ Perfect |
| **Word Cloud** | ✅ Working |
| **Translation** | ✅ Working |
| **Localization** | ✅ Working |
| **Overall Score** | **10/10** |

---

### Test Case 3: Noise Environment (Edge Case)

| Metric | Result |
|--------|--------|
| **Name** | Crowd Talking |
| **Genre** | Noise (not a podcast) |
| **Duration** | 0 mins |
| **Transcription Quality** | No topics found |
| **Topic Segmentation** | No topics found |
| **Segment Durations** | No topics found |
| **Interactive Timestamp Bar** | No topics found |
| **Summarization** | No topics found |
| **Keywords** | No topics found |
| **Word Cloud** | No topics found |
| **Translation** | No topics found |
| **Localization** | No topics found |
| **Overall Score** | **N/A** (Expected behavior for noise) |

> **Note**: This test validates that the system correctly identifies and handles non-speech audio by gracefully reporting "No topics found" rather than producing false positives.

---

### Test Case 4: TED Talk

| Metric | Result |
|--------|--------|
| **Name** | Ted Talk |
| **Genre** | Business |
| **Duration** | 4 mins |
| **Transcription Quality** | 10/10 |
| **Topic Segmentation** | 3 segments |
| **Segment Durations** | 1:39 \| 1:34 \| 0:52 |
| **Interactive Timestamp Bar** | ✅ Working |
| **Summarization** | ✅ Perfect |
| **Keywords** | ✅ Good |
| **Word Cloud** | ✅ Working |
| **Translation** | ✅ Working |
| **Localization** | ✅ Working |
| **Overall Score** | **9/10** |

---

### Test Case 5: Audio Book

| Metric | Result |
|--------|--------|
| **Name** | Audio Book |
| **Genre** | Crime |
| **Duration** | 12 mins |
| **Transcription Quality** | 10/10 |
| **Topic Segmentation** | 10 segments |
| **Segment Durations** | 1:12 \| 1:04 \| 1:24 \| 1:12 \| 1:02 \| 1:05 \| 1:08 \| ... |
| **Interactive Timestamp Bar** | ✅ Working |
| **Summarization** | ✅ Perfect |
| **Keywords** | ✅ Good |
| **Word Cloud** | ✅ Working |
| **Translation** | ✅ Working |
| **Localization** | ✅ Working |
| **Overall Score** | **10/10** |

---

## 📊 Test Summary

| Content Type | Duration | Score |
|--------------|----------|-------|
| Music | 4 mins | 9/10 |
| Political Podcast | 10 mins | 10/10 |
| Noise (Edge Case) | 0 mins | N/A |
| TED Talk | 4 mins | 9/10 |
| Audio Book | 12 mins | 10/10 |

**Average Score (valid tests): 9.5/10** ✨

---

👤 Author

    Potheesh Vignesh K

    Role: Lead Developer

    Stack: Python, NLP, Streamlit, Three.js

⚡ Acknowledgements

    ChatGPT: For assistance with code optimization and documentation.

    Anti-Gravity: For keeping things light (and Pythonic).


Built with ❤️ and Python.
