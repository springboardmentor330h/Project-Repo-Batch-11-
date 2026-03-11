# backend/clean_transcripts.py

import os
import re


def clean_transcripts(transcripts_folder, base_folder):
    """
    Cleans transcript files and saves cleaned versions.
    """

    cleaned_folder = os.path.join(base_folder, "cleaned")
    os.makedirs(cleaned_folder, exist_ok=True)

    for file in os.listdir(transcripts_folder):
        if file.endswith(".txt"):
            input_path = os.path.join(transcripts_folder, file)

            with open(input_path, "r", encoding="utf-8") as f:
                text = f.read()

            # Basic cleaning
            text = re.sub(r"\s+", " ", text)
            text = text.strip()

            output_path = os.path.join(cleaned_folder, file)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text)

    print("All transcripts cleaned and normalized.")

    return cleaned_folder