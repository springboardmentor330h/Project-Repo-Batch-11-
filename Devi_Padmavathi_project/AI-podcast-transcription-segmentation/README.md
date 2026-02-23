 # Talk2Topics

### AI-Powered Podcast Transcription & Topic Segmentation System

An end-to-end intelligent pipeline that converts long podcast audio into structured, searchable knowledge using speech recognition and NLP.  
It automatically detects topics, extracts keywords, generates summaries, and enables easy navigation across podcast content.

---

## Project Overview

### Problem Statement
Long podcasts contain valuable information but are difficult to search, skim, or navigate. Users often need to listen to entire episodes to find specific discussions.



### Objectives
- Convert audio podcasts into structured text  
- Automatically detect topic boundaries  
- Generate concise summaries per topic  
- Extract meaningful keywords  
- Provide an interactive navigation interface  



### Significance
Long-form audio content is rapidly growing, but most platforms still treat podcasts as linear media that must be consumed sequentially. This project demonstrates how artificial intelligence can transform passive audio into structured, searchable knowledge.

By converting speech into semantically organized information, the system reduces cognitive load, improves information accessibility, and enables users to interact with spoken content the same way they interact with text — through scanning, searching, and navigation.

### Applications
The system can be applied across multiple real-world domains:

- Education — fast review of lectures and learning content  
- Research — quick extraction of relevant discussions  
- Media Analysis — topic tracking and content indexing  
- Knowledge Management — searchable spoken archives

---

## Dataset Description

- Source: TED Talks audio dataset
- Language: English
- Audio Format: MP3 → converted to WAV
- Total Podcasts Processed: 10
- Duration Range: 30 minutes – 63 minutes

**Preprocessing Performed**

- Format conversion
- Audio normalization
- Mono conversion
- Silence trimming
- Chunking for ASR processing

---

## System Architecture

![System Architecture](assets/architecture.png)

---

### System Pipeline Explanation

#### Audio Input
The system accepts raw podcast audio files and prepares them for processing.

#### Audio Preprocessing
Audio is cleaned, normalized, converted to mono if required, and divided into chunks to improve transcription performance.

#### Speech-to-Text Transcription
The processed audio is converted into text using a speech recognition model that generates timestamped transcripts.

#### Sentence Splitting
The transcript is divided into individual sentences to enable detailed semantic analysis.

#### Topic Segmentation
Sentences are grouped into coherent topic segments using semantic similarity techniques.

#### Keyword Extraction
Important keywords are extracted from each segment to represent its core idea.

#### Summarization
Each segment is summarized to provide a concise understanding of the discussion.

#### Sentiment Analysis
The emotional tone of each segment is analyzed to provide contextual insights.

#### Structured Output
All results are organized into a structured format for easy reading, searching, and navigation.

---

## Tools & Technologies Used

**Audio Processing**

- PyDub — format conversion and normalization
- LibROSA — waveform analysis and audio handling

**Speech Recognition**

- Whisper — high-accuracy transcription with timestamps

**Natural Language Processing**

- Sentence Transformers — semantic embeddings
- TF-IDF — keyword extraction
- T5 — abstractive summarization
- TextBlob — sentiment scoring

**Interface**

- HTML + JavaScript UI for segment navigation

---

## Implementation Details

This section describes the methodology used to implement each major component of the system pipeline.

### 1. Transcription
Audio files were transcribed using a speech recognition model capable of generating timestamp-aligned text. Before transcription, audio was preprocessed through format conversion, normalization, mono conversion, silence trimming, and chunking. Chunking ensured long recordings could be processed efficiently while maintaining accuracy. The output consisted of text segments mapped to exact timestamps, enabling later navigation and alignment features.


### 2. Topic Segmentation
After transcription, the text was divided into sentences and transformed into semantic embeddings. Two segmentation strategies were explored:

| Feature | Similarity-Based Method | Clustering-Based Method |
|--------|--------------------------|---------------------------|
| Detection Style | Sentence-to-sentence comparison | Global semantic grouping |
| Topic Coherence | Medium | High |
| Boundary Stability | Sensitive | Stable |
| Noise Handling | Weak | Strong |
| Segment Quality | Fragmented | Meaningful |
| Summary Alignment | Inconsistent | Accurate |

**Final Choice:**  Clustering-based segmentation.

**Reason:**  Produced clearer topic boundaries and better summaries.


### 3. Summarization
Summaries were generated at the topic-segment level instead of summarizing the entire transcript at once. This approach preserves contextual meaning and ensures each summary corresponds to a specific discussion. The summarization model condenses segment text while retaining key information, making it easier for users to scan content quickly.


### 4. Sentiment Analysis
Each topic segment was analyzed using a sentiment classification model. The model evaluates linguistic patterns to determine whether the tone of a segment is positive, negative, or neutral. Performing sentiment analysis per segment rather than per transcript provides finer insights into emotional variations across the podcast.


### 5. Interactive Timeline & Keyword Cloud
Structured outputs from earlier stages were used to build user-facing navigation features:

- **Interactive Timeline:** Uses timestamps from transcription and segmentation to allow direct navigation to specific topics.
- **Keyword Cloud:** Keywords extracted from each segment are aggregated and displayed visually to highlight dominant themes.

These components transform raw transcript data into an intuitive exploration interface, enabling fast information retrieval without listening to the full podcast.


### Implementation Insight
Similarity-based segmentation can detect subtle topic shifts but tends to over-segment content. Clustering-based segmentation, in contrast, produces more meaningful topic groupings and stronger summaries. Based on these observations, clustering was selected as the final segmentation strategy.

---

## Generated Outputs

For each podcast the system produces:

- Topic segments with timestamps
- Segment summaries
- Keyword lists
- Sentiment labels
- Structured transcript

These outputs enable topic-wise browsing instead of linear listening.

---

## Testing Evaluation

The system was tested on multiple podcast types:

- Interview style
- Lecture style
- Conversational podcasts

**Evaluation Criteria**

- Transcription accuracy
- Segment boundaries
- Keyword relevance
- Summary clarity
- UI usability
- Timestamp alignment

### Testing Log Summary

| Podcast          | Issue                      | Fix Applied                   |
| ---------------- | -------------------------- | ----------------------------- |
| Long lecture     | Over-segmentation          | Adjusted clustering threshold |
| Dialogue podcast | Abrupt boundaries          | Merged short segments         |
| Noisy audio      | Minor transcription errors | Audio normalization           |

---
## User Feedback

**User 1 – Non-technical**
- Understood interface quickly
- Used summaries to decide which part to read
- Felt transcript text was long but acceptable

**User 2 – Basic technical background**
- Navigation between segments was easy
- Liked summary before transcript
- Said sentiment labels were not very noticeable

**User 3 – First-time user**
- System felt simple to use
- Summaries matched content well
- Suggested slightly shorter summaries

### Improvements Implemented
- Reduced number of segments
- Shortened summaries
- Improved keyword highlighting
- Increased spacing between sections

---

## Limitations

While the system performs well for structured podcast understanding, a few practical limitations were observed:

- **Speech Recognition Sensitivity** — Transcription accuracy may drop in noisy recordings, overlapping speech, or strong accents.
- **Segmentation Granularity Trade-off** — Very fine segmentation can fragment topics, while broader segmentation may merge closely related discussions.
- **Model Dependency** — Output quality depends on pretrained models; performance may vary across domains or speaking styles.
- **Keyword Noise** — Occasionally generic words appear among extracted keywords despite filtering.
- **Sentiment Simplicity** — Sentiment analysis is polarity-based and may not capture nuanced tone such as sarcasm or mixed emotions.
- **Processing Time for Long Audio** — Longer podcasts require chunking and sequential processing, which increases runtime.

---

## Future Scope

- Add speaker diarization to distinguish multiple speakers within a podcast
- Improve topic segmentation using adaptive or hierarchical clustering methods
- Enhance summary quality using larger context-aware language models
- Implement automatic topic title generation for clearer segment labels
- Add confidence scores for transcripts, summaries, and sentiment predictions
- Build advanced analytics dashboards for deeper content insights
- Optimize processing speed for long-duration audio files
- Support distributed processing for large podcast collections
- Provide API endpoints for external application integration
- Improve robustness for noisy audio and overlapping speech

---

## Technical Distinction

This project was developed with a focus on solving real structural weaknesses found in typical speech-to-text systems rather than simply implementing a standard pipeline.

During experimentation, it was observed that most transcript processing systems fail not because of model limitations, but because of poor segmentation logic. Initial baseline segmentation produced fragmented topics and inconsistent summaries. After evaluating multiple strategies, semantic embedding-based clustering was selected because it generated more coherent topic boundaries and significantly improved downstream outputs such as summaries and keyword relevance.

This iterative selection process demonstrates an important engineering principle:

Architecture decisions influence output quality more than individual model choices.

---

## Experimental Insight

Two segmentation strategies were implemented and evaluated:

| Approach | Behavior | Outcome |
|--------|----------|--------|
| Similarity threshold | Detected small topic shifts | Produced fragmented segments |
| Semantic clustering | Grouped sentences by meaning | Produced coherent topics |

**Final Decision:** Semantic clustering  
**Reason:** More meaningful topic grouping and better summary alignment.

---

## System-Level Strength

What differentiates this system is not any single component, but the way all components work together:

- Sentence-level embeddings enable semantic segmentation
- Segmentation improves summary clarity
- Summaries improve navigation usability
- Keywords improve interpretability
- Timestamps preserve traceability to audio

This dependency chain ensures each stage strengthens the next, producing structured knowledge rather than raw transcripts.

---

## Engineering Maturity Demonstrated

This project reflects understanding of:

- pipeline design rather than script chaining
- evaluation before optimization
- usability alongside model performance
- trade-offs between granularity and coherence
- real-world constraints such as long audio handling

---

## Final Statement

This system is not just an implementation of NLP techniques — it is a structured solution to transforming long-form audio into navigable knowledge.

---

## Conclusion

Talk2Topics demonstrates how speech recognition and NLP can transform long audio content into structured knowledge. The system successfully converts raw podcasts into organized segments with summaries, keywords, and sentiment insights, making long-form audio searchable, readable, and navigable.

The clustering-based segmentation method provided the most meaningful results and enabled high-quality summaries, validating the effectiveness of embedding-driven semantic analysis.

---
