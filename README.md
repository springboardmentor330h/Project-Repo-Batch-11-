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
- Topic Segmentation, Keywords, and Summaries

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








## Notes

Due to the large size of the audio files, they are not stored directly in this GitHub repository.

All processed episodes can be downloaded from the Google Drive link provided above. The dataset can also be regenerated locally using the provided scripts. 

Same is true for the output json embeddings too.
