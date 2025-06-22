import tkinter as tk
from tkinter import ttk

class AudioGUI:
    """Reines GUI‑Objekt, keine Logik!"""
    DEFAULT_OUTPUT_FILENAME = "zusammengefuegt.mp3"

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MP3 & ElevenLabs Tool")
        self._build_ui()

    def _build_ui(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.grid(row=0, column=0, sticky="nsew")

        # === AUDIO-BEREICH ===
        ttk.Label(frame, text="Audio", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(frame, text="Gewählte MP3-Dateien:").grid(row=1, column=0, sticky="w")
        self.listbox_files = tk.Listbox(frame, width=60, height=8)
        self.listbox_files.grid(row=2, column=0, columnspan=2, sticky="ew")
        self.btn_files = ttk.Button(frame, text="Dateien wählen")
        self.btn_files.grid(row=3, column=0, sticky="w")
        ttk.Label(frame, text="Ziel-MP3:").grid(row=4, column=0, sticky="w")
        self.entry_output = ttk.Entry(frame, width=50)
        self.entry_output.grid(row=5, column=0, sticky="ew")
        self.btn_output = ttk.Button(frame, text="Speicherort...")
        self.btn_output.grid(row=5, column=1, sticky="w")
        self.btn_combine = ttk.Button(frame, text="Zusammenfügen & Speichern")
        self.btn_combine.grid(row=6, column=0, pady=10, sticky="w")
        self.progress = ttk.Progressbar(frame)
        self.progress.grid(row=7, column=0, columnspan=2, sticky="ew", pady=5)

        # Separator + Überschrift Textbereich
        ttk.Separator(frame, orient='horizontal').grid(row=8, column=0, columnspan=2, sticky="ew", pady=15)
        ttk.Label(frame, text="Text", font=("Arial", 12, "bold")).grid(row=9, column=0, sticky="w", pady=(0,5))

        # === TEXT-BEREICH ===
        self.text_input = tk.Text(frame, height=20, wrap="word")
        self.text_input.grid(row=10, column=0, columnspan=2, sticky="nsew")
        self.btn_split_text = ttk.Button(frame, text="Text teilen & speichern")
        self.btn_split_text.grid(row=11, column=0, sticky="w", pady=(5, 0))

        # Layout-Konfiguration
        self.root.columnconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(10, weight=1)