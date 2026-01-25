import librosa
import numpy as np
import matplotlib.pyplot as plt

def explore_audio(file_path):
    print(f"Exploring audio file: {file_path}")
    y, sr = librosa.load(file_path, sr=None)
    
    duration = librosa.get_duration(y=y, sr=sr)
    print(f"Sample Rate: {sr} Hz")
    print(f"Duration: {duration:.2f} seconds")
    print(f"Max Amplitude: {np.max(np.abs(y)):.4f}")
    print(f"Mean Amplitude: {np.mean(y):.4f}")
    
    # Save a waveform plot
    plt.figure(figsize=(10, 4))
    librosa.display.waveshow(y, sr=sr)
    plt.title(f"Waveform of {file_path}")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.tight_layout()
    plt.savefig("eda_waveform.png")
    print("Waveform saved to eda_waveform.png")

if __name__ == "__main__":
    explore_audio("data/raw/audio/episode_sample.wav")
