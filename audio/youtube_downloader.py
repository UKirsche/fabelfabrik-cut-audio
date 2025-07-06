import os
import re
import yt_dlp
from yt_dlp.utils import ExtractorError, UnavailableVideoError, GeoRestrictedError
from typing import Optional, Callable, Dict, Any
import urllib.parse
import urllib.request
import socket
from pathlib import Path


class YouTubeDownloaderError(Exception):
    """Custom exception for YouTube downloader errors"""
    pass


class InvalidURLError(YouTubeDownloaderError):
    """Exception for invalid YouTube URLs"""
    pass


class NetworkError(YouTubeDownloaderError):
    """Exception for network connectivity issues"""
    pass


class PermissionError(YouTubeDownloaderError):
    """Exception for file system permission issues"""
    pass


class VideoUnavailableError(YouTubeDownloaderError):
    """Exception for private or unavailable videos"""
    pass


class FormatError(YouTubeDownloaderError):
    """Exception for invalid format requests"""
    pass


class YouTubeDownloader:
    def __init__(self):
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': '%(title)s.%(ext)s',  # Default output template
            'noplaylist': True,  # Only download single video, not playlist
            'socket_timeout': 30,  # Timeout for socket operations
            'retries': 3,  # Number of retries for failed downloads
        }
        
        # YouTube URL patterns for validation
        self.youtube_patterns = [
            r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([\w-]+)',
            r'(?:https?://)?(?:www\.)?youtube\.com/embed/([\w-]+)',
            r'(?:https?://)?(?:www\.)?youtube\.com/v/([\w-]+)',
            r'(?:https?://)?youtu\.be/([\w-]+)',
            r'(?:https?://)?(?:www\.)?youtube\.com/shorts/([\w-]+)',
        ]
    
    def download(self, url: str, output_path: str, progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None) -> str:
        """
        Download audio from YouTube URL with comprehensive error handling
        
        Args:
            url: YouTube URL to download
            output_path: Directory to save the downloaded file
            progress_callback: Optional callback function to report download progress
            
        Returns:
            str: Path to the downloaded file
            
        Raises:
            InvalidURLError: If URL is not a valid YouTube URL
            VideoUnavailableError: If video is private or unavailable
            NetworkError: If network connectivity issues occur
            PermissionError: If file system permissions are insufficient
            FormatError: If requested format is not available
            YouTubeDownloaderError: For other download failures
        """
        # Comprehensive validation before download
        self._validate_url(url)
        self._validate_output_path(output_path)
        self._check_network_connectivity()
        
        try:
            # Ensure output directory exists with proper permissions
            self._ensure_output_directory(output_path)
            
            # Update output template to include the specified path
            opts = self.ydl_opts.copy()
            opts['outtmpl'] = os.path.join(output_path, '%(title)s.%(ext)s')
            
            # Add progress hook if callback is provided
            if progress_callback:
                opts['progress_hooks'] = [self._progress_hook_wrapper(progress_callback)]
            
            # Download the audio with enhanced error handling
            with yt_dlp.YoutubeDL(opts) as ydl:
                try:
                    # Get video info first to validate URL and availability
                    info = ydl.extract_info(url, download=False)
                    self._validate_video_info(info)
                    
                    video_title = info.get('title', 'Unknown')
                    
                    # Check if video has audio streams
                    self._validate_audio_availability(info)
                    
                    # Download the video
                    ydl.download([url])
                    
                    # Construct and verify the output filename
                    output_file = self._get_output_filename(ydl, info, output_path)
                    
                    return output_file
                    
                except ExtractorError as e:
                    self._handle_extractor_error(e)
                except yt_dlp.DownloadError as e:
                    self._handle_download_error(e)
                    
        except socket.timeout:
            raise NetworkError("Network timeout - check your internet connection")
        except socket.gaierror:
            raise NetworkError("DNS resolution failed - check your internet connection")
        except OSError as e:
            if "Permission denied" in str(e):
                raise PermissionError(f"Permission denied when writing to {output_path}")
            else:
                raise YouTubeDownloaderError(f"File system error: {str(e)}")
        except (InvalidURLError, VideoUnavailableError, FormatError, NetworkError, PermissionError):
            # Re-raise our custom exceptions without wrapping
            raise
        except Exception as e:
            raise YouTubeDownloaderError(f"Unexpected error during download: {str(e)}")
    
    def _progress_hook_wrapper(self, progress_callback: Callable[[Dict[str, Any]], None]):
        """
        Wrapper for progress hook to format progress data for GUI callback
        """
        def progress_hook(d: Dict[str, Any]):
            try:
                if d['status'] == 'downloading':
                    # Format progress data for GUI
                    progress_data = {
                        'status': 'downloading',
                        'filename': d.get('filename', ''),
                        'downloaded_bytes': d.get('downloaded_bytes', 0),
                        'total_bytes': d.get('total_bytes') or d.get('total_bytes_estimate', 0),
                        'speed': d.get('speed', 0),
                        'eta': d.get('eta', 0),
                    }
                    
                    # Calculate percentage if total bytes is available
                    if progress_data['total_bytes'] > 0:
                        progress_data['percent'] = (progress_data['downloaded_bytes'] / progress_data['total_bytes']) * 100
                    else:
                        progress_data['percent'] = 0
                    
                    progress_callback(progress_data)
                    
                elif d['status'] == 'finished':
                    progress_callback({
                        'status': 'finished',
                        'filename': d.get('filename', ''),
                        'percent': 100
                    })
                    
                elif d['status'] == 'error':
                    progress_callback({
                        'status': 'error',
                        'error': d.get('error', 'Unknown error')
                    })
                    
            except Exception as e:
                # Don't let progress callback errors break the download
                print(f"Progress callback error: {e}")
        
        return progress_hook
    
    def get_video_info(self, url: str) -> Dict[str, Any]:
        """
        Get video information without downloading with enhanced error handling
        
        Args:
            url: YouTube URL
            
        Returns:
            Dict containing video information
            
        Raises:
            InvalidURLError: If URL is not a valid YouTube URL
            VideoUnavailableError: If video is private or unavailable
            NetworkError: If network connectivity issues occur
            YouTubeDownloaderError: For other failures
        """
        # Validate URL before attempting to get info
        self._validate_url(url)
        self._check_network_connectivity()
        
        try:
            with yt_dlp.YoutubeDL({'quiet': True, 'socket_timeout': 15}) as ydl:
                info = ydl.extract_info(url, download=False)
                self._validate_video_info(info)
                
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'view_count': info.get('view_count', 0),
                    'upload_date': info.get('upload_date', ''),
                    'description': info.get('description', ''),
                    'availability': info.get('availability', 'unknown'),
                    'live_status': info.get('live_status', 'unknown'),
                }
        except ExtractorError as e:
            self._handle_extractor_error(e)
        except socket.timeout:
            raise NetworkError("Network timeout while getting video info")
        except Exception as e:
            raise YouTubeDownloaderError(f"Failed to get video info: {str(e)}")
    
    def set_audio_quality(self, quality: str):
        """
        Set the preferred audio quality with validation
        
        Args:
            quality: Audio quality (e.g., '192', '320', 'best')
        
        Raises:
            FormatError: If quality is not valid
        """
        valid_qualities = ['best', '320', '256', '192', '128', '96', '64']
        if quality not in valid_qualities:
            raise FormatError(f"Invalid audio quality '{quality}'. Valid options: {', '.join(valid_qualities)}")
        
        if self.ydl_opts['postprocessors']:
            self.ydl_opts['postprocessors'][0]['preferredquality'] = quality
    
    def set_output_format(self, format_code: str):
        """
        Set the preferred audio format with validation
        
        Args:
            format_code: Audio format (e.g., 'mp3', 'wav', 'flac')
        
        Raises:
            FormatError: If format is not supported
        """
        valid_formats = ['mp3', 'wav', 'flac', 'aac', 'm4a', 'ogg']
        if format_code.lower() not in valid_formats:
            raise FormatError(f"Invalid audio format '{format_code}'. Valid options: {', '.join(valid_formats)}")
        
        if self.ydl_opts['postprocessors']:
            self.ydl_opts['postprocessors'][0]['preferredcodec'] = format_code.lower()
    
    # === VALIDATION METHODS ===
    
    def _validate_url(self, url: str):
        """
        Validate YouTube URL format
        
        Args:
            url: URL to validate
            
        Raises:
            InvalidURLError: If URL is not a valid YouTube URL
        """
        if not url or not isinstance(url, str):
            raise InvalidURLError("URL cannot be empty")
        
        # Check if URL matches any YouTube pattern
        for pattern in self.youtube_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return  # Valid YouTube URL found
        
        raise InvalidURLError("Invalid YouTube URL format. Please provide a valid YouTube video URL.")
    
    def _validate_output_path(self, output_path: str):
        """
        Validate output path and permissions
        
        Args:
            output_path: Directory path to validate
            
        Raises:
            PermissionError: If path is not writable
        """
        if not output_path:
            raise PermissionError("Output path cannot be empty")
        
        # Check if parent directory exists and is writable
        path_obj = Path(output_path)
        if path_obj.exists():
            if not os.access(output_path, os.W_OK):
                raise PermissionError(f"No write permission for directory: {output_path}")
        else:
            # Check if parent directory is writable
            parent_dir = path_obj.parent
            if not parent_dir.exists():
                try:
                    parent_dir.mkdir(parents=True, exist_ok=True)
                except OSError as e:
                    raise PermissionError(f"Cannot create directory {parent_dir}: {str(e)}")
            elif not os.access(parent_dir, os.W_OK):
                raise PermissionError(f"No write permission for parent directory: {parent_dir}")
    
    def _check_network_connectivity(self):
        """
        Check basic network connectivity to YouTube
        
        Raises:
            NetworkError: If network is not accessible
        """
        try:
            # Try to resolve YouTube's domain
            socket.gethostbyname('www.youtube.com')
        except socket.gaierror:
            raise NetworkError("Cannot connect to YouTube. Please check your internet connection.")
    
    def _ensure_output_directory(self, output_path: str):
        """
        Ensure output directory exists with proper permissions
        
        Args:
            output_path: Directory path to create
            
        Raises:
            PermissionError: If directory cannot be created
        """
        try:
            os.makedirs(output_path, exist_ok=True)
        except OSError as e:
            if "Permission denied" in str(e):
                raise PermissionError(f"Permission denied when creating directory: {output_path}")
            else:
                raise PermissionError(f"Cannot create directory {output_path}: {str(e)}")
    
    def _validate_video_info(self, info: Dict[str, Any]):
        """
        Validate video availability and accessibility
        
        Args:
            info: Video information dictionary
            
        Raises:
            VideoUnavailableError: If video is not available
        """
        if not info:
            raise VideoUnavailableError("Video information could not be retrieved")
        
        # Check availability status
        availability = info.get('availability', '')
        if availability in ['private', 'premium_only', 'subscriber_only', 'needs_auth']:
            raise VideoUnavailableError(f"Video is not publicly available: {availability}")
        
        # Check if video is live and still ongoing
        live_status = info.get('live_status', '')
        if live_status == 'is_live':
            raise VideoUnavailableError("Cannot download ongoing live streams")
        
        # Check if video has been removed
        if info.get('title') == '[Deleted video]':
            raise VideoUnavailableError("Video has been deleted")
    
    def _validate_audio_availability(self, info: Dict[str, Any]):
        """
        Check if video has available audio streams
        
        Args:
            info: Video information dictionary
            
        Raises:
            FormatError: If no audio is available
        """
        formats = info.get('formats', [])
        has_audio = any(f.get('acodec') != 'none' for f in formats)
        
        if not has_audio:
            raise FormatError("No audio streams available for this video")
    
    def _get_output_filename(self, ydl, info: Dict[str, Any], output_path: str) -> str:
        """
        Get and verify the output filename
        
        Args:
            ydl: YouTube-dl object
            info: Video information
            output_path: Output directory
            
        Returns:
            str: Path to the downloaded file
            
        Raises:
            YouTubeDownloaderError: If file was not created
        """
        # Construct the expected output filename
        safe_title = ydl.prepare_filename(info)
        base_name = os.path.splitext(os.path.basename(safe_title))[0]
        output_file = os.path.join(output_path, f"{base_name}.mp3")
        
        # Verify the file was created
        if not os.path.exists(output_file):
            # Sometimes the filename might be slightly different, try to find it
            for file in os.listdir(output_path):
                if file.endswith('.mp3') and base_name in file:
                    output_file = os.path.join(output_path, file)
                    break
            else:
                raise YouTubeDownloaderError(f"Downloaded file not found in {output_path}")
        
        return output_file
    
    def _handle_extractor_error(self, error: ExtractorError):
        """
        Handle yt-dlp extractor errors with specific error types
        
        Args:
            error: The extractor error
            
        Raises:
            VideoUnavailableError or YouTubeDownloaderError
        """
        error_msg = str(error).lower()
        
        if any(keyword in error_msg for keyword in ['private', 'unavailable', 'removed', 'deleted']):
            raise VideoUnavailableError(f"Video is unavailable: {str(error)}")
        elif 'sign in' in error_msg or 'login' in error_msg:
            raise VideoUnavailableError("Video requires authentication to access")
        elif 'geo' in error_msg or 'country' in error_msg:
            raise VideoUnavailableError("Video is not available in your country")
        else:
            raise YouTubeDownloaderError(f"Video extraction failed: {str(error)}")
    
    def _handle_download_error(self, error: yt_dlp.DownloadError):
        """
        Handle yt-dlp download errors with specific error types
        
        Args:
            error: The download error
            
        Raises:
            NetworkError or FormatError or YouTubeDownloaderError
        """
        error_msg = str(error).lower()
        
        if any(keyword in error_msg for keyword in ['network', 'connection', 'timeout', 'unreachable']):
            raise NetworkError(f"Network error during download: {str(error)}")
        elif any(keyword in error_msg for keyword in ['format', 'codec', 'no audio']):
            raise FormatError(f"Audio format not available: {str(error)}")
        else:
            raise YouTubeDownloaderError(f"Download failed: {str(error)}")
