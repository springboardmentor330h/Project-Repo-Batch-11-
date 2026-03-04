from pydub import AudioSegment
from pydub.effects import normalize
import os

input_path = "data/raw_audio/Infection-Episode-102.mp3"
output_path = "data/preprocessed_audio/pydub_test.wav"

audio = AudioSegment.from_file(input_path)
audio = audio.set_channels(1).set_frame_rate(16000)
audio = normalize(audio)

audio.export(output_path, format="wav")

print("PyDub test completed. Output saved:", output_path)
