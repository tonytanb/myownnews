#!/usr/bin/env python3
"""
Simple test for the AudioService to verify it works correctly
"""

import sys
import os
import time

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audio_service import AudioService

def test_audio_service():
    """Test the AudioService with a simple script"""
    print("🧪 Testing AudioService...")
    
    # Initialize the service
    audio_service = AudioService(voice_id='Joanna')
    
    # Test script
    test_script = """
    Good morning! Welcome to your personalized Curio News briefing. 
    Today we have some interesting stories to share with you.
    
    In technology news, artificial intelligence continues to advance rapidly.
    Thank you for listening to Curio News!
    """
    
    # Test audio generation
    print("\n📝 Testing audio generation...")
    result = audio_service.generate_audio_url(test_script, "test-run-001")
    
    # Check results
    if result['success']:
        print("✅ Audio generation successful!")
        print(f"   - Audio URL: {'Present' if result['audio_url'] else 'Missing'}")
        print(f"   - Duration: {result.get('duration', 0):.1f} seconds")
        print(f"   - Generation time: {result.get('generation_time_ms', 0):.1f}ms")
        print(f"   - Voice ID: {result.get('voice_id', 'Unknown')}")
        print(f"   - Fallback used: {result.get('fallback_used', False)}")
        
        if result.get('audio_url'):
            # Check if it's a data URL
            if result['audio_url'].startswith('data:audio/mpeg;base64,'):
                print("   - Audio format: Base64 data URL ✅")
                # Check if base64 data is reasonable length
                base64_data = result['audio_url'].split(',')[1]
                data_size = len(base64_data) * 3 / 4  # Approximate decoded size
                print(f"   - Audio data size: ~{data_size/1024:.1f} KB")
            else:
                print(f"   - Audio format: {result['audio_url'][:50]}...")
        
    else:
        print("❌ Audio generation failed!")
        print(f"   - Error: {result.get('message', 'Unknown error')}")
        if 'errors' in result:
            for error_type, error_msg in result['errors'].items():
                print(f"   - {error_type}: {error_msg}")
    
    # Test word timings
    print("\n📝 Testing word timings...")
    try:
        word_timings = audio_service.get_word_timings(test_script)
        if word_timings:
            print(f"✅ Word timings generated: {len(word_timings)} words")
            # Show first few timings
            for i, timing in enumerate(word_timings[:5]):
                print(f"   - {timing['word']}: {timing['start']:.2f}s - {timing['end']:.2f}s")
            if len(word_timings) > 5:
                print(f"   - ... and {len(word_timings) - 5} more words")
        else:
            print("⚠️ No word timings generated")
    except Exception as e:
        print(f"❌ Word timing test failed: {e}")
    
    # Test fallback scenario
    print("\n📝 Testing fallback scenario...")
    try:
        # Test with empty script to trigger fallback
        fallback_result = audio_service.generate_audio_url("", "test-fallback-001")
        if fallback_result['success']:
            print("✅ Fallback handling successful!")
            print(f"   - Fallback used: {fallback_result.get('fallback_used', False)}")
            print(f"   - Hardcoded fallback: {fallback_result.get('hardcoded_fallback', False)}")
        else:
            print("⚠️ Fallback returned failure (this might be expected)")
    except Exception as e:
        print(f"❌ Fallback test failed: {e}")
    
    print("\n🎉 AudioService test completed!")
    return result['success']

if __name__ == "__main__":
    success = test_audio_service()
    sys.exit(0 if success else 1)