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

<img width="1024" height="1536" alt="image" src="https://github.com/user-attachments/assets/43c765b5-ca39-44e4-b895-cc2d8d796240" />


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

### Topic Segments

The transcript is divided into coherent topic-based segments using semantic similarity analysis.

Each segment includes:
- Segment ID
- Title (generated from key nouns)
- Start and end timestamps
- Full segment text

### Interactive Timeline

Using extracted timestamps, each segment is mapped to its corresponding time range within the episode.

- Displays start and end time for each topic
- Enables navigation based on time
- Helps users jump directly to specific sections

### Keyword Cloud

A WordCloud visualization is generated using extracted TF-IDF keywords.

- Highlights frequently occurring important terms
- Provides quick insight into dominant themes
- Enhances visual interpretability

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
























### **System Testing Log**



#### **Test Log Entry 1**



**Podcast Name \& Source**

This American Life – Episode 1 (Public Podcast Dataset)



**Episode Duration \& Number of Speakers**

~55 minutes, multiple speakers



**Transcription Issues Encountered**

* Minor word omissions during fast-paced speech
* Incorrect transcription of proper nouns
* Speaker attribution errors during overlapping dialogue



**Segmentation Problems Observed**

* Long discussions split into multiple smaller segments
* Some segment boundaries slightly early or late



**UI Behavior Issues / Bugs**

* Long summaries required additional scrolling
* Minor text alignment inconsistencies



Overall System Performance Notes

System handled long-form storytelling effectively with minor transcription and formatting issues.



#### **Test Log Entry 2**



**Podcast Name \& Source**

This American Life – Episode 10 (Public Podcast Dataset)



**Episode Duration \& Number of Speakers**

~50 minutes, multiple speakers



**Transcription Issues Encountered**

* Background noise caused occasional missing words
* Inconsistent punctuation in extended sentences



**Segmentation Problems Observed**

* Over-segmentation during gradual topic transitions
* Some related topics split unnecessarily



**UI Behavior Issues / Bugs**

* Segment titles wrapped inconsistently
* Navigation buttons worked as expected



Overall System Performance Notes

Stable performance with good topic detection; segmentation needs refinement for smooth transitions.



#### **Test Log Entry 3**



**Podcast Name \& Source**

Interview Podcast Sample (Public Dataset)



**Episode Duration \& Number of Speakers**

~30 minutes, 2 speakers



**Transcription Issues Encountered**

* Occasional confusion between interviewer and guest
* Fast responses led to minor transcription gaps



**Segmentation Problems Observed**

* Question–answer sections sometimes merged
* Topic boundaries mostly accurate



**UI Behavior Issues / Bugs**

* No major UI issues observed
* Smooth segment navigation



Overall System Performance Notes

System performed well for interview-style podcasts with minimal issues.



#### **Test Log Entry 4**



**Podcast Name \& Source**

News Discussion Podcast (Public Dataset)



**Episode Duration \& Number of Speakers**

~20 minutes, 3 speakers



**Transcription Issues Encountered**

* Overlapping speech caused partial sentence loss
* Acronyms occasionally misinterpreted



**Segmentation Problems Observed**

* Rapid topic changes grouped into single segments
* Major topic breaks correctly identified



**UI Behavior Issues / Bugs**

* Minor spacing inconsistencies between segments
* Timestamp navigation accurate



Overall System Performance Notes

System handled short, fast-paced discussions reasonably well with slight transcription challenges.



#### **Test Log Entry 5**



**Podcast Name \& Source**

Casual Talk Podcast Sample (Public Dataset)



**Episode Duration \& Number of Speakers**

~15 minutes, 2 speakers



**Transcription Issues Encountered**

* Informal speech led to grammatical inconsistencies
* Filler words frequently included



**Segmentation Problems Observed**

* Short conversations occasionally over-segmented
* Segment labels sometimes too generic



**UI Behavior Issues / Bugs**

* No functional UI issues
* Consistent display across all sections



Overall System Performance Notes

System performed well for casual conversations with minor labeling and segmentation improvements needed.





**Summary of Testing Observations**



Transcription: Errors increase with fast or overlapping speech



Segmentation: Over-segmentation occurs during gradual topic changes



UI: Mostly stable with minor formatting inconsistencies



Overall Performance: System is robust across diverse podcast formats with scope for clarity improvements



#### User Feedback Collection





Feedback was collected from 5 users who were not involved in project development.



Questions Asked

* Was the interface easy to understand?
* Were summaries helpful?
* Was anything confusing?
* What could be improved?



User Feedback Summary



User	Feedback

User 1	Interface was clear, summaries helpful

User 2	Wanted shorter summaries

User 3	Keywords were useful but repetitive

User 4	Navigation was smooth

User 5	Segment titles could be clearer



#### Iterations and Improvements Made



Based on testing results and user feedback, the following improvements were implemented:



* Improvements Applied
* Reduced summary length for clarity
* Improved topic segment labels
* Removed generic and duplicate keywords
* Fixed UI spacing and alignment issues
* Improved formatting consistency across segments

















**Author**

Shambhavi Bajoria











