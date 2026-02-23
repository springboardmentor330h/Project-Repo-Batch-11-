import json
import re
from pathlib import Path

# Input and Output paths
input_file = Path("../transcripts/103.txt")
output_file = Path("outputs/sentences_103.json")

# Read transcript
text = input_file.read_text(encoding="utf-8")

# Simple sentence splitting using regex
sentences = re.split(r'(?<=[.!?])\s+', text.strip())

# Remove empty lines
sentences = [s for s in sentences if s.strip()]

# Save to JSON
output_file.parent.mkdir(parents=True, exist_ok=True)
output_file.write_text(json.dumps(sentences, indent=2), encoding="utf-8")

print(f"Done! Saved {len(sentences)} sentences to {output_file}")

