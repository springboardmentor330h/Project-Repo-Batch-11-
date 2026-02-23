"""
Audio Transcription Script 

"""

import os
import sys
from pathlib import Path
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


# Check for required libraries
import whisper
import torch
import numpy as np



class AudioTranscriber:
    """Transcribe audio files using WhisperASR"""
    
    def __init__(self, model_size="base", language="en"):
        """Initialize transcriber"""
        self.model_size = model_size
        self.language = language
        self.model = None
        
        print(f" Using device: CPU")
        print(f"Model: Whisper {model_size}")
        print(f" Language: {language}\n")
    
    def load_model(self):
        """Load Whisper model"""
        if self.model is None:
            print(f"Loading Whisper model ({self.model_size})...")
            print(" (First time will download ~140MB)")
            
            try:
                self.model = whisper.load_model(self.model_size, device="cpu")
                print("  Model loaded successfully!\n")
            except Exception as e:
                print(f" Error loading model: {e}")
                sys.exit(1)
    
    def transcribe_file(self, audio_path):
        """Transcribe a single audio file"""
        
        # Load model if needed
        if self.model is None:
            self.load_model()
        
        try:
            # Transcribe
            result = self.model.transcribe(
                str(audio_path),
                language=self.language,
                word_timestamps=True,
                fp16=False,  # CPU requires FP32
                verbose=False
            )
            
            # Extract segments with word timestamps
            segments = []
            
            for segment in result.get("segments", []):
                seg_data = {
                    "start": round(segment["start"], 2),
                    "end": round(segment["end"], 2),
                    "text": segment["text"].strip()
                }
                
                # Add word-level timestamps
                if "words" in segment:
                    words = []
                    for word in segment["words"]:
                        words.append({
                            "word": word.get("word", "").strip(),
                            "start": round(word.get("start", 0), 2),
                            "end": round(word.get("end", 0), 2)
                        })
                    seg_data["words"] = words
                
                segments.append(seg_data)
            
            return {
                "success": True,
                "text": result.get("text", "").strip(),
                "language": result.get("language", self.language),
                "segments": segments
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def save_transcript(self, result, output_path, audio_file):
        """Save transcript to JSON file"""
        
        if not result["success"]:
            return False
        
        # Create output data
        transcript = {
            "metadata": {
                "audio_file": audio_file,
                "model": self.model_size,
                "language": result["language"],
                "num_segments": len(result["segments"]),
                "duration": result["segments"][-1]["end"] if result["segments"] else 0,
                "timestamp": datetime.now().isoformat()
            },
            "text": result["text"],
            "segments": result["segments"]
        }
        
        # Save to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(transcript, f, indent=2, ensure_ascii=False)
        
        return True


def find_audio_chunks(input_dir):
    """Find all audio chunk files"""
    chunk_files = list(input_dir.glob("*_chunk_*.wav"))
    
    if not chunk_files:
        # Try without chunk pattern
        chunk_files = list(input_dir.glob("*.wav"))
    
    return sorted(chunk_files)


def group_by_audio_id(chunk_files):
    """Group chunks by source audio"""
    groups = {}
    
    for chunk_file in chunk_files:
        name = chunk_file.stem
        
        # Extract audio ID 
        if "_chunk_" in name:
            audio_id = name.rsplit("_chunk_", 1)[0]
        else:
            audio_id = name
        
        if audio_id not in groups:
            groups[audio_id] = []
        groups[audio_id].append(chunk_file)
    
    return groups


def main():
    """Main transcription pipeline"""
    
    print("\n" + "=" * 70)
    print("AUDIO TRANSCRIPTION - CPU VERSION")
    print("=" * 70 + "\n")
    
    # Setup paths
    project_root = Path.cwd()
    input_dir = project_root / "dataset" / "processed_audio" / "chunks"
    output_dir = project_root / "output" / "transcripts"
    
    print(f"Project: {project_root.name}")
    print(f" Input:  {input_dir}")
    print(f" Output: {output_dir}\n")
    
    # Check input directory
    if not input_dir.exists():
        print(f" Input directory not found!")
        print(f"  Looking for: {input_dir}")
        print("\n Solutions:")
        print(" 1. Run audio preprocessing first:")
        print("  python audio_preprocessing.py")
        print(" 2. Or update the input_dir path in the script")
        sys.exit(1)
    
    # Find audio files
    chunk_files = find_audio_chunks(input_dir)
    
    if not chunk_files:
        print(f" No audio files found in: {input_dir}")
        print("\n Make sure you have .wav files in the chunks directory")
        sys.exit(1)
    
    # Group by audio ID
    chunk_groups = group_by_audio_id(chunk_files)
    
    print(f" Found: {len(chunk_files)} files from {len(chunk_groups)} audio source(s)")
    print("\n" + "=" * 70)
    print("STARTING TRANSCRIPTION")
    print("=" * 70)
    
    # Initialize transcriber
    transcriber = AudioTranscriber(model_size="base", language="en")
    
    # Process each audio group
    start_time = datetime.now()
    total_processed = 0
    total_failed = 0
    
    for audio_idx, (audio_id, chunks) in enumerate(chunk_groups.items(), 1):
        print(f"\n[{audio_idx}/{len(chunk_groups)}] Audio: {audio_id}")
        print(f"{'─' * 70}")
        print(f"Chunks: {len(chunks)}\n")
        
        all_segments = []
        
        for chunk_idx, chunk_file in enumerate(chunks, 1):
            # Progress
            print(f"  [{chunk_idx}/{len(chunks)}] {chunk_file.name}")
            print(f" Transcribing... ", end='', flush=True)
            
            # Transcribe
            result = transcriber.transcribe_file(chunk_file)
            
            if result["success"]:
                # Save individual chunk transcript
                output_file = output_dir / f"{chunk_file.stem}.json"
                transcriber.save_transcript(result, output_file, chunk_file.name)
                
                # Collect segments for combined transcript
                all_segments.extend(result["segments"])
                
                print(f" {len(result['segments'])} segments")
                total_processed += 1
            else:
                print(f"Error: {result.get('error', 'Unknown error')}")
                total_failed += 1
        
        # Create combined transcript
        if all_segments:
            print(f"\n Combining {len(all_segments)} segments...")
            
            combined_file = output_dir / f"{audio_id}_combined.json"
            combined_data = {
                "metadata": {
                    "audio_id": audio_id,
                    "model": "base",
                    "num_chunks": len(chunks),
                    "total_segments": len(all_segments),
                    "total_duration": round(all_segments[-1]["end"], 2) if all_segments else 0,
                    "timestamp": datetime.now().isoformat()
                },
                "segments": all_segments
            }
            
            with open(combined_file, 'w', encoding='utf-8') as f:
                json.dump(combined_data, f, indent=2, ensure_ascii=False)
            
            print(f"Saved: {combined_file.name}")
    
    # Final summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f" Processed: {total_processed} chunks")
    print(f" Failed: {total_failed} chunks")
    print(f"⏱Time: {duration:.1f}s ({duration/60:.1f} minutes)")
    print(f"Output: {output_dir}")
    print("=" * 70 + "\n")
    
    if total_processed > 0:
        print(" Transcription complete!")
        print(f"Check your transcripts in: output/transcripts/\n")
        print(" Next step: Clean transcripts")
        print("python clean_transcripts_final.py\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n Stopped by user\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n Error: {e}\n")
        import traceback
        traceback.print_exc()
        print("\n If you need help, check:")
        print(" - Input directory exists: dataset/processed_audio/chunks/")
        print("- Audio files are present (.wav format)")
        print("- Whisper is installed: pip install openai-whisper\n")
        sys.exit(1)