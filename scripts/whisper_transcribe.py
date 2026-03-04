import os
import whisper

CHUNK_DIR = "data/chunks_10min"
OUT_DIR = "data/transcripts"

os.makedirs(OUT_DIR, exist_ok=True)

model = whisper.load_model("base")

for file in os.listdir(CHUNK_DIR):
    if not file.endswith(".wav"):
        continue

    print(f"Transcribing {file}")
    result = model.transcribe(os.path.join(CHUNK_DIR, file))

    out_path = os.path.join(OUT_DIR, file.replace(".wav", ".txt"))
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(result["text"])

print("✅ Transcription completed.")
