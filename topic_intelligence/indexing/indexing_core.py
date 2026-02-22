import json
import sys
from pathlib import Path
from collections import defaultdict


def build_index(input_path: str) -> dict:
    input_path = Path(input_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "topics" not in data:
        raise ValueError("Input JSON must contain 'topics'")

    # Build search index
    search_index = defaultdict(list)
    
    for topic in data["topics"]:
        # Index by keywords
        for keyword in topic.get("keywords", []):
            search_index[keyword.lower()].append(topic["topic_id"])
        
        # Index by summary content
        summary_words = topic.get("summary", "").lower().split()
        for word in summary_words:
            if len(word) > 3:  # Filter short words
                search_index[word].append(topic["topic_id"])
        
        # Index by full text
        text_words = topic.get("text", "").lower().split()
        for word in text_words:
            if len(word) > 3:
                search_index[word].append(topic["topic_id"])

    indexed = {
        "audio_file": data.get("audio_file"),
        "topics": data["topics"],
        "search_index": dict(search_index),
        "metadata": {
            "total_topics": len(data["topics"]),
            "indexed_at": __import__("datetime").datetime.now().isoformat()
        }
    }

    return indexed


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python indexing_core.py <segmented_output.json>")
        sys.exit(1)

    input_file = sys.argv[1]
    result = build_index(input_file)

    output_path = "indexed_output.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Indexed output saved to {output_path}")
