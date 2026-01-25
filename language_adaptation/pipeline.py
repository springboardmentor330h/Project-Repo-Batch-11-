
from language_adaptation.romanizer import romanize_text


def romanize_pipeline(text: str, lang: str) -> str:
    return romanize_text(text, lang)
