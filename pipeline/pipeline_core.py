import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import whisper
import json
import unicodedata

from language_adaptation.translator import translate_auto
from language_adaptation.romanizer import romanize_text


WHISPER_MODEL = "base"
USER_PREFERRED_LANGUAGE = "en"


SCRIPT_LANGUAGE_MAP = {
    "DEVANAGARI": "hi",
    "TELUGU": "te",
    "TAMIL": "ta",
    "KANNADA": "kn",
    "MALAYALAM": "ml",
    "BENGALI": "bn",
    "GUJARATI": "gu",
    "MEETEI": "mni",
    "ARABIC": "ar",
    "CYRILLIC": "ru",
    "HIRAGANA": "ja",
    "KATAKANA": "ja",
    "CJK": "zh",
    "HANGUL": "ko"
}


def detect_language_from_script(text: str, fallback: str) -> str:
    for ch in text:
        if ch.isascii():
            continue
        try:
            script = unicodedata.name(ch).split()[0]
        except ValueError:
            continue

        if script in SCRIPT_LANGUAGE_MAP:
            return SCRIPT_LANGUAGE_MAP[script]

    return fallback


def process_audio(audio_path: str) -> dict:
    audio_path = Path(audio_path)

    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    model = whisper.load_model(WHISPER_MODEL)

    result = model.transcribe(
        str(audio_path),
        fp16=False,
        verbose=False
    )

    detected_lang = result.get("language", "en")
    segments_out = []

    for idx, seg in enumerate(result.get("segments", [])):
        text = seg["text"].strip()
        segment_lang = detect_language_from_script(text, detected_lang)

        if segment_lang != USER_PREFERRED_LANGUAGE:
            try:
                translation = translate_auto(text, segment_lang, USER_PREFERRED_LANGUAGE)
            except Exception:
                translation = text
        else:
            translation = text

        if segment_lang != "en":
            try:
                romanized = romanize_text(text, segment_lang)
            except Exception:
                romanized = text
        else:
            romanized = text

        segments_out.append({
            "segment_id": idx,
            "start": float(seg["start"]),
            "end": float(seg["end"]),
            "text": text,
            "language": segment_lang,
            "translation": translation,
            "romanized": romanized
        })

    return {
        "audio_file": audio_path.name,
        "language_detected": detected_lang,
        "segments": segments_out
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python pipeline_core.py <audio_file>")
        sys.exit(1)

    audio_file = sys.argv[1]
    output = process_audio(audio_file)

    OUTPUT_FILE = PROJECT_ROOT / "outputs" / "pipeline_output.json"
    OUTPUT_FILE.parent.mkdir(exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Pipeline output saved to {OUTPUT_FILE}")
