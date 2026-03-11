"""
Audio Preprocessing Pipeline

Steps:
1. Dataset Validation
2. Format Standardization (WAV, 16kHz, Mono, 16-bit)
3. Noise Reduction
4. Loudness Normalization
5. Silence Trimming
6. Audio Chunking (with overlap)

"""

import os
import sys
from pathlib import Path
import json
from datetime import datetime


# Audio processing libraries
import librosa
import soundfile as sf
import numpy as np
from scipy import signal
import noisereduce as nr
import pyloudnorm as pyln



class AudioPreprocessor:
    """ audio preprocessing pipeline"""
    
    def __init__(self, config=None):
        """Initialize with configuration"""
        self.config = config or self.default_config()
        
    @staticmethod
    def default_config():
        """preprocessing configuration"""
        return {
            "target_sr": 16000,          # 16 kHz sample rate
            "target_channels": 1,         # Mono
            "target_bit_depth": 16,       # 16-bit
            "chunk_duration": 25,         # 25 seconds per chunk
            "chunk_overlap": 5,           # 5 second overlap
            "noise_reduction": True,
            "normalization": True,
            "target_lufs": -16,          # Target loudness
            "silence_trimming": True,
            "silence_threshold": -40,     # dB
            "min_silence_duration": 2.0   # seconds
        }
    
    def validate_audio_file(self, file_path):
        """Validate audio file"""
        try:
            info = sf.info(file_path)
            
            validation = {
                "valid": True,
                "file": str(file_path),
                "format": file_path.suffix,
                "sample_rate": info.samplerate,
                "channels": info.channels,
                "duration": info.duration,
                "frames": info.frames
            }
            
            return validation
            
        except Exception as e:
            return {
                "valid": False,
                "file": str(file_path),
                "error": str(e)
            }
    
    def load_audio(self, file_path):
        """Load audio file"""
        audio, sr = librosa.load(file_path, sr=None, mono=False)
        return audio, sr
    
    def standardize_format(self, audio, sr):
        """
        Step 1: Standardize audio format
        - Convert to mono
        - Resample to 16kHz
        """
        # Convert to mono if stereo
        if len(audio.shape) > 1:
            audio = librosa.to_mono(audio)
        
        # Resample to target sample rate
        if sr != self.config["target_sr"]:
            audio = librosa.resample(audio, orig_sr=sr, target_sr=self.config["target_sr"])
            sr = self.config["target_sr"]
        
        return audio, sr
    
    def reduce_noise(self, audio, sr):
        """
        Step 2: Noise reduction using spectral subtraction
        """
        if not self.config["noise_reduction"]:
            return audio
        
        try:
            # Apply noise reduction
            reduced_audio = nr.reduce_noise(
                y=audio,
                sr=sr,
                stationary=True,
                prop_decrease=0.8
            )
            return reduced_audio
        except Exception as e:
            print(f" Noise reduction failed: {e}, using original audio")
            return audio
    
    def normalize_loudness(self, audio, sr):
        """
        Step 3: Loudness normalization to -16 LUFS
        """
        if not self.config["normalization"]:
            return audio
        
        try:
            # Create loudness meter
            meter = pyln.Meter(sr)
            
            # Measure loudness
            loudness = meter.integrated_loudness(audio)
            
            # Normalize to target LUFS
            normalized_audio = pyln.normalize.loudness(
                audio,
                loudness,
                self.config["target_lufs"]
            )
            
            return normalized_audio
            
        except Exception as e:
            print(f" Loudness normalization failed: {e}, using original audio")
            return audio
    
    def trim_silence(self, audio, sr):
        """
        Step 4: Trim silence from beginning and end
        """
        if not self.config["silence_trimming"]:
            return audio
        
        # Convert dB to amplitude
        threshold = librosa.db_to_amplitude(self.config["silence_threshold"])
        
        # Trim silence
        trimmed_audio, _ = librosa.effects.trim(
            audio,
            top_db=-self.config["silence_threshold"],
            frame_length=2048,
            hop_length=512
        )
        
        return trimmed_audio
    
    def chunk_audio(self, audio, sr, audio_id):
        """
        Step 5: Split audio into chunks with overlap
        """
        chunk_duration = self.config["chunk_duration"]
        chunk_overlap = self.config["chunk_overlap"]
        
        # Calculate samples
        chunk_samples = int(chunk_duration * sr)
        overlap_samples = int(chunk_overlap * sr)
        hop_samples = chunk_samples - overlap_samples
        
        chunks = []
        chunk_metadata = []
        end = 0
        
        # Create chunks
        for i, start in enumerate(range(0, len(audio) - chunk_samples + 1, hop_samples)):
            end = start + chunk_samples
            chunk = audio[start:end]
            
            # Calculate timestamps
            start_time = start / sr
            end_time = end / sr
            
            chunk_info = {
                "chunk_id": i + 1,
                "start_time": round(start_time, 2),
                "end_time": round(end_time, 2),
                "duration": round(end_time - start_time, 2),
                "start_sample": start,
                "end_sample": end,
                "overlap_with_previous": chunk_overlap if i > 0 else 0
            }
            
            chunks.append(chunk)
            chunk_metadata.append(chunk_info)
        
        # Handle remaining audio
        if len(audio) > end:
            remaining = audio[end:]
            if len(remaining) > sr * 5:  # Only if more than 5 seconds
                start_time = end / sr
                end_time = len(audio) / sr
                
                chunk_info = {
                    "chunk_id": len(chunks) + 1,
                    "start_time": round(start_time, 2),
                    "end_time": round(end_time, 2),
                    "duration": round(end_time - start_time, 2),
                    "start_sample": end,
                    "end_sample": len(audio),
                    "overlap_with_previous": 0
                }
                
                chunks.append(remaining)
                chunk_metadata.append(chunk_info)
        
        return chunks, chunk_metadata
    
    def save_audio(self, audio, sr, output_path):
        """Save processed audio"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        sf.write(
            output_path,
            audio,
            sr,
            subtype='PCM_16'  # 16-bit
        )
    
    def process_file(self, input_path, output_dir, create_chunks=True):
        """Process a single audio file through complete pipeline"""
        
        print(f"\n Processing: {input_path.name}")
        
        try:
            # Step 0: Validate
            validation = self.validate_audio_file(input_path)
            if not validation["valid"]:
                print(f"  Invalid file: {validation['error']}")
                return None
            
            print(f"  Valid audio: {validation['duration']:.2f}s, {validation['sample_rate']}Hz")
            
            # Load audio
            print(f"  Loading audio...")
            audio, sr = self.load_audio(input_path)
            
            # Step 1: Standardize format
            print(f"   Standardizing format (16kHz, mono)...")
            audio, sr = self.standardize_format(audio, sr)
            
            # Step 2: Noise reduction
            if self.config["noise_reduction"]:
                print(f"  Applying noise reduction...")
                audio = self.reduce_noise(audio, sr)
            
            # Step 3: Normalize loudness
            if self.config["normalization"]:
                print(f"  Normalizing loudness to {self.config['target_lufs']} LUFS...")
                audio = self.normalize_loudness(audio, sr)
            
            # Step 4: Trim silence
            if self.config["silence_trimming"]:
                print(f"   Trimming silence...")
                original_duration = len(audio) / sr
                audio = self.trim_silence(audio, sr)
                new_duration = len(audio) / sr
                trimmed = original_duration - new_duration
                if trimmed > 0.5:
                    print(f"  Trimmed {trimmed:.2f}s of silence")
            
            # Save full processed audio
            audio_id = input_path.stem
            # Naming convention: {original_name}_16k_mono_clean_norm_trim.wav
            full_output = output_dir / "full" / f"{audio_id}_16k_mono_clean_norm_trim.wav"
            print(f"  Saving full processed audio...")
            self.save_audio(audio, sr, full_output)
            
            # Step 5: Create chunks
            if create_chunks:
                print(f"  Creating chunks ({self.config['chunk_duration']}s with {self.config['chunk_overlap']}s overlap)...")
                chunks, chunk_metadata = self.chunk_audio(audio, sr, audio_id)
                
                print(f"  Created {len(chunks)} chunks")
                
                # Save chunks
                chunks_dir = output_dir / "chunks"
                chunks_dir.mkdir(parents=True, exist_ok=True)
                
                for i, (chunk, metadata) in enumerate(zip(chunks, chunk_metadata)):
                    # Naming convention: {original_name}_16k_mono_clean_norm_trim_chunk_{number}.wav
                    chunk_filename = f"{audio_id}_16k_mono_clean_norm_trim_chunk_{metadata['chunk_id']:03d}.wav"
                    chunk_path = chunks_dir / chunk_filename
                    self.save_audio(chunk, sr, chunk_path)
                
                # Save metadata
                metadata_path = output_dir / "metadata" / f"{audio_id}_16k_mono_clean_norm_trim_chunks_metadata.json"
                metadata_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(metadata_path, 'w') as f:
                    json.dump({
                        "audio_id": audio_id,
                        "original_file": str(input_path.name),
                        "original_duration": validation['duration'],
                        "processed_duration": len(audio) / sr,
                        "sample_rate": sr,
                        "num_chunks": len(chunks),
                        "chunk_duration": self.config['chunk_duration'],
                        "chunk_overlap": self.config['chunk_overlap'],
                        "chunks": chunk_metadata
                    }, f, indent=2)
            
            print(f" Complete!")
            
            return {
                "success": True,
                "audio_id": audio_id,
                "original_duration": validation['duration'],
                "processed_duration": len(audio) / sr,
                "num_chunks": len(chunks) if create_chunks else 0
            }
            
        except Exception as e:
            print(f"    ✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}


def main():
    """Main preprocessing pipeline"""
    
    print("\n" + "=" * 70)
    print("AUDIO PREPROCESSING PIPELINE")
    print("=" * 70 + "\n")
    
    # Paths
    project_root = Path.cwd()
    input_dir = project_root / "dataset" / "raw_audio"
    output_dir = project_root / "dataset" / "processed_audio"
    
    print(f" Project root: {project_root}")
    print(f" Input:  {input_dir}")
    print(f" Output: {output_dir}\n")
    
    # Check input directory
    if not input_dir.exists():
        print(f" Error: Input directory not found: {input_dir}")
        print("\n Tip: Place your audio files in dataset/raw_audio/\n")
        sys.exit(1)
    
    # Find audio files
    audio_extensions = ['.mp3', '.wav', '.m4a', '.flac', '.ogg']
    audio_files = []
    for ext in audio_extensions:
        audio_files.extend(input_dir.glob(f"*{ext}"))
    
    if not audio_files:
        print(f" No audio files found in: {input_dir}")
        print(f"  Supported formats: {', '.join(audio_extensions)}\n")
        sys.exit(1)
    
    print(f" Found {len(audio_files)} audio file(s)")
    print("=" * 70)
    
    # Initialize preprocessor
    preprocessor = AudioPreprocessor()
    
    # Display configuration
    print("\n  Configuration:")
    print(f"   Sample Rate: {preprocessor.config['target_sr']} Hz")
    print(f"   Channels: {preprocessor.config['target_channels']} (Mono)")
    print(f"   Bit Depth: {preprocessor.config['target_bit_depth']}-bit")
    print(f"   Chunk Duration: {preprocessor.config['chunk_duration']}s")
    print(f"   Chunk Overlap: {preprocessor.config['chunk_overlap']}s")
    print(f"   Noise Reduction: {'✓' if preprocessor.config['noise_reduction'] else '✗'}")
    print(f"   Normalization: {'✓' if preprocessor.config['normalization'] else '✗'}")
    print(f"   Silence Trimming: {'✓' if preprocessor.config['silence_trimming'] else '✗'}")
    
    # Process files
    results = {
        "processed": 0,
        "failed": 0,
        "total_duration": 0,
        "total_chunks": 0
    }
    
    start_time = datetime.now()
    
    for i, audio_file in enumerate(audio_files, 1):
        print(f"\n[{i}/{len(audio_files)}] " + "=" * 50)
        
        result = preprocessor.process_file(audio_file, output_dir, create_chunks=True)
        
        if result and result["success"]:
            results["processed"] += 1
            results["total_duration"] += result["processed_duration"]
            results["total_chunks"] += result.get("num_chunks", 0)
        else:
            results["failed"] += 1
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # Summary
    print("\n" + "=" * 70)
    print("PREPROCESSING SUMMARY")
    print("=" * 70)
    print(f" Successfully processed: {results['processed']} file(s)")
    if results["failed"] > 0:
        print(f" Failed: {results['failed']} file(s)")
    print(f" Total audio duration: {results['total_duration']:.2f}s ({results['total_duration']/60:.2f} min)")
    print(f" Total chunks created: {results['total_chunks']}")
    print(f" Processing time: {duration:.2f}s")
    print(f" Output location: {output_dir.absolute()}")
    print("=" * 70 + "\n")
    
    if results["processed"] > 0:
        print(" Preprocessing complete!")
        print(f" Processed audio: {output_dir / 'full'}")
        print(f" Audio chunks: {output_dir / 'chunks'}")
        print(f" Metadata: {output_dir / 'metadata'}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Interrupted by user\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n Unexpected error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)