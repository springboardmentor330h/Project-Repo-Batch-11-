import os
import json
import nltk
from src.segmentation_service import TopicSegmenter
from src.summarization_service import Summarizer
from src.sentiment_service import SentimentAnalyzer

# Ensure all NLTK data is downloaded
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger_eng')

def run_pipeline(transcript_path, output_dir):
    with open(transcript_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Combine chunk texts into one big transcript
    full_text = " ".join([chunk['text'] for chunk in data])
    audio_id = os.path.basename(transcript_path).replace("_transcript.json", "")
    
    segmenter = TopicSegmenter()
    summarizer = Summarizer()
    sentiment_analyzer = SentimentAnalyzer()
    
    print(f"\n--- Processing Audio ID: {audio_id} ---")
    
    # Step 3 & 4: Implement Topic Segmentation (Algorithms 1 & 3)
    print("Segmenting transcript using Algorithm 1 (Baseline)...")
    baseline_segs = segmenter.segment_transcript_baseline(full_text, threshold=0.55)
    
    print("Segmenting transcript using Algorithm 3 (Embedding-based)...")
    embedding_segs = segmenter.segment_transcript_embedding(full_text)
    
    # Step 5: Compare and Evaluate
    print(f"Algorithm 1 segments: {len(baseline_segs)}")
    print(f"Algorithm 3 segments: {len(embedding_segs)}")
    
    # Usually Embedding-based is better as it captures semantic drift.
    # We will use Algorithm 3 as the 'Final' one for Step 6.
    final_segments = embedding_segs
    
    output_file = os.path.join(output_dir, f"{audio_id}_segmented.json")
    results = []
    
    # Step 7 & 8: Titles, Keywords, and Summaries
    print(f"Generating titles, keywords, and summaries for {len(final_segments)} segments...")
    for i, seg_text in enumerate(final_segments):
        keywords = summarizer.extract_keywords(seg_text)
        summary = summarizer.generate_summary(seg_text)
        title = summarizer.generate_title(seg_text, summary=summary)
        sentiment = sentiment_analyzer.analyze_segment(seg_text)
        
        results.append({
            "segment_id": i + 1,
            "title": title,
            "text": seg_text,
            "keywords": keywords,
            "summary": summary,
            "sentiment": sentiment
        })
        
        # Incremental save
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4)
            
        print(f"Processed Segment {i+1}/{len(final_segments)}: {title}")
    
    print(f"\nWeek 3 results for {audio_id} complete. Saved to {output_file}")
    return results

if __name__ == "__main__":
    TRANSCRIPT_DIR = "data/transcripts"
    OUTPUT_DIR = "data/segmented"
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    transcripts = [f for f in os.listdir(TRANSCRIPT_DIR) if f.endswith("_transcript.json")]
    
    for t in transcripts:
        run_pipeline(os.path.join(TRANSCRIPT_DIR, t), OUTPUT_DIR)
