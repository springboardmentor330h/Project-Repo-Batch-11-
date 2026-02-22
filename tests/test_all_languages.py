from language_adaptation.translator import translate_auto

tests = [
    ("English → Hindi", "This is a test", "hi"),
    ("English → Telugu", "This is a test", "te"),
    ("English → Tamil", "This is a test", "ta"),
    ("English → Kannada", "This is a test", "kn"),
    ("English → Malayalam", "This is a test", "ml"),
    ("English → Bengali", "This is a test", "bn"),
    ("English → Marathi", "This is a test", "mr"),
    ("English → Urdu", "This is a test", "ur"),
    ("English → Arabic", "This is a test", "ar"),
    ("English → Russian", "This is a test", "ru"),
    ("English → Chinese", "This is a test", "zh-cn"),

    ("Hindi → English", "यह एक परीक्षण है", "en"),
    ("Telugu → English", "ఇది ఒక పరీక్ష", "en"),
    ("Tamil → English", "இது ஒரு சோதனை", "en"),
    ("Kannada → English", "ಇದು ಒಂದು ಪರೀಕ್ಷೆ", "en"),
    ("Malayalam → English", "ഇത് ഒരു പരീക്ഷണമാണ്", "en"),
    ("Bengali → English", "এটি একটি পরীক্ষা", "en"),
    ("Marathi → English", "हे एक चाचणी आहे", "en"),
    ("Urdu → English", "یہ ایک امتحان ہے", "en"),
    ("Arabic → English", "هذا اختبار", "en"),
    ("Russian → English", "Это тест", "en"),
    ("Chinese → English", "这是一个测试", "en"),
]

print("\n================ TRANSLATION TEST RESULTS ================\n")

for label, text, target in tests:
    print(label)
    print("Input :", text)
    print("Output:", translate_auto(text, target))
    print("-" * 60)
