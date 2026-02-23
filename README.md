# Automated Podcast Transcription Project

## 1. Project Overview

###  Problem Statement

Podcasts contain valuable information across domains such as education, business, technology, and media. However, they are typically long-form audio content, making it difficult for users to:

- Quickly locate specific topics within an episode  
- Extract key insights without listening to the entire recording  
- Analyze emotional tone or discussion flow  
- Navigate transcripts efficiently  

Manual listening is time-consuming and inefficient, especially for researchers, students, and media professionals. Therefore, an automated system is required to convert podcast audio into structured, searchable, and analyzable text.


### Objectives of the Project

The primary objectives of this project are:

- To automatically transcribe podcast audio into timestamped text  
- To segment transcripts into meaningful topic-based sections  
- To generate concise summaries for each segment  
- To extract relevant keywords using TF-IDF  
- To perform sentiment analysis using VADER  
- To generate structured metadata for improved navigation and visualization  

The goal is to create an intelligent system that transforms unstructured audio into structured insights.


### Significance and Real-World Applications

This system has multiple real-world applications:

- **Education** – Enables students to quickly review lecture-based podcasts and identify important concepts.  
- **Accessibility** – Assists hearing-impaired users by providing structured transcripts and summaries.  
- **Media & Journalism** – Helps journalists analyze topic transitions and sentiment trends.  
- **Research & Data Analysis** – Facilitates thematic analysis of long-form discussions.  
- **Content Navigation** – Allows users to jump directly to relevant sections within podcast episodes.  

By automating transcription and analysis, the system significantly improves content accessibility, usability, and analytical capability.

## 2. Dataset Description

### Source of the Dataset

The dataset used in this project is based on transcripts from the **"This American Life"** podcast.

"This American Life" is a long-form storytelling podcast featuring real-life narratives, interviews, and thematic discussions. The dataset includes episode-level transcript files that were processed for segmentation and analysis.

### Preprocessing Steps Undertaken

A total of **10 podcast episodes** from the *This American Life* dataset were used for analysis.

The following preprocessing steps were applied before segmentation and analysis:

#### Transcript Cleaning

- Removal of timestamp brackets (e.g., `[12.45 - 18.90]`)
- Removal of unnecessary speaker labels
- Whitespace normalization and formatting standardization

This ensured that the transcript text was clean and suitable for NLP processing.

#### Timestamp Extraction

Regular expressions were used to extract:

- Start time  
- End time  

from each transcript line.

## 3. System Architecture

###  Overall Architecture Flow

<img width="600" height="750" alt="image" src="https://github.com/user-attachments/assets/43c765b5-ca39-44e4-b895-cc2d8d796240" />


##  4. Tools and Libraries Used

###  Audio Processing

Although the primary focus of the project was transcript-based analysis, podcast audio files in MP3 format were used as input.  
Audio files were transcribed using Whisper, and transcript files were structured for downstream NLP processing.

### Speech-to-Text – Whisper

OpenAI's Whisper model was used to convert podcast audio into timestamped transcripts.  
Whisper provides high transcription accuracy and generates start and end timestamps, which were essential for timeline-based segmentation.

###  NLP & Analysis

#### SentenceTransformer (MiniLM)

The `all-MiniLM-L6-v2` model was used to generate sentence embeddings.  
These embeddings capture semantic meaning and were used to compute cosine similarity for topic segmentation.

#### TF-IDF (Scikit-learn)

TF-IDF vectorization was used for:
- Extractive summarization (selecting the most relevant sentence)
- Keyword extraction (top 5 important terms per segment)

#### VADER Sentiment Analyzer (NLTK)

VADER was used to classify sentiment at the segment level.  
It provides a compound score that was used to label segments as Positive, Negative, or Neutral.

###  User Interface

The project includes a structured output system where:
- Full transcripts  
- Topic segments  
- Segment summaries  
- Keywords  
- Sentiment labels  
are presented in an organized interface for easy navigation and interpretation.

## 5. Implementation Details

Transcription
- Whisper was used to generate timestamped transcripts from podcast audio.

Topic Segmentation
- Sentence embeddings were generated.

Cosine similarity computed between adjacent sentences.
- Topic boundaries identified where similarity drops below threshold.

Summary Generation
- TF-IDF scoring selects the most representative sentence.

Sentiment Analysis
- VADER compound score thresholds:
  - ≥ 0.05 → Positive
  - ≤ -0.05 → Negative
  - Otherwise → Neutral

Interactive Timeline & Keyword Cloud
- Timestamps were proportionally mapped to segment boundaries.
- WordCloud was generated using extracted keywords for visualization.

## 6. Results and Outputs

The system successfully converts long-form podcast audio into structured, segmented, and analyzable textual insights.

Below are the major outputs generated by the system:

### Full Transcript

The complete transcript of each podcast episode is generated using Whisper.

- Contains timestamped speech segments
- Preserves chronological flow
- Enables time-based navigation
<img width="500" height="300" alt="image" src="https://github.com/user-attachments/assets/7a2da7c8-fc7d-4d5d-805b-26887bfa0ac0" />

### Topic Segments

The transcript is divided into coherent topic-based segments using semantic similarity analysis.

Each segment includes:
- Segment ID
- Title (generated from key nouns)
- Start and end timestamps
- Full segment text
- <img width="500" height="300" alt="image" src="https://github.com/user-attachments/assets/d7a64b46-a287-4d86-9866-760b90619efb" />


### Interactive Timeline

Using extracted timestamps, each segment is mapped to its corresponding time range within the episode.

- Displays start and end time for each topic
- Enables navigation based on time
- Helps users jump directly to specific sections
<img width="500" height="200" alt="image" src="https://github.com/user-attachments/assets/0b74d47e-2081-47dd-839d-66609ff188b6" />


### Keyword 

A keyword visualization is generated using extracted TF-IDF keywords.

- Highlights frequently occurring important terms
- Provides quick insight into dominant themes
- Enhances visual interpretability
<img width="500" height="300" alt="image" src="https://github.com/user-attachments/assets/d4a4d2fc-8c22-40d7-87bc-7a2d5aa0abe4" />


###  User Interface
The system interface displays:
- Full transcript
- Topic segments
- Segment summaries
- Extracted keywords
- Sentiment labels
- Timeline information

## 7. Testing and Feedback

### Testing Log

| Podcast    | Issue Identified        | Corrective Action Taken |
|------------|------------------------|--------------------------|
| Episode 1  | Over-segmentation       | Adjusted similarity threshold |
| Episode 2  | Irrelevant keywords     | Improved stopword filtering |
| Episode 3  | Short summaries         | Increased MIN_WORDS value |


### User Feedback Summary

- Summaries were helpful but sometimes too brief.  
- Topic titles needed refinement.  
- UI navigation was intuitive.  
- Sentiment classification was generally accurate.  

### Improvements Implemented

Based on testing and user feedback, the following improvements were made:

- Fine-tuned similarity threshold for better segmentation  
- Enhanced keyword filtering logic  
- Increased minimum word count for stronger summaries  
- Minor UI formatting improvements  
The system performance improved after these refinements.


## 8. Limitations

Despite achieving the core objectives, the system has certain limitations:

- **Transcription Accuracy Dependency**  
  The accuracy of generated transcripts depends heavily on the clarity and quality of the input audio.

- **Sensitivity to Background Noise**  
  Background noise, overlapping speech, or unclear pronunciation may reduce speech recognition performance.

- **Segmentation Threshold Generalization**  
  The cosine similarity threshold used for topic segmentation may not generalize equally well across all podcast styles or genres.

- **Lexicon-Based Sentiment Analysis**  
  VADER sentiment analysis is rule-based and may not fully capture contextual or sarcastic expressions.

- **Extractive Summarization Limitation**  
  Since summaries are generated using an extractive TF-IDF approach, they may not always capture deeper semantic meaning or contextual nuances.


## 9. Future Work

The system can be further enhanced in the following ways:

- **Advanced Speech Recognition Models**  
  Integrate more advanced or domain-specific speech recognition models to improve transcription accuracy.

- **Real-Time Transcription**  
  Extend the system to support real-time or streaming transcription for live podcasts.

- **Speaker Identification**  
  Implement speaker diarization to differentiate between multiple speakers within an episode.

- **Improved Topic Segmentation**  
  Use advanced topic modeling techniques such as LDA or transformer-based models for more accurate segmentation.

- **Enhanced User Interface**  
  Improve UI design with advanced navigation features, search functionality, and better visualization components.

- **Cloud Deployment**  
  Deploy the system on cloud infrastructure to support scalability and multi-user access.



