#!/usr/bin/env python3
"""
Build-Script für macOS App-Bundle
"""
import os
import subprocess
import shutil

def build_app():
    """Erstellt die macOS App"""

    print("🚀 Starte Build-Prozess für macOS...")

    # Alte Builds löschen
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")

    # PyInstaller-Befehl
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", "MP3 Combiner",
        "--add-data", "audio:audio",
        "--clean",
        "converter.py"
    ]

    try:
        subprocess.run(cmd, check=True)
        print("✅ Build erfolgreich!")
        print("📦 App erstellt in: dist/MP3 Combiner.app")

        # App-Info anzeigen
        app_path = "dist/MP3 Combiner.app"
        if os.path.exists(app_path):
            size = get_folder_size(app_path)
            print(f"📊 App-Größe: {size:.1f} MB")

    except subprocess.CalledProcessError as e:
        print(f"❌ Build fehlgeschlagen: {e}")

def get_folder_size(folder):
    """Berechnet Ordnergröße in MB"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size / (1024 * 1024)

if __name__ == "__main__":
    build_app()