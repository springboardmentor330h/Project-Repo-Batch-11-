import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.tokenize import sent_tokenize

# Download necessary nltk data
nltk.download('punkt')

class TopicSegmenter:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        print(f"Loading SBERT model: {model_name}...")
        self.model = SentenceTransformer(model_name)

    def segment_transcript_baseline(self, text, threshold=0.5):
        """
        Algorithm 1: Sentence Similarity Baseline.
        Compares TF-IDF or simple vector similarity between consecutive sentences.
        """
        sentences = sent_tokenize(text)
        if len(sentences) < 2:
            return [text]

        # Using SBERT for simplicity in baseline comparison too, but with a different logic 
        # or we could use simple word overlaps. Let's use cosine similarity of embeddings 
        # but with a fixed threshold for 'baseline'.
        
        embeddings = self.model.encode(sentences)
        
        segments = []
        current_segment = [sentences[0]]
        
        for i in range(1, len(sentences)):
            sim = cosine_similarity([embeddings[i-1]], [embeddings[i]])[0][0]
            
            if sim < threshold:
                segments.append(" ".join(current_segment))
                current_segment = [sentences[i]]
            else:
                current_segment.append(sentences[i])
        
        segments.append(" ".join(current_segment))
        return segments

    def segment_transcript_embedding(self, text, window_size=3, threshold_multiplier=1.3, min_sentences=8):
        """
        Algorithm 3 (Refined): Industrial Topic Segmentation.
        Uses SBERT embeddings and a sliding window to detect true topic drift.
        Enforces a minimum sentence count of 8 to ensure coherent 'chapters'.
        """
        sentences = sent_tokenize(text)
        if len(sentences) < min_sentences:
            return [text]

        # Pre-filter filler-only sentences if needed (simplified here)
        fillers = {"yeah", "i know", "exactly", "that's great", "uh", "you know", "right", "good", "okay"}
        
        embeddings = self.model.encode(sentences)
        
        similarities = []
        for i in range(len(embeddings) - 1):
            sim = cosine_similarity([embeddings[i]], [embeddings[i+1]])[0][0]
            similarities.append(sim)
        
        boundaries = [0]
        avg_sim = np.mean(similarities)
        
        last_boundary = 0
        for i in range(1, len(similarities) - 1):
            # Check if this similarity is a local minimum (potential boundary)
            is_local_min = similarities[i] < similarities[i-1] and similarities[i] < similarities[i+1]
            
            # Significant drop and enough distance from previous boundary
            if is_local_min and similarities[i] < (avg_sim / threshold_multiplier):
                if (i + 1 - last_boundary) >= min_sentences:
                    boundaries.append(i + 1)
                    last_boundary = i + 1
        
        boundaries.append(len(sentences))
        
        segments = []
        for b in range(len(boundaries) - 1):
            seg_text = " ".join(sentences[boundaries[b]:boundaries[b+1]])
            segments.append(seg_text)
            
        return segments

if __name__ == "__main__":
    # Test with a dummy transcript
    sample_text = (
        "Welcome to the political podcast. Today we are talking about the economy. "
        "Inflation is at an all-time high and the stock market is volatile. "
        "The FED is planning to raise interest rates again. "
        "In other news, the election is coming up soon. "
        "Candidates are starting to campaign in Iowa and New Hampshire. "
        "Voter turnout is expected to be record-breaking this year. "
        "Finally, let's talk about the new environmental policy. "
        "The government is investing in green energy and solar panels."
    )
    
    segmenter = TopicSegmenter()
    
    print("\n--- Baseline Segmentation ---")
    baseline_segs = segmenter.segment_transcript_baseline(sample_text, threshold=0.6)
    for i, s in enumerate(baseline_segs):
        print(f"Segment {i+1}: {s[:50]}...")
        
    print("\n--- Embedding-Based Segmentation ---")
    embedding_segs = segmenter.segment_transcript_embedding(sample_text)
    for i, s in enumerate(embedding_segs):
        print(f"Segment {i+1}: {s[:50]}...")
