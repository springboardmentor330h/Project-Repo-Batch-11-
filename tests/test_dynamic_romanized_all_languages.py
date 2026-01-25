from language_adaptation.dynamic_romanized_tone import (
    dynamic_romanized_tone,
    SUPPORTED_LANGUAGES
)

print("\n================ DYNAMIC ROMANIZED TONE TEST ================\n")

tests = [
    "I don't understand this",
    "This concept is confusing",
    "Explain this again",
    "Please explain in simple terms",
    "This looks fine"
]

for text in tests:
    print("INPUT :", text)
    for lang, name in SUPPORTED_LANGUAGES.items():
        print(name)
        print("Output:", dynamic_romanized_tone(text, lang))
        print("-" * 60)
