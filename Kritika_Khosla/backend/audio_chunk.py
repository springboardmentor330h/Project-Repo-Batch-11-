# backend/audio_chunk.py

import os
from pydub import AudioSegment


def trim_and_chunk_audio(audio_path, base_folder, chunk_length_ms=120000):
    """
    Trims and chunks audio into fixed-length pieces.
    Saves chunks inside session folder.
    """

    chunks_folder = os.path.join(base_folder, "chunks")
    os.makedirs(chunks_folder, exist_ok=True)

    audio = AudioSegment.from_file(audio_path)

    for i, start in enumerate(range(0, len(audio), chunk_length_ms)):
        end = min(start + chunk_length_ms, len(audio))
        chunk = audio[start:end]

        chunk_file = os.path.join(chunks_folder, f"chunk_{i:03}.wav")
        chunk.export(chunk_file, format="wav")

    print("Audio trimmed and chunked successfully")

    return chunks_folder