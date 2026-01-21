import os
import subprocess
from tqdm import tqdm

INPUT_DIR = "episodes"

def preprocess_audio(input_path, temp_output_path):
    """
    Applies:
    1) Noise reduction
    2) Loudness normalization
    3) Silence trimming
    """

    filter_chain = (
        "afftdn,"  # noise reduction
        "loudnorm=I=-16:LRA=11:TP=-1.5,"  # loudness normalization
        "silenceremove=start_periods=1:start_duration=1:start_threshold=-50dB:"
        "stop_periods=1:stop_duration=1:stop_threshold=-50dB"  # silence trimming
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-af", filter_chain,
        temp_output_path
    ]

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False


def main():
    files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".resampled.wav")]

    print(f"Found {len(files)} files")

    for f in tqdm(files):
        input_path = os.path.join(INPUT_DIR, f)
        temp_path = os.path.join(INPUT_DIR, f.replace(".resampled.wav", ".tmp.wav"))

        ok = preprocess_audio(input_path, temp_path)

        if not ok:
            print(f"[FAIL] {f}")
            continue

        # Replace original with processed
        try:
            os.replace(temp_path, input_path)
        except Exception as e:
            print(f"[REPLACE FAIL] {f}: {e}")

    print("Done preprocessing.")


if __name__ == "__main__":
    main()
