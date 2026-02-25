"""
Transcript Cleaning Script
"""

import json
import re
from pathlib import Path
import sys
from datetime import datetime




class TranscriptCleaner:
    """Clean and merge transcript segments"""
    
    # Filler words to remove
    FILLERS = [
        r'\bum+\b', r'\buh+\b', r'\blike\b', r'\byou know\b',
        r'\bi mean\b', r'\bsort of\b', r'\bkind of\b', 
        r'\bbasically\b', r'\bactually\b', r'\bliterally\b',
        r'\bso\b', r'\bwell\b', r'\bright\b', r'\bokay\b',
        r'\byeah\b', r'\byep\b', r'\bnah\b'
    ]
    
    def __init__(self, aggressive=False):
        """Initialize cleaner"""
        self.aggressive = aggressive
        print(f"Mode: {'Aggressive' if aggressive else 'Conservative'}")
        print()
    
    def clean_text(self, text):
        """Clean a text segment"""
        if not text or not text.strip():
            return ""
        
        # Remove artifacts
        text = re.sub(r'\[.*?\]', '', text)  
        
        # Remove fillers at sentence start
        for filler in self.FILLERS:
            text = re.sub(rf'^{filler}[,\s]+', '', text, flags=re.IGNORECASE)
            text = re.sub(rf'\s+{filler},\s+', ' ', text, flags=re.IGNORECASE)
            
            # Aggressive: remove all fillers
            if self.aggressive:
                text = re.sub(rf'\s+{filler}\s+', ' ', text, flags=re.IGNORECASE)
        
        # Fix spacing
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)
        
        # Remove repeated words
        text = re.sub(r'\b(\w+)\s+\1\b', r'\1', text, flags=re.IGNORECASE)
        
        # Capitalize first letter
        if text:
            text = text[0].upper() + text[1:]
        
        # Add period if needed
        if text and text[-1] not in '.!?':
            text += '.'
        
        return text
    
    def is_sentence_end(self, text):
        """Check if text ends with punctuation"""
        return text.rstrip().endswith(('.', '!', '?'))
    
    def merge_segments(self, segments):
        """Merge segments into sentences"""
        if not segments:
            return []
        
        sentences = []
        current = {
            "sentence_id": 1,
            "start": None,
            "end": None,
            "text": "",
            "count": 0
        }
        
        for seg in segments:
            text = seg.get("text", "").strip()
            if not text:
                continue
            
            # Initialize start
            if current["start"] is None:
                current["start"] = seg.get("start", 0)
            
            # Add space
            if current["text"] and not current["text"].endswith((' ', '-')):
                current["text"] += " "
            
            # Add text
            current["text"] += text
            current["end"] = seg.get("end", 0)
            current["count"] += 1
            
            # Check sentence end
            if self.is_sentence_end(text):
                cleaned = self.clean_text(current["text"])
                
                if cleaned:
                    sentences.append({
                        "sentence_id": current["sentence_id"],
                        "start": current["start"],
                        "end": current["end"],
                        "text": cleaned,
                        "duration": round(current["end"] - current["start"], 2),
                        "original_segments": current["count"]
                    })
                
                # Reset
                current = {
                    "sentence_id": len(sentences) + 1,
                    "start": None,
                    "end": None,
                    "text": "",
                    "count": 0
                }
        
        # Handle remaining
        if current["text"].strip():
            cleaned = self.clean_text(current["text"])
            if cleaned:
                sentences.append({
                    "sentence_id": current["sentence_id"],
                    "start": current["start"],
                    "end": current["end"],
                    "text": cleaned,
                    "duration": round(current["end"] - current["start"], 2),
                    "original_segments": current["count"]
                })
        
        return sentences
    
    def process_file(self, input_path, output_path):
        """Process one transcript file"""
        
        # Load file
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            return {"success": False, "error": str(e)}
        
        # Extract segments
        if isinstance(data, list):
            segments = data
        elif isinstance(data, dict):
            segments = data.get("segments", [])
        else:
            return {"success": False, "error": "Invalid format"}
        
        if not segments:
            return {"success": False, "error": "No segments"}
        
        # Merge and clean
        sentences = self.merge_segments(segments)
        
        # Create output
        output = {
            "metadata": {
                "original_file": input_path.name,
                "original_segments": len(segments),
                "cleaned_sentences": len(sentences),
                "total_duration": round(sentences[-1]["end"] - sentences[0]["start"], 2) if sentences else 0,
                "merged": len(segments) - len(sentences),
                "mode": "aggressive" if self.aggressive else "conservative",
                "timestamp": datetime.now().isoformat()
            },
            "sentences": sentences
        }
        
        # Save
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        return {
            "success": True,
            "segments": len(segments),
            "sentences": len(sentences),
            "merged": len(segments) - len(sentences)
        }


def main():
    """Main function"""
    
    # Paths
    project_root = Path.cwd()
    input_dir = project_root / "output" / "transcripts"
    output_dir = project_root / "output" / "transcripts_cleaned"
    
    print(f"Project: {project_root.name}")
    print(f"Input:  {input_dir}")
    print(f"Output: {output_dir}\n")
    
    # Check input
    if not input_dir.exists():
        print(" Input directory not found!")
        print(f" Expected: {input_dir}")
        print("\n Run transcription first:")
        print(" python transcribe_audio.py\n")
        sys.exit(1)
    
    # Find files
    files = [f for f in input_dir.glob("*.json") if "_cleaned" not in f.name]
    
    if not files:
        print(" No transcript files found!")
        print(f" Looking in: {input_dir}\n")
        sys.exit(1)
    
    print(f" Found: {len(files)} file(s)\n")
    print("=" * 70)
    print("PROCESSING")
    print("=" * 70 + "\n")
    
    # Initialize cleaner
    cleaner = TranscriptCleaner(aggressive=False)
    
    # Process
    results = {
        "processed": 0,
        "failed": 0,
        "total_segments": 0,
        "total_sentences": 0,
        "total_merged": 0
    }
    
    for i, file in enumerate(files, 1):
        print(f"[{i}/{len(files)}] {file.name}")
        
        output_file = output_dir / f"{file.stem}_cleaned.json"
        result = cleaner.process_file(file, output_file)
        
        if result["success"]:
            print(f" {result['segments']} → {result['sentences']} sentences")
            print(f" Merged: {result['merged']}")
            print(f" Saved: {output_file.name}\n")
            
            results["processed"] += 1
            results["total_segments"] += result["segments"]
            results["total_sentences"] += result["sentences"]
            results["total_merged"] += result["merged"]
        else:
            print(f"  ✗ Error: {result['error']}\n")
            results["failed"] += 1
    
    
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f" Processed: {results['processed']}")
    print(f" Failed: {results['failed']}")
    print(f" {results['total_segments']} segments → {results['total_sentences']} sentences")
    print(f" Merged: {results['total_merged']} segments")
    print(f" Output: {output_dir}")
    print("=" * 70 + "\n")
    
    if results["processed"] > 0:
        print(" Cleaning complete")
        print(f" Check: output/transcripts_cleaned/\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n Stopped\n")
    except Exception as e:
        print(f"\n Error: {e}\n")
        import traceback
        traceback.print_exc()