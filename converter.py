# main.py
from audio.audio_controller import AudioController
from audio.audio_gui import AudioGUI
from audio.audio_combiner import AudioCombiner

if __name__ == "__main__":
    combiner = AudioCombiner()
    gui = AudioGUI()
    controller = AudioController(gui, combiner)
    gui.root.mainloop()