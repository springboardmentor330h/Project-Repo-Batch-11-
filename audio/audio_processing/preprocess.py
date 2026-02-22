import os
import librosa
import soundfile as sf
import numpy as np


RAW_AUDIO_DIR = "data/raw_audio"
PROCESSED_AUDIO_DIR = "data/processed_audio"

TARGET_SAMPLE_RATE = 16000
SILENCE_TOP_DB = 30


def reduce_noise(audio: np.ndarray) -> np.ndarray:
    stft = librosa.stft(audio)
    magnitude, phase = librosa.magphase(stft)

    noise_profile = np.median(magnitude, axis=1, keepdims=True)
    reduced_magnitude = np.maximum(magnitude - noise_profile, 0)

    reduced_stft = reduced_magnitude * phase
    return librosa.istft(reduced_stft)


def preprocess_audio(filename: str):
    input_path = os.path.join(RAW_AUDIO_DIR, filename)
    base_name = os.path.splitext(filename)[0]
    output_path = os.path.join(PROCESSED_AUDIO_DIR, base_name + ".wav")

    print(f"🔊 Processing: {filename}")

    audio, sr = librosa.load(
        input_path,
        sr=TARGET_SAMPLE_RATE,
        mono=True
    )

    audio = reduce_noise(audio)

    audio = librosa.util.normalize(audio)

    audio, _ = librosa.effects.trim(
        audio,
        top_db=SILENCE_TOP_DB
    )

    sf.write(output_path, audio, TARGET_SAMPLE_RATE)

    print(f"[SUCCESS] Saved cleaned audio to: {output_path}")


if __name__ == "__main__":
    os.makedirs(PROCESSED_AUDIO_DIR, exist_ok=True)

    for file in os.listdir(RAW_AUDIO_DIR):
        if file.lower().endswith((".mp3", ".wav")):
            preprocess_audio(file)

    print("[SUCCESS] Audio preprocessing completed (no chunking).")
