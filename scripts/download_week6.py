import os
import requests
import subprocess
from pydub import AudioSegment

import json

# Load metadata
METADATA_FILE = "data/podcast_metadata.json"
with open(METADATA_FILE, "r", encoding="utf-8") as f:
    METADATA = json.load(f)

# Only process non-local ones
NEW_PODCASTS = [p for p in METADATA if p["url"] != "local"]

RAW_DIR = "data/raw"
MAX_MINUTES = 45

def download_and_trim(pid, url):
    print(f"--- Processing Podcast {pid} ---")
    output_path = os.path.join(RAW_DIR, f"{pid}.mp3")
    
    # Download
    try:
        print(f"Downloading from {url}...")
        response = requests.get(url, stream=True, timeout=60)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Downloaded to {output_path}")
        else:
            print(f"Failed to download. Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error downloading: {e}")
        return False

    # Trim to 45 mins
    try:
        print(f"Trimming to {MAX_MINUTES} minutes...")
        audio = AudioSegment.from_file(output_path)
        max_ms = MAX_MINUTES * 60 * 1000
        if len(audio) > max_ms:
            trimmed = audio[:max_ms]
            trimmed.export(output_path, format="mp3")
            print(f"Trimmed successfully.")
        else:
            print(f"Audio is shorter than {MAX_MINUTES} mins. No trim needed.")
    except Exception as e:
        print(f"Error trimming: {e}")
        # Not a deal breaker if trim fails, but usually means pydub/ffmpeg issues
        
    return True

if __name__ == "__main__":
    os.makedirs(RAW_DIR, exist_ok=True)
    for p in NEW_PODCASTS:
        download_and_trim(p["id"], p["url"])
