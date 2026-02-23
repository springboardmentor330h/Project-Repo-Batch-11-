import json
from pathlib import Path

EP = "83"

SENTENCES_FILE = Path(f"outputs/sentences_{EP}.json")
SEGMENTS_FILE  = Path(f"outputs/segments_{EP}.json")
OUT_FILE       = Path(f"outputs/timestamps_{EP}.json")

sentences = json.loads(SENTENCES_FILE.read_text(encoding="utf-8"))
segments  = json.loads(SEGMENTS_FILE.read_text(encoding="utf-8"))

TOTAL_DURATION_SEC = 30 * 60  # adjust if needed
seconds_per_sentence = TOTAL_DURATION_SEC / len(sentences)

sentence_time = {
    i: i * seconds_per_sentence
    for i in range(len(sentences))
}

timestamps = {}

for seg_id, seg_sents in segments.items():
    indices = [i for i, s in enumerate(sentences) if s in seg_sents]

    if not indices:
        continue

    start = min(indices)
    end   = max(indices)

    timestamps[seg_id] = {
        "start_sec": round(sentence_time[start], 2),
        "end_sec": round(sentence_time[end], 2)
    }

OUT_FILE.write_text(json.dumps(timestamps, indent=2), encoding="utf-8")

print(f"Saved timestamps to {OUT_FILE}")