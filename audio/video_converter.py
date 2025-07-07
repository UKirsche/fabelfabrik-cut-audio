import os
import re
import subprocess
from typing import Optional, Callable, Dict, Any
from pathlib import Path


class VideoConverterError(Exception):
    """Custom exception for video converter errors"""
    pass


class InputFileError(VideoConverterError):
    """Exception for invalid input file errors"""
    pass


class OutputFileError(VideoConverterError):
    """Exception for output file errors"""
    pass


class ConversionError(VideoConverterError):
    """Exception for conversion process errors"""
    pass


class PermissionError(VideoConverterError):
    """Exception for file system permission issues"""
    pass


class VideoConverter:
    """Handles conversion of MP4 videos to animated GIFs"""

    # Available resolutions for GIF output - now width-based with auto height
    RESOLUTIONS = {
        "240p": "320",
        "360p": "480", 
        "480p": "640",
        "720p": "1280",
        "Original": "original"
    }

    def __init__(self):
        """Initialize the video converter"""
        self._check_ffmpeg_available()

    def _check_ffmpeg_available(self):
        """Check if FFmpeg is available on the system"""
        try:
            subprocess.run(
                ["ffmpeg", "-version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
        except (subprocess.SubprocessError, FileNotFoundError):
            raise VideoConverterError(
                "FFmpeg is not available. Please install FFmpeg to use video conversion features."
            )

    def convert_to_gif(
        self,
        input_file: str,
        output_dir: str,
        resolution: str = "480p",
        fps: int = 10,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> str:
        """
        Convert MP4 video to animated GIF

        Args:
            input_file: Path to input MP4 file
            output_dir: Directory to save the output GIF
            resolution: Resolution for the output GIF (from RESOLUTIONS)
            fps: Frames per second for the output GIF
            progress_callback: Optional callback function to report conversion progress

        Returns:
            str: Path to the output GIF file

        Raises:
            InputFileError: If input file is invalid
            OutputFileError: If output directory is invalid
            PermissionError: If file system permissions are insufficient
            ConversionError: If conversion fails
        """
        # Validate input and output
        self._validate_input_file(input_file)
        self._validate_output_dir(output_dir)

        # Validate resolution
        if resolution not in self.RESOLUTIONS:
            raise ConversionError(f"Invalid resolution: {resolution}. Valid options: {', '.join(self.RESOLUTIONS.keys())}")

        # Create output filename
        input_path = Path(input_file)
        output_filename = f"{input_path.stem}.gif"
        output_path = os.path.join(output_dir, output_filename)

        # Prepare FFmpeg command
        ffmpeg_cmd = self._prepare_ffmpeg_command(input_file, output_path, resolution, fps)

        try:
            # Run FFmpeg with progress monitoring
            self._run_ffmpeg_with_progress(ffmpeg_cmd, input_file, progress_callback)

            # Verify output file exists
            if not os.path.exists(output_path):
                raise ConversionError("Conversion failed: Output file was not created")

            return output_path

        except subprocess.SubprocessError as e:
            raise ConversionError(f"FFmpeg conversion failed: {str(e)}")
        except Exception as e:
            if isinstance(e, VideoConverterError):
                raise
            raise ConversionError(f"Unexpected error during conversion: {str(e)}")

    def _prepare_ffmpeg_command(self, input_file: str, output_path: str, resolution: str, fps: int) -> list:
        """Prepare FFmpeg command for conversion"""
        cmd = [
            "ffmpeg",
            "-y",  # ← WICHTIG: Automatisches Überschreiben ohne Nachfrage!
            "-i", input_file
        ]

        # Add resolution filter if not original
        if resolution != "Original":
            # Use width-based scaling with automatic height calculation
            target_width = self.RESOLUTIONS[resolution]
            # Scale to specific width, height will be calculated automatically to maintain aspect ratio
            cmd.extend(["-vf", f"scale={target_width}:-1:flags=lanczos"])

        # Set framerate
        cmd.extend(["-r", str(fps)])

        # Output options for GIF
        cmd.extend([
            "-f", "gif",
            output_path
        ])

        return cmd

    def _run_ffmpeg_with_progress(
        self,
        cmd: list,
        input_file: str,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ):
        """Run FFmpeg command with progress monitoring"""
        # Get video duration for progress calculation
        duration = self._get_video_duration(input_file)

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1
        )

        # Process FFmpeg output to track progress
        for line in process.stderr:
            if "time=" in line and progress_callback and duration:
                # Extract time information
                time_match = re.search(r"time=(\d+):(\d+):(\d+\.\d+)", line)
                if time_match:
                    h, m, s = map(float, time_match.groups())
                    current_time = h * 3600 + m * 60 + s
                    progress = min(100, (current_time / duration) * 100)

                    # Call progress callback
                    progress_callback({
                        "status": "converting",
                        "percent": progress,
                        "filename": os.path.basename(input_file)
                    })

        # Wait for process to complete
        process.wait()

        # Check if conversion was successful
        if process.returncode != 0:
            stderr = process.stderr.read() if process.stderr else "Unknown error"
            raise ConversionError(f"FFmpeg conversion failed with code {process.returncode}: {stderr}")

        # Final progress update
        if progress_callback:
            progress_callback({
                "status": "finished",
                "percent": 100,
                "filename": os.path.basename(input_file)
            })

    def _get_video_duration(self, input_file: str) -> float:
        """Get video duration in seconds for progress calculation"""
        try:
            cmd = [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                input_file
            ]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            return float(result.stdout.strip())
        except (subprocess.SubprocessError, ValueError):
            # If duration can't be determined, return None
            return None

    def _validate_input_file(self, input_file: str):
        """Validate input file exists and is a valid MP4"""
        if not input_file:
            raise InputFileError("Input file path cannot be empty")

        if not os.path.exists(input_file):
            raise InputFileError(f"Input file does not exist: {input_file}")

        if not os.path.isfile(input_file):
            raise InputFileError(f"Input path is not a file: {input_file}")

        # Check file extension
        if not input_file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            raise InputFileError(f"Input file must be a video file (MP4, AVI, MOV, MKV): {input_file}")

        # Check if file is readable
        if not os.access(input_file, os.R_OK):
            raise PermissionError(f"No read permission for input file: {input_file}")

    def _validate_output_dir(self, output_dir: str):
        """Validate output directory exists and is writable"""
        if not output_dir:
            raise OutputFileError("Output directory path cannot be empty")

        # Create directory if it doesn't exist
        try:
            os.makedirs(output_dir, exist_ok=True)
        except OSError as e:
            raise PermissionError(f"Cannot create output directory: {str(e)}")

        # Check if directory is writable
        if not os.access(output_dir, os.W_OK):
            raise PermissionError(f"No write permission for output directory: {output_dir}")