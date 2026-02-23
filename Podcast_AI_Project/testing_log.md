# Week 6 – System Testing Log

## Automated Podcast Transcription Project

**Date:** February 12, 2026  
**Tester:** PSSR Vivek  
**System Version:** Streamlit App v2.0 (with Upload & Analyze tab)

---

## Test Environment

| Item | Details |
|------|---------|
| **OS** | Windows |
| **Python** | 3.x with venv |
| **Models** | Whisper (base), BART-large-CNN, all-MiniLM-L6-v2, KeyBERT, TextBlob |
| **UI** | Streamlit (localhost:8501) |

---

## Podcast Samples Tested

### Sample 1: Genre 1 — Education (English Learning Podcast)

| Field | Details |
|-------|---------|
| **Podcast Name** | English Listening Practice (multiple episodes) |
| **Genre** | Education / English Learning |
| **Episodes Tested** | 154 episodes (e.g., "Pronunciation", "Travel Phrasal Verbs", "Childhood Activities", "Introverts and Extroverts") |
| **Duration Range** | 3–30 minutes per episode |
| **Speakers** | 1–2 speakers (primarily single narrator with occasional conversations) |
| **Audio Quality** | High (studio-recorded podcasts) |
| **Total Segments** | 2,847 |

### Sample 2: Genre 2 — News (Current Affairs Podcast)

| Field | Details |
|-------|---------|
| **Podcast Name** | ILTV News Podcast |
| **Genre** | News / Current Affairs |
| **Episodes Tested** | 1 episode (news_episode_01.mp3) |
| **Duration** | ~30 minutes |
| **Speakers** | Multiple speakers (interview format) |
| **Audio Quality** | Moderate (broadcast quality with background audio) |
| **Total Segments** | 40 |

---

## Testing Results by Area

### 1. Transcription Accuracy

| Metric | Result |
|--------|--------|
| **Overall** | Whisper base model handles clear speech well |
| **Education Genre** | High accuracy — studio-quality audio, single speaker |
| **News Genre** | Moderate accuracy — multiple speakers, some overlapping |

**Issues Found:**
- 498 segments with very short text (<50 characters) — likely due to fragmented transcription of short phrases/idioms in education content
- Some repeated phrases detected in 385 segments — common in educational content ("which means...", "an example would be...")
- No timestamp data preserved from Whisper — segments lack start/end times

**Examples of Short Segments:**
- ID 7: "That train has left the station." (31 chars)
- ID 10: "on top of the world." (20 chars)
- ID 21: "What is the opposite word of warm? It is cool." (47 chars)

---

### 2. Topic Segmentation

| Metric | Result |
|--------|--------|
| **Total Segments** | 2,887 (2,847 education + 40 news) |
| **Min Segment Length** | 1 word |
| **Max Segment Length** | 713 words |
| **Average Segment Length** | 88 words |

**Issues Found:**
- 491 segments contain fewer than 10 words — too small to be meaningful topic segments
- 19 segments exceed 500 words — potentially too large, may contain multiple topics
- Education segments range widely (1–713 words) suggesting inconsistent segmentation
- News segments are more consistent (12–526 words, avg 112)

**Improvement Suggestion:**
- Consider merging very small segments (<10 words) with adjacent ones
- Consider splitting very large segments (>500 words)

---

### 3. Summary Quality

| Metric | Result |
|--------|--------|
| **Summaries Generated** | 2,887/2,887 (100%) |
| **Empty Summaries** | 0 |
| **Very Long (>400 chars)** | 320 summaries |
| **Identical to Text** | 0 |

**Issues Found:**
- 320 summaries exceed 400 characters — could be more concise
- Summaries for short segments sometimes just repeat the full text (expected behavior)
- Education summaries capture lesson content well
- News summaries accurately reflect current affairs topics

**Sample Education Summary:**
> "To go steady with someone, which means to have a more committed and serious relationship with someone. An example would be, James wants to go..."

**Sample News Summary:**
> "Qatar unleashed all of their forces that had been lying in weight, thinking they would finish us off once and for. After October the 7th they..."

---

### 4. Keyword Usefulness

| Metric | Result |
|--------|--------|
| **Keywords Generated** | 2,887/2,887 (100%) |
| **Empty Keywords** | 0 |

**Issues Found:**
- Top keywords are very generic and not topic-specific:
  - "things" (2,094 times), "want" (1,912), "time" (1,767), "think" (1,615)
  - These appear across almost all segments and don't help distinguish topics
- "don" appears 495 times — this is a stopword fragment ("don't") not properly filtered
- More useful keywords like "english" (340), "language" (212) appear lower
- Education segments use TF-IDF which produces common English words
- News segments use KeyBERT which produces slightly better domain keywords

**Improvement Made:**
- News genre keywords were regenerated using KeyBERT for better quality
- Consider reprocessing education keywords with KeyBERT as well

---

### 5. Sentiment Labels

| Metric | Result |
|--------|--------|
| **Sentiment Generated** | 2,887/2,887 (100%) |
| **Score Range** | -0.700 to 1.000 |
| **Average Score** | 0.142 |

**Distribution:**

| Sentiment | Education | News | Total |
|-----------|-----------|------|-------|
| Positive | 1,615 (56.7%) | 0 (0%) | 1,615 (55.9%) |
| Neutral | 1,066 (37.4%) | 40 (100%) | 1,106 (38.3%) |
| Negative | 166 (5.8%) | 0 (0%) | 166 (5.7%) |

**Issues Found:**
- **News genre shows 100% neutral sentiment** — this is likely because the news sentiment was set as default "neutral" during initial segmentation and not properly re-analyzed
- Education sentiment distribution seems reasonable (majority positive for learning content)
- Negative education segments (5.8%) may relate to discussion of difficulties/challenges

**Improvement Needed:**
- Re-run sentiment analysis on news genre segments using TextBlob or similar
- Verify that neutral-heavy distribution makes sense for educational content

---

### 6. UI Behavior

| Feature | Status | Notes |
|---------|--------|-------|
| Genre filter dropdown | ✅ Working | Filters segments correctly |
| Segment timeline | ✅ Working | Color-coded by sentiment |
| Pagination (Prev/Next) | ✅ Working | 50 segments per page |
| Jump to Segment | ✅ Working | Dropdown in sidebar |
| Summary display | ✅ Working | Green success box |
| Keyword display | ✅ Working | Text display |
| Word Cloud | ✅ Working | Viridis colormap |
| Sentiment display | ✅ Working | Color-coded by label |
| Transcript display | ✅ Working | Full text shown |
| Upload & Analyze tab | ✅ Working | Full pipeline runs |
| Audio player | ✅ Working | Plays uploaded audio |

**Issues Found:**
- No loading skeleton when switching between segments
- Word cloud may fail for segments with very few keywords
- Genre Browser sidebar filters remain visible when on Upload tab

---

### 7. Timestamp Correctness

| Status | Details |
|--------|---------|
| ❌ Not Implemented | Segments do not contain timestamp fields |

**Issue:**
- No `start_time` or `end_time` fields exist in segment data
- Whisper transcription does produce timestamps but they are not preserved in the segmentation pipeline
- Users cannot map segments back to specific positions in the audio

---

### 8. Data Completeness

| Field | Missing Count |
|-------|---------------|
| id | 0 |
| title | 0 |
| text | 0 |
| summary | 0 |
| keywords | 0 |
| sentiment | 0 |
| sentiment_score | 0 |
| genre | 2,847 (education segments missing) |

**Issue:**
- 2,847 education segments don't have an explicit `genre` field in the JSON — the app assigns "genre1_education" at runtime as a fallback

---

## Summary of Issues & Improvements

### Issues Identified

| # | Area | Issue | Severity |
|---|------|-------|----------|
| 1 | Segmentation | 491 segments with <10 words (too small) | Medium |
| 2 | Segmentation | 19 segments with >500 words (too large) | Low |
| 3 | Keywords | Top keywords are generic ("things", "want", "time") | Medium |
| 4 | Keywords | Stopword fragment "don" not filtered | Low |
| 5 | Sentiment | News genre shows 100% neutral (not properly analyzed) | High |
| 6 | Data | 2,847 segments missing explicit genre field | Medium |
| 7 | Timestamps | No timestamp data in segments | Medium |
| 8 | Summaries | 320 summaries exceed 400 characters | Low |

### Improvements Made During Week 6

| # | Improvement | Details |
|---|------------|---------|
| 1 | News Summaries | Generated BART summaries for all 40 news segments |
| 2 | News Keywords | Regenerated keywords using KeyBERT for better quality |
| 3 | Upload Feature | Added "Upload & Analyze" tab for real-time audio processing |
| 4 | Pipeline Module | Created reusable `upload_analyzer.py` with full pipeline |
| 5 | UI Polish | Added custom CSS, progress bars, and organized layout |
| 6 | Data Backup | Created backup of segments_final.json before modifications |

---

## Overall Assessment

The system successfully processes podcasts from 2 different genres (education and news) with complete transcription, segmentation, summarization, keyword extraction, and sentiment analysis. The UI provides clear navigation and visualization.

**Key Strengths:**
- Complete end-to-end pipeline from audio to insights
- 100% data completeness for all core fields
- Two-genre support demonstrating versatility
- Interactive Upload & Analyze feature for live demonstrations

**Areas for Future Improvement:**
- Keyword quality needs refinement (too generic for education genre)
- News sentiment analysis needs to be properly re-run
- Very small segments could be merged for better coherence
- Timestamp integration would improve audio navigation
