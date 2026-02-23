import os
import numpy as np
import soundfile as sf
import noisereduce as nr
from scipy.signal import resample

RAW = "data/wav_clean"
OUT = "data/processed_audio"
os.makedirs(OUT, exist_ok=True)

TARGET_SR = 16000
CHUNK_SEC = 30

print("Starting audio preprocessing...")

for file in os.listdir(RAW):
    if file.lower().endswith(".mp3") or file.lower().endswith(".wav"):
        print("Processing:", file)

        path = os.path.join(RAW, file)

        # Read MP3/WAV directly (no ffmpeg)
        audio, sr = sf.read(path)

        # Convert to mono
        if audio.ndim > 1:
            audio = np.mean(audio, axis=1)

        # Resample to 16kHz
        if sr != TARGET_SR:
            audio = resample(audio, int(len(audio) * TARGET_SR / sr))

        # Normalize
        audio = audio / np.max(np.abs(audio))

        # Noise reduction
        audio = nr.reduce_noise(y=audio, sr=TARGET_SR)

        chunk_samples = CHUNK_SEC * TARGET_SR
        base = os.path.splitext(file)[0]

        for i in range(0, len(audio), chunk_samples):
            chunk = audio[i:i + chunk_samples]
            if len(chunk) < chunk_samples:
                continue

            out_path = os.path.join(OUT, f"{base}_chunk{i//chunk_samples}.wav")
            sf.write(out_path, chunk, TARGET_SR)

print("Audio preprocessing completed successfully.")
