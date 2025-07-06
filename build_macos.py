#!/usr/bin/env python3
"""
MP3 Combiner - macOS Build Script (Robust Version)
"""

import os
import sys
import subprocess
import shutil
import time
import stat
from pathlib import Path

class Builder:
    def __init__(self):
        self.project_dir = Path.cwd()
        self.dist_dir = self.project_dir / "dist"
        self.build_dir = self.project_dir / "build"
        self.app_name = "MP3 Combiner"
        self.spec_file = f"{self.app_name}.spec"
        
    def force_remove_dir(self, directory):
        """Löscht Verzeichnis mit allen nötigen Permissions"""
        if not directory.exists():
            return True
            
        try:
            # Erst alle Dateien beschreibbar machen
            for root, dirs, files in os.walk(directory):
                for d in dirs:
                    dir_path = Path(root) / d
                    try:
                        dir_path.chmod(0o755)
                    except:
                        pass
                for f in files:
                    file_path = Path(root) / f
                    try:
                        file_path.chmod(0o644)
                    except:
                        pass
            
            # Dann löschen
            shutil.rmtree(directory)
            return True
            
        except PermissionError as e:
            print(f"   ⚠️  Permissions-Problem: {e}")
            print(f"   🔧 Versuche mit sudo...")
            
            try:
                # Mit sudo löschen
                result = subprocess.run([
                    'sudo', 'rm', '-rf', str(directory)
                ], check=True)
                return True
            except subprocess.CalledProcessError:
                print(f"   ❌ Auch sudo konnte {directory} nicht löschen")
                return False
                
        except Exception as e:
            print(f"   ❌ Unerwarteter Fehler: {e}")
            return False
    
    def clean_previous_builds(self):
        """Löscht alte Build-Dateien (robust)"""
        print("🧹 Bereinige alte Builds...")
        
        success = True
        
        for directory in [self.dist_dir, self.build_dir]:
            if directory.exists():
                print(f"   📂 Lösche: {directory}")
                if not self.force_remove_dir(directory):
                    print(f"   ❌ Konnte {directory} nicht löschen!")
                    success = False
                else:
                    print(f"   ✅ {directory} gelöscht")
            else:
                print(f"   ✅ {directory} existiert nicht")
        
        # Zusätzlich __pycache__ aufräumen
        pycache_dirs = list(self.project_dir.rglob("__pycache__"))
        for pycache in pycache_dirs:
            try:
                shutil.rmtree(pycache)
            except:
                pass
        
        if success:
            print("✅ Bereinigung erfolgreich\n")
        else:
            print("⚠️  Bereinigung teilweise fehlgeschlagen\n")
            # Trotzdem weitermachen
        
        return True  # Immer True, damit Build weitergeht
    
    def check_dependencies(self):
        """Prüft alle Abhängigkeiten"""
        print("🔍 Prüfe Abhängigkeiten...")
        
        # Python-Module
        required_modules = ['tkinter', 'pydub', 'yt_dlp']
        missing_modules = []
        
        for module in required_modules:
            try:
                __import__(module)
                print(f"   ✅ {module}")
            except ImportError:
                print(f"   ❌ {module}")
                missing_modules.append(module)
        
        if missing_modules:
            print(f"\n❌ Fehlende Module: {missing_modules}")
            print("Installieren mit: pip install pydub")
            return False
        
        # PyInstaller
        try:
            result = subprocess.run(['pyinstaller', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"   ✅ PyInstaller {version}")
            else:
                print("   ❌ PyInstaller nicht gefunden")
                return False
        except FileNotFoundError:
            print("   ❌ PyInstaller nicht gefunden")
            print("Installieren mit: pip install pyinstaller")
            return False
        
        print("✅ Abhängigkeiten OK\n")
        return True
    
    def check_main_file(self):
        """Prüft ob converter.py existiert"""
        main_file = self.project_dir / "converter.py"
        if not main_file.exists():
            print("❌ converter.py nicht gefunden!")
            print("Verfügbare Python-Dateien:")
            for py_file in self.project_dir.glob("*.py"):
                print(f"   - {py_file.name}")
            return False
        
        print(f"✅ Hauptdatei gefunden: converter.py\n")
        return True
    
    def run_pyinstaller(self):
        """Führt PyInstaller aus"""
        print("🚀 Starte PyInstaller...")
        
        cmd = [
            "pyinstaller",
            self.spec_file,
            "--clean",
            "--noconfirm"
        ]
        
        print(f"   Kommando: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, cwd=self.project_dir, 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ PyInstaller erfolgreich!")
                return True
            else:
                print(f"❌ PyInstaller fehlgeschlagen!")
                print("STDOUT:", result.stdout[-500:])  # Letzten 500 Zeichen
                print("STDERR:", result.stderr[-500:])
                return False
                
        except Exception as e:
            print(f"❌ PyInstaller Fehler: {e}")
            return False
    
    def post_process_app(self):
        """Nachbearbeitung der App"""
        app_path = self.dist_dir / f"{self.app_name}.app"
        
        if not app_path.exists():
            print("❌ App-Bundle nicht gefunden!")
            return False
        
        print("🔧 App-Nachbearbeitung...")
        
        macos_dir = app_path / "Contents" / "MacOS"
        if macos_dir.exists():
            files = list(macos_dir.iterdir())
            print(f"   📂 Dateien: {[f.name for f in files]}")
            
            # ffmpeg prüfen
            has_ffmpeg = (macos_dir / "ffmpeg").exists()
            has_ffprobe = (macos_dir / "ffprobe").exists()
            
            print(f"   {'✅' if has_ffmpeg else '❌'} ffmpeg")
            print(f"   {'✅' if has_ffprobe else '❌'} ffprobe")
        
        return True
    
    def test_app(self):
        """Testet die erstellte App"""
        app_path = self.dist_dir / f"{self.app_name}.app"
        
        if app_path.exists():
            print("✅ App wurde erstellt!")
            print(f"   📱 Pfad: {app_path}")
            print(f"   🚀 Starten: open '{app_path}'")
            return True
        else:
            print("❌ App nicht gefunden!")
            return False
    
    def build(self):
        """Hauptbuild-Prozess"""
        print("🎵 MP3 Combiner - macOS Build (Robust)")
        print("=" * 50)
        
        steps = [
            ("Abhängigkeiten prüfen", self.check_dependencies),
            ("Hauptdatei prüfen", self.check_main_file),
            ("Alte Builds löschen", self.clean_previous_builds),
            ("PyInstaller ausführen", self.run_pyinstaller),
            ("App nachbearbeiten", self.post_process_app),
            ("App testen", self.test_app),
        ]
        
        for step_name, step_func in steps:
            print(f"\n📋 {step_name}...")
            if not step_func():
                print(f"\n❌ Build fehlgeschlagen bei: {step_name}")
                return False
        
        print("\n🎉 BUILD ERFOLGREICH!")
        return True

if __name__ == "__main__":
    builder = Builder()
    builder.build()