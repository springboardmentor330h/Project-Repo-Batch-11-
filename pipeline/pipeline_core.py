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


WHISPER_MODEL = "small"  # Small model (244M params) - good balance of accuracy and speed
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


def process_audio(audio_path: str, source_lang: str = "auto") -> dict:
    """Process audio file and transcribe it.
    
    Args:
        audio_path: Path to the audio file
        source_lang: Language code ('auto' for auto-detect, or specific code like 'te', 'hi', etc.)
    """
    audio_path = Path(audio_path)

    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    model = whisper.load_model(WHISPER_MODEL)

    # Determine transcription language
    if source_lang and source_lang != "auto":
        # Use user-specified language (for when auto-detect fails)
        detected_lang = source_lang
        print(f"Using user-specified language: {detected_lang}")
    else:
        # Auto-detect language from audio
        audio = whisper.load_audio(str(audio_path))
        audio_30s = whisper.pad_or_trim(audio)  # Use first 30 seconds for detection
        mel = whisper.log_mel_spectrogram(audio_30s, n_mels=model.dims.n_mels).to(model.device)
        
        _, probs = model.detect_language(mel)
        detected_lang = max(probs, key=probs.get)
        print(f"Auto-detected language: {detected_lang} (confidence: {probs[detected_lang]:.2f})")

    # Transcribe with determined language
    result = model.transcribe(
        str(audio_path),
        language=detected_lang,  # Use determined language for accurate transcription
        task="transcribe",  # Transcribe in native language, do NOT translate to English
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
    if len(sys.argv) < 2:
        print("Usage: python pipeline_core.py <audio_file> [language_code]")
        print("       language_code: 'auto' (default), 'te', 'hi', 'ta', 'en', etc.")
        sys.exit(1)

    audio_file = sys.argv[1]
    source_lang = sys.argv[2] if len(sys.argv) > 2 else "auto"
    output = process_audio(audio_file, source_lang)

    OUTPUT_FILE = PROJECT_ROOT / "outputs" / "pipeline_output.json"
    OUTPUT_FILE.parent.mkdir(exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Pipeline output saved to {OUTPUT_FILE}")
