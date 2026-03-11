"""
Evaluation and Keyword Extraction for Algorithm 2 (TextTiling)

This script:
1. Evaluates segmentation quality (human judgment criteria)
2. Extracts keywords from each segment using TF-IDF (with smart fallback)
3. Generates meaningful extractive summaries using sentence scoring
"""

import json
import os
import re
from collections import Counter
from typing import List, Dict

# ── Optional library imports ──────────────────────────────────────────────────
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("  sklearn not available. Install with: pip install scikit-learn")

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize, sent_tokenize
    NLTK_AVAILABLE = True
    for _pkg, _path in [
        ('stopwords',  'corpora/stopwords'),
        ('punkt',      'tokenizers/punkt'),
        ('punkt_tab',  'tokenizers/punkt_tab'),
    ]:
        try:
            nltk.data.find(_path)
        except LookupError:
            nltk.download(_pkg, quiet=True)
except ImportError:
    NLTK_AVAILABLE = False
    print("  NLTK not available. Install with: pip install nltk")


# ─────────────────────────────────────────────────────────────────────────────
# SEGMENTATION EVALUATOR
# ─────────────────────────────────────────────────────────────────────────────
class SegmentationEvaluator:
    """Evaluate segmentation quality based on human judgment criteria."""

    def evaluate_segmentation(self, data: Dict) -> Dict:
        """
        Evaluate segmentation quality.
        Criteria:
          1. Naturalness  — topic sentence count
          2. Balance      — topic size consistency
          3. Topic count  — reasonable number of segments
        """
        topics = data.get('topics', [])

        evaluation = {
            'total_topics': len(topics),
            'naturalness_score': 0,
            'logical_separation_score': 0,
            'length_appropriateness_score': 0,
            'overall_score': 0,
            'feedback': []
        }

        if not topics:
            evaluation['feedback'].append("⚠️  No topics found")
            return evaluation

        sentences_per_topic = [t.get('num_sentences', 0) for t in topics]
        avg_sentences = sum(sentences_per_topic) / len(sentences_per_topic)

        # 1. Naturalness
        if 5 <= avg_sentences <= 30:
            evaluation['naturalness_score'] = 10
            evaluation['feedback'].append("✓ Natural topic length (5–30 sentences)")
        elif 3 <= avg_sentences <= 50:
            evaluation['naturalness_score'] = 7
            evaluation['feedback'].append("~ Acceptable topic length")
        else:
            evaluation['naturalness_score'] = 4
            evaluation['feedback'].append("⚠️  Topics may be too short or too long")

        # 2. Balance
        if len(topics) > 1:
            variance  = sum((s - avg_sentences) ** 2 for s in sentences_per_topic) / len(sentences_per_topic)
            std       = variance ** 0.5
            cv        = std / avg_sentences if avg_sentences > 0 else 0
            if cv < 0.5:
                evaluation['logical_separation_score'] = 10
                evaluation['feedback'].append("✓ Topics are well-balanced")
            elif cv < 1.0:
                evaluation['logical_separation_score'] = 7
                evaluation['feedback'].append("~ Topics have some variation in size")
            else:
                evaluation['logical_separation_score'] = 4
                evaluation['feedback'].append("⚠️  Topics vary significantly in size")
        else:
            evaluation['logical_separation_score'] = 5
            evaluation['feedback'].append("ℹ️  Only one topic detected")

        # 3. Topic count
        n = len(topics)
        if 3 <= n <= 20:
            evaluation['length_appropriateness_score'] = 10
            evaluation['feedback'].append("✓ Good number of topics")
        elif 1 <= n < 3 or 20 < n <= 50:
            evaluation['length_appropriateness_score'] = 7
            evaluation['feedback'].append("~ Acceptable number of topics")
        else:
            evaluation['length_appropriateness_score'] = 4
            evaluation['feedback'].append(
                "⚠️  Too many topics (over-segmentation)" if n > 50 else "⚠️  Very few topics"
            )

        evaluation['overall_score'] = (
            evaluation['naturalness_score'] +
            evaluation['logical_separation_score'] +
            evaluation['length_appropriateness_score']
        ) / 3

        return evaluation


# ─────────────────────────────────────────────────────────────────────────────
# KEYWORD EXTRACTOR  (improved)
# ─────────────────────────────────────────────────────────────────────────────
class KeywordExtractor:
    """
    Extract meaningful keywords from topic segments.

    Strategy:
    - Multiple segments  → TF-IDF (highlights words unique to each segment)
    - Single segment     → Scored frequency (filters generic filler words,
                           boosts longer / capitalized / repeated terms)
    """

    # Words that are common in podcast speech but carry no topical meaning
    FILLER_WORDS = {
        'um', 'uh', 'like', 'know', 'think', 'gonna', 'want', 'get', 'got',
        'would', 'could', 'said', 'say', 'says', 'saying', 'talk', 'talking',
        'thing', 'things', 'stuff', 'lot', 'lots', 'really', 'actually',
        'basically', 'literally', 'definitely', 'certainly', 'obviously',
        'right', 'okay', 'yeah', 'yep', 'well', 'also', 'even', 'still',
        'back', 'kind', 'sort', 'mean', 'need', 'look', 'looking', 'come',
        'coming', 'going', 'make', 'makes', 'making', 'take', 'taking',
        'something', 'anything', 'everything', 'nothing', 'someone',
        'people', 'person', 'way', 'ways', 'time', 'times', 'day', 'days',
        'year', 'years', 'number', 'numbers', 'little', 'bit', 'good',
        'great', 'big', 'new', 'old', 'first', 'last', 'next', 'much',
        'many', 'long', 'point', 'part', 'place', 'world', 'today', 'week',
    }

    # Core English stopwords (used when NLTK unavailable)
    BASE_STOPWORDS = {
        'i','me','my','myself','we','our','ours','ourselves','you','your',
        'yours','yourself','yourselves','he','him','his','himself','she',
        'her','hers','herself','it','its','itself','they','them','their',
        'theirs','themselves','what','which','who','whom','this','that',
        'these','those','am','is','are','was','were','be','been','being',
        'have','has','had','having','do','does','did','doing','a','an',
        'the','and','but','if','or','because','as','until','while','of',
        'at','by','for','with','about','against','between','into','through',
        'during','before','after','above','below','to','from','up','down',
        'in','out','on','off','over','under','again','further','then',
        'once','here','there','when','where','why','how','all','both',
        'each','few','more','most','other','some','such','no','nor','not',
        'only','own','same','so','than','too','very','s','t','can','will',
        'just','don','should','now',
    }

    def __init__(self):
        self.stopwords = set(self.BASE_STOPWORDS) | set(self.FILLER_WORDS)
        if NLTK_AVAILABLE:
            try:
                self.stopwords.update(stopwords.words('english'))
            except Exception:
                pass

    # ── tokenisation ─────────────────────────────────────────────────────────
    def tokenize(self, text: str) -> List[str]:
        """Lowercase, clean, tokenize and remove stopwords."""
        cleaned = re.sub(r'[^a-z0-9\s]', ' ', text.lower())
        tokens  = word_tokenize(cleaned) if NLTK_AVAILABLE else cleaned.split()
        return [t for t in tokens if t not in self.stopwords and len(t) > 3]

    # ── single-segment keyword extraction ────────────────────────────────────
    def extract_keywords_frequency(self, text: str, top_n: int = 6) -> List[str]:
        """
        Improved frequency-based keyword extraction for single-segment case.

        Scoring:
          base  = term frequency
          bonus = +0.5 per extra character beyond length 5  (longer = more specific)
          bonus = +1.0 if the word appears capitalised in original text
                  (proper nouns like "Reddit", "OpenAI" are more informative)
        """
        tokens     = self.tokenize(text)
        if not tokens:
            return []

        freq       = Counter(tokens)
        total      = sum(freq.values())

        # Find words that appear capitalised in original (proper nouns)
        cap_words  = set(re.findall(r'\b([A-Z][a-z]{2,})\b', text))
        cap_lower  = {w.lower() for w in cap_words}

        scored = {}
        for word, count in freq.items():
            tf         = count / total
            length_b   = max(0, (len(word) - 5)) * 0.5
            capital_b  = 1.0 if word in cap_lower else 0.0
            scored[word] = tf + length_b + capital_b

        # Sort by score descending, return top_n
        keywords = sorted(scored, key=lambda w: scored[w], reverse=True)[:top_n]
        return keywords

    # ── multi-segment TF-IDF keyword extraction ───────────────────────────────
    def extract_keywords_tfidf(
        self, segments_texts: List[str], top_n: int = 6
    ) -> List[List[str]]:
        """
        TF-IDF keyword extraction across all segments.
        Falls back to improved frequency method when sklearn is unavailable
        or there is only one segment.
        """
        if not SKLEARN_AVAILABLE or len(segments_texts) < 2:
            return [self.extract_keywords_frequency(t, top_n) for t in segments_texts]

        try:
            vectorizer = TfidfVectorizer(
                max_features=200,
                stop_words='english',
                ngram_range=(1, 2),   # include bigrams for richer keywords
                min_df=1,
                max_df=0.85,          # ignore words present in >85 % of segments
                sublinear_tf=True,    # log-scale TF dampens very common words
            )

            tfidf_matrix  = vectorizer.fit_transform(segments_texts)
            feature_names = vectorizer.get_feature_names_out()

            all_keywords = []
            for i in range(len(segments_texts)):
                row         = tfidf_matrix[i].toarray()[0]
                top_indices = row.argsort()[-top_n:][::-1]
                keywords    = [
                    feature_names[idx]
                    for idx in top_indices
                    if row[idx] > 0
                    and feature_names[idx].lower() not in self.FILLER_WORDS
                ]
                # Fallback to frequency method for this segment if TF-IDF found nothing
                if not keywords:
                    keywords = self.extract_keywords_frequency(segments_texts[i], top_n)
                all_keywords.append(keywords)

            return all_keywords

        except Exception as e:
            print(f"  TF-IDF failed: {e}. Falling back to frequency method.")
            return [self.extract_keywords_frequency(t, top_n) for t in segments_texts]


# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY GENERATOR  (significantly improved)
# ─────────────────────────────────────────────────────────────────────────────
class SummaryGenerator:
    """
    Generate meaningful extractive summaries for each topic segment.

    Algorithm (TextRank-lite):
      1. Score every sentence by how many keywords it contains
         + a small positional bonus (earlier sentences score slightly higher)
      2. Pick the top-2 scoring sentences (in their original order)
      3. Join them into a fluent 2-sentence summary

    This is far better than "first + last" because:
      - It selects sentences that actually mention the topic's key terms
      - It avoids sign-off lines ("Hope you have a great week!") which
        score zero for keywords
      - It handles segments of any length gracefully
    """

    # Sentences containing only these patterns are skipped
    SKIP_PATTERNS = [
        r"^(thanks?|thank you|hope you|have a great|have a good|see you|"
        r"talk (to you )?next|stay tuned|subscribe|follow us|bye|goodbye|"
        r"welcome (back|to)|intro|outro)[\s,!.]*$",
    ]

    def _is_filler_sentence(self, text: str) -> bool:
        """Return True if this sentence is a generic filler / sign-off."""
        t = text.strip().lower().rstrip('.,!?')
        for pat in self.SKIP_PATTERNS:
            if re.match(pat, t, re.IGNORECASE):
                return True
        # Also skip very short sentences (fewer than 5 words)
        if len(t.split()) < 5:
            return True
        return False

    def _score_sentence(
        self,
        text: str,
        keyword_set: set,
        position: int,
        total: int,
    ) -> float:
        """
        Score a sentence for summary inclusion.

        score = keyword_hits / max(1, word_count)     ← keyword density
              + position_bonus                         ← slight early-sentence bonus
              + length_bonus                           ← prefer medium-length sentences
        """
        words       = text.lower().split()
        word_count  = len(words)
        if word_count == 0:
            return 0.0

        # Keyword density
        hits        = sum(1 for w in words if re.sub(r'[^a-z]', '', w) in keyword_set)
        kw_density  = hits / word_count

        # Position bonus: first 30 % of segment gets up to +0.15
        pos_ratio   = position / max(1, total - 1)
        pos_bonus   = 0.15 * max(0.0, 1.0 - pos_ratio / 0.3) if pos_ratio <= 0.3 else 0.0

        # Length bonus: sentences between 10 and 35 words are ideal
        if 10 <= word_count <= 35:
            length_bonus = 0.10
        elif word_count < 10:
            length_bonus = -0.05
        else:
            length_bonus = 0.0

        return kw_density + pos_bonus + length_bonus

    def generate_summary(
        self,
        sentences: List[Dict],
        keywords: List[str] = None,
        max_sentences: int = 2,
    ) -> str:
        """
        Generate a meaningful extractive summary.

        Args:
            sentences   : List of sentence dicts with 'text' key
            keywords    : Keywords for this segment (used for scoring)
            max_sentences: Number of sentences to include (default 2)

        Returns:
            A coherent 1–2 sentence summary string
        """
        if not sentences:
            return "No content available."

        # Filter out filler sentences
        valid = [
            (i, s) for i, s in enumerate(sentences)
            if not self._is_filler_sentence(s.get('text', ''))
        ]

        if not valid:
            # All sentences were fillers — just return the longest one
            return max(sentences, key=lambda s: len(s.get('text', ''))).get('text', '')

        if len(valid) == 1:
            return valid[0][1].get('text', '')

        # Build keyword set for scoring
        kw_set = set()
        if keywords:
            for kw in keywords:
                for w in kw.lower().split():
                    kw_set.add(re.sub(r'[^a-z]', '', w))

        # Fallback: use top frequent words from the segment text
        if not kw_set:
            all_text = ' '.join(s.get('text', '') for s in sentences).lower()
            words    = re.findall(r'\b[a-z]{4,}\b', all_text)
            freq     = Counter(words)
            kw_set   = {w for w, _ in freq.most_common(15)}

        n = len(valid)

        # Score each valid sentence
        scored = []
        for rank, (orig_idx, sent) in enumerate(valid):
            text  = sent.get('text', '')
            score = self._score_sentence(text, kw_set, rank, n)
            scored.append((score, orig_idx, text))

        # Pick top-N by score, then re-sort by original position for natural flow
        scored.sort(key=lambda x: x[0], reverse=True)
        top    = scored[:max_sentences]
        top.sort(key=lambda x: x[1])   # restore original order

        summary_parts = [t[2].strip().rstrip('.') for t in top]

        # Join naturally
        if len(summary_parts) == 1:
            result = summary_parts[0]
        else:
            result = '. '.join(summary_parts)

        # Ensure it ends with a period
        if result and not result.endswith(('.', '!', '?')):
            result += '.'

        return result


# ─────────────────────────────────────────────────────────────────────────────
# STANDALONE PIPELINE FUNCTIONS  (unchanged interface, better internals)
# ─────────────────────────────────────────────────────────────────────────────
def process_algorithm2_output(
    input_path: str,
    output_path: str,
    keywords_per_topic: int = 6,
) -> None:
    """Process Algorithm 2 output with evaluation, keywords, and summaries."""

    print(f"\n{'='*80}")
    print(f"Processing: {os.path.basename(input_path)}")
    print(f"{'='*80}")

    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    evaluator         = SegmentationEvaluator()
    keyword_extractor = KeywordExtractor()
    summary_generator = SummaryGenerator()

    # Evaluate
    print("\n  Evaluating Segmentation Quality...")
    evaluation = evaluator.evaluate_segmentation(data)
    print(f"    Overall Score: {evaluation['overall_score']:.1f}/10")
    for fb in evaluation['feedback']:
        print(f"    {fb}")

    # Keywords
    print("\n  Extracting Keywords...")
    topics         = data.get('topics', [])
    segment_texts  = [
        ' '.join(s.get('text', '') for s in t.get('sentences', []))
        for t in topics
    ]

    if len(segment_texts) > 1 and SKLEARN_AVAILABLE:
        print("    Using TF-IDF method")
        all_keywords = keyword_extractor.extract_keywords_tfidf(segment_texts, keywords_per_topic)
    else:
        print("    Using improved frequency method")
        all_keywords = [
            keyword_extractor.extract_keywords_frequency(t, keywords_per_topic)
            for t in segment_texts
        ]

    # Summaries
    print("\n  Generating Summaries...")
    for i, topic in enumerate(topics):
        keywords          = all_keywords[i] if i < len(all_keywords) else []
        topic['keywords'] = keywords
        topic['summary']  = summary_generator.generate_summary(
            topic.get('sentences', []), keywords
        )
        print(f"\n    Topic {i+1}: {topic.get('label','')}")
        print(f"    Keywords : {', '.join(keywords)}")
        print(f"    Summary  : {topic['summary'][:120]}{'...' if len(topic['summary']) > 120 else ''}")

    data['evaluation']          = evaluation
    data['enhanced']            = True
    data['enhancement_method']  = 'tfidf_keywords_extractive_summary_v2'

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n  Enhanced output saved to: {output_path}")
    print(f"{'='*80}\n")


def batch_process_algorithm2(
    input_dir: str = 'output/topics2/segments',
    output_dir: str = 'output/topics2_enhanced',
    keywords_per_topic: int = 6,
) -> None:
    """Batch process all Algorithm 2 outputs."""

    print("\n" + "="*80)
    print("  EVALUATION AND KEYWORD EXTRACTION — ALGORITHM 2")
    print("="*80)

    if not os.path.exists(input_dir):
        print(f"\n  Input directory not found: {input_dir}")
        print("  Please run Algorithm 2 first: python algorithim2.py")
        return

    json_files = [f for f in os.listdir(input_dir) if f.endswith('.json')]
    if not json_files:
        print(f"\n  No JSON files found in: {input_dir}")
        return

    print(f"\n  Found {len(json_files)} files")
    print(f"  Input  : {input_dir}")
    print(f"  Output : {output_dir}")

    for i, filename in enumerate(json_files, 1):
        print(f"\n{'='*80}\n  File {i}/{len(json_files)}: {filename}\n{'='*80}")
        try:
            process_algorithm2_output(
                input_path=os.path.join(input_dir, filename),
                output_path=os.path.join(output_dir, filename),
                keywords_per_topic=keywords_per_topic,
            )
        except Exception as e:
            print(f"  Error processing {filename}: {e}")

    print("\n" + "="*80)
    print("  BATCH PROCESSING COMPLETE")
    print("="*80)


if __name__ == "__main__":
    batch_process_algorithm2(
        input_dir='output/topics2/topics2/segments',
        output_dir='output/topics2_enhanced',
        keywords_per_topic=6,
    )
