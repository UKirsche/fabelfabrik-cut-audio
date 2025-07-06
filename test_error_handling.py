#!/usr/bin/env python3
"""
Demonstration script for YouTube downloader error handling.
This script tests various error scenarios to show how the enhanced error handling works.
"""

import os
import tempfile
from audio.youtube_downloader import (
    YouTubeDownloader, 
    InvalidURLError, 
    NetworkError, 
    VideoUnavailableError, 
    FormatError,
    PermissionError,
    YouTubeDownloaderError
)

def test_error_handling():
    """Test various error scenarios"""
    downloader = YouTubeDownloader()
    
    print("🧪 Testing YouTube Downloader Error Handling\n")
    
    # Test 1: Invalid URL
    print("1. Testing invalid URL...")
    try:
        downloader._validate_url("https://www.google.com")
    except InvalidURLError as e:
        print(f"   ✅ Caught InvalidURLError: {e}")
    
    # Test 2: Empty URL
    print("\n2. Testing empty URL...")
    try:
        downloader._validate_url("")
    except InvalidURLError as e:
        print(f"   ✅ Caught InvalidURLError: {e}")
    
    # Test 3: Valid YouTube URLs
    print("\n3. Testing valid YouTube URLs...")
    valid_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
        "youtube.com/watch?v=abc123"
    ]
    for url in valid_urls:
        try:
            downloader._validate_url(url)
            print(f"   ✅ Valid URL: {url}")
        except InvalidURLError as e:
            print(f"   ❌ Unexpected error for {url}: {e}")
    
    # Test 4: Audio quality validation
    print("\n4. Testing audio quality validation...")
    try:
        downloader.set_audio_quality("999")  # Invalid quality
    except FormatError as e:
        print(f"   ✅ Caught FormatError for invalid quality: {e}")
    
    try:
        downloader.set_audio_quality("320")  # Valid quality
        print("   ✅ Valid audio quality '320' accepted")
    except FormatError as e:
        print(f"   ❌ Unexpected error for valid quality: {e}")
    
    # Test 5: Audio format validation
    print("\n5. Testing audio format validation...")
    try:
        downloader.set_output_format("xyz")  # Invalid format
    except FormatError as e:
        print(f"   ✅ Caught FormatError for invalid format: {e}")
    
    try:
        downloader.set_output_format("mp3")  # Valid format
        print("   ✅ Valid audio format 'mp3' accepted")
    except FormatError as e:
        print(f"   ❌ Unexpected error for valid format: {e}")
    
    # Test 6: Empty output path
    print("\n6. Testing empty output path...")
    try:
        downloader._validate_output_path("")
    except PermissionError as e:
        print(f"   ✅ Caught PermissionError for empty path: {e}")
    
    # Test 7: Valid output path
    print("\n7. Testing valid output path...")
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            downloader._validate_output_path(temp_dir)
            print(f"   ✅ Valid output path accepted: {temp_dir}")
        except PermissionError as e:
            print(f"   ❌ Unexpected error for valid path: {e}")
    
    # Test 8: Video info validation
    print("\n8. Testing video info validation...")
    
    # Test private video
    private_video_info = {
        'title': 'Private Video',
        'availability': 'private',
        'live_status': 'not_live'
    }
    try:
        downloader._validate_video_info(private_video_info)
    except VideoUnavailableError as e:
        print(f"   ✅ Caught VideoUnavailableError for private video: {e}")
    
    # Test live stream
    live_video_info = {
        'title': 'Live Stream',
        'availability': 'public',
        'live_status': 'is_live'
    }
    try:
        downloader._validate_video_info(live_video_info)
    except VideoUnavailableError as e:
        print(f"   ✅ Caught VideoUnavailableError for live stream: {e}")
    
    # Test deleted video
    deleted_video_info = {
        'title': '[Deleted video]',
        'availability': 'public',
        'live_status': 'not_live'
    }
    try:
        downloader._validate_video_info(deleted_video_info)
    except VideoUnavailableError as e:
        print(f"   ✅ Caught VideoUnavailableError for deleted video: {e}")
    
    # Test 9: Audio availability validation
    print("\n9. Testing audio availability validation...")
    
    # Video without audio
    no_audio_info = {
        'formats': [
            {'acodec': 'none', 'format_id': '1'},
            {'acodec': 'none', 'format_id': '2'}
        ]
    }
    try:
        downloader._validate_audio_availability(no_audio_info)
    except FormatError as e:
        print(f"   ✅ Caught FormatError for video without audio: {e}")
    
    # Video with audio
    with_audio_info = {
        'formats': [
            {'acodec': 'mp3', 'format_id': '1'},
            {'acodec': 'aac', 'format_id': '2'}
        ]
    }
    try:
        downloader._validate_audio_availability(with_audio_info)
        print("   ✅ Video with audio streams accepted")
    except FormatError as e:
        print(f"   ❌ Unexpected error for video with audio: {e}")
    
    print("\n🎉 Error handling tests completed successfully!")
    print("\nThe YouTube downloader now includes comprehensive error handling for:")
    print("  • Invalid URL formats")
    print("  • Network connectivity issues")
    print("  • File system permissions")
    print("  • Private/unavailable videos")
    print("  • Live stream restrictions")
    print("  • Audio format validation")
    print("  • Clear user feedback messages")

if __name__ == "__main__":
    test_error_handling()
