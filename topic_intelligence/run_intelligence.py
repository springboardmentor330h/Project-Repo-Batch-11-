import os
import json
from keywords import extract_keywords
from summary_and_hooks import (
    generate_title,
    generate_hook,
    generate_questions
)

INPUT_DIR = "topic_segmentation/output"
OUTPUT_DIR = "topic_intelligence/output"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def enrich_topics(filename):
    with open(os.path.join(INPUT_DIR, filename), "r", encoding="utf-8") as f:
        topics = json.load(f)

    enriched = []

    for topic in topics:
        text = topic["text"]

        enriched.append({
            "topic_id": topic["topic_id"],
            "start": topic["start"],
            "end": topic["end"],
            "title": generate_title(text),
            "keywords": extract_keywords(text),
            "hook": generate_hook(text),
            "questions": generate_questions(text),
            "text": text
        })

    out_path = os.path.join(OUTPUT_DIR, filename)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(enriched, f, indent=2)

    print(f"✨ Topic intelligence added: {out_path}")

if __name__ == "__main__":
    for file in os.listdir(INPUT_DIR):
        if file.endswith(".json"):
            enrich_topics(file)
