import librosa
import soundfile as sf
import noisereduce as nr
import os


def reduce_audio_noise(input_path,
                       output_folder="../dataset/processed_audio"):
    """
    Apply noise reduction to audio.
    Returns cleaned audio file path.
    """

    # Load normalized audio dynamically
    audio, sr = librosa.load(input_path, sr=16000)

    # Apply noise reduction
    reduced_noise = nr.reduce_noise(y=audio, sr=sr)

    # Create output filename dynamically
    filename = os.path.basename(input_path)
    name_without_ext = os.path.splitext(filename)[0]

    output_path = os.path.join(
        output_folder,
        f"{name_without_ext}_cleaned.wav"
    )

    os.makedirs(output_folder, exist_ok=True)

    # Save cleaned audio
    sf.write(output_path, reduced_noise, sr)

    print("Noise reduction applied successfully")

    return output_path


# Runs only if executed directly
if __name__ == "__main__":
    test_file = "../dataset/processed_audio/podcast_16k_normalized.wav"
    reduce_audio_noise(test_file)