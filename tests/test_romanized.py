
from romanizer import romanize_text

tests = {
    "te": "ఈ భావన గందరగోళంగా ఉంది",
    "hi": "यह एक परीक्षण है",
    "ta": "இந்த கருத்து குழப்பமானது",
    "kn": "ಈ ಪರಿಕಲ್ಪನೆ ಗೊಂದಲಕಾರಿಯಾಗಿದೆ",
    "ml": "ഈ ആശയം ആശയക്കുഴപ്പമാണ്",
    "bn": "এই ধারণাটি বিভ্রান্তিকর",
    "mr": "ही संकल्पना गोंधळात टाकणारी आहे",
    "ur": "یہ تصور الجھن میں ہے",
    "ar": "هذا المفهوم مربك",
    "ru": "Эта концепция сбивает с толку",
    "zh": "这种概念令人困惑",
}

for lang, text in tests.items():
    print(f"\nLANG: {lang.upper()}")
    print("NATIVE   :", text)
    print("ROMANIZED:", romanize_text(text, lang))
    print("-" * 50)
