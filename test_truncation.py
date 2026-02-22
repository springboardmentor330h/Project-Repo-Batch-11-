from language_adaptation.translator import translate_auto
import time

def test_truncation():
    print("Testing Translation Truncation...")
    
    # Create a long text (~6000 chars)
    sentence = "This is a sentence that we will repeat to make a long text. "
    long_text = sentence * 200
    
    print(f"Original Length: {len(long_text)} chars")
    
    try:
        start = time.time()
        translated = translate_auto(long_text, "en", "te") # Translate to Telugu
        end = time.time()
        
        print(f"Translation Time: {end - start:.2f}s")
        print(f"Translated Length: {len(translated)} chars")
        
        # Check if it's significantly shorter (indicative of truncation)
        # Telugu text is usually shorter/longer but not by 90%
        ratio = len(translated) / len(long_text)
        print(f"Length Ratio: {ratio:.2f}")
        
        if ratio < 0.5:
            print("⚠️ POTENTIAL TRUNCATION DETECTED!")
        else:
            print("✅ Verification passed (no obvious truncation)")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_truncation()
