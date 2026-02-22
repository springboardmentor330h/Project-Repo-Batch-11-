from deep_translator import GoogleTranslator

def test_romanization_support():
    print("Testing deep-translator return type...")
    text = "Hello world"
    try:
        # deep-translator's translate() returns a string usually. 
        # But let's check if there's an option for more details or if we need another library.
        res = GoogleTranslator(source='en', target='te').translate(text)
        print(f"Result type: {type(res)}")
        print(f"Result: {res}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_romanization_support()
