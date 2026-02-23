import os
import librosa
import soundfile as sf
import noisereduce as nr
import numpy as np

input_path = "data/wav"
output_path = "data/clean"
os.makedirs(output_path, exist_ok=True)

TARGET_SR = 16000

files = sorted([f for f in os.listdir(input_path) if f.endswith(".wav")])
total = len(files)
processed = 0

for idx, file in enumerate(files, 1):
    clean_path = os.path.join(output_path, file)

    # 🔁 SKIP FILE IF ALREADY PROCESSED
    if os.path.exists(clean_path):
        print(f"[SKIP] Already exists: {clean_path}")
        continue

    file_path = os.path.join(input_path, file)
    print(f"[{idx}/{total}] Processing {file} ...")

    try:
        audio, sr = librosa.load(file_path, sr=None)

        # Resample
        if sr != TARGET_SR:
            audio = librosa.resample(audio, orig_sr=sr, target_sr=TARGET_SR)

        # Mono
        if len(audio.shape) > 1:
            audio = librosa.to_mono(audio)

        # Noise reduction
        reduced_noise = nr.reduce_noise(y=audio, sr=TARGET_SR)

        # Normalize
        peak = np.max(np.abs(reduced_noise))
        if peak > 0:
            reduced_noise = reduced_noise / peak

        # Trim silence
        clips = librosa.effects.split(reduced_noise, top_db=30)
        trimmed_segments = [reduced_noise[start:end] for start, end in clips]

        if len(trimmed_segments) > 0:
            trimmed = np.concatenate(trimmed_segments)
        else:
            print(f"[!] No silence trim found, keeping original")
            trimmed = reduced_noise

        sf.write(clean_path, trimmed, TARGET_SR)
        processed += 1

        print(f"✔ Saved Clean: {clean_path}")

    except Exception as e:
        print(f"[ERROR] Failed {file}: {e}")
        continue

print(f"\n🎉 Completed! Processed {processed} new files, skipped {total-processed} already done.")




