import json
from pathlib import Path
from sentence_transformers import SentenceTransformer, util

# Load sentences
input_file = Path("../outputs/sentences_103.json")
sentences = json.loads(input_file.read_text(encoding="utf-8"))

# Load embedding model
model = SentenceTransformer("all-MiniL" \
"M-L6-v2")

embeddings = model.encode(sentences, convert_to_tensor=True)

segments = []
current_segment = [sentences[0]]

for i in range(1, len(sentences)):
    sim = float(util.cos_sim(embeddings[i], embeddings[i-1]))
    
    # Boundary condition (lower similarity → new topic)
    if sim < 0.40:
        segments.append(current_segment)
        current_segment = []
    
    current_segment.append(sentences[i])

# Add last segment
segments.append(current_segment)

# Save output
output_file = Path("../outputs/segments_baseline.json")
output_file.write_text(json.dumps(segments, indent=2), encoding="utf-8")

print(f"Done! Generated {len(segments)} baseline topic segments -> {output_file}")


