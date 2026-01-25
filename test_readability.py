from language_adaptation.romanizer import romanize_text

def test_readability():
    print("Testing Romanization Readability (Aksharamukha)...")
    
    cases = [
        ("te", "నమస్కారం", "Ramarkaram or similar Readable"), 
        ("hi", "नमस्ते दुनिया", "Namaste Duniya"),
        ("ta", "வணக்கம்", "Vanakkam"),
        ("ml", "നമസ്കാരം", "Namaskaram")
    ]
    
    for lang, text, expected in cases:
        result = romanize_text(text, lang)
        print(f"\nLanguage: {lang}")
        print(f"Original: {text}")
        print(f"Romanized: {result}")
        # print(f"Expected (approx): {expected}")

if __name__ == "__main__":
    test_readability()
