import os
import glob
import threading
import json
from src.audio_processor import preprocess_audio
from src.stt_service import transcribe_chunks
from run_week3 import run_pipeline

RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed/chunks"
TRANSCRIPT_DIR = "data/transcripts"
SEGMENTED_DIR = "data/segmented"
METADATA_FILE = "data/podcast_metadata.json"

def update_metadata_status(audio_id, status, extra_data=None):
    """Updates the status and optional metadata of a podcast."""
    if not os.path.exists(METADATA_FILE):
        return
    
    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    
    for item in metadata:
        if str(item["id"]) == str(audio_id):
            item["status"] = status
            if extra_data:
                item.update(extra_data)
            break
            
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)

def process_single_podcast(audio_id, audio_path):
    """Runs the full pipeline for a single audio file."""
    try:
        update_metadata_status(audio_id, "processing")
        
        print(f"\n>>>> STARTING PIPELINE FOR ID: {audio_id} <<<<")
        
        # Step A: Preprocess (Chunking)
        print("--- Preprocessing ---")
        preprocess_audio(audio_path, PROCESSED_DIR, audio_id)
            
        # Step B: STT (Transcription)
        print("--- Transcribing ---")
        transcribe_chunks(PROCESSED_DIR, audio_id, model_size="large-v3", output_dir=TRANSCRIPT_DIR)
            
        # Step C: NLP (Segmentation, Summarization, Sentiment)
        transcript_json = os.path.join(TRANSCRIPT_DIR, f"{audio_id}_transcript.json")
        if os.path.exists(transcript_json):
            print("--- Analyzing (NLP) ---")
            run_pipeline(transcript_json, SEGMENTED_DIR)
            
            # Extract preview info for instant loading
            segmented_path = os.path.join(SEGMENTED_DIR, f"{audio_id}_segmented.json")
            extra_data = {}
            if os.path.exists(segmented_path):
                with open(segmented_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    extra_data = {
                        "segment_count": len(data),
                        "preview_summary": data[0]["summary"] if data else ""
                    }
            
            update_metadata_status(audio_id, "completed", extra_data)
            print(f">>>> PIPELINE COMPLETE FOR ID: {audio_id} <<<<")
        else:
            print(f"Error: Transcript for {audio_id} not found.")
            update_metadata_status(audio_id, "error")

    except Exception as e:
        print(f"Error in pipeline for {audio_id}: {e}")
        update_metadata_status(audio_id, "error")

def start_background_processing(audio_id, audio_path):
    """Starts the pipeline in a background thread."""
    thread = threading.Thread(target=process_single_podcast, args=(audio_id, audio_path))
    thread.start()
    return thread
