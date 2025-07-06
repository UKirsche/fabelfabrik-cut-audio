# main.py
import sys, os

# Laufzeit-Hack für PyInstaller: sicherstellen, dass ffmpeg/ffprobe im PATH sind
if getattr(sys, "frozen", False):
    base = sys._MEIPASS
else:
    base = os.getcwd()
os.environ["PATH"] += os.pathsep + base

from audio.audio_controller import AudioController
from audio.audio_gui import AudioGUI
from audio.audio_combiner import AudioCombiner
from audio.youtube_downloader import YouTubeDownloader
import audio.text_tools

if __name__ == "__main__":
    combiner = AudioCombiner()
    gui = AudioGUI()
    controller = AudioController(
        gui, 
        combiner, 
        audio.text_tools
    )
    gui.root.mainloop()
