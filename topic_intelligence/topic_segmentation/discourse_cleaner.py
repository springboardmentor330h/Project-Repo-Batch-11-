import re

FILLERS = [
    r"\byou know\b", r"\bokay\b", r"\balright\b",
    r"\buh\b", r"\bum\b", r"\byeah\b",
    r"\bright\b", r"\bjust\b", r"\blike\b", r"\bi mean\b"
]

def clean_text(text: str) -> str:
    t = text.lower()
    for f in FILLERS:
        t = re.sub(f, " ", t)
    t = re.sub(r"\b(\w+)\s+\1\b", r"\1", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()
