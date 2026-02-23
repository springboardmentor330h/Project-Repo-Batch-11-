import os
from huggingface_hub import snapshot_download

def download_model_no_symlinks(model_id="Systran/faster-whisper-large-v3", local_dir="models/faster-whisper-large-v3"):
    print(f"Downloading {model_id} to {local_dir} (bypassing symlinks)...")
    os.makedirs(local_dir, exist_ok=True)
    
    # Download directly to the local_dir without symlinks
    snapshot_download(
        repo_id=model_id,
        local_dir=local_dir,
        local_dir_use_symlinks=False,
        # Only download weight files and configs
        ignore_patterns=["*.txt", "*.md", ".git*"]
    )
    print("Download complete.")

if __name__ == "__main__":
    download_model_no_symlinks()
