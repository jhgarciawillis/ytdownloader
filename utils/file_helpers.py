import os
import re
import hashlib
from typing import List, Optional, Tuple
import unicodedata
import zipfile
import shutil

class FileHelper:
    """
    Comprehensive file and path utility class for managing downloads and file operations
    """

    @staticmethod
    def sanitize_filename(filename: str, max_length: int = 255) -> str:
        """
        Thoroughly sanitize filenames to ensure cross-platform compatibility
        
        Args:
            filename (str): Original filename
            max_length (int): Maximum allowed filename length
        
        Returns:
            str: Sanitized filename
        """
        # Normalize Unicode characters
        filename = unicodedata.normalize('NFKD', filename)
        
        # Remove non-ASCII characters and replace with closest ASCII equivalent
        filename = filename.encode('ascii', 'ignore').decode('ascii')
        
        # Replace problematic characters
        filename = re.sub(r'[^\w\-_\. ]', '_', filename)
        
        # Replace multiple spaces with single space
        filename = re.sub(r'\s+', ' ', filename)
        
        # Trim filename
        filename = filename.strip('. ')[:max_length]
        
        # Ensure non-empty filename
        return filename if filename else 'unnamed_file'

    @staticmethod
    def generate_unique_filename(
        base_path: str, 
        filename: str, 
        extension: str = '.mp3'
    ) -> str:
        """
        Generate a unique filename to prevent overwriting
        
        Args:
            base_path (str): Directory to save the file
            filename (str): Base filename
            extension (str): File extension
        
        Returns:
            str: Unique filepath
        """
        # Sanitize filename
        clean_filename = FileHelper.sanitize_filename(filename)
        
        # Full path construction
        filepath = os.path.join(base_path, f"{clean_filename}{extension}")
        
        # Check and modify if file exists
        counter = 1
        while os.path.exists(filepath):
            filepath = os.path.join(
                base_path, 
                f"{clean_filename}_{counter}{extension}"
            )
            counter += 1
        
        return filepath

    @staticmethod
    def create_directory(path: str) -> bool:
        """
        Safely create a directory
        
        Args:
            path (str): Directory path to create
        
        Returns:
            bool: True if directory created or exists, False on error
        """
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except (OSError, PermissionError) as e:
            print(f"Error creating directory {path}: {e}")
            return False

    @staticmethod
    def create_zip_archive(
        source_dir: str, 
        output_path: Optional[str] = None, 
        archive_name: Optional[str] = None
    ) -> Optional[str]:
        """
        Create a zip archive of a directory
        
        Args:
            source_dir (str): Directory to compress
            output_path (Optional[str]): Output directory for zip
            archive_name (Optional[str]): Custom archive name
        
        Returns:
            Optional[str]: Path to created zip file
        """
        if not os.path.exists(source_dir):
            print(f"Source directory {source_dir} does not exist")
            return None
        
        # Determine output path
        output_path = output_path or os.path.dirname(source_dir)
        archive_name = archive_name or f"download_{os.path.basename(source_dir)}"
        
        # Ensure valid filename
        archive_name = FileHelper.sanitize_filename(archive_name)
        
        # Full zip path
        zip_path = os.path.join(output_path, f"{archive_name}.zip")
        
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(source_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, source_dir)
                        zipf.write(file_path, arcname)
            
            return zip_path
        except Exception as e:
            print(f"Error creating zip archive: {e}")
            return None

    @staticmethod
    def calculate_file_hash(filepath: str, algorithm: str = 'md5') -> Optional[str]:
        """
        Calculate hash of a file for integrity checking
        
        Args:
            filepath (str): Path to the file
            algorithm (str): Hash algorithm to use
        
        Returns:
            Optional[str]: File hash or None
        """
        hash_algorithms = {
            'md5': hashlib.md5,
            'sha1': hashlib.sha1,
            'sha256': hashlib.sha256
        }
        
        if algorithm not in hash_algorithms:
            print(f"Unsupported hash algorithm: {algorithm}")
            return None
        
        try:
            hasher = hash_algorithms[algorithm]()
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except IOError as e:
            print(f"Error calculating file hash: {e}")
            return None

    @staticmethod
    def cleanup_temp_files(
        directory: str, 
        max_age_hours: int = 24, 
        file_extensions: List[str] = ['.mp3', '.zip']
    ) -> Tuple[int, int]:
        """
        Clean up temporary files older than specified time
        
        Args:
            directory (str): Directory to clean
            max_age_hours (int): Maximum file age in hours
            file_extensions (List[str]): File types to clean
        
        Returns:
            Tuple[int, int]: (files_checked, files_deleted)
        """
        import time
        
        files_checked = 0
        files_deleted = 0
        current_time = time.time()
        
        for filename in os.listdir(directory):
            if any(filename.endswith(ext) for ext in file_extensions):
                files_checked += 1
                filepath = os.path.join(directory, filename)
                
                # Check file age
                if (current_time - os.path.getmtime(filepath)) > (max_age_hours * 3600):
                    try:
                        os.remove(filepath)
                        files_deleted += 1
                    except Exception as e:
                        print(f"Error deleting {filepath}: {e}")
        
        return files_checked, files_deleted