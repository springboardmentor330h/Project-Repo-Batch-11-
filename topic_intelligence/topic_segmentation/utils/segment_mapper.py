
from difflib import SequenceMatcher


def similarity_ratio(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def find_best_segment_match(sentence: str, segments: list) -> dict:
    
        
    if not segments:
        return {}
    
    best_match = None
    best_score = 0.0
    
    for seg in segments:
        text_score = similarity_ratio(sentence, seg.get("text", ""))
        trans_score = similarity_ratio(sentence, seg.get("translation", ""))
        
        score = max(text_score, trans_score)
        
        if score > best_score:
            best_score = score
            best_match = seg
    
    if best_score > 0.6:
        return best_match
    
    return {}


def build_sentence_data(sentence: str, segment: dict, start: float, end: float) -> dict:
    
        
    return {
        "text": sentence,
        "translation": segment.get("translation", sentence),
        "romanized": segment.get("romanized", sentence),
        "language": segment.get("language", "en"),
        "start": start,
        "end": end
    }


def map_sentences_to_segments(sentences: list, timestamps: list, segments: list) -> list:
    
        
    sentence_data = []
    
    for i, sentence in enumerate(sentences):
        start, end = timestamps[i] if i < len(timestamps) else (0.0, 0.0)
        
        segment = find_best_segment_match(sentence, segments)
        
        sent_data = build_sentence_data(sentence, segment, start, end)
        sentence_data.append(sent_data)
    
    return sentence_data
