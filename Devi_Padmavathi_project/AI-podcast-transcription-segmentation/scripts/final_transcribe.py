import whisper
import json
import os

# ---------------- CONFIG ----------------
AUDIO_DIR = "data/wav"          # adjust ONLY if your wav folder is elsewhere
OUTPUT_DIR = "transcripts"
MODEL_SIZE = "base"

PODCAST_IDS = [
    "2695", "2716", "54715",
    "61300", "61301", "61302",
    "64196", "79", "83", "103"
]
# ----------------------------------------

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("Loading Whisper model...")
model = whisper.load_model(MODEL_SIZE)

for pid in PODCAST_IDS:
    audio_path = os.path.join(AUDIO_DIR, f"{pid}.wav")

    if not os.path.exists(audio_path):
        print(f"❌ Missing audio: {audio_path}")
        continue

    print(f"🎙️ Transcribing {pid}.wav")

    result = model.transcribe(audio_path, language="en", verbose=False)

    segments = []
    for seg in result["segments"]:
        segments.append({
            "start": round(seg["start"], 2),
            "end": round(seg["end"], 2),
            "text": seg["text"].strip()
        })

    output_path = os.path.join(OUTPUT_DIR, f"{pid}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(segments, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved → {output_path}")

print("🎉 Transcription completed.")
