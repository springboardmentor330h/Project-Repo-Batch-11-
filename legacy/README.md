# **🎧 AI Automated Podcast Transcription \& Topic Intelligence - Infosys SpringBoard**



An end-to-end local AI system that converts long podcast audio into clean English transcripts, intelligently segmented topics, and navigable transcript sections — all without using cloud APIs.

## 

## 🚀 Project Overview



Podcasts are rich in information but difficult to navigate once they exceed a few minutes.

This project solves that problem by transforming raw podcast audio into:



Structured transcripts with timestamps



Meaningful topic segments



Keywords and short summaries per topic



A navigation interface to jump directly to relevant content



The system is designed as a modular AI pipeline, suitable for research, demos, and real-world applications.



## 🎯 Core Objective



Automatically convert long podcast audio into accurate, topic-segmented English transcripts with timestamps, enabling fast navigation and understanding.



### 🧠 Key Features (What’s Implemented Now)

### 1️⃣ Speech-to-Text Transcription



Uses OpenAI Whisper (local, CPU-only)



Generates timestamped transcript segments



Supports long audio files (30–90 minutes)



### 2️⃣ Multilingual Normalization (Innovative Addition)



This is NOT standard Whisper usage — it is a custom enhancement.



#### 🔹 Automatic Translation to English



Implemented using MarianMT (Helsinki-NLP)



Converts non-English speech into English



Ensures all downstream NLP works on a single language



📁 Location:



language\_adaptation/translator.py



#### 🔹 Romanization Layer



Converts native scripts (Hindi, Telugu, etc.) into Roman English



Preserves pronunciation alongside translation



📁 Location:



language\_adaptation/romanizer.py





✅ This makes the system:



Language-aware



Search-friendly



More human-readable

### 

### 3️⃣ Topic Segmentation Engine (Week 3 – Core Work)



The transcript is divided into meaningful topics using multiple algorithms.



📁 Location:



topic\_segmentation/algorithms/



Implemented Algorithms

Algorithm	Description	Status

Algo 1	Sentence Similarity (SBERT)	✅

Algo 2	TextTiling (Lexical Cohesion)	✅

Algo 3	Embedding + Dynamic Threshold	✅

Algo 4	TF-IDF Drift Detection	✅

Algo 5	Hybrid Segmentation Engine	✅ (Default)

⭐ Hybrid Segmentation Engine (Final Choice)



Combines:



Sentence embeddings



TF-IDF drift



Minimum segment size



Smoothed boundaries



Produces human-reasonable topics instead of sentence-level noise.



### 4️⃣ Pre-Merge Short Segments (Important Fix)



Whisper outputs very short segments, which can cause over-segmentation.



✅ Solution:



Adjacent short segments are merged before topic segmentation



Based on duration and text length thresholds



📁 Location:



topic\_segmentation/utils/merge\_segments.py





This significantly improves topic coherence.



### 5️⃣ Keywords \& Topic Summaries



For each topic:



Top keywords extracted using TF-IDF



1–2 line summaries generated from topic content



Used for:



Navigation labels



Quick understanding



UI display

### 

### 6️⃣ Transcript Navigation \& Segment Jumping (Week 4)



Turns NLP output into a usable product.



📁 Location:



ui/transcript\_navigator.py



Current UI Features



Displays list of topics



Each topic shows keywords and summary



Clicking a topic displays its transcript text



Users can return to topic list and switch context



This acts like a table of contents for podcasts.



🔄 System Pipeline (Current)

Audio File (.mp3 / .wav)

&nbsp;       ↓

pipeline\_core.py

(Whisper + Translation + Romanization)

&nbsp;       ↓

pipeline\_output.json

&nbsp;       ↓

topic\_segmentation\_core.py

(Pre-merge + Segmentation + Keywords + Summaries)

&nbsp;       ↓

segmented\_output.json

&nbsp;       ↓

indexing\_core.py

&nbsp;       ↓

indexed\_output.json

&nbsp;       ↓

UI: Transcript Navigation



📂 Project Structure (Simplified)

Podcast\_AI\_Project/

│

├── pipeline\_core.py

├── pipeline\_runner.py

├── topic\_segmentation\_core.py

├── indexing\_core.py

│

├── language\_adaptation/

│   ├── translator.py

│   └── romanizer.py

│

├── topic\_segmentation/

│   ├── algorithms/

│   └── utils/

│

├── ui/

│   └── transcript\_navigator.py

│

├── data/

│   └── raw\_audio/

│

└── venv/



✅ What Is Fully Working



End-to-end pipeline (audio → indexed topics)



All 5 topic segmentation algorithms



Hybrid segmentation engine



Keyword extraction



Topic summaries



Transcript navigation UI



CPU-only execution



⚠️ Known Limitations (Non-Blocking)



Whisper segments are short

→ mitigated using pre-merge logic



Mixed-language detection is global

→ per-segment detection planned



CPU-only processing is slower

→ acceptable for demo \& research



🔮 Future Work \& Research Directions



Planned enhancements to make this research-grade:



Per-segment language detection using Whisper probabilities



Click-to-jump audio playback from UI



Algorithm comparison dashboard



Semantic search across transcripts



Abstractive topic summaries using LLMs



Speaker diarization



🎓 Why This Project Is Strong for Placements



Shows real system design, not just model usage



Demonstrates algorithm comparison \& hybrid reasoning



Includes custom NLP innovations



Bridges AI → NLP → UX



Easily explainable in interviews



🧑‍💻 Author



Potheesh Vignesh K

AI Software Developer \& Innovator Enthusiast

Project focused on applied AI systems, not toy demos.

