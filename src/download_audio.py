import os
import time
import pandas as pd
import requests
from urllib.parse import urlparse

CSV_PATH = "dataset/metadata/politicalpodcasts.csv"
OUTPUT_DIR = "dataset/raw_audio"
URL_COLUMN = "url"


def download_audio(url, output_path, retries=3):
    for attempt in range(retries):
        try:
            with requests.get(url, stream=True, timeout=60, allow_redirects=True) as r:
                r.raise_for_status()

                with open(output_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

            return True

        except Exception as e:
            print(f"Retry {attempt + 1}/{retries} failed:", e)
            time.sleep(3)

    return False


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    try:
        df = pd.read_csv(CSV_PATH)
        print("CSV loaded")
        print("Columns:", list(df.columns))
        print("-" * 60)
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return

    success = 0
    failed = 0

    for index, row in df.iterrows():
        url = str(row[URL_COLUMN]).strip()

        if not url.startswith("http"):
            print(f"Invalid URL at row {index + 1}")
            failed += 1
            continue

        parsed = urlparse(url)
        ext = os.path.splitext(parsed.path)[1]
        if ext == "":
            ext = ".mp3"

        filename = f"audio_{index + 1:03}{ext}"
        output_path = os.path.join(OUTPUT_DIR, filename)

        print(f" Downloading {filename}")

        if download_audio(url, output_path):
            print(f" Saved: {filename}\n")
            success += 1
        else:
            print(f"Failed: {filename}\n")
            failed += 1

    print("=" * 60)
    print(f"Download finished")
    print(f"Successful: {success}")
    print(f"Failed: {failed}")


if __name__ == "__main__":
    main()






