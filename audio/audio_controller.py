import os
import threading
from tkinter import filedialog, messagebox

class AudioController:
    """Verbindet GUI, Combiner & Text-Tools."""

    def __init__(self, gui, combiner, text_tools):
        self.gui = gui
        self.combiner = combiner
        self.text_tools = text_tools
        self._connect_events()

    def _connect_events(self):
        """Bindet Buttons an Funktionen."""
        self.gui.btn_files.config(command=self.select_files)
        self.gui.btn_output.config(command=self.save_file)
        self.gui.btn_combine.config(command=self.combine)
        self.gui.btn_split_text.config(command=self.split_and_save_text)

    # === MP3 COMBINE ===
    def select_files(self):
        files = filedialog.askopenfilenames(
            title="MP3 wählen",
            filetypes=[("MP3 Dateien", "*.mp3")]
        )
        if files:
            self.gui.listbox_files.delete(0, "end")
            for file in files:
                self.gui.listbox_files.insert("end", file)
            self.gui.entry_output.delete(0, "end")
            self.gui.entry_output.insert(
                0, os.path.join(os.path.dirname(files[0]), self.gui.DEFAULT_OUTPUT_FILENAME)
            )

    def save_file(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".mp3",
            filetypes=[("MP3 Dateien", "*.mp3")],
            initialfile=self.gui.entry_output.get()
        )
        if filename:
            self.gui.entry_output.delete(0, "end")
            self.gui.entry_output.insert(0, filename)

    def combine(self):
        files = self.gui.listbox_files.get(0, "end")
        output_path = self.gui.entry_output.get()
        if not files:
            messagebox.showwarning("Warnung", "Bitte MP3-Dateien auswählen.")
            return
        if not output_path.endswith('.mp3'):
            messagebox.showwarning("Warnung", "Dateiname muss auf .mp3 enden.")
            return
        self.gui.btn_combine['state'] = "disabled"
        self.gui.progress['maximum'] = len(files)
        self.gui.progress['value'] = 0

        threading.Thread(target=self._combine_thread, args=(files, output_path)).start()

    def _combine_thread(self, files, output_path):
        try:
            def progress_callback(current, total):
                self.gui.progress['value'] = current
                self.gui.progress['maximum'] = total
                self.gui.root.update_idletasks()

            combined = self.combiner.combine_files(files, progress_callback=progress_callback)
            self.combiner.export(combined, output_path)
            messagebox.showinfo("Fertig", f"Datei gespeichert: {output_path}")

        except Exception as e:
            messagebox.showerror("Fehler", str(e))
        finally:
            self.gui.btn_combine['state'] = "normal"

    # === TEXT SPLIT ===
    def split_and_save_text(self):
        text = self.gui.text_input.get("1.0", "end").strip()
        if not text:
            messagebox.showwarning("Warnung", "Bitte Text eingeben.")
            return

        output_dir = filedialog.askdirectory(title="Ordner wählen für Chunks")
        if output_dir:
            self.text_tools.save_chunks_to_files(text, output_dir)
            messagebox.showinfo("Erfolg", f"Chunks gespeichert: {output_dir}")