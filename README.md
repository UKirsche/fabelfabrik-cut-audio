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
├── youtube_downloader.py  # YouTube Download Funktionalität
├── text_tools.py          # Text-Tools für Chunking
└── main.py                # Startpunkt des Programms
```

---

## Voraussetzungen

- **Python 3.8+**
- [pydub](https://github.com/jiaaro/pydub)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) (für YouTube Downloads)
- [tkinter](https://wiki.python.org/moin/TkInter) (bei Python meist dabei)
- ffmpeg (für pydub, muss installiert sein!)

### Installation von Abhängigkeiten

```bash
pip install pydub yt-dlp
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

## YouTube Downloader Benutzung

1. **YouTube-URL eingeben:**
    - Geben Sie die vollständige YouTube-URL im GUI-Feld ein.
    - Unterstützte Formate: youtube.com/watch?v=..., youtu.be/..., youtube.com/embed/..., youtube.com/shorts/...
2. **Download Button:**
    - Drücken Sie den „Download" Button, um das Herunterladen zu starten.
3. **Download Fortschritt:**
    - Der Fortschrittsbalken zeigt den aktuellen Fortschritt an.
    - Status-Nachrichten informieren über den aktuellen Download-Status.
4. **Erfolgsnachricht:**
    - Nach dem Herunterladen und Konvertieren wird eine Erfolgsnachricht angezeigt.
    - Die heruntergeladene Datei wird automatisch zur Liste der MP3-Dateien hinzugefügt.

### YouTube Konfigurationsoptionen

- **Audio-Qualität:** Standard 192 kbps, konfigurierbar über Code
- **Audio-Format:** Standard MP3, weitere Formate (WAV, FLAC, AAC, M4A, OGG) unterstützt
- **Netzwerk-Timeout:** 30 Sekunden für Socket-Operationen
- **Retry-Versuche:** 3 automatische Wiederholungsversuche bei fehlgeschlagenen Downloads

### Fehlerbehandlung

Der YouTube Downloader bietet umfassendes Error Handling für:
- **Ungültige URLs:** Prüfung auf gültige YouTube-URL-Formate
- **Netzwerk-Probleme:** Verbindungsprüfung und Timeout-Behandlung
- **Video-Verfügbarkeit:** Private Videos, geografische Beschränkungen, gelöschte Videos
- **Live-Streams:** Ongoing Live-Streams können nicht heruntergeladen werden
- **Audio-Formate:** Überprüfung auf verfügbare Audio-Streams
- **Dateisystem-Berechtigungen:** Schreibrechte für Ausgabeordner

---

## Architektur (Clean Code)

- **audio_combiner.py:**  
  Enthält die Fachlogik (MP3 zusammenfügen, speichern). Keine GUI-Abhängigkeit.
- **audio_gui.py:**  
  Erstellt die Benutzeroberfläche, kennt keine Logik.
- **audio_controller.py:**  
  Verbindet GUI mit der Logik, behandelt Events und steuert die Anwendung.
- **youtube_downloader.py:**  
  Implementiert YouTube Download-Funktionalität mit umfassendem Error Handling, URL-Validierung und Fortschritts-Callbacks.
- **text_tools.py:**  
  Bietet Text-Splitting und Chunking-Funktionalitäten.
- **main.py:**  
  Startet alles, sorgt für die Verkabelung.

Diese Struktur ermöglicht einfache Wartung, Erweiterung und (bei Bedarf) das Testen der Logik ohne GUI.

---

## Tests

Das Projekt enthält umfassende Tests für die YouTube-Download-Funktionalität:

### Test-Ausführung

```bash
# Alle Tests ausführen
python run_tests.py

# Nur Unit Tests
python run_tests.py unit

# Nur Integration Tests
python run_tests.py integration

# Einzelne Test-Dateien
python -m pytest tests/test_youtube_downloader.py -v
python -m pytest tests/test_integration.py -v
```

### Test-Kategorien

- **Unit Tests** (`tests/test_youtube_downloader.py`):
  - URL-Validierung
  - Netzwerk-Konnektivitätsprüfung
  - Ausgabepfad-Validierung
  - Video-Info-Validierung
  - Audio-Verfügbarkeitsprüfung
  - Fehlerbehandlung
  - Progress-Callback-Funktionalität

- **Integration Tests** (`tests/test_integration.py`):
  - Kompletter Download-Workflow
  - Mocked YouTube-Responses
  - Fehlerfortpflanzung zwischen Komponenten
  - Konfigurationsintegration
  - Dateisystem-Integration

---

## Hinweise

- Die Reihenfolge in der Dateiauswahl bestimmt die Abspielreihenfolge im Ergebnis.
- Zwischen den Tracks wird automatisch 1 Sekunde Pause eingefügt (einstellbar im Code).
- Exportiert wird immer als MP3.

---

## Lizenz

MIT License – frei verwendbar.  
Wenn dir das Tool hilft, gerne einen Stern dalassen oder mitentwickeln!
