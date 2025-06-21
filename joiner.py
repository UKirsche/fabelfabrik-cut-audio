import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from pydub import AudioSegment
import threading
import os

# ----------- Fachlogik (ohne GUI) ------------
def combine_mp3_files(files, pause_duration_ms=1000):
    pause = AudioSegment.silent(duration=pause_duration_ms)
    combined = AudioSegment.empty()
    for idx, file in enumerate(files):
        audio = AudioSegment.from_mp3(file)
        combined += audio
        if idx < len(files) - 1:
            combined += pause
    return combined

def export_mp3(audio_segment, output_path):
    audio_segment.export(output_path, format="mp3")

# ----------- GUI-Code (nur Oberfläche/Interaktion) ------------

def select_files():
    files = filedialog.askopenfilenames(
        title="MP3 wählen",
        filetypes=[("MP3 Dateien", "*.mp3")]
    )
    if files:
        listbox_files.delete(0, tk.END)
        for file in files:
            listbox_files.insert(tk.END, file)
        # Standard-Ausgabedatei setzen
        entry_output.delete(0, tk.END)
        entry_output.insert(0, os.path.join(os.path.dirname(files[0]), "zusammengefuegt.mp3"))

def save_file():
    filename = filedialog.asksaveasfilename(
        defaultextension=".mp3",
        filetypes=[("MP3 Dateien", "*.mp3")],
        initialfile=entry_output.get()
    )
    if filename:
        entry_output.delete(0, tk.END)
        entry_output.insert(0, filename)

def combine():
    files = listbox_files.get(0, tk.END)
    output_path = entry_output.get()
    if not files:
        messagebox.showwarning("Warnung", "Bitte MP3-Dateien auswählen.")
        return
    if not output_path.endswith('.mp3'):
        messagebox.showwarning("Warnung", "Dateiname muss auf .mp3 enden.")
        return
    btn_combine['state'] = tk.DISABLED
    progress['maximum'] = len(files)
    progress['value'] = 0
    threading.Thread(target=combine_thread, args=(files, output_path)).start()

def combine_thread(files, output_path):
    try:
        pause_ms = 1000
        combined = AudioSegment.empty()
        for idx, file in enumerate(files):
            audio = AudioSegment.from_mp3(file)
            combined += audio
            if idx < len(files) - 1:
                combined += AudioSegment.silent(duration=pause_ms)
            # Fortschritt aktualisieren
            progress['value'] = idx + 1
            root.update_idletasks()
        export_mp3(combined, output_path)
        messagebox.showinfo("Fertig", f"Datei gespeichert: {output_path}")
    except Exception as e:
        messagebox.showerror("Fehler", str(e))
    finally:
        btn_combine['state'] = tk.NORMAL

# ----------- Fenster/Widgets anlegen ------------

root = tk.Tk()
root.title("MP3 Verbinder")

frame = ttk.Frame(root, padding=10)
frame.grid(row=0, column=0, sticky="nsew")

ttk.Label(frame, text="Gewählte MP3-Dateien:").grid(row=0, column=0, sticky="w")
listbox_files = tk.Listbox(frame, width=60, height=8)
listbox_files.grid(row=1, column=0, columnspan=2, sticky="ew")

btn_files = ttk.Button(frame, text="Dateien wählen", command=select_files)
btn_files.grid(row=2, column=0, sticky="w")

ttk.Label(frame, text="Ziel-MP3:").grid(row=3, column=0, sticky="w")
entry_output = ttk.Entry(frame, width=50)
entry_output.grid(row=4, column=0, sticky="ew")
btn_output = ttk.Button(frame, text="Speicherort...", command=save_file)
btn_output.grid(row=4, column=1, sticky="w")

btn_combine = ttk.Button(frame, text="Zusammenfügen & Speichern", command=combine)
btn_combine.grid(row=5, column=0, pady=10, sticky="w")

progress = ttk.Progressbar(frame)
progress.grid(row=6, column=0, columnspan=2, sticky="ew", pady=5)

root.columnconfigure(0, weight=1)
frame.columnconfigure(0, weight=1)

root.mainloop()