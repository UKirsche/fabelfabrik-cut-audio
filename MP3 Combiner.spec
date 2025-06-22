# -*- mode: python ; coding: utf-8 -*-

import os
import subprocess
import sys

# Aktuelles Projektverzeichnis
python_path = sys.executable
project_dir = os.path.dirname(os.path.abspath('converter.py'))

print("=" * 60)
print("🔧 MP3 Combiner - PyInstaller Spec-Datei (final)")
print("=" * 60)
print(f"Python: {python_path}")
print(f"Projekt: {project_dir}")

def find_ffmpeg():
    """Findet ffmpeg und ffprobe Pfade"""
    binaries = []
    paths_to_check = [
        '/opt/homebrew/bin/ffmpeg',
        '/opt/homebrew/bin/ffprobe',
        '/usr/local/bin/ffmpeg',
        '/usr/local/bin/ffprobe',
        '/usr/bin/ffmpeg',
        '/usr/bin/ffprobe'
    ]
    for binary in ['ffmpeg', 'ffprobe']:
        # Versuche mit 'which'
        try:
            result = subprocess.run(['which', binary], capture_output=True, text=True)
            if result.returncode == 0:
                path = result.stdout.strip()
                if os.path.exists(path):
                    binaries.append((path, '.'))
                    print(f"✅ {binary} gefunden: {path}")
                    continue
        except:
            pass

        # Fallback
        for path in paths_to_check:
            if binary in path and os.path.exists(path):
                binaries.append((path, '.'))
                print(f"✅ {binary} gefunden: {path}")
                break
        else:
            print(f"⚠️  {binary} nicht gefunden!")

    return binaries

# Finde ffmpeg & ffprobe
ffmpeg_binaries = find_ffmpeg()

# Zusätzliche Datenordner
datas = []
if os.path.exists('audio'):
    datas.append(('audio', 'audio'))
    print("✅ audio-Ordner wird eingebunden")

print(f"📦 Binärdateien: {len(ffmpeg_binaries)} gefunden")
print(f"📁 Datenordner: {len(datas)}")
print("=" * 60)

# Analysis: Haupt-Schritt
a = Analysis(
    ['converter.py'],
    pathex=[project_dir],
    binaries=ffmpeg_binaries,
    datas=datas,
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'pydub',
        'pydub.utils'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MP3 Combiner',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,   # False = .app ohne Terminal-Fenster
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

app = BUNDLE(
    exe,
    name='MP3 Combiner.app',
    icon=None,
    bundle_identifier='com.example.mp3combiner',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSAppleScriptEnabled': False,
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeName': 'MP3 Audio File',
                'CFBundleTypeIconFile': 'mp3.icns',
                'LSItemContentTypes': ['public.mp3'],
                'LSHandlerRank': 'Owner'
            }
        ]
    },
)