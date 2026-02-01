import os
import librosa
import soundfile as sf
import noisereduce as nr
import numpy as np
from pydub import AudioSegment, effects

class AudioPreprocessor:
    def __init__(self, target_sr=16000):
        self.target_sr = target_sr

    def process(self, input_path, output_path):
        """
        Full preprocessing pipeline:
        1. Load audio (resample to 16kHz, mono)
        2. Noise Reduction (using noisereduce)
        3. Normalization (using pydub)
        4. Trim Silence
        5. Export as WAV
        """
        print(f"Preprocessing {input_path}...")
        
        # 1. Load with Librosa
        y, sr = librosa.load(input_path, sr=self.target_sr, mono=True)

        # 2. Noise Reduction
        reduced_y = nr.reduce_noise(y=y, sr=sr, prop_decrease=0.6)

        # Temp save for Pydub
        temp_wav = input_path + "_temp.wav"
        sf.write(temp_wav, reduced_y, sr, subtype="PCM_16")

        # 3. Load into Pydub
        audio = AudioSegment.from_wav(temp_wav)

        # 4. Normalize
        audio = effects.normalize(audio)

        # 5. Trim Silence (Lead/Trail)
        audio = audio.strip_silence(silence_len=1000, silence_thresh=-40)

        # Export
        audio.export(output_path, format="wav")
        
        # Cleanup temp
        if os.path.exists(temp_wav):
            os.remove(temp_wav)
            
        return output_path

if __name__ == "__main__":
    print("AudioPreprocessor module loaded.")
