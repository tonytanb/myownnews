#!/usr/bin/env python3
"""
Quick Deployment Check for Consolidated Architecture
Validates the current deployment is working properly
"""

import requests
import json
import time
import os
import sys
from datetime import datetime

# Configuration
API_BASE_URL = os.getenv('API_URL', 'https://nqot0dir0h.execute-api.us-west-2.amazonaws.com/prod')

def quick_deployment_check():
    """Quick check of deployed consolidated system"""
    print("🚀 Quick Deployment Check for Consolidated Architecture")
    print(f"API URL: {API_BASE_URL}")
    print("=" * 60)
    
    session = requests.Session()
    issues = []
    checks_passed = 0
    total_checks = 0
    
    # Check 1: Bootstrap endpoint responds
    total_checks += 1
    try:
        print("1. Testing bootstrap endpoint...")
        response = session.get(f"{API_BASE_URL}/bootstrap", timeout=10)
        
        if response.status_code != 200:
            issues.append(f"Bootstrap HTTP {response.status_code}")
        else:
            data = response.json()
            if data.get('script') and data.get('sources'):
                print("   ✅ Bootstrap endpoint working")
                checks_passed += 1
            else:
                issues.append("Bootstrap missing required fields")
    except Exception as e:
        issues.append(f"Bootstrap error: {str(e)}")
    
    # Check 2: Generate-fresh endpoint responds
    total_checks += 1
    try:
        print("2. Testing generate-fresh endpoint...")
        response = session.post(f"{API_BASE_URL}/generate-fresh", timeout=15)
        
        if response.status_code != 200:
            issues.append(f"Generate-fresh HTTP {response.status_code}")
        else:
            data = response.json()
            if data.get('runId'):
                print("   ✅ Generate-fresh endpoint working")
                checks_passed += 1
            else:
                issues.append("Generate-fresh missing runId")
    except Exception as e:
        issues.append(f"Generate-fresh error: {str(e)}")
    
    # Check 3: Latest endpoint responds
    total_checks += 1
    try:
        print("3. Testing latest endpoint...")
        response = session.get(f"{API_BASE_URL}/latest", timeout=10)
        
        if response.status_code != 200:
            issues.append(f"Latest HTTP {response.status_code}")
        else:
            data = response.json()
            if data.get('script'):
                print("   ✅ Latest endpoint working")
                checks_passed += 1
            else:
                issues.append("Latest missing script")
    except Exception as e:
        issues.append(f"Latest error: {str(e)}")
    
    # Check 4: CORS headers present
    total_checks += 1
    try:
        print("4. Testing CORS headers...")
        response = session.options(f"{API_BASE_URL}/bootstrap", timeout=10)
        
        if response.status_code not in [200, 204]:
            issues.append(f"CORS OPTIONS HTTP {response.status_code}")
        else:
            headers = response.headers
            if 'Access-Control-Allow-Origin' in headers:
                print("   ✅ CORS headers present")
                checks_passed += 1
            else:
                issues.append("Missing CORS headers")
    except Exception as e:
        issues.append(f"CORS error: {str(e)}")
    
    # Check 5: Error handling works
    total_checks += 1
    try:
        print("5. Testing error handling...")
        response = session.get(f"{API_BASE_URL}/invalid-endpoint", timeout=10)
        
        if response.status_code in [403, 404]:
            print("   ✅ Error handling working")
            checks_passed += 1
        else:
            issues.append(f"Unexpected error response: {response.status_code}")
    except Exception as e:
        issues.append(f"Error handling test failed: {str(e)}")
    
    # Summary
    success_rate = (checks_passed / total_checks) * 100 if total_checks > 0 else 0
    
    print("\n" + "=" * 60)
    print("📊 Deployment Check Results")
    print("=" * 60)
    print(f"Checks Passed: {checks_passed}/{total_checks}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if issues:
        print(f"\n❌ ISSUES FOUND ({len(issues)}):")
        for issue in issues:
            print(f"  - {issue}")
    
    if success_rate >= 80:
        print("\n✅ DEPLOYMENT CHECK: PASSED")
        print("🚀 Consolidated architecture is deployed and working!")
        return True
    else:
        print("\n❌ DEPLOYMENT CHECK: FAILED")
        print("⚠️ Some critical issues need attention")
        return False

if __name__ == "__main__":
    success = quick_deployment_check()
    sys.exit(0 if success else 1)