import os
import json
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

SEGMENTED_DIR = "data/segmented"

def load_podcast_data(podcast_id):
    path = os.path.join(SEGMENTED_DIR, f"{podcast_id}_segmented.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

@app.route("/api/podcasts", methods=["GET"])
def get_podcasts():
    """Returns a list of available podcasts with basic metadata."""
    podcasts = []
    # IDs we know exist and are processed
    valid_ids = ["0", "1", "3"]
    
    # In a real app, we'd pull titles from the CSV, but here we use IDs
    titles = {
        "0": "Pod Save America: Episode 0",
        "1": "Pod Save America: Episode 1",
        "3": "Pod Save America: Episode 3"
    }
    
    for pid in valid_ids:
        data = load_podcast_data(pid)
        if data:
            podcasts.append({
                "id": pid,
                "title": titles.get(pid, f"Podcast {pid}"),
                "segment_count": len(data),
                "preview_summary": data[0]["summary"] if data else ""
            })
    return jsonify(podcasts)

@app.route("/api/podcast/<podcast_id>", methods=["GET"])
def get_podcast_details(podcast_id):
    """Returns the full segmented data for a specific podcast."""
    data = load_podcast_data(podcast_id)
    if data:
        return jsonify(data)
    return jsonify({"error": "Podcast not found"}), 404

@app.route("/api/search", methods=["GET"])
def search():
    """Searches for segments containing the query string across all podcasts."""
    query = request.args.get("q", "").lower()
    if not query:
        return jsonify([])
    
    results = []
    valid_ids = ["0", "1", "3"]
    
    for pid in valid_ids:
        data = load_podcast_data(pid)
        if data:
            for seg in data:
                # Search in text, keywords, and summary
                if (query in seg["text"].lower() or 
                    any(query in kw.lower() for kw in seg["keywords"]) or 
                    query in seg["summary"].lower()):
                    
                    results.append({
                        "podcast_id": pid,
                        "segment_id": seg["segment_id"],
                        "summary": seg["summary"],
                        "keywords": seg["keywords"],
                        "text": seg["text"]
                    })
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
