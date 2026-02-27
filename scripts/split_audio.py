from pydub import AudioSegment
import os

INPUT_DIR = "data/raw_audio"
OUTPUT_DIR = "data/processed_audio"  # Relative path
CHUNK_LENGTH_MS = 5 * 60 * 1000  # 5 minutes

os.makedirs(OUTPUT_DIR, exist_ok=True)

for file in os.listdir(INPUT_DIR):
    if file.endswith(".mp3"):
        audio_path = os.path.join(INPUT_DIR, file)
        audio = AudioSegment.from_mp3(audio_path)

        base_name = os.path.splitext(file)[0]

        for i, start in enumerate(range(0, len(audio), CHUNK_LENGTH_MS)):
            chunk = audio[start:start + CHUNK_LENGTH_MS]
            out_path = os.path.join(
                OUTPUT_DIR, f"{base_name}_part{i+1}.wav"
            )
            chunk.export(out_path, format="wav")

        print(f"Split completed: {file}")
