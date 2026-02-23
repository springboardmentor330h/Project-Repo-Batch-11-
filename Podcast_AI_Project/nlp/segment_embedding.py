import os
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

INPUT = "data/sentences.txt"
OUTPUT = "results/segmented_embedding.txt"

os.makedirs("results", exist_ok=True)

print("Loading sentences...")

with open(INPUT, "r", encoding="utf-8") as f:
    sentences = [line.strip() for line in f.readlines() if line.strip()]

print("Loading embedding model...")

model = SentenceTransformer('all-MiniLM-L6-v2')

print("Generating embeddings...")

embeddings = model.encode(sentences)

print("Computing similarities...")

similarities = []

for i in range(len(embeddings) - 1):
    sim = cosine_similarity(
        [embeddings[i]],
        [embeddings[i + 1]]
    )[0][0]
    similarities.append(sim)

threshold = np.mean(similarities) - np.std(similarities)

print("Segmenting transcript...")

segments = []
current = [sentences[0]]

for i in range(1, len(sentences)):
    if similarities[i - 1] < threshold:
        segments.append(" ".join(current))
        current = [sentences[i]]
    else:
        current.append(sentences[i])

segments.append(" ".join(current))

with open(OUTPUT, "w", encoding="utf-8") as f:
    for idx, seg in enumerate(segments):
        f.write(f"\n--- SEGMENT {idx+1} ---\n")
        f.write(seg + "\n")

print("Embedding-based segmentation completed.")
print("Total segments:", len(segments))
print("Saved at:", OUTPUT)
