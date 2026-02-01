import os
import json
import librosa
import soundfile as sf
from pydub import AudioSegment, effects
import noisereduce as nr
import numpy as np

RAW_DIR = "data/raw_audio"
PROC_DIR = "data/processed_audio"
CHUNK_DIR = "data/chunks_10min"
META_DIR = "data/metadata"

os.makedirs(PROC_DIR, exist_ok=True)
os.makedirs(CHUNK_DIR, exist_ok=True)
os.makedirs(META_DIR, exist_ok=True)

TARGET_SR = 16000
CHUNK_DURATION_MS = 10 * 60 * 1000  # 10 minutes

def preprocess_audio(file_path):
    y, sr = librosa.load(file_path, sr=TARGET_SR, mono=True)

    # Noise reduction
    reduced = nr.reduce_noise(y=y, sr=sr)

    # Save temporary cleaned WAV
    temp_wav = "temp_clean.wav"
    sf.write(temp_wav, reduced, sr, subtype="PCM_16")

    audio = AudioSegment.from_wav(temp_wav)

    # Normalize loudness
    audio = effects.normalize(audio)

    # Trim leading & trailing silence
    audio = audio.strip_silence(silence_len=2000, silence_thresh=-40)

    return audio

for file in os.listdir(RAW_DIR):
    if not file.lower().endswith(".mp3"):
        continue

    print(f"Processing: {file}")
    input_path = os.path.join(RAW_DIR, file)

    audio = preprocess_audio(input_path)

    base = os.path.splitext(file)[0]
    processed_path = os.path.join(PROC_DIR, f"{base}.wav")
    audio.export(processed_path, format="wav")

    # Chunking into 10-min segments
    chunks = []
    for i in range(0, len(audio), CHUNK_DURATION_MS):
        chunk = audio[i:i + CHUNK_DURATION_MS]
        chunk_name = f"{base}_chunk_{i//CHUNK_DURATION_MS}.wav"
        chunk_path = os.path.join(CHUNK_DIR, chunk_name)
        chunk.export(chunk_path, format="wav")

        chunks.append({
            "chunk": chunk_name,
            "start_sec": i / 1000,
            "end_sec": min((i + CHUNK_DURATION_MS) / 1000, len(audio) / 1000)
        })

    # Save metadata
    meta_path = os.path.join(META_DIR, f"{base}.json")
    with open(meta_path, "w") as f:
        json.dump(chunks, f, indent=2)

    print(f"Completed: {file} | Chunks: {len(chunks)}")

print("✅ Audio preprocessing completed successfully.")
