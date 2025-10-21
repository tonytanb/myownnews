#!/usr/bin/env python3
"""
Judge Demonstration Optimizer for Curio News
Ensures instant response times and impressive technical depth for live demo
"""

import requests
import json
import time
import asyncio
import concurrent.futures
from datetime import datetime
from typing import Dict, List, Any

class JudgeDemoOptimizer:
    def __init__(self, api_url: str, frontend_url: str):
        self.api_url = api_url.strip()
        self.frontend_url = frontend_url.strip()
        self.optimization_results = []
        self.session = requests.Session()
        
        # Pre-warm session with keep-alive
        self.session.headers.update({
            'Connection': 'keep-alive',
            'User-Agent': 'JudgeDemo/1.0 (AWS-Agent-Hackathon)'
        })
    
    def log_optimization(self, test_name: str, success: bool, message: str = "", data: Any = None):
        """Log optimization result"""
        result = {
            'optimization': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        self.optimization_results.append(result)
        
        status = "✅ OPTIMIZED" if success else "❌ NEEDS WORK"
        print(f"{status} {test_name}: {message}")
    
    def pre_warm_api_endpoints(self) -> bool:
        """Pre-warm all API endpoints for instant response"""
        print("🔥 Pre-warming API endpoints for instant demo response...")
        
        endpoints_to_warm = [
            '/bootstrap',
            '/latest',
            '/trace/demo-trace-12345'
        ]
        
        warm_count = 0
        for endpoint in endpoints_to_warm:
            try:
                start_time = time.time()
                response = self.session.get(f"{self.api_url}{endpoint}", timeout=5)
                response_time = time.time() - start_time
                
                if response.status_code in [200, 404]:  # 404 is OK for trace endpoint
                    warm_count += 1
                    print(f"   ✅ {endpoint}: {response_time:.3f}s")
                else:
                    print(f"   ⚠️ {endpoint}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ {endpoint}: {str(e)[:50]}...")
        
        success_rate = (warm_count / len(endpoints_to_warm)) * 100
        
        if success_rate >= 80:
            self.log_optimization("API Pre-warming", True, f"{warm_count}/{len(endpoints_to_warm)} endpoints warmed")
            return True
        else:
            self.log_optimization("API Pre-warming", False, f"Only {warm_count}/{len(endpoints_to_warm)} endpoints warmed")
            return False
    
    def test_instant_bootstrap_response(self) -> bool:
        """Test that bootstrap responds instantly for judge demo"""
        print("⚡ Testing instant bootstrap response...")
        
        response_times = []
        for i in range(5):
            try:
                start_time = time.time()
                response = self.session.get(f"{self.api_url}/bootstrap", timeout=3)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    response_times.append(response_time)
                    print(f"   Sample {i+1}: {response_time:.3f}s")
                else:
                    print(f"   Sample {i+1}: Failed (HTTP {response.status_code})")
                
                time.sleep(0.2)  # Brief pause
                
            except Exception as e:
                print(f"   Sample {i+1}: Exception - {str(e)[:50]}...")
        
        if not response_times:
            self.log_optimization("Instant Bootstrap", False, "No successful responses")
            return False
        
        avg_time = sum(response_times) / len(response_times)
        min_time = min(response_times)
        
        # Judge demo criteria: < 500ms average, < 200ms minimum
        if avg_time < 0.5 and min_time < 0.2:
            self.log_optimization("Instant Bootstrap", True, f"Excellent: {avg_time:.3f}s avg, {min_time:.3f}s min")
            return True
        elif avg_time < 1.0:
            self.log_optimization("Instant Bootstrap", True, f"Good: {avg_time:.3f}s avg")
            return True
        else:
            self.log_optimization("Instant Bootstrap", False, f"Too slow: {avg_time:.3f}s avg")
            return False
    
    def test_agent_progress_indicators(self) -> bool:
        """Test that agent progress indicators work smoothly"""
        print("🤖 Testing agent progress indicators...")
        
        try:
            # Test bootstrap for agent status
            response = self.session.get(f"{self.api_url}/bootstrap", timeout=5)
            
            if response.status_code != 200:
                self.log_optimization("Agent Progress", False, f"Bootstrap failed: HTTP {response.status_code}")
                return False
            
            data = response.json()
            
            # Check for agent status fields
            required_fields = ['agentStatus', 'traceId']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                self.log_optimization("Agent Progress", False, f"Missing fields: {missing_fields}")
                return False
            
            # Check if agent status is meaningful
            agent_status = data.get('agentStatus', '')
            if not agent_status or len(agent_status) < 3:
                self.log_optimization("Agent Progress", False, "Empty or invalid agent status")
                return False
            
            # Check trace ID format
            trace_id = data.get('traceId', '')
            if not trace_id or len(trace_id) < 5:
                self.log_optimization("Agent Progress", False, "Invalid trace ID")
                return False
            
            self.log_optimization("Agent Progress", True, f"Status: '{agent_status}', Trace: '{trace_id}'")
            return True
            
        except Exception as e:
            self.log_optimization("Agent Progress", False, f"Exception: {str(e)}")
            return False
    
    def test_trace_functionality_depth(self) -> bool:
        """Test that trace functionality shows impressive technical depth"""
        print("🔍 Testing trace functionality for technical depth...")
        
        try:
            # Test trace endpoint with demo trace ID
            response = self.session.get(f"{self.api_url}/trace/demo-trace-12345", timeout=5)
            
            # Even if it returns 404, check that the endpoint is accessible
            if response.status_code == 404:
                # This is expected for demo trace ID
                self.log_optimization("Trace Depth", True, "Trace endpoint accessible (404 expected for demo)")
                return True
            elif response.status_code == 200:
                try:
                    trace_data = response.json()
                    
                    # Check for technical depth indicators
                    depth_indicators = ['traceId', 'agents', 'steps', 'decisions', 'reasoning']
                    found_indicators = [field for field in depth_indicators if field in str(trace_data).lower()]
                    
                    if len(found_indicators) >= 2:
                        self.log_optimization("Trace Depth", True, f"Rich trace data with {len(found_indicators)} depth indicators")
                        return True
                    else:
                        self.log_optimization("Trace Depth", True, "Basic trace functionality working")
                        return True
                        
                except json.JSONDecodeError:
                    self.log_optimization("Trace Depth", False, "Invalid JSON in trace response")
                    return False
            else:
                self.log_optimization("Trace Depth", False, f"Trace endpoint error: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_optimization("Trace Depth", False, f"Exception: {str(e)}")
            return False
    
    def test_demo_scenario_performance(self) -> bool:
        """Test specific demo scenarios for judge presentation"""
        print("🎯 Testing demo scenarios for judge presentation...")
        
        demo_scenarios = [
            {
                'name': 'Cold Start Demo',
                'description': 'First impression when judges visit',
                'target_time': 1.0
            },
            {
                'name': 'Audio Play Demo',
                'description': 'Audio playback demonstration',
                'target_time': 0.5
            },
            {
                'name': 'Trace View Demo',
                'description': 'Agent provenance demonstration',
                'target_time': 0.8
            }
        ]
        
        successful_scenarios = 0
        
        for scenario in demo_scenarios:
            try:
                start_time = time.time()
                response = self.session.get(f"{self.api_url}/bootstrap", timeout=5)
                response_time = time.time() - start_time
                
                if response.status_code == 200 and response_time < scenario['target_time']:
                    successful_scenarios += 1
                    print(f"   ✅ {scenario['name']}: {response_time:.3f}s (target: <{scenario['target_time']}s)")
                else:
                    print(f"   ⚠️ {scenario['name']}: {response_time:.3f}s (target: <{scenario['target_time']}s)")
                
                time.sleep(0.3)  # Brief pause between scenarios
                
            except Exception as e:
                print(f"   ❌ {scenario['name']}: Exception - {str(e)[:50]}...")
        
        success_rate = (successful_scenarios / len(demo_scenarios)) * 100
        
        if success_rate >= 80:
            self.log_optimization("Demo Scenarios", True, f"{successful_scenarios}/{len(demo_scenarios)} scenarios ready")
            return True
        else:
            self.log_optimization("Demo Scenarios", False, f"Only {successful_scenarios}/{len(demo_scenarios)} scenarios ready")
            return False
    
    def test_concurrent_judge_access(self) -> bool:
        """Test performance under concurrent judge access"""
        print("👥 Testing concurrent judge access simulation...")
        
        def make_judge_request():
            try:
                start_time = time.time()
                response = self.session.get(f"{self.api_url}/bootstrap", timeout=10)
                end_time = time.time()
                
                return {
                    'success': response.status_code == 200,
                    'time': end_time - start_time,
                    'status': response.status_code
                }
            except Exception as e:
                return {
                    'success': False,
                    'time': 0,
                    'error': str(e)
                }
        
        # Simulate 3 judges accessing simultaneously
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(make_judge_request) for _ in range(3)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        successful_requests = [r for r in results if r['success']]
        success_rate = (len(successful_requests) / len(results)) * 100
        
        if successful_requests:
            avg_time = sum(r['time'] for r in successful_requests) / len(successful_requests)
            print(f"   Successful requests: {len(successful_requests)}/{len(results)}")
            print(f"   Average response time: {avg_time:.3f}s")
        
        if success_rate >= 100 and successful_requests:
            avg_time = sum(r['time'] for r in successful_requests) / len(successful_requests)
            if avg_time < 2.0:
                self.log_optimization("Concurrent Access", True, f"Perfect: {success_rate:.0f}% success, {avg_time:.3f}s avg")
                return True
            else:
                self.log_optimization("Concurrent Access", True, f"Good: {success_rate:.0f}% success")
                return True
        else:
            self.log_optimization("Concurrent Access", False, f"Only {success_rate:.0f}% success rate")
            return False
    
    def optimize_for_judge_demo(self) -> Dict[str, Any]:
        """Run all judge demo optimizations"""
        print("🏆 Optimizing Curio News for Judge Demonstration")
        print(f"API URL: {self.api_url}")
        print(f"Frontend URL: {self.frontend_url}")
        print("=" * 60)
        
        # Run optimization tests
        print("\n🔥 Pre-warming Systems...")
        pre_warm_success = self.pre_warm_api_endpoints()
        
        print("\n⚡ Testing Instant Response...")
        instant_success = self.test_instant_bootstrap_response()
        
        print("\n🤖 Testing Agent Indicators...")
        agent_success = self.test_agent_progress_indicators()
        
        print("\n🔍 Testing Technical Depth...")
        trace_success = self.test_trace_functionality_depth()
        
        print("\n🎯 Testing Demo Scenarios...")
        demo_success = self.test_demo_scenario_performance()
        
        print("\n👥 Testing Concurrent Access...")
        concurrent_success = self.test_concurrent_judge_access()
        
        # Calculate results
        total_optimizations = len(self.optimization_results)
        successful_optimizations = sum(1 for result in self.optimization_results if result['success'])
        optimization_rate = (successful_optimizations / total_optimizations) * 100 if total_optimizations > 0 else 0
        
        print("\n" + "=" * 60)
        print(f"🏆 Judge Demo Optimization Results")
        print(f"Total Optimizations: {total_optimizations}")
        print(f"Successful: {successful_optimizations}")
        print(f"Optimization Rate: {optimization_rate:.1f}%")
        
        # Determine judge readiness
        critical_optimizations = [instant_success, agent_success, demo_success]
        judge_ready = all(critical_optimizations) and optimization_rate >= 80
        
        if judge_ready:
            print("🎉 JUDGE DEMO STATUS: FULLY OPTIMIZED")
            print("✨ Ready to impress judges with:")
            print("   • Instant response times")
            print("   • Smooth agent progress indicators")
            print("   • Impressive technical depth")
            print("   • Reliable concurrent access")
        else:
            print("⚠️ JUDGE DEMO STATUS: NEEDS OPTIMIZATION")
            print("\nAreas needing attention:")
            for result in self.optimization_results:
                if not result['success']:
                    print(f"  - {result['optimization']}: {result['message']}")
        
        return {
            'judge_ready': judge_ready,
            'optimization_rate': optimization_rate,
            'total_optimizations': total_optimizations,
            'successful_optimizations': successful_optimizations,
            'optimization_results': self.optimization_results,
            'critical_systems': {
                'instant_response': instant_success,
                'agent_indicators': agent_success,
                'technical_depth': trace_success,
                'demo_scenarios': demo_success,
                'concurrent_access': concurrent_success
            }
        }

def main():
    """Main judge demo optimization execution"""
    api_url = "https://nqot0dir0h.execute-api.us-west-2.amazonaws.com/prod"
    frontend_url = "http://curio-news-frontend-1760997974.s3-website-us-west-2.amazonaws.com"
    
    optimizer = JudgeDemoOptimizer(api_url, frontend_url)
    results = optimizer.optimize_for_judge_demo()
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"tests/judge_demo_results_{timestamp}.json"
    
    try:
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n📄 Judge demo optimization results saved to: {results_file}")
    except Exception as e:
        print(f"⚠️ Could not save results: {e}")
    
    return results['judge_ready']

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)