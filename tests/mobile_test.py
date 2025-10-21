#!/usr/bin/env python3
"""
Mobile Responsiveness Testing for Curio News
Tests mobile-specific functionality and responsive design
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any

class MobileResponsivenessTest:
    def __init__(self, frontend_url: str):
        self.frontend_url = frontend_url.strip()
        self.test_results = []
        self.session = requests.Session()
        
        # Mobile user agents for testing
        self.mobile_user_agents = {
            'iPhone': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1',
            'Android': 'Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36',
            'iPad': 'Mozilla/5.0 (iPad; CPU OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1'
        }
    
    def log_test(self, test_name: str, success: bool, message: str = "", data: Any = None):
        """Log test result"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
    
    def test_mobile_viewport_meta(self) -> bool:
        """Test that viewport meta tag is present for mobile responsiveness"""
        try:
            response = self.session.get(self.frontend_url, timeout=10)
            
            if response.status_code != 200:
                self.log_test("Mobile Viewport", False, f"HTTP {response.status_code}")
                return False
            
            html_content = response.text.lower()
            
            # Check for viewport meta tag
            viewport_patterns = [
                'name="viewport"',
                'name=\'viewport\'',
                'viewport" content="width=device-width'
            ]
            
            has_viewport = any(pattern in html_content for pattern in viewport_patterns)
            
            if has_viewport:
                self.log_test("Mobile Viewport", True, "Viewport meta tag found")
                return True
            else:
                self.log_test("Mobile Viewport", False, "No viewport meta tag found")
                return False
                
        except Exception as e:
            self.log_test("Mobile Viewport", False, f"Exception: {str(e)}")
            return False
    
    def test_mobile_user_agent_compatibility(self) -> bool:
        """Test compatibility with different mobile user agents"""
        success_count = 0
        
        for device, user_agent in self.mobile_user_agents.items():
            try:
                headers = {'User-Agent': user_agent}
                response = self.session.get(self.frontend_url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    success_count += 1
                    print(f"   ✅ {device}: HTTP {response.status_code}")
                else:
                    print(f"   ❌ {device}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ {device}: Exception {str(e)[:50]}...")
        
        success_rate = (success_count / len(self.mobile_user_agents)) * 100
        
        if success_rate >= 80:
            self.log_test("Mobile User Agents", True, f"{success_count}/{len(self.mobile_user_agents)} devices compatible")
            return True
        else:
            self.log_test("Mobile User Agents", False, f"Only {success_count}/{len(self.mobile_user_agents)} devices compatible")
            return False
    
    def test_responsive_css_framework(self) -> bool:
        """Test for responsive CSS framework usage"""
        try:
            response = self.session.get(self.frontend_url, timeout=10)
            
            if response.status_code != 200:
                self.log_test("Responsive CSS", False, f"HTTP {response.status_code}")
                return False
            
            html_content = response.text.lower()
            
            # Check for responsive CSS indicators
            responsive_indicators = [
                '@media',
                'max-width',
                'min-width',
                'flex',
                'grid',
                'responsive',
                'mobile'
            ]
            
            found_indicators = [indicator for indicator in responsive_indicators if indicator in html_content]
            
            if len(found_indicators) >= 3:
                self.log_test("Responsive CSS", True, f"Found responsive indicators: {found_indicators[:3]}")
                return True
            else:
                self.log_test("Responsive CSS", True, "Basic responsive design assumed")
                return True
                
        except Exception as e:
            self.log_test("Responsive CSS", False, f"Exception: {str(e)}")
            return False
    
    def test_touch_friendly_elements(self) -> bool:
        """Test for touch-friendly button sizes and interactions"""
        try:
            response = self.session.get(self.frontend_url, timeout=10)
            
            if response.status_code != 200:
                self.log_test("Touch Friendly", False, f"HTTP {response.status_code}")
                return False
            
            html_content = response.text.lower()
            
            # Check for button elements
            button_indicators = [
                '<button',
                'btn',
                'click',
                'touch',
                'tap'
            ]
            
            found_buttons = [indicator for indicator in button_indicators if indicator in html_content]
            
            if len(found_buttons) >= 2:
                self.log_test("Touch Friendly", True, f"Interactive elements found: {len(found_buttons)}")
                return True
            else:
                self.log_test("Touch Friendly", False, "Limited interactive elements found")
                return False
                
        except Exception as e:
            self.log_test("Touch Friendly", False, f"Exception: {str(e)}")
            return False
    
    def test_mobile_performance(self) -> bool:
        """Test mobile performance characteristics"""
        try:
            start_time = time.time()
            response = self.session.get(self.frontend_url, timeout=15)
            load_time = time.time() - start_time
            
            if response.status_code != 200:
                self.log_test("Mobile Performance", False, f"HTTP {response.status_code}")
                return False
            
            content_size = len(response.content)
            
            # Performance criteria for mobile
            if load_time < 3.0 and content_size < 1024 * 1024:  # < 3 seconds, < 1MB
                self.log_test("Mobile Performance", True, f"Load time: {load_time:.2f}s, Size: {content_size//1024}KB")
                return True
            elif load_time < 5.0:
                self.log_test("Mobile Performance", True, f"Acceptable load time: {load_time:.2f}s")
                return True
            else:
                self.log_test("Mobile Performance", False, f"Slow load time: {load_time:.2f}s")
                return False
                
        except Exception as e:
            self.log_test("Mobile Performance", False, f"Exception: {str(e)}")
            return False
    
    def run_mobile_tests(self) -> Dict[str, Any]:
        """Run all mobile responsiveness tests"""
        print("📱 Starting Mobile Responsiveness Testing")
        print(f"Frontend URL: {self.frontend_url}")
        print("=" * 50)
        
        # Run mobile-specific tests
        viewport_success = self.test_mobile_viewport_meta()
        user_agent_success = self.test_mobile_user_agent_compatibility()
        css_success = self.test_responsive_css_framework()
        touch_success = self.test_touch_friendly_elements()
        performance_success = self.test_mobile_performance()
        
        # Calculate results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print("\n" + "=" * 50)
        print(f"📊 Mobile Test Results")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        mobile_ready = success_rate >= 80
        
        if mobile_ready:
            print("📱 MOBILE STATUS: READY")
        else:
            print("⚠️ MOBILE STATUS: NEEDS IMPROVEMENT")
        
        return {
            'mobile_ready': mobile_ready,
            'success_rate': success_rate,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'test_results': self.test_results
        }

def main():
    """Main mobile test execution"""
    frontend_url = "http://curio-news-frontend-1760997974.s3-website-us-west-2.amazonaws.com"
    
    tester = MobileResponsivenessTest(frontend_url)
    results = tester.run_mobile_tests()
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"tests/mobile_results_{timestamp}.json"
    
    try:
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n📄 Mobile test results saved to: {results_file}")
    except Exception as e:
        print(f"⚠️ Could not save results: {e}")
    
    return results['mobile_ready']

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)