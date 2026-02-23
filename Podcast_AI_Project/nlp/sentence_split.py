import os
from pathlib import Path
import nltk

nltk.download("punkt")

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_DIR = BASE_DIR / "data" / "processed_text" / "genre2_news"
OUT_DIR = BASE_DIR / "data" / "sentences" / "genre2_news"

OUT_DIR.mkdir(parents=True, exist_ok=True)

print("📰 Sentence splitting ONLY for genre2_news...")

count = 0

for file in INPUT_DIR.glob("*.txt"):
    with open(file, "r", encoding="utf-8") as f:
        text = f.read().strip()

    sentences = nltk.sent_tokenize(text)

    out_path = OUT_DIR / file.name

    with open(out_path, "w", encoding="utf-8") as f:
        for s in sentences:
            f.write(s.strip() + "\n")

    print(f"➡ Sentences saved: {file.name}")
    count += 1

print("\n✅ News sentence splitting complete.")
print(f"📊 Files processed: {count}")
