# backend/transcribe_all.py

import os
import whisper

print("Loading Whisper model (this happens only once)...")
model = whisper.load_model("base")


def transcribe_audio_folder(chunks_folder, base_folder):
    """
    Transcribes all audio chunks inside folder.
    Saves transcripts inside session folder.
    """

    transcripts_folder = os.path.join(base_folder, "transcripts")
    os.makedirs(transcripts_folder, exist_ok=True)

    audio_files = sorted([
        f for f in os.listdir(chunks_folder)
        if f.endswith(".wav")
    ])

    print(f"Found {len(audio_files)} audio files")

    for i, file in enumerate(audio_files, start=1):
        file_path = os.path.join(chunks_folder, file)

        print(f"[{i}/{len(audio_files)}] Transcribing {file}")

        result = model.transcribe(file_path)
        text = result["text"].strip()

        output_file = os.path.join(
            transcripts_folder,
            file.replace(".wav", ".txt")
        )

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text)

    print("All files processed.")

    return transcripts_folder