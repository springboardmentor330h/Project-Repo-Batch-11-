import os
from pydub import AudioSegment

RAW_DIR = "./data/raw/AUDIO"
WAV_DIR = "./data/wav"

os.makedirs(WAV_DIR, exist_ok=True)

for file in os.listdir(RAW_DIR):
    if file.endswith(".mp3"):
        mp3_path = os.path.join(RAW_DIR, file)
        wav_path = os.path.join(WAV_DIR, file.replace(".mp3", ".wav"))

        print(f"[+] Converting {file} → WAV")
        
        audio = AudioSegment.from_mp3(mp3_path)
        audio = audio.set_frame_rate(16000).set_channels(1)
        audio.export(wav_path, format="wav")

print("✔ Conversion to WAV Completed!")
