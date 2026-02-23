import os
from pydub import AudioSegment

input_path = "data/clean"
chunk_path = "data/chunks"
os.makedirs(chunk_path, exist_ok=True)

CHUNK_MS = 30 * 1000  # 30 sec

for file in os.listdir(input_path):
    if not file.endswith(".wav"):
        continue

    audio = AudioSegment.from_wav(os.path.join(input_path, file))

    for i in range(0, len(audio), CHUNK_MS):
        chunk = audio[i:i+CHUNK_MS]
        chunk_name = f"{file.replace('.wav', '')}_chunk{i//CHUNK_MS}.wav"
        chunk.export(os.path.join(chunk_path, chunk_name), format="wav")
        print(f"[+] Created chunk {chunk_name}")

print("\n✔ Chunking Done!")
