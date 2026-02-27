# audio_preprocessing.py

import os
import json
import logging
from pathlib import Path

import numpy as np
import librosa
import soundfile as sf
import pyloudnorm as pyln
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError
from scipy.signal import stft, istft

# ================= CONFIG ================= #

INPUT_DIR = Path("audio_input")
PROCESSED_DIR = Path("audio_processed")
CHUNKS_DIR = Path("audio_chunks")

SUPPORTED_FORMATS = [".mp3", ".wav", ".m4a"]

TARGET_SR = 16000
TARGET_LUFS = -16.0
SILENCE_TOP_DB = 40
CHUNK_LENGTH = 120  # seconds
OVERLAP = 30        # seconds

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AudioPipeline")

# ========================================== #


def validate_audio(file_path):
    if file_path.suffix.lower() not in SUPPORTED_FORMATS:
        logger.warning(f"Unsupported format: {file_path.name}")
        return None
    try:
        return AudioSegment.from_file(file_path)
    except CouldntDecodeError:
        logger.error(f"Corrupted file: {file_path.name}")
        return None


def convert_to_standard(audio_segment):
    audio_segment = audio_segment.set_frame_rate(TARGET_SR)
    audio_segment = audio_segment.set_channels(1)
    audio_segment = audio_segment.set_sample_width(2)
    return audio_segment


def spectral_subtraction(y, sr):
    f, t, Zxx = stft(y, fs=sr, nperseg=1024)
    magnitude = np.abs(Zxx)
    phase = np.angle(Zxx)

    noise_estimate = np.mean(magnitude[:, :5], axis=1, keepdims=True)
    cleaned_magnitude = magnitude - noise_estimate
    cleaned_magnitude = np.maximum(cleaned_magnitude, 0)

    Zxx_clean = cleaned_magnitude * np.exp(1j * phase)
    _, cleaned_audio = istft(Zxx_clean, fs=sr)

    return cleaned_audio


def normalize_loudness(y, sr):
    meter = pyln.Meter(sr)
    loudness = meter.integrated_loudness(y)
    return pyln.normalize.loudness(y, loudness, TARGET_LUFS)


def trim_silence(y):
    intervals = librosa.effects.split(y, top_db=SILENCE_TOP_DB)
    if len(intervals) == 0:
        return y
    start = intervals[0][0]
    end = intervals[-1][1]
    return y[start:end]


def chunk_audio(y, sr, episode_name):
    chunk_length_sec = 120  # 2 minutes
    chunk_samples = int(chunk_length_sec * sr)

    total_samples = len(y)

    episode_chunk_dir = CHUNKS_DIR / episode_name
    episode_chunk_dir.mkdir(parents=True, exist_ok=True)

    metadata = []
    index = 0

    for start in range(0, total_samples, chunk_samples):
        end = min(start + chunk_samples, total_samples)

        chunk = y[start:end]

        chunk_name = f"{episode_name}_chunk_{index}.wav"
        chunk_path = episode_chunk_dir / chunk_name

        sf.write(chunk_path, chunk, sr, subtype="PCM_16")

        metadata.append({
            "chunk_name": chunk_name,
            "start_time": start / sr,
            "end_time": end / sr
        })

        index += 1

    return metadata



def process_file(file_path):
    logger.info(f"Processing {file_path.name}")

    audio = validate_audio(file_path)
    if audio is None:
        return

    audio = convert_to_standard(audio)

    episode_name = file_path.stem
    PROCESSED_DIR.mkdir(exist_ok=True)

    temp_wav = PROCESSED_DIR / f"{episode_name}_temp.wav"
    audio.export(temp_wav, format="wav")

    y, sr = librosa.load(temp_wav, sr=TARGET_SR)

    y = spectral_subtraction(y, sr)
    y = normalize_loudness(y, sr)
    y = trim_silence(y)

    final_path = PROCESSED_DIR / f"{episode_name}.wav"
    sf.write(final_path, y, sr, subtype="PCM_16")

    chunks_metadata = chunk_audio(y, sr, episode_name)

    metadata = {
        "episode": episode_name,
        "sample_rate": sr,
        "target_lufs": TARGET_LUFS,
        "chunks": chunks_metadata
    }

    with open(PROCESSED_DIR / f"{episode_name}_metadata.json", "w") as f:
        json.dump(metadata, f, indent=4)

    os.remove(temp_wav)

    logger.info(f"Finished {episode_name}")


def main():
    files = list(INPUT_DIR.glob("*"))
    if not files:
        logger.warning("No audio files found.")
        return

    for file in files:
        process_file(file)


if __name__ == "__main__":
    main()
