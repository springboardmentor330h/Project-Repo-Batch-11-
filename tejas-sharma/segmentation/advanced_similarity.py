import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SENTENCE_DIR = os.path.join(BASE_DIR, "..", "results", "sentences")
OUTPUT_DIR = os.path.join(BASE_DIR, "..", "results", "advanced_segments")

os.makedirs(OUTPUT_DIR, exist_ok=True)

WINDOW_SIZE = 3        # context window
THRESHOLD = 0.25       # higher than baseline

def build_context(sentences, index, window=3):
    start = max(0, index - window)
    end = min(len(sentences), index + window + 1)
    return " ".join(sentences[start:end])

processed = 0

for filename in os.listdir(SENTENCE_DIR):
    if not filename.endswith(".txt"):
        continue

    with open(os.path.join(SENTENCE_DIR, filename), "r", encoding="utf-8") as f:
        sentences = [line.strip() for line in f if line.strip()]

    if len(sentences) < 5:
        continue

    contexts = [build_context(sentences, i, WINDOW_SIZE) for i in range(len(sentences))]

    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1,2))
    tfidf = vectorizer.fit_transform(contexts)

    boundaries = [0]

    for i in range(len(contexts) - 1):
        sim = cosine_similarity(tfidf[i], tfidf[i + 1])[0][0]
        if sim < THRESHOLD:
            boundaries.append(i + 1)

    boundaries.append(len(sentences))

    segments = []
    for i in range(len(boundaries) - 1):
        seg = " ".join(sentences[boundaries[i]:boundaries[i + 1]])
        segments.append(seg)

    out_file = os.path.join(OUTPUT_DIR, filename)
    with open(out_file, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments):
            f.write(f"\n--- Segment {i + 1} ---\n{seg}\n")

    processed += 1
    print(f"Processed {processed}: {filename}")

print("Advanced contextual topic segmentation completed.")
