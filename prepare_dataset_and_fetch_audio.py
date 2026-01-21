#!/usr/bin/env python3
"""
Prepare CSVs from Parquet and download first N episode audios.
Final output: ONLY .resampled.wav files
Naming: podcast<row_id_padded>_<video_id>.resampled.wav
"""

import os
import csv
import time
import subprocess
import pandas as pd
from tqdm import tqdm

##### CONFIG #####
PARQUET_PATH = "train-00000-of-00001-25f40520d4548308.parquet"
EPISODES_CSV = "lex_fridman_cleaned.csv"
NUM_EPISODES_TO_FETCH = 100
EPISODE_OUTPUT_DIR = "episodes"
MANIFEST_CSV = "download_manifest.csv"

TARGET_SR = 16000
TARGET_CH = 1

# YT_DLP_OPTS = ["--no-playlist", "--ignore-errors", "--no-warnings"]
COOKIES_FILE = "cookies.txt"
YT_DLP_OPTS = ["--no-playlist", "--ignore-errors", "--no-warnings", "--cookies", COOKIES_FILE]

SLEEP_BETWEEN_DOWNLOADS = 10
##### END CONFIG #####

os.makedirs(EPISODE_OUTPUT_DIR, exist_ok=True)


def clean_text_for_one_line(s):
    if not isinstance(s, str):
        return ""
    return s.replace("\r", " ").replace("\n", " ").strip()


def download_and_resample(video_id, final_path):
    """
    Downloads audio, resamples to 16kHz mono, deletes temp files,
    and saves ONLY final_path (.resampled.wav)
    """
    temp_template = os.path.join(EPISODE_OUTPUT_DIR, "%(id)s.%(ext)s")
    url = f"https://www.youtube.com/watch?v={video_id}"

    # Step 1: Download audio
    # cmd_dl = ["yt-dlp", "-x", "--audio-format", "wav", "-o", temp_template] + YT_DLP_OPTS + [url]
    cmd_dl = [
        "yt-dlp",
        "-f", "bestaudio/best",
        "-x",
        "--audio-format", "wav",
        "--audio-quality", "0",
        "-o", temp_template
    ] + YT_DLP_OPTS + [url]

    try:
        subprocess.run(cmd_dl, check=True)
    except subprocess.CalledProcessError:
        return False

    # Step 2: Find downloaded temp file
    downloaded = None
    for f in os.listdir(EPISODE_OUTPUT_DIR):
        if f.startswith(video_id + ".") and not f.endswith(".resampled.wav"):
            downloaded = os.path.join(EPISODE_OUTPUT_DIR, f)
            break

    if downloaded is None:
        return False

    # Step 3: Resample
    cmd_ff = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-i", downloaded,
        "-ar", str(TARGET_SR),
        "-ac", str(TARGET_CH),
        final_path
    ]

    try:
        subprocess.run(cmd_ff, check=True)
    except subprocess.CalledProcessError:
        return False

    # Step 4: Delete temp file
    try:
        os.remove(downloaded)
    except Exception:
        pass

    return os.path.exists(final_path)


def main():
    print("Loading parquet:", PARQUET_PATH)
    df = pd.read_parquet(PARQUET_PATH)
    print("Rows in parquet:", len(df))

    # Build minimal CSV
    episodes_rows = []
    for idx, row in df.iterrows():
        row_id = int(idx) + 1
        video_id = str(row.get("id", "")).strip()
        title = str(row.get("title", "")).strip()
        transcript = clean_text_for_one_line(str(row.get("text", "")).strip())

        episodes_rows.append({
            "row_id": row_id,
            "video_id": video_id,
            "title": title,
            "transcript": transcript
        })

    episodes_df = pd.DataFrame(episodes_rows)
    episodes_df.to_csv(EPISODES_CSV, index=False)
    print("Saved episodes CSV:", EPISODES_CSV)

    total = len(episodes_df)
    pad_width = len(str(total))

    manifest_exists = os.path.exists(MANIFEST_CSV)
    with open(MANIFEST_CSV, "a", newline="", encoding="utf-8") as mf:
        writer = csv.DictWriter(mf, fieldnames=["row_id", "video_id", "episode_path", "status", "title"])
        if not manifest_exists:
            writer.writeheader()

        to_fetch = episodes_df.head(NUM_EPISODES_TO_FETCH)

        for _, r in tqdm(to_fetch.iterrows(), total=len(to_fetch), desc="fetch"):
            rid = int(r["row_id"])
            vid = r["video_id"]
            title = r["title"]

            padded = str(rid).zfill(pad_width)
            final_name = f"podcast{padded}_{vid}.resampled.wav"
            final_path = os.path.join(EPISODE_OUTPUT_DIR, final_name)

            if os.path.exists(final_path):
                writer.writerow({
                    "row_id": rid,
                    "video_id": vid,
                    "episode_path": final_path,
                    "status": "exists",
                    "title": title
                })
                continue

            print("Downloading:", vid)

            ok = download_and_resample(vid, final_path)

            if ok:
                writer.writerow({
                    "row_id": rid,
                    "video_id": vid,
                    "episode_path": final_path,
                    "status": "downloaded",
                    "title": title
                })
                print(f"[OK] {vid} -> {final_path}")
            else:
                writer.writerow({
                    "row_id": rid,
                    "video_id": vid,
                    "episode_path": "",
                    "status": "failed",
                    "title": title
                })
                print(f"[FAIL] {vid}")

            time.sleep(SLEEP_BETWEEN_DOWNLOADS)

    print("Download manifest saved to:", MANIFEST_CSV)


if __name__ == "__main__":
    main()
