# audio_combiner.py
from pydub import AudioSegment
AudioSegment.ffmpeg = "ffmpeg"
AudioSegment.ffprobe = "ffprobe"
class AudioCombiner:
    def __init__(self, pause_duration_ms=1000):
        self.pause_duration_ms = pause_duration_ms

    def combine_files(self, files, progress_callback=None):
        pause = AudioSegment.silent(duration=self.pause_duration_ms)
        combined = AudioSegment.empty()
        for idx, file in enumerate(files):
            audio = AudioSegment.from_mp3(file)
            combined += audio
            if idx < len(files) - 1:
                combined += pause
            if progress_callback:
                progress_callback(idx + 1, len(files))
        return combined

    def export(self, combined, output_path):
        combined.export(
            output_path,
            format="mp3",
            bitrate="128k",
            parameters=["-write_xing", "0"]
        )