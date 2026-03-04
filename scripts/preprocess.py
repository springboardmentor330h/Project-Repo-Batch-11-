import librosa
import soundfile as sf
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INPUT_DIR = os.path.join(BASE_DIR, "data", "raw_audio")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "processed_audio")

os.makedirs(OUTPUT_DIR, exist_ok=True)

for file in os.listdir(INPUT_DIR):
    if file.endswith(".mp3"):
        audio_path = os.path.join(INPUT_DIR, file)
        y, sr = librosa.load(audio_path, sr=16000, mono=True)

        out_path = os.path.join(
            OUTPUT_DIR,
            file.replace(".mp3", ".wav")
        )

        sf.write(out_path, y, sr)
        print(f"Processed: {file}")
