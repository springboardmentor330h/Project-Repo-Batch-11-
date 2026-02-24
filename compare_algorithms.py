#!/usr/bin/env python3

"""
compare_algorithms.py

Step 5: Compare baseline vs embedding segmentation.

Outputs:
 - comparison_summary.csv
 - boundary_overlap.csv
 - plots/

Usage:
  python compare_algorithms.py
"""

import os
import json
import pandas as pd
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt

BASELINE_DIR = "output_json_baseline"
EMBEDDING_DIR = "output_json_embedding"
OUT_DIR = "comparison_outputs"

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(os.path.join(OUT_DIR, "plots"), exist_ok=True)


def load_jsons(folder):
    data = {}
    for f in os.listdir(folder):
        if f.endswith(".json"):
            path = os.path.join(folder, f)
            with open(path, "r", encoding="utf-8") as fh:
                j = json.load(fh)
                key = j["audio_id"]
                data[key] = j
    return data


def get_boundaries(segments):
    return [s["start_sentence"] for s in segments]


def main():
    print("Loading baseline outputs...")
    baseline = load_jsons(BASELINE_DIR)

    print("Loading embedding outputs...")
    embedding = load_jsons(EMBEDDING_DIR)

    rows = []
    overlap_rows = []

    common_ids = set(baseline.keys()) & set(embedding.keys())

    print(f"Found {len(common_ids)} common episodes")

    for aid in tqdm(common_ids):
        b = baseline[aid]
        e = embedding[aid]

        b_segs = b["segments"]
        e_segs = e["segments"]

        b_lens = [s["num_words"] for s in b_segs]
        e_lens = [s["num_words"] for s in e_segs]

        rows.append({
            "audio_id": aid,
            "baseline_segments": len(b_segs),
            "embedding_segments": len(e_segs),
            "baseline_avg_words": np.mean(b_lens),
            "embedding_avg_words": np.mean(e_lens),
            "baseline_std_words": np.std(b_lens),
            "embedding_std_words": np.std(e_lens)
        })

        b_bounds = set(get_boundaries(b_segs))
        e_bounds = set(get_boundaries(e_segs))

        intersection = len(b_bounds & e_bounds)
        union = len(b_bounds | e_bounds)

        jaccard = intersection / union if union > 0 else 0

        overlap_rows.append({
            "audio_id": aid,
            "baseline_boundaries": len(b_bounds),
            "embedding_boundaries": len(e_bounds),
            "common_boundaries": intersection,
            "jaccard_similarity": jaccard
        })

    df_summary = pd.DataFrame(rows)
    df_overlap = pd.DataFrame(overlap_rows)

    df_summary.to_csv(os.path.join(OUT_DIR, "comparison_summary.csv"), index=False)
    df_overlap.to_csv(os.path.join(OUT_DIR, "boundary_overlap.csv"), index=False)

    print("Saved:")
    print(" - comparison_summary.csv")
    print(" - boundary_overlap.csv")

    # ---- Plots ----

    plt.figure(figsize=(10,5))
    plt.hist(df_summary["baseline_segments"], alpha=0.5, label="Baseline")
    plt.hist(df_summary["embedding_segments"], alpha=0.5, label="Embedding")
    plt.legend()
    plt.title("Segment Count Distribution")
    plt.xlabel("Number of segments")
    plt.ylabel("Frequency")
    plt.savefig(os.path.join(OUT_DIR, "plots", "segment_count_dist.png"))
    plt.close()

    plt.figure(figsize=(10,5))
    plt.hist(df_summary["baseline_avg_words"], alpha=0.5, label="Baseline")
    plt.hist(df_summary["embedding_avg_words"], alpha=0.5, label="Embedding")
    plt.legend()
    plt.title("Average Segment Length (words)")
    plt.xlabel("Words")
    plt.ylabel("Frequency")
    plt.savefig(os.path.join(OUT_DIR, "plots", "segment_length_dist.png"))
    plt.close()

    print("Plots saved in comparison_outputs/plots/")


if __name__ == "__main__":
    main()
