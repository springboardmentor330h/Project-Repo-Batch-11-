from language_adaptation.language_detector import detect_language

tests = [
    "This is English",
    "यह हिंदी है",
    "ఇది తెలుగు",
    "这是中文",
    "مرحبا بك",
    "Это русский текст"
]

print("\n=== LANGUAGE DETECTOR TEST ===\n")

for text in tests:
    lang = detect_language(text)
    print(f"{text}  -->  {lang}")
