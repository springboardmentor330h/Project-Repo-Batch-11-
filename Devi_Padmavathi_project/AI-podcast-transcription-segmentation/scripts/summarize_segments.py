from transformers import pipeline
import json

from pathlib import Path

summarizer = pipeline(
    "summarization",
    model="facebook/bart-large-cnn",
    device=-1
)

def chunk(text, max_words=450):
    words = text.split()
    if len(words) <= max_words:
        return [text]
    return [" ".join(words[i:i+max_words]) for i in range(0, len(words), max_words)]
 
def summarize_text(text):
    wc = len(text.split())
    max_len = min(140, max(40, wc // 2))
    min_len = max(20, wc // 6)
    return summarizer(
        text,
        max_length=max_len,
        min_length=min_len,
        do_sample=False
    )[0]["summary_text"]

EP = "103"

input_file = Path(f"outputs/segments_{EP}.json")
segments = json.loads(input_file.read_text(encoding="utf-8"))

summaries = {}

for segment_id, sentences in segments.items():
    text = " ".join(sentences)
    chunks = chunk(text)
    summaries[segment_id] = " ".join(summarize_text(ch) for ch in chunks)

out_file = Path(f"outputs/summaries_{EP}.json")
out_file.write_text(json.dumps(summaries, indent=2), encoding="utf-8")

print(f"{EP}: {len(summaries)} summaries created")