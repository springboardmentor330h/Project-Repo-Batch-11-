#!/usr/bin/env python3
"""
baseline_segmentation.py

Pure baseline segmentation:
 - Read cleaned CSV (row_id, video_id, title, transcript)
 - Sentence-split
 - Chunk into fixed-size chunks (default = 4 sentences)
 - TF-IDF on chunks
 - Cosine similarity between consecutive chunks
 - Auto threshold (mean - k*std OR percentile)
 - Topic boundary detection
 - Outputs per-episode JSON + combined CSV

NO length-based merging or splitting.
"""

import os
import re
import json
import csv
import argparse
from tqdm import tqdm
import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# -------------------------
# Utilities
# -------------------------
SENT_SPLIT_RE = re.compile(r'(?<=[\.\?\!])\s+|\n+')

def split_into_sentences(text):
    if not isinstance(text, str) or text.strip() == "":
        return []
    return [s.strip() for s in SENT_SPLIT_RE.split(text) if s and s.strip()]

def chunk_sentences(sentences, chunk_size):
    if chunk_size <= 1:
        return [[s] for s in sentences]
    return [sentences[i:i+chunk_size] for i in range(0, len(sentences), chunk_size)]

def chunk_texts_from_sent_chunks(sent_chunks):
    return [" ".join(c) for c in sent_chunks]

def words_count(text):
    return len(text.split())


# -------------------------
# Similarity logic
# -------------------------
def compute_chunk_similarities(chunk_texts, tfidf_max_features=None):
    if len(chunk_texts) < 2:
        return np.array([], dtype=float)

    vectorizer = TfidfVectorizer(
        max_features=tfidf_max_features,
        ngram_range=(1,2)
    )
    X = vectorizer.fit_transform(chunk_texts)

    sims = []
    for i in range(len(chunk_texts) - 1):
        sim = cosine_similarity(X[i], X[i+1])[0, 0]
        sims.append(float(sim))

    return np.array(sims, dtype=float)

def detect_boundaries_from_sims(sims, threshold):
    boundaries = [0]
    for i, s in enumerate(sims):
        if s < threshold:
            boundaries.append(i+1)
    return boundaries


# -------------------------
# Segment building
# -------------------------
def build_segments_from_chunk_boundaries(sent_chunks, boundaries):
    segments = []

    # Compute sentence indices
    chunk_start_sent = []
    acc = 0
    for c in sent_chunks:
        chunk_start_sent.append(acc)
        acc += len(c)

    for seg_idx, start_chunk_idx in enumerate(boundaries):
        if seg_idx+1 < len(boundaries):
            end_chunk_idx = boundaries[seg_idx+1] - 1
        else:
            end_chunk_idx = len(sent_chunks)-1

        start_sentence = chunk_start_sent[start_chunk_idx]
        end_sentence = chunk_start_sent[end_chunk_idx] + len(sent_chunks[end_chunk_idx]) - 1

        seg_sentences = []
        for ci in range(start_chunk_idx, end_chunk_idx+1):
            seg_sentences.extend(sent_chunks[ci])

        seg_text = " ".join(seg_sentences).strip()

        segments.append({
            "segment_id": seg_idx,
            "start_sentence": start_sentence,
            "end_sentence": end_sentence,
            "text": seg_text,
            "num_words": words_count(seg_text)
        })

    return segments


# -------------------------
# Episode processing
# -------------------------
def process_episode(row, config):
    row_id = int(row["row_id"])
    audio_id = str(row["video_id"])
    title = row.get("title", "")
    transcript = row.get("transcript", "") or ""

    sentences = split_into_sentences(transcript)
    n_sentences = len(sentences)

    sent_chunks = chunk_sentences(sentences, config["chunk_size"])
    n_chunks = len(sent_chunks)
    chunk_texts = chunk_texts_from_sent_chunks(sent_chunks)

    sims = compute_chunk_similarities(chunk_texts, config["tfidf_max_features"])
    sims_mean = float(np.mean(sims)) if sims.size else 0.0
    sims_std = float(np.std(sims)) if sims.size else 0.0

    if config["use_percentile"] and sims.size:
        threshold = float(np.percentile(sims, config["percentile"]))
    else:
        threshold = max(0.0, sims_mean - config["auto_k"] * sims_std)

    boundaries = detect_boundaries_from_sims(sims, threshold)
    segments = build_segments_from_chunk_boundaries(sent_chunks, boundaries)

    metadata = {
        "row_id": row_id,
        "audio_id": audio_id,
        "title": title,
        "n_sentences": n_sentences,
        "n_chunks": n_chunks,
        "n_segments": len(segments),
        "sims_mean": sims_mean,
        "sims_std": sims_std,
        "sims_threshold": threshold,
        "chunk_size": config["chunk_size"],
        "tfidf_max_features": config["tfidf_max_features"]
    }

    return metadata, segments


# -------------------------
# Output helpers
# -------------------------
def save_episode_json(metadata, segments, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    fname = f"segments_row{metadata['row_id']:03d}_audio_{metadata['audio_id']}.json"
    fpath = os.path.join(out_dir, fname)

    payload = dict(metadata)
    payload["segments"] = segments

    with open(fpath, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)

    return fpath

def append_segments_to_csv(csv_path, metadata, segments, write_header=False):
    header = ["row_id", "audio_id", "segment_id", "start_sentence", "end_sentence", "num_words", "segment_text", "title"]

    with open(csv_path, "a", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
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
                metadata["title"]
            ])


# -------------------------
# CLI
# -------------------------
def parse_args():
    p = argparse.ArgumentParser(description="Baseline segmentation (pure similarity-based)")
    p.add_argument("--input_csv", default="lex_fridman_cleaned.csv")
    p.add_argument("--out_json_dir", default="output_json")
    p.add_argument("--segments_csv", default="segments_all.csv")
    p.add_argument("--n", type=int, default=0)
    p.add_argument("--chunk_size", type=int, default=4)
    p.add_argument("--tfidf_max_features", type=int, default=20000)
    p.add_argument("--use_percentile", action="store_true")
    p.add_argument("--percentile", type=float, default=10.0)
    p.add_argument("--auto_k", type=float, default=1.0)
    return p.parse_args()


def main():
    args = parse_args()

    config = {
        "chunk_size": args.chunk_size,
        "tfidf_max_features": args.tfidf_max_features,
        "use_percentile": args.use_percentile,
        "percentile": args.percentile,
        "auto_k": args.auto_k
    }

    print("Loading:", args.input_csv)
    df = pd.read_csv(args.input_csv, dtype=str).fillna("")

    for col in ["row_id", "video_id", "title", "transcript"]:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")

    n_total = len(df)
    n_to_process = args.n if args.n > 0 else n_total
    n_to_process = min(n_to_process, n_total)

    os.makedirs(args.out_json_dir, exist_ok=True)

    if os.path.exists(args.segments_csv):
        os.remove(args.segments_csv)

    append_segments_to_csv(args.segments_csv, {}, [], write_header=True)

    for i, (_, row) in enumerate(tqdm(df.iterrows(), total=n_to_process, desc="episodes")):
        if i >= n_to_process:
            break

        metadata, segments = process_episode(row, config)
        save_episode_json(metadata, segments, args.out_json_dir)
        append_segments_to_csv(args.segments_csv, metadata, segments)

    print("Done.")
    print("JSON dir:", args.out_json_dir)
    print("CSV:", args.segments_csv)


if __name__ == "__main__":
    main()
