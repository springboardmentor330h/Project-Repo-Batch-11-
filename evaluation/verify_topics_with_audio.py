import json

INPUT_FILE = "pipeline_output.json"
TOPIC_FILE = None

from topic_segmentation.algorithms.segment_hybrid_engine import segment

data = json.load(open(INPUT_FILE, encoding="utf-8"))
topics = segment(data["segments"])

print("\n[TOPIC VERIFICATION OUTPUT]\n")

for t in topics:
    segs = t["segments"]

    start = segs[0]["start"]
    end = segs[-1]["end"]

    text = " ".join(s["text"] for s in segs)

    print("=" * 80)
    print(f"TOPIC {t['topic_id']}  |  {start:.2f}s → {end:.2f}s")
    print("-" * 80)
    print(text)
    print()
