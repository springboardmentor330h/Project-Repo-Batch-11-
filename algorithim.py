import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class TopicSegmenter:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """Initialize the sentence transformer model"""
        print(f"Loading model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        print("Model loaded successfully!")
    
    def load_transcript(self, json_path):
        """Load a cleaned transcript JSON file"""
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def extract_sentences(self, transcript_data):
        """Extract sentences from transcript JSON"""
        sentences = []
        for sentence in transcript_data.get('sentences', []):
            text = sentence.get('text', '').strip()
            if text:
                sentences.append({
                    'text': text,
                    'sentence_id': sentence.get('sentence_id'),
                    'start': sentence.get('start'),
                    'end': sentence.get('end')
                })
        return sentences
    
    def calculate_similarity_scores(self, sentences):
        """Calculate cosine similarity between adjacent sentences"""
        if len(sentences) < 2:
            return []
        
        # Get sentence texts
        texts = [s['text'] for s in sentences]
        
        # Generate embeddings
        print(f"Generating embeddings for {len(texts)} sentences...")
        embeddings = self.model.encode(texts)
        
        # Calculate similarity between adjacent sentences
        similarities = []
        for i in range(len(embeddings) - 1):
            sim = cosine_similarity(
                embeddings[i].reshape(1, -1),
                embeddings[i + 1].reshape(1, -1)
            )[0][0]
            similarities.append(sim)
        
        return similarities
    
    def detect_topic_boundaries(self, similarities, threshold=0.5):
        """Detect topic boundaries where similarity drops below threshold"""
        boundaries = []
        for i, sim in enumerate(similarities):
            if sim < threshold:
                boundaries.append(i + 1)  # Boundary after sentence i
        return boundaries
    
    def segment_into_topics(self, sentences, boundaries):
        """Segment sentences into topics based on boundaries"""
        topics = []
        start_idx = 0
        
        for boundary in boundaries:
            topic_sentences = sentences[start_idx:boundary]
            if topic_sentences:
                topics.append(topic_sentences)
            start_idx = boundary
        
        # Add remaining sentences as last topic
        if start_idx < len(sentences):
            topics.append(sentences[start_idx:])
        
        return topics
    
    def process_transcript(self, json_path, threshold=0.5):
        """Process a single transcript file"""
        print(f"\nProcessing: {os.path.basename(json_path)}")
        
        # Load transcript
        transcript_data = self.load_transcript(json_path)
        
        # Extract sentences
        sentences = self.extract_sentences(transcript_data)
        print(f"Found {len(sentences)} sentences")
        
        if len(sentences) < 2:
            print("Not enough sentences for topic segmentation")
            return None
        
        # Calculate similarities
        similarities = self.calculate_similarity_scores(sentences)
        
        # Detect boundaries
        boundaries = self.detect_topic_boundaries(similarities, threshold)
        print(f"Detected {len(boundaries)} topic boundaries")
        
        # Segment into topics
        topics = self.segment_into_topics(sentences, boundaries)
        print(f"Created {len(topics)} topics")
        
        return {
            'metadata': transcript_data.get('metadata', {}),
            'topics': topics,
            'similarities': similarities,
            'boundaries': boundaries
        }
    
    def save_topics(self, result, output_path):
        """Save segmented topics to JSON file"""
        output_data = {
            'metadata': result['metadata'],
            'num_topics': len(result['topics']),
            'boundaries': result['boundaries'],
            'topics': []
        }
        
        for i, topic in enumerate(result['topics']):
            topic_data = {
                'topic_id': i + 1,
                'num_sentences': len(topic),
                'start_time': topic[0]['start'] if topic else None,
                'end_time': topic[-1]['end'] if topic else None,
                'sentences': topic
            }
            output_data['topics'].append(topic_data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"Saved to: {output_path}")

def main():
    # Initialize segmenter
    segmenter = TopicSegmenter()
    
    # Paths
    input_dir = 'output/transcripts_cleaned'
    output_dir = 'output/topics'
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Process all cleaned transcript files
    json_files = [f for f in os.listdir(input_dir) if f.endswith('.json')]
    
    print(f"\nFound {len(json_files)} files to process")
    
    for json_file in json_files:
        input_path = os.path.join(input_dir, json_file)
        output_filename = json_file.replace('_cleaned.json', '_topics.json')
        output_path = os.path.join(output_dir, output_filename)
        
        try:
            # Process transcript
            result = segmenter.process_transcript(input_path, threshold=0.5)
            
            if result:
                # Save topics
                segmenter.save_topics(result, output_path)
        
        except Exception as e:
            print(f"Error processing {json_file}: {str(e)}")
            continue
    
    print("\n Topic segmentation complete!")

if __name__ == "__main__":
    main()