



try:
    from indic_transliteration import sanscript
    from indic_transliteration.sanscript import transliterate
    USE_INDIC = True
except ImportError:
    USE_INDIC = False

from unidecode import unidecode

SUPPORTED_ROMANIZATION_LANGS = {
    "hi", "mr", "sa", "te", "ta", "kn", "ml", "bn", "gu", "mni",
    "ar", "ru", "ja", "zh", "ko", "pa"
}

# Mapping specific languages to indic-transliteration constants
INDIC_SCRIPT_MAP = {
    "hi": sanscript.DEVANAGARI,
    "mr": sanscript.DEVANAGARI,
    "sa": sanscript.DEVANAGARI,
    "te": sanscript.TELUGU,
    "ta": sanscript.TAMIL,
    "kn": sanscript.KANNADA,
    "ml": sanscript.MALAYALAM,
    "bn": sanscript.BENGALI,
    "gu": sanscript.GUJARATI,
    "pa": sanscript.GURMUKHI
}

def romanize_text(text: str, lang: str) -> str:
    """
    Romanize text using indic-transliteration for Indic scripts (IAST format) 
    and unidecode for others.
    """
    if not text or not text.strip():
        return text

    if lang == "en":
        return text

    if lang not in SUPPORTED_ROMANIZATION_LANGS:
        return text

    # Use indic-transliteration for Indic languages if available
    if USE_INDIC and lang in INDIC_SCRIPT_MAP:
        try:
            source_script = INDIC_SCRIPT_MAP[lang]
            # Convert to IAST (International Alphabet of Sanskrit Transliteration)
            # This provides high-quality, readable romanization with diacritics
            romanized = transliterate(text, source_script, sanscript.IAST)
            if romanized and romanized != text:
                return romanized
        except Exception as e:
            print(f"Indic-transliteration error: {e}")
            # Fallback to unidecode

    try:
        romanized = unidecode(text)
        return romanized.strip() if romanized else text
    except Exception:
        return text
