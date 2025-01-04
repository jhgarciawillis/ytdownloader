from dataclasses import dataclass
import re
from typing import Optional
from datetime import datetime

@dataclass
class VideoInfo:
    url: str
    title: str
    playlist_title: Optional[str] = None
    duration: Optional[int] = None  # Duration in seconds
    upload_date: Optional[datetime] = None
    view_count: Optional[int] = None
    thumbnail_url: Optional[str] = None

    @staticmethod
    def clean_filename(title: str, max_length: int = 255) -> str:
        """
        Sanitize filenames by removing invalid characters and limiting length.
        
        Args:
            title (str): Original video title
            max_length (int): Maximum allowed filename length
        
        Returns:
            str: Cleaned filename
        """
        # Remove invalid filename characters
        cleaned_title = re.sub(r'[\\/*?:"<>|]', "", title)
        
        # Replace spaces and multiple spaces with single underscore
        cleaned_title = re.sub(r'\s+', '_', cleaned_title)
        
        # Truncate to max length
        cleaned_title = cleaned_title[:max_length]
        
        # Remove trailing periods or spaces
        cleaned_title = cleaned_title.strip('. ')
        
        return cleaned_title if cleaned_title else "unnamed_video"

    def get_sanitized_title(self, prefix: str = "", suffix: str = "") -> str:
        """
        Generate a fully sanitized filename with optional prefix/suffix.
        
        Args:
            prefix (str, optional): Prefix to add to the filename
            suffix (str, optional): Suffix to add to the filename
        
        Returns:
            str: Fully sanitized filename
        """
        base_title = self.clean_filename(self.title)
        
        # Combine prefix, base title, and suffix
        full_title = f"{prefix}_{base_title}_{suffix}".strip('_')
        
        return self.clean_filename(full_title)

    def __repr__(self) -> str:
        """
        String representation of VideoInfo for debugging.
        
        Returns:
            str: Detailed string representation
        """
        return (
            f"VideoInfo("
            f"title='{self.title}', "
            f"url='{self.url}', "
            f"playlist='{self.playlist_title or 'N/A'}', "
            f"duration={self.duration or 'N/A'})"
        )