import os
import json
from sklearn.feature_extraction.text import TfidfVectorizer

# ---------------- CONFIG ----------------
INPUT_DIR = "outputs"
OUTPUT_DIR = "outputs"

PODCAST_IDS = [
    "2695", "2716", "54715",
    "61300", "61301", "61302",
    "64196", "79", "83", "103"
]

TOP_K = 6   # keywords per final topic
# ----------------------------------------

os.makedirs(OUTPUT_DIR, exist_ok=True)


def extract_keywords_tfidf(texts, top_k=6):
    """
    Extract meaningful keywords using tuned TF-IDF.
    One keyword list per topic.
    """

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),   # words + phrases
        max_df=0.85,          # remove very common terms
        min_df=2,             # remove rare noise
        sublinear_tf=True
    )

    tfidf_matrix = vectorizer.fit_transform(texts)
    feature_names = vectorizer.get_feature_names_out()

    all_keywords = []

    for row in tfidf_matrix:
        scores = row.toarray()[0]
        top_indices = scores.argsort()[-top_k:][::-1]

        keywords = [
            feature_names[i]
            for i in top_indices
            if scores[i] > 0
        ]

        all_keywords.append(keywords)

    return all_keywords


for pid in PODCAST_IDS:
    input_path = os.path.join(INPUT_DIR, f"final_{pid}_topics.json")

    if not os.path.exists(input_path):
        print(f"❌ Missing final topics file: final_{pid}_topics.json")
        continue

    with open(input_path, "r", encoding="utf-8") as f:
        final_topics = json.load(f)

    print(f"🔹 Extracting TF-IDF keywords for FINAL topics of podcast {pid}")

    topic_texts = [topic["text"] for topic in final_topics]
    keyword_lists = extract_keywords_tfidf(topic_texts, TOP_K)

    output = {
        str(topic["segment_id"]): keywords
        for topic, keywords in zip(final_topics, keyword_lists)
    }

    output_path = os.path.join(OUTPUT_DIR, f"final_keywords_{pid}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved → {output_path}")

print("🎉 TF-IDF keyword extraction for FINAL topics completed.")
