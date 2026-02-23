import os
import json
import nltk
from nltk.tokenize import sent_tokenize

# ---------------- CONFIG ----------------
TRANSCRIPTS_DIR = "transcripts"
OUTPUT_DIR = "outputs"

PODCAST_IDS = [
    "2695", "2716", "54715",
    "61300", "61301", "61302",
    "64196", "79", "83", "103"
]
# ----------------------------------------

os.makedirs(OUTPUT_DIR, exist_ok=True)

def split_into_sentences(segments):
    sentences = []
    buffer_text = ""
    start_time = None
    sentence_id = 0

    for seg in segments:
        text = seg["text"].strip()

        if not text:
            continue

        if start_time is None:
            start_time = seg["start"]

        buffer_text += " " + text
        end_time = seg["end"]

        split_sents = sent_tokenize(buffer_text)

        # keep last incomplete sentence in buffer
        for sent in split_sents[:-1]:
            sentences.append({
                "sentence_id": sentence_id,
                "text": sent.strip(),
                "start": round(start_time, 2),
                "end": round(end_time, 2)
            })
            sentence_id += 1
            start_time = end_time

        buffer_text = split_sents[-1]

    # flush remaining buffer
    if buffer_text.strip():
        sentences.append({
            "sentence_id": sentence_id,
            "text": buffer_text.strip(),
            "start": round(start_time, 2),
            "end": round(end_time, 2)
        })

    return sentences


for pid in PODCAST_IDS:
    input_path = os.path.join(TRANSCRIPTS_DIR, f"{pid}.json")

    if not os.path.exists(input_path):
        print(f"❌ Missing transcript: {pid}.json")
        continue

    with open(input_path, "r", encoding="utf-8") as f:
        transcript_segments = json.load(f)

    print(f"🔹 Processing sentences for podcast {pid}")

    sentences = split_into_sentences(transcript_segments)

    output_path = os.path.join(OUTPUT_DIR, f"sentences_{pid}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(sentences, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved → {output_path}")

print("🎉 Sentence splitting completed for all podcasts.")
