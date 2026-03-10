# 🚀 Week 1: Project Initialization and Dataset Acquisition

> *Setting up the foundation for our podcast analysis pipeline*

## 📋 Overview

**Week 1** establishes the project foundation by verifying the development environment and acquiring the podcast dataset from Kaggle. This creates the baseline for all subsequent processing pipelines in our automated podcast transcription and segmentation system.

---

## 🎯 Objectives

- ✅ **Project Setup**: Initialize structure and verify environment
- ✅ **Dependencies**: Confirm Python libraries and system configuration
- ✅ **Data Acquisition**: Download podcast dataset from Kaggle
- ✅ **Sample Creation**: Generate truncated datasets for development
- ✅ **Directory Structure**: Establish organized data folders

---

## 📁 Contents

### `project_init_and_dataset_acquisition.ipynb`

A comprehensive Jupyter notebook covering project setup and data acquisition.

#### 🔧 Key Sections:

1. **Environment Verification**
   - Verify Python version and available libraries
   - Check system compatibility (GPU/CPU availability)
   - Validate development dependencies

2. **Dataset Acquisition**
   - Download from [Kaggle - This American Life Podcast Transcript Dataset](https://www.kaggle.com/datasets/thedevastator/this-american-life-podcast-transcript-dataset)
   - Dataset includes:
     - 600 podcast episode transcripts
     - Reference transcripts (CSV format)
   - **Note**: Audio files stored separately due to size

3. **Dataset Verification**
   - List and validate all downloaded transcript files
   - Verify audio file availability
   - Check directory structure integrity

4. **Create Truncated Dataset**
   - Extract first 200 rows from full CSV files
   - Generate sample datasets for faster iteration:
     - `lines_clean_200.csv` - Sample transcript lines
     - `episode_info_clean_200.csv` - Sample episode metadata
   - Output location: `data/transcripts_raw_truncated/`

#### 📄 Files Used:

| File | Purpose | Location |
|------|---------|----------|
| `lines_clean.csv` | Full transcript lines | `data/transcripts_raw/` |
| `episode_info_clean.csv` | Episode metadata | `data/transcripts_raw/` |
| `lines_clean_200.csv` | Sample transcripts (200 rows) | `data/transcripts_raw_truncated/` |
| `episode_info_clean_200.csv` | Sample metadata (200 rows) | `data/transcripts_raw_truncated/` |

---

## 📊 Data Acquired

### 🎙️ Raw Transcripts
- **Source**: Kaggle dataset 
- **Format**: CSV (Comma-Separated Values)
- **Coverage**: 600 complete podcast episodes
- **Location**: `data/transcripts_raw/`

### 🎵 Audio Files
- **Source**: [This American Life](https://www.thisamericanlife.org/archive)
- **Format**: MP3
- **Total Size**: ~6 GB (for 200 mp3 files)
- **Episodes**: 200 numbered audio files
- **Location**: `data/audio_raw/`
- **Storage**: Stored locally due to size; not committed to Git

### ✂️ Truncated Samples
- **Purpose**: Development and testing with reduced dataset
- **Size**: 200 rows each (subset of full dataset)
- **Generation**: Automated via pandas DataFrame slicing
- **Benefits**: Faster iteration for prototyping

---

## 🔧 Dependencies

### 📚 Core Libraries
- `pandas` - Data manipulation and CSV processing
- `python` 3.8+ - Base programming language

### 🖥️ Environment Setup
- Google Colab or local Python environment
- Google Drive integration (for Colab workflows)
- ~7 GB free disk space

---

## 🧠 Key Concepts

### 📂 Dataset Structure
```
Transcripts Format:
├── lines_clean.csv
│   └── Columns: episode_id, line_text, speaker_id, timestamp, ...
├── episode_info_clean.csv
│   └── Columns: episode_id, title, date_published, duration, ...
└── Audio Files: episode_{1-30}.mp3

Truncated Samples:
├── lines_clean_200.csv (first 200 lines)
└── episode_info_clean_200.csv (first 200 rows)
```

### 🎧 Dataset Source
The dataset comes from the public "This American Life" podcast:
- Episodes from season 1-X
- High-quality human-generated transcripts
- Diverse content categories (news, storytelling, interviews)
- ~40-60 minutes per episode

---

## 🔄 Workflow

1. **Mount Environment** (if using Colab)
   - Connect to Google Drive for data access

2. **Verify Setup**
   - Check Python version
   - List available libraries
   - Confirm GPU availability (optional)

3. **Download Dataset**
   - Authenticate with Kaggle API
   - Download transcript CSV files
   - Download audio MP3 files
   - Validate file integrity

4. **Create Samples**
   - Read full CSV files with pandas
   - Extract first 200 rows
   - Export to truncated CSV files
   - Verify output structure

---

## 📤 Output Files

After completing this notebook, the following files are created:

```
data/
├── transcripts_raw/
│   ├── lines_clean.csv (full dataset)
│   └── episode_info_clean.csv (full dataset)
├── transcripts_raw_truncated/
│   ├── lines_clean_200.csv (NEW - sample)
│   └── episode_info_clean_200.csv (NEW - sample)
└── audio_raw/
    └── episode_{1-200}.mp3 (full audio files)
```

---

## ➡️ Next Steps

After Week 1 completion:

1. **Week 2 - Audio Preprocessing**
   - Process raw audio files
   - Apply noise reduction and normalization
   - Convert MP3 → WAV format
   - Create 30-second chunks

2. **Week 2 - Speech-to-Text**
   - Run Whisper ASR on audio chunks
   - Generate JSON transcriptions
   - Process all 200 episodes

3. **Week 2 - Quality Evaluation**
   - Compare Whisper output against reference transcripts
   - Calculate Word Error Rate (WER)
   - Identify accuracy patterns

---

## ⚠️ Common Issues

### Dataset Not Found
- Verify Kaggle credentials are set up correctly
- Check disk space availability (need ~7 GB)
- Ensure Google Drive mount successful (if using Colab)

### Import Errors
- Run `pip install -r requirements.txt` to install all dependencies
- Verify pandas version (1.0+)

### Memory Issues
- Reduce batch size when processing large CSVs
- Use `chunksize` parameter in pandas for large files

---

## 📚 References

- **Dataset**: [This American Life - Kaggle](https://www.kaggle.com/datasets/thedevastator/this-american-life-podcast-transcript-dataset)
- **Pandas Documentation**: https://pandas.pydata.org/docs/
- **CSV Format**: RFC 4180 Standard

---

## ⏱️ Estimated Runtime

- **Environment Setup**: 2-5 minutes
- **Dataset Download**: 15-30 minutes (depends on internet speed)
- **Truncated Dataset Creation**: 1-2 minutes
- **Total**: ~20-40 minutes

---

## 📝 Author Notes

This week establishes the foundation for the entire pipeline. All subsequent weeks depend on:
- Correct dataset acquisition
- Proper directory structure
- Validated file integrity

*Ensure all output files are present before proceeding to Week 2.*
