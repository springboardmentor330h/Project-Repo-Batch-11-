"""
Simple Comparison: Algorithm 2 vs Algorithm 3
Compare TextTiling (Algorithm 2) with Embeddings (Algorithm 3)
"""

import json
import os
import pandas as pd

def analyze_file(filepath):
    """Analyze a single segmented file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        topics = data.get('topics', [])
        
        # Safely calculate metrics with None handling
        if topics:
            durations = [t.get('duration', 0) for t in topics if t.get('duration') is not None]
            sentences = [t.get('num_sentences', 0) for t in topics if t.get('num_sentences') is not None]
            
            avg_duration = sum(durations) / len(durations) if durations else 0
            avg_sentences = sum(sentences) / len(sentences) if sentences else 0
        else:
            avg_duration = 0
            avg_sentences = 0
        
        return {
            'num_topics': len(topics),
            'avg_duration': avg_duration,
            'avg_sentences': avg_sentences,
            'total_duration': data.get('total_duration', 0) or 0
        }
    except Exception as e:
        print(f"     Error analyzing file: {e}")
        return {
            'num_topics': 0,
            'avg_duration': 0,
            'avg_sentences': 0,
            'total_duration': 0
        }

def compare_algorithms():
    """Compare Algorithm 2 and Algorithm 3."""
    
    # Directories
    algo2_dir = 'output/topics2/topics2/segments'
    algo3_dir = 'output/topics3/topics3/segments'
    
    print("\n" + "="*80)
    print("ALGORITHM COMPARISON: TextTiling vs Embeddings")
    print("="*80)
    
    # Check directories
    print("\nChecking directories...")
    
    if not os.path.exists(algo2_dir):
        print(f" Algorithm 2 directory not found: {algo2_dir}")
        return
    
    if not os.path.exists(algo3_dir):
        print(f" Algorithm 3 directory not found: {algo3_dir}")
        return
    
    # Get files
    files2 = set([f for f in os.listdir(algo2_dir) if f.endswith('.json')])
    files3 = set([f for f in os.listdir(algo3_dir) if f.endswith('.json')])
    
    print(f"✓ Algorithm 2: {len(files2)} files")
    print(f"✓ Algorithm 3: {len(files3)} files")
    
    # Find common files
    common_files = files2.intersection(files3)
    
    if not common_files:
        print("\n No common files found between algorithms!")
        print("\nFiles in Algorithm 2:")
        for f in sorted(files2)[:5]:
            print(f"  - {f}")
        print("\nFiles in Algorithm 3:")
        for f in sorted(files3)[:5]:
            print(f"  - {f}")
        return
    
    print(f"\n✓ Found {len(common_files)} common files to compare")
    
    # Compare each file
    results = []
    
    print("\n" + "="*80)
    print("DETAILED COMPARISON")
    print("="*80)
    
    for filename in sorted(common_files):
        file2 = os.path.join(algo2_dir, filename)
        file3 = os.path.join(algo3_dir, filename)
        
        try:
            analysis2 = analyze_file(file2)
            analysis3 = analyze_file(file3)
            
            # Skip if both are empty
            if analysis2['num_topics'] == 0 and analysis3['num_topics'] == 0:
                print(f"\n  Skipping {filename} - no topics found in either algorithm")
                continue
            
            results.append({
                'filename': filename,
                'algo2_topics': analysis2['num_topics'],
                'algo3_topics': analysis3['num_topics'],
                'algo2_avg_duration': analysis2['avg_duration'],
                'algo3_avg_duration': analysis3['avg_duration'],
                'algo2_avg_sentences': analysis2['avg_sentences'],
                'algo3_avg_sentences': analysis3['avg_sentences'],
                'duration': analysis2['total_duration']
            })
            
            # Print comparison for this file
            print(f"\n {filename}")
            print(f"   Duration: {analysis2['total_duration']/60:.1f} minutes")
            print(f"\n   Algorithm 2 (TextTiling):")
            print(f"      Topics: {analysis2['num_topics']}")
            print(f"      Avg topic duration: {analysis2['avg_duration']:.1f}s")
            print(f"      Avg sentences/topic: {analysis2['avg_sentences']:.1f}")
            print(f"\n   Algorithm 3 (Embeddings):")
            print(f"      Topics: {analysis3['num_topics']}")
            print(f"      Avg topic duration: {analysis3['avg_duration']:.1f}s")
            print(f"      Avg sentences/topic: {analysis3['avg_sentences']:.1f}")
            
            # Quick comparison
            if analysis2['num_topics'] == analysis3['num_topics']:
                print(f"      → Same number of topics")
            elif analysis2['num_topics'] > analysis3['num_topics']:
                print(f"      → Algorithm 2 found more topics (+{analysis2['num_topics'] - analysis3['num_topics']})")
            else:
                print(f"      → Algorithm 3 found more topics (+{analysis3['num_topics'] - analysis2['num_topics']})")
        
        except Exception as e:
            print(f"\n Error processing {filename}: {e}")
            continue
    
    if not results:
        print("\n No valid results to compare!")
        print("Please check that your algorithm outputs have valid topic data.")
        return
    
    # Summary statistics
    df = pd.DataFrame(results)
    
    # Filter out rows where BOTH algorithms found 0 topics (invalid data)
    df = df[(df['algo2_topics'] > 0) | (df['algo3_topics'] > 0)]
    
    if df.empty:
        print("\n No valid data to analyze after filtering!")
        return
    
    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80)
    print(f"\nFiles analyzed: {len(df)}")
    
    print(f"\n Algorithm 2 (TextTiling - Lexical Cohesion):")
    print(f"   Avg topics per file: {df['algo2_topics'].mean():.1f}")
    print(f"   Avg topic duration: {df['algo2_avg_duration'].mean():.1f}s")
    print(f"   Avg sentences/topic: {df['algo2_avg_sentences'].mean():.1f}")
    
    print(f"\n Algorithm 3 (Embeddings - Semantic Meaning):")
    print(f"   Avg topics per file: {df['algo3_topics'].mean():.1f}")
    print(f"   Avg topic duration: {df['algo3_avg_duration'].mean():.1f}s")
    print(f"   Avg sentences/topic: {df['algo3_avg_sentences'].mean():.1f}")
    
    # Recommendation
    print("\n" + "="*80)
    print(" SMART RECOMMENDATION FOR YOUR DATA")
    print("="*80)
    
    avg_topics_2 = df['algo2_topics'].mean()
    avg_topics_3 = df['algo3_topics'].mean()
    avg_duration_2 = df['algo2_avg_duration'].mean()
    avg_duration_3 = df['algo3_avg_duration'].mean()
    avg_sentences_2 = df['algo2_avg_sentences'].mean()
    avg_sentences_3 = df['algo3_avg_sentences'].mean()
    
    # Multiple scoring criteria
    scores = {'algo2': 0, 'algo3': 0}
    reasons = {'algo2': [], 'algo3': []}
    
    # 1. Topic count comparison (more topics usually better for short audio)
    # For very short files (all showing 0 duration), prefer reasonable topic count
    if avg_topics_2 > 0 and avg_topics_3 > 0:
        # Both found topics - compare them
        if 3 <= avg_topics_2 <= 20:
            scores['algo2'] += 10
        elif 1 <= avg_topics_2 <= 3 or 20 < avg_topics_2 <= 50:
            scores['algo2'] += 7
        else:
            scores['algo2'] += 4
        
        if 3 <= avg_topics_3 <= 20:
            scores['algo3'] += 10
        elif 1 <= avg_topics_3 <= 3 or 20 < avg_topics_3 <= 50:
            scores['algo3'] += 7
        else:
            scores['algo3'] += 4
    
    # 2. Compare topic counts directly
    if avg_topics_3 > avg_topics_2 * 1.2:
        scores['algo3'] += 5
        reasons['algo3'].append(f"Detects more topics ({avg_topics_3:.1f} vs {avg_topics_2:.1f})")
    elif avg_topics_2 > avg_topics_3 * 1.2:
        scores['algo2'] += 5
        reasons['algo2'].append(f"Detects more topics ({avg_topics_2:.1f} vs {avg_topics_3:.1f})")
    
    # 3. Sentences per topic (ideal: 5-30 sentences)
    def sentences_score(avg_sentences):
        """How reasonable is sentences per topic?"""
        if 5 <= avg_sentences <= 30:
            return 10
        elif 3 <= avg_sentences < 5 or 30 < avg_sentences <= 50:
            return 7
        else:
            return 4
    
    score2_sentences = sentences_score(avg_sentences_2)
    score3_sentences = sentences_score(avg_sentences_3)
    
    scores['algo2'] += score2_sentences
    scores['algo3'] += score3_sentences
    
    if score3_sentences > score2_sentences:
        reasons['algo3'].append(f"Better sentences per topic ({avg_sentences_3:.1f} avg)")
    elif score2_sentences > score3_sentences:
        reasons['algo2'].append(f"Better sentences per topic ({avg_sentences_2:.1f} avg)")
    
    # 4. Consistency across files
    std_topics_2 = df['algo2_topics'].std()
    std_topics_3 = df['algo3_topics'].std()
    
    # Lower std = more consistent
    if std_topics_3 < std_topics_2 * 0.8:
        scores['algo3'] += 5
        reasons['algo3'].append("More consistent across different files")
    elif std_topics_2 < std_topics_3 * 0.8:
        scores['algo2'] += 5
        reasons['algo2'].append("More consistent across different files")
    
    # 5. Per-file win rate
    wins = {'algo2': 0, 'algo3': 0, 'tie': 0}
    
    for _, row in df.iterrows():
        # Simple comparison: which found more reasonable number of topics
        file_score_2 = 0
        file_score_3 = 0
        
        # Prefer 1-20 topics
        if 1 <= row['algo2_topics'] <= 20:
            file_score_2 += 2
        if 1 <= row['algo3_topics'] <= 20:
            file_score_3 += 2
        
        # Prefer 5-25 sentences per topic
        if 5 <= row['algo2_avg_sentences'] <= 25:
            file_score_2 += 1
        if 5 <= row['algo3_avg_sentences'] <= 25:
            file_score_3 += 1
        
        if file_score_3 > file_score_2:
            wins['algo3'] += 1
        elif file_score_2 > file_score_3:
            wins['algo2'] += 1
        else:
            wins['tie'] += 1
    
    if wins['algo3'] > wins['algo2']:
        scores['algo3'] += 8
        reasons['algo3'].append(f"Performs better on more files ({wins['algo3']}/{len(df)} files)")
    elif wins['algo2'] > wins['algo3']:
        scores['algo2'] += 8
        reasons['algo2'].append(f"Performs better on more files ({wins['algo2']}/{len(df)} files)")
    
    # Calculate final recommendation
    total_score_2 = scores['algo2']
    total_score_3 = scores['algo3']
    
    print("\n Scoring Breakdown:")
    print(f"   Algorithm 2 (TextTiling):  {total_score_2} points")
    print(f"   Algorithm 3 (Embeddings):  {total_score_3} points")
    
    print("\n" + "-"*80)
    
    # Final recommendation
    if total_score_3 > total_score_2 + 5:
        confidence = "HIGH"
        print(f"\n **STRONG RECOMMENDATION: Use Algorithm 3 (Embeddings)**")
        print(f"   Confidence: {confidence} ({total_score_3} vs {total_score_2} points)")
        print(f"\n   Why Algorithm 3 is better for YOUR data:")
        for reason in reasons['algo3']:
            print(f"      • {reason}")
        print(f"\n   Algorithm 3 advantages:")
        print(f"      • Understands semantic meaning (not just word matching)")
        print(f"      • Better at detecting topic shifts")
        print(f"      • Handles synonyms and paraphrasing")
        print(f"\n    Note: Slower processing, requires model (~90MB)")
        
    elif total_score_2 > total_score_3 + 5:
        confidence = "HIGH"
        print(f"\n **STRONG RECOMMENDATION: Use Algorithm 2 (TextTiling)**")
        print(f"   Confidence: {confidence} ({total_score_2} vs {total_score_3} points)")
        print(f"\n    Why Algorithm 2 is better for YOUR data:")
        for reason in reasons['algo2']:
            print(f"      • {reason}")
        print(f"\n   Algorithm 2 advantages:")
        print(f"      • Fast processing")
        print(f"      • Good vocabulary-based segmentation")
        print(f"      • Works well when topics have distinct vocabulary")
        print(f"\n  Bonus: No model download needed!")
        
    elif total_score_3 > total_score_2:
        confidence = "MODERATE"
        print(f"\n **RECOMMENDATION: Use Algorithm 3 (Embeddings)**")
        print(f"   Confidence: {confidence} ({total_score_3} vs {total_score_2} points)")
        print(f"\n   Why Algorithm 3 has a slight edge:")
        for reason in reasons['algo3']:
            print(f"      • {reason}")
        print(f"\n   Note: Both algorithms perform reasonably well on your data")
        print(f"     Choose Algorithm 3 for quality, Algorithm 2 for speed")
        
    elif total_score_2 > total_score_3:
        confidence = "MODERATE"
        print(f"\n **RECOMMENDATION: Use Algorithm 2 (TextTiling)**")
        print(f"   Confidence: {confidence} ({total_score_2} vs {total_score_3} points)")
        print(f"\n    Why Algorithm 2 has a slight edge:")
        for reason in reasons['algo2']:
            print(f"      • {reason}")
        print(f"\n    Note: Both algorithms perform reasonably well on your data")
        print(f"        Choose Algorithm 2 for speed, Algorithm 3 for quality")
        
    else:
        print(f"\n **TIE: Both algorithms perform equally well**")
        print(f"   Scores: Algorithm 2: {total_score_2}, Algorithm 3: {total_score_3}")
        print(f"\n    Performance Summary:")
        print(f"      Algorithm 2: {avg_topics_2:.1f} topics, {avg_duration_2:.0f}s per topic")
        print(f"      Algorithm 3: {avg_topics_3:.1f} topics, {avg_duration_3:.0f}s per topic")
        print(f"\n   Choose based on priorities:")
        print(f"      • Speed → Algorithm 2 (TextTiling)")
        print(f"      • Quality → Algorithm 3 (Embeddings)")
    
    # Additional context
    print("\n" + "-"*80)
    print("\n Your Data Characteristics:")
    avg_file_duration = df['duration'].mean()
    if avg_file_duration > 0:
        print(f"   • Average file duration: {avg_file_duration/60:.1f} minutes")
    else:
        print(f"   • Duration data: Not available (check your transcript metadata)")
    print(f"   • Files analyzed: {len(df)}")
    print(f"   • Algorithm 2 avg: {avg_topics_2:.1f} topics, {avg_sentences_2:.1f} sentences/topic")
    print(f"   • Algorithm 3 avg: {avg_topics_3:.1f} topics, {avg_sentences_3:.1f} sentences/topic")
    
    print("\n Additional Considerations:")
    print("   • Check visualizations: topics2/visualizations/ vs topics3/visualizations/")
    print("   • Manually review 1-2 segmented files to verify quality")
    print("   • If processing many files regularly: Algorithm 2 is faster")
    print("   • If quality is critical: Algorithm 3 is more accurate")
    
    # Export comparison
    output_file = 'output/comparison_algo2_vs_algo3.csv'
    df.to_csv(output_file, index=False)
    print(f"\n Detailed comparison exported to: {output_file}")
    
    print("\n" + "="*80)
    print(" Comparison complete!")
    print("="*80 + "\n")

if __name__ == "__main__":
    compare_algorithms()