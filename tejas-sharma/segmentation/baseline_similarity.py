import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SENTENCE_DIR = os.path.join(BASE_DIR, "..", "results", "sentences")
OUTPUT_DIR = os.path.join(BASE_DIR, "..", "results", "baseline_segments")

os.makedirs(OUTPUT_DIR, exist_ok=True)

THRESHOLD = 0.2

processed = 0

for filename in os.listdir(SENTENCE_DIR):
    if not filename.endswith(".txt"):
        continue

    with open(os.path.join(SENTENCE_DIR, filename), "r", encoding="utf-8") as f:
        sentences = [line.strip() for line in f if line.strip()]

    if len(sentences) < 2:
        continue

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf = vectorizer.fit_transform(sentences)

    boundaries = [0]

    for i in range(len(sentences) - 1):
        sim = cosine_similarity(tfidf[i], tfidf[i + 1])[0][0]
        if sim < THRESHOLD:
            boundaries.append(i + 1)

    boundaries.append(len(sentences))

    segments = []
    for i in range(len(boundaries) - 1):
        segment = " ".join(sentences[boundaries[i]:boundaries[i + 1]])
        segments.append(segment)

    out_file = os.path.join(OUTPUT_DIR, filename)
    with open(out_file, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments):
            f.write(f"\n--- Segment {i + 1} ---\n{seg}\n")

    processed += 1
    print(f"Processed {processed}: {filename}")

print("Baseline topic segmentation completed for all files.")
