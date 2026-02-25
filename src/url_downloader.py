"""
URL Audio Downloader Module

"""

import requests
from pathlib import Path
from urllib.parse import urlparse
import mimetypes
from typing import Optional, Callable


class URLDownloader:
    """Download audio files from URLs with validation and progress tracking."""
    
    SUPPORTED_AUDIO_EXTENSIONS = {'.mp3', '.wav', '.mp4', '.m4a', '.flac', '.ogg', '.webm'}
    SUPPORTED_MIME_TYPES = {
        'audio/mpeg', 'audio/mp3', 'audio/wav', 'audio/x-wav',
        'audio/mp4', 'audio/m4a', 'audio/flac', 'audio/ogg',
        'audio/webm', 'video/mp4', 'video/webm'
    }
    
    def __init__(self, timeout: int = 60, chunk_size: int = 8192):
        """
        Initialize downloader.
        
        Args:
            timeout: Request timeout in seconds
            chunk_size: Download chunk size in bytes
        """
        self.timeout = timeout
        self.chunk_size = chunk_size
    
    def validate_url(self, url: str) -> tuple[bool, str]:
        """
        Validate if URL is properly formatted.
        
        Args:
            url: URL to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        url = url.strip()
        
        if not url:
            return False, "URL cannot be empty"
        
        if not url.startswith(('http://', 'https://')):
            return False, "URL must start with http:// or https://"
        
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                return False, "Invalid URL format"
        except Exception as e:
            return False, f"Invalid URL: {str(e)}"
        
        return True, ""
    
    def get_file_extension(self, url: str, content_type: Optional[str] = None) -> str:
        """
        Determine file extension from URL or content type.
        
        Args:
            url: Download URL
            content_type: HTTP Content-Type header
            
        Returns:
            File extension (e.g., '.mp3')
        """
        # Try to get extension from URL path
        parsed = urlparse(url)
        ext = Path(parsed.path).suffix.lower()
        
        if ext in self.SUPPORTED_AUDIO_EXTENSIONS:
            return ext
        
        # Try to get extension from content type
        if content_type:
            ext = mimetypes.guess_extension(content_type.split(';')[0].strip())
            if ext and ext.lower() in self.SUPPORTED_AUDIO_EXTENSIONS:
                return ext.lower()
        
        # Default to .mp3
        return '.mp3'
    
    def download(
        self,
        url: str,
        output_path: Path,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> tuple[bool, str]:
        """
        Download audio file from URL.
        
        Args:
            url: URL to download from
            output_path: Path to save the downloaded file
            progress_callback: Optional callback function(downloaded_bytes, total_bytes)
            
        Returns:
            Tuple of (success, error_message)
        """
        # Validate URL
        is_valid, error_msg = self.validate_url(url)
        if not is_valid:
            return False, error_msg
        
        try:
            # Send HEAD request first to check content type and size
            head_response = requests.head(url, timeout=self.timeout, allow_redirects=True)
            content_type = head_response.headers.get('Content-Type', '')
            
            # Validate content type
            mime_type = content_type.split(';')[0].strip().lower()
            if mime_type and mime_type not in self.SUPPORTED_MIME_TYPES:
                return False, f"Unsupported content type: {content_type}. Expected audio file."
            
            # Get file size if available
            total_size = int(head_response.headers.get('Content-Length', 0))
            
            # Download file
            with requests.get(url, stream=True, timeout=self.timeout, allow_redirects=True) as response:
                response.raise_for_status()
                
                # Create output directory if needed
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                downloaded = 0
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=self.chunk_size):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            # Call progress callback
                            if progress_callback:
                                progress_callback(downloaded, total_size)
            
            return True, ""
            
        except requests.exceptions.Timeout:
            return False, "Download timed out. Please try again."
        
        except requests.exceptions.HTTPError as e:
            return False, f"HTTP error: {e.response.status_code} - {e.response.reason}"
        
        except requests.exceptions.ConnectionError:
            return False, "Connection error. Please check your internet connection."
        
        except Exception as e:
            return False, f"Download failed: {str(e)}"
    
    def download_with_retry(
        self,
        url: str,
        output_path: Path,
        retries: int = 3,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> tuple[bool, str]:
        """
        Download with retry logic.
        
        Args:
            url: URL to download from
            output_path: Path to save the downloaded file
            retries: Number of retry attempts
            progress_callback: Optional progress callback
            
        Returns:
            Tuple of (success, error_message)
        """
        last_error = ""
        
        for attempt in range(retries):
            success, error = self.download(url, output_path, progress_callback)
            
            if success:
                return True, ""
            
            last_error = error
            
            # Don't retry for validation errors
            if "Invalid URL" in error or "Unsupported content type" in error:
                break
        
        return False, f"Failed after {retries} attempts. Last error: {last_error}"
