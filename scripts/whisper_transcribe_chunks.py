import os
import whisper
from tqdm import tqdm

# Paths
CHUNKS_DIR = "data/chunks_10min"
OUTPUT_DIR = "data/transcripts"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load Whisper model (CPU-safe)
model = whisper.load_model("base")

audio_files = sorted([
    f for f in os.listdir(CHUNKS_DIR)
    if f.endswith(".wav")
])

for file in tqdm(audio_files, desc="Transcribing chunks"):
    input_path = os.path.join(CHUNKS_DIR, file)
    output_path = os.path.join(
        OUTPUT_DIR, file.replace(".wav", ".txt")
    )

    if os.path.exists(output_path):
        continue  # skip already done files

    result = model.transcribe(
        input_path,
        fp16=False,
        language="en"
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result["text"])

print("✅ All chunk transcriptions completed")
