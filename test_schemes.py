from aksharamukha import transliterate

def test_schemes():
    print("Testing Aksharamukha Schemes...")
    
    text_te = "నమస్కారం"
    schemes = ['ISO', 'IAST', 'HK', 'ITRANS', 'Velthuis']
    
    print(f"Original: {text_te}")
    for scheme in schemes:
        try:
            res = transliterate.process("Telugu", scheme, text_te)
            print(f"{scheme}: {res}")
        except Exception as e:
            print(f"{scheme} error: {e}")

if __name__ == "__main__":
    test_schemes()
