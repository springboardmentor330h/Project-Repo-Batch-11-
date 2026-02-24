from pydub import AudioSegment
import os

INPUT_DIR = "raw_audio"
OUTPUT_DIR = "processed_chunks"

INTRO_TRIM_MS = 6000
OUTRO_TRIM_MS = 6000   
CHUNK_LENGTH_MS = 29 * 1000 

os.makedirs(OUTPUT_DIR, exist_ok=True)

for filename in os.listdir(INPUT_DIR):
    if not filename.endswith(".wav"):
        continue

    print(f"Processing: {filename}")

    audio_path = os.path.join(INPUT_DIR, filename)
    audio = AudioSegment.from_wav(audio_path)
 
    if len(audio) > (INTRO_TRIM_MS + OUTRO_TRIM_MS):
        audio = audio[INTRO_TRIM_MS : len(audio) - OUTRO_TRIM_MS]

    base_name = filename.replace(".wav", "")
    
    for i in range(0, len(audio), CHUNK_LENGTH_MS):
        chunk = audio[i : i + CHUNK_LENGTH_MS]

        chunk_filename = f"{base_name}_chunk_{i // CHUNK_LENGTH_MS}.wav"
        chunk_path = os.path.join(OUTPUT_DIR, chunk_filename)

        chunk.export(chunk_path, format="wav")

print("Audio preprocessing completed for all files")


