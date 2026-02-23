import re
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd

INPUT = "results/segmented_embedding.txt"
OUTPUT = "results/segment_keywords.csv"

# Read segments
with open(INPUT, "r", encoding="utf-8") as f:
    content = f.read()

# Split by segment markers
segments = re.split(r"--- SEGMENT \d+ ---", content)
segments = [s.strip() for s in segments if s.strip()]

print("Total segments for keyword extraction:", len(segments))

# TF-IDF Vectorizer
vectorizer = TfidfVectorizer(stop_words="english", max_features=20)

tfidf_matrix = vectorizer.fit_transform(segments)
terms = vectorizer.get_feature_names_out()

keywords = []

for i, segment in enumerate(segments):
    row = tfidf_matrix[i].toarray().flatten()
    top_indices = row.argsort()[-5:][::-1]
    top_terms = [terms[j] for j in top_indices]
    keywords.append([i + 1, ", ".join(top_terms)])

df = pd.DataFrame(keywords, columns=["Segment", "Keywords"])
df.to_csv(OUTPUT, index=False)

print("Keyword extraction completed.")
print("Saved at:", OUTPUT)
