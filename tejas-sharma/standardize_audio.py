from pydub import AudioSegment
import soundfile as sf
import numpy as np
import noisereduce as nr
import os

INPUT_DIR = "raw_audio"
OUTPUT_DIR = "standardized_audio"

os.makedirs(OUTPUT_DIR, exist_ok=True)

for filename in os.listdir(INPUT_DIR):
    if not filename.lower().endswith((".wav", ".mp3")):
        continue

    print(f"Standardizing: {filename}")

    input_path = os.path.join(INPUT_DIR, filename)

    audio = AudioSegment.from_file(input_path)

    audio = audio.set_channels(1)

    audio = audio.set_frame_rate(16000)

    temp_path = "temp.wav"
    audio.export(temp_path, format="wav")

    data, sr = sf.read(temp_path)

    reduced_audio = nr.reduce_noise(y=data, sr=sr)


    normalized_audio = reduced_audio / np.max(np.abs(reduced_audio))

    base_name = os.path.splitext(filename)[0]
    output_path = os.path.join(OUTPUT_DIR, f"{base_name}_standardized.wav")

    sf.write(output_path, normalized_audio, sr)

    os.remove(temp_path)

print("Audio standardization completed for all files.")
