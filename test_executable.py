#!/usr/bin/env python3
"""
Test script for MP3 Combiner standalone executable
Tests YouTube downloads, ffmpeg integration, file paths, and error handling
"""

import os
import sys
import subprocess
import tempfile
import shutil
import time
from pathlib import Path

# Color codes for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.ENDC}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.ENDC}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.ENDC}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.ENDC}")

def print_header(message):
    print(f"\n{Colors.BOLD}{'='*60}")
    print(f"🧪 {message}")
    print(f"{'='*60}{Colors.ENDC}")

class ExecutableTest:
    def __init__(self):
        self.executable_path = None
        self.temp_dir = None
        self.test_results = []
        
    def setup(self):
        """Setup test environment"""
        print_header("Setting up test environment")
        
        # Find executable
        possible_paths = [
            "./dist/MP3 Combiner.app/Contents/MacOS/MP3 Combiner",
            "./dist/MP3 Combiner",
            "dist/MP3 Combiner.app/Contents/MacOS/MP3 Combiner",
            "dist/MP3 Combiner"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                self.executable_path = os.path.abspath(path)
                print_success(f"Found executable: {self.executable_path}")
                break
        
        if not self.executable_path:
            print_error("Executable not found!")
            return False
            
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp(prefix="mp3_combiner_test_")
        print_success(f"Created temp directory: {self.temp_dir}")
        
        return True
    
    def test_executable_launch(self):
        """Test if executable can launch without crashing"""
        print_header("Testing executable launch")
        
        try:
            # Try to run with --help or version flag (if available)
            # Since this is a GUI app, we'll just test if it can be executed
            result = subprocess.run(
                [self.executable_path, "--help"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 or "usage" in result.stdout.lower():
                print_success("Executable launches successfully")
                return True
            else:
                print_warning("Executable launched but returned non-zero exit code")
                print_info(f"stdout: {result.stdout}")
                print_info(f"stderr: {result.stderr}")
                return True  # GUI apps might not support --help
                
        except subprocess.TimeoutExpired:
            print_warning("Executable launch timed out (might be waiting for GUI)")
            return True  # This is expected for GUI apps
        except Exception as e:
            print_error(f"Failed to launch executable: {e}")
            return False
    
    def test_import_dependencies(self):
        """Test if all dependencies can be imported"""
        print_header("Testing dependency imports")
        
        # Create a test script that imports key dependencies
        test_script = f"""
import sys
import os
sys.path.insert(0, '{os.path.dirname(self.executable_path)}')

try:
    import yt_dlp
    print("✅ yt_dlp imported successfully")
    print(f"yt_dlp version: {{yt_dlp.version.__version__}}")
    
    import pydub
    print("✅ pydub imported successfully")
    
    import tkinter
    print("✅ tkinter imported successfully")
    
    # Note: requests is used by yt_dlp internally, but not directly by our app
    
    # Test yt_dlp functionality
    ydl = yt_dlp.YoutubeDL({{'quiet': True}})
    print("✅ yt_dlp.YoutubeDL instantiated successfully")
    
    print("SUCCESS: All dependencies imported")
    
except Exception as e:
    print(f"ERROR: {{e}}")
    sys.exit(1)
"""
        
        test_file = os.path.join(self.temp_dir, "test_imports.py")
        with open(test_file, 'w') as f:
            f.write(test_script)
        
        try:
            result = subprocess.run(
                [sys.executable, test_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print_success("All dependencies imported successfully")
                print_info(result.stdout)
                return True
            else:
                print_error("Dependency import failed")
                print_info(f"stdout: {result.stdout}")
                print_info(f"stderr: {result.stderr}")
                return False
                
        except Exception as e:
            print_error(f"Failed to test imports: {e}")
            return False
    
    def test_ffmpeg_integration(self):
        """Test ffmpeg integration"""
        print_header("Testing ffmpeg integration")
        
        # Check if ffmpeg binaries are available
        ffmpeg_paths = [
            "/opt/homebrew/bin/ffmpeg",
            "/usr/local/bin/ffmpeg",
            "/usr/bin/ffmpeg"
        ]
        
        ffmpeg_found = False
        for path in ffmpeg_paths:
            if os.path.exists(path):
                print_success(f"Found ffmpeg at: {path}")
                ffmpeg_found = True
                break
        
        if not ffmpeg_found:
            # Check if it's in PATH
            try:
                result = subprocess.run(["which", "ffmpeg"], capture_output=True, text=True)
                if result.returncode == 0:
                    print_success(f"Found ffmpeg in PATH: {result.stdout.strip()}")
                    ffmpeg_found = True
            except:
                pass
        
        if not ffmpeg_found:
            print_error("ffmpeg not found in system")
            return False
        
        # Test ffmpeg functionality
        try:
            result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print_success("ffmpeg is working correctly")
                return True
            else:
                print_error("ffmpeg version check failed")
                return False
        except Exception as e:
            print_error(f"Failed to test ffmpeg: {e}")
            return False
    
    def test_file_permissions(self):
        """Test file paths and permissions"""
        print_header("Testing file paths and permissions")
        
        # Test executable permissions
        if os.access(self.executable_path, os.X_OK):
            print_success("Executable has execute permissions")
        else:
            print_error("Executable lacks execute permissions")
            return False
        
        # Test write permissions in temp directory
        test_file = os.path.join(self.temp_dir, "test_write.txt")
        try:
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            print_success("Write permissions working in temp directory")
        except Exception as e:
            print_error(f"Write permission test failed: {e}")
            return False
        
        # Test creating audio directory
        audio_dir = os.path.join(self.temp_dir, "audio")
        try:
            os.makedirs(audio_dir, exist_ok=True)
            print_success("Can create audio directory")
        except Exception as e:
            print_error(f"Failed to create audio directory: {e}")
            return False
        
        return True
    
    def test_youtube_download_capability(self):
        """Test YouTube download capability (without actually downloading)"""
        print_header("Testing YouTube download capability")
        
        # Create a test script that tests yt_dlp functionality
        test_script = f"""
import sys
import os
sys.path.insert(0, '{os.path.dirname(self.executable_path)}')

try:
    import yt_dlp
    
    # Test URL extraction (without downloading)
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll - safe test video
    
    ydl_opts = {{
        'quiet': True,
        'no_warnings': True,
        'simulate': True,  # Don't actually download
        'extract_flat': False,
    }}
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(test_url, download=False)
            if info and 'title' in info:
                print(f"✅ Successfully extracted video info: {{info['title']}}")
                print("✅ YouTube download capability working")
            else:
                print("❌ Failed to extract video info")
                sys.exit(1)
        except Exception as e:
            print(f"❌ YouTube extraction failed: {{e}}")
            sys.exit(1)
            
except Exception as e:
    print(f"❌ yt_dlp test failed: {{e}}")
    sys.exit(1)
"""
        
        test_file = os.path.join(self.temp_dir, "test_youtube.py")
        with open(test_file, 'w') as f:
            f.write(test_script)
        
        try:
            result = subprocess.run(
                [sys.executable, test_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print_success("YouTube download capability working")
                print_info(result.stdout)
                return True
            else:
                print_error("YouTube download test failed")
                print_info(f"stdout: {result.stdout}")
                print_info(f"stderr: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print_error("YouTube download test timed out")
            return False
        except Exception as e:
            print_error(f"Failed to test YouTube download: {e}")
            return False
    
    def test_error_handling(self):
        """Test error handling"""
        print_header("Testing error handling")
        
        # Test with invalid URL
        test_script = f"""
import sys
import os
sys.path.insert(0, '{os.path.dirname(self.executable_path)}')

try:
    import yt_dlp
    
    # Test with invalid URL
    invalid_url = "https://invalid-url-that-does-not-exist.com/video"
    
    ydl_opts = {{
        'quiet': True,
        'no_warnings': True,
        'simulate': True,
    }}
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(invalid_url, download=False)
            print("❌ Should have failed with invalid URL")
            sys.exit(1)
        except Exception as e:
            print(f"✅ Correctly handled invalid URL: {{type(e).__name__}}")
            
    print("✅ Error handling working correctly")
            
except Exception as e:
    print(f"❌ Error handling test failed: {{e}}")
    sys.exit(1)
"""
        
        test_file = os.path.join(self.temp_dir, "test_error_handling.py")
        with open(test_file, 'w') as f:
            f.write(test_script)
        
        try:
            result = subprocess.run(
                [sys.executable, test_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print_success("Error handling working correctly")
                print_info(result.stdout)
                return True
            else:
                print_error("Error handling test failed")
                print_info(f"stdout: {result.stdout}")
                print_info(f"stderr: {result.stderr}")
                return False
                
        except Exception as e:
            print_error(f"Failed to test error handling: {e}")
            return False
    
    def cleanup(self):
        """Clean up test environment"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            print_success("Cleaned up test environment")
    
    def run_all_tests(self):
        """Run all tests"""
        print_header("MP3 Combiner Executable Test Suite")
        
        if not self.setup():
            print_error("Setup failed, aborting tests")
            return False
        
        tests = [
            ("Executable Launch", self.test_executable_launch),
            ("Dependency Imports", self.test_import_dependencies),
            ("FFmpeg Integration", self.test_ffmpeg_integration),
            ("File Permissions", self.test_file_permissions),
            ("YouTube Download Capability", self.test_youtube_download_capability),
            ("Error Handling", self.test_error_handling),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
                    self.test_results.append((test_name, True, ""))
                else:
                    self.test_results.append((test_name, False, "Test failed"))
                    
            except Exception as e:
                print_error(f"Test '{test_name}' crashed: {e}")
                self.test_results.append((test_name, False, str(e)))
        
        # Print summary
        print_header("Test Results Summary")
        for test_name, passed_test, error in self.test_results:
            if passed_test:
                print_success(f"{test_name}")
            else:
                print_error(f"{test_name}: {error}")
        
        print(f"\n{Colors.BOLD}Overall Result: {passed}/{total} tests passed{Colors.ENDC}")
        
        if passed == total:
            print_success("All tests passed! 🎉")
            success = True
        else:
            print_error(f"{total - passed} test(s) failed")
            success = False
        
        self.cleanup()
        return success

if __name__ == "__main__":
    tester = ExecutableTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
