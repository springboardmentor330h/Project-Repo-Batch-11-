#!/usr/bin/env python3
"""
embedding_segmentation.py

Algorithm 2: Embedding-based topic segmentation

Pipeline:
 - Read cleaned CSV (row_id, video_id, title, transcript)
 - Sentence-split (1 sentence = 1 unit)
 - Sentence embeddings using SentenceTransformers
 - Cosine similarity between consecutive sentences
 - Auto threshold (mean - k*std OR percentile)
 - Topic boundary detection
 - Build segments
 - Save per-episode JSON
 - Save combined CSV (segments_all_embedding.csv)

Dependencies:
  pip install pandas numpy tqdm sentence-transformers scikit-learn
"""

import os
import re
import json
import csv
import argparse
import numpy as np
import pandas as pd
from tqdm import tqdm

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# -------------------------
# Utilities
# -------------------------

SENT_SPLIT_RE = re.compile(r'(?<=[\.\?\!])\s+|\n+')

def split_into_sentences(text):
    if not isinstance(text, str) or text.strip() == "":
        return []
    pieces = [s.strip() for s in SENT_SPLIT_RE.split(text) if s and s.strip()]
    return pieces

def word_count(text):
    return len(text.split())


# -------------------------
# Core logic
# -------------------------

def compute_sentence_similarities(sentences, model):
    if len(sentences) < 2:
        return np.array([], dtype=float)

    embeddings = model.encode(sentences, show_progress_bar=False)
    sims = []
    for i in range(len(embeddings) - 1):
        sim = cosine_similarity(
            embeddings[i].reshape(1, -1),
            embeddings[i + 1].reshape(1, -1)
        )[0][0]
        sims.append(float(sim))

    return np.array(sims, dtype=float)


def detect_boundaries_from_sims(sims, threshold):
    boundaries = [0]
    for i, s in enumerate(sims):
        if s < threshold:
            boundaries.append(i + 1)
    return boundaries


def build_segments(sentences, boundaries):
    segments = []

    for seg_id, start_idx in enumerate(boundaries):
        if seg_id + 1 < len(boundaries):
            end_idx = boundaries[seg_id + 1] - 1
        else:
            end_idx = len(sentences) - 1

        seg_sents = sentences[start_idx:end_idx + 1]
        seg_text = " ".join(seg_sents).strip()

        segments.append({
            "segment_id": seg_id,
            "start_sentence": start_idx,
            "end_sentence": end_idx,
            "text": seg_text,
            "num_words": word_count(seg_text)
        })

    return segments


# -------------------------
# Episode processing
# -------------------------

def process_episode(row, model, config):
    row_id = int(row["row_id"])
    audio_id = str(row["video_id"])
    title = row.get("title", "")
    transcript = row.get("transcript", "") or ""

    sentences = split_into_sentences(transcript)
    n_sentences = len(sentences)

    sims = compute_sentence_similarities(sentences, model)
    sims_mean = float(np.mean(sims)) if sims.size > 0 else 0.0
    sims_std = float(np.std(sims)) if sims.size > 0 else 0.0

    if config["use_percentile"]:
        if sims.size > 0:
            threshold = float(np.percentile(sims, config["percentile"]))
        else:
            threshold = config["threshold_fallback"]
    else:
        threshold = max(0.0, sims_mean - config["auto_k"] * sims_std)

    boundaries = detect_boundaries_from_sims(sims, threshold)
    segments = build_segments(sentences, boundaries)

    metadata = {
        "row_id": row_id,
        "audio_id": audio_id,
        "title": title,
        "algorithm": "embedding",
        "n_sentences": n_sentences,
        "n_segments": len(segments),
        "sims_mean": sims_mean,
        "sims_std": sims_std,
        "sims_threshold": threshold,
        "model_name": config["model_name"]
    }

    return metadata, segments


# -------------------------
# I/O helpers
# -------------------------

def save_episode_json(metadata, segments, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    fname = f"segments_row{metadata['row_id']:03d}_audio_{metadata['audio_id']}_embedding.json"
    path = os.path.join(out_dir, fname)

    payload = dict(metadata)
    payload["segments"] = segments

    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    return path


def append_segments_to_csv(csv_path, metadata, segments, write_header=False):
    header = ["row_id", "audio_id", "segment_id", "start_sentence", "end_sentence", "num_words", "segment_text", "title", "algorithm"]

    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(header)

        for s in segments:
            writer.writerow([
                metadata["row_id"],
                metadata["audio_id"],
                s["segment_id"],
                s["start_sentence"],
                s["end_sentence"],
                s["num_words"],
                s["text"].replace("\n", " ").replace("\r", " "),
                metadata.get("title", ""),
                "embedding"
            ])


# -------------------------
# CLI
# -------------------------

def parse_args():
    p = argparse.ArgumentParser(description="Embedding-based topic segmentation")
    p.add_argument("--input_csv", default="lex_fridman_cleaned.csv")
    p.add_argument("--out_json_dir", default="output_json_embedding")
    p.add_argument("--segments_csv", default="segments_all_embedding.csv")
    p.add_argument("--n", type=int, default=0)
    p.add_argument("--model_name", default="all-MiniLM-L6-v2")
    p.add_argument("--use_percentile", action="store_true")
    p.add_argument("--percentile", type=float, default=10.0)
    p.add_argument("--auto_k", type=float, default=1.0)
    p.add_argument("--threshold_fallback", type=float, default=0.0)
    return p.parse_args()


# -------------------------
# Main
# -------------------------

def main():
    args = parse_args()

    config = {
        "model_name": args.model_name,
        "use_percentile": args.use_percentile,
        "percentile": args.percentile,
        "auto_k": args.auto_k,
        "threshold_fallback": args.threshold_fallback
    }

    print("Loading embedding model:", args.model_name)
    model = SentenceTransformer(args.model_name)

    print("Loading CSV:", args.input_csv)
    df = pd.read_csv(args.input_csv, dtype=str).fillna("")

    for col in ["row_id", "video_id", "transcript", "title"]:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")

    total = len(df)
    n_to_process = args.n if args.n > 0 else total
    n_to_process = min(n_to_process, total)

    os.makedirs(args.out_json_dir, exist_ok=True)

    if os.path.exists(args.segments_csv):
        os.remove(args.segments_csv)

    append_segments_to_csv(args.segments_csv, {}, [], write_header=True)

    processed = 0

    for i, (_, row) in enumerate(tqdm(df.iterrows(), total=n_to_process, desc="episodes")):
        if i >= n_to_process:
            break

        metadata, segments = process_episode(row, model, config)
        save_episode_json(metadata, segments, args.out_json_dir)
        append_segments_to_csv(args.segments_csv, metadata, segments)

        processed += 1

    print(f"\nDone. Processed {processed} episodes.")
    print("JSON output:", args.out_json_dir)
    print("Combined CSV:", args.segments_csv)


if __name__ == "__main__":
    main()
