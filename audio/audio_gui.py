# audio_gui.py
import tkinter as tk
from tkinter import ttk

class AudioGUI:
    """Reines GUI-Objekt, keine Logik!"""
    DEFAULT_OUTPUT_FILENAME = "zusammengefuegt.mp3"

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MP3 Verbinder")
        self._build_ui()

    def _build_ui(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.grid(row=0, column=0, sticky="nsew")

        ttk.Label(frame, text="Gewählte MP3-Dateien:").grid(row=0, column=0, sticky="w")
        self.listbox_files = tk.Listbox(frame, width=60, height=8)
        self.listbox_files.grid(row=1, column=0, columnspan=2, sticky="ew")

        self.btn_files = ttk.Button(frame, text="Dateien wählen")
        self.btn_files.grid(row=2, column=0, sticky="w")

        ttk.Label(frame, text="Ziel-MP3:").grid(row=3, column=0, sticky="w")
        self.entry_output = ttk.Entry(frame, width=50)
        self.entry_output.grid(row=4, column=0, sticky="ew")
        self.btn_output = ttk.Button(frame, text="Speicherort...")
        self.btn_output.grid(row=4, column=1, sticky="w")

        self.btn_combine = ttk.Button(frame, text="Zusammenfügen & Speichern")
        self.btn_combine.grid(row=5, column=0, pady=10, sticky="w")

        self.progress = ttk.Progressbar(frame)
        self.progress.grid(row=6, column=0, columnspan=2, sticky="ew", pady=5)

        self.root.columnconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)