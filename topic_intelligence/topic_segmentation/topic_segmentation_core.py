import json
import sys
import re
from pathlib import Path
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from .utils.merge_segments import merge_short_segments
from .utils.segment_mapper import map_sentences_to_segments
from .discourse_cleaner import clean_text
from .concept_anchors import has_concept_anchor
from .definition_filter import is_definition
from .keywords import extract_keywords
from .summaries import generate_summary
from textblob import TextBlob


EMBED_MODEL = "all-MiniLM-L6-v2"
SIM_THRESHOLD = 0.82
MIN_DEF_SENTENCES = 2
MAX_SENTENCES_PER_TOPIC = 10

embedder = SentenceTransformer(EMBED_MODEL)


def split_sentences(text: str):
    return [
        s.strip()
        for s in re.split(r'(?<=[.!?])\s+', text)
        if len(s.strip()) > 30
    ]


def segment_topics(segments):
    merged = merge_short_segments(segments)

    sentences = []
    timestamps = []

    for seg in merged:
        for sent in split_sentences(seg["translation"]):
            sentences.append(sent)
            timestamps.append((seg["start"], seg["end"]))

    cleaned = [clean_text(s) for s in sentences]
    embeddings = embedder.encode(cleaned)

    groups = []
    current = [0]
    def_count = 1 if is_definition(sentences[0]) else 0

    for i in range(1, len(sentences)):
        sim = cosine_similarity(
            [embeddings[i - 1]],
            [embeddings[i]]
        )[0][0]

        anchor = has_concept_anchor(sentences[i])
        is_def = is_definition(sentences[i])

        if (anchor and def_count >= MIN_DEF_SENTENCES) or len(current) >= MAX_SENTENCES_PER_TOPIC:
            groups.append(current)
            current = [i]
            def_count = 1 if is_def else 0
        else:
            current.append(i)
            if is_def:
                def_count += 1

    if current:
        groups.append(current)

    return groups, sentences, timestamps


def build_topic(topic_id, ids, sentences, timestamps, original_segments):
    
        
    definition_sents = [sentences[i] for i in ids if is_definition(sentences[i])]
    fallback_sents = [sentences[i] for i in ids]

    base_text = (
        " ".join(definition_sents)
        if len(definition_sents) >= MIN_DEF_SENTENCES
        else " ".join(fallback_sents)
    )

    cleaned = clean_text(base_text)
    summary = generate_summary(cleaned)
    keywords = extract_keywords(cleaned, summary_text=summary)
    
    # Add sentiment analysis
    blob = TextBlob(cleaned)
    sentiment_score = blob.sentiment.polarity
    if sentiment_score > 0.1:
        sentiment = "POSITIVE"
    elif sentiment_score < -0.1:
        sentiment = "NEGATIVE"
    else:
        sentiment = "NEUTRAL"
    
    topic_sentences = [sentences[i] for i in ids]
    topic_timestamps = [timestamps[i] for i in ids]
    sentences_data = map_sentences_to_segments(topic_sentences, topic_timestamps, original_segments)

    return {
        "topic_id": topic_id,
        "start": timestamps[ids[0]][0],
        "end": timestamps[ids[-1]][1],
        "summary": summary,
        "keywords": keywords,
        "text": " ".join(fallback_sents),
        "sentences": sentences_data,
        "sentiment": sentiment,
        "sentiment_score": round(sentiment_score, 2)
    }


def main(input_path):
    
    input_path = Path(input_path)
    
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    topic_ids, sentences, timestamps = segment_topics(data["segments"])

    topics = [
        build_topic(i, ids, sentences, timestamps, data["segments"])
        for i, ids in enumerate(topic_ids)
        if len(ids) >= 3
    ]

    output_path = input_path.parent / "segmented_output.json"
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            {"audio_file": data["audio_file"], "topics": topics},
            f,
            indent=2,
            ensure_ascii=False
        )

    print(f"[SUCCESS] Topic segmentation completed: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m topic_intelligence.topic_segmentation.topic_segmentation_core <pipeline_output.json>")
        sys.exit(1)

    main(sys.argv[1])
