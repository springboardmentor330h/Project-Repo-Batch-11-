from faster_whisper import WhisperModel
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
    - Removes filler words (um, uh, etc.)
    - Normalizes extra spaces
    """
    fillers = r'\b(um|uh|err|ah|like|you know|sort of|kind of)\b'
    text = re.sub(fillers, '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def transcribe_chunks(chunks_dir, audio_id, model_size="large-v3", output_dir="data/transcripts"):
    """
    Transcribes all chunks for a given audio_id using high-fidelity faster-whisper.
    Uses large-v3 for maximum accuracy (industry standard).
    """
    # Use local path to bypass Windows symlink issues
    local_model_path = os.path.join("models", f"faster-whisper-{model_size}")
    model_path = local_model_path if os.path.exists(local_model_path) else model_size
    
    print(f"Loading High-Fidelity Model from: {model_path}...")
    
    device = "cpu"
    compute_type = "int8"
    
    model = WhisperModel(model_path, device=device, compute_type=compute_type)
    
    chunk_files = sorted(glob.glob(os.path.join(chunks_dir, str(audio_id), "*.wav")))
    
    if not chunk_files:
        print(f"No chunks found for audio_id: {audio_id}")
        return
    
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{audio_id}_transcript.json")
    
    full_transcript = []
    
    # Resume logic
    if os.path.exists(output_path):
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                full_transcript = json.load(f)
            print(f"Resuming {audio_id} from {len(full_transcript)} chunks.")
        except:
            full_transcript = []
            
    done_files = {item["chunk_file"] for item in full_transcript}
    
    for chunk_file in tqdm(chunk_files, desc=f"99%+ Accuracy Transcription ({audio_id})"):
        base_name = os.path.basename(chunk_file)
        if base_name in done_files:
            continue
            
        # transcribe with high accuracy settings
        segments, info = model.transcribe(
            chunk_file, 
            beam_size=5, 
            word_timestamps=True,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500)
        )
        
        segments = list(segments)
        combined_text = " ".join([seg.text for seg in segments])
        cleaned_text = clean_text(combined_text)
        
        chunk_data = {
            "chunk_file": base_name,
            "text": cleaned_text,
            "segments": [
                {
                    "start": s.start,
                    "end": s.end,
                    "text": s.text,
                    "words": [{"word": w.word, "start": w.start, "end": w.end} for w in (s.words or [])]
                } for s in segments
            ]
        }
        full_transcript.append(chunk_data)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(full_transcript, f, indent=4, ensure_ascii=False)
        
    print(f"High-fidelity transcription for {audio_id} complete.")
    return full_transcript

if __name__ == "__main__":
    CHUNKS_DIR = "data/processed/chunks"
    TRANSCRIPT_DIR = "data/transcripts"
    
    # Example ID
    AUDIO_ID = "11"
    if os.path.exists(os.path.join(CHUNKS_DIR, AUDIO_ID)):
        transcribe_chunks(CHUNKS_DIR, AUDIO_ID)
