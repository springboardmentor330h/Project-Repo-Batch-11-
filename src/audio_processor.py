import librosa
import soundfile as sf
import numpy as np
import os
import noisereduce as nr
from pydub import AudioSegment
from static_ffmpeg import add_paths

add_paths()

def preprocess_audio(input_path, output_dir, audio_id):
    """
    Preprocesses a single audio file:
    1. Resample to 16kHz
    2. Mono conversion
    3. Noise reduction
    4. Normalization
    5. Chunking into 20-30s segments
    """
    print(f"Preprocessing audio: {input_path}")
    
    try:
        # Load audio at 16kHz mono, limited to 45 minutes (2700 seconds)
        print(f"Loading first 45 minutes of {input_path}...")
        y, sr = librosa.load(input_path, sr=16000, mono=True, duration=2700)
        
        # Noise reduction
        print("Applying noise reduction...")
        y_denoised = nr.reduce_noise(y=y, sr=sr)
        
        # Normalization (Root Mean Square normalization)
        print("Applying normalization...")
        y_norm = librosa.util.normalize(y_denoised)
        
        # Silence trimming
        y_trimmed, _ = librosa.effects.trim(y_norm, top_db=25)
        
        # Chunking: 20-30 seconds
        chunk_length_s = 25
        chunk_samples = chunk_length_s * sr
        
        total_samples = len(y_trimmed)
        num_chunks = int(np.ceil(total_samples / chunk_samples))
        
        chunk_dir = os.path.join(output_dir, str(audio_id))
        os.makedirs(chunk_dir, exist_ok=True)
        
        chunk_info = []
        
        for i in range(num_chunks):
            start_sample = i * chunk_samples
            end_sample = min((i + 1) * chunk_samples, total_samples)
            
            chunk = y_trimmed[start_sample:end_sample]
            
            chunk_file = os.path.join(chunk_dir, f"chunk_{i}.wav")
            sf.write(chunk_file, chunk, sr)
            
            chunk_info.append({
                "audio_id": audio_id,
                "chunk_id": i,
                "file_path": chunk_file,
                "start_time": (start_sample / sr),
                "end_time": (end_sample / sr)
            })
            
        print(f"Successfully chunked {audio_id} into {num_chunks} segments.")
        return chunk_info
        
    except Exception as e:
        print(f"Error processing {input_path}: {e}")
        return []

def process_batch(input_dir, output_base_dir, limit=3):
    files = glob.glob(os.path.join(input_dir, "raw_*.mp3"))[:limit]
    all_chunks = {}
    
    for f in files:
        audio_id = os.path.basename(f).replace("raw_", "").replace(".mp3", "")
        chunks = preprocess_audio(f, output_base_dir, audio_id)
        all_chunks[audio_id] = chunks
    
    return all_chunks

if __name__ == "__main__":
    import glob
    RAW_DIR = "data/raw/audio_samples"
    PROCESSED_BASE = "data/processed/chunks"
    
    process_batch(RAW_DIR, PROCESSED_BASE, limit=3)
