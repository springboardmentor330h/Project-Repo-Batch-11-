# 🎧 Podcast AI - Intelligent Audio Analysis Platform

Podcast AI is a powerful tool designed to transform raw audio content into structured, actionable insights. By leveraging advanced AI models, it automates the process of transcribing, segmenting, summarizing, and translating podcast episodes, making content accessible across language barriers.

## 🚀 Key Features

### 1. **Intelligent Transcription**
-   Uses **OpenAI's Whisper** model for high-accuracy speech-to-text conversion.
-   Handles various accents and audio conditions effectively.

### 2. **Topic Segmentation**
-   Automatically divides long audio files into coherent segments/topics.
-   Uses semantic analysis to detect topic shifts, allowing for easy navigation through the content.

### 3. **Abstractive Summarization**
-   Generates concise, human-readable summaries for each topic.
-   Follows a consistent *"This topic is about..."* format using **Flan-T5** and custom prompting.

### 4. **Multi-Language Translation**
-   **Supports 10+ Languages**: Including Telugu, Hindi, Tamil, Kannada, Malayalam, Bengali, Marathi, Urdu, Arabic, Russian, and more.
-   **Smart Chunking**: Handles long transcripts (>10,000 characters) without truncation or errors by intelligently splitting text.
-   Powered by **`deep-translator`** (Google Translate backend) for reliable accuracy.

### 5. **Localization (Romanization)**
-   **Readable Script**: Converts non-English translations (like Telugu or Hindi script) into readable English characters (Romanized).
-   **Standardized Format**: Uses **IAST** (International Alphabet of Sanskrit Transliteration) via **`indic-transliteration`** for phonetically accurate readability (e.g., *namaskāraṃ* instead of *nmskr*).
-   **Dual Display**: Shows both the original translated script and the romanized text side-by-side.

### 6. **Large File Support**
-   Optimized for large podcast episodes.
-   Supports file uploads up to **4GB**.
-   Visual file size indicator.

---

## 🛠️ Tech Stack

-   **Frontend**: [Streamlit](https://streamlit.io/)
-   **AI/ML Models**: 
    -   Transcription: `openai/whisper`
    -   Summarization: `google/flan-t5-base`
    -   Translation: `deep-translator`
    -   Romanization: `indic-transliteration`
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
    -   The system will transcribe, segment, and summarize the content. This may take a few minutes depending on file size.

4.  **Explore Insights**
    -   **Topics**: View segmented topics with start/end times and summaries.
    -   **Transcript**: Read the full transcript or topic-specific segments.
    -   **Keywords**: See extracted key terms for each topic.

5.  **Translation & Romanization**
    -   Select a target language (e.g., Telugu) under the **Translation** section.
    -   Click **"Translate All Topics"** to see the text in the target script.
    -   Click **"Romanize Translations"** to see the readable English version of the translation.

---

## 📁 Project Structure

```
├── data/                   # Storage for uploaded audio files
├── language_adaptation/    # Translation and Romanization modules
│   ├── translator.py       # Deep Translator logic with chunking
│   └── romanizer.py        # Indic Transliteration logic
├── outputs/                # JSON outputs (segments, transcripts)
├── pipeline/               # Core pipeline orchestration
├── topic_intelligence/     # Topic modeling and segmentation
│   └── topic_segmentation/
│       ├── summaries.py    # Abstractive summarization
│       └── ...
├── ui/                     # Streamlit frontend application
│   └── app.py              # Main UI entry point
└── requirements.txt        # Project dependencies
```

👤 Author

    Potheesh Vignesh K

    Role: Lead Developer

    Stack: Python, NLP, Streamlit

⚡ Acknowledgements

    ChatGPT: For assistance with code optimization and documentation.

    Anti-Gravity: For keeping things light (and Pythonic).

    Open Source Community: For the amazing libraries (transformers, whisper, deep-translator).

Built with ❤️ and Python.
