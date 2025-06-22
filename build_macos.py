#!/usr/bin/env python3
"""
Build-Script mit Spec-Datei für zuverlässige ffmpeg-Einbindung
"""
import os
import subprocess
import shutil

def build_app():
    """Erstellt die macOS App mit Spec-Datei"""

    print("🔨 Starte Build mit Spec-Datei...")

    # Alte Builds löschen
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")

    # Mit Spec-Datei builden
    cmd = ["pyinstaller", "MP3 Combiner.spec", "--clean", "--noconfirm"]

    try:
        subprocess.run(cmd, check=True)
        print("\n✅ Build erfolgreich!")
        
        # App-Info anzeigen
        app_path = "dist/MP3 Combiner.app"
        if os.path.exists(app_path):
            size = get_folder_size(app_path)
            print(f"📦 App-Größe: {size:.1f} MB")
            
            # Binärdateien prüfen
            macos_dir = f"{app_path}/Contents/MacOS"
            files = os.listdir(macos_dir)
            print(f"📂 Enthaltene Dateien: {files}")
            
            if 'ffmpeg' in files:
                print("✅ ffmpeg eingebettet")
            else:
                print("❌ ffmpeg fehlt!")
                
            if 'ffprobe' in files:
                print("✅ ffprobe eingebettet")
            else:
                print("❌ ffprobe fehlt!")
                
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Build fehlgeschlagen: {e}")
        return False

def get_folder_size(folder):
    """Berechnet Ordnergröße in MB"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.exists(fp):
                total_size += os.path.getsize(fp)
    return total_size / (1024 * 1024)

if __name__ == "__main__":
    print("🎵 MP3 Combiner - Build mit Spec-Datei")
    print("=" * 50)
    build_app()