import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

INPUT = "data/sentences.txt"
OUTPUT = "results/segmented_baseline.txt"

sentences = open(INPUT, encoding="utf-8").read().splitlines()

vectorizer = TfidfVectorizer(stop_words="english")
X = vectorizer.fit_transform(sentences)

similarities = []
for i in range(len(sentences) - 1):
    sim = cosine_similarity(X[i], X[i + 1])[0][0]
    similarities.append(sim)

threshold = np.mean(similarities) * 0.7

segments = []
current = []

for i, sent in enumerate(sentences[:-1]):
    current.append(sent)

    if similarities[i] < threshold:
        segments.append(current)
        current = []

current.append(sentences[-1])
segments.append(current)

with open(OUTPUT, "w", encoding="utf-8") as f:
    for idx, seg in enumerate(segments):
        f.write(f"\n===== TOPIC SEGMENT {idx+1} =====\n")
        for s in seg:
            f.write(s + "\n")

print("Baseline segmentation completed.")
print("Total segments:", len(segments))
print("Output saved at:", OUTPUT)
