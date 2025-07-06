import os
import threading
from tkinter import filedialog, messagebox
from .youtube_downloader import (YouTubeDownloader, YouTubeDownloaderError, 
                                 InvalidURLError, NetworkError, PermissionError, 
                                 VideoUnavailableError, FormatError)

class AudioController:
    """Verbindet GUI, Combiner & Text-Tools."""

    def __init__(self, gui, combiner, text_tools):
        self.gui = gui
        self.combiner = combiner
        self.text_tools = text_tools
        self.youtube_downloader = YouTubeDownloader()
        self._connect_events()
        self._connect_youtube_events()

    def _connect_events(self):
        """Bindet Buttons an Funktionen."""
        self.gui.btn_files.config(command=self.select_files)
        self.gui.btn_output.config(command=self.save_file)
        self.gui.btn_combine.config(command=self.combine)
        self.gui.btn_split_text.config(command=self.split_and_save_text)
    
    def _connect_youtube_events(self):
        """Bind YouTube download button"""
        self.gui.btn_youtube_download.config(command=self.download_youtube)

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
                # Schedule GUI updates in main thread
                self.gui.root.after(0, lambda: self._update_progress(current, total))

            combined = self.combiner.combine_files(files, progress_callback=progress_callback)
            self.combiner.export(combined, output_path)
            
            # Schedule success message in main thread
            self.gui.root.after(0, lambda: messagebox.showinfo("Fertig", f"Datei gespeichert: {output_path}"))

        except Exception as e:
            # Schedule error message in main thread
            self.gui.root.after(0, lambda: messagebox.showerror("Fehler", str(e)))
        finally:
            # Schedule button re-enabling in main thread
            self.gui.root.after(0, lambda: setattr(self.gui.btn_combine, 'state', "normal"))

    def _update_progress(self, current, total):
        """Update progress bar in main thread"""
        self.gui.progress['value'] = current
        self.gui.progress['maximum'] = total
        self.gui.root.update_idletasks()

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
    
    # === YOUTUBE DOWNLOAD ===
    def download_youtube(self):
        """Get URL from GUI, validate it, start download in separate thread"""
        url = self.gui.get_youtube_url()
        if not url:
            messagebox.showwarning("Warnung", "Bitte YouTube URL eingeben.")
            return
        
        # Basic URL validation
        if not ("youtube.com" in url or "youtu.be" in url):
            messagebox.showwarning("Warnung", "Bitte eine gültige YouTube URL eingeben.")
            return
        
        # Disable download button and reset progress
        self.gui.btn_youtube_download['state'] = "disabled"
        self.gui.progress_youtube['value'] = 0
        self.gui.set_download_status("Download wird vorbereitet...")
        
        # Start download in separate thread
        threading.Thread(target=self._download_thread, args=(url,)).start()
    
    def _download_thread(self, url):
        """Handle download process, update progress, handle errors"""
        try:
            # Get directory for saving (same as current output directory or user's home)
            output_path = self.gui.entry_output.get()
            if output_path:
                download_dir = os.path.dirname(output_path)
            else:
                download_dir = os.path.expanduser("~")
            
            # Progress callback to update GUI
            def progress_callback(progress_data):
                status = progress_data.get('status', '')
                if status == 'downloading':
                    percent = progress_data.get('percent', 0)
                    self.gui.progress_youtube['value'] = percent
                    filename = os.path.basename(progress_data.get('filename', ''))
                    self.gui.set_download_status(f"Download läuft: {filename} ({percent:.1f}%)")
                elif status == 'finished':
                    self.gui.progress_youtube['value'] = 100
                    self.gui.set_download_status("Download abgeschlossen, konvertiere zu MP3...")
                elif status == 'error':
                    error_msg = progress_data.get('error', 'Unbekannter Fehler')
                    self.gui.set_download_status(f"Fehler: {error_msg}")
                
                # Update GUI in main thread
                self.gui.root.update_idletasks()
            
            # Start download
            downloaded_file = self.youtube_downloader.download(url, download_dir, progress_callback)
            
            # Add downloaded file to listbox
            self.gui.listbox_files.insert("end", downloaded_file)
            
            # Update status
            filename = os.path.basename(downloaded_file)
            self.gui.set_download_status(f"Download erfolgreich: {filename}")
            
            # Show success message
            messagebox.showinfo("Download abgeschlossen", f"Datei heruntergeladen: {filename}")
            
        except InvalidURLError as e:
            self.gui.set_download_status(f"Ungültige URL: {str(e)}")
            messagebox.showerror("Ungültige URL", str(e))
            
        except VideoUnavailableError as e:
            self.gui.set_download_status(f"Video nicht verfügbar: {str(e)}")
            messagebox.showerror("Video nicht verfügbar", str(e))
            
        except NetworkError as e:
            self.gui.set_download_status(f"Netzwerk-Fehler: {str(e)}")
            messagebox.showerror("Netzwerk-Fehler", 
                               f"{str(e)}\n\nBitte überprüfen Sie Ihre Internetverbindung und versuchen Sie es erneut.")
            
        except PermissionError as e:
            self.gui.set_download_status(f"Berechtigung-Fehler: {str(e)}")
            messagebox.showerror("Berechtigung-Fehler", 
                               f"{str(e)}\n\nBitte überprüfen Sie die Ordnerberechtigung oder wählen Sie einen anderen Speicherort.")
            
        except FormatError as e:
            self.gui.set_download_status(f"Format-Fehler: {str(e)}")
            messagebox.showerror("Format-Fehler", str(e))
            
        except YouTubeDownloaderError as e:
            error_msg = str(e)
            self.gui.set_download_status(f"Download-Fehler: {error_msg}")
            messagebox.showerror("Download-Fehler", error_msg)
            
        except Exception as e:
            error_msg = f"Unerwarteter Fehler: {str(e)}"
            self.gui.set_download_status(error_msg)
            messagebox.showerror("Unerwarteter Fehler", 
                               f"{error_msg}\n\nBitte versuchen Sie es erneut oder kontaktieren Sie den Support, wenn das Problem weiterhin besteht.")
            
        finally:
            # Re-enable download button
            self.gui.btn_youtube_download['state'] = "normal"