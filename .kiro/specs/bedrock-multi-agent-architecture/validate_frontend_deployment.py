#!/usr/bin/env python3
"""
Validate Frontend Deployment
Check if the new frontend build is deployed and accessible
"""

import requests
import json
from datetime import datetime

def validate_frontend():
    """Validate the frontend deployment"""
    url = "http://curio-news-frontend-1760997974.s3-website-us-west-2.amazonaws.com/"
    
    print("=" * 80)
    print("FRONTEND DEPLOYMENT VALIDATION")
    print("=" * 80)
    print(f"\nChecking: {url}")
    print()
    
    try:
        # Fetch the HTML
        response = requests.get(url, headers={'Cache-Control': 'no-cache'})
        html = response.text
        
        # Check for the new JS bundle
        if 'main.3eab7ce1.js' in html:
            print("✅ New JavaScript bundle detected (main.3eab7ce1.js)")
        else:
            print("❌ Old JavaScript bundle still present")
            
        # Check for the new CSS
        if 'main.6cff8c6d.css' in html:
            print("✅ New CSS bundle detected (main.6cff8c6d.css)")
        else:
            print("❌ Old CSS bundle still present")
            
        # Fetch the JS bundle to check for components
        if 'main.3eab7ce1.js' in html:
            js_url = f"{url}static/js/main.3eab7ce1.js"
            js_response = requests.get(js_url, headers={'Cache-Control': 'no-cache'})
            js_content = js_response.text
            
            components_to_check = [
                'AgentCollaborationTrace',
                'AgentFlowDiagram',
                'PerformanceMonitor',
                'DebuggingDashboard'
            ]
            
            print("\nComponent Check:")
            for component in components_to_check:
                if component in js_content:
                    print(f"  ✅ {component} found in bundle")
                else:
                    print(f"  ❌ {component} NOT found in bundle")
        
        # Check API connectivity
        print("\nAPI Connectivity:")
        api_url = "https://nqot0dir0h.execute-api.us-west-2.amazonaws.com/prod/latest"
        api_response = requests.get(api_url, timeout=10)
        if api_response.status_code == 200:
            print(f"  ✅ API responding (HTTP {api_response.status_code})")
            data = api_response.json()
            if 'agent_trace' in data or 'orchestration_trace' in data:
                print("  ✅ API includes agent trace data")
            else:
                print("  ⚠️  API response missing agent trace data")
        else:
            print(f"  ❌ API error (HTTP {api_response.status_code})")
            
        print("\n" + "=" * 80)
        print("INSTRUCTIONS FOR VIEWING CHANGES:")
        print("=" * 80)
        print("\n1. Clear your browser cache:")
        print("   - Chrome/Edge: Ctrl+Shift+Delete (Cmd+Shift+Delete on Mac)")
        print("   - Firefox: Ctrl+Shift+Delete (Cmd+Shift+Delete on Mac)")
        print("   - Safari: Cmd+Option+E")
        print("\n2. Hard refresh the page:")
        print("   - Chrome/Firefox: Ctrl+F5 or Ctrl+Shift+R")
        print("   - Mac: Cmd+Shift+R")
        print("\n3. Enable Demo Mode:")
        print("   - Click the '🎬 Demo Mode' button in the top right")
        print("   - This will show the Agent Collaboration Trace")
        print("\n4. Or wait for content generation:")
        print("   - The trace appears automatically during generation")
        print("   - Or when there's orchestration trace data")
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == '__main__':
    validate_frontend()
