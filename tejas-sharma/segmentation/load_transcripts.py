import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# FINAL, CONFIRMED path for Week 3
TRANSCRIPTS_DIR = os.path.join(BASE_DIR, "..", "data", "transcripts_txt")

print("Looking for transcripts in:")
print(TRANSCRIPTS_DIR)

transcripts = {}

if not os.path.exists(TRANSCRIPTS_DIR):
    raise FileNotFoundError(f"Transcript folder not found: {TRANSCRIPTS_DIR}")

for filename in os.listdir(TRANSCRIPTS_DIR):
    if filename.endswith(".txt"):
        file_path = os.path.join(TRANSCRIPTS_DIR, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            transcripts[filename] = f.read()

print("Total transcripts loaded:", len(transcripts))
import nltk
nltk.download('punkt')
from nltk.tokenize import sent_tokenize

transcript_sentences = {}

for name, text in transcripts.items():
    sentences = sent_tokenize(text)
    transcript_sentences[name] = sentences

# Debug check
sample_file = list(transcript_sentences.keys())[0]
print(f"\nSample file: {sample_file}")
print("Number of sentences:", len(transcript_sentences[sample_file]))
print("First 3 sentences:")
for s in transcript_sentences[sample_file][:3]:
    print("-", s)
