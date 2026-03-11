import os
import json
import re
import nltk
import numpy as np
nltk.download("averaged_perceptron_tagger_eng")
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk import word_tokenize, pos_tag


# ---------------- SETUP ----------------
nltk.download("punkt")
nltk.download("averaged_perceptron_tagger")
nltk.download("vader_lexicon")

sia = SentimentIntensityAnalyzer()
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

TRANSCRIPTS_DIR = "data/transcripts"
SEGMENTS_DIR = "data/segments"
METADATA_PATH = "data/segment_metadata.json"

os.makedirs(SEGMENTS_DIR, exist_ok=True)

# PARAMETERS
MAX_EPISODES = 10
MIN_WORDS = 120
SIMILARITY_OFFSET = 0.08

# HELPERS 
def clean_line(line):
    return re.sub(r"\[.*?\]", "", line).strip()

def extract_time(line):
    match = re.search(r"\[(\d+\.?\d*)\s*-\s*(\d+\.?\d*)\]", line)
    return (float(match.group(1)), float(match.group(2))) if match else (None, None)

def remove_speaker_prefix(text):
    return re.sub(r"^[A-Z ]{2,30}:\s*", "", text)

def extractive_summary(sentences):
    if len(sentences) == 1:
        return sentences[0]
    vec = TfidfVectorizer(stop_words="english")
    X = vec.fit_transform(sentences)
    scores = X.sum(axis=1).A1
    return sentences[int(scores.argmax())]

def generate_semantic_topic(summary):
    words = word_tokenize(summary)
    tagged = pos_tag(words)

    nouns = [
        w.lower() for w, t in tagged
        if t.startswith("NN") and len(w) > 2
    ]

    blacklist = {
        "ira", "glass", "joe", "kevin", "said", "says",
        "one", "time", "thing", "people"
    }
    nouns = [n for n in nouns if n not in blacklist]

    if not nouns:
        return "General Discussion"

    return " ".join(nouns[:3]).title()

# MAIN 
metadata = []
global_segment_id = 0

episode_files = sorted(
    [f for f in os.listdir(TRANSCRIPTS_DIR)
     if f.startswith("episode_") and f.endswith(".txt")],
    key=lambda x: int(x.replace("episode_", "").replace(".txt", ""))
)[:MAX_EPISODES]

print("Processing episodes:", episode_files)

for episode_file in episode_files:
    episode_id = episode_file.replace("episode_", "").replace(".txt", "")
    print(f"\n▶ Episode {episode_id}")

    with open(os.path.join(TRANSCRIPTS_DIR, episode_file), encoding="utf-8") as f:
        lines = f.readlines()

    texts, start_times = [], []

    for line in lines:
        start, _ = extract_time(line)
        text = clean_line(line)
        if text and start is not None:
            texts.append(text)
            start_times.append(start)

    if len(texts) < 10:
        continue

    episode_start = start_times[0]
    episode_end = start_times[-1]

    full_text = " ".join(texts)
    sentences = nltk.sent_tokenize(full_text)

    embeddings = embed_model.encode(sentences)
    similarities = [
        cosine_similarity([embeddings[i]], [embeddings[i + 1]])[0][0]
        for i in range(len(sentences) - 1)
    ]

    threshold = np.mean(similarities) - SIMILARITY_OFFSET
    boundaries = [i + 1 for i, s in enumerate(similarities) if s < threshold]

    start_idx = 0
    local_segment_id = 0
    total_sentences = len(sentences)

    for boundary in boundaries + [total_sentences]:
        seg_sentences = sentences[start_idx:boundary]
        segment_text = " ".join(seg_sentences)

        if len(segment_text.split()) < MIN_WORDS:
            continue

        # TIMESTAMPS 
        seg_start = episode_start + (
            (start_idx / total_sentences) * (episode_end - episode_start)
        )
        seg_end = episode_start + (
            (boundary / total_sentences) * (episode_end - episode_start)
        )

        raw_summary = extractive_summary(seg_sentences)
        summary = remove_speaker_prefix(raw_summary)
        title = generate_semantic_topic(summary)

        tfidf = TfidfVectorizer(stop_words="english", max_features=5)
        tfidf.fit([segment_text])
        keywords = tfidf.get_feature_names_out().tolist()

        score = sia.polarity_scores(segment_text)["compound"]
        sentiment_label = (
            "Positive" if score >= 0.05 else
            "Negative" if score <= -0.05 else
            "Neutral"
        )

        seg_filename = f"episode_{episode_id}_segment_{local_segment_id}.txt"
        with open(os.path.join(SEGMENTS_DIR, seg_filename), "w", encoding="utf-8") as f:
            f.write(segment_text)

        metadata.append({
            "episode_id": episode_id,
            "episode_title": f"Episode {episode_id}",
            "segment_id": global_segment_id,
            "local_segment_id": local_segment_id,
            "title": title,
            "summary": summary,
            "keywords": keywords,
            "sentiment": {
                "label": sentiment_label,
                "score": round(score, 2)
            },
            "time": {
                "start": round(seg_start, 2),
                "end": round(seg_end, 2)
            }
        })

        global_segment_id += 1
        local_segment_id += 1
        start_idx = boundary

# SAVE 
with open(METADATA_PATH, "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2)

print("\n Tasks completed successfully")
print(f"• Episodes processed: {len(episode_files)}")
print(f"• Segments created: {len(metadata)}")

