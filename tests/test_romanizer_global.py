from language_adaptation.romanizer import romanize_text

tests = [
    ("hi", "यह एक परीक्षण है"),
    ("te", "ఇది పరీక్ష"),
    ("ta", "இது சோதனை"),
    ("ar", "مرحبا بكم"),
    ("ru", "Сегодня мы говорим"),
    ("zh", "今天我们讨论"),
    ("en", "This should stay same")
]

for lang, text in tests:
    print(f"LANG: {lang}")
    print("INPUT:", text)
    print("ROMANIZED:", romanize_text(text, lang))
    print("=" * 60)
