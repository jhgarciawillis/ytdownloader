import os
import yt_dlp
import logging
from typing import Optional, List, Dict, Any

from models.video_info import VideoInfo
from utils.file_helpers import FileHelper
from config import (
    FFMPEG_PATH, 
    PREFERRED_AUDIO_FORMAT, 
    AUDIO_QUALITY, 
    MAX_RETRY_ATTEMPTS
)

class AudioDownloader:
    """
    Advanced audio downloading and processing service
    """

    def __init__(
        self, 
        output_dir: str, 
        audio_format: str = PREFERRED_AUDIO_FORMAT,
        quality: str = AUDIO_QUALITY
    ):
        """
        Initialize AudioDownloader with configuration options
        
        Args:
            output_dir (str): Base directory for downloads
            audio_format (str): Preferred audio format
            quality (str): Audio quality setting
        """
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        
        # Comprehensive yt-dlp options for audio extraction
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': audio_format,
                'preferredquality': quality,
            }],
            'outtmpl': '%(title)s.%(ext)s',
            'no_color': True,
            'no_warnings': True,
            'ignoreerrors': False,
            'quiet': False,
            
            # FFmpeg configuration
            'ffmpeg_location': FFMPEG_PATH,
            
            # Retry and connection settings
            'retries': MAX_RETRY_ATTEMPTS,
            'fragment_retries': 2,
            'buffer_size': 1024 * 1024,  # 1MB buffer
            'no_part': True,  # Disable .part file creation
            
            # Geo and age restrictions
            'geo_bypass': True,
            'age_limit': 0,
        }

    def download_audio(
        self, 
        video: VideoInfo, 
        custom_title: Optional[str] = None,
        playlist_folder: Optional[str] = None
    ) -> Optional[str]:
        """
        Download audio for a single video
        
        Args:
            video (VideoInfo): Video information
            custom_title (Optional[str]): Custom filename
            playlist_folder (Optional[str]): Subfolder for playlist downloads
        
        Returns:
            Optional[str]: Path to downloaded audio file
        """
        try:
            # Determine output directory
            output_dir = self.output_dir
            if playlist_folder:
                output_dir = os.path.join(output_dir, playlist_folder)
            
            # Ensure output directory exists
            FileHelper.create_directory(output_dir)
            
            # Prepare filename
            filename = custom_title or video.title
            sanitized_filename = FileHelper.sanitize_filename(filename)
            
            # Generate unique filepath
            filepath = FileHelper.generate_unique_filename(
                output_dir, 
                sanitized_filename, 
                f'.{self.ydl_opts["postprocessors"][0]["preferredcodec"]}'
            )
            
            # Update yt-dlp options with specific output template
            self.ydl_opts['outtmpl'] = filepath
            
            # Download audio
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                ydl.download([video.url])
            
            # Verify file exists
            if os.path.exists(filepath):
                self.logger.info(f"Successfully downloaded: {filepath}")
                return filepath
            else:
                self.logger.warning(f"Download completed but file not found: {filepath}")
                return None
        
        except Exception as e:
            self.logger.error(f"Download failed for {video.title}: {e}")
            return None

    def batch_download(
        self, 
        videos: List[VideoInfo], 
        custom_titles: Optional[List[str]] = None,
        playlist_folder: Optional[str] = None
    ) -> List[str]:
        """
        Batch download multiple videos
        
        Args:
            videos (List[VideoInfo]): List of videos to download
            custom_titles (Optional[List[str]]): Custom titles for each video
            playlist_folder (Optional[str]): Subfolder for downloads
        
        Returns:
            List[str]: Paths of successfully downloaded files
        """
        # Use original titles if no custom titles provided
        if not custom_titles:
            custom_titles = [video.title for video in videos]
        
        # Ensure titles list matches videos list
        custom_titles = custom_titles[:len(videos)]
        
        downloaded_files = []
        for video, title in zip(videos, custom_titles):
            filepath = self.download_audio(
                video, 
                custom_title=title, 
                playlist_folder=playlist_folder
            )
            
            if filepath:
                downloaded_files.append(filepath)
        
        return downloaded_files

    def get_audio_metadata(self, filepath: str) -> Dict[str, Any]:
        """
        Extract metadata from downloaded audio file
        
        Args:
            filepath (str): Path to audio file
        
        Returns:
            Dict[str, Any]: Audio file metadata
        """
        try:
            from mutagen.mp3 import MP3
            from mutagen.easyid3 import EasyID3
            
            audio = MP3(filepath, ID3=EasyID3)
            metadata = {
                'filename': os.path.basename(filepath),
                'size': os.path.getsize(filepath),
                'duration': audio.info.length,
                'bitrate': audio.info.bitrate,
                'tags': dict(audio)
            }
            
            return metadata
        
        except ImportError:
            self.logger.warning("Mutagen library not available for metadata extraction")
            return {}
        except Exception as e:
            self.logger.error(f"Metadata extraction error: {e}")
            return {}