from language_adaptation.pipeline import translate_to_romanized

LANGUAGES = {
    "te": "Telugu (Tanglish)",
    "hi": "Hindi (Hinglish)",
    "ta": "Tamil (Tanglish)",
    "kn": "Kannada (Kanglish)",
    "ml": "Malayalam (Manglish)",
    "bn": "Bengali (Banglish)",
    "mr": "Marathi (Minglish)",
    "ur": "Urdu (Roman)",
    "ar": "Arabic (Arablish)",
    "ru": "Russian (Russlish)",
    "zh-cn": "Chinese (Chinglish)",
}

print("\n================ PIPELINE TEST (TRANSLATE → ROMANIZED) ================\n")

input_text = "This concept is confusing"

for lang, name in LANGUAGES.items():
    result = translate_to_romanized(input_text, lang)

    print(name)
    print("English Input :", result["english_input"])
    print("Translated   :", result["translated_text"])
    print("Romanized    :", result["romanized_output"])
    print("-" * 60)
