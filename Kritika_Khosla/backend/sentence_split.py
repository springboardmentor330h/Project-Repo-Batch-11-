# backend/sentence_split.py

import os
import json
import nltk
from nltk.tokenize import sent_tokenize

nltk.download("punkt")


def segment_transcripts(cleaned_folder, base_folder):
    """
    Reads cleaned transcripts and splits into sentences.
    Returns list of sentences.
    """

    segmented_folder = os.path.join(base_folder, "segmented")
    os.makedirs(segmented_folder, exist_ok=True)

    all_sentences = []

    for file in os.listdir(cleaned_folder):
        if file.endswith(".txt"):
            file_path = os.path.join(cleaned_folder, file)

            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()

            sentences = sent_tokenize(text)
            all_sentences.extend(sentences)

    output_file = os.path.join(segmented_folder, "sentences.json")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_sentences, f, indent=4, ensure_ascii=False)

    print("Sentence segmentation completed")

    return all_sentences