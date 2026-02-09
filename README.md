# Automated Podcast Transcription and Topic Segmentation

This repository contains the initial milestone work for a project focused on building a complete pipeline for long-form podcast transcription and topic segmentation.

The primary goal of this phase is to prepare a high-quality, large-scale dataset consisting of aligned podcast audio and transcripts, suitable for downstream tasks such as topic boundary detection, summarization, and semantic segmentation.

---

## Dataset

The project uses the **Lex Fridman Podcast** dataset from Hugging Face. 
https://huggingface.co/datasets/Whispering-GPT/lex-fridman-podcast

This dataset was selected because:

- Episodes are long-form (typically 1–3 hours)
- Conversations span diverse technical and philosophical topics
- High-quality transcripts are available
- The format is well-suited for topic segmentation research

---

## Audio Files

Due to the large size of the processed audio files, they are not hosted directly on GitHub.

They can be downloaded from the following Google Drive folder:

**Google Drive:**  
https://drive.google.com/drive/folders/11WZNY_P54YauvS8zX-9YsdDo9A6JBctt?usp=sharing

The folder contains fully preprocessed podcast episodes in standardized WAV format.

---

## Repository Structure

### Files

#### `train-00000-of-00001-25f40520d4548308.parquet`

Original dataset in Parquet format.

#### `parquet_to_csv.py`

Converts the Parquet file into a CSV file (`lex_fridman_full.csv`) without cleaning.

#### `lex_fridman_full.csv`

Raw CSV conversion of the Parquet dataset.

#### `prepare_dataset_and_fetch_audio.py`

Main dataset preparation script. This script:

- Extracts relevant columns
- Adds row identifiers
- Creates a cleaned CSV
- Downloads episode audio
- Converts audio to WAV
- Resamples to 16 kHz mono
- Applies consistent naming
- Generates a download manifest

#### `lex_fridman_cleaned.csv`

Cleaned CSV containing:

- `row_id`
- `video_id`
- `title`
- `transcript`

#### `preprocessing.py`

Applies signal-level preprocessing:

- Noise reduction
- Loudness normalization
- Silence trimming

---

## Audio Format Standardization

All podcast episodes are standardized to the following format:

- WAV
- 16,000 Hz sample rate
- Mono channel

This format is commonly used in speech processing and NLP pipelines.

---

## Naming Convention

Each audio file follows this format:

podcast<row_id>_<video_id>.resampled.wav

makefile
Copy code

**Example:**

podcast036_HYsLTNXMl1Q.resampled.wav

yaml
Copy code

This ensures traceability between CSV entries and audio files.

---

## Dataset Size

Each Lex Fridman episode is typically 1–2 hours long. Even without using all audio files, the dataset already contains:

- Over 70 hours of audio even if we use only 45 podcasts
- More than 10 GB of processed data

This is sufficient for initial modeling, experimentation, and evaluation.

---

## Preprocessing Steps

Each audio file undergoes the following preprocessing:

- Noise reduction
- Loudness normalization
- Silence trimming
- Resampling to 16 kHz
- Conversion to mono

This ensures uniformity and improves data quality for downstream tasks.

---

## Current Status

The following components have been completed:

- Dataset selection
- Parquet to CSV conversion
- Dataset cleaning
- Audio downloading
- Audio standardization
- Audio preprocessing
- Naming standardization
- Manifest generation
- Reproducible pipeline setup
- **Week 3:** Topic Segmentation, Keywords, and Summaries
- **Week 4:** User Interface and Transcript Navigation

## Week 3: Topic Segmentation and Analysis

### Overview

Week 3 focuses on converting transcripts into structured, topic-wise representations by:
1. Segmenting transcripts into topics
2. Extracting keywords for each segment
3. Creating short summaries for each segment

### Topic Segmentation Algorithms

#### Algorithm 1: Baseline (TF-IDF + Chunk-based Similarity)

**File:** `baseline_segmentation.py`

**Method:**
- Splits transcript into sentences
- Groups sentences into fixed-size chunks (default: 4 sentences per chunk)
- Applies TF-IDF vectorization on chunks
- Computes cosine similarity between consecutive chunks
- Detects topic boundaries where similarity drops below threshold
- Threshold: `mean - k*std` 

**Characteristics:**
- Uses lexical similarity (bag-of-words approach)
- Works at chunk level (4 sentences)
- Produces fewer, longer segments

#### Algorithm 2: Embedding-based (Sentence Transformers)

**File:** `embedding_segmentation.py`

**Method:**
- Splits transcript into individual sentences
- Generates semantic embeddings using SentenceTransformers (`all-MiniLM-L6-v2`)
- Computes cosine similarity between consecutive sentence embeddings
- Detects topic boundaries where semantic similarity drops below threshold
- Threshold: `mean - k*std`

**Characteristics:**
- Uses semantic similarity (meaning-based approach)
- Works at sentence level (1 sentence = 1 unit)
- Produces more, shorter, and more consistent segments

### Comparison and Evaluation

**Quantitative Analysis:**

The comparison results are available in `comparison_outputs/`:
- `comparison_summary.csv` - Statistical comparison of both algorithms (segment counts, average word counts, standard deviations)
- `boundary_overlap.csv` - Boundary overlap analysis (Jaccard similarity between algorithms)
- `plots/segment_count_dist.png` - Distribution of segment counts per episode
- `plots/segment_length_dist.png` - Distribution of average segment lengths (words)

**Note:** You can examine detailed examples by comparing segments in `segments_all_baseline.csv` and `segments_all_embedding.csv` for the same episode to see the differences in segmentation approaches.

**Key Findings:**
- **Embedding algorithm produces significantly more segments** than baseline
- **Embedding algorithm produces smaller and more consistent segment lengths** (average segment length is much smaller)
- Baseline algorithm produces fewer segments with highly variable lengths (some very short, some extremely long)

**Qualitative Evaluation:**

After manual review of sample segments from both algorithms:

1. **Are the segments meaningful?**
   - **Embedding algorithm:** Yes, segments are more meaningful and coherent. Each segment focuses on a single topic or subtopic.
   - **Baseline algorithm:** Segments are less coherent, often mixing multiple topics within a single segment.

2. **Do topic boundaries feel natural to a human reader?**
   - **Embedding algorithm:** Yes, boundaries are more natural and align better with topic transitions in the conversation.
   - **Baseline algorithm:** Boundaries are less natural, sometimes splitting topics mid-discussion or combining unrelated topics.

3. **Which approach performs better and why?**
   - **Embedding algorithm performs better** for the following reasons:
     - **More natural boundaries:** Semantic embeddings capture meaning better than lexical similarity, resulting in boundaries that align with actual topic shifts
     - **Better segmentation:** Produces more granular segments that capture individual topics/subtopics rather than grouping multiple topics together
     - **More consistent:** Segment lengths are more uniform and appropriate for the content
     - **More meaningful segments:** Each segment makes sense as a standalone unit, making it easier to understand the topic being discussed

The embedding-based approach leverages semantic understanding, which is crucial for conversational transcripts where topics can shift subtly without obvious keyword changes.

### Outputs

**Complete outputs (segmented transcripts, keywords, and summaries) are available on Google Drive:**

**Google Drive:** https://drive.google.com/drive/folders/1YopGLkQYHibzAyZu4P6VmW03x-z_RQPC?usp=sharing

The folder contains:
- `output_json_baseline/` - Baseline algorithm segments 
- `output_json_embedding/` - Embedding algorithm segments 
- `output_kws_summaries/json_updated/` - Segments with keywords and summaries 
- `output_kws_summaries/json_with_sentiment/` - Segments with keywords and summaries and sentiment (positive, negative or neutral)

**Local outputs (in repository):**
- `segments_all_baseline.csv` - Combined baseline segments
- `segments_all_embedding.csv` - Combined embedding segments
- `comparison_outputs/` - Comparison results and visualizations

### Keywords and Summaries

**File:** `keywords_and_summaries.py`

**Keywords Extraction:**
- Method: TF-IDF vectorization
- N-gram range: (1, 2) - captures single words and bigrams
- Stopwords removed using NLTK English stopwords
- Top-k keywords extracted per segment (default: 10)

**Summaries Generation:**
- Method: LLM-based summarization using T5-small model
- Model: `t5-small` (local, offline)
- Summary length: Adaptive (1-2 sentences, typically 10-80 tokens)
- Format: Concise summaries capturing the main point of each segment

**Output Format:**

Each segment JSON file contains:
```json
{
  "segment_id": 0,
  "start_sentence": 0,
  "end_sentence": 4,
  "text": "Segment text...",
  "num_words": 85,
  "keywords": ["keyword1", "keyword2", ...],
  "summary": "Short summary of the segment..."
}
```

### Usage

**Run Baseline Segmentation:**
```bash
python baseline_segmentation.py --input_csv lex_fridman_cleaned.csv --out_json_dir output_json_baseline --segments_csv segments_all_baseline.csv
```

**Run Embedding Segmentation:**
```bash
python embedding_segmentation.py --input_csv lex_fridman_cleaned.csv --out_json_dir output_json_embedding --segments_csv segments_all_embedding.csv
```

**Compare Algorithms:**
```bash
python compare_algorithms.py
```

**Extract Keywords and Summaries:**
```bash
python keywords_and_summaries.py --input_json_dir output_json_embedding --local_model_dir models/t5-small --top_k 10
```

---

## Week 4: User Interface and Transcript Navigation

### Overview

Week 4 focuses on building an interactive user interface that allows users to navigate podcast transcripts efficiently through topic-based segment jumping. This eliminates the need for endless scrolling or manual text searching.

### Features Implemented

**File:** `app.py` (Streamlit application)

**Core Functionality:**

1. **Episode Selection**
   - Dropdown menu to select from 228 processed podcast episodes
   - Displays episode title and metadata

2. **Topic Segment Navigation**
   - Displays all segments for the selected episode
   - Each segment labeled with summary (truncated to 70 chars) or keywords
   - Format: "Segment X: [summary/keywords]"

3. **Segment Jumping**
   - Click/select any segment from dropdown
   - Instantly displays the full transcript text for that segment
   - Direct access to topic content

4. **Segment Metadata Display**
   - Start/end sentence indices
   - Word count
   - Keywords (if available)
   - Full transcript text in scrollable text area

### How It Works

1. **User selects episode** → System loads corresponding JSON file
2. **System extracts segments** → Builds list of segment labels from summaries/keywords
3. **User selects segment** → System retrieves segment text
4. **System displays content** → Shows transcript text with metadata

**Data Flow:**
```
JSON File (output_kws_summaries/json_updated/)
    ↓
Load episode data
    ↓
Extract segments array
    ↓
Build labels (summary/keywords)
    ↓
User selection
    ↓
Display segment.text
```

### Running the Application

**Prerequisites:**
```bash
pip install streamlit
```

**Launch the app:**
```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

### Technical Implementation

**Technology Stack:**
- **Streamlit** - Interactive web application framework
- **JSON** - Data storage format (from Week 3 outputs)
- **Python** - Backend logic

**Key Components:**
- `@st.cache_data` - Caching for performance (episode file list)
- `st.selectbox()` - Episode and segment selection widgets
- `st.text_area()` - Transcript display with scrolling
- `st.metric()` - Metadata visualization

## Week 5: Visualization and Detail Enhancements

### Overview

Week 5 focuses on improving the visualization, presentation, and usability of the outputs generated in Weeks 3 and 4.  
No new machine learning models are trained in this phase. Instead, existing results such as topic segments, summaries, keywords, and sentiment scores are transformed into interactive and visual components.

The objective is to make long-form podcast transcripts easier to explore, interpret, and navigate for human users.

---

### Features Implemented

**File:** `app.py` (Streamlit application)

---

### 1. Visual Topic Timeline

A visual timeline is introduced to represent the full podcast episode as a single continuous horizontal bar.

- Each block represents one topic segment
- Block width is proportional to the segment length (measured using word count)
- Blocks are arranged sequentially to reflect podcast progression
- Color encoding represents sentiment:
  - Green → Positive
  - Orange → Neutral
  - Red → Negative

This timeline provides a high-level structural overview of the podcast and enables quick understanding of topic flow.

---

### 2. Sentiment Visualization

Each topic segment includes sentiment information computed earlier in the pipeline.

- Sentiment label: Positive / Neutral / Negative
- Sentiment score: Numerical polarity value

Sentiment is displayed:
- Visually in the timeline using color
- Textually in the segment detail view

---

### 3. Keyword Display and Keyword Cloud

For every selected segment:

- Extracted keywords are displayed as a list
- A keyword cloud is generated using the `WordCloud` library
- Word size reflects keyword importance (uniform weighting used for visualization)

This allows users to quickly grasp the dominant themes within each segment.

---

### 4. Polished Segment Summaries

Summaries generated in Week 3 are refined for readability without regenerating them.

Improvements include:
- Corrected capitalization and grammar
- Removal of filler words
- Improved sentence flow
- Ensuring summaries remain concise (2–3 sentences)

This enhances presentation quality while preserving original semantic meaning.

---

### 5. Improved Formatting and Layout

The interface is reorganized to make information more scannable and user-friendly.

Each segment’s information is clearly separated using headings:
- Summary
- Keywords
- Keyword Cloud
- Sentiment
- Transcript Text

Additional improvements include:
- Consistent spacing between sections
- Clear visual separation
- Scrollable transcript display for long segments

The focus is on clarity, usability, and functional design.

---

# Week 6: System Testing and Feedback Collection

## 1. Summary
The system was tested against **10 podcast episodes** (varying in length, topic, and speaker style) and feedback was collected from **three external users**.

While the core NLP pipeline (segmentation, sentiment analysis, and summarization) is robust, testing revealed specific friction points in the User Interface (navigation). This report details the testing logs, user feedback, and the changes made to address these issues.

---

## 2. Internal System Testing Log
* **Tester:** Developer (Self-Testing)
* **Scope:** 10 Episodes (~20 hours of audio data)
* **Focus:** Transcription accuracy, segmentation logic, and UI stability.

| Podcast Episode | Type/Genre | Transcription & Segmentation Issues | Summary & Keyword Performance | Sentiment & UI Behavior |
| :--- | :--- | :--- | :--- | :--- |
| **1. Stephen Wolfram** | Physics (3.5h) | **Segmentation:** Generally good, but some segments are too short (filler words). | **Summary:** Critical Bug. Model entered a repetition loop ("et cetera et cetera" x15). | **Sentiment:** Well-handled. |
| **2. Jed Buchwald** | History (1.5h) | **Transcription:** Entity Error ("Buckwald" vs "Buchwald"). | **Summary:** Recursive phrasing noted in 2 segments. | **Sentiment:** Neutral/Academic tone handled well. |
| **3. Sergey Nazarov** | Crypto (2.5h) | **Segmentation:** "Micro-segments" detected (e.g., segments containing only "Wait, wait"). | **Keywords:** Excellent tech extraction ("DeFi", "Oracle"). | **Sentiment:** Well-handled. |
| **4. Philip Goff** | Philosophy (2h) | **Transcription:** Good handling of abstract terms ("Panpsychism"). | **Keywords:** High relevance ("Consciousness", "Qualia"). | **Sentiment:** "Dark" philosophical concepts occasionally mislabeled as Negative. |
| **5. Oriol Vinyals** | AI/Gaming (1h) | **Segmentation:** Clean boundaries between "StarCraft" and "Language" topics. | **Summary:** Concise and accurate. | **Sentiment:** Well-handled. |
| **6. Ray Dalio** | Economics (1h) | **Transcription:** Clear. | **Keywords:** Noisy. Included numbers ("10") and "Youtube" as top tags. | **Sentiment:** Correctly identified advice as Positive. |
| **7. Michael Malice** | Politics (1.5h) | **Transcription:** Struggled slightly with rapid banter/interruptions. | **Summary:** Context error (interpreted "Dasvidanya" as a name). | **Sentiment:** High variance (Red/Green swings) accurately reflected chaotic tone. |
| **8. Tomaso Poggio** | Neuroscience (1h) | **Segmentation:** Excellent distinct breaks. | **Keywords:** Generic but accurate ("Brains", "Center"). | **Sentiment:** Well-handled. |
| **9. George Hotz** | Tech (3h) | **Transcription:** Good capture of informal slang. | **Summary:** Occasionally vague ("The purpose is to maximize it" - missing context). | **Sentiment:** Mostly Positive/Energetic, matching speaker vibe. |
| **10. Tim Dillon** | Comedy (1.5h) | **Segmentation:** Good. | **Keywords:** Ads mixed with content ("Spoon", "Business"). | **Sentiment:** **Edge Case:** System missed sarcasm, labeling cynical rants as "Positive." |

---

## 3. User Feedback Collection
**Methodology:** Feedback was taken from 3 External Users.

### User 1: Ayush (Friend)
* **Positive:** "The Visual Timeline is the best part. I immediately understood the 'emotional arc' of the episode."
* **Critical Feedback:**
    * **The Disconnect:** Attempted to click the bars on the chart to filter data, but nothing happened. Found it frustrating to match Segment IDs manually.
    * **Dropdown:** The list is too long to scroll through.

### User 2: Ishita (Classmate)
* **Positive:** "Cool concept, seeing the shape of a conversation is fascinating."
* **Critical Feedback:**
    * **Navigation:** "The dropdown list is very long... scrolling to find a topic feels overwhelming." Suggested "Next/Previous" buttons.
    * **Context:** Found it difficult to map the "Sentence Index" numbers to the actual audio progress.

### User 3: Tanmay (Friend)
* **Positive:** Liked the "Green/Red" sentiment coloring and the clean layout.
* **Critical Feedback:**
    * **The "Barcode" Effect:** On long episodes (200+ segments), the chart bars become too thin to hover over effectively.
    * **Repetition Bug:** Noticed summary glitches where words repeated ("comrade, comrade") or summaries cut off mid-sentence.
    * **Empty Data:** Some segments were just one word (e.g., "Yes", "Sure"), creating clutter.

---

## 4. Synthesis & Patterns Identified
Based on the combined testing data, the following patterns have emerged that require attention in the iteration phase.

### A. Navigation Friction
* **Observation:** Users expect the Altair chart to be clickable. When it isn't, they are forced to use the dropdown, which is overwhelming for long episodes (200+ items).
* **Decision:** Implementing full Altair interactivity is complex, but adding "Next Segment" / "Previous Segment" buttons is a high-value, low-effort fix to improve flow.

### B. Content Noise (Glitches)
* **Micro-segments:** Segments with <10 words ("Wait, wait", "Yes") clutter the UI.
* **Summary Loops:** The model occasionally gets stuck repeating phrases ("et cetera").
* **Keywords:** Stop words like "yeah", "oh", and "thing" are appearing in word clouds.

---

## 5. Implementation of Week 6 Fixes (Completed)
In accordance with Week 6 guidelines, no new models were trained and no JSON data was regenerated. The following code-level improvements have been successfully implemented in `app.py` to address user feedback.

### 1: UI & Navigation Improvements 
* **Next / Previous Buttons:** Implemented `st.button("Next")` and `st.button("Previous")` to allow users to navigate segments sequentially without repeatedly opening the dropdown list.
* **State Management:** Utilized `st.session_state` to ensure safe and smooth transitions between segments.

### s2: Data Cleaning & Post-Processing 
* **Micro-Segment Filter:** Added logic to hide or merge any segment containing fewer than **15 words**, significantly reducing the "Barcode" effect and removing empty/low-value data points.
* **Keyword Exclusion:** Updated the `STOP_WORDS` list during display time to explicitly remove common conversational fillers detected during testing:
    > `['yeah', 'oh', 'okay', 'right', 'know', 'thing', 'et', 'cetera']`

### 3: Content Presentation 
* **Summary Repetition Detection:** Implemented a validation check for summary loops.
    * *Logic:* If a 3-word phrase repeats more than 2 times in a summary, the system automatically falls back to displaying the **raw transcript** for that segment instead.
* **Formatting:** Standardized headings and spacing for a cleaner reading experience.

---

## Conclusion
The system has passed the **"Validation"** phase. The User Experience friction points identified during testing have been resolved via the Week 6 code updates listed above.


## Notes

Due to the large size of the audio files, they are not stored directly in this GitHub repository.

All processed episodes can be downloaded from the Google Drive link provided above. The dataset can also be regenerated locally using the provided scripts. 

Same is true for the output json embeddings too.
