import os
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"
import glob
from src.audio_processor import preprocess_audio
from src.stt_service import transcribe_chunks
from run_week3 import run_pipeline

RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed/chunks"
TRANSCRIPT_DIR = "data/transcripts"
SEGMENTED_DIR = "data/segmented"

def run_scaling_pipeline():
    # 1. Identity all raw audio files
    audio_files = glob.glob(os.path.join(RAW_DIR, "*.mp3"))
    print(f"Found {len(audio_files)} raw audio files.")
    
    for audio_path in audio_files:
        audio_id = os.path.basename(audio_path).replace(".mp3", "")
        print(f"\n>>>> STARTING PIPELINE FOR ID: {audio_id} <<<<")
        
        # Target output
        final_json = os.path.join(SEGMENTED_DIR, f"{audio_id}_segmented.json")
        if os.path.exists(final_json):
            print(f"Skipping ID {audio_id} - already processed.")
            continue
            
        # Step A: Preprocess (Chunking)
        chunk_dir = os.path.join(PROCESSED_DIR, audio_id)
        if not os.path.exists(chunk_dir) or not os.listdir(chunk_dir):
            print("--- Preprocessing ---")
            preprocess_audio(audio_path, PROCESSED_DIR, audio_id)
        else:
            print("--- Skipping Preprocessing (chunks exist) ---")
            
        # Step B: STT (Transcription)
        transcript_json = os.path.join(TRANSCRIPT_DIR, f"{audio_id}_transcript.json")
        if not os.path.exists(transcript_json):
            print("--- Transcribing ---")
            transcribe_chunks(PROCESSED_DIR, audio_id, model_size="large-v3", output_dir=TRANSCRIPT_DIR)
        else:
            print("--- Skipping Transcription (transcript exists) ---")
            
        # Step C: NLP (Segmentation, Summarization, Sentiment)
        if os.path.exists(transcript_json):
            print("--- Analyzing (NLP) ---")
            run_pipeline(transcript_json, SEGMENTED_DIR)
        else:
            print(f"Error: Transcript for {audio_id} not found. Skipping NLP.")

if __name__ == "__main__":
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    os.makedirs(TRANSCRIPT_DIR, exist_ok=True)
    os.makedirs(SEGMENTED_DIR, exist_ok=True)
    run_scaling_pipeline()
