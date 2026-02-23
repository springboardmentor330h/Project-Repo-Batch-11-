import os
import json
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# ------------- CONFIG -----------------
INPUT_DIR = "outputs"
OUTPUT_DIR = "outputs/keyword_clouds"

PODCAST_ID = "2695"   # change if needed
SEGMENT_ID = 0        # any segment
# --------------------------------------

os.makedirs(OUTPUT_DIR, exist_ok=True)

input_path = os.path.join(INPUT_DIR, f"final_{PODCAST_ID}_data.json")

with open(input_path, "r", encoding="utf-8") as f:
    data = json.load(f)

segment = next(s for s in data if s["segment_id"] == SEGMENT_ID)
keywords = segment["keywords"]

text = " ".join(keywords)

wc = WordCloud(
    width=800,
    height=400,
    background_color="white"
).generate(text)

plt.figure(figsize=(10, 5))
plt.imshow(wc, interpolation="bilinear")
plt.axis("off")

output_path = os.path.join(
    OUTPUT_DIR,
    f"keyword_cloud_{PODCAST_ID}_segment_{SEGMENT_ID}.png"
)
plt.savefig(output_path, bbox_inches="tight")
plt.close()

print(f"✅ Keyword cloud saved → {output_path}")
