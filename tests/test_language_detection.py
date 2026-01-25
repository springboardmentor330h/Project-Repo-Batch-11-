from language_adaptation.language_detector import detect_language

samples = {
    "en": "Hello, welcome to McDonald's",
    "hi": "यह एक परीक्षण वाक्य है",
    "te": "ఇది ఒక పరీక్ష వాక్యం",
    "ta": "இது ஒரு சோதனை வாக்கியம்",
    "ar": "مرحبا بكم في ماكدونالدز",
    "ru": "Сегодня мы говорим о Макдональдсе",
    "zh": "今天我们讨论麦当劳"
}

for expected, text in samples.items():
    detected = detect_language(text)
    print(f"TEXT: {text}")
    print(f"EXPECTED: {expected}, DETECTED: {detected}")
    print("-" * 50)
