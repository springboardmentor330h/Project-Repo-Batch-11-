import whisper
import json
import os
import glob
import re
from tqdm import tqdm
from static_ffmpeg import add_paths

# Add ffmpeg to the path
add_paths()

def clean_text(text):
    """
    Performs basic text cleaning:
    - Removes filler words (um, uh, etc.) - simple regex
    - Basic punctuation and spacing normalization
    """
    # Simple list of filler words
    fillers = r'\b(um|uh|err|ah|like|you know|sort of|kind of)\b'
    text = re.sub(fillers, '', text, flags=re.IGNORECASE)
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def transcribe_chunks(chunks_dir, audio_id, model_name="base", output_dir="data/transcripts"):
    """
    Transcribes all chunks for a given audio_id and aggregates results.
    """
    print(f"Loading Whisper model: {model_name}...")
    model = whisper.load_model(model_name)
    
    chunk_files = sorted(glob.glob(os.path.join(chunks_dir, str(audio_id), "*.wav")))
    
    if not chunk_files:
        print(f"No chunks found for audio_id: {audio_id}")
        return
    
    os.makedirs(output_dir, exist_ok=True)
    
    full_transcript = []
    
    output_path = os.path.join(output_dir, f"{audio_id}_transcript.json")
    
    # Check for existing transcript to resume
    if os.path.exists(output_path):
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                full_transcript = json.load(f)
            print(f"Resuming {audio_id} from {len(full_transcript)} existing chunks.")
        except Exception as e:
            print(f"Failed to load existing transcript for {audio_id}: {e}")
            full_transcript = []
    else:
        full_transcript = []
    
    done_files = {item["chunk_file"] for item in full_transcript}
    
    for chunk_file in tqdm(chunk_files, desc=f"Transcribing chunks of {audio_id}"):
        base_name = os.path.basename(chunk_file)
        if base_name in done_files:
            continue
            
        result = model.transcribe(chunk_file, verbose=False)
        cleaned_text = clean_text(result["text"])
        
        chunk_data = {
            "chunk_file": base_name,
            "text": cleaned_text,
            "segments": result["segments"]
        }
        full_transcript.append(chunk_data)
        
        # Incremental save
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(full_transcript, f, indent=4, ensure_ascii=False)
        
    print(f"Transcription for {audio_id} complete. Saved to: {output_path}")
    return full_transcript

def process_batch_transcribe(chunks_dir, output_dir, limit=3):
    # Find all subdirectories in chunks_dir (each is an audio_id)
    audio_ids = [os.path.basename(d) for d in glob.glob(os.path.join(chunks_dir, "*")) if os.path.isdir(d)][:limit]
    
    for audio_id in audio_ids:
        transcribe_chunks(chunks_dir, audio_id, model_name="base", output_dir=output_dir)

if __name__ == "__main__":
    import glob
    CHUNKS_DIR = "data/processed/chunks"
    TRANSCRIPT_DIR = "data/transcripts"
    
    # Targeting the ongoing episode (ID 3) to complete it
    AUDIO_ID = 3
    if os.path.exists(os.path.join(CHUNKS_DIR, str(AUDIO_ID))):
        transcribe_chunks(CHUNKS_DIR, AUDIO_ID, model_name="base", output_dir=TRANSCRIPT_DIR)
    else:
        print(f"No chunks found for ID {AUDIO_ID} to resume.")
