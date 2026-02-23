from pydub import AudioSegment
from pathlib import Path

AUDIO_DIR = Path("data/wav")

selected = []

for wav in AUDIO_DIR.glob("*.wav"):
    audio = AudioSegment.from_wav(wav)
    duration_min = len(audio) / 1000 / 60

    if 45 <= duration_min <= 70:
        selected.append((wav.name, round(duration_min, 2)))

print("Good 1-hour podcasts:\n")
for name, dur in selected:
    print(name, "→", dur, "minutes")