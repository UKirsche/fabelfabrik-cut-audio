# main.py
from audio.audio_controller import AudioController
from audio.audio_gui import AudioGUI
from audio.audio_combiner import AudioCombiner
import audio.text_tools

if __name__ == "__main__":
    combiner = AudioCombiner()
    gui = AudioGUI()
    controller = AudioController(gui, combiner, text_tools=audio.text_tools)
    gui.root.mainloop()