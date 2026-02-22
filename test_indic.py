from indic_transliteration import sanscript
from indic_transliteration.sanscript import SchemeMap, SCHEMES, transliterate

def test_indic():
    print("Testing indic-transliteration...")
    
    text_te = "నమస్కారం" # Namaskaram
    text_hi = "नमस्ते दुनिया" # Namaste Duniya
    
    # Check what schemes are available
    # usually sanscript.TELUGU, sanscript.DEVANAGARI, sanscript.IAST, sanscript.ITRANS
    
    try:
        # Telugu to IAST
        res_te = transliterate(text_te, sanscript.TELUGU, sanscript.IAST)
        print(f"\nTelugu (IAST): {res_te}")
        
        res_te_hk = transliterate(text_te, sanscript.TELUGU, sanscript.HK)
        print(f"Telugu (HK): {res_te_hk}")

        res_te_itrans = transliterate(text_te, sanscript.TELUGU, sanscript.ITRANS)
        print(f"Telugu (ITRANS): {res_te_itrans}")

        # Hindi to IAST
        res_hi = transliterate(text_hi, sanscript.DEVANAGARI, sanscript.IAST)
        print(f"\nHindi (IAST): {res_hi}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_indic()
