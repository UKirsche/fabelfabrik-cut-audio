# -*- mode: python ; coding: utf-8 -*-
import subprocess
import os

def find_binary(name):
    """Findet Binärdatei-Pfad mit Debug-Output"""
    print(f"🔍 Suche {name}...")

    # 1. 'which' versuchen
    try:
        result = subprocess.run(['which', name], capture_output=True, text=True)
        if result.returncode == 0:
            path = result.stdout.strip()
            print(f"  'which' gefunden: {path}")
            if os.path.exists(path):
                print(f"  ✅ Datei existiert: {path}")
                return path
            else:
                print(f"  ❌ Datei existiert nicht: {path}")
    except Exception as e:
        print(f"  'which' Fehler: {e}")

    # 2. Bekannte Pfade prüfen
    common_paths = [
        f"/opt/homebrew/bin/{name}",
        f"/usr/local/bin/{name}",
        f"/usr/bin/{name}",
    ]

    print(f"  Prüfe bekannte Pfade...")
    for path in common_paths:
        print(f"    Teste: {path}")
        if os.path.exists(path):
            print(f"  ✅ Gefunden: {path}")
            return path
        else:
            print(f"    ❌ Nicht gefunden")

    print(f"  ❌ {name} nirgends gefunden!")
    return None

# ffmpeg/ffprobe Pfade finden
print("=" * 50)
print("🔍 Suche ffmpeg/ffprobe für PyInstaller...")
print("=" * 50)

ffmpeg_path = find_binary('ffmpeg')
ffprobe_path = find_binary('ffprobe')

print("=" * 50)
print(f"ERGEBNIS:")
print(f"ffmpeg: {ffmpeg_path}")
print(f"ffprobe: {ffprobe_path}")
print("=" * 50)

# Binärdateien für PyInstaller
binaries = []
datas = []

# audio-Ordner hinzufügen (falls existiert)
if os.path.exists('audio'):
    datas.append(('audio', 'audio'))
    print("✅ audio-Ordner gefunden")

# ffmpeg hinzufügen (falls gefunden)
if ffmpeg_path and os.path.exists(ffmpeg_path):
    binaries.append((ffmpeg_path, '.'))
    print(f"✅ ffmpeg wird eingebunden: {ffmpeg_path}")
else:
    print("❌ ffmpeg wird NICHT eingebunden!")

# ffprobe hinzufügen (falls gefunden)
if ffprobe_path and os.path.exists(ffprobe_path):
    binaries.append((ffprobe_path, '.'))
    print(f"✅ ffprobe wird eingebunden: {ffprobe_path}")
else:
    print("❌ ffprobe wird NICHT eingebunden!")

print(f"Finale binaries Liste: {binaries}")
print(f"Finale datas Liste: {datas}")
print("=" * 50)

a = Analysis(
    ['converter.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='MP3 Combiner',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

app = BUNDLE(
    exe,
    name='MP3 Combiner.app',
    icon=None,
    bundle_identifier=None,
)