#!/usr/bin/env python3
"""
Quick Validation Script for Curio Core Fixes
Provides fast validation of critical system components
"""

import requests
import json
import time
import os
from datetime import datetime

# Configuration
API_BASE_URL = os.getenv('API_URL', 'https://nqot0dir0h.execute-api.us-west-2.amazonaws.com/prod')

def quick_health_check():
    """Quick health check of critical components"""
    print("🏥 Quick Health Check")
    print("=" * 40)
    
    session = requests.Session()
    issues = []
    
    try:
        # Test bootstrap endpoint
        print("Testing bootstrap endpoint...")
        response = session.get(f"{API_BASE_URL}/bootstrap", timeout=10)
        
        if response.status_code != 200:
            issues.append(f"Bootstrap HTTP {response.status_code}")
        else:
            data = response.json()
            
            # Check audio URL
            audio_url = data.get('audioUrl')
            if audio_url:
                try:
                    audio_response = session.head(audio_url, timeout=5)
                    if audio_response.status_code not in [200, 206]:
                        issues.append(f"Audio HTTP {audio_response.status_code}")
                    else:
                        print("✅ Audio URL accessible")
                except:
                    issues.append("Audio URL network error")
            else:
                issues.append("No audio URL")
            
            # Check agent outputs
            agent_outputs = data.get('agentOutputs', {})
            if not agent_outputs:
                issues.append("No agent outputs")
            else:
                agent_count = len([k for k, v in agent_outputs.items() if v])
                print(f"✅ Agent outputs: {agent_count} sections")
            
            # Check word timings
            word_timings = data.get('word_timings', [])
            script = data.get('script', '')
            if script and word_timings:
                script_words = len(script.split())
                timing_ratio = len(word_timings) / script_words if script_words > 0 else 0
                if timing_ratio < 0.5:
                    issues.append(f"Insufficient word timings: {len(word_timings)}/{script_words}")
                else:
                    print(f"✅ Word timings: {len(word_timings)}/{script_words} words")
            else:
                issues.append("Missing script or word timings")
    
    except Exception as e:
        issues.append(f"Bootstrap error: {str(e)}")
    
    # Summary
    print("\n" + "=" * 40)
    if issues:
        print("❌ ISSUES FOUND:")
        for issue in issues:
            print(f"  - {issue}")
        print(f"\nStatus: {len(issues)} issues need attention")
    else:
        print("✅ ALL CHECKS PASSED")
        print("Status: System appears healthy")
    
    return len(issues) == 0

if __name__ == "__main__":
    success = quick_health_check()
    exit(0 if success else 1)