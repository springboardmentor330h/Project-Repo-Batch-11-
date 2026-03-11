import os
import subprocess


def convert_to_wav_16k(audio_path, base_folder):
    """
    Converts input audio to 16kHz mono WAV
    Saves inside session base_folder
    """

    output_path = os.path.join(base_folder, "converted.wav")

    command = [
        "ffmpeg",
        "-y",
        "-i", audio_path,
        "-ar", "16000",
        "-ac", "1",
        output_path
    ]

    subprocess.run(command, check=True)

    return output_path