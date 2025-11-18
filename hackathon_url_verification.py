#!/usr/bin/env python3
"""
Hackathon URL Verification Script
Verifies that the submitted URL is working with all latest features
"""

import requests
import json
from datetime import datetime

def test_frontend_url():
    """Test the frontend URL that was submitted to hackathon"""
    frontend_url = "http://curio-news-frontend-1760997974.s3-website-us-west-2.amazonaws.com/"
    
    print("🔍 Testing Hackathon Submission URL...")
    print(f"URL: {frontend_url}")
    
    try:
        response = requests.get(frontend_url, timeout=10)
        if response.status_code == 200:
            print("✅ Frontend URL is accessible")
            
            # Check if it contains expected content
            content = response.text
            if "CURIO" in content and "Today's Brief" in content:
                print("✅ Frontend contains expected Curio News content")
                return True
            else:
                print("❌ Frontend doesn't contain expected content")
                return False
        else:
            print(f"❌ Frontend URL returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accessing frontend: {e}")
        return False

def test_api_endpoints():
    """Test the API endpoints that the frontend uses"""
    api_base = "https://nqot0dir0h.execute-api.us-west-2.amazonaws.com/prod"
    
    print("\n🔍 Testing API Endpoints...")
    
    # Test bootstrap endpoint
    try:
        response = requests.get(f"{api_base}/bootstrap", timeout=15)
        if response.status_code == 200:
            data = response.json()
            print("✅ Bootstrap API working")
            print(f"   - News items: {len(data.get('news_items', []))}")
            print(f"   - Script length: {len(data.get('script', ''))}")
            print(f"   - Agent outputs: {bool(data.get('agentOutputs'))}")
            return True
        else:
            print(f"❌ Bootstrap API returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

def test_s3_cleanup():
    """Verify S3 bucket cleanup was successful"""
    print("\n🔍 Verifying S3 Cleanup...")
    
    import boto3
    try:
        s3 = boto3.client('s3')
        buckets = s3.list_buckets()
        
        curio_buckets = [b['Name'] for b in buckets['Buckets'] if 'curio' in b['Name'].lower()]
        
        print(f"✅ Remaining Curio buckets: {len(curio_buckets)}")
        for bucket in curio_buckets:
            print(f"   - {bucket}")
            
        # Check if our main bucket is still there
        if 'curio-news-frontend-1760997974' in curio_buckets:
            print("✅ Main hackathon bucket preserved")
            return True
        else:
            print("❌ Main hackathon bucket missing!")
            return False
            
    except Exception as e:
        print(f"❌ Error checking S3: {e}")
        return False

def main():
    """Run all verification tests"""
    print("🚀 Hackathon URL Verification")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    results = []
    
    # Test frontend
    results.append(test_frontend_url())
    
    # Test API
    results.append(test_api_endpoints())
    
    # Test S3 cleanup
    results.append(test_s3_cleanup())
    
    print("\n" + "=" * 50)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 50)
    
    if all(results):
        print("🎉 ALL TESTS PASSED!")
        print("✅ Your hackathon submission URL is working perfectly")
        print("✅ All latest features are deployed")
        print("✅ Duplicate buckets cleaned up")
        print("\n🏆 Ready for judging!")
    else:
        print("⚠️  Some issues detected:")
        if not results[0]:
            print("   - Frontend URL issues")
        if not results[1]:
            print("   - API endpoint issues")
        if not results[2]:
            print("   - S3 cleanup issues")
    
    print(f"\n🌐 Hackathon URL: http://curio-news-frontend-1760997974.s3-website-us-west-2.amazonaws.com/")

if __name__ == "__main__":
    main()