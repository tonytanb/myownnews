#!/usr/bin/env python3
"""
Entertainment Recommendations Verification Script
Tests the deployed entertainment recommendations functionality
"""

import requests
import json
import time
from datetime import datetime

# Configuration
FRONTEND_URL = "http://curio-news-frontend-1761841602.s3-website-us-west-2.amazonaws.com"
API_URL = "https://nqot0dir0h.execute-api.us-west-2.amazonaws.com/prod"

def test_api_entertainment_data():
    """Test that the API returns entertainment recommendations data"""
    print("🔍 Testing API entertainment data generation...")
    
    try:
        # Test the main API endpoint
        response = requests.get(f"{API_URL}/generate-content", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if entertainment_recommendations exists
            if 'entertainment_recommendations' in data:
                entertainment = data['entertainment_recommendations']
                print("✅ Entertainment recommendations found in API response")
                
                # Check for top movies
                if 'top_movies' in entertainment and entertainment['top_movies']:
                    print(f"✅ Top movies: {len(entertainment['top_movies'])} items")
                    for i, movie in enumerate(entertainment['top_movies'][:2]):
                        print(f"   - {movie.get('title', 'Unknown')} ({movie.get('platform', 'Unknown platform')})")
                
                # Check for TV series
                if 'must_watch_series' in entertainment and entertainment['must_watch_series']:
                    print(f"✅ Must-watch series: {len(entertainment['must_watch_series'])} items")
                    for i, series in enumerate(entertainment['must_watch_series'][:2]):
                        print(f"   - {series.get('title', 'Unknown')} ({series.get('platform', 'Unknown platform')})")
                
                # Check for theater plays
                if 'theater_plays' in entertainment and entertainment['theater_plays']:
                    print(f"✅ Theater plays: {len(entertainment['theater_plays'])} items")
                    for i, play in enumerate(entertainment['theater_plays'][:2]):
                        print(f"   - {play.get('title', 'Unknown')} ({play.get('venue', 'Unknown venue')})")
                
                return True
            else:
                print("❌ No entertainment_recommendations found in API response")
                print("Available keys:", list(data.keys()))
                return False
        else:
            print(f"❌ API request failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API test failed: {str(e)}")
        return False

def test_frontend_accessibility():
    """Test that the frontend is accessible and loads properly"""
    print("\n🌐 Testing frontend accessibility...")
    
    try:
        response = requests.get(FRONTEND_URL, timeout=10)
        
        if response.status_code == 200:
            content = response.text
            
            # Check for key elements
            checks = [
                ("React app", "root" in content),
                ("CSS bundle", "main." in content and ".css" in content),
                ("JS bundle", "main." in content and ".js" in content),
                ("Title", "Curio News" in content or "title" in content.lower())
            ]
            
            all_passed = True
            for check_name, passed in checks:
                if passed:
                    print(f"✅ {check_name} found")
                else:
                    print(f"❌ {check_name} missing")
                    all_passed = False
            
            return all_passed
        else:
            print(f"❌ Frontend not accessible (status {response.status_code})")
            return False
            
    except Exception as e:
        print(f"❌ Frontend accessibility test failed: {str(e)}")
        return False

def test_entertainment_data_structure():
    """Test various data combinations and edge cases"""
    print("\n🧪 Testing entertainment data structure and edge cases...")
    
    try:
        response = requests.get(f"{API_URL}/generate-content", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'entertainment_recommendations' not in data:
                print("❌ No entertainment_recommendations in response")
                return False
            
            entertainment = data['entertainment_recommendations']
            
            # Test data structure for movies
            if 'top_movies' in entertainment and entertainment['top_movies']:
                movie = entertainment['top_movies'][0]
                required_fields = ['title', 'genre', 'rating', 'platform', 'description']
                optional_fields = ['release_year', 'runtime']
                
                print("🎬 Testing movie data structure:")
                for field in required_fields:
                    if field in movie and movie[field]:
                        print(f"   ✅ {field}: {movie[field]}")
                    else:
                        print(f"   ❌ Missing required field: {field}")
                
                for field in optional_fields:
                    if field in movie and movie[field]:
                        print(f"   ✅ {field}: {movie[field]}")
            
            # Test data structure for series
            if 'must_watch_series' in entertainment and entertainment['must_watch_series']:
                series = entertainment['must_watch_series'][0]
                required_fields = ['title', 'genre', 'rating', 'platform', 'description', 'seasons', 'status']
                
                print("\n📺 Testing series data structure:")
                for field in required_fields:
                    if field in series and series[field]:
                        print(f"   ✅ {field}: {series[field]}")
                    else:
                        print(f"   ❌ Missing required field: {field}")
            
            # Test data structure for plays
            if 'theater_plays' in entertainment and entertainment['theater_plays']:
                play = entertainment['theater_plays'][0]
                required_fields = ['title', 'genre', 'description']
                optional_fields = ['venue', 'city', 'show_times', 'ticket_info', 'rating']
                
                print("\n🎭 Testing play data structure:")
                for field in required_fields:
                    if field in play and play[field]:
                        print(f"   ✅ {field}: {play[field]}")
                    else:
                        print(f"   ❌ Missing required field: {field}")
                
                for field in optional_fields:
                    if field in play and play[field]:
                        print(f"   ✅ {field}: {play[field]}")
            
            return True
            
    except Exception as e:
        print(f"❌ Data structure test failed: {str(e)}")
        return False

def run_verification():
    """Run all verification tests"""
    print("🎬 Entertainment Recommendations Verification")
    print("=" * 50)
    print(f"Frontend URL: {FRONTEND_URL}")
    print(f"API URL: {API_URL}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = {
        'api_entertainment_data': test_api_entertainment_data(),
        'frontend_accessibility': test_frontend_accessibility(),
        'data_structure': test_entertainment_data_structure()
    }
    
    print("\n" + "=" * 50)
    print("📊 VERIFICATION RESULTS")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All entertainment recommendations tests PASSED!")
        print("✅ Entertainment Hub is ready for production deployment")
    else:
        print("⚠️  Some tests failed. Review issues before production deployment.")
    
    return passed == total

if __name__ == "__main__":
    success = run_verification()
    exit(0 if success else 1)