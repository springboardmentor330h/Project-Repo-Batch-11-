import os
import json
from textblob import TextBlob

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


def analyze_sentiment(text):
    """
    Returns sentiment label and polarity score
    """
    polarity = TextBlob(text).sentiment.polarity

    if polarity > 0.1:
        label = "Positive"
    elif polarity < -0.1:
        label = "Negative"
    else:
        label = "Neutral"

    return label, round(polarity, 3)


for pid in PODCAST_IDS:
    input_path = os.path.join(INPUT_DIR, f"final_{pid}_data.json")

    if not os.path.exists(input_path):
        print(f"❌ Missing file: final_{pid}_data.json")
        continue

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"🔹 Running sentiment analysis for podcast {pid}")

    sentiment_output = []

    for segment in data:
        label, score = analyze_sentiment(segment["transcript"])

        sentiment_output.append({
            "segment_id": segment["segment_id"],
            "sentiment": label,
            "score": score
        })

    output_path = os.path.join(OUTPUT_DIR, f"final_sentiment_{pid}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(sentiment_output, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved → {output_path}")

print("🎉 Sentiment analysis completed.")
