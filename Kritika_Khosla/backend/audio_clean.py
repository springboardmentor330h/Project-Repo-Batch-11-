from pydub import AudioSegment
from pydub.effects import normalize
import os


def normalize_audio(input_path, output_folder="../dataset/processed_audio"):
    """
    Normalize audio volume.
    Takes input file path and saves normalized file.
    Returns output file path.
    """

    # Load audio dynamically
    audio = AudioSegment.from_wav(input_path)

    # Normalize
    normalized_audio = normalize(audio)

    # Create output filename automatically
    filename = os.path.basename(input_path)
    name_without_ext = os.path.splitext(filename)[0]

    output_path = os.path.join(
        output_folder,
        f"{name_without_ext}_normalized.wav"
    )

    # Export normalized file
    normalized_audio.export(output_path, format="wav")

    print("Audio normalized successfully")

    return output_path


# This part runs only if file executed directly
if __name__ == "__main__":
    test_file = "../dataset/processed_audio/podcast_16k.wav"
    normalize_audio(test_file)