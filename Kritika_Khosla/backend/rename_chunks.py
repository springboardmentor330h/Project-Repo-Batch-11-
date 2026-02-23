import os


def rename_audio_chunks(chunk_folder):
    """
    Rename all .wav files in a folder to audio_001.wav format.
    Returns list of renamed file paths.
    """

    if not os.path.exists(chunk_folder):
        print("Chunk folder does not exist.")
        return []

    files = sorted(
        [f for f in os.listdir(chunk_folder) if f.endswith(".wav")]
    )

    if not files:
        print("No .wav files found.")
        return []

    renamed_files = []

    # Temporary rename to avoid overwrite conflicts
    temp_files = []
    for filename in files:
        old_path = os.path.join(chunk_folder, filename)
        temp_path = os.path.join(chunk_folder, f"temp_{filename}")
        os.rename(old_path, temp_path)
        temp_files.append(temp_path)

    # Final rename
    for i, temp_path in enumerate(sorted(temp_files), start=1):
        new_name = f"audio_{i:03d}.wav"
        new_path = os.path.join(chunk_folder, new_name)

        os.rename(temp_path, new_path)
        renamed_files.append(new_path)

    print("All chunks renamed successfully.")

    return renamed_files


# Optional standalone execution
if __name__ == "__main__":
    folder = "../dataset/processed_audio/chunks"
    rename_audio_chunks(folder)