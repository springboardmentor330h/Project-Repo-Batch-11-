import json
from pathlib import Path

inp = Path("outputs/summaries.json")
out = Path("outputs/summaries_clean.json")

data = json.loads(inp.read_text(encoding="utf-8"))
clean = [{"segment_id": int(k), "summary": v} for k, v in data.items()]
clean = sorted(clean, key=lambda x: x["segment_id"])

out.write_text(json.dumps(clean, indent=2), encoding="utf-8")
print("Saved to", out)