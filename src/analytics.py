"""
Advanced Analytics Module
Provides detailed analytics and insights about transcribed content
"""

import numpy as np
from collections import Counter
from typing import Dict, List, Tuple
import re


class TranscriptAnalytics:
    """
    Advanced analytics for transcribed audio
    """
    
    def __init__(self):
        """Initialize analytics calculator"""
        pass
    
    def calculate_all_metrics(
        self, 
        transcript_data: Dict,
        topics_data: Dict
    ) -> Dict:
        """
        Calculate all analytics metrics
        
        Args:
            transcript_data: Cleaned transcript data
            topics_data: Topic segmentation data
            
        Returns:
            Dictionary with all metrics
        """
        sentences = transcript_data.get('sentences', [])
        topics = topics_data.get('topics', [])
        
        # Get full text
        full_text = " ".join([s['text'] for s in sentences])
        
        # Calculate all metrics
        metrics = {
            'basic': self.calculate_basic_metrics(sentences, full_text),
            'vocabulary': self.calculate_vocabulary_metrics(full_text),
            'speaking': self.calculate_speaking_metrics(sentences),
            'readability': self.calculate_readability_metrics(full_text),
            'topics': self.calculate_topic_metrics(topics),
            'sentiment': self.calculate_sentiment_timeline(sentences)
        }
        
        return metrics
    
    def calculate_basic_metrics(
        self, 
        sentences: List[Dict], 
        full_text: str
    ) -> Dict:
        """Calculate basic text metrics"""
        # Calculate duration
        if sentences:
            total_duration = sentences[-1]['end'] - sentences[0]['start']
        else:
            total_duration = 0
        
        # Word and sentence counts
        words = full_text.split()
        
        return {
            'total_words': len(words),
            'total_sentences': len(sentences),
            'total_characters': len(full_text),
            'duration_seconds': total_duration,
            'duration_minutes': total_duration / 60,
            'avg_words_per_sentence': len(words) / len(sentences) if sentences else 0
        }
    
    def calculate_vocabulary_metrics(self, text: str) -> Dict:
        """Calculate vocabulary diversity metrics"""
        # Tokenize
        words = text.lower().split()
        words = [re.sub(r'[^a-z]', '', w) for w in words if w]
        
        # Calculate metrics
        unique_words = set(words)
        word_freq = Counter(words)
        
        return {
            'unique_words': len(unique_words),
            'total_words': len(words),
            'vocabulary_diversity': len(unique_words) / len(words) if words else 0,
            'top_10_words': word_freq.most_common(10),
            'hapax_legomena': sum(1 for count in word_freq.values() if count == 1)
        }
    
    def calculate_speaking_metrics(self, sentences: List[Dict]) -> Dict:
        """Calculate speaking rate and patterns"""
        if not sentences:
            return {}
        
        # Words per minute calculation
        total_duration = sentences[-1]['end'] - sentences[0]['start']
        total_words = sum(len(s['text'].split()) for s in sentences)
        
        wpm = (total_words / total_duration) * 60 if total_duration > 0 else 0
        
        # Sentence durations
        sentence_durations = [s['end'] - s['start'] for s in sentences]
        
        # Pauses between sentences
        pauses = []
        for i in range(len(sentences) - 1):
            pause = sentences[i+1]['start'] - sentences[i]['end']
            if pause > 0:
                pauses.append(pause)
        
        return {
            'words_per_minute': round(wpm, 1),
            'avg_sentence_duration': np.mean(sentence_durations) if sentence_durations else 0,
            'median_sentence_duration': np.median(sentence_durations) if sentence_durations else 0,
            'avg_pause_duration': np.mean(pauses) if pauses else 0,
            'total_pause_time': sum(pauses) if pauses else 0,
            'speech_rate_category': self._categorize_wpm(wpm)
        }
    
    def _categorize_wpm(self, wpm: float) -> str:
        """Categorize speaking rate"""
        if wpm < 100:
            return "Very Slow"
        elif wpm < 130:
            return "Slow"
        elif wpm < 160:
            return "Normal"
        elif wpm < 190:
            return "Fast"
        else:
            return "Very Fast"
    
    def calculate_readability_metrics(self, text: str) -> Dict:
        """Calculate readability scores"""
        try:
            import textstat
            
            return {
                'flesch_reading_ease': textstat.flesch_reading_ease(text),
                'flesch_kincaid_grade': textstat.flesch_kincaid_grade(text),
                'gunning_fog': textstat.gunning_fog(text),
                'automated_readability_index': textstat.automated_readability_index(text),
                'coleman_liau_index': textstat.coleman_liau_index(text),
                'reading_level': self._interpret_grade_level(
                    textstat.flesch_kincaid_grade(text)
                )
            }
        except ImportError:
            return {'error': 'textstat not installed'}
    
    def _interpret_grade_level(self, grade: float) -> str:
        """Interpret Flesch-Kincaid grade level"""
        if grade < 6:
            return "Elementary"
        elif grade < 9:
            return "Middle School"
        elif grade < 13:
            return "High School"
        elif grade < 16:
            return "College"
        else:
            return "Graduate"
    
    def calculate_topic_metrics(self, topics: List[Dict]) -> Dict:
        """Calculate topic-related metrics"""
        if not topics:
            return {}
        
        # Topic durations
        durations = [t['duration'] for t in topics]
        
        # Topic distribution
        topic_distribution = {
            t['label']: t['duration'] for t in topics
        }
        
        return {
            'num_topics': len(topics),
            'avg_topic_duration': np.mean(durations),
            'median_topic_duration': np.median(durations),
            'shortest_topic': min(durations),
            'longest_topic': max(durations),
            'topic_distribution': topic_distribution
        }
    
    def calculate_sentiment_timeline(self, sentences: List[Dict]) -> Dict:
        """Calculate sentiment changes over time"""
        from textblob import TextBlob
        
        timeline = []
        for sent in sentences:
            blob = TextBlob(sent['text'])
            timeline.append({
                'time': (sent['start'] + sent['end']) / 2,
                'polarity': blob.sentiment.polarity,
                'subjectivity': blob.sentiment.subjectivity
            })
        
        # Calculate statistics
        polarities = [t['polarity'] for t in timeline]
        
        return {
            'timeline': timeline,
            'avg_polarity': np.mean(polarities) if polarities else 0,
            'polarity_std': np.std(polarities) if polarities else 0,
            'most_positive_time': max(timeline, key=lambda x: x['polarity'])['time'] if timeline else 0,
            'most_negative_time': min(timeline, key=lambda x: x['polarity'])['time'] if timeline else 0
        }
    
    def generate_word_frequency_data(self, text: str, top_n: int = 20) -> List[Tuple]:
        """
        Generate word frequency data for visualization
        
        Args:
            text: Input text
            top_n: Number of top words to return
            
        Returns:
            List of (word, frequency) tuples
        """
        # Tokenize and clean
        words = text.lower().split()
        words = [re.sub(r'[^a-z]', '', w) for w in words if w]
        
        # Remove common stopwords
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 
                    'to', 'for', 'of', 'with', 'is', 'was', 'are', 'were',
                    'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did',
                    'i', 'you', 'he', 'she', 'it', 'we', 'they', 'this', 'that'}
        
        words = [w for w in words if w not in stopwords and len(w) > 2]
        
        # Count frequencies
        word_freq = Counter(words)
        
        return word_freq.most_common(top_n)
    
    def calculate_speaker_metrics(
        self, 
        labeled_segments: List[Dict]
    ) -> Dict:
        """
        Calculate per-speaker metrics (if speaker diarization is available)
        
        Args:
            labeled_segments: Transcript segments with speaker labels
            
        Returns:
            Speaker statistics dictionary
        """
        speaker_stats = {}
        
        for seg in labeled_segments:
            speaker = seg.get('speaker', 'Unknown')
            duration = seg['end'] - seg['start']
            words = seg['text'].split()
            
            if speaker not in speaker_stats:
                speaker_stats[speaker] = {
                    'total_time': 0,
                    'total_words': 0,
                    'num_turns': 0,
                    'avg_words_per_turn': 0,
                    'wpm': 0
                }
            
            speaker_stats[speaker]['total_time'] += duration
            speaker_stats[speaker]['total_words'] += len(words)
            speaker_stats[speaker]['num_turns'] += 1
        
        # Calculate derived metrics
        for speaker in speaker_stats:
            stats = speaker_stats[speaker]
            stats['avg_words_per_turn'] = stats['total_words'] / stats['num_turns']
            stats['wpm'] = (stats['total_words'] / stats['total_time']) * 60
            stats['time_minutes'] = stats['total_time'] / 60
        
        return speaker_stats


# Convenience function
def analyze_transcript(
    transcript_data: Dict,
    topics_data: Dict
) -> Dict:
    """
    Quick function to analyze transcript
    
    Args:
        transcript_data: Cleaned transcript
        topics_data: Topic segmentation results
        
    Returns:
        Complete analytics dictionary
    """
    analytics = TranscriptAnalytics()
    return analytics.calculate_all_metrics(transcript_data, topics_data)


if __name__ == "__main__":
    print("Transcript Analytics Module")
    print("Provides comprehensive analytics including:")
    print("  - Speaking rate (WPM)")
    print("  - Vocabulary diversity")
    print("  - Readability scores")
    print("  - Topic distribution")
    print("  - Sentiment timeline")
