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
        # Ensure essential NLTK resources are available
        resources = {
            'tokenizers/punkt': 'punkt',
            'corpora/stopwords': 'stopwords'
        }
        for path, pkg in resources.items():
            try:
                nltk.data.find(path)
            except LookupError:
                nltk.download(pkg, quiet=True)

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

    def enforce_topic_count(self, segments, min_topics=None, max_topics=None, duration=None):
        """
        Ensures the number of segments falls within a range that adapts to podcast length.
        Target: 11 minutes (660s) -> 10 topics (~1 topic per 66s).
        """
        if not segments:
            return []

        # Calculate limits based on duration if provided, else word count
        if min_topics is None or max_topics is None:
            if duration:
                # 660s / 66 = 10 topics
                calculated_max = max(2, int(duration // 66))
                calculated_min = max(1, calculated_max - 1)
            else:
                word_count = len(" ".join([s["text"] for s in segments]).split())
                calculated_max = max(3, word_count // 150) # High density
                calculated_min = max(2, calculated_max // 2)
            
            min_topics = min_topics or calculated_min
            max_topics = max_topics or calculated_max

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

    def generate_title(self, text, keywords):
        """
        Generates a clear, human-readable, and semantically representative title.
        Adapts to the content by selecting the most significant keywords.
        """
        if not keywords:
            sentences = sent_tokenize(text)
            if not sentences:
                return "General Discussion"
            # Extract first meaningful phrase
            words = [w for w in sentences[0].split() if len(w) > 3][:4]
            return " ".join(words).capitalize() + "..."
        
        # Select top 3 keywords, filter out very short ones
        top_k = [k.strip().title() for k in keywords if len(k) > 2][:3]
        
        if len(top_k) >= 2:
            return f"{', '.join(top_k[:-1])} & {top_k[-1]}"
        elif top_k:
            return top_k[0]
        return "Insight Segment"

    def summarize(self, text, num_sentences=2):
        sentences = sent_tokenize(text)
        return " ".join(sentences[:num_sentences])

if __name__ == "__main__":
    INPUT_DIR = "data/final_transcripts"
    OUTPUT_DIR = "data/topics"
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    segmenter = TopicSegmenter()

    for file in os.listdir(INPUT_DIR):
        if not file.endswith("_merged.json"):
            continue

        with open(os.path.join(INPUT_DIR, file), "r", encoding="utf-8") as f:
            data = json.load(f)

        segments = data["segments"]
        # Convert segments to a single text for segmentation logic
        full_text = " ".join([s["text"] for s in segments])
        
        # We use similarity segmentation as a default for the standalone script
        raw_topics = segmenter.segment_with_similarity(full_text)
        final_topics = segmenter.enforce_topic_count(raw_topics)

        output = {
            "episode": data.get("episode", file.replace("_merged.json", "")),
            "num_topics": len(final_topics),
            "topics": []
        }

        # Standalone script usually doesn't have accurate timestamps without complex mapping
        # but we can try to estimate or just provide keywords/summaries
        for idx, topic in enumerate(final_topics, 1):
            topic_text = topic["text"]
            keywords = segmenter.extract_keywords(topic_text)
            output["topics"].append({
                "topic_id": idx,
                "title": segmenter.generate_title(topic_text, keywords),
                "summary": segmenter.summarize(topic_text),
                "keywords": keywords,
                "text": topic_text
            })

        out_path = os.path.join(
            OUTPUT_DIR,
            file.replace("_merged.json", "_topics.json")
        )

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)

        print(f"✅ Topic segmentation completed: {out_path}")

    print("🎉 All episodes segmented successfully")
