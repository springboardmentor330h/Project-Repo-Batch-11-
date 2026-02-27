import os
import json
import numpy as np
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import sent_tokenize
from scipy.signal import argrelextrema

# Lazy import for heavy libraries
try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

class TopicSegmenter:
    def __init__(self):
        self.embedding_model = None
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)

    def _load_model(self):
        if self.embedding_model is None:
            if SentenceTransformer is None:
                raise ImportError("sentence-transformers not installed")
            print("Loading embedding model...")
            self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

    def _merge_short_segments(self, segments, min_len_chars=200):
        """
        Merges segments that are too short into the previous one.
        Unconditionally merges if len < min_len_chars.
        """
        if not segments:
            return []
        
        merged = [segments[0]]
        for i in range(1, len(segments)):
            curr = segments[i]
            prev = merged[-1]
            
            if len(curr["text"]) < min_len_chars:
                prev["text"] += " " + curr["text"]
            else:
                merged.append(curr)
        return merged

    def segment_with_similarity(self, text, window_size=5, threshold=0.4):
        """
        Algorithm 1: Sentence Similarity Baseline (Improved)
        """
        sentences = sent_tokenize(text)
        if len(sentences) < window_size * 2:
            return [{"text": text}]

        windows = []
        for i in range(0, len(sentences), window_size):
            window_text = " ".join(sentences[i:i+window_size])
            windows.append(window_text)

        vectorizer = TfidfVectorizer(stop_words='english')
        try:
            tfidf_matrix = vectorizer.fit_transform(windows)
            sims = cosine_similarity(tfidf_matrix[:-1], tfidf_matrix[1:]).diagonal()
        except ValueError:
            return [{"text": text}]

        adaptive_thresh = np.mean(sims) - 0.5 * np.std(sims)
        final_thresh = min(threshold, adaptive_thresh)

        boundaries = [0]
        for i, sim in enumerate(sims):
            if sim < final_thresh:
                boundaries.append(i + 1)
        boundaries.append(len(windows))

        segments = []
        for i in range(len(boundaries) - 1):
            start_idx = boundaries[i] * window_size
            end_idx = boundaries[i+1] * window_size
            segment_text = " ".join(sentences[start_idx:end_idx])
            segments.append({"text": segment_text})
        
        return self._merge_short_segments(segments, min_len_chars=300)

    def segment_with_texttiling(self, text):
        """
        Algorithm 2: TextTiling (NLTK)
        """
        try:
            tt = nltk.tokenize.TextTilingTokenizer(w=20, k=6) 
            sentences = sent_tokenize(text)
            chunk_size = 10 
            fake_paragraphs = [" ".join(sentences[i:i+chunk_size]) for i in range(0, len(sentences), chunk_size)]
            prep_text = "\n\n".join(fake_paragraphs)
            
            tiles = tt.tokenize(prep_text)
            segments = [{"text": tile.replace("\n\n", " ").strip()} for tile in tiles]
            return self._merge_short_segments(segments)
        except Exception as e:
            print(f"TextTiling failed: {e}")
            return [{"text": text}]

    def segment_with_embeddings(self, text, threshold=0.55):
        """
        Algorithm 3: Embedding-based (Robust)
        """
        self._load_model()
        sentences = sent_tokenize(text)
        if not sentences:
            return []

        chunk_size = 5 
        chunks = [" ".join(sentences[i:i+chunk_size]) for i in range(0, len(sentences), chunk_size)]
        
        if len(chunks) < 2:
            return [{"text": text}]

        embeddings = self.embedding_model.encode(chunks)
        sims = cosine_similarity(embeddings[:-1], embeddings[1:]).diagonal()
        
        cutoff = np.mean(sims) - 0.15 
        
        boundaries = [0]
        for i, sim in enumerate(sims):
            if sim < cutoff:
                boundaries.append(i + 1)
        boundaries.append(len(chunks))
        
        segments = []
        for i in range(len(boundaries) - 1):
            start_idx = boundaries[i]
            end_idx = boundaries[i+1]
            segment_text = " ".join(chunks[start_idx:end_idx])
            segments.append({"text": segment_text})
            
        return self._merge_short_segments(segments, min_len_chars=500)

    def enforce_topic_count(self, segments, min_topics=10, max_topics=15):
        """
        Ensures the number of segments falls within the specified range.
        This is a port of the logic from the old root script.
        """
        if not segments:
            return []

        # Merge until max_topics
        while len(segments) > max_topics:
            # Find smallest segment by text length
            smallest_idx = min(range(len(segments)), key=lambda i: len(segments[i]["text"]))
            if smallest_idx > 0:
                segments[smallest_idx - 1]["text"] += " " + segments[smallest_idx]["text"]
                del segments[smallest_idx]
            else:
                # If it's the first one, merge with next
                if len(segments) > 1:
                    segments[0]["text"] += " " + segments[1]["text"]
                    del segments[1]
                else:
                    break

        # Split until min_topics (simple split by sentences)
        while len(segments) < min_topics:
            largest_idx = max(range(len(segments)), key=lambda i: len(segments[i]["text"]))
            text = segments[largest_idx]["text"]
            sentences = sent_tokenize(text)
            if len(sentences) < 2:
                break # Cannot split further
            
            mid = len(sentences) // 2
            segments[largest_idx]["text"] = " ".join(sentences[:mid])
            segments.insert(largest_idx + 1, {"text": " ".join(sentences[mid:])})

        return segments

    def extract_keywords(self, text, top_n=5):
        try:
            vectorizer = CountVectorizer(stop_words='english', ngram_range=(1, 2))
            dtm = vectorizer.fit_transform([text])
            vocab = vectorizer.get_feature_names_out()
            freqs = dtm.toarray()[0]
            sorted_indices = np.argsort(freqs)[::-1][:top_n]
            return [vocab[i] for i in sorted_indices]
        except:
            return []

    def summarize(self, text, num_sentences=2):
        sentences = sent_tokenize(text)
        return " ".join(sentences[:num_sentences])

if __name__ == "__main__":
    pass
