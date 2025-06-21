# audio_controller.py
import os
import threading
from tkinter import filedialog, messagebox
from pydub import AudioSegment  # Nur für Fortschritt/Update

class AudioController:
    """Verbindet GUI und Fachlogik, steuert Events."""
    def __init__(self, gui, combiner):
        self.gui = gui
        self.combiner = combiner
        self._connect_events()

    def _connect_events(self):
        """
        Verbindet UI-Elemente mit ihren Event-Handler-Methoden.
        
        Diese Methode implementiert das Event-Binding-Pattern und stellt die
        Verbindung zwischen GUI-Komponenten und der Geschäftslogik her.
        
        Event-Bindings:
        - btn_files: Öffnet Dateiauswahl-Dialog (select_files)
        - btn_output: Öffnet Speichern-Dialog (save_file) 
        - btn_combine: Startet MP3-Zusammenfügung (combine)
        
        Vorteile dieser Struktur:
        - Zentrale Verwaltung aller Event-Bindings
        - Klare Trennung von UI-Erstellung und Event-Handling
        - Bessere Wartbarkeit und Übersichtlichkeit
        - Einfaches Hinzufügen neuer Events
        """
        self.gui.btn_files.config(command=self.select_files)
        self.gui.btn_output.config(command=self.save_file)
        self.gui.btn_combine.config(command=self.combine)

    def select_files(self):
        files = filedialog.askopenfilenames(
            title="MP3 wählen",
            filetypes=[("MP3 Dateien", "*.mp3")]
        )
        if files:
            self.gui.listbox_files.delete(0, "end")
            for file in files:
                self.gui.listbox_files.insert("end", file)
            # Standard-Ausgabedatei setzen
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

        #für den Status unten!
        threading.Thread(target=self._combine_thread, args=(files, output_path)).start()

    def _combine_thread(self, files, output_path):
        """
        Thread-Worker-Methode für die asynchrone MP3-Dateien-Kombinierung.
        
        Diese Methode läuft in einem separaten Thread, um die GUI während der
        Audio-Verarbeitung nicht zu blockieren. Sie koordiniert den gesamten
        Kombinierungsprozess und stellt sicher, dass die UI responsiv bleibt.
        
        Args:
            files (list): Liste der zu kombinierenden MP3-Dateipfade
            output_path (str): Pfad für die resultierende Ausgabedatei
        
        Threading-Pattern:
        - Läuft in separatem Thread (nicht im GUI-Thread)
        - Verwendet Callback für UI-Updates
        - Stellt GUI-Zustand nach Abschluss wieder her
        
        Fehlerbehandlung:
        - Try-Catch für alle Verarbeitungsfehler
        - Finally-Block garantiert GUI-Wiederherstellung
        - Benutzerfreundliche Fehlermeldungen
        """
        try:
            # Callback-Methode wird übergeben an Combiner für Status-Updates
            # Ermöglicht Echzeit-Fortschrittsanzeige während der Verarbeitung
            def progress_callback(current, total):
                self.gui.progress['value'] = current
                self.gui.progress['maximum'] = total
                self.gui.root.update_idletasks()  # Erzwingt sofortige UI-Aktualisierung

            # Hauptverarbeitung: Dateien kombinieren mit Fortschritts-Callback
            combined = self.combiner.combine_files(files, progress_callback=progress_callback)
            
            # Resultat als MP3-Datei exportieren
            self.combiner.export(combined, output_path)
            
            # Erfolgsmeldung anzeigen
            messagebox.showinfo("Fertig", f"Datei gespeichert: {output_path}")
            
        except Exception as e:
            # Alle Fehler abfangen und benutzerfreundlich anzeigen
            messagebox.showerror("Fehler", str(e))
            
        finally:
            # GUI-Zustand wiederherstellen (Button wieder aktivieren)
            # Wird IMMER ausgeführt, auch bei Fehlern
            self.gui.btn_combine['state'] = "normal"