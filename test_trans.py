from deep_translator import GoogleTranslator
import time

def test_translation():
    print("Testing deep-translator...")
    text = "Hello, world! Welcome to the podcast."
    
    try:
        # Try Telugu
        res = GoogleTranslator(source='auto', target='te').translate(text)
        print(f"Telugu: {res}")
        
        # Try Hindi
        res = GoogleTranslator(source='auto', target='hi').translate(text)
        print(f"Hindi: {res}")
        
        print("Success!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_translation()
