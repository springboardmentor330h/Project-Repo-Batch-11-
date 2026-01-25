import whisper
import os

model = whisper.load_model("base")

def transcribe_audio(audio_path: str) -> str:
    result = model.transcribe(audio_path)

    if isinstance(result, dict) and "text" in result:
        return result["text"].strip()

    return ""
