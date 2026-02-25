"""
Algorithm 3: Modern Embedding-Based Topic Segmentation
Uses semantic embeddings to detect topic boundaries in transcripts
"""

import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple
from scipy.signal import find_peaks


class EmbeddingBasedSegmenter:
    """
    Modern topic segmentation using semantic embeddings.
    
    Steps:
    1. Convert sentences to embeddings (dense vector representations)
    2. Measure similarity between consecutive embeddings
    3. Detect boundaries where similarity drops sharply
    """
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize the segmenter with a pre-trained embedding model.
        
        Args:
            model_name: Name of the sentence-transformers model to use
                       'all-MiniLM-L6-v2' - Fast, good quality (default)
                       'all-mpnet-base-v2' - Higher quality, slower
                       'paraphrase-multilingual-MiniLM-L12-v2' - Multilingual
        """
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        print("Model loaded successfully!")
    
    def convert_to_embeddings(self, sentences: List[str]) -> np.ndarray:
        """
        Step 1: Transform text chunks into dense vector representations.
        
        Args:
            sentences: List of sentence texts
            
        Returns:
            Array of embeddings (shape: [n_sentences, embedding_dim])
        """
        print(f"Converting {len(sentences)} sentences to embeddings...")
        embeddings = self.model.encode(sentences, show_progress_bar=True)
        print(f"Embeddings shape: {embeddings.shape}")
        return embeddings
    
    def measure_similarity(self, embeddings: np.ndarray) -> np.ndarray:
        """
        Step 2: Calculate cosine similarity between consecutive embedding vectors.
        
        Args:
            embeddings: Array of sentence embeddings
            
        Returns:
            Array of similarity scores between consecutive sentences
        """
        similarities = []
        
        for i in range(len(embeddings) - 1):
            # Cosine similarity between consecutive embeddings
            sim = cosine_similarity(
                embeddings[i].reshape(1, -1),
                embeddings[i + 1].reshape(1, -1)
            )[0][0]
            similarities.append(sim)
        
        return np.array(similarities)
    
    def detect_boundaries(
        self, 
        similarities: np.ndarray,
        threshold: float = None,
        min_distance: int = 5,
        prominence: float = 0.1
    ) -> List[int]:
        """
        Step 3: Detect topic boundaries where similarity drops sharply.
        
        Args:
            similarities: Array of similarity scores
            threshold: Manual threshold (if None, uses automatic detection)
            min_distance: Minimum sentences between boundaries
            prominence: How prominent peaks must be (for automatic detection)
            
        Returns:
            List of boundary indices (sentence positions)
        """
        # Invert similarities to find "peaks" in dissimilarity
        dissimilarities = 1 - similarities
        
        if threshold is not None:
            # Manual threshold method
            boundaries = np.where(similarities < threshold)[0]
            boundaries = self._filter_close_boundaries(boundaries, min_distance)
        else:
            # Automatic peak detection method
            peaks, properties = find_peaks(
                dissimilarities,
                distance=min_distance,
                prominence=prominence
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
        min_distance: int = 5,
        prominence: float = 0.1
    ) -> Tuple[List[List[Dict]], np.ndarray, np.ndarray]:
        """
        Complete segmentation pipeline.
        
        Args:
            sentences: List of sentence dictionaries from cleaned transcript
            threshold: Similarity threshold for boundary detection
            min_distance: Minimum sentences between boundaries
            prominence: Peak prominence for automatic detection
            
        Returns:
            Tuple of (segments, embeddings, similarities)
        """
        # Extract sentence texts
        texts = [s['text'] for s in sentences]
        
        # Step 1: Convert to embeddings
        embeddings = self.convert_to_embeddings(texts)
        
        # Step 2: Measure similarity
        similarities = self.measure_similarity(embeddings)
        
        # Step 3: Detect boundaries
        boundaries = self.detect_boundaries(
            similarities, 
            threshold=threshold,
            min_distance=min_distance,
            prominence=prominence
        )
        
        # Create segments
        segments = self._create_segments(sentences, boundaries)
        
        print(f"\nFound {len(segments)} topics/segments")
        print(f"Boundary positions: {boundaries}")
        
        return segments, embeddings, similarities
    
    def _create_segments(
        self, 
        sentences: List[Dict], 
        boundaries: List[int]
    ) -> List[List[Dict]]:
        """Create segments from sentences and boundary positions."""
        segments = []
        start = 0
        
        for boundary in boundaries:
            # Add 1 because boundary is the index where similarity was measured
            # (between sentence i and i+1)
            end = boundary + 1
            segments.append(sentences[start:end])
            start = end
        
        # Add final segment
        if start < len(sentences):
            segments.append(sentences[start:])
        
        return segments
    
    def visualize_segmentation(
        self,
        similarities: np.ndarray,
        boundaries: List[int],
        save_path: str = None
    ):
        """
        Visualize similarity scores and detected boundaries.
        
        Args:
            similarities: Array of similarity scores
            boundaries: List of detected boundary positions
            save_path: Path to save the plot (if None, displays only)
        """
        plt.figure(figsize=(12, 6))
        
        # Plot similarity scores
        plt.plot(similarities, label='Cosine Similarity', linewidth=2)
        
        # Mark boundaries
        for boundary in boundaries:
            plt.axvline(
                x=boundary, 
                color='r', 
                linestyle='--', 
                alpha=0.7,
                label='Topic Boundary' if boundary == boundaries[0] else ''
            )
        
        plt.xlabel('Sentence Index')
        plt.ylabel('Similarity Score')
        plt.title('Embedding-Based Topic Segmentation')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Visualization saved to: {save_path}")
        
        plt.show()


def process_transcript_file(
    input_path: str,
    output_path: str,
    model_name: str = 'all-MiniLM-L6-v2',
    threshold: float = None,
    min_distance: int = 5,
    prominence: float = 0.1,
    visualize: bool = True
):
    """
    Process a single transcript file with embedding-based segmentation.
    
    Args:
        input_path: Path to cleaned transcript JSON file
        output_path: Path to save segmented output
        model_name: Sentence transformer model name
        threshold: Similarity threshold (None for automatic)
        min_distance: Minimum sentences between topics
        prominence: Peak prominence for automatic detection
        visualize: Whether to create visualization
    """
    # Load transcript
    print(f"\nProcessing: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    sentences = data.get('sentences', [])
    if not sentences:
        print("No sentences found in transcript!")
        return
    
    # Initialize segmenter
    segmenter = EmbeddingBasedSegmenter(model_name=model_name)
    
    # Perform segmentation
    segments, embeddings, similarities = segmenter.segment_transcript(
        sentences,
        threshold=threshold,
        min_distance=min_distance,
        prominence=prominence
    )
    
    # Prepare output
    output_data = {
        'metadata': data.get('metadata', {}),
        'total_duration': data.get('total_duration'),
        'merged': data.get('merged'),
        'segmentation_method': 'embedding_based',
        'model_used': model_name,
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
        output_data['topics'].append(topic)
    
    # Save output - create separate directories
    # Extract base directory and filename
    base_dir = os.path.dirname(os.path.dirname(output_path))  # Get parent of output_path dir
    filename = os.path.basename(output_path)
    
    # Create separate directories
    segments_dir = os.path.join(base_dir, 'topics3', 'segments')
    viz_dir = os.path.join(base_dir, 'topics3', 'visualizations')
    
    os.makedirs(segments_dir, exist_ok=True)
    os.makedirs(viz_dir, exist_ok=True)
    
    # Save segment to segments folder
    segment_path = os.path.join(segments_dir, filename)
    with open(segment_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"Segmented transcript saved to: {segment_path}")
    
    # Visualize - save to visualizations folder
    if visualize:
        viz_filename = filename.replace('.json', '_visualization.png')
        viz_path = os.path.join(viz_dir, viz_filename)
        boundaries = []
        cumulative = 0
        for topic in output_data['topics'][:-1]:
            cumulative += topic['num_sentences']
            boundaries.append(cumulative - 1)
        
        segmenter.visualize_segmentation(similarities, boundaries, viz_path)
    
    return output_data


def batch_process_transcripts(
    input_dir: str,
    output_base_dir: str,
    model_name: str = 'all-MiniLM-L6-v2',
    threshold: float = None,
    min_distance: int = 5,
    prominence: float = 0.1,
    visualize: bool = True
):
    """
    Process all transcript files in a directory.
    
    Args:
        input_dir: Directory containing cleaned transcript JSON files
        output_base_dir: Base directory for topics3 (will create segments/ and visualizations/ subdirs)
        model_name: Sentence transformer model name
        threshold: Similarity threshold (None for automatic)
        min_distance: Minimum sentences between topics
        prominence: Peak prominence for automatic detection
        visualize: Whether to create visualization plots (default: True)
    """
    # Get all JSON files
    json_files = [f for f in os.listdir(input_dir) if f.endswith('.json')]
    
    print(f"Found {len(json_files)} transcript files to process")
    print(f"Output structure:")
    print(f"  Segments: {output_base_dir}/segments/")
    if visualize:
        print(f"  Visualizations: {output_base_dir}/visualizations/")
    else:
        print(f"  Visualizations: DISABLED")
    
    # Process each file
    for i, filename in enumerate(json_files, 1):
        print(f"\n{'='*60}")
        print(f"Processing file {i}/{len(json_files)}: {filename}")
        print(f"{'='*60}")
        
        input_path = os.path.join(input_dir, filename)
        # Pass a dummy output path, the function will create proper structure
        output_path = os.path.join(output_base_dir, 'segments', filename)
        
        try:
            process_transcript_file(
                input_path,
                output_path,
                model_name=model_name,
                threshold=threshold,
                min_distance=min_distance,
                prominence=prominence,
                visualize=visualize
            )
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            continue
    
    print(f"\n{'='*60}")
    print(f"Batch processing complete!")
    print(f"Processed {len(json_files)} files")
    print(f"Segments saved to: {output_base_dir}/segments/")
    if visualize:
        print(f"Visualizations saved to: {output_base_dir}/visualizations/")


if __name__ == "__main__":
    # Example usage
    
    # Configuration
    INPUT_DIR = "output/transcripts_cleaned"
    OUTPUT_BASE_DIR = "output/topics3"  # Will create segments/ and visualizations/ inside
    
    # Model options:
    # 'all-MiniLM-L6-v2' - Fast, good quality (384 dimensions)
    # 'all-mpnet-base-v2' - Better quality, slower (768 dimensions)
    # 'paraphrase-multilingual-MiniLM-L12-v2' - Multilingual support
    MODEL_NAME = 'all-MiniLM-L6-v2'
    
    # Segmentation parameters:
    # threshold: Manual similarity threshold (0-1), None for automatic
    # min_distance: Minimum sentences between topic boundaries
    # prominence: How prominent similarity drops must be (for automatic mode)
    # visualize: Create plots? True=helpful for tuning, False=faster processing
    
    # Option 1: With visualizations (recommended for first use)
    batch_process_transcripts(
        input_dir=INPUT_DIR,
        output_base_dir=OUTPUT_BASE_DIR,
        model_name=MODEL_NAME,
        threshold=None,  # Automatic
        min_distance=5,
        prominence=0.1,
        visualize=False # Create visualization plots
    )
    
    # Option 2: Without visualizations (faster, for production)
    # batch_process_transcripts(
    #     input_dir=INPUT_DIR,
    #     output_base_dir=OUTPUT_BASE_DIR,
    #     model_name=MODEL_NAME,
    #     threshold=None,
    #     min_distance=5,
    #     prominence=0.1,
    #     visualize=False  # Skip visualizations - faster!
    # )
    
    # Option 3: Manual threshold
    # batch_process_transcripts(
    #     input_dir=INPUT_DIR,
    #     output_base_dir=OUTPUT_BASE_DIR,
    #     model_name=MODEL_NAME,
    #     threshold=0.7,  # Manual: boundaries where similarity < 0.7
    #     min_distance=5,
    #     visualize=True
    # )
    
    # Process single file example
    # process_transcript_file(
    #     input_path="output/transcripts_cleaned/audio_001.json",
    #     output_path="output/topics3/segments/audio_001.json",
    #     model_name=MODEL_NAME,
    #     visualize=True  # or False
    # )