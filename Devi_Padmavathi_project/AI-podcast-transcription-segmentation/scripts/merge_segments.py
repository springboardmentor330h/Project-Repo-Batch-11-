import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------- CONFIG ----------------
SEGMENT_DIR = "outputs"
OUTPUT_DIR = "outputs"

PODCAST_IDS = [
    "2695", "2716", "54715",
    "61300", "61301", "61302",
    "64196", "79", "83", "103"
]

MERGE_SIMILARITY_THRESHOLD = 0.60   # higher = stronger merge
MIN_SEGMENT_WORDS = 120             # avoid tiny segments
# ----------------------------------------

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("🔹 Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")


def get_embedding(text):
    return model.encode([text])[0]


def merge_segments(segments):
    merged = []
    i = 0

    embeddings = [get_embedding(seg["text"]) for seg in segments]

    while i < len(segments):
        current = segments[i]
        current_emb = embeddings[i]

        j = i + 1
        while j < len(segments):
            next_emb = embeddings[j]

            sim = cosine_similarity(
                current_emb.reshape(1, -1),
                next_emb.reshape(1, -1)
            )[0][0]

            word_count = len(current["text"].split())

            # merge if semantically similar OR too small
            if sim > MERGE_SIMILARITY_THRESHOLD or word_count < MIN_SEGMENT_WORDS:
                current = {
                    "segment_id": current["segment_id"],
                    "start": current["start"],
                    "end": segments[j]["end"],
                    "text": current["text"] + " " + segments[j]["text"]
                }
                current_emb = get_embedding(current["text"])
                j += 1
            else:
                break

        merged.append(current)
        i = j

    return merged


for pid in PODCAST_IDS:
    input_path = os.path.join(SEGMENT_DIR, f"segments_{pid}.json")

    if not os.path.exists(input_path):
        print(f"❌ Missing segments file for {pid}")
        continue

    with open(input_path, "r", encoding="utf-8") as f:
        segments = json.load(f)

    print(f"🔹 Merging segments for podcast {pid} (initial: {len(segments)})")

    final_segments = merge_segments(segments)

    # reassign clean segment IDs
    for idx, seg in enumerate(final_segments):
        seg["segment_id"] = idx

    output_path = os.path.join(OUTPUT_DIR, f"final_{pid}_topics.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_segments, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved → {output_path} | Final segments: {len(final_segments)}")

print("🎉 High-quality topic clustering completed.")


