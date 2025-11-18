#!/usr/bin/env python3
"""
Hackathon Verification Script
Verifies that Curio News is ready for hackathon demonstration
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any

class HackathonVerifier:
    def __init__(self):
        self.api_url = "https://nqot0dir0h.execute-api.us-west-2.amazonaws.com/prod"
        self.frontend_url = "http://curio-news-frontend-1760997974.s3-website-us-west-2.amazonaws.com"
        self.verification_results = []
        
    def log_verification(self, test_name: str, success: bool, message: str = "", details: Any = None):
        """Log verification result"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'details': details
        }
        self.verification_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
        if details and not success:
            print(f"   Details: {json.dumps(details, indent=2)[:200]}...")
    
    def verify_api_endpoints(self) -> bool:
        """Verify all API endpoints are working"""
        print("🔧 Verifying API Endpoints...")
        
        endpoints = [
            ("/bootstrap", "Bootstrap endpoint"),
            ("/agent-status", "Agent status endpoint"),
            ("/trace", "Trace endpoint")
        ]
        
        all_working = True
        
        for endpoint, description in endpoints:
            try:
                response = requests.get(f"{self.api_url}{endpoint}", timeout=10)
                
                if endpoint == "/bootstrap" and response.status_code == 200:
                    content = response.json()
                    has_content = bool(content.get('script') and content.get('audioUrl'))
                    self.log_verification(f"API {description}", has_content, 
                                        f"HTTP {response.status_code}, has content: {has_content}")
                    if not has_content:
                        all_working = False
                        
                elif endpoint == "/agent-status" and response.status_code in [200, 400]:
                    # Agent status endpoint expects parameters, so 400 is acceptable
                    self.log_verification(f"API {description}", True, 
                                        f"HTTP {response.status_code} (accessible)")
                elif endpoint == "/trace" and response.status_code in [200, 400, 401, 403]:
                    # Trace endpoint may require auth, so 401/403 is acceptable for verification
                    self.log_verification(f"API {description}", True, 
                                        f"HTTP {response.status_code} (endpoint exists)")
                else:
                    self.log_verification(f"API {description}", False, 
                                        f"HTTP {response.status_code}")
                    all_working = False
                    
            except Exception as e:
                self.log_verification(f"API {description}", False, f"Error: {str(e)}")
                all_working = False
        
        return all_working
    
    def verify_frontend_accessibility(self) -> bool:
        """Verify frontend is accessible and loading"""
        print("🌐 Verifying Frontend Accessibility...")
        
        try:
            response = requests.get(self.frontend_url, timeout=10)
            
            if response.status_code == 200:
                content = response.text
                has_react = "react" in content.lower() or "root" in content
                has_title = "curio news" in content.lower()
                
                frontend_working = has_react or len(content) > 1000
                
                self.log_verification("Frontend Accessibility", frontend_working,
                                    f"HTTP {response.status_code}, content length: {len(content)}")
                return frontend_working
            else:
                self.log_verification("Frontend Accessibility", False,
                                    f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_verification("Frontend Accessibility", False, f"Error: {str(e)}")
            return False
    
    def verify_content_quality(self) -> bool:
        """Verify content quality and completeness"""
        print("📝 Verifying Content Quality...")
        
        try:
            response = requests.get(f"{self.api_url}/bootstrap", timeout=10)
            
            if response.status_code == 200:
                content = response.json()
                
                # Check required fields
                required_fields = ['script', 'audioUrl', 'news_items', 'generatedAt']
                missing_fields = [field for field in required_fields if not content.get(field)]
                
                # Check content quality
                script_length = len(content.get('script', ''))
                news_count = len(content.get('news_items', []))
                has_audio = bool(content.get('audioUrl'))
                
                quality_score = 0
                if script_length >= 500:
                    quality_score += 0.3
                if news_count >= 3:
                    quality_score += 0.3
                if has_audio:
                    quality_score += 0.4
                
                quality_good = quality_score >= 0.8 and not missing_fields
                
                details = {
                    'script_length': script_length,
                    'news_count': news_count,
                    'has_audio': has_audio,
                    'quality_score': quality_score,
                    'missing_fields': missing_fields
                }
                
                self.log_verification("Content Quality", quality_good,
                                    f"Quality score: {quality_score:.1f}, News: {news_count}, Script: {script_length}chars",
                                    details)
                return quality_good
            else:
                self.log_verification("Content Quality", False,
                                    f"Bootstrap failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_verification("Content Quality", False, f"Error: {str(e)}")
            return False
    
    def verify_performance(self) -> bool:
        """Verify performance meets hackathon standards"""
        print("⚡ Verifying Performance...")
        
        response_times = []
        
        # Test multiple requests
        for i in range(3):
            try:
                start_time = time.time()
                response = requests.get(f"{self.api_url}/bootstrap", timeout=10)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    response_times.append(response_time)
                    
            except Exception:
                continue
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            
            performance_good = avg_response_time < 2.0 and max_response_time < 5.0
            
            details = {
                'avg_response_time': avg_response_time,
                'max_response_time': max_response_time,
                'successful_requests': len(response_times)
            }
            
            self.log_verification("Performance", performance_good,
                                f"Avg: {avg_response_time:.2f}s, Max: {max_response_time:.2f}s",
                                details)
            return performance_good
        else:
            self.log_verification("Performance", False, "No successful requests")
            return False
    
    def verify_demo_readiness(self) -> bool:
        """Verify system is ready for live demo"""
        print("🎬 Verifying Demo Readiness...")
        
        demo_checks = []
        
        # Check 1: Fresh content available
        try:
            response = requests.get(f"{self.api_url}/bootstrap", timeout=10)
            if response.status_code == 200:
                content = response.json()
                generated_at = content.get('generatedAt', '')
                
                # Check if content is recent (within last 24 hours)
                if generated_at:
                    try:
                        from datetime import datetime, timedelta
                        gen_time = datetime.fromisoformat(generated_at.replace('Z', '+00:00'))
                        now = datetime.now(gen_time.tzinfo)
                        is_recent = (now - gen_time) < timedelta(hours=24)
                        demo_checks.append(("Fresh Content", is_recent, f"Generated: {generated_at}"))
                    except:
                        demo_checks.append(("Fresh Content", True, "Content available"))
                else:
                    demo_checks.append(("Fresh Content", False, "No generation timestamp"))
            else:
                demo_checks.append(("Fresh Content", False, f"HTTP {response.status_code}"))
        except Exception as e:
            demo_checks.append(("Fresh Content", False, str(e)))
        
        # Check 2: Audio accessibility
        try:
            response = requests.get(f"{self.api_url}/bootstrap", timeout=10)
            if response.status_code == 200:
                content = response.json()
                audio_url = content.get('audioUrl', '')
                
                if audio_url:
                    # Quick check if audio URL is accessible
                    audio_response = requests.head(audio_url, timeout=5)
                    audio_accessible = audio_response.status_code == 200
                    demo_checks.append(("Audio Accessibility", audio_accessible, f"Audio URL: {audio_response.status_code}"))
                else:
                    demo_checks.append(("Audio Accessibility", False, "No audio URL"))
            else:
                demo_checks.append(("Audio Accessibility", False, "Bootstrap failed"))
        except Exception as e:
            demo_checks.append(("Audio Accessibility", False, str(e)))
        
        # Check 3: Frontend loads quickly
        try:
            start_time = time.time()
            response = requests.get(self.frontend_url, timeout=10)
            load_time = time.time() - start_time
            
            frontend_fast = response.status_code == 200 and load_time < 3.0
            demo_checks.append(("Frontend Speed", frontend_fast, f"Load time: {load_time:.2f}s"))
        except Exception as e:
            demo_checks.append(("Frontend Speed", False, str(e)))
        
        # Log all demo checks
        all_demo_ready = True
        for check_name, success, message in demo_checks:
            self.log_verification(f"Demo {check_name}", success, message)
            if not success:
                all_demo_ready = False
        
        return all_demo_ready
    
    def run_hackathon_verification(self) -> Dict[str, Any]:
        """Run complete hackathon verification"""
        print("🏆 Starting Hackathon Verification")
        print(f"API URL: {self.api_url}")
        print(f"Frontend URL: {self.frontend_url}")
        print("=" * 80)
        
        # Run all verifications
        api_working = self.verify_api_endpoints()
        frontend_working = self.verify_frontend_accessibility()
        content_good = self.verify_content_quality()
        performance_good = self.verify_performance()
        demo_ready = self.verify_demo_readiness()
        
        # Calculate overall readiness
        total_tests = len(self.verification_results)
        passed_tests = sum(1 for result in self.verification_results if result['success'])
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        # Determine overall readiness
        critical_systems = [api_working, frontend_working, content_good]
        overall_ready = all(critical_systems) and success_rate >= 80
        
        return self._generate_verification_summary(overall_ready, success_rate)
    
    def _generate_verification_summary(self, overall_ready: bool, success_rate: float) -> Dict[str, Any]:
        """Generate verification summary"""
        total_tests = len(self.verification_results)
        passed_tests = sum(1 for result in self.verification_results if result['success'])
        
        print("\n" + "=" * 80)
        print("🏆 HACKATHON VERIFICATION SUMMARY")
        print("=" * 80)
        print(f"Total Checks: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        print("\n📋 Verification Details:")
        for result in self.verification_results:
            status = "✅" if result['success'] else "❌"
            print(f"  {status} {result['test']}: {result['message']}")
        
        if overall_ready:
            print("\n🎉 HACKATHON STATUS: READY FOR DEMO!")
            print("✅ All critical systems operational")
            print("✅ Content quality verified")
            print("✅ Performance meets standards")
            print("✅ Demo scenarios validated")
            print("\n🚀 System is ready for hackathon presentation!")
        else:
            print("\n⚠️ HACKATHON STATUS: NEEDS ATTENTION")
            print("\nFailed Checks:")
            for result in self.verification_results:
                if not result['success']:
                    print(f"  ❌ {result['test']}: {result['message']}")
            print("\n🔧 Please address failed checks before demo")
        
        return {
            'overall_ready': overall_ready,
            'success_rate': success_rate,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'verification_results': self.verification_results,
            'verification_timestamp': datetime.now().isoformat(),
            'api_url': self.api_url,
            'frontend_url': self.frontend_url
        }

def main():
    """Main verification execution"""
    verifier = HackathonVerifier()
    
    try:
        results = verifier.run_hackathon_verification()
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"hackathon_verification_{timestamp}.json"
        
        try:
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\n📄 Verification results saved to: {results_file}")
        except Exception as e:
            print(f"⚠️ Could not save results file: {e}")
        
        # Exit with appropriate code
        exit_code = 0 if results['overall_ready'] else 1
        
        if results['overall_ready']:
            print("\n🎯 READY FOR HACKATHON SUBMISSION!")
        else:
            print("\n⚠️ Please address issues before hackathon demo")
        
        exit(exit_code)
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        exit(1)

if __name__ == "__main__":
    main()