import re

DEF_PATTERNS = [
    r"\bis called\b", r"\bmeans\b", r"\brefers to\b",
    r"\bwe use\b", r"\bis used\b", r"\bthe difference\b",
    r"\bin arabic\b", r"\bin english\b", r"\bthis form\b",
    r"\bthis word\b", r"\bthis is\b", r"\bdefinition\b"
]

EX_PATTERNS = [
    r"\bfor example\b", r"\blet us say\b", r"\bfor instance\b",
    r"\bexercise\b", r"\bdrill\b", r"\bpage\b",
    r"\bwe say\b", r"\bgoing to\b"
]

def is_definition(sent: str) -> bool:
    s = sent.lower()
    if any(re.search(p, s) for p in EX_PATTERNS):
        return False
    return any(re.search(p, s) for p in DEF_PATTERNS)
