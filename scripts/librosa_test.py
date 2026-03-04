import librosa

audio_path = "data/raw_audio/Infection-Episode-102.mp3"

y, sr = librosa.load(audio_path, sr=None)

duration = librosa.get_duration(y=y, sr=sr)

print("LibROSA test completed")
print("Sample Rate:", sr)
print("Duration (seconds):", round(duration, 2))
print("Amplitude range:", min(y), "to", max(y))
