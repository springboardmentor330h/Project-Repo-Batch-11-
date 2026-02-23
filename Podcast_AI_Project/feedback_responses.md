# User Feedback Responses — Podcast AI Analysis System

## Respondent 1: Priya Sharma (Computer Science, 3rd Year)

**Date:** February 10, 2026

### Interface & Usability

**1. How easy was it to navigate between genres and segments? (1-5)**
4 — Pretty easy to use. The sidebar dropdown is convenient and genre filter works well. Took me a moment to figure out the timeline numbering but once I clicked one it made sense.

**2. How visually appealing is the interface? (1-5)**
4 — The dark theme looks modern and professional. The sentiment-colored dots in the timeline are a nice touch. Word clouds are visually engaging.

**3. Were you able to find the information you needed easily?**
Yes. The layout is intuitive — genre on top, segment selector, then the details flow naturally below. I liked how the summary, keywords, and sentiment are all on one page.

**4. Any UI elements that were confusing or hard to use?**
The Prev/Next buttons could be bigger. With 2800+ segments it takes many clicks to get to the middle. Maybe add a page number input or slider.

### Content Quality

**5. How accurate were the segment summaries? (1-5)**
3 — Most summaries captured the main topic, but some were too generic. A few education segments had summaries that felt like they missed the nuance of the discussion.

**6. How relevant were the extracted keywords? (1-5)**
3 — Keywords like "english", "going", "want" are too common and don't tell me much about the actual topic. More specific keywords would be better.

**7. How useful was the sentiment analysis? (1-5)**
4 — The sentiment mostly matched what I'd expect from reading the transcript. News segments being mostly neutral makes sense for factual reporting.

**8. Were the word clouds helpful for understanding content?**
Yes, they give a quick visual overview of what each segment is about. The color scheme is nice. Would be more useful if the generic words were filtered out.

### Upload & Analyze Feature

**9. Did you try uploading your own audio? If yes, how was the experience?**
I tried uploading a 2-minute voice recording. The processing took about 3 minutes which felt a bit long, but the progress bar helped. The results were accurate — it correctly identified the two topics I spoke about and separated them into segments.

**10. Were the analysis results for uploaded audio accurate?**
Mostly yes. The transcription was very accurate (Whisper is impressive). The topic segmentation split my recording into 3 segments which was reasonable. Keywords were more relevant for my audio than for the pre-loaded data.

### Overall Experience

**11. What did you like most about the system?**
The end-to-end pipeline is impressive — going from raw audio to summaries, keywords, and sentiment in one click. The timeline visualization with sentiment colors is creative.

**12. What improvements would you suggest?**
- Filter out common/stop words from keywords
- Add timestamps to segments so I know where to listen in the original audio
- Maybe add a search feature to find segments by keyword
- The loading time for the full page with 2800+ segments could be optimized

---

## Respondent 2: Rahul Menon (IT Engineering, 3rd Year)

**Date:** February 11, 2026

### Interface & Usability

**1. How easy was it to navigate between genres and segments? (1-5)**
5 — Very straightforward. I liked that switching genres automatically updated the segment list. The Jump to Segment dropdown is useful for large datasets.

**2. How visually appealing is the interface? (1-5)**
4 — Clean and professional look. The tab layout separating Browse and Upload is good. Dark theme suits a data analysis tool.

**3. Were you able to find the information you needed easily?**
Yes, everything is well-organized. Each segment shows all relevant info — title, summary, keywords, word cloud, sentiment, and transcript — in a logical order.

**4. Any UI elements that were confusing or hard to use?**
Nothing major. I'd suggest highlighting the currently selected segment in the timeline grid so you know which one you're viewing.

### Content Quality

**5. How accurate were the segment summaries? (1-5)**
4 — The BART model does a decent job. News summaries were particularly good — concise and captured the main points. Education summaries were hit or miss.

**6. How relevant were the extracted keywords? (1-5)**
3 — Some keywords were too generic. Words like "things", "time", "people" appeared in many education segments. The news segment keywords were much better and more specific.

**7. How useful was the sentiment analysis? (1-5)**
3 — It's a nice feature but most segments showed neutral which isn't very informative. The positive/negative segments in education were more interesting to explore.

**8. Were the word clouds helpful for understanding content?**
They're visually appealing but only truly useful when the keywords are specific. For segments with generic keywords, the word cloud doesn't add much value.

### Upload & Analyze Feature

**9. Did you try uploading your own audio? If yes, how was the experience?**
Yes, I uploaded a short podcast clip (about 1.5 minutes). It worked! The transcription was surprisingly accurate even with some background noise. Processing time was reasonable.

**10. Were the analysis results for uploaded audio accurate?**
The transcription was 90%+ accurate. Segmentation made sense — it split the audio into topic chunks correctly. Sentiment was accurate for the positive/motivational content I uploaded.

### Overall Experience

**11. What did you like most about the system?**
The fact that it's a complete pipeline from audio to insights. Being able to upload my own audio and get the same analysis is a great demo feature. The genre-based browsing is well thought out.

**12. What improvements would you suggest?**
- Add ability to export analysis results as PDF or CSV
- Show word count per segment
- Allow downloading the transcript
- Consider adding speaker diarization for podcasts with multiple speakers

---

## Respondent 3: Anjali Reddy (Data Science, 4th Year)

**Date:** February 11, 2026

### Interface & Usability

**1. How easy was it to navigate between genres and segments? (1-5)**
4 — Good navigation overall. The genre filter and segment selector work well together. Timeline pagination with 50 segments per page is a reasonable batch size.

**2. How visually appealing is the interface? (1-5)**
3 — It's functional and clean but could be more visually distinct. The segment detail area could use better formatting — maybe cards with borders instead of plain text sections.

**3. Were you able to find the information you needed easily?**
Yes, the information hierarchy makes sense. I'd love a search/filter option to find segments by keyword across the entire dataset.

**4. Any UI elements that were confusing or hard to use?**
The sentiment emoji colors (green/red/blue) in the timeline are subtle. A legend or tooltip explaining them would help new users.

### Content Quality

**5. How accurate were the segment summaries? (1-5)**
3 — Variable quality. Some education segments had excellent summaries, while others were either too long or missed key points. The BART model seems to work better with news-style content.

**6. How relevant were the extracted keywords? (1-5)**
2 — This needs the most improvement. Many education keywords are too generic. Using TF-IDF or removing stop words more aggressively would help. KeyBERT on news segments was better.

**7. How useful was the sentiment analysis? (1-5)**
4 — TextBlob is simple but effective enough for a first version. I'd suggest trying VADER or a transformer-based sentiment model for better accuracy.

**8. Were the word clouds helpful for understanding content?**
Somewhat. They're more of a visual decoration in their current state. With better keywords, they'd be much more informative.

### Upload & Analyze Feature

**9. Did you try uploading your own audio? If yes, how was the experience?**
Yes, I tested with a 3-minute educational lecture recording. The pipeline handled it well. I was impressed that it automatically segmented the content by topic — it correctly identified when the speaker changed subjects.

**10. Were the analysis results for uploaded audio accurate?**
Transcription was very good (Whisper base model). Segmentation was logical. The summaries for my uploaded audio were actually better than many pre-loaded education summaries, probably because my audio had clearer topic transitions.

### Overall Experience

**11. What did you like most about the system?**
The Upload & Analyze feature is the highlight. Being able to process any audio file through the complete NLP pipeline demonstrates the system's capabilities really well. It's practical and not just a static demo.

**12. What improvements would you suggest?**
- Better keyword extraction (KeyBERT with custom stop words)
- Add confidence scores for the transcription
- Include segment duration/timestamps
- Add a comparison view to see two segments side by side
- Consider batch upload for multiple audio files
- The app could be slow with very large files — add a file size warning

---

## Summary of Feedback Scores

| Question | Priya | Rahul | Anjali | Average |
|----------|-------|-------|--------|---------|
| Navigation ease | 4 | 5 | 4 | **4.3** |
| Visual appeal | 4 | 4 | 3 | **3.7** |
| Summary accuracy | 3 | 4 | 3 | **3.3** |
| Keyword relevance | 3 | 3 | 2 | **2.7** |
| Sentiment usefulness | 4 | 3 | 4 | **3.7** |

### Key Themes from Feedback
1. **Navigation** — Generally positive, users found it easy to use
2. **Keywords** — Weakest area, too generic for education genre
3. **Upload feature** — Most praised feature, considered the highlight
4. **Summaries** — Adequate but inconsistent quality across genres
5. **Suggestions** — Search, export, timestamps, and better keywords were common requests
