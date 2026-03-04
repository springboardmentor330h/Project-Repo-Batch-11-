import whisper
import os

INPUT_DIR = "data/segmented_audio"
OUTPUT_DIR = "data/transcripts"
os.makedirs(OUTPUT_DIR, exist_ok=True)

model = whisper.load_model("base")  # keep base (balanced)

for file in os.listdir(INPUT_DIR):
    if file.endswith(".wav"):
        audio_path = os.path.join(INPUT_DIR, file)
        print(f"Transcribing: {file}")

        result = model.transcribe(
            audio_path,
            fp16=False,
            language="en",
            verbose=False
        )

        out_file = os.path.join(
            OUTPUT_DIR,
            file.replace(".wav", ".txt")
        )

        with open(out_file, "w", encoding="utf-8") as f:
            f.write(result["text"])

        print(f"Saved transcript: {out_file}")
