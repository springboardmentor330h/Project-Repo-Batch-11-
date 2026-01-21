#!/usr/bin/env python3
"""
keywords_and_summaries.py

Offline keyword extraction + LLM summaries using T5-small.

Outputs:
 - Updated JSONs with keywords + summaries
 - segments_keywords.csv
 - segments_summaries.csv
"""

import os
import json
import argparse
from glob import glob
from tqdm import tqdm
import re
import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize

import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# NLTK setup
try:
    nltk.data.find("tokenizers/punkt")
except:
    nltk.download("punkt")
try:
    nltk.data.find("corpora/stopwords")
except:
    nltk.download("stopwords")

STOPWORDS = set(stopwords.words("english"))

def normalize_text(s):
    if not isinstance(s, str):
        return ""
    return s.replace("\n", " ").strip()

def simple_tokenize_for_tfidf(text):
    return text.lower()

# ------------------ KEYWORDS ------------------

def extract_keywords_tfidf(text, top_k=10):
    text = simple_tokenize_for_tfidf(text)
    if not text.strip():
        return []

    words = [w for w in word_tokenize(text) if w.isalpha() and w not in STOPWORDS]
    if len(words) < 4:
        freq = {}
        for w in words:
            freq[w] = freq.get(w, 0) + 1
        kws = sorted(freq.items(), key=lambda x: -x[1])
        return [w for w, _ in kws[:top_k]]

    vec = TfidfVectorizer(ngram_range=(1,2), stop_words="english")
    try:
        X = vec.fit_transform([text])
    except:
        return []

    feature_array = np.array(vec.get_feature_names_out())
    tfidf_scores = np.ravel(X.sum(axis=0))
    if tfidf_scores.size == 0:
        return []

    top_idxs = tfidf_scores.argsort()[::-1][:top_k]
    return feature_array[top_idxs].tolist()

# ------------------ SUMMARY ------------------

def summarize_t5(model, tokenizer, text):
    text = normalize_text(text)
    if len(text.split()) < 20:
        return text

    input_text = "summarize: " + text

    inputs = tokenizer(
        input_text,
        return_tensors="pt",
        truncation=True,
        max_length=512
    )

    input_len = inputs["input_ids"].shape[1]

    max_len = min(80, int(input_len * 0.6))
    min_len = max(10, int(max_len * 0.4))

    if min_len >= max_len:
        min_len = max_len - 1

    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_length=max_len,
            min_length=min_len,
            do_sample=False,
            num_beams=1
        )

    return tokenizer.decode(output[0], skip_special_tokens=True)

# ------------------ PROCESS ------------------

def process_one_json(path, model, tokenizer, args, out_json_dir, keywords_rows, summaries_rows):
    with open(path, "r", encoding="utf-8") as fh:
        payload = json.load(fh)

    segments = payload.get("segments", [])
    row_id = payload.get("row_id")
    audio_id = payload.get("audio_id")

    for seg in segments:
        seg_id = seg.get("segment_id")
        seg_text = normalize_text(seg.get("text", ""))

        # Keywords
        kws = extract_keywords_tfidf(seg_text, top_k=args.top_k)
        seg["keywords"] = kws

        # Summary
        try:
            summ = summarize_t5(model, tokenizer, seg_text)
        except Exception:
            summ = seg_text[:200]

        seg["summary"] = summ

        keywords_rows.append({
            "row_id": row_id,
            "audio_id": audio_id,
            "segment_id": seg_id,
            "keywords": ";".join(kws)
        })

        summaries_rows.append({
            "row_id": row_id,
            "audio_id": audio_id,
            "segment_id": seg_id,
            "summary": summ
        })

    out_path = os.path.join(out_json_dir, os.path.basename(path))
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)

# ------------------ MAIN ------------------

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input_json_dir", required=True)
    p.add_argument("--out_dir", default="output_kws_summaries")
    p.add_argument("--top_k", type=int, default=10)
    p.add_argument("--local_model_dir", required=True)
    args = p.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    out_json_dir = os.path.join(args.out_dir, "json_updated")
    os.makedirs(out_json_dir, exist_ok=True)

    print("Loading T5 model (offline)...")
    tokenizer = AutoTokenizer.from_pretrained(args.local_model_dir, local_files_only=True)
    model = AutoModelForSeq2SeqLM.from_pretrained(args.local_model_dir, local_files_only=True)
    model.eval()

    json_files = sorted(glob(os.path.join(args.input_json_dir, "*.json")))
    print(f"Found {len(json_files)} JSON files")

    keywords_rows = []
    summaries_rows = []

    for path in tqdm(json_files, desc="Processing"):
        try:
            process_one_json(path, model, tokenizer, args, out_json_dir, keywords_rows, summaries_rows)
        except Exception as e:
            print(f"[WARN] Failed {path}: {e}")

    pd.DataFrame(keywords_rows).to_csv(os.path.join(args.out_dir, "segments_keywords.csv"), index=False)
    pd.DataFrame(summaries_rows).to_csv(os.path.join(args.out_dir, "segments_summaries.csv"), index=False)

    print("Done.")
    print("Updated JSONs:", out_json_dir)

if __name__ == "__main__":
    main()
