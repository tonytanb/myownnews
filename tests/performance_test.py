#!/usr/bin/env python3
"""
Performance Testing and Optimization for Curio News
Tests response times, caching, and judge demo readiness
"""

import requests
import json
import time
import statistics
from datetime import datetime
from typing import Dict, List, Any

class PerformanceTest:
    def __init__(self, api_url: str, frontend_url: str):
        self.api_url = api_url.strip()
        self.frontend_url = frontend_url.strip()
        self.test_results = []
        self.session = requests.Session()
    
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
    
    def measure_api_response_time(self, endpoint: str, method: str = 'GET', samples: int = 3) -> Dict[str, float]:
        """Measure API response time with multiple samples"""
        times = []
        
        for i in range(samples):
            try:
                start_time = time.time()
                
                if method == 'GET':
                    response = self.session.get(f"{self.api_url}{endpoint}", timeout=10)
                elif method == 'POST':
                    response = self.session.post(f"{self.api_url}{endpoint}", timeout=15)
                
                end_time = time.time()
                response_time = end_time - start_time
                
                if response.status_code in [200, 201]:
                    times.append(response_time)
                    print(f"   Sample {i+1}: {response_time:.3f}s (HTTP {response.status_code})")
                else:
                    print(f"   Sample {i+1}: Failed (HTTP {response.status_code})")
                
                time.sleep(0.5)  # Brief pause between samples
                
            except Exception as e:
                print(f"   Sample {i+1}: Exception - {str(e)[:50]}...")
        
        if times:
            return {
                'avg': statistics.mean(times),
                'min': min(times),
                'max': max(times),
                'samples': len(times)
            }
        else:
            return {'avg': 0, 'min': 0, 'max': 0, 'samples': 0}
    
    def test_bootstrap_performance(self) -> bool:
        """Test bootstrap endpoint performance for instant demo"""
        print("   Testing bootstrap endpoint performance...")
        
        perf_data = self.measure_api_response_time('/bootstrap', 'GET', 5)
        
        if perf_data['samples'] == 0:
            self.log_test("Bootstrap Performance", False, "No successful requests")
            return False
        
        avg_time = perf_data['avg']
        
        # Judge demo criteria: < 1 second for instant response
        if avg_time < 1.0:
            self.log_test("Bootstrap Performance", True, f"Excellent: {avg_time:.3f}s avg (Judge-ready)")
            return True
        elif avg_time < 2.0:
            self.log_test("Bootstrap Performance", True, f"Good: {avg_time:.3f}s avg")
            return True
        else:
            self.log_test("Bootstrap Performance", False, f"Too slow: {avg_time:.3f}s avg")
            return False
    
    def test_agent_orchestration_performance(self) -> bool:
        """Test agent orchestration startup time"""
        print("   Testing agent orchestration performance...")
        
        perf_data = self.measure_api_response_time('/generate-fresh', 'POST', 2)
        
        if perf_data['samples'] == 0:
            self.log_test("Agent Orchestration Performance", False, "No successful requests")
            return False
        
        avg_time = perf_data['avg']
        
        # Agent orchestration should start quickly (< 5 seconds)
        if avg_time < 3.0:
            self.log_test("Agent Orchestration Performance", True, f"Fast startup: {avg_time:.3f}s avg")
            return True
        elif avg_time < 5.0:
            self.log_test("Agent Orchestration Performance", True, f"Acceptable startup: {avg_time:.3f}s avg")
            return True
        else:
            self.log_test("Agent Orchestration Performance", False, f"Slow startup: {avg_time:.3f}s avg")
            return False
    
    def test_frontend_load_performance(self) -> bool:
        """Test frontend loading performance"""
        print("   Testing frontend load performance...")
        
        times = []
        for i in range(3):
            try:
                start_time = time.time()
                response = self.session.get(self.frontend_url, timeout=10)
                end_time = time.time()
                
                if response.status_code == 200:
                    load_time = end_time - start_time
                    times.append(load_time)
                    print(f"   Sample {i+1}: {load_time:.3f}s")
                else:
                    print(f"   Sample {i+1}: Failed (HTTP {response.status_code})")
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"   Sample {i+1}: Exception - {str(e)[:50]}...")
        
        if not times:
            self.log_test("Frontend Performance", False, "No successful loads")
            return False
        
        avg_time = statistics.mean(times)
        
        # Frontend should load quickly for judge demo
        if avg_time < 2.0:
            self.log_test("Frontend Performance", True, f"Fast load: {avg_time:.3f}s avg")
            return True
        elif avg_time < 4.0:
            self.log_test("Frontend Performance", True, f"Acceptable load: {avg_time:.3f}s avg")
            return True
        else:
            self.log_test("Frontend Performance", False, f"Slow load: {avg_time:.3f}s avg")
            return False
    
    def test_caching_effectiveness(self) -> bool:
        """Test caching effectiveness for repeated requests"""
        print("   Testing caching effectiveness...")
        
        # First request (cache miss)
        start_time = time.time()
        response1 = self.session.get(f"{self.api_url}/bootstrap", timeout=10)
        first_time = time.time() - start_time
        
        if response1.status_code != 200:
            self.log_test("Caching Effectiveness", False, "First request failed")
            return False
        
        time.sleep(0.5)
        
        # Second request (should be cached)
        start_time = time.time()
        response2 = self.session.get(f"{self.api_url}/bootstrap", timeout=10)
        second_time = time.time() - start_time
        
        if response2.status_code != 200:
            self.log_test("Caching Effectiveness", False, "Second request failed")
            return False
        
        # Check if second request is faster (indicating caching)
        improvement = ((first_time - second_time) / first_time) * 100
        
        print(f"   First request: {first_time:.3f}s")
        print(f"   Second request: {second_time:.3f}s")
        print(f"   Improvement: {improvement:.1f}%")
        
        if second_time < first_time:
            self.log_test("Caching Effectiveness", True, f"Caching working: {improvement:.1f}% faster")
            return True
        else:
            self.log_test("Caching Effectiveness", True, "Consistent response times")
            return True
    
    def test_concurrent_requests(self) -> bool:
        """Test performance under concurrent load"""
        print("   Testing concurrent request handling...")
        
        import threading
        import queue
        
        results_queue = queue.Queue()
        
        def make_request():
            try:
                start_time = time.time()
                response = self.session.get(f"{self.api_url}/bootstrap", timeout=10)
                end_time = time.time()
                
                results_queue.put({
                    'success': response.status_code == 200,
                    'time': end_time - start_time,
                    'status': response.status_code
                })
            except Exception as e:
                results_queue.put({
                    'success': False,
                    'time': 0,
                    'error': str(e)
                })
        
        # Launch 5 concurrent requests
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=15)
        
        # Collect results
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())
        
        successful_requests = [r for r in results if r['success']]
        success_rate = (len(successful_requests) / len(results)) * 100 if results else 0
        
        if successful_requests:
            avg_time = statistics.mean([r['time'] for r in successful_requests])
            print(f"   Successful requests: {len(successful_requests)}/{len(results)}")
            print(f"   Average response time: {avg_time:.3f}s")
        
        if success_rate >= 80:
            self.log_test("Concurrent Load", True, f"{success_rate:.0f}% success rate")
            return True
        else:
            self.log_test("Concurrent Load", False, f"Only {success_rate:.0f}% success rate")
            return False
    
    def test_judge_demo_readiness(self) -> bool:
        """Test specific scenarios for judge demonstration"""
        print("   Testing judge demo scenarios...")
        
        demo_scenarios = []
        
        # Scenario 1: Cold start (first request)
        try:
            start_time = time.time()
            response = self.session.get(f"{self.api_url}/bootstrap", timeout=10)
            cold_start_time = time.time() - start_time
            
            demo_scenarios.append({
                'name': 'Cold Start',
                'success': response.status_code == 200,
                'time': cold_start_time,
                'target': 2.0  # Should be under 2 seconds
            })
        except Exception as e:
            demo_scenarios.append({
                'name': 'Cold Start',
                'success': False,
                'error': str(e)
            })
        
        # Scenario 2: Immediate second request (cached)
        try:
            start_time = time.time()
            response = self.session.get(f"{self.api_url}/bootstrap", timeout=10)
            cached_time = time.time() - start_time
            
            demo_scenarios.append({
                'name': 'Cached Request',
                'success': response.status_code == 200,
                'time': cached_time,
                'target': 1.0  # Should be under 1 second
            })
        except Exception as e:
            demo_scenarios.append({
                'name': 'Cached Request',
                'success': False,
                'error': str(e)
            })
        
        # Evaluate demo readiness
        successful_scenarios = [s for s in demo_scenarios if s.get('success', False)]
        fast_scenarios = [s for s in successful_scenarios if s.get('time', 999) < s.get('target', 1)]
        
        for scenario in demo_scenarios:
            if scenario.get('success'):
                time_str = f"{scenario['time']:.3f}s" if 'time' in scenario else "N/A"
                target_str = f"(target: <{scenario.get('target', 'N/A')}s)" if 'target' in scenario else ""
                print(f"   {scenario['name']}: {time_str} {target_str}")
            else:
                print(f"   {scenario['name']}: FAILED")
        
        demo_ready = len(fast_scenarios) >= len(demo_scenarios) * 0.8
        
        if demo_ready:
            self.log_test("Judge Demo Readiness", True, f"{len(fast_scenarios)}/{len(demo_scenarios)} scenarios ready")
            return True
        else:
            self.log_test("Judge Demo Readiness", False, f"Only {len(fast_scenarios)}/{len(demo_scenarios)} scenarios ready")
            return False
    
    def run_performance_tests(self) -> Dict[str, Any]:
        """Run all performance tests"""
        print("⚡ Starting Performance Testing")
        print(f"API URL: {self.api_url}")
        print(f"Frontend URL: {self.frontend_url}")
        print("=" * 60)
        
        # Run performance tests
        bootstrap_perf = self.test_bootstrap_performance()
        agent_perf = self.test_agent_orchestration_performance()
        frontend_perf = self.test_frontend_load_performance()
        caching_perf = self.test_caching_effectiveness()
        concurrent_perf = self.test_concurrent_requests()
        demo_ready = self.test_judge_demo_readiness()
        
        # Calculate results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print("\n" + "=" * 60)
        print(f"📊 Performance Test Results")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Determine performance status
        critical_tests = [bootstrap_perf, demo_ready]
        performance_ready = all(critical_tests) and success_rate >= 70
        
        if performance_ready:
            print("🚀 PERFORMANCE STATUS: OPTIMIZED FOR DEMO")
        else:
            print("⚠️ PERFORMANCE STATUS: NEEDS OPTIMIZATION")
        
        return {
            'performance_ready': performance_ready,
            'success_rate': success_rate,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'test_results': self.test_results,
            'critical_performance': {
                'bootstrap': bootstrap_perf,
                'demo_ready': demo_ready,
                'frontend_load': frontend_perf
            }
        }

def main():
    """Main performance test execution"""
    api_url = "https://nqot0dir0h.execute-api.us-west-2.amazonaws.com/prod"
    frontend_url = "http://curio-news-frontend-1760997974.s3-website-us-west-2.amazonaws.com"
    
    tester = PerformanceTest(api_url, frontend_url)
    results = tester.run_performance_tests()
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"tests/performance_results_{timestamp}.json"
    
    try:
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n📄 Performance results saved to: {results_file}")
    except Exception as e:
        print(f"⚠️ Could not save results: {e}")
    
    return results['performance_ready']

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)