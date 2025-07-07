import tkinter as tk
from tkinter import ttk

class AudioGUI:
    """Reines GUI‑Objekt, keine Logik!"""
    DEFAULT_OUTPUT_FILENAME = "zusammengefuegt.mp3"
    DEFAULT_CHUNK_LENGTH = "2500"
    DEFAULT_GIF_RESOLUTION = "480p"

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MP3, Video & ElevenLabs Tool")

        # Get screen dimensions and calculate appropriate window size
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # For MacBook Air 13" (1440x900) and similar small screens, use more conservative sizing
        if screen_height <= 900:  # MacBook Air or similar
            window_width = min(800, int(screen_width * 0.75))
            window_height = min(650, int(screen_height * 0.70))  # Even smaller height for better fit
        else:
            window_width = min(900, int(screen_width * 0.8))
            window_height = min(800, int(screen_height * 0.85))

        # Calculate position to center the window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        # Set window size and position
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Set minimum size (smaller for better compatibility with small screens)
        self.root.minsize(550, 400)

        self._setup_scrollable_ui()

    def _setup_scrollable_ui(self):
        """Setup a scrollable UI for better compatibility with small screens"""
        # Main canvas and scrollbar setup
        self.canvas = tk.Canvas(self.root)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Layout canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Enable mouse wheel scrolling
        self._bind_mouse_wheel()

        # Build the actual UI content
        self._build_ui()

    def _bind_mouse_wheel(self):
        """Bind mouse wheel events for scrolling"""
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        # Bind to canvas and main window
        self.canvas.bind("<MouseWheel>", _on_mousewheel)  # Windows
        self.canvas.bind("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))  # Linux
        self.canvas.bind("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))  # Linux

    def _build_ui(self):
        # Get screen height for UI adjustments
        screen_height = self.root.winfo_screenheight()

        frame = ttk.Frame(self.scrollable_frame, padding=10)
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
        ttk.Label(frame, text="Text to Chunks", font=("Arial", 12, "bold")).grid(row=9, column=0, sticky="w", pady=(0,5))

        # === TEXT-BEREICH ===
        # Reduce text area height on smaller screens to ensure YouTube section is visible
        text_height = 15 if screen_height <= 900 else 20
        self.text_input = tk.Text(frame, height=text_height, wrap="word")
        self.text_input.grid(row=10, column=0, columnspan=2, sticky="nsew")

        # Chunk-Länge Eingabefeld
        chunk_frame = ttk.Frame(frame)
        chunk_frame.grid(row=11, column=0, columnspan=2, sticky="ew", pady=(5, 0))
        ttk.Label(chunk_frame, text="Chunk-Länge (Zeichen):").grid(row=0, column=0, sticky="w")
        self.entry_chunk_length = ttk.Entry(chunk_frame, width=10)
        self.entry_chunk_length.insert(0, self.DEFAULT_CHUNK_LENGTH)
        self.entry_chunk_length.grid(row=0, column=1, sticky="w", padx=(5, 0))

        self.btn_split_text = ttk.Button(chunk_frame, text="Text teilen & speichern")
        self.btn_split_text.grid(row=0, column=2, sticky="w", padx=(20, 0))

        # Separator + Überschrift YouTube-Bereich
        ttk.Separator(frame, orient='horizontal').grid(row=12, column=0, columnspan=2, sticky="ew", pady=15)
        ttk.Label(frame, text="YouTube Download", font=("Arial", 12, "bold")).grid(row=13, column=0, sticky="w", pady=(0,5))

        # === YOUTUBE-BEREICH ===
        self._build_youtube_section(frame)

        # Separator + Überschrift Video-Bereich
        ttk.Separator(frame, orient='horizontal').grid(row=18, column=0, columnspan=2, sticky="ew", pady=15)
        ttk.Label(frame, text="Video", font=("Arial", 12, "bold")).grid(row=19, column=0, sticky="w", pady=(0,5))

        # === VIDEO-BEREICH ===
        self._build_video_section(frame)

        # Layout-Konfiguration
        self.scrollable_frame.columnconfigure(0, weight=1)
        self.scrollable_frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(10, weight=1)  # Text area should expand

    def _build_youtube_section(self, frame):
        """Create and layout YouTube download UI elements"""
        # URL input field
        ttk.Label(frame, text="YouTube URL:").grid(row=14, column=0, sticky="w")
        self.entry_youtube_url = ttk.Entry(frame, width=50)
        self.entry_youtube_url.grid(row=15, column=0, sticky="ew")

        # Download button
        self.btn_youtube_download = ttk.Button(frame, text="Download")
        self.btn_youtube_download.grid(row=15, column=1, sticky="w", padx=(5, 0))

        # Progress bar
        self.progress_youtube = ttk.Progressbar(frame)
        self.progress_youtube.grid(row=16, column=0, columnspan=2, sticky="ew", pady=5)

        # Status label
        self.label_youtube_status = ttk.Label(frame, text="")
        self.label_youtube_status.grid(row=17, column=0, columnspan=2, sticky="w")

    def _build_video_section(self, frame):
        """Create and layout Video to GIF conversion UI elements"""
        # File selection
        ttk.Label(frame, text="Mp4 to Gif", font=("Arial", 12, "bold")).grid(row=19, column=0, sticky="w", pady=(0,5))
        ttk.Label(frame, text="MP4-Datei:").grid(row=20, column=0, sticky="w")
        self.entry_video_file = ttk.Entry(frame, width=50)
        self.entry_video_file.grid(row=20, column=0, sticky="ew")
        self.btn_video_file = ttk.Button(frame, text="Datei wählen")
        self.btn_video_file.grid(row=20, column=1, sticky="w", padx=(5, 0))

        # Resolution selection
        resolution_frame = ttk.Frame(frame)
        resolution_frame.grid(row=21, column=0, columnspan=2, sticky="ew", pady=(5, 0))
        ttk.Label(resolution_frame, text="GIF-Auflösung:").grid(row=0, column=0, sticky="w")

        # Create resolution dropdown
        self.resolution_var = tk.StringVar(value=self.DEFAULT_GIF_RESOLUTION)
        resolutions = ["240p", "360p", "480p", "720p", "Original"]
        self.resolution_dropdown = ttk.Combobox(resolution_frame, textvariable=self.resolution_var, values=resolutions, width=10, state="readonly")
        self.resolution_dropdown.grid(row=0, column=1, sticky="w", padx=(5, 0))

        # Convert button
        self.btn_convert_gif = ttk.Button(resolution_frame, text="Zu GIF konvertieren")
        self.btn_convert_gif.grid(row=0, column=2, sticky="w", padx=(20, 0))

        # Progress bar
        self.progress_video = ttk.Progressbar(frame)
        self.progress_video.grid(row=22, column=0, columnspan=2, sticky="ew", pady=5)

        # Status label
        self.label_video_status = ttk.Label(frame, text="")
        self.label_video_status.grid(row=23, column=0, columnspan=2, sticky="w")

    def get_youtube_url(self):
        """Return URL from input field"""
        return self.entry_youtube_url.get().strip()

    def set_download_status(self, status):
        """Update status label"""
        self.label_youtube_status.config(text=status)

    def get_chunk_length(self) -> int:
        """Gibt die vom Benutzer eingegebene Chunk-Länge zurück."""
        try:
            value = int(self.entry_chunk_length.get())
            return max(100, value)  # Mindestens 100 Zeichen
        except ValueError:
            return int(self.DEFAULT_CHUNK_LENGTH)

    def get_video_file(self) -> str:
        """Return the selected video file path"""
        return self.entry_video_file.get().strip()

    def set_video_file(self, file_path: str):
        """Set the video file path in the entry field"""
        self.entry_video_file.delete(0, "end")
        self.entry_video_file.insert(0, file_path)

    def get_gif_resolution(self) -> str:
        """Return the selected GIF resolution"""
        return self.resolution_var.get()

    def set_video_status(self, status: str):
        """Update video conversion status label"""
        self.label_video_status.config(text=status)
