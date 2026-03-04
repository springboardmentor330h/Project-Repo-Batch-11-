import os
import json
import whisper
from tqdm import tqdm

CHUNKS_DIR = "data/chunks_10min"
OUTPUT_DIR = "data/transcripts"

os.makedirs(OUTPUT_DIR, exist_ok=True)

model = whisper.load_model("base")

audio_files = sorted([
    f for f in os.listdir(CHUNKS_DIR)
    if f.endswith(".wav")
])

if not audio_files:
    raise RuntimeError("No WAV chunks found in data/chunks_10min")

for file in tqdm(audio_files, desc="Transcribing with timestamps"):
    audio_path = os.path.join(CHUNKS_DIR, file)
    output_path = os.path.join(
        OUTPUT_DIR, file.replace(".wav", ".json")
    )

    if os.path.exists(output_path):
        continue

    result = model.transcribe(
        audio_path,
        fp16=False,
        language="en",
        verbose=False
    )

    transcript_data = {
        "audio_file": file,
        "segments": []
    }

    for seg in result["segments"]:
        transcript_data["segments"].append({
            "start": round(seg["start"], 2),
            "end": round(seg["end"], 2),
            "text": seg["text"].strip()
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(transcript_data, f, indent=2)

print("✅ Timestamped transcription completed")
