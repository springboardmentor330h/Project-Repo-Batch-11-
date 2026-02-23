# Lexara: AI that Understands Conversations

Lexara is a professional-grade podcast intelligence platform that transforms raw audio into structured, navigable intelligence.

## 🚀 The Lexara Refinement

We have moved beyond simple transcription to **Industrial Discourse Analysis**.

### 1. Conceptual Chapter Titling
- **QA-Driven Synthesis**: Our refined `Summarizer` now uses a **Question-Answering** strategy to distill complex segments into meaningful 2-4 word "Chapter Headings" (e.g., *"Campaign Clash Over Medicare"*, *"Social Security Strategy"*).
- **Professional Navigation**: These titles act as a high-level "Table of Contents" in the Lexara Dashboard, allowing users to jump directly to specific thematic discussion blocks.

### 2. Industry-Grade Segmentation
- **Coherent Chapters**: Refactored the SBERT segmentation service to enforce a strict minimum sentence count and semantic consistency, ensuring that each chapter is a complete, meaningful unit of discussion.
- **Noise Suppression**: The pipeline now merges conversational fillers and brief affirmations into the core topic chapters.

### 3. The Lexara Dashboard
- **Premium Branding**: A sleek, dark-mode interface powered by React and Framer Motion.
- **Library Explorer**: Browse full episodes and instantly view their "Topic Chapters" in the sidebar.
- **Deep Search**: Search across keywords and summaries to find exact moments in long-form podcasts.

## 📈 Technical Specs
- **AI Models**: SBERT (Segmentation), T5-Small (Summarization & Titling), Whisper (ASR).
- **Backend**: Flask API serving structured JSON disk data.
- **Frontend**: Vite + React with custom Glassmorphism CSS.

---
*Lexara — Spoken word, structured intelligence.*
