import os
import re
from transformers import pipeline

INPUT_FILE = "results/segmented_embedding.txt"
OUT_FILE = "results/segment_summaries.txt"

os.makedirs("results", exist_ok=True)

print("🚀 Loading summarization model...")

summarizer = pipeline(
    "summarization",
    model="facebook/bart-large-cnn",
    device=-1
)

# -------------------------------
# LOAD SEGMENTS
# -------------------------------

def load_segments(path):
    segments = {}
    current_id = None
    buffer = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            match = re.search(r"SEGMENT\s+(\d+)", line)

            if match:
                if current_id is not None:
                    segments[current_id] = " ".join(buffer)
                current_id = int(match.group(1))
                buffer = []

            elif line.startswith("==="):
                continue
            else:
                buffer.append(line)

        if current_id is not None:
            segments[current_id] = " ".join(buffer)

    return segments


# -------------------------------
# FIND LAST COMPLETED
# -------------------------------

last_done = 0

if os.path.exists(OUT_FILE):
    with open(OUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            m = re.match(r"SEGMENT\s+(\d+)", line)
            if m:
                last_done = int(m.group(1))

print("⏩ Resuming from segment:", last_done + 1)


segments = load_segments(INPUT_FILE)
print("📊 Total segments available:", len(segments))

# -------------------------------
# RESUME LOOP
# -------------------------------

with open(OUT_FILE, "a", encoding="utf-8") as out:

    for sid in sorted(segments):

        if sid <= last_done:
            continue

        text = segments[sid]

        print("✍ Summarizing segment", sid)

        if len(text.strip()) < 40:
            summary = text

        else:
            chunks = [text[i:i+900] for i in range(0, len(text), 900)]

            summaries = []
            for ch in chunks:
                result = summarizer(
                    ch,
                    max_length=90,
                    min_length=30,
                    do_sample=False
                )
                summaries.append(result[0]["summary_text"])

            summary = " ".join(summaries)

        out.write(f"SEGMENT {sid}:\n")
        out.write(f"Summary: {summary}\n\n")

print("✅ Resume summarization completed.")
