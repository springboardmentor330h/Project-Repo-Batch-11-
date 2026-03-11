"""
Algorithm 2: Classical NLP Approach - TextTiling
Based on lexical cohesion for topic segmentation

TextTiling Concept:
- Same Topic: Consistent vocabulary and repeated terms create cohesive blocks
- Topic Change: Vocabulary shift signals semantic boundary between segments

Reference: Hearst, M. A. (1997). TextTiling: Segmenting text into multi-paragraph subtopic passages.
"""

import json
import os
import numpy as np
from typing import List, Dict, Tuple
from collections import Counter
import re
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for batch processing
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# Try to import NLTK for better tokenization
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    NLTK_AVAILABLE = True
    
    # Download required data
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords', quiet=True)
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
        
except ImportError:
    NLTK_AVAILABLE = False
    print("Warning: NLTK not available. Using basic tokenization.")

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    print("Warning: TextBlob not available. Sentiment analysis will be disabled.")


class TextTilingSegmenter:
    """
    TextTiling algorithm for topic segmentation based on lexical cohesion.
    
    Core idea:
    - Analyzes vocabulary distribution across text blocks
    - High similarity = same topic (lexical cohesion)
    - Low similarity = topic boundary (lexical shift)
    """
    
    def __init__(self, block_size: int = 10, smoothing_width: int = 2):
        """
        Initialize TextTiling segmenter.
        
        Args:
            block_size: Number of sentences per block for comparison (default: 10)
            smoothing_width: Width for smoothing similarity scores (default: 2)
        """
        self.block_size = block_size
        self.smoothing_width = smoothing_width
        
        # Initialize stopwords
        if NLTK_AVAILABLE:
            try:
                self.stopwords = set(stopwords.words('english'))
            except:
                self.stopwords = self._get_basic_stopwords()
        else:
            self.stopwords = self._get_basic_stopwords()
    
    def _get_basic_stopwords(self) -> set:
        """Get basic English stopwords if NLTK is not available."""
        return {
            'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you',
            'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself',
            'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them',
            'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this',
            'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing',
            'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
            'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between',
            'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to',
            'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again',
            'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how',
            'all', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such',
            'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
            's', 't', 'can', 'will', 'just', 'don', 'should', 'now'
        }
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize and clean text.
        
        Args:
            text: Input text
            
        Returns:
            List of cleaned tokens
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        
        # Tokenize
        if NLTK_AVAILABLE:
            tokens = word_tokenize(text)
        else:
            tokens = text.split()
        
        # Remove stopwords and short words
        tokens = [
            token for token in tokens 
            if token not in self.stopwords and len(token) > 2
        ]
        
        return tokens
    
    def create_vocabulary_blocks(
        self, 
        sentences: List[Dict]
    ) -> List[Counter]:
        """
        Create vocabulary blocks from sentences.
        
        Each block contains word frequencies for a group of sentences.
        
        Args:
            sentences: List of sentence dictionaries
            
        Returns:
            List of Counter objects (vocabulary for each block)
        """
        blocks = []
        
        for i in range(0, len(sentences), self.block_size):
            # Get block of sentences
            block_sentences = sentences[i:i + self.block_size]
            
            # Combine text from all sentences in block
            block_text = ' '.join([s.get('text', '') for s in block_sentences])
            
            # Tokenize and count words
            tokens = self.tokenize(block_text)
            word_counts = Counter(tokens)
            
            blocks.append(word_counts)
        
        return blocks
    
    def calculate_lexical_cohesion(
        self, 
        block1: Counter, 
        block2: Counter
    ) -> float:
        """
        Calculate lexical cohesion (similarity) between two vocabulary blocks.
        
        Uses cosine similarity of word frequency vectors.
        
        Args:
            block1: First vocabulary block
            block2: Second vocabulary block
            
        Returns:
            Cohesion score (0 to 1, higher = more similar)
        """
        # Get all unique words from both blocks
        all_words = set(block1.keys()) | set(block2.keys())
        
        if not all_words:
            return 0.0
        
        # Create vectors
        vec1 = np.array([block1.get(word, 0) for word in all_words])
        vec2 = np.array([block2.get(word, 0) for word in all_words])
        
        # Calculate cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        
        return similarity
    
    def compute_cohesion_scores(
        self, 
        blocks: List[Counter]
    ) -> np.ndarray:
        """
        Compute cohesion scores between consecutive blocks.
        
        Args:
            blocks: List of vocabulary blocks
            
        Returns:
            Array of cohesion scores
        """
        scores = []
        
        for i in range(len(blocks) - 1):
            cohesion = self.calculate_lexical_cohesion(blocks[i], blocks[i + 1])
            scores.append(cohesion)
        
        return np.array(scores)
    
    def smooth_scores(self, scores: np.ndarray) -> np.ndarray:
        """
        Smooth cohesion scores to reduce noise.
        
        Args:
            scores: Raw cohesion scores
            
        Returns:
            Smoothed scores
        """
        if len(scores) < 3:
            return scores
        
        # Simple moving average
        smoothed = np.copy(scores)
        width = self.smoothing_width
        
        for i in range(width, len(scores) - width):
            smoothed[i] = np.mean(scores[i - width:i + width + 1])
        
        return smoothed
    
    def detect_boundaries(
        self, 
        cohesion_scores: np.ndarray,
        threshold: float = None,
        min_distance: int = 2
    ) -> List[int]:
        """
        Detect topic boundaries from cohesion scores.
        
        Low cohesion = vocabulary shift = topic boundary
        
        Args:
            cohesion_scores: Array of cohesion scores
            threshold: Manual threshold (if None, uses automatic detection)
            min_distance: Minimum blocks between boundaries
            
        Returns:
            List of boundary block indices
        """
        # Invert cohesion scores (low cohesion = high boundary signal)
        boundary_signal = 1 - cohesion_scores
        
        if threshold is not None:
            # Manual threshold
            boundaries = np.where(cohesion_scores < threshold)[0]
            boundaries = self._filter_close_boundaries(boundaries, min_distance)
        else:
            # Automatic peak detection
            # Find peaks in the boundary signal (valleys in cohesion)
            mean_signal = np.mean(boundary_signal)
            std_signal = np.std(boundary_signal)
            
            # Adaptive threshold
            height = mean_signal + 0.5 * std_signal
            
            peaks, _ = find_peaks(
                boundary_signal,
                height=height,
                distance=min_distance
            )
            boundaries = peaks
        
        return boundaries.tolist()
    
    def _filter_close_boundaries(
        self, 
        boundaries: np.ndarray, 
        min_distance: int
    ) -> np.ndarray:
        """Filter out boundaries that are too close together."""
        if len(boundaries) == 0:
            return boundaries
        
        filtered = [boundaries[0]]
        for b in boundaries[1:]:
            if b - filtered[-1] >= min_distance:
                filtered.append(b)
        
        return np.array(filtered)
    
    def segment_transcript(
        self,
        sentences: List[Dict],
        threshold: float = None,
        min_distance: int = 2
    ) -> Tuple[List[List[Dict]], List[Counter], np.ndarray]:
        """
        Complete TextTiling segmentation pipeline.
        
        Args:
            sentences: List of sentence dictionaries
            threshold: Cohesion threshold for boundaries (None for automatic)
            min_distance: Minimum blocks between boundaries
            
        Returns:
            Tuple of (segments, blocks, cohesion_scores)
        """
        print(f"Processing {len(sentences)} sentences...")
        print(f"Block size: {self.block_size} sentences per block")
        
        # Step 1: Create vocabulary blocks
        print("\nStep 1: Creating vocabulary blocks...")
        blocks = self.create_vocabulary_blocks(sentences)
        print(f"Created {len(blocks)} blocks")
        
        # Step 2: Calculate lexical cohesion
        print("\nStep 2: Calculating lexical cohesion scores...")
        cohesion_scores = self.compute_cohesion_scores(blocks)
        print(f"Computed {len(cohesion_scores)} cohesion scores")
        
        # Step 3: Smooth scores
        print("\nStep 3: Smoothing scores...")
        smoothed_scores = self.smooth_scores(cohesion_scores)
        
        # Step 4: Detect boundaries
        print("\nStep 4: Detecting topic boundaries...")
        boundary_blocks = self.detect_boundaries(
            smoothed_scores,
            threshold=threshold,
            min_distance=min_distance
        )
        
        print(f"Found {len(boundary_blocks) + 1} topics")
        print(f"Boundary blocks: {boundary_blocks}")
        
        # Step 5: Create segments from boundaries
        segments = self._create_segments_from_blocks(
            sentences, 
            boundary_blocks
        )
        
        return segments, blocks, smoothed_scores
    
    def _create_segments_from_blocks(
        self,
        sentences: List[Dict],
        boundary_blocks: List[int]
    ) -> List[List[Dict]]:
        """
        Create sentence segments from block boundaries.
        
        Args:
            sentences: List of all sentences
            boundary_blocks: Block indices where boundaries occur
            
        Returns:
            List of sentence segments
        """
        segments = []
        start_sentence = 0
        
        for block_idx in boundary_blocks:
            # Convert block index to sentence index
            end_sentence = (block_idx + 1) * self.block_size
            end_sentence = min(end_sentence, len(sentences))
            
            segment = sentences[start_sentence:end_sentence]
            if segment:
                segments.append(segment)
            
            start_sentence = end_sentence
        
        # Add final segment
        if start_sentence < len(sentences):
            segments.append(sentences[start_sentence:])
        
        return segments
    
    def visualize_segmentation(
        self,
        cohesion_scores: np.ndarray,
        boundaries: List[int],
        save_path: str = None
    ):
        """
        Visualize cohesion scores and detected boundaries.
        
        Args:
            cohesion_scores: Array of cohesion scores
            boundaries: List of boundary block indices
            save_path: Path to save the plot
        """
        plt.figure(figsize=(12, 6))
        
        # Plot cohesion scores
        plt.plot(cohesion_scores, label='Lexical Cohesion', linewidth=2, color='blue')
        
        # Plot inverted (boundary signal)
        boundary_signal = 1 - cohesion_scores
        plt.plot(boundary_signal, label='Boundary Signal', linewidth=2, 
                color='orange', alpha=0.7, linestyle='--')
        
        # Mark boundaries
        for boundary in boundaries:
            plt.axvline(
                x=boundary, 
                color='r', 
                linestyle='--', 
                alpha=0.7,
                label='Topic Boundary' if boundary == boundaries[0] else ''
            )
        
        plt.xlabel('Block Index')
        plt.ylabel('Score')
        plt.title('TextTiling Topic Segmentation\n(Low cohesion = Topic boundary)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Visualization saved to: {save_path}")
        
        plt.close()


    def get_topic_label(self, text: str) -> str:
        """Generate a semantic label for the topic based on keywords."""
        if not text:
            return "Unknown Topic"
            
        # 1. Extract potential keywords (nouns/proper nouns if possible)
        # Simple frequency-based approach for zero-dependency
        tokens = self.tokenize(text)
        if not tokens:
            return "General Discussion"
            
        # Filter for longer words which are usually more descriptive
        long_tokens = [t for t in tokens if len(t) > 4]
        if not long_tokens:
            long_tokens = tokens
            
        counter = Counter(long_tokens)
        top_words = [word.capitalize() for word, _ in counter.most_common(3)]
        
        if top_words:
            return " & ".join(top_words)
        return "General Topic"

    def analyze_sentiment(self, text: str) -> float:
        """Calculate sentiment polarity (-1 to 1)."""
        if not TEXTBLOB_AVAILABLE or not text:
            return 0.0
        try:
            return TextBlob(text).sentiment.polarity
        except:
            return 0.0


def process_transcript_file(
    input_path: str,
    output_path: str,
    block_size: int = 10,
    smoothing_width: int = 2,
    threshold: float = None,
    min_distance: int = 2,
    visualize: bool = True
):
    """
    Process a single transcript file with TextTiling segmentation.
    
    Args:
        input_path: Path to cleaned transcript JSON
        output_path: Path to save segmented output
        block_size: Sentences per block
        smoothing_width: Smoothing parameter
        threshold: Cohesion threshold (None for automatic)
        min_distance: Minimum blocks between boundaries
        visualize: Whether to create visualization
    """
    print(f"\nProcessing: {input_path}")
    
    # Load transcript
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    sentences = data.get('sentences', [])
    if not sentences:
        print("No sentences found!")
        return
    
    # Initialize segmenter
    segmenter = TextTilingSegmenter(
        block_size=block_size,
        smoothing_width=smoothing_width
    )
    
    # Perform segmentation
    segments, blocks, cohesion_scores = segmenter.segment_transcript(
        sentences,
        threshold=threshold,
        min_distance=min_distance
    )
    
    # Prepare output
    output_data = {
        'metadata': data.get('metadata', {}),
        'total_duration': data.get('total_duration'),
        'merged': data.get('merged'),
        'segmentation_method': 'texttiling',
        'parameters': {
            'block_size': block_size,
            'smoothing_width': smoothing_width,
            'threshold': threshold if threshold else 'automatic'
        },
        'num_topics': len(segments),
        'topics': []
    }
    
    # Add segments as topics
    for i, segment in enumerate(segments):
        topic = {
            'topic_id': i + 1,
            'num_sentences': len(segment),
            'start_time': segment[0]['start'] if segment else 0,
            'end_time': segment[-1]['end'] if segment else 0,
            'duration': (segment[-1]['end'] - segment[0]['start']) if segment else 0,
            'sentences': segment
        }
        
        # Add Semantic Label and Sentiment
        full_text = " ".join([s.get('text', '') for s in segment])
        topic['label'] = segmenter.get_topic_label(full_text)
        topic['sentiment_score'] = segmenter.analyze_sentiment(full_text)
        
        output_data['topics'].append(topic)
    
    # Create output directories
    base_dir = os.path.dirname(os.path.dirname(output_path))
    filename = os.path.basename(output_path)
    
    segments_dir = os.path.join(base_dir, 'topics2', 'segments')
    viz_dir = os.path.join(base_dir, 'topics2', 'visualizations')
    
    os.makedirs(segments_dir, exist_ok=True)
    os.makedirs(viz_dir, exist_ok=True)
    
    # Save segment
    segment_path = os.path.join(segments_dir, filename)
    with open(segment_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nSegmented transcript saved to: {segment_path}")
    
    # Visualize
    if visualize:
        viz_filename = filename.replace('.json', '_visualization.png')
        viz_path = os.path.join(viz_dir, viz_filename)
        
        # Get boundary blocks
        boundary_blocks = []
        cumulative_sentences = 0
        for topic in output_data['topics'][:-1]:
            cumulative_sentences += topic['num_sentences']
            boundary_blocks.append(cumulative_sentences // block_size)
        
        segmenter.visualize_segmentation(cohesion_scores, boundary_blocks, viz_path)
    
    return output_data


def batch_process_transcripts(
    input_dir: str,
    output_base_dir: str,
    block_size: int = 10,
    smoothing_width: int = 2,
    threshold: float = None,
    min_distance: int = 2,
    visualize: bool = True
):
    """
    Batch process multiple transcript files.
    
    Args:
        input_dir: Directory with cleaned transcripts
        output_base_dir: Base directory for topics2
        block_size: Sentences per block
        smoothing_width: Smoothing parameter
        threshold: Cohesion threshold
        min_distance: Minimum blocks between boundaries
        visualize: Create visualizations (default: True)
    """
    json_files = [f for f in os.listdir(input_dir) if f.endswith('.json')]
    
    print(f"Found {len(json_files)} transcript files")
    print(f"Output structure:")
    print(f"  Segments: {output_base_dir}/segments/")
    if visualize:
        print(f"  Visualizations: {output_base_dir}/visualizations/")
    else:
        print(f"  Visualizations: DISABLED")
    
    for i, filename in enumerate(json_files, 1):
        print(f"\n{'='*60}")
        print(f"Processing file {i}/{len(json_files)}: {filename}")
        print(f"{'='*60}")
        
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_base_dir, 'segments', filename)
        
        try:
            process_transcript_file(
                input_path,
                output_path,
                block_size=block_size,
                smoothing_width=smoothing_width,
                threshold=threshold,
                min_distance=min_distance,
                visualize=visualize
            )
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            continue
    
    print(f"\n{'='*60}")
    print(f"Batch processing complete!")
    print(f"Segments saved to: {output_base_dir}/segments/")
    if visualize:
        print(f"Visualizations saved to: {output_base_dir}/visualizations/")


if __name__ == "__main__":
    # Configuration
    INPUT_DIR = "output/transcripts_cleaned"
    OUTPUT_BASE_DIR = "output/topics2"
    
    # TextTiling parameters:
    # block_size: Number of sentences per vocabulary block (default: 10)
    # smoothing_width: Smoothing parameter (default: 2)
    # threshold: Cohesion threshold (None for automatic)
    # min_distance: Minimum blocks between boundaries (default: 2)
    # visualize: Create plots? True=helpful for tuning, False=faster processing
    
    # Option 1: With visualizations (recommended for first use)
    batch_process_transcripts(
        input_dir=INPUT_DIR,
        output_base_dir=OUTPUT_BASE_DIR,
        block_size=10,
        smoothing_width=2,
        threshold=None,  # Automatic
        min_distance=2,
        visualize=True  # Create visualization plots
    )
    
    # Option 2: Without visualizations (faster, for production)
    # batch_process_transcripts(
    #     input_dir=INPUT_DIR,
    #     output_base_dir=OUTPUT_BASE_DIR,
    #     block_size=10,
    #     smoothing_width=2,
    #     threshold=None,
    #     min_distance=2,
    #     visualize=False  # Skip visualizations - faster!
    # )
    
    # Option 3: Custom parameters with manual threshold
    # batch_process_transcripts(
    #     input_dir=INPUT_DIR,
    #     output_base_dir=OUTPUT_BASE_DIR,
    #     block_size=15,  # Larger blocks
    #     smoothing_width=3,  # More smoothing
    #     threshold=0.3,  # Manual threshold
    #     min_distance=3,
    #     visualize=True
    # )
    
    # Single file example:
    # process_transcript_file(
    #     input_path="output/transcripts_cleaned/audio_001.json",
    #     output_path="output/topics2/segments/audio_001.json",
    #     block_size=10,
    #     visualize=True  # or False
    # )