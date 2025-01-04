import streamlit as st
import time
from typing import List, Optional, Callable
import threading
import queue

class DownloadProgressTracker:
    """
    Advanced download progress tracking and management
    """

    def __init__(self, total_videos: int):
        """
        Initialize progress tracker
        
        Args:
            total_videos (int): Total number of videos to download
        """
        self.total_videos = total_videos
        self.current_video = 0
        self.successful_downloads = 0
        self.failed_downloads = 0
        self.download_queue = queue.Queue()
        self.download_thread = None
        self.stop_event = threading.Event()

        # Streamlit-specific progress elements
        self.progress_bar = st.progress(0)
        self.status_text = st.empty()
        self.detailed_status = st.expander("Download Details")

    def start_download(self, download_func: Callable):
        """
        Start asynchronous download process
        
        Args:
            download_func (Callable): Function to execute downloads
        """
        self.download_thread = threading.Thread(
            target=self._download_worker, 
            args=(download_func,)
        )
        self.download_thread.start()

    def _download_worker(self, download_func: Callable):
        """
        Background download worker
        
        Args:
            download_func (Callable): Function to execute downloads
        """
        try:
            while not self.stop_event.is_set():
                # Fetch next download task
                video = self.download_queue.get(timeout=1)
                
                if video is None:
                    break
                
                try:
                    # Execute download
                    result = download_func(video)
                    
                    if result:
                        self.successful_downloads += 1
                        self._update_progress(video.title, success=True)
                    else:
                        self.failed_downloads += 1
                        self._update_progress(video.title, success=False)
                
                except Exception as e:
                    self.failed_downloads += 1
                    self._update_progress(video.title, success=False, error=str(e))
                
                finally:
                    self.download_queue.task_done()
        
        except queue.Empty:
            pass
        finally:
            self.stop_event.set()

    def _update_progress(
        self, 
        video_title: str, 
        success: bool = True, 
        error: Optional[str] = None
    ):
        """
        Update download progress and UI
        
        Args:
            video_title (str): Title of current video
            success (bool): Download success status
            error (Optional[str]): Error message if download failed
        """
        self.current_video += 1
        progress = self.current_video / self.total_videos

        # Update Streamlit progress bar
        self.progress_bar.progress(progress)

        # Status message
        status_message = f"Downloading: {video_title}"
        if not success:
            status_message += " [FAILED]"
            if error:
                status_message += f" - {error}"
        
        self.status_text.text(status_message)

        # Detailed status logging
        with self.detailed_status:
            st.write(f"Video: {video_title}")
            st.write(f"Status: {'Success' if success else 'Failed'}")
            if error:
                st.error(f"Error: {error}")

    def add_download_task(self, video):
        """
        Add video to download queue
        
        Args:
            video: Video to be downloaded
        """
        self.download_queue.put(video)

    def finalize_download(self):
        """
        Finalize download process and display summary
        """
        # Wait for all downloads to complete
        self.download_queue.join()
        self.stop_event.set()

        if self.download_thread:
            self.download_thread.join()

        # Display final summary
        st.success("Download Complete!")
        st.metric("Total Videos", self.total_videos)
        st.metric("Successful Downloads", self.successful_downloads)
        st.metric("Failed Downloads", self.failed_downloads)

    @staticmethod
    def display_download_estimates(videos):
        """
        Estimate and display download details
        
        Args:
            videos (List): List of videos to download
        """
        # Estimated file size (assumes average MP3 size)
        estimated_size_per_video = 5  # MB
        total_estimated_size = len(videos) * estimated_size_per_video

        with st.expander("Download Estimates"):
            st.write(f"Total Videos: {len(videos)}")
            st.write(f"Estimated Total Size: {total_estimated_size} MB")
            st.write("Estimated Download Time: Varies based on connection speed")

    @staticmethod
    def create_download_summary(
        successful_videos, 
        failed_videos
    ):
        """
        Generate comprehensive download summary
        
        Args:
            successful_videos (List): List of successfully downloaded videos
            failed_videos (List): List of failed video downloads
        
        Returns:
            dict: Download summary statistics
        """
        return {
            "total_videos": len(successful_videos) + len(failed_videos),
            "successful_count": len(successful_videos),
            "failed_count": len(failed_videos),
            "success_rate": len(successful_videos) / (len(successful_videos) + len(failed_videos)) * 100,
            "successful_videos": [v.title for v in successful_videos],
            "failed_videos": [v.title for v in failed_videos]
        }