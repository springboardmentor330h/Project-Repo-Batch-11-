import re

ANCHORS = [
    r"\bnow\b", r"\bnext\b", r"\banother\b",
    r"\bremember\b", r"\bimportant\b",
    r"\bthe difference\b", r"\bthis is called\b",
    r"\bthis means\b", r"\bin arabic\b", r"\bin english\b"
]

def has_concept_anchor(sentence: str) -> bool:
    s = sentence.lower()
    return any(re.search(p, s) for p in ANCHORS)
