# backend/pipeline.py

import os
import json

from .audio_convert import convert_to_wav_16k
from .audio_chunk import trim_and_chunk_audio
from .transcribe_all import transcribe_audio_folder
from .clean_transcripts import clean_transcripts
from .sentence_split import segment_transcripts
from .topic_segmentation_embeddings import segment_topics_embeddings
from .summarization import generate_summary
from .sentiment_analysis import analyze_sentiment
from .keyword_extraction import extract_keywords


def run_full_pipeline(audio_path, session_id):
    """
    Runs complete AI audio analysis pipeline
    Each upload is isolated using session_id
    """

    # 🔥 Create isolated working directory
    base_folder = os.path.join("dataset", "uploads", session_id)
    os.makedirs(base_folder, exist_ok=True)

    print("Step 1: Converting audio")
    converted_path = convert_to_wav_16k(audio_path, base_folder)

    print("Step 2: Chunking audio")
    chunks_folder = trim_and_chunk_audio(converted_path, base_folder)

    print("Step 3: Transcribing audio")
    transcripts_folder = transcribe_audio_folder(chunks_folder, base_folder)

    print("Step 4: Cleaning transcripts")
    cleaned_folder = clean_transcripts(transcripts_folder, base_folder)

    print("Step 5: Sentence segmentation")
    segmented_folder = segment_transcripts(cleaned_folder, base_folder)

    print("Step 6: Topic segmentation")
    topics = segment_topics_embeddings(
        segmented_folder,
        min_blocks_per_topic=8,
        similarity_drop_percentile=10
    )

    print("Step 7: Generating insights")

    results = []

    for topic_text in topics:

        if not topic_text or len(topic_text.strip()) < 50:
            continue

        try:
            summary = generate_summary(topic_text)
        except Exception as e:
            print("Summary error:", e)
            summary = ""

        try:
            sentiment = analyze_sentiment(topic_text)
        except Exception as e:
            print("Sentiment error:", e)
            sentiment = "Neutral"

        try:
            keywords = extract_keywords(topic_text)
        except Exception as e:
            print("Keyword error:", e)
            keywords = []

        results.append({
            "summary": summary,
            "sentiment": sentiment,
            "keywords": keywords
        })

    # 🔥 Save result per session
    result_file = os.path.join(base_folder, "result.json")

    with open(result_file, "w", encoding="utf-8") as f:
        json.dump({"topics": results}, f, indent=4, ensure_ascii=False)

    print("Pipeline completed successfully")

    return {"topics": results}