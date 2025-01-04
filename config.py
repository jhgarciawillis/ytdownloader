import tempfile
import os

# Directory Configurations
TEMP_DOWNLOAD_DIR = tempfile.mkdtemp()
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# FFmpeg Configuration
FFMPEG_PATH = r"C:\Python312\ffmpeg\bin\ffmpeg.exe"  # Adjust based on your system
FFMPEG_SYSTEM_PATH = "ffmpeg"  # Fallback system path

# Download Limits and Constraints
MAX_PLAYLIST_VIDEOS = 1000  # Maximum videos to download from a playlist
MAX_RETRY_ATTEMPTS = 5  # Maximum download retry attempts
DOWNLOAD_CHUNK_SIZE = 50  # Number of videos to download in a single chunk

# Audio Configurations
PREFERRED_AUDIO_FORMAT = 'mp3'
AUDIO_QUALITY = '192'  # Bitrate for audio conversion

# Supported File Naming Options
NAMING_OPTIONS = [
    "Original Video Titles", 
    "Custom Prefix", 
    "Numbered Sequence"
]

# Supported Download Methods
DOWNLOAD_METHODS = [
    "Temporary Directory", 
    "Download as ZIP", 
    "Custom Download Folder"
]

# Logging Configuration
LOG_FILE = os.path.join(SCRIPT_DIR, 'download_log.txt')

# URL Patterns
YOUTUBE_DOMAINS = [
    'www.youtube.com', 
    'youtube.com', 
    'youtu.be', 
    'm.youtube.com'
]

# Supported Audio Formats
SUPPORTED_AUDIO_FORMATS = ['mp3', 'm4a', 'wav', 'flac', 'webm']