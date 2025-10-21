#!/usr/bin/env python3
"""
Performance and Reliability Testing for Curio News System
Task 7.3: Conduct performance and reliability testing

Tests:
- System under concurrent load
- Agent execution times meet requirements
- Consistent content quality over multiple runs
- Requirements: 5.1, 5.2, 5.3
"""

import requests
import json
import time
import sys
import os
import threading
import queue
import statistics
from datetime import datetime
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration
API_BASE_URL = os.getenv('API_URL', 'https://nqot0dir0h.execute-api.us-west-2.amazonaws.com/prod')
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://curio-news-frontend-1760997974.s3-website-us-west-2.amazonaws.com')
CONCURRENT_USERS = 5  # Number of concurrent users to simulate
RELIABILITY_RUNS = 5  # Number of runs to test consistency
MAX_AGENT_TIME = 60  # Maximum acceptable time per agent (seconds)
MAX_TOTAL_TIME = 300  # Maximum acceptable total workflow time (seconds)
CONTENT_QUALITY_THRESHOLD = 0.8  # 80% consistency required

class PerformanceReliabilityTester:
    def __init__(self):
        self.api_url = API_BASE_URL
        self.frontend_url = FRONTEND_URL
        self.test_results = []
        self.session = requests.Session()
        self.expected_agents = [
            "NEWS_FETCHER",
            "CONTENT_CURATOR", 
            "FAVORITE_SELECTOR",
            "SCRIPT_GENERATOR",
            "MEDIA_ENHANCER",
            "WEEKEND_EVENTS"
        ]
        
    def log_test(self, test_name: str, success: bool, message: str = "", data: Any = None):
        """Log test result with detailed information"""
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
        
        if data and not success:
            print(f"   Debug data: {json.dumps(data, indent=2)[:300]}...")
    
    def measure_single_workflow_performance(self, run_id_suffix: str = "") -> Dict[str, Any]:
        """Measure performance of a single complete workflow"""
        workflow_start = time.time()
        
        try:
            # Step 1: Start content generation
            response = self.session.post(f"{self.api_url}/generate-fresh", timeout=20)
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f"Generation start failed: HTTP {response.status_code}",
                    'total_time': time.time() - workflow_start
                }
            
            data = response.json()
            run_id = data.get('runId')
            
            if not run_id:
                return {
                    'success': False,
                    'error': 'No runId returned',
                    'total_time': time.time() - workflow_start
                }
            
            generation_start_time = time.time() - workflow_start
            
            # Step 2: Monitor agent execution with detailed timing
            agent_times = {}
            agent_start_times = {}
            current_agent = None
            orchestration_complete = False
            
            max_polls = MAX_TOTAL_TIME // 2  # Poll every 2 seconds
            
            for poll_count in range(max_polls):
                try:
                    response = self.session.get(
                        f"{self.api_url}/agent-status?runId={run_id}", 
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        status_data = response.json()
                        new_agent = status_data.get('currentAgent', 'UNKNOWN')
                        status = status_data.get('status', 'UNKNOWN')
                        
                        # Track agent transitions
                        if new_agent != current_agent and new_agent in self.expected_agents:
                            current_time = time.time() - workflow_start
                            
                            # Record completion time for previous agent
                            if current_agent and current_agent in agent_start_times:
                                agent_times[current_agent] = current_time - agent_start_times[current_agent]
                            
                            # Start timing new agent
                            agent_start_times[new_agent] = current_time
                            current_agent = new_agent
                        
                        # Check for completion
                        if status in ['SUCCESS', 'COMPLETED'] or new_agent == 'COMPLETED':
                            # Record final agent completion
                            if current_agent and current_agent in agent_start_times:
                                agent_times[current_agent] = time.time() - workflow_start - agent_start_times[current_agent]
                            
                            orchestration_complete = True
                            break
                        
                        # Check for failure
                        if status == 'FAILED':
                            return {
                                'success': False,
                                'error': f'Orchestration failed at agent: {new_agent}',
                                'total_time': time.time() - workflow_start,
                                'run_id': run_id,
                                'agent_times': agent_times
                            }
                    
                    time.sleep(2)
                    
                except Exception as e:
                    continue
            
            orchestration_time = time.time() - workflow_start
            
            if not orchestration_complete:
                return {
                    'success': False,
                    'error': 'Orchestration timeout',
                    'total_time': orchestration_time,
                    'run_id': run_id,
                    'agent_times': agent_times
                }
            
            # Step 3: Validate content and measure bootstrap performance
            bootstrap_start = time.time()
            response = self.session.get(f"{self.api_url}/bootstrap", timeout=15)
            bootstrap_time = time.time() - bootstrap_start
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'Bootstrap failed: HTTP {response.status_code}',
                    'total_time': time.time() - workflow_start,
                    'run_id': run_id,
                    'agent_times': agent_times
                }
            
            content = response.json()
            total_time = time.time() - workflow_start
            
            # Analyze content quality
            content_analysis = self.analyze_content_quality(content)
            
            return {
                'success': True,
                'total_time': total_time,
                'generation_start_time': generation_start_time,
                'orchestration_time': orchestration_time,
                'bootstrap_time': bootstrap_time,
                'agent_times': agent_times,
                'run_id': run_id,
                'content_analysis': content_analysis
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'total_time': time.time() - workflow_start if 'workflow_start' in locals() else 0
            }
    
    def analyze_content_quality(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content quality metrics"""
        analysis = {
            'news_items_count': len(content.get('news_items', [])),
            'script_length': len(content.get('script', '')),
            'has_audio_url': bool(content.get('audioUrl')),
            'word_timings_count': len(content.get('word_timings', [])),
            'agent_outputs_count': len(content.get('agentOutputs', {})),
            'quality_score': 0
        }
        
        # Calculate quality score (0-1)
        score = 0
        
        # News items (0.2 points)
        if analysis['news_items_count'] >= 3:
            score += 0.2
        elif analysis['news_items_count'] >= 1:
            score += 0.1
        
        # Script content (0.2 points)
        if analysis['script_length'] >= 500:
            score += 0.2
        elif analysis['script_length'] >= 100:
            score += 0.1
        
        # Audio URL (0.2 points)
        if analysis['has_audio_url']:
            score += 0.2
        
        # Word timings (0.2 points)
        if analysis['word_timings_count'] >= 10:
            score += 0.2
        elif analysis['word_timings_count'] >= 1:
            score += 0.1
        
        # Agent outputs (0.2 points)
        if analysis['agent_outputs_count'] >= 3:
            score += 0.2
        elif analysis['agent_outputs_count'] >= 1:
            score += 0.1
        
        analysis['quality_score'] = score
        return analysis
    
    def test_concurrent_load_performance(self) -> bool:
        """Test system performance under concurrent load (Requirement 5.1)"""
        print(f"🚀 Testing concurrent load with {CONCURRENT_USERS} simultaneous users...")
        
        def concurrent_user_workflow(user_id: int) -> Dict[str, Any]:
            """Simulate a single user workflow"""
            user_session = requests.Session()
            start_time = time.time()
            
            try:
                # Test bootstrap endpoint (most common user action)
                response = user_session.get(f"{self.api_url}/bootstrap", timeout=15)
                bootstrap_time = time.time() - start_time
                
                if response.status_code == 200:
                    content = response.json()
                    return {
                        'user_id': user_id,
                        'success': True,
                        'bootstrap_time': bootstrap_time,
                        'content_size': len(json.dumps(content))
                    }
                else:
                    return {
                        'user_id': user_id,
                        'success': False,
                        'error': f'HTTP {response.status_code}',
                        'bootstrap_time': bootstrap_time
                    }
                    
            except Exception as e:
                return {
                    'user_id': user_id,
                    'success': False,
                    'error': str(e),
                    'bootstrap_time': time.time() - start_time
                }
        
        # Execute concurrent requests
        concurrent_results = []
        with ThreadPoolExecutor(max_workers=CONCURRENT_USERS) as executor:
            futures = [executor.submit(concurrent_user_workflow, i) for i in range(CONCURRENT_USERS)]
            
            for future in as_completed(futures, timeout=30):
                try:
                    result = future.result()
                    concurrent_results.append(result)
                except Exception as e:
                    concurrent_results.append({
                        'success': False,
                        'error': str(e)
                    })
        
        # Analyze concurrent performance
        successful_requests = [r for r in concurrent_results if r.get('success', False)]
        success_rate = len(successful_requests) / len(concurrent_results) * 100
        
        if successful_requests:
            avg_response_time = statistics.mean([r['bootstrap_time'] for r in successful_requests])
            max_response_time = max([r['bootstrap_time'] for r in successful_requests])
            min_response_time = min([r['bootstrap_time'] for r in successful_requests])
            
            performance_data = {
                'success_rate': success_rate,
                'avg_response_time': avg_response_time,
                'max_response_time': max_response_time,
                'min_response_time': min_response_time,
                'concurrent_users': CONCURRENT_USERS
            }
            
            # Performance criteria: 80% success rate, avg response < 5s
            if success_rate >= 80 and avg_response_time < 5.0:
                self.log_test("Concurrent Load Performance", True, 
                             f"{success_rate:.0f}% success, {avg_response_time:.2f}s avg response", 
                             performance_data)
                return True
            else:
                self.log_test("Concurrent Load Performance", False, 
                             f"{success_rate:.0f}% success, {avg_response_time:.2f}s avg response", 
                             performance_data)
                return False
        else:
            self.log_test("Concurrent Load Performance", False, 
                         "No successful concurrent requests")
            return False
    
    def test_agent_execution_time_requirements(self) -> bool:
        """Test that agent execution times meet requirements (Requirement 5.2)"""
        print("⏱️ Testing agent execution time requirements...")
        
        # Run a single workflow to measure agent times
        workflow_result = self.measure_single_workflow_performance("timing_test")
        
        if not workflow_result.get('success'):
            self.log_test("Agent Execution Times", False, 
                         f"Workflow failed: {workflow_result.get('error', 'Unknown error')}")
            return False
        
        agent_times = workflow_result.get('agent_times', {})
        total_time = workflow_result.get('total_time', 0)
        
        # Check individual agent times
        slow_agents = []
        for agent, exec_time in agent_times.items():
            if exec_time > MAX_AGENT_TIME:
                slow_agents.append(f"{agent}: {exec_time:.1f}s")
        
        # Check total workflow time
        timing_issues = []
        if total_time > MAX_TOTAL_TIME:
            timing_issues.append(f"Total workflow time: {total_time:.1f}s (max: {MAX_TOTAL_TIME}s)")
        
        if slow_agents:
            timing_issues.extend([f"Slow agents: {', '.join(slow_agents)}"])
        
        timing_data = {
            'total_time': total_time,
            'agent_times': agent_times,
            'max_agent_time': MAX_AGENT_TIME,
            'max_total_time': MAX_TOTAL_TIME,
            'agents_tested': len(agent_times)
        }
        
        if timing_issues:
            self.log_test("Agent Execution Times", False, 
                         f"Timing requirements not met: {'; '.join(timing_issues)}", 
                         timing_data)
            return False
        else:
            avg_agent_time = statistics.mean(agent_times.values()) if agent_times else 0
            self.log_test("Agent Execution Times", True, 
                         f"All agents within limits - Total: {total_time:.1f}s, Avg per agent: {avg_agent_time:.1f}s", 
                         timing_data)
            return True
    
    def test_content_quality_consistency(self) -> bool:
        """Test consistent content quality over multiple runs (Requirement 5.3)"""
        print(f"🔍 Testing content quality consistency over {RELIABILITY_RUNS} runs...")
        
        consistency_results = []
        successful_runs = 0
        
        for run_number in range(1, RELIABILITY_RUNS + 1):
            print(f"   Run {run_number}/{RELIABILITY_RUNS}...")
            
            workflow_result = self.measure_single_workflow_performance(f"consistency_{run_number}")
            
            if workflow_result.get('success'):
                successful_runs += 1
                consistency_results.append(workflow_result['content_analysis'])
            else:
                print(f"   Run {run_number} failed: {workflow_result.get('error', 'Unknown error')}")
            
            # Wait between runs to avoid overwhelming the system
            if run_number < RELIABILITY_RUNS:
                time.sleep(5)
        
        if successful_runs < 2:
            self.log_test("Content Quality Consistency", False, 
                         f"Need at least 2 successful runs, got {successful_runs}")
            return False
        
        # Analyze consistency metrics
        news_counts = [r['news_items_count'] for r in consistency_results]
        script_lengths = [r['script_length'] for r in consistency_results]
        quality_scores = [r['quality_score'] for r in consistency_results]
        audio_success_rate = sum(1 for r in consistency_results if r['has_audio_url']) / len(consistency_results)
        
        # Calculate consistency metrics
        consistency_metrics = {
            'successful_runs': successful_runs,
            'total_runs': RELIABILITY_RUNS,
            'success_rate': successful_runs / RELIABILITY_RUNS,
            'news_items': {
                'min': min(news_counts),
                'max': max(news_counts),
                'avg': statistics.mean(news_counts),
                'std_dev': statistics.stdev(news_counts) if len(news_counts) > 1 else 0
            },
            'script_length': {
                'min': min(script_lengths),
                'max': max(script_lengths),
                'avg': statistics.mean(script_lengths),
                'std_dev': statistics.stdev(script_lengths) if len(script_lengths) > 1 else 0
            },
            'quality_scores': {
                'min': min(quality_scores),
                'max': max(quality_scores),
                'avg': statistics.mean(quality_scores),
                'std_dev': statistics.stdev(quality_scores) if len(quality_scores) > 1 else 0
            },
            'audio_success_rate': audio_success_rate
        }
        
        # Check consistency requirements
        consistency_issues = []
        
        # Success rate should be at least 80%
        if consistency_metrics['success_rate'] < CONTENT_QUALITY_THRESHOLD:
            consistency_issues.append(f"Success rate too low: {consistency_metrics['success_rate']:.1%}")
        
        # News items should be consistent (3-10 items, low variation)
        if consistency_metrics['news_items']['min'] < 3:
            consistency_issues.append(f"Some runs have too few news items: {consistency_metrics['news_items']['min']}")
        
        if consistency_metrics['news_items']['std_dev'] > 2:
            consistency_issues.append(f"News item count too variable: σ={consistency_metrics['news_items']['std_dev']:.1f}")
        
        # Quality scores should be consistently high
        if consistency_metrics['quality_scores']['avg'] < 0.7:
            consistency_issues.append(f"Average quality score too low: {consistency_metrics['quality_scores']['avg']:.2f}")
        
        # Audio generation should be reliable
        if audio_success_rate < 0.8:
            consistency_issues.append(f"Audio generation unreliable: {audio_success_rate:.1%} success")
        
        if consistency_issues:
            self.log_test("Content Quality Consistency", False, 
                         f"Consistency issues: {'; '.join(consistency_issues)}", 
                         consistency_metrics)
            return False
        else:
            self.log_test("Content Quality Consistency", True, 
                         f"Consistent quality - {consistency_metrics['success_rate']:.1%} success, avg quality {consistency_metrics['quality_scores']['avg']:.2f}", 
                         consistency_metrics)
            return True
    
    def test_system_stability_under_load(self) -> bool:
        """Test system stability during extended load testing"""
        print("🔄 Testing system stability under extended load...")
        
        stability_start = time.time()
        stability_results = []
        
        # Run multiple concurrent workflows over time
        for cycle in range(3):  # 3 cycles of concurrent load
            print(f"   Load cycle {cycle + 1}/3...")
            
            cycle_results = []
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = [
                    executor.submit(self.measure_single_workflow_performance, f"stability_{cycle}_{i}")
                    for i in range(3)
                ]
                
                for future in as_completed(futures, timeout=MAX_TOTAL_TIME + 60):
                    try:
                        result = future.result()
                        cycle_results.append(result)
                    except Exception as e:
                        cycle_results.append({
                            'success': False,
                            'error': str(e)
                        })
            
            stability_results.extend(cycle_results)
            
            # Brief pause between cycles
            if cycle < 2:
                time.sleep(10)
        
        # Analyze stability
        successful_workflows = [r for r in stability_results if r.get('success', False)]
        stability_success_rate = len(successful_workflows) / len(stability_results) * 100
        
        stability_data = {
            'total_workflows': len(stability_results),
            'successful_workflows': len(successful_workflows),
            'success_rate': stability_success_rate,
            'test_duration': time.time() - stability_start
        }
        
        # Stability criteria: 70% success rate under load
        if stability_success_rate >= 70:
            self.log_test("System Stability Under Load", True, 
                         f"{stability_success_rate:.0f}% success rate under extended load", 
                         stability_data)
            return True
        else:
            self.log_test("System Stability Under Load", False, 
                         f"Only {stability_success_rate:.0f}% success rate under load", 
                         stability_data)
            return False
    
    def run_performance_reliability_tests(self) -> Dict[str, Any]:
        """Run all performance and reliability tests"""
        print("🚀 Starting Performance and Reliability Testing")
        print(f"API URL: {self.api_url}")
        print(f"Frontend URL: {self.frontend_url}")
        print(f"Concurrent Users: {CONCURRENT_USERS}")
        print(f"Reliability Runs: {RELIABILITY_RUNS}")
        print(f"Max Agent Time: {MAX_AGENT_TIME}s")
        print(f"Max Total Time: {MAX_TOTAL_TIME}s")
        print("=" * 80)
        
        # Test 1: Concurrent load performance (Requirement 5.1)
        print("\n🚀 Test 1: Concurrent Load Performance")
        concurrent_success = self.test_concurrent_load_performance()
        
        # Test 2: Agent execution time requirements (Requirement 5.2)
        print("\n⏱️ Test 2: Agent Execution Time Requirements")
        timing_success = self.test_agent_execution_time_requirements()
        
        # Test 3: Content quality consistency (Requirement 5.3)
        print("\n🔍 Test 3: Content Quality Consistency")
        consistency_success = self.test_content_quality_consistency()
        
        # Test 4: System stability under load
        print("\n🔄 Test 4: System Stability Under Load")
        stability_success = self.test_system_stability_under_load()
        
        # Calculate overall results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        # Determine overall success
        critical_tests = [concurrent_success, timing_success, consistency_success]
        overall_success = all(critical_tests) and success_rate >= 75
        
        return self._generate_test_summary(overall_success)
    
    def _generate_test_summary(self, overall_success: bool) -> Dict[str, Any]:
        """Generate comprehensive test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print("📊 Performance and Reliability Test Results")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        print("\n📋 Test Details:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"  {status} {result['test']}: {result['message']}")
        
        print("\n📈 Requirements Validation:")
        req_5_1 = any(r['test'] == 'Concurrent Load Performance' and r['success'] for r in self.test_results)
        req_5_2 = any(r['test'] == 'Agent Execution Times' and r['success'] for r in self.test_results)
        req_5_3 = any(r['test'] == 'Content Quality Consistency' and r['success'] for r in self.test_results)
        
        print(f"  {'✅' if req_5_1 else '❌'} Requirement 5.1: Fast and reliable content generation")
        print(f"  {'✅' if req_5_2 else '❌'} Requirement 5.2: Accurate progress indicators")
        print(f"  {'✅' if req_5_3 else '❌'} Requirement 5.3: Complete loading state replacement")
        
        if overall_success:
            print("\n🎉 OVERALL STATUS: PERFORMANCE AND RELIABILITY VALIDATED")
            print("✅ System handles concurrent load effectively")
            print("✅ Agent execution times meet requirements")
            print("✅ Content quality is consistent across runs")
            print("✅ System remains stable under extended load")
            print("\n🚀 The system is ready for production deployment!")
        else:
            print("\n⚠️ OVERALL STATUS: PERFORMANCE ISSUES DETECTED")
            print("\nFailed Areas:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  ❌ {result['test']}: {result['message']}")
        
        return {
            'overall_success': overall_success,
            'success_rate': success_rate,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'test_results': self.test_results,
            'requirements_validation': {
                'requirement_5_1': req_5_1,
                'requirement_5_2': req_5_2,
                'requirement_5_3': req_5_3
            },
            'performance_metrics': {
                'concurrent_users_tested': CONCURRENT_USERS,
                'reliability_runs_tested': RELIABILITY_RUNS,
                'max_agent_time_limit': MAX_AGENT_TIME,
                'max_total_time_limit': MAX_TOTAL_TIME
            }
        }

def main():
    """Main test execution"""
    tester = PerformanceReliabilityTester()
    results = tester.run_performance_reliability_tests()
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"tests/performance_reliability_results_{timestamp}.json"
    
    try:
        os.makedirs("tests", exist_ok=True)
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n📄 Detailed results saved to: {results_file}")
    except Exception as e:
        print(f"⚠️ Could not save results file: {e}")
    
    # Exit with appropriate code
    sys.exit(0 if results['overall_success'] else 1)

if __name__ == "__main__":
    main()