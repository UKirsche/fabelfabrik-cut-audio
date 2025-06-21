import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from pydub import AudioSegment
import threading
import os

class MP3CombinerApp:
    PAUSE_DURATION_MS = 1000
    DEFAULT_OUTPUT_FILENAME = "zusammengefuegt.mp3"

    def __init__(self):
        self._setup_ui()

    def _setup_ui(self):
        self.root = tk.Tk()
        self.root.title("MP3 Verbinder")

        # Hauptframe für den Inhalt
        self.frame = ttk.Frame(self.root, padding=10)
        self.frame.grid(row=0, column=0, sticky="nsew")

        # Statusbalken-Frame am unteren Rand
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))

        self._create_file_selection_widgets()
        self._create_output_widgets()
        self._create_combine_button()
        self._create_progress_widgets()
        self._configure_layout()

    def _create_file_selection_widgets(self):
        ttk.Label(self.frame, text="Gewählte MP3-Dateien:").grid(row=0, column=0, sticky="w")

        self.listbox_files = tk.Listbox(self.frame, width=60, height=8)
        self.listbox_files.grid(row=1, column=0, columnspan=3, sticky="ew")

        self.btn_files = ttk.Button(self.frame, text="Dateien wählen", command=self._select_files)
        self.btn_files.grid(row=2, column=0, sticky="w")

    def _create_output_widgets(self):
        ttk.Label(self.frame, text="Ziel-MP3:").grid(row=3, column=0, sticky="w")

        self.entry_output = ttk.Entry(self.frame, width=50)
        self.entry_output.grid(row=4, column=0, sticky="ew")

        self.btn_output = ttk.Button(self.frame, text="Speicherort...", command=self._save_file)
        self.btn_output.grid(row=4, column=1, sticky="w")

    def _create_combine_button(self):
        self.btn_combine = ttk.Button(self.frame, text="Zusammenfügen & Speichern", command=self._combine)
        self.btn_combine.grid(row=5, column=0, pady=10, sticky="w")

    def _create_progress_widgets(self):
        self.progress = ttk.Progressbar(self.status_frame)
        self.progress.grid(row=0, column=0, sticky="ew")

    def _configure_layout(self):
        # Hauptfenster konfigurieren
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Hauptframe konfigurieren
        self.frame.columnconfigure(0, weight=1)

        # Statusframe konfigurieren
        self.status_frame.columnconfigure(0, weight=1)

    def _select_files(self):
        files = filedialog.askopenfilenames(
            title="Wähle MP3-Dateien",
            filetypes=[("MP3 Dateien", "*.mp3")]
        )
        if files:
            self._update_file_list(files)
            self._set_default_output_path(files[0])

    def _update_file_list(self, files):
        self.listbox_files.delete(0, tk.END)
        for file in files:
            self.listbox_files.insert(tk.END, file)

    def _set_default_output_path(self, first_file):
        default_output = os.path.join(
            os.path.dirname(first_file),
            self.DEFAULT_OUTPUT_FILENAME
        )
        self.entry_output.delete(0, tk.END)
        self.entry_output.insert(0, default_output)

    def _save_file(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".mp3",
            filetypes=[("MP3 Dateien", "*.mp3")],
            initialfile=self.entry_output.get()
        )
        if filename:
            self.entry_output.delete(0, tk.END)
            self.entry_output.insert(0, filename)

    def _combine(self):
        files = self.listbox_files.get(0, tk.END)
        output_path = self.entry_output.get()

        if not self._validate_input(files, output_path):
            return

        threading.Thread(target=self._combine_audio_files, args=(files, output_path)).start()

    def _validate_input(self, files, output_path):
        if not files:
            messagebox.showwarning("Warnung", "Bitte MP3-Dateien auswählen.")
            return False

        if not output_path.endswith('.mp3'):
            messagebox.showwarning("Warnung", "Dateiname muss auf .mp3 enden.")
            return False

        return True

    def _combine_audio_files(self, files, output_path):
        self._set_combining_state(True)
        self._setup_progress(len(files))

        try:
            combined_audio = self._process_files(files)
            self._export_audio(combined_audio, output_path)
            messagebox.showinfo("Fertig", f"Datei gespeichert: {output_path}")
        except Exception as e:
            messagebox.showerror("Fehler", f"Export fehlgeschlagen: {e}")
        finally:
            self._set_combining_state(False)

    def _set_combining_state(self, is_combining):
        state = tk.DISABLED if is_combining else tk.NORMAL
        self.btn_combine['state'] = state

    def _setup_progress(self, total_files):
        self.progress['maximum'] = total_files
        self.progress['value'] = 0

    def _process_files(self, files):
        pause = AudioSegment.silent(duration=self.PAUSE_DURATION_MS)
        combined = AudioSegment.empty()

        for idx, file in enumerate(files):
            audio = AudioSegment.from_mp3(file)
            combined += audio

            if idx < len(files) - 1:
                combined += pause

            self._update_progress()

        return combined

    def _update_progress(self):
        self.progress['value'] += 1
        self.root.update_idletasks()

    def _export_audio(self, combined_audio, output_path):
        combined_audio.export(output_path, format="mp3")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = MP3CombinerApp()
    app.run()