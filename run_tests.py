#!/usr/bin/env python3
"""
Test runner for YouTube downloader functionality.
Runs both unit tests and integration tests.
"""

import unittest
import sys
import os

def run_all_tests():
    """Run all tests for the YouTube downloader"""
    # Add current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = os.path.join(current_dir, 'tests')
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return success/failure
    return result.wasSuccessful()

def run_specific_test(test_file):
    """Run a specific test file"""
    # Add current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    # Import and run specific test
    if test_file == 'unit':
        from tests.test_youtube_downloader import TestYouTubeDownloader
        suite = unittest.TestLoader().loadTestsFromTestCase(TestYouTubeDownloader)
    elif test_file == 'integration':
        from tests.test_integration import TestYouTubeDownloaderIntegration
        suite = unittest.TestLoader().loadTestsFromTestCase(TestYouTubeDownloaderIntegration)
    else:
        print(f"Unknown test file: {test_file}")
        return False
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
        if test_type in ['unit', 'integration']:
            success = run_specific_test(test_type)
        else:
            print("Usage: python run_tests.py [unit|integration]")
            print("       python run_tests.py  (runs all tests)")
            sys.exit(1)
    else:
        success = run_all_tests()
    
    sys.exit(0 if success else 1)
