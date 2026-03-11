"""
AudioInsight — One-Time Setup Script
Run this once before launching the app for the first time.

Usage:
    python setup.py
"""

import subprocess
import sys
from pathlib import Path


def run(cmd, label):
    print(f"\n{'─'*60}")
    print(f"  {label}")
    print(f"{'─'*60}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"  ⚠ Command exited with code {result.returncode} — check output above.")
    else:
        print(f"  ✓ Done")
    return result.returncode == 0


def main():
    print("\n" + "="*60)
    print("  AudioInsight Setup")
    print("="*60)

    # 1. Install Python packages
    run(f"{sys.executable} -m pip install -r requirements.txt",
        "Installing Python dependencies…")

    # 2. Download NLTK data
    print("\n  Downloading NLTK data…")
    try:
        import nltk
        for pkg in ["stopwords", "punkt", "punkt_tab"]:
            nltk.download(pkg, quiet=True)
        print("  ✓ NLTK data ready")
    except Exception as e:
        print(f"  ⚠ NLTK download skipped: {e}")

    # 3. Download TextBlob corpora
    print("\n  Downloading TextBlob corpora…")
    try:
        import subprocess
        subprocess.run([sys.executable, "-m", "textblob.download_corpora"], check=False)
        print("  ✓ TextBlob corpora ready")
    except Exception as e:
        print(f"  ⚠ TextBlob download skipped: {e}")

    # 4. Verify Whisper
    print("\n  Verifying Whisper…")
    try:
        import whisper
        print("  ✓ Whisper installed")
    except ImportError:
        print("  ✗ Whisper not found — run: pip install openai-whisper")

    # 5. Verify Streamlit
    print("\n  Verifying Streamlit…")
    try:
        import streamlit
        print(f"  ✓ Streamlit {streamlit.__version__}")
    except ImportError:
        print("  ✗ Streamlit not found — run: pip install streamlit")

    # 6. Create output directories
    print("\n  Creating output directories…")
    for d in ["output/transcripts", "output/transcripts_cleaned",
              "output/topics", "output/topics_enhanced",
              "dataset/raw_audio", "dataset/processed_audio",
              "storage"]:
        Path(d).mkdir(parents=True, exist_ok=True)
    print("  ✓ Directories ready")

    # 7. Check all pipeline modules exist
    print("\n  Checking pipeline modules…")
    modules = [
        "audio_preprocessing.py",
        "transcribe.py",
        "trancript_cleaner.py",
        "algorithim2.py",
        "algorithim3.py",
        "evaluate.py",
        "speaker_diarization.py",
        "analytics.py",
        "data_storage.py",
        "url_downloader.py",
        "download_audio.py",
        "compare.py",
        "app.py",
    ]
    missing = [m for m in modules if not Path(m).exists()]
    if missing:
        print(f"  ⚠ Missing files (place them in this directory):")
        for m in missing:
            print(f"      — {m}")
    else:
        print(f"  ✓ All {len(modules)} pipeline modules found")

    print("\n" + "="*60)
    print("  Setup complete!")
    print("="*60)
    print("\n  To launch the app:")
    print("      streamlit run app.py\n")


if __name__ == "__main__":
    main()
