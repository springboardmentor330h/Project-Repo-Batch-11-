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
from .topic_title_generator import generate_topic_title
from textblob import TextBlob

# Import animation module
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from topic_intelligence.animation.animation_state import generate_animation_states


# =========================
# CONFIG
# =========================

EMBED_MODEL = "all-MiniLM-L6-v2"
SIM_THRESHOLD = 0.82
MIN_DEF_SENTENCES = 2
MAX_SENTENCES_PER_TOPIC = 10
PROJECT_TITLE = "LEXARA: Automated Podcast Transcription & Insights"

embedder = SentenceTransformer(EMBED_MODEL)


def split_sentences(text: str):
    """Split text into sentences with minimum length."""
    return [
        s.strip()
        for s in re.split(r'(?<=[.!?])\s+', text)
        if len(s.strip()) > 30
    ]


def segment_topics(segments):
    """
    Segment transcript into topic groups based on semantic similarity.
    
    Args:
        segments: List of transcript segments from Whisper
        
    Returns:
        Tuple of (topic_groups, sentences, timestamps)
    """
    merged = merge_short_segments(segments)

    sentences = []
    timestamps = []

    for seg in merged:
        for sent in split_sentences(seg["translation"]):
            sentences.append(sent)
            timestamps.append((seg["start"], seg["end"]))

    if not sentences:
        return [], [], []

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
    """
    Build a complete topic object with title, summary, keywords, and sentiment.
    
    Args:
        topic_id: Unique topic identifier
        ids: List of sentence indices in this topic
        sentences: All sentences list
        timestamps: All timestamps list
        original_segments: Original Whisper segments
        
    Returns:
        Dictionary with topic data including topic_title
    """
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
    
    # Generate context-aware topic title (max 8-10 words)
    topic_title = generate_topic_title(cleaned, keywords)
    
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
        "segment_id": f"seg_{topic_id + 1:03d}",
        "start": timestamps[ids[0]][0],
        "end": timestamps[ids[-1]][1],
        "topic_title": topic_title,
        "summary": summary,
        "keywords": keywords,
        "text": " ".join(fallback_sents),
        "sentences": sentences_data,
        "sentiment": sentiment,
        "sentiment_score": round(sentiment_score, 2)
    }


def validate_topics(topics):
    """
    Validate topic output for completeness and non-overlap.
    
    Args:
        topics: List of topic dictionaries
        
    Returns:
        Tuple of (is_valid, errors)
    """
    errors = []
    
    # Check each segment has exactly one topic title
    for topic in topics:
        if not topic.get("topic_title"):
            errors.append(f"Topic {topic.get('topic_id')} missing topic_title")
    
    # Check for overlapping segments
    sorted_topics = sorted(topics, key=lambda t: t.get("start", 0))
    for i in range(1, len(sorted_topics)):
        prev = sorted_topics[i-1]
        curr = sorted_topics[i]
        if prev.get("end", 0) > curr.get("start", 0):
            errors.append(f"Overlapping: {prev.get('segment_id')} and {curr.get('segment_id')}")
    
    return len(errors) == 0, errors


def main(input_path):
    """
    Main entry point for topic segmentation.
    
    Args:
        input_path: Path to pipeline_output.json
    """
    input_path = Path(input_path)
    
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    topic_ids, sentences, timestamps = segment_topics(data["segments"])

    topics = [
        build_topic(i, ids, sentences, timestamps, data["segments"])
        for i, ids in enumerate(topic_ids)
        if len(ids) >= 3
    ]
    
    # Validate topics
    is_valid, errors = validate_topics(topics)
    if not is_valid:
        print(f"[WARNING] Validation issues: {errors}")
    
    # Generate animation states for 3D visualization
    animation_states = generate_animation_states(topics)

    output_path = input_path.parent / "segmented_output.json"
    
    # Format output according to LEXARA schema
    output_data = {
        "Project_Title": PROJECT_TITLE,
        "audio_file": data["audio_file"],
        "topics": topics,
        "Transcription_Output": [
            {
                "Segment_ID": t["segment_id"],
                "Start_Time": t["start"],
                "End_Time": t["end"],
                "Topic_Title": t["topic_title"],
                "Transcript_Text": t["text"]
            }
            for t in topics
        ],
        "3D_Animation_Output": animation_states
    }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            output_data,
            f,
            indent=2,
            ensure_ascii=False
        )

    print(f"[SUCCESS] LEXARA topic segmentation completed: {output_path}")
    print(f"[INFO] Generated {len(topics)} topics with titles and animation states")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m topic_intelligence.topic_segmentation.topic_segmentation_core <pipeline_output.json>")
        sys.exit(1)

    main(sys.argv[1])
