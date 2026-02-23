import pandas as pd
import requests
import os
import librosa
import soundfile as sf
from tqdm import tqdm
import time

def download_podcasts(csv_path, output_dir, limit=3):
    print(f"Reading dataset from {csv_path}...")
    df = pd.read_csv(csv_path)
    
    os.makedirs(output_dir, exist_ok=True)
    
    downloaded_files = []
    count = 0
    
    for index, row in df.iterrows():
        if count >= limit:
            break
            
        audio_url = row['pod_link']
        audio_id = row[0]
        
        file_path = os.path.join(output_dir, f"raw_{audio_id}.mp3")
        
        if os.path.exists(file_path):
            print(f"File already exists: {file_path}")
            downloaded_files.append(file_path)
            count += 1
            continue

        try:
            print(f"Downloading full episode {audio_id} from {audio_url}...")
            with requests.get(audio_url, stream=True, timeout=30) as r:
                r.raise_for_status()
                with open(file_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            downloaded_files.append(file_path)
            count += 1
        except Exception as e:
            print(f"Failed to download {audio_url}: {e}")
            
    print(f"Successfully downloaded {len(downloaded_files)} full episodes to {output_dir}")
    return downloaded_files

if __name__ == "__main__":
    CSV_PATH = "data/raw/audio/politicalpodcasts.csv"
    OUTPUT_DIR = "data/raw/audio_samples"
    download_podcasts(CSV_PATH, OUTPUT_DIR, limit=200)
