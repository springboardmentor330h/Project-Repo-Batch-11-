# Automated Podcast Transcription and Topic Segmentation

An industry-grade AI pipeline that transforms raw podcast audio into interactive, segmented, and summarized digital content. Built for high-efficiency content discovery and navigation.

## 🚀 Quick Start (Execution Guide)

To run the full stack, you will need to start the Backend and the Frontend simultaneously.

### 1. Prerequisites
- Python 3.10+
- Node.js & npm
- FFmpeg (for audio processing)

### 2. Backend Setup (Flask)
```bash
# Install Python dependencies
pip install -r requirements.txt

# Start the Flask API server
python app.py
```
*The API will be available at `http://localhost:5000`*

### 3. Frontend Setup (React)
```bash
cd frontend

# Install Node dependencies
npm install

# Start the React development server
npm run dev
```
*The Dashboard will be live at `http://localhost:3000`*

## 🛠️ Project Architecture

### Milestone 1 & 2: The AI Pipeline
- **Audio Preprocessing**: Automatic spectral gating noise reduction and RMS normalization using `Librosa` and `Noisereduce`.
- **Speech-to-Text**: High-accuracy transcription using **OpenAI Whisper (Base)**.
- **Topic Segmentation**: Advanced embedding-based segmentation using **SBERT (Sentence-BERT)** to detect natural thematic shifts.
- **Content Analysis**: Automated keyword extraction (**RAKE**) and abstractive summarization (**T5 Transformer**).

### Milestone 3: The User Interface
- **React Dashboard**: A modern, dark-mode interface built with **Vite**, **Tailwind CSS**, and **Framer Motion**.
- **Segment Jumping**: One-click navigation to specific topics within the transcript.
- **Global Search**: Cross-podcast indexing for instant keyword discovery.

## 📁 Directory Structure
- `src/`: Core logic for STT, Segmentation, and Summarization.
- `scripts/`: Data acquisition and exploration scripts.
- `data/segmented/`: Final processed intelligence files (JSON).
- `frontend/`: React application source code.
- `app.py`: Flask API entry point.

---
*Developed as an end-to-end industry submission for Podcast Audio Analysis.*
