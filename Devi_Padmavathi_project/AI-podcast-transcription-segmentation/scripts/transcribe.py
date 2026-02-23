from pathlib import Path
import whisper

model = whisper.load_model("base")

AUDIO_DIR = Path("data/wav")
TRANSCRIPT_DIR = Path("transcripts")
TRANSCRIPT_DIR.mkdir(exist_ok=True)

for audio_file in ["79.wav", "83.wav"]:
    audio_path = AUDIO_DIR / audio_file
    result = model.transcribe(str(audio_path))

    out_file = TRANSCRIPT_DIR / audio_file.replace(".wav", ".txt")
    out_file.write_text(result["text"], encoding="utf-8")

    print(f"Saved transcript → {out_file}")