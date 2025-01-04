import streamlit as st
from typing import List, Optional, Tuple
from models.video_info import VideoInfo

class DownloadOptionsUI:
    """
    Comprehensive UI component for managing download options in Streamlit
    """

    @staticmethod
    def display_url_input() -> Optional[str]:
        """
        Display URL input field with validation
        
        Returns:
            Optional[str]: Validated YouTube URL
        """
        url = st.text_input(
            "Enter YouTube Video, Playlist, or Channel URL",
            help="Supports individual videos, playlists, and channel URLs"
        )
        
        if url:
            # Basic URL validation could be added here
            return url
        
        return None

    @staticmethod
    def select_download_method() -> str:
        """
        Allow user to select download method
        
        Returns:
            str: Selected download method
        """
        return st.radio(
            "Download Method",
            [
                "Temporary Directory", 
                "Download as ZIP", 
                "Custom Download Folder"
            ],
            help=(
                "• Temporary Directory: Quick, ephemeral downloads\n"
                "• ZIP: Packaged download for easy transfer\n"
                "• Custom Folder: Choose your specific save location"
            )
        )

    @staticmethod
    def configure_naming_options() -> Tuple[str, Optional[str]]:
        """
        Configure file naming strategy
        
        Returns:
            Tuple[str, Optional[str]]: Naming method and optional prefix
        """
        naming_method = st.radio(
            "File Naming Strategy",
            [
                "Original Video Titles", 
                "Custom Prefix", 
                "Numbered Sequence"
            ]
        )
        
        custom_prefix = None
        if naming_method == "Custom Prefix":
            custom_prefix = st.text_input(
                "Enter Prefix", 
                help="Prefix will be added before original video title"
            )
        
        return naming_method, custom_prefix

    @staticmethod
    def select_videos(videos: List[VideoInfo]) -> List[VideoInfo]:
        """
        Interactive video selection interface
        
        Args:
            videos (List[VideoInfo]): List of available videos
        
        Returns:
            List[VideoInfo]: Selected videos
        """
        st.subheader("Video Selection")
        
        # Display video information in an interactive table
        video_data = [
            {
                "Select": False, 
                "Title": v.title, 
                "Duration": v.duration or "N/A"
            } for v in videos
        ]
        
        edited_df = st.data_editor(
            video_data,
            column_config={
                "Select": st.column_config.CheckboxColumn(
                    "Select",
                    help="Check videos to download"
                ),
                "Title": st.column_config.TextColumn("Video Title"),
                "Duration": st.column_config.TextColumn("Duration")
            },
            disabled=["Title", "Duration"]
        )
        
        # Filter selected videos
        selected_indices = [
            i for i, row in enumerate(edited_df) 
            if row["Select"]
        ]
        
        return [videos[i] for i in selected_indices]

    @staticmethod
    def audio_format_options() -> Tuple[str, str]:
        """
        Configure audio format and quality
        
        Returns:
            Tuple[str, str]: Selected audio format and quality
        """
        audio_format = st.selectbox(
            "Audio Format",
            ["MP3", "M4A", "WAV", "FLAC"],
            help="Choose the audio file format"
        )
        
        quality_options = {
            "Low (128 kbps)": "128",
            "Medium (192 kbps)": "192",
            "High (256 kbps)": "256",
            "Very High (320 kbps)": "320"
        }
        
        quality = st.select_slider(
            "Audio Quality",
            options=list(quality_options.keys()),
            value="Medium (192 kbps)",
            help="Higher quality means larger file size"
        )
        
        return audio_format.lower(), quality_options[quality]

    @staticmethod
    def confirm_download(
        video_count: int, 
        total_size_estimate: Optional[float] = None
    ) -> bool:
        """
        Final download confirmation
        
        Args:
            video_count (int): Number of videos to download
            total_size_estimate (Optional[float]): Estimated download size
        
        Returns:
            bool: Confirmation status
        """
        confirmation_text = f"Confirm download of {video_count} video(s)"
        
        if total_size_estimate:
            confirmation_text += f" (Est. {total_size_estimate:.2f} MB)"
        
        return st.button(
            confirmation_text, 
            type="primary"
        )

    @staticmethod
    def display_download_progress(
        current: int, 
        total: int, 
        current_video: Optional[str] = None
    ):
        """
        Display download progress
        
        Args:
            current (int): Current download progress
            total (int): Total videos to download
            current_video (Optional[str]): Currently downloading video
        """
        progress_percentage = int((current / total) * 100)
        
        st.progress(progress_percentage)
        
        if current_video:
            st.text(f"Downloading: {current_video}")
        
        st.text(f"Progress: {current}/{total} videos")