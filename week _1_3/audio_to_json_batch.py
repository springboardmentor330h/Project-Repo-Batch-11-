import json
import os
from textblob import TextBlob

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FOLDER = os.path.join(BASE_DIR, "transcripts")

# -------------------------------
# Load Whisper model
# -------------------------------
model = whisper.load_model("base")

# -------------------------------
# Process each audio file
# -------------------------------
for audio_file in os.listdir(AUDIO_DIR):
    if audio_file.endswith((".mp3", ".wav", ".m4a")):
        episode_name = os.path.splitext(audio_file)[0]
        audio_path = os.path.join(AUDIO_DIR, audio_file)

        print(f"Processing {audio_file}...")

        # Transcribe
        result = model.transcribe(audio_path)
        chunks = chunk_text(result["text"])

        segments = []
        for i, chunk in enumerate(chunks):
            segments.append({
                "title": f"{episode_name}_chunk{i}",
                "text": chunk,
                "summary": chunk[:200] + "...",
                "keywords": get_keywords(chunk),
                "sentiment": get_sentiment(chunk)
            })

        # Save JSON
        output_file = f"{episode_name}_segments.json"
        output_path = os.path.join(OUTPUT_DIR, output_file)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(segments, f, indent=2)

        print(f"Saved {output_file}")

print("All episodes converted successfully ✅")
