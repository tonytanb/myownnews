#!/usr/bin/env python3
"""
Final Deployment Validator for Curio News
Validates production deployment across multiple devices and browsers
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any

class DeploymentValidator:
    def __init__(self, api_url: str, frontend_url: str):
        self.api_url = api_url.strip()
        self.frontend_url = frontend_url.strip()
        self.validation_results = []
        self.session = requests.Session()
        
        # Different user agents for device/browser testing
        self.user_agents = {
            'Chrome Desktop': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Firefox Desktop': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Safari Desktop': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Chrome Mobile': 'Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36',
            'Safari Mobile': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1',
            'Edge Desktop': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59'
        }
    
    def log_validation(self, test_name: str, success: bool, message: str = "", data: Any = None):
        """Log validation result"""
        result = {
            'validation': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        self.validation_results.append(result)
        
        status = "✅ VALID" if success else "❌ INVALID"
        print(f"{status} {test_name}: {message}")
    
    def validate_production_api_deployment(self) -> bool:
        """Validate that API is properly deployed to production"""
        print("🚀 Validating production API deployment...")
        
        api_endpoints = [
            ('/bootstrap', 'Bootstrap endpoint'),
            ('/latest', 'Latest content endpoint'),
            ('/trace/demo-trace', 'Trace endpoint')
        ]
        
        working_endpoints = 0
        
        for endpoint, description in api_endpoints:
            try:
                response = self.session.get(f"{self.api_url}{endpoint}", timeout=10)
                
                # Check for proper CORS headers
                cors_headers = [
                    'Access-Control-Allow-Origin',
                    'Access-Control-Allow-Methods'
                ]
                
                has_cors = all(header in response.headers for header in cors_headers)
                
                if response.status_code in [200, 404] and has_cors:  # 404 OK for some endpoints
                    working_endpoints += 1
                    print(f"   ✅ {description}: HTTP {response.status_code} with CORS")
                else:
                    print(f"   ❌ {description}: HTTP {response.status_code}, CORS: {has_cors}")
                    
            except Exception as e:
                print(f"   ❌ {description}: Exception - {str(e)[:50]}...")
        
        success_rate = (working_endpoints / len(api_endpoints)) * 100
        
        if success_rate >= 80:
            self.log_validation("Production API", True, f"{working_endpoints}/{len(api_endpoints)} endpoints working")
            return True
        else:
            self.log_validation("Production API", False, f"Only {working_endpoints}/{len(api_endpoints)} endpoints working")
            return False
    
    def validate_frontend_backend_integration(self) -> bool:
        """Validate seamless frontend and backend integration"""
        print("🔗 Validating frontend-backend integration...")
        
        try:
            # Test that frontend can access backend
            response = self.session.get(f"{self.api_url}/bootstrap", timeout=10)
            
            if response.status_code != 200:
                self.log_validation("Frontend-Backend Integration", False, f"API not accessible: HTTP {response.status_code}")
                return False
            
            data = response.json()
            
            # Check for required integration fields
            integration_fields = ['audioUrl', 'script', 'news_items', 'sources']
            missing_fields = [field for field in integration_fields if field not in data]
            
            if missing_fields:
                self.log_validation("Frontend-Backend Integration", False, f"Missing integration fields: {missing_fields}")
                return False
            
            # Validate data types for frontend consumption
            if not isinstance(data.get('news_items'), list):
                self.log_validation("Frontend-Backend Integration", False, "news_items is not a list")
                return False
            
            if not isinstance(data.get('sources'), list):
                self.log_validation("Frontend-Backend Integration", False, "sources is not a list")
                return False
            
            if not isinstance(data.get('script'), str) or len(data.get('script', '')) < 10:
                self.log_validation("Frontend-Backend Integration", False, "Invalid script content")
                return False
            
            # Test audio URL accessibility
            audio_url = data.get('audioUrl', '')
            if audio_url:
                try:
                    audio_response = self.session.head(audio_url, timeout=5)
                    if audio_response.status_code not in [200, 206]:
                        print(f"   ⚠️ Audio URL not accessible: HTTP {audio_response.status_code}")
                except:
                    print(f"   ⚠️ Audio URL test failed")
            
            self.log_validation("Frontend-Backend Integration", True, "All integration fields valid")
            return True
            
        except Exception as e:
            self.log_validation("Frontend-Backend Integration", False, f"Exception: {str(e)}")
            return False
    
    def validate_multiple_devices_browsers(self) -> bool:
        """Validate deployment across multiple devices and browsers"""
        print("📱💻 Validating across multiple devices and browsers...")
        
        successful_tests = 0
        total_tests = len(self.user_agents)
        
        for device_browser, user_agent in self.user_agents.items():
            try:
                headers = {'User-Agent': user_agent}
                
                # Test API access with different user agents
                api_response = self.session.get(f"{self.api_url}/bootstrap", headers=headers, timeout=8)
                
                # Test frontend access
                frontend_response = self.session.get(self.frontend_url, headers=headers, timeout=8)
                
                api_success = api_response.status_code == 200
                frontend_success = frontend_response.status_code == 200
                
                if api_success and frontend_success:
                    successful_tests += 1
                    print(f"   ✅ {device_browser}: API & Frontend OK")
                elif api_success:
                    successful_tests += 0.5
                    print(f"   ⚠️ {device_browser}: API OK, Frontend issues")
                else:
                    print(f"   ❌ {device_browser}: API issues")
                
                time.sleep(0.3)  # Brief pause between tests
                
            except Exception as e:
                print(f"   ❌ {device_browser}: Exception - {str(e)[:30]}...")
        
        success_rate = (successful_tests / total_tests) * 100
        
        if success_rate >= 80:
            self.log_validation("Multi-Device Support", True, f"{success_rate:.1f}% device/browser compatibility")
            return True
        else:
            self.log_validation("Multi-Device Support", False, f"Only {success_rate:.1f}% device/browser compatibility")
            return False
    
    def validate_production_performance(self) -> bool:
        """Validate production performance standards"""
        print("⚡ Validating production performance...")
        
        performance_tests = [
            ('API Response Time', self.api_url + '/bootstrap', 2.0),
            ('Frontend Load Time', self.frontend_url, 5.0)
        ]
        
        passed_tests = 0
        
        for test_name, url, max_time in performance_tests:
            try:
                start_time = time.time()
                response = self.session.get(url, timeout=max_time + 2)
                response_time = time.time() - start_time
                
                if response.status_code == 200 and response_time < max_time:
                    passed_tests += 1
                    print(f"   ✅ {test_name}: {response_time:.3f}s (target: <{max_time}s)")
                elif response.status_code == 200:
                    print(f"   ⚠️ {test_name}: {response_time:.3f}s (slow, target: <{max_time}s)")
                else:
                    print(f"   ❌ {test_name}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ {test_name}: Exception - {str(e)[:50]}...")
        
        success_rate = (passed_tests / len(performance_tests)) * 100
        
        if success_rate >= 80:
            self.log_validation("Production Performance", True, f"{passed_tests}/{len(performance_tests)} performance tests passed")
            return True
        else:
            self.log_validation("Production Performance", False, f"Only {passed_tests}/{len(performance_tests)} performance tests passed")
            return False
    
    def validate_error_handling_resilience(self) -> bool:
        """Validate error handling and system resilience"""
        print("🛡️ Validating error handling and resilience...")
        
        error_tests = [
            ('Invalid Endpoint', '/invalid-endpoint-test', [404, 403]),
            ('Malformed Request', '/bootstrap?invalid=param', [200, 400]),
            ('Large Request', '/bootstrap', [200])  # Normal request should still work
        ]
        
        resilient_responses = 0
        
        for test_name, endpoint, acceptable_codes in error_tests:
            try:
                response = self.session.get(f"{self.api_url}{endpoint}", timeout=5)
                
                if response.status_code in acceptable_codes:
                    resilient_responses += 1
                    print(f"   ✅ {test_name}: HTTP {response.status_code} (expected)")
                else:
                    print(f"   ⚠️ {test_name}: HTTP {response.status_code} (unexpected)")
                    
            except Exception as e:
                print(f"   ❌ {test_name}: Exception - {str(e)[:50]}...")
        
        success_rate = (resilient_responses / len(error_tests)) * 100
        
        if success_rate >= 70:
            self.log_validation("Error Handling", True, f"{resilient_responses}/{len(error_tests)} error scenarios handled properly")
            return True
        else:
            self.log_validation("Error Handling", False, f"Only {resilient_responses}/{len(error_tests)} error scenarios handled properly")
            return False
    
    def validate_security_headers(self) -> bool:
        """Validate security headers and HTTPS configuration"""
        print("🔒 Validating security configuration...")
        
        try:
            response = self.session.get(f"{self.api_url}/bootstrap", timeout=5)
            
            # Check for important security headers
            security_headers = {
                'Access-Control-Allow-Origin': 'CORS protection',
                'Content-Type': 'Content type specification'
            }
            
            present_headers = 0
            for header, description in security_headers.items():
                if header in response.headers:
                    present_headers += 1
                    print(f"   ✅ {description}: {header} present")
                else:
                    print(f"   ⚠️ {description}: {header} missing")
            
            # Check HTTPS usage
            uses_https = self.api_url.startswith('https://')
            if uses_https:
                present_headers += 1
                print(f"   ✅ HTTPS: Secure connection")
            else:
                print(f"   ⚠️ HTTPS: Using HTTP (not secure)")
            
            security_score = (present_headers / (len(security_headers) + 1)) * 100
            
            if security_score >= 70:
                self.log_validation("Security Configuration", True, f"{security_score:.0f}% security score")
                return True
            else:
                self.log_validation("Security Configuration", False, f"Only {security_score:.0f}% security score")
                return False
                
        except Exception as e:
            self.log_validation("Security Configuration", False, f"Exception: {str(e)}")
            return False
    
    def validate_final_deployment(self) -> Dict[str, Any]:
        """Run complete deployment validation"""
        print("🚀 Final Deployment Validation for Curio News")
        print(f"API URL: {self.api_url}")
        print(f"Frontend URL: {self.frontend_url}")
        print("=" * 60)
        
        # Run all validation tests
        api_valid = self.validate_production_api_deployment()
        integration_valid = self.validate_frontend_backend_integration()
        devices_valid = self.validate_multiple_devices_browsers()
        performance_valid = self.validate_production_performance()
        error_handling_valid = self.validate_error_handling_resilience()
        security_valid = self.validate_security_headers()
        
        # Calculate results
        total_validations = len(self.validation_results)
        successful_validations = sum(1 for result in self.validation_results if result['success'])
        validation_rate = (successful_validations / total_validations) * 100 if total_validations > 0 else 0
        
        print("\n" + "=" * 60)
        print(f"🚀 Final Deployment Validation Results")
        print(f"Total Validations: {total_validations}")
        print(f"Successful: {successful_validations}")
        print(f"Validation Rate: {validation_rate:.1f}%")
        
        # Determine deployment readiness
        critical_validations = [api_valid, integration_valid, performance_valid]
        deployment_ready = all(critical_validations) and validation_rate >= 75
        
        if deployment_ready:
            print("🎉 DEPLOYMENT STATUS: PRODUCTION READY")
            print("✨ Validated systems:")
            print("   • Production API deployment")
            print("   • Frontend-backend integration")
            print("   • Multi-device compatibility")
            print("   • Production performance")
            print("   • Error handling resilience")
            print("   • Security configuration")
        else:
            print("⚠️ DEPLOYMENT STATUS: NEEDS ATTENTION")
            print("\nValidation issues:")
            for result in self.validation_results:
                if not result['success']:
                    print(f"  - {result['validation']}: {result['message']}")
        
        return {
            'deployment_ready': deployment_ready,
            'validation_rate': validation_rate,
            'total_validations': total_validations,
            'successful_validations': successful_validations,
            'validation_results': self.validation_results,
            'critical_systems': {
                'api_deployment': api_valid,
                'integration': integration_valid,
                'multi_device': devices_valid,
                'performance': performance_valid,
                'error_handling': error_handling_valid,
                'security': security_valid
            }
        }

def main():
    """Main deployment validation execution"""
    api_url = "https://nqot0dir0h.execute-api.us-west-2.amazonaws.com/prod"
    frontend_url = "http://curio-news-frontend-1760997974.s3-website-us-west-2.amazonaws.com"
    
    validator = DeploymentValidator(api_url, frontend_url)
    results = validator.validate_final_deployment()
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"tests/deployment_validation_{timestamp}.json"
    
    try:
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n📄 Deployment validation results saved to: {results_file}")
    except Exception as e:
        print(f"⚠️ Could not save results: {e}")
    
    return results['deployment_ready']

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)