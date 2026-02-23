import os
import json
import re
from transformers import pipeline

# ---------------- CONFIG ----------------
INPUT_DIR = "outputs"
OUTPUT_DIR = "outputs"

PODCAST_IDS = [
    "2695", "2716", "54715",
    "61300", "61301", "61302",
    "64196", "79", "83", "103"
]

MODEL_NAME = "facebook/bart-large-cnn"

MAX_INPUT_CHARS = 2800     # safe truncation
MIN_LEN = 25              # short & meaningful
MAX_LEN = 60              # UI/PPT friendly
# ----------------------------------------

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("🔹 Loading summarization model...")
summarizer = pipeline(
    "summarization",
    model=MODEL_NAME,
    device=-1  # CPU
)


def clean_summary(text: str) -> str:
    """Light cleanup to remove generic starters and extra spaces."""
    patterns = [
        r"^this talk (discusses|explains|describes)\s*",
        r"^the speaker (discusses|explains|describes)\s*",
        r"^in this (talk|segment),?\s*",
    ]
    for p in patterns:
        text = re.sub(p, "", text, flags=re.IGNORECASE)
    return text.strip().rstrip(".")


def summarize_text(text: str) -> str:
    text = text.replace("\n", " ").strip()
    if len(text) > MAX_INPUT_CHARS:
        text = text[:MAX_INPUT_CHARS]

    out = summarizer(
        text,
        min_length=MIN_LEN,
        max_length=MAX_LEN,
        do_sample=False
    )[0]["summary_text"]

    return clean_summary(out)


for pid in PODCAST_IDS:
    in_path = os.path.join(INPUT_DIR, f"final_{pid}_topics.json")
    if not os.path.exists(in_path):
        print(f"❌ Missing: final_{pid}_topics.json")
        continue

    with open(in_path, "r", encoding="utf-8") as f:
        topics = json.load(f)

    print(f"🔹 Generating summaries for podcast {pid}")

    summaries = []
    for t in topics:
        summaries.append({
            "segment_id": t["segment_id"],
            "start": t["start"],
            "end": t["end"],
            "summary": summarize_text(t["text"])
        })

    out_path = os.path.join(OUTPUT_DIR, f"final_summaries_{pid}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summaries, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved → {out_path}")

print("🎉 Clean, meaningful summaries generated.")
