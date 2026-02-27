import sys
import os
# Add parent directory to path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from topic_segmentation import TopicSegmenter

def test_segmenter():
    print("Initializing Segmenter...")
    seg = TopicSegmenter()
    
    text = """
    Artificial Intelligence is rapidly evolving. Machine learning models are becoming more capable. 
    Neural networks mimic the human brain. Data is the oil of the digital age.
    
    Pizza is a popular dish in Italy. The dough is made from flour and water. 
    Tomatoes and cheese are essential toppings. Baking requires a hot oven.
    """
    
    print("\n--- Test 1: Similarity Segmentation ---")
    s1 = seg.segment_with_similarity(text, window_size=2)
    print(f"Segments found: {len(s1)}")
    for s in s1:
        print(f"- {s['text'][:30]}...")
        
    print("\n--- Test 2: TextTiling ---")
    s2 = seg.segment_with_texttiling(text)
    print(f"Segments found: {len(s2)}")
    
    print("\n--- Test 3: Keywords ---")
    k = seg.extract_keywords(text)
    print(f"Keywords: {k}")
    
    print("\n✅ Verification Script Finished")

if __name__ == "__main__":
    test_segmenter()
