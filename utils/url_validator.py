import re
from urllib.parse import urlparse, parse_qs
from typing import Optional, Dict

class YouTubeURLValidator:
    """
    Comprehensive URL validation and extraction utility for YouTube URLs
    """
    
    # Regular expressions for different YouTube URL patterns
    YOUTUBE_PATTERNS = {
        'standard_video': r'^(https?\:\/\/)?(www\.youtube\.com\/watch\?v=)([^&]+)',
        'shortened_video': r'^(https?\:\/\/)?(youtu\.be\/)([^&\?]+)',
        'playlist': r'^(https?\:\/\/)?(www\.youtube\.com\/playlist\?list=)([^&]+)',
        'channel': r'^(https?\:\/\/)?(www\.youtube\.com\/channel\/)([^&\/]+)'
    }

    @classmethod
    def validate_youtube_url(cls, url: str) -> bool:
        """
        Validates if the given URL is a valid YouTube URL
        
        Args:
            url (str): URL to validate
        
        Returns:
            bool: True if valid YouTube URL, False otherwise
        """
        if not url or not isinstance(url, str):
            return False
        
        # Check against predefined patterns
        return any(
            re.match(pattern, url, re.IGNORECASE)
            for pattern in cls.YOUTUBE_PATTERNS.values()
        )

    @classmethod
    def extract_video_id(cls, url: str) -> Optional[str]:
        """
        Extracts the video ID from various YouTube URL formats
        
        Args:
            url (str): YouTube video URL
        
        Returns:
            Optional[str]: Extracted video ID or None
        """
        if not cls.validate_youtube_url(url):
            return None
        
        # Video ID extraction strategies
        extractors = [
            lambda u: re.search(r'v=([^&]+)', u),
            lambda u: re.search(r'youtu\.be\/([^&\?]+)', u),
            lambda u: re.search(r'embed\/([^&\?]+)', u)
        ]
        
        for extractor in extractors:
            match = extractor(url)
            if match:
                return match.group(1)
        
        return None

    @classmethod
    def parse_youtube_url(cls, url: str) -> Dict[str, str]:
        """
        Comprehensive URL parsing for YouTube links
        
        Args:
            url (str): YouTube URL to parse
        
        Returns:
            Dict[str, str]: Parsed URL components
        """
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        
        return {
            'scheme': parsed_url.scheme,
            'netloc': parsed_url.netloc,
            'path': parsed_url.path,
            'video_id': cls.extract_video_id(url),
            'query_params': query_params
        }

    @classmethod
    def is_playlist_url(cls, url: str) -> bool:
        """
        Determines if the URL is a YouTube playlist
        
        Args:
            url (str): URL to check
        
        Returns:
            bool: True if playlist URL, False otherwise
        """
        return bool(re.match(cls.YOUTUBE_PATTERNS['playlist'], url, re.IGNORECASE))

    @classmethod
    def is_channel_url(cls, url: str) -> bool:
        """
        Determines if the URL is a YouTube channel
        
        Args:
            url (str): URL to check
        
        Returns:
            bool: True if channel URL, False otherwise
        """
        return bool(re.match(cls.YOUTUBE_PATTERNS['channel'], url, re.IGNORECASE))

    @classmethod
    def sanitize_url(cls, url: str) -> Optional[str]:
        """
        Sanitizes and normalizes YouTube URLs
        
        Args:
            url (str): URL to sanitize
        
        Returns:
            Optional[str]: Sanitized URL or None
        """
        if not cls.validate_youtube_url(url):
            return None
        
        # Remove unnecessary tracking parameters
        cleaned_url = re.sub(r'&.*', '', url)
        
        # Ensure https protocol
        if not cleaned_url.startswith(('http://', 'https://')):
            cleaned_url = f'https://{cleaned_url}'
        
        return cleaned_url