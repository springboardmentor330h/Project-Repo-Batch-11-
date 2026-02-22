"""
Data Storage Module for AudioInsight
Handles saving and loading of processed transcription data
"""

import json
import os
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import shutil


class TranscriptionStorage:
    """
    Manages storage and retrieval of transcription data
    """
    
    def __init__(self, storage_dir: str = "transcription_history"):
        """
        Initialize storage manager
        
        Args:
            storage_dir: Directory to store transcription data
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        self.data_dir = self.storage_dir / "data"
        self.audio_dir = self.storage_dir / "audio"
        self.metadata_dir = self.storage_dir / "metadata"
        
        for dir_path in [self.data_dir, self.audio_dir, self.metadata_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    
    def generate_id(self, filename: str) -> str:
        """
        Generate unique ID for a transcription
        
        Args:
            filename: Original audio filename
            
        Returns:
            Unique ID string
        """
        timestamp = datetime.now().isoformat()
        unique_string = f"{filename}_{timestamp}"
        return hashlib.md5(unique_string.encode()).hexdigest()[:12]
    
    
    def save_transcription(
        self, 
        data: Dict, 
        audio_path: Optional[str] = None,
        custom_name: Optional[str] = None
    ) -> str:
        """
        Save transcription data
        
        Args:
            data: Processed transcription data dictionary
            audio_path: Path to original audio file (optional)
            custom_name: Custom name for this transcription (optional)
            
        Returns:
            Transcription ID
        """
        # Generate unique ID
        filename = data.get('file_name', 'unknown')
        trans_id = self.generate_id(filename)
        
        # Add metadata
        data['transcription_id'] = trans_id
        data['saved_at'] = datetime.now().isoformat()
        data['custom_name'] = custom_name or filename
        
        # Save main data
        data_path = self.data_dir / f"{trans_id}.json"
        with open(data_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Save audio file if provided
        if audio_path and os.path.exists(audio_path):
            audio_ext = Path(audio_path).suffix
            audio_dest = self.audio_dir / f"{trans_id}{audio_ext}"
            shutil.copy2(audio_path, audio_dest)
        
        # Save metadata for quick listing
        metadata = {
            'id': trans_id,
            'filename': filename,
            'custom_name': custom_name or filename,
            'saved_at': data['saved_at'],
            'duration': data.get('audio_duration', 0),
            'num_topics': len(data.get('topics', {}).get('topics', [])),
            'num_sentences': len(data.get('cleaned_transcript', {}).get('sentences', [])),
            'model_used': data.get('model_size', 'unknown')
        }
        
        metadata_path = self.metadata_dir / f"{trans_id}.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✅ Saved transcription: {trans_id}")
        return trans_id
    
    
    def load_transcription(self, trans_id: str) -> Optional[Dict]:
        """
        Load transcription data by ID
        
        Args:
            trans_id: Transcription ID
            
        Returns:
            Transcription data dictionary or None if not found
        """
        data_path = self.data_dir / f"{trans_id}.json"
        
        if not data_path.exists():
            print(f"❌ Transcription not found: {trans_id}")
            return None
        
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Add audio path if exists
            for ext in ['.mp3', '.wav', '.m4a', '.flac', '.ogg']:
                audio_path = self.audio_dir / f"{trans_id}{ext}"
                if audio_path.exists():
                    data['audio_path'] = str(audio_path)
                    break
            
            print(f"✅ Loaded transcription: {trans_id}")
            return data
            
        except Exception as e:
            print(f"❌ Error loading transcription: {e}")
            return None
    
    
    def list_transcriptions(self) -> List[Dict]:
        """
        List all saved transcriptions
        
        Returns:
            List of transcription metadata dictionaries
        """
        transcriptions = []
        
        for metadata_file in self.metadata_dir.glob("*.json"):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                transcriptions.append(metadata)
            except Exception as e:
                print(f"⚠️ Error reading {metadata_file}: {e}")
        
        # Sort by saved_at (newest first)
        transcriptions.sort(key=lambda x: x.get('saved_at', ''), reverse=True)
        
        return transcriptions
    
    
    def search_transcriptions(self, query: str) -> List[Dict]:
        """
        Search transcriptions by filename or custom name
        
        Args:
            query: Search query string
            
        Returns:
            List of matching transcription metadata
        """
        all_trans = self.list_transcriptions()
        query_lower = query.lower()
        
        matches = [
            t for t in all_trans
            if query_lower in t.get('filename', '').lower() 
            or query_lower in t.get('custom_name', '').lower()
        ]
        
        return matches
    
    
    def delete_transcription(self, trans_id: str) -> bool:
        """
        Delete a transcription and all associated files
        
        Args:
            trans_id: Transcription ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Delete data file
            data_path = self.data_dir / f"{trans_id}.json"
            if data_path.exists():
                data_path.unlink()
            
            # Delete metadata
            metadata_path = self.metadata_dir / f"{trans_id}.json"
            if metadata_path.exists():
                metadata_path.unlink()
            
            # Delete audio files (check all extensions)
            for ext in ['.mp3', '.wav', '.m4a', '.flac', '.ogg', '.webm']:
                audio_path = self.audio_dir / f"{trans_id}{ext}"
                if audio_path.exists():
                    audio_path.unlink()
            
            print(f"✅ Deleted transcription: {trans_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error deleting transcription: {e}")
            return False
    
    
    def get_storage_stats(self) -> Dict:
        """
        Get storage statistics
        
        Returns:
            Dictionary with storage stats
        """
        num_transcriptions = len(list(self.data_dir.glob("*.json")))
        
        # Calculate total size
        total_size = 0
        for dir_path in [self.data_dir, self.audio_dir, self.metadata_dir]:
            for file_path in dir_path.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        
        # Convert to MB
        total_size_mb = total_size / (1024 * 1024)
        
        return {
            'num_transcriptions': num_transcriptions,
            'total_size_mb': round(total_size_mb, 2),
            'storage_dir': str(self.storage_dir)
        }
    
    
    def export_transcription(self, trans_id: str, export_dir: str) -> bool:
        """
        Export transcription to a directory
        
        Args:
            trans_id: Transcription ID
            export_dir: Directory to export to
            
        Returns:
            True if successful
        """
        try:
            export_path = Path(export_dir)
            export_path.mkdir(parents=True, exist_ok=True)
            
            # Load data
            data = self.load_transcription(trans_id)
            if not data:
                return False
            
            # Export JSON
            json_path = export_path / f"{trans_id}_data.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Export transcript as TXT
            if 'cleaned_transcript' in data:
                txt_path = export_path / f"{trans_id}_transcript.txt"
                sentences = data['cleaned_transcript'].get('sentences', [])
                with open(txt_path, 'w', encoding='utf-8') as f:
                    for sent in sentences:
                        f.write(sent['text'] + '\n')
            
            # Copy audio if exists
            if 'audio_path' in data and os.path.exists(data['audio_path']):
                audio_src = Path(data['audio_path'])
                audio_dest = export_path / f"{trans_id}{audio_src.suffix}"
                shutil.copy2(audio_src, audio_dest)
            
            print(f"✅ Exported to: {export_dir}")
            return True
            
        except Exception as e:
            print(f"❌ Error exporting: {e}")
            return False
    
    
    def cleanup_old_transcriptions(self, days: int = 30) -> int:
        """
        Delete transcriptions older than specified days
        
        Args:
            days: Number of days to keep
            
        Returns:
            Number of transcriptions deleted
        """
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_count = 0
        
        for trans in self.list_transcriptions():
            saved_at = datetime.fromisoformat(trans['saved_at'])
            if saved_at < cutoff_date:
                if self.delete_transcription(trans['id']):
                    deleted_count += 1
        
        print(f"🧹 Cleaned up {deleted_count} old transcriptions")
        return deleted_count


# Convenience functions
def save_transcription(data: Dict, audio_path: Optional[str] = None, 
                      custom_name: Optional[str] = None) -> str:
    """Quick save function"""
    storage = TranscriptionStorage()
    return storage.save_transcription(data, audio_path, custom_name)


def load_transcription(trans_id: str) -> Optional[Dict]:
    """Quick load function"""
    storage = TranscriptionStorage()
    return storage.load_transcription(trans_id)


def list_transcriptions() -> List[Dict]:
    """Quick list function"""
    storage = TranscriptionStorage()
    return storage.list_transcriptions()


if __name__ == "__main__":
    # Test the storage module
    storage = TranscriptionStorage()
    
    print("Storage Stats:")
    stats = storage.get_storage_stats()
    print(f"  Transcriptions: {stats['num_transcriptions']}")
    print(f"  Total Size: {stats['total_size_mb']} MB")
    print(f"  Location: {stats['storage_dir']}")
