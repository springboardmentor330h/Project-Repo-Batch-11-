import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRANSCRIPTS_DIR = os.path.join(BASE_DIR, "..", "data", "transcripts_txt")
OUTPUT_DIR = os.path.join(BASE_DIR, "..", "results", "sentences")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def split_into_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if len(s.strip()) > 0]

count = 0

for filename in os.listdir(TRANSCRIPTS_DIR):
    if not filename.endswith(".txt"):
        continue

    with open(os.path.join(TRANSCRIPTS_DIR, filename), "r", encoding="utf-8") as f:
        text = f.read()

    sentences = split_into_sentences(text)

    out_file = os.path.join(OUTPUT_DIR, filename)
    with open(out_file, "w", encoding="utf-8") as f:
        for s in sentences:
            f.write(s + "\n")

    count += 1
    print(f"Processed {count}: {filename} ({len(sentences)} sentences)")

print("Sentence splitting completed for all transcripts.")
