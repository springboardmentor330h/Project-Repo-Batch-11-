import whisper

audio_path = "data/preprocessed_audio/pydub_test.wav"

model = whisper.load_model("base")
result = model.transcribe(audio_path)

print("Whisper test completed")
print("Transcript preview:")
print(result["text"][:500])
