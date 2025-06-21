# MP3 Audio Combiner (Tkinter GUI)

Ein einfaches Python-Tool, um mehrere MP3-Dateien zu einer neuen Datei zusammenzufügen.  
Das Programm bietet eine übersichtliche Benutzeroberfläche mit Fortschrittsanzeige und arbeitet nach modernen Software-Prinzipien (Trennung von GUI, Logik und Controller).

---

## Projektstruktur

```
audio_combiner/
├── audio_combiner.py      # Fachlogik (MP3-Dateien zusammenfügen)
├── audio_gui.py           # Benutzeroberfläche (Tkinter)
├── audio_controller.py    # Steuerung & Event-Handling
└── main.py                # Startpunkt des Programms
```

---

## Voraussetzungen

- **Python 3.8+**
- [pydub](https://github.com/jiaaro/pydub)
- [tkinter](https://wiki.python.org/moin/TkInter) (bei Python meist dabei)
- ffmpeg (für pydub, muss installiert sein!)

### Installation von Abhängigkeiten

```bash
pip install pydub
```

**ffmpeg muss auf deinem System installiert und im PATH verfügbar sein:**
- [ffmpeg Download](https://ffmpeg.org/download.html)
- Unter Windows: ffmpeg.exe zu Umgebungsvariablen hinzufügen
- Unter Linux: meist `sudo apt install ffmpeg`

---

## Benutzung

1. **Projekt herunterladen** und entpacken/klonen.
2. **Im Projektordner ausführen:**
    ```bash
    python main.py
    ```
3. **GUI verwenden:**
    - „Dateien wählen“: MP3-Dateien auswählen (Reihenfolge beachten!)
    - Ziel-Datei festlegen
    - „Zusammenfügen & Speichern“ klicken
    - Fortschrittsbalken zeigt den Stand an

---

## Architektur (Clean Code)

- **audio_combiner.py:**  
  Enthält die Fachlogik (MP3 zusammenfügen, speichern). Keine GUI-Abhängigkeit.
- **audio_gui.py:**  
  Erstellt die Benutzeroberfläche, kennt keine Logik.
- **audio_controller.py:**  
  Verbindet GUI mit der Logik, behandelt Events und steuert die Anwendung.
- **main.py:**  
  Startet alles, sorgt für die Verkabelung.

Diese Struktur ermöglicht einfache Wartung, Erweiterung und (bei Bedarf) das Testen der Logik ohne GUI.

---

## Hinweise

- Die Reihenfolge in der Dateiauswahl bestimmt die Abspielreihenfolge im Ergebnis.
- Zwischen den Tracks wird automatisch 1 Sekunde Pause eingefügt (einstellbar im Code).
- Exportiert wird immer als MP3.

---

## Lizenz

MIT License – frei verwendbar.  
Wenn dir das Tool hilft, gerne einen Stern dalassen oder mitentwickeln!
