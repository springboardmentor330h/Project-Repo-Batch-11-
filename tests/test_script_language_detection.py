from pipeline_core import detect_language_from_script

tests = {
    "नमस्ते": "hi",
    "తెలుగు": "te",
    "தமிழ்": "ta",
    "ಕನ್ನಡ": "kn",
    "മലയാളം": "ml",
    "বাংলা": "bn",
    "ગુજરાતી": "gu",
    "মণিপুরি": "bn",
    "مرحبا": "ar",
    "Привет": "ru",
    "こんにちは": "ja",
    "你好": "zh",
    "안녕하세요": "ko",
    "Hello world": "en"
}

for text, expected in tests.items():
    detected = detect_language_from_script(text, "en")
    print(text, "→", detected)
    assert detected == expected

print("[SUCCESS] Script-based language detection PASSED (script-honest)")
