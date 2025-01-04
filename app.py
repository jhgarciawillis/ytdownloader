import streamlit as st
import logging
import os
import tempfile

# Import custom modules
from config import TEMP_DOWNLOAD_DIR
from services.youtube_extractor import YouTubeExtractor
from services.audio_downloader import AudioDownloader
from ui.download_options import DownloadOptionsUI
from ui.progress_tracking import DownloadProgressTracker
from utils.url_validator import YouTubeURLValidator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class YouTubeAudioDownloaderApp:
    """
    Main Streamlit application for YouTube Audio Downloader
    """

    def __init__(self):
        """
        Initialize application components
        """
        # Set page configuration
        st.set_page_config(
            page_title="YouTube Audio Downloader",
            page_icon="🎵",
            layout="wide",
            initial_sidebar_state="expanded"
        )

        # Initialize services and utilities
        self.extractor = YouTubeExtractor()
        self.output_dir = TEMP_DOWNLOAD_DIR

    def run(self):
        """
        Main application entry point
        """
        # Application title and description
        st.title("🎵 YouTube Audio Downloader")
        st.markdown("""
        ### Download audio from YouTube videos, playlists, and channels
        - Supports single videos, playlists, and channel downloads
        - Multiple audio format options
        - Customizable file naming
        """)

        # URL Input
        url = DownloadOptionsUI.display_url_input()

        if not url:
            st.info("Please enter a valid YouTube URL")
            return

        # Validate URL
        if not YouTubeURLValidator.validate_youtube_url(url):
            st.error("Invalid YouTube URL. Please check and try again.")
            return

        # Determine URL type and extract videos
        videos = self._extract_videos(url)

        if not videos:
            st.warning("No videos found. Please check the URL.")
            return

        # Display download estimates
        DownloadProgressTracker.display_download_estimates(videos)

        # Allow video selection
        selected_videos = DownloadOptionsUI.select_videos(videos)

        if not selected_videos:
            st.warning("No videos selected for download.")
            return

        # Configure download options
        download_method = DownloadOptionsUI.select_download_method()
        naming_method, custom_prefix = DownloadOptionsUI.configure_naming_options()
        audio_format, audio_quality = DownloadOptionsUI.audio_format_options()

        # Prepare custom titles based on naming method
        custom_titles = self._generate_custom_titles(
            selected_videos, 
            naming_method, 
            custom_prefix
        )

        # Confirm download
        if DownloadOptionsUI.confirm_download(len(selected_videos)):
            self._perform_download(
                selected_videos, 
                custom_titles, 
                download_method, 
                audio_format, 
                audio_quality
            )

    def _extract_videos(self, url: str):
        """
        Extract videos based on URL type
        
        Args:
            url (str): YouTube URL
        
        Returns:
            List[VideoInfo]: Extracted videos
        """
        if YouTubeURLValidator.is_playlist_url(url):
            return self.extractor.extract_playlist_videos(url)
        elif YouTubeURLValidator.is_channel_url(url):
            return self.extractor.get_channel_videos(url)
        else:
            # Single video
            video = self.extractor.extract_video_info(url)
            return [video] if video else []

    def _generate_custom_titles(
        self, 
        videos, 
        naming_method, 
        custom_prefix=None
    ):
        """
        Generate custom titles for videos
        
        Args:
            videos (List[VideoInfo]): Videos to name
            naming_method (str): Naming strategy
            custom_prefix (Optional[str]): Prefix for titles
        
        Returns:
            List[str]: Custom titles
        """
        if naming_method == "Original Video Titles":
            return [video.title for video in videos]
        
        if naming_method == "Custom Prefix":
            prefix = custom_prefix or "audio"
            return [f"{prefix}_{i+1}" for i in range(len(videos))]
        
        if naming_method == "Numbered Sequence":
            return [f"track_{i+1}" for i in range(len(videos))]

    def _perform_download(
        self, 
        videos, 
        custom_titles, 
        download_method, 
        audio_format, 
        audio_quality
    ):
        """
        Execute audio download process
        
        Args:
            videos (List[VideoInfo]): Videos to download
            custom_titles (List[str]): Custom titles for videos
            download_method (str): Download method selection
            audio_format (str): Audio file format
            audio_quality (str): Audio quality
        """
        # Determine output directory based on method
        if download_method == "Custom Download Folder":
            output_dir = st.text_input("Enter download directory path")
            if not output_dir:
                st.error("Please specify a download directory")
                return
        else:
            output_dir = (
                tempfile.mkdtemp() if download_method == "Temporary Directory"
                else TEMP_DOWNLOAD_DIR
            )

        # Initialize downloader with selected format and quality
        downloader = AudioDownloader(
            output_dir=output_dir,
            audio_format=audio_format,
            quality=audio_quality
        )

        # Initialize progress tracker
        progress_tracker = DownloadProgressTracker(len(videos))

        # Perform downloads
        successful_videos = []
        failed_videos = []

        for video, title in zip(videos, custom_titles):
            try:
                download_result = downloader.download_audio(
                    video, 
                    custom_title=title
                )
                
                if download_result:
                    successful_videos.append(video)
                else:
                    failed_videos.append(video)
            except Exception as e:
                logger.error(f"Download failed for {video.title}: {e}")
                failed_videos.append(video)

        # Display download summary
        summary = DownloadProgressTracker.create_download_summary(
            successful_videos, 
            failed_videos
        )

        # Show summary stats
        st.write("### Download Summary")
        st.metric("Total Videos", summary['total_videos'])
        st.metric("Successful Downloads", summary['successful_count'])
        st.metric("Failed Downloads", summary['failed_count'])
        st.metric("Success Rate", f"{summary['success_rate']:.2f}%")

def main():
    app = YouTubeAudioDownloaderApp()
    app.run()

if __name__ == "__main__":
    main()