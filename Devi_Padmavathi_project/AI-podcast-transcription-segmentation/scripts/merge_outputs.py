import os
import json

# ---------------- CONFIG ----------------
INPUT_DIR = "outputs"
OUTPUT_DIR = "outputs"

PODCAST_IDS = [
    "2695", "2716", "54715",
    "61300", "61301", "61302",
    "64196", "79", "83", "103"
]
# ----------------------------------------

os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


for pid in PODCAST_IDS:
    print(f"🔹 Merging final outputs for podcast {pid}")

    topics_path = os.path.join(INPUT_DIR, f"final_{pid}_topics.json")
    keywords_path = os.path.join(INPUT_DIR, f"final_keywords_{pid}.json")
    summaries_path = os.path.join(INPUT_DIR, f"final_summaries_{pid}.json")
    sentiment_path = os.path.join(INPUT_DIR, f"final_sentiment_{pid}.json")

    if not all(map(os.path.exists, [
        topics_path,
        keywords_path,
        summaries_path,
        sentiment_path
    ])):
        print(f"❌ Missing files for podcast {pid}")
        continue

    topics = load_json(topics_path)
    keywords = load_json(keywords_path)
    summaries = load_json(summaries_path)
    sentiments = load_json(sentiment_path)

    # Build lookup maps
    summary_map = {
        str(item["segment_id"]): item["summary"]
        for item in summaries
    }

    sentiment_map = {
        item["segment_id"]: item
        for item in sentiments
    }

    final_data = []

    for topic in topics:
        sid_str = str(topic["segment_id"])
        sid_int = topic["segment_id"]

        sentiment_info = sentiment_map.get(sid_int, {})

        final_data.append({
            "segment_id": sid_int,
            "start": topic["start"],
            "end": topic["end"],
            "summary": summary_map.get(sid_str, ""),
            "keywords": keywords.get(sid_str, []),
            "sentiment": sentiment_info.get("sentiment", "Neutral"),
            "sentiment_score": sentiment_info.get("score", 0.0),
            "transcript": topic["text"]
        })

    output_path = os.path.join(OUTPUT_DIR, f"final_{pid}_data.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Final merged file saved → {output_path}")

print("🎉 All final podcast data merged successfully.")
