import os
import json
from pathlib import Path
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# -------------------------------
# CONFIG
# -------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

NEWS_SENTENCES_DIR = BASE_DIR / "data" / "sentences" / "genre2_news"

OUTPUT_FILE = BASE_DIR / "results" / "segment_outputs" / "news_segments.json"

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

MODEL_NAME = "all-MiniLM-L6-v2"

SIM_THRESHOLD = 0.70   # topic change sensitivity
MIN_SEGMENT_LEN = 4


# -------------------------------
# LOAD MODEL
# -------------------------------

print("🧠 Loading embedding model...")
model = SentenceTransformer(MODEL_NAME)


# -------------------------------
# SEGMENT ONE FILE
# -------------------------------

def segment_sentences(sentences):
    embeddings = model.encode(sentences)

    segments = []
    current = [sentences[0]]

    for i in range(len(sentences) - 1):

        sim = cosine_similarity(
            embeddings[i].reshape(1, -1),
            embeddings[i + 1].reshape(1, -1)
        )[0][0]

        if sim < SIM_THRESHOLD and len(current) >= MIN_SEGMENT_LEN:
            segments.append(" ".join(current))
            current = []

        current.append(sentences[i + 1])

    if current:
        segments.append(" ".join(current))

    return segments



# -------------------------------
# RUN ONLY FOR NEWS
# -------------------------------

print("📰 Running topic segmentation ONLY for genre2_news...")

all_segments = []
seg_id = 100000   # high range so no clash with education

for file in os.listdir(NEWS_SENTENCES_DIR):

    if not file.endswith(".txt"):
        continue

    path = NEWS_SENTENCES_DIR / file

    print("➡ Processing:", file)

    with open(path, "r", encoding="utf-8") as f:
        sentences = [l.strip() for l in f.readlines() if l.strip()]

    if len(sentences) < 10:
        continue

    blocks = segment_sentences(sentences)

    for block in blocks:
        all_segments.append({
            "id": seg_id,
            "genre": "genre2_news",
            "source_file": file,
            "title": block[:80],
            "text": block,
            "summary": "",
            "keywords": "",
            "sentiment": "neutral",
            "sentiment_score": 0.0
        })

        seg_id += 1


# -------------------------------
# SAVE
# -------------------------------

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(all_segments, f, indent=2, ensure_ascii=False)

print("\n✅ News topic segmentation complete.")
print("📄 Saved to:", OUTPUT_FILE)
print("📊 Total news segments:", len(all_segments))
