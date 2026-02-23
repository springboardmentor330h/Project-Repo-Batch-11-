import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------- CONFIG ----------------
SENTENCE_DIR = "outputs"
OUTPUT_DIR = "outputs"

PODCAST_IDS = [
    "2695", "2716", "54715",
    "61300", "61301", "61302",
    "64196", "79", "83", "103"
]

DRIFT_THRESHOLD = 0.35      # semantic drift sensitivity
MIN_SENTENCES = 6           # minimum sentences before split
MERGE_THRESHOLD = 5         # merge tiny segments
# ----------------------------------------

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("🔹 Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")


def segment_sentences(sentences):
    texts = [s["text"] for s in sentences]
    embeddings = model.encode(texts)

    segments = []
    current_segment = [sentences[0]]
    current_embeddings = [embeddings[0]]

    for i in range(1, len(sentences)):
        # semantic center of current segment
        segment_center = np.mean(current_embeddings, axis=0, keepdims=True)

        similarity = cosine_similarity(
            segment_center,
            embeddings[i].reshape(1, -1)
        )[0][0]

        # split when cumulative meaning drifts
        if similarity < DRIFT_THRESHOLD and len(current_segment) >= MIN_SENTENCES:
            segments.append(current_segment)
            current_segment = []
            current_embeddings = []

        current_segment.append(sentences[i])
        current_embeddings.append(embeddings[i])

    segments.append(current_segment)

    # merge very small segments
    merged_segments = []
    for seg in segments:
        if merged_segments and len(seg) < MERGE_THRESHOLD:
            merged_segments[-1].extend(seg)
        else:
            merged_segments.append(seg)

    return merged_segments


for pid in PODCAST_IDS:
    input_path = os.path.join(SENTENCE_DIR, f"sentences_{pid}.json")

    if not os.path.exists(input_path):
        print(f"❌ Missing file: sentences_{pid}.json")
        continue

    with open(input_path, "r", encoding="utf-8") as f:
        sentences = json.load(f)

    print(f"🔹 Segmenting podcast {pid} ({len(sentences)} sentences)")

    segments = segment_sentences(sentences)

    output = []
    for idx, seg in enumerate(segments):
        output.append({
            "segment_id": idx,
            "start": seg[0]["start"],
            "end": seg[-1]["end"],
            "text": " ".join(s["text"] for s in seg)
        })

    output_path = os.path.join(OUTPUT_DIR, f"segments_{pid}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved → {output_path} | Segments: {len(output)}")

print("🎉 Semantic topic segmentation completed successfully.")
