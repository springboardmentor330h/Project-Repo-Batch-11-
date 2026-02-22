from language_adaptation.romanizer import romanize_text

tests = {
    "hi": "यह एक परीक्षण है",
    "te": "ఇది ఒక పరీక్ష",
    "ta": "இது ஒரு சோதனை",
    "kn": "ಇದು ಒಂದು ಪರೀಕ್ಷೆ",
    "ml": "ഇത് ഒരു പരീക്ഷണം",
    "ur": "یہ ایک امتحان ہے",
    "ar": "هذا اختبار",
    "ru": "Это тест",
    "zh": "这是一个测试",
}

print("\n=== GLOBAL ROMANIZER TEST ===\n")

for lang, text in tests.items():
    try:
        result = romanize_text(text, lang)
        print(f"{lang} | {text} → {result}")
    except Exception as e:
        print(f"{lang} | ERROR → {e}")
