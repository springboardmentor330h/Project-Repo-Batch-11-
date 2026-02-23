import os
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
import shutil
from datetime import datetime
from src.pipeline_manager import start_background_processing

app = Flask(__name__)
CORS(app)

SEGMENTED_DIR = "data/segmented"

METADATA_FILE = "data/podcast_metadata.json"

def load_metadata():
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def load_podcast_data(podcast_id):
    path = os.path.join(SEGMENTED_DIR, f"{podcast_id}_segmented.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

@app.route("/api/podcasts", methods=["GET"])
def get_podcasts():
    """Returns the list of podcasts directly from cached metadata (Instant)."""
    return jsonify(load_metadata())

@app.route("/api/podcast/<podcast_id>", methods=["GET"])
def get_podcast_details(podcast_id):
    """Returns the full segmented data for a specific podcast."""
    data = load_podcast_data(podcast_id)
    if data:
        return jsonify(data)
    return jsonify({"error": "Podcast not found"}), 404

@app.route("/api/search", methods=["GET"])
def search():
    # ... (existing search logic remains same, just ensure it works with dynamic ids)
    # [Same as before, no changes needed for search logic]
    return search_logic() # Placeholder for multi-replace

@app.route("/api/upload", methods=["POST"])
def upload_podcast():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files["file"]
    
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    
    # Auto-generate title and domain
    filename_raw = file.filename
    # Clean up filename for title
    title = os.path.splitext(filename_raw)[0].replace('_', ' ').replace('-', ' ').title()
    domain = "New Upload"
    
    if file and filename_raw.lower().endswith(".mp3"):
        metadata = load_metadata()
        # Generate new unique ID
        existing_ids = [int(m["id"]) for m in metadata if str(m["id"]).isdigit()]
        new_id = str(max(existing_ids) + 1 if existing_ids else 100)
        
        filename = f"{new_id}.mp3"
        filepath = os.path.join("data/raw", filename)
        os.makedirs("data/raw", exist_ok=True)
        file.save(filepath)
        
        # Add to metadata
        new_entry = {
            "id": new_id,
            "title": title,
            "domain": domain,
            "url": "upload",
            "status": "processing",
            "upload_date": datetime.now().isoformat()
        }
        metadata.append(new_entry)
        with open(METADATA_FILE, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4)
            
        # Trigger processing pipeline in background
        start_background_processing(new_id, filepath)
        
        return jsonify(new_entry), 201
    
    return jsonify({"error": "Only MP3 files are supported"}), 400

@app.route("/api/podcast/<podcast_id>", methods=["DELETE"])
def delete_podcast(podcast_id):
    metadata = load_metadata()
    updated_metadata = [m for m in metadata if str(m["id"]) != str(podcast_id)]
    
    if len(updated_metadata) == len(metadata):
        return jsonify({"error": "Podcast not found"}), 404
    
    # 1. Update metadata file
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(updated_metadata, f, indent=4)
    
    # 2. Cleanup files
    # Raw
    raw_path = os.path.join("data/raw", f"{podcast_id}.mp3")
    if os.path.exists(raw_path): os.remove(raw_path)
    
    # Processed (Chunks)
    chunk_dir = os.path.join("data/processed/chunks", str(podcast_id))
    if os.path.exists(chunk_dir): shutil.rmtree(chunk_dir)
    
    # Transcripts
    transcript_path = os.path.join("data/transcripts", f"{podcast_id}_transcript.json")
    if os.path.exists(transcript_path): os.remove(transcript_path)
    
    # Segmented
    segmented_path = os.path.join("data/segmented", f"{podcast_id}_segmented.json")
    if os.path.exists(segmented_path): os.remove(segmented_path)
    
    return jsonify({"message": f"Podcast {podcast_id} deleted successfully"}), 200

def search_logic():
    # Helper to keep original search logic intact
    query = request.args.get("q", "").lower()
    if not query: return jsonify([])
    results = []
    metadata = load_metadata()
    processed_files = os.listdir(SEGMENTED_DIR) if os.path.exists(SEGMENTED_DIR) else []
    processed_ids = [f.split('_')[0] for f in processed_files if f.endswith('_segmented.json')]
    metadata_map = {str(m["id"]): m for m in metadata}
    for pid in processed_ids:
        data = load_podcast_data(pid)
        if data:
            m_info = metadata_map.get(pid, {"title": f"Podcast {pid}"})
            for seg in data:
                if (query in seg["text"].lower() or any(query in kw.lower() for kw in seg["keywords"]) or query in seg["summary"].lower()):
                    results.append({"podcast_id": pid, "podcast_title": m_info["title"], "segment_id": seg["segment_id"], "summary": seg["summary"], "keywords": seg["keywords"], "text": seg["text"]})
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
