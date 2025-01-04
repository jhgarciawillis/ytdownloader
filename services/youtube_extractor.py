import yt_dlp
from typing import List, Optional, Dict, Any
from models.video_info import VideoInfo
from utils.url_validator import YouTubeURLValidator
from config import MAX_PLAYLIST_VIDEOS
import logging
from datetime import datetime

class YouTubeExtractor:
    """
    Advanced YouTube video and playlist extraction service
    """

    def __init__(self, max_videos: int = MAX_PLAYLIST_VIDEOS):
        """
        Initialize the extractor with configurable parameters
        
        Args:
            max_videos (int): Maximum number of videos to extract from a playlist
        """
        self.max_videos = max_videos
        self.logger = logging.getLogger(__name__)
        
        # Comprehensive yt-dlp extraction options
        self.ydl_opts = {
            'extract_flat': False,  # Get full video information
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': True,  # Continue extraction if one video fails
            'no_color': True,
            'force_generic_extractor': False,
            
            # Additional metadata extraction
            'writeinfojson': False,
            'skip_download': True,
            
            # Performance and rate limiting
            'concurrent_downloads': 5,
            'retries': 3,
            'fragment_retries': 2,
            
            # Geo and age restrictions handling
            'geo_bypass': True,
            'age_limit': 0,
        }

    def _convert_duration(self, duration: Optional[int]) -> Optional[str]:
        """
        Convert duration seconds to human-readable format
        
        Args:
            duration (Optional[int]): Duration in seconds
        
        Returns:
            Optional[str]: Formatted duration string
        """
        if not duration:
            return None
        
        hours, remainder = divmod(duration, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        parts = []
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if seconds > 0:
            parts.append(f"{seconds}s")
        
        return " ".join(parts) if parts else "0s"

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """
        Parse upload date string to datetime
        
        Args:
            date_str (Optional[str]): Date string from yt-dlp
        
        Returns:
            Optional[datetime]: Parsed datetime object
        """
        if not date_str:
            return None
        
        try:
            # Try multiple date formats
            for fmt in ['%Y%m%d', '%Y-%m-%d', '%d.%m.%Y']:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            return None
        except Exception as e:
            self.logger.warning(f"Date parsing error: {e}")
            return None

    def extract_video_info(self, url: str) -> Optional[VideoInfo]:
        """
        Extract detailed information for a single video
        
        Args:
            url (str): YouTube video URL
        
        Returns:
            Optional[VideoInfo]: Extracted video information
        """
        if not YouTubeURLValidator.validate_youtube_url(url):
            self.logger.error(f"Invalid YouTube URL: {url}")
            return None

        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                
                if not info_dict:
                    self.logger.warning(f"No info extracted for URL: {url}")
                    return None

                return VideoInfo(
                    url=url,
                    title=info_dict.get('title', 'Untitled Video'),
                    playlist_title=info_dict.get('playlist_title'),
                    duration=info_dict.get('duration'),
                    upload_date=self._parse_date(info_dict.get('upload_date')),
                    view_count=info_dict.get('view_count'),
                    thumbnail_url=info_dict.get('thumbnail')
                )

        except Exception as e:
            self.logger.error(f"Error extracting video info: {e}")
            return None

    def extract_playlist_videos(self, playlist_url: str) -> List[VideoInfo]:
        """
        Extract videos from a YouTube playlist
        
        Args:
            playlist_url (str): YouTube playlist URL
        
        Returns:
            List[VideoInfo]: List of extracted video information
        """
        if not YouTubeURLValidator.is_playlist_url(playlist_url):
            self.logger.error(f"Invalid playlist URL: {playlist_url}")
            return []

        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                playlist_info = ydl.extract_info(playlist_url, download=False)
                
                if not playlist_info or 'entries' not in playlist_info:
                    self.logger.warning(f"No entries found in playlist: {playlist_url}")
                    return []

                # Limit number of videos
                entries = playlist_info['entries'][:self.max_videos]
                
                videos = []
                for entry in entries:
                    video = self.extract_video_info(entry['webpage_url'])
                    if video:
                        videos.append(video)

                return videos

        except Exception as e:
            self.logger.error(f"Playlist extraction error: {e}")
            return []

    def get_channel_videos(self, channel_url: str) -> List[VideoInfo]:
        """
        Extract videos from a YouTube channel
        
        Args:
            channel_url (str): YouTube channel URL
        
        Returns:
            List[VideoInfo]: List of channel's video information
        """
        if not YouTubeURLValidator.is_channel_url(channel_url):
            self.logger.error(f"Invalid channel URL: {channel_url}")
            return []

        # Similar implementation to playlist extraction
        # Left as an exercise or future enhancement
        self.logger.warning("Channel video extraction not fully implemented")
        return []