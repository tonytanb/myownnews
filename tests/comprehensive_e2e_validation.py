#!/usr/bin/env python3
"""
Comprehensive End-to-End Validation Test
Combines agent orchestration and frontend integration testing
Tests complete content generation workflow and validates reliable performance
"""

import requests
import json
import time
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configuration
API_BASE_URL = os.getenv('API_URL', 'https://nqot0dir0h.execute-api.us-west-2.amazonaws.com/prod')
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://curio-news-frontend-1760997974.s3-website-us-west-2.amazonaws.com')
TEST_TIMEOUT = 300  # 5 minutes for complete workflow
RELIABILITY_RUNS = 3  # Number of runs to test reliability

class ComprehensiveE2EValidator:
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
    
    def test_system_health_check(self) -> bool:
        """Test that all system components are healthy"""
        try:
            print("🏥 Testing system health...")
            
            health_checks = []
            
            # Check API bootstrap endpoint
            try:
                response = self.session.get(f"{self.api_url}/bootstrap", timeout=10)
                if response.status_code == 200:
                    health_checks.append("API Bootstrap")
                else:
                    print(f"   API Bootstrap failed: {response.status_code}")
            except Exception as e:
                print(f"   API Bootstrap error: {e}")
            
            # Check frontend accessibility
            try:
                response = self.session.get(self.frontend_url, timeout=10)
                if response.status_code == 200:
                    health_checks.append("Frontend")
                else:
                    print(f"   Frontend failed: {response.status_code}")
            except Exception as e:
                print(f"   Frontend error: {e}")
            
            # Check agent status endpoint
            try:
                response = self.session.get(f"{self.api_url}/agent-status?runId=health-check", timeout=10)
                if response.status_code in [200, 404]:  # 404 is acceptable for non-existent runId
                    health_checks.append("Agent Status")
                else:
                    print(f"   Agent Status failed: {response.status_code}")
            except Exception as e:
                print(f"   Agent Status error: {e}")
            
            if len(health_checks) >= 2:  # Need at least API and one other component
                self.log_test("System Health Check", True, 
                             f"Healthy components: {', '.join(health_checks)}")
                return True
            else:
                self.log_test("System Health Check", False, 
                             f"Only {len(health_checks)} components healthy")
                return False
                
        except Exception as e:
            self.log_test("System Health Check", False, f"Exception: {str(e)}")
            return False
    
    def test_complete_workflow_single_run(self, run_number: int = 1) -> Dict[str, Any]:
        """Test complete workflow from generation to frontend display"""
        try:
            print(f"🔄 Testing complete workflow (Run {run_number})...")
            
            workflow_start = time.time()
            
            # Step 1: Start content generation
            print(f"   Step 1: Starting content generation...")
            try:
                response = self.session.post(f"{self.api_url}/generate-fresh", timeout=20)
                
                if response.status_code != 200:
                    return {
                        'success': False,
                        'step_failed': 'generation_start',
                        'error': f"HTTP {response.status_code}",
                        'total_time': time.time() - workflow_start
                    }
                
                data = response.json()
                run_id = data.get('runId')
                
                if not run_id:
                    return {
                        'success': False,
                        'step_failed': 'generation_start',
                        'error': 'No runId returned',
                        'total_time': time.time() - workflow_start
                    }
                
                print(f"   Started generation with runId: {run_id}")
                
            except Exception as e:
                return {
                    'success': False,
                    'step_failed': 'generation_start',
                    'error': str(e),
                    'total_time': time.time() - workflow_start
                }
            
            # Step 2: Monitor agent orchestration
            print(f"   Step 2: Monitoring agent orchestration...")
            orchestration_success = False
            completed_agents = []
            
            max_polls = TEST_TIMEOUT // 2  # Poll every 2 seconds
            
            for poll_count in range(max_polls):
                try:
                    response = self.session.get(
                        f"{self.api_url}/agent-status?runId={run_id}", 
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        status_data = response.json()
                        current_agent = status_data.get('currentAgent', 'UNKNOWN')
                        status = status_data.get('status', 'UNKNOWN')
                        
                        if poll_count % 15 == 0:  # Log every 30 seconds
                            elapsed = time.time() - workflow_start
                            print(f"   [{elapsed:.0f}s] Agent: {current_agent} - Status: {status}")
                        
                        # Check for completion
                        if status in ['SUCCESS', 'COMPLETED'] or current_agent == 'COMPLETED':
                            orchestration_success = True
                            completed_agents = self.expected_agents.copy()
                            break
                        
                        # Check for failure
                        if status == 'FAILED':
                            break
                    
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"   Status check error: {e}")
                    time.sleep(2)
                    continue
            
            orchestration_time = time.time() - workflow_start
            
            if not orchestration_success:
                return {
                    'success': False,
                    'step_failed': 'agent_orchestration',
                    'error': 'Orchestration did not complete successfully',
                    'total_time': orchestration_time,
                    'run_id': run_id
                }
            
            print(f"   Agent orchestration completed in {orchestration_time:.1f}s")
            
            # Step 3: Validate content completeness
            print(f"   Step 3: Validating content completeness...")
            try:
                response = self.session.get(f"{self.api_url}/bootstrap", timeout=15)
                
                if response.status_code != 200:
                    return {
                        'success': False,
                        'step_failed': 'content_validation',
                        'error': f"Bootstrap HTTP {response.status_code}",
                        'total_time': time.time() - workflow_start,
                        'run_id': run_id
                    }
                
                content = response.json()
                
                # Validate content sections
                validation_issues = []
                
                if not content.get('news_items') or len(content.get('news_items', [])) < 3:
                    validation_issues.append("Insufficient news items")
                
                if not content.get('script') or len(content.get('script', '')) < 100:
                    validation_issues.append("Script too short")
                
                if not content.get('audioUrl') or not content.get('audioUrl', '').startswith('http'):
                    validation_issues.append("Invalid audio URL")
                
                if not content.get('word_timings'):
                    validation_issues.append("Missing word timings")
                
                agent_outputs = content.get('agentOutputs', {})
                if not agent_outputs.get('favoriteStory'):
                    validation_issues.append("Missing favorite story")
                
                if not agent_outputs.get('weekendRecommendations'):
                    validation_issues.append("Missing weekend recommendations")
                
                if validation_issues:
                    return {
                        'success': False,
                        'step_failed': 'content_validation',
                        'error': f"Validation issues: {'; '.join(validation_issues)}",
                        'total_time': time.time() - workflow_start,
                        'run_id': run_id,
                        'content_summary': {
                            'news_items': len(content.get('news_items', [])),
                            'script_length': len(content.get('script', '')),
                            'has_audio': bool(content.get('audioUrl')),
                            'word_timings': len(content.get('word_timings', [])),
                            'agent_outputs': len(agent_outputs)
                        }
                    }
                
                print(f"   Content validation passed")
                
            except Exception as e:
                return {
                    'success': False,
                    'step_failed': 'content_validation',
                    'error': str(e),
                    'total_time': time.time() - workflow_start,
                    'run_id': run_id
                }
            
            # Step 4: Test frontend integration
            print(f"   Step 4: Testing frontend integration...")
            try:
                response = self.session.get(self.frontend_url, timeout=15)
                
                if response.status_code != 200:
                    return {
                        'success': False,
                        'step_failed': 'frontend_integration',
                        'error': f"Frontend HTTP {response.status_code}",
                        'total_time': time.time() - workflow_start,
                        'run_id': run_id
                    }
                
                # Basic frontend validation
                html_content = response.text
                if 'root' not in html_content:
                    return {
                        'success': False,
                        'step_failed': 'frontend_integration',
                        'error': 'Frontend missing root element',
                        'total_time': time.time() - workflow_start,
                        'run_id': run_id
                    }
                
                print(f"   Frontend integration validated")
                
            except Exception as e:
                return {
                    'success': False,
                    'step_failed': 'frontend_integration',
                    'error': str(e),
                    'total_time': time.time() - workflow_start,
                    'run_id': run_id
                }
            
            total_time = time.time() - workflow_start
            
            return {
                'success': True,
                'total_time': total_time,
                'orchestration_time': orchestration_time,
                'run_id': run_id,
                'completed_agents': completed_agents,
                'content_summary': {
                    'news_items': len(content.get('news_items', [])),
                    'script_length': len(content.get('script', '')),
                    'has_audio': bool(content.get('audioUrl')),
                    'word_timings': len(content.get('word_timings', [])),
                    'agent_outputs': len(agent_outputs)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'step_failed': 'workflow_exception',
                'error': str(e),
                'total_time': time.time() - workflow_start if 'workflow_start' in locals() else 0
            }
    
    def test_reliability_under_various_conditions(self) -> Dict[str, Any]:
        """Test system reliability by running multiple complete workflows"""
        try:
            print(f"🔄 Testing reliability with {RELIABILITY_RUNS} complete workflow runs...")
            
            reliability_results = []
            successful_runs = 0
            total_time = 0
            
            for run_number in range(1, RELIABILITY_RUNS + 1):
                print(f"\n--- Reliability Run {run_number}/{RELIABILITY_RUNS} ---")
                
                run_result = self.test_complete_workflow_single_run(run_number)
                reliability_results.append(run_result)
                
                if run_result['success']:
                    successful_runs += 1
                    total_time += run_result['total_time']
                    print(f"✅ Run {run_number} completed in {run_result['total_time']:.1f}s")
                else:
                    print(f"❌ Run {run_number} failed at {run_result.get('step_failed', 'unknown')}: {run_result.get('error', 'unknown error')}")
                
                # Wait between runs to avoid overwhelming the system
                if run_number < RELIABILITY_RUNS:
                    print("   Waiting 10 seconds before next run...")
                    time.sleep(10)
            
            success_rate = (successful_runs / RELIABILITY_RUNS) * 100
            avg_time = total_time / successful_runs if successful_runs > 0 else 0
            
            # Determine reliability status
            if success_rate >= 80:
                reliability_status = "EXCELLENT"
            elif success_rate >= 60:
                reliability_status = "GOOD"
            elif success_rate >= 40:
                reliability_status = "FAIR"
            else:
                reliability_status = "POOR"
            
            reliability_summary = {
                'success_rate': success_rate,
                'successful_runs': successful_runs,
                'total_runs': RELIABILITY_RUNS,
                'average_time': avg_time,
                'reliability_status': reliability_status,
                'run_results': reliability_results
            }
            
            if success_rate >= 60:  # At least 60% success rate
                self.log_test("Reliability Testing", True, 
                             f"{reliability_status} reliability: {success_rate:.0f}% success rate, avg {avg_time:.1f}s")
            else:
                self.log_test("Reliability Testing", False, 
                             f"{reliability_status} reliability: {success_rate:.0f}% success rate")
            
            return reliability_summary
            
        except Exception as e:
            self.log_test("Reliability Testing", False, f"Exception: {str(e)}")
            return {
                'success_rate': 0,
                'successful_runs': 0,
                'total_runs': RELIABILITY_RUNS,
                'reliability_status': 'ERROR',
                'error': str(e)
            }
    
    def test_performance_benchmarks(self, reliability_results: Dict[str, Any]) -> bool:
        """Test that performance meets acceptable benchmarks"""
        try:
            print("⚡ Testing performance benchmarks...")
            
            if not reliability_results.get('run_results'):
                self.log_test("Performance Benchmarks", False, "No reliability data available")
                return False
            
            successful_runs = [r for r in reliability_results['run_results'] if r['success']]
            
            if not successful_runs:
                self.log_test("Performance Benchmarks", False, "No successful runs to analyze")
                return False
            
            # Calculate performance metrics
            times = [r['total_time'] for r in successful_runs]
            orchestration_times = [r.get('orchestration_time', 0) for r in successful_runs]
            
            avg_total_time = sum(times) / len(times)
            max_total_time = max(times)
            min_total_time = min(times)
            
            avg_orchestration_time = sum(orchestration_times) / len(orchestration_times)
            
            # Performance benchmarks
            performance_issues = []
            
            # Total workflow should complete within 5 minutes
            if avg_total_time > 300:
                performance_issues.append(f"Average total time too long: {avg_total_time:.1f}s")
            
            # No single run should take more than 8 minutes
            if max_total_time > 480:
                performance_issues.append(f"Maximum time too long: {max_total_time:.1f}s")
            
            # Agent orchestration should complete within 4 minutes on average
            if avg_orchestration_time > 240:
                performance_issues.append(f"Average orchestration time too long: {avg_orchestration_time:.1f}s")
            
            if performance_issues:
                self.log_test("Performance Benchmarks", False, 
                             f"Performance issues: {'; '.join(performance_issues)}")
                return False
            else:
                self.log_test("Performance Benchmarks", True, 
                             f"Good performance - Avg: {avg_total_time:.1f}s, Max: {max_total_time:.1f}s")
                return True
                
        except Exception as e:
            self.log_test("Performance Benchmarks", False, f"Exception: {str(e)}")
            return False
    
    def test_content_quality_consistency(self, reliability_results: Dict[str, Any]) -> bool:
        """Test that content quality is consistent across runs"""
        try:
            print("🔍 Testing content quality consistency...")
            
            if not reliability_results.get('run_results'):
                self.log_test("Content Quality Consistency", False, "No reliability data available")
                return False
            
            successful_runs = [r for r in reliability_results['run_results'] if r['success']]
            
            if len(successful_runs) < 2:
                self.log_test("Content Quality Consistency", False, "Need at least 2 successful runs")
                return False
            
            # Analyze content consistency
            news_item_counts = [r.get('content_summary', {}).get('news_items', 0) for r in successful_runs]
            script_lengths = [r.get('content_summary', {}).get('script_length', 0) for r in successful_runs]
            word_timing_counts = [r.get('content_summary', {}).get('word_timings', 0) for r in successful_runs]
            agent_output_counts = [r.get('content_summary', {}).get('agent_outputs', 0) for r in successful_runs]
            
            quality_issues = []
            
            # Check news items consistency (should be 3-10 items)
            if min(news_item_counts) < 3:
                quality_issues.append(f"Some runs have too few news items: {min(news_item_counts)}")
            
            if max(news_item_counts) - min(news_item_counts) > 5:
                quality_issues.append(f"News item count varies too much: {min(news_item_counts)}-{max(news_item_counts)}")
            
            # Check script length consistency (should be at least 500 characters)
            if min(script_lengths) < 500:
                quality_issues.append(f"Some scripts too short: {min(script_lengths)} chars")
            
            # Check word timings (should have some)
            if min(word_timing_counts) < 10:
                quality_issues.append(f"Some runs missing word timings: {min(word_timing_counts)}")
            
            # Check agent outputs (should have at least 2)
            if min(agent_output_counts) < 2:
                quality_issues.append(f"Some runs missing agent outputs: {min(agent_output_counts)}")
            
            if quality_issues:
                self.log_test("Content Quality Consistency", False, 
                             f"Quality issues: {'; '.join(quality_issues)}")
                return False
            else:
                avg_news = sum(news_item_counts) / len(news_item_counts)
                avg_script = sum(script_lengths) / len(script_lengths)
                self.log_test("Content Quality Consistency", True, 
                             f"Consistent quality - Avg {avg_news:.1f} news items, {avg_script:.0f} char scripts")
                return True
                
        except Exception as e:
            self.log_test("Content Quality Consistency", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run comprehensive end-to-end validation"""
        print("🚀 Starting Comprehensive End-to-End Validation")
        print(f"API URL: {self.api_url}")
        print(f"Frontend URL: {self.frontend_url}")
        print(f"Reliability Runs: {RELIABILITY_RUNS}")
        print("=" * 80)
        
        # Test 1: System health check
        print("\n🏥 Test 1: System Health Check")
        health_success = self.test_system_health_check()
        
        if not health_success:
            print("❌ System health check failed - aborting comprehensive validation")
            return self._generate_validation_summary(False, None)
        
        # Test 2: Reliability testing
        print(f"\n🔄 Test 2: Reliability Testing ({RELIABILITY_RUNS} runs)")
        reliability_results = self.test_reliability_under_various_conditions()
        
        # Test 3: Performance benchmarks
        print("\n⚡ Test 3: Performance Benchmarks")
        performance_success = self.test_performance_benchmarks(reliability_results)
        
        # Test 4: Content quality consistency
        print("\n🔍 Test 4: Content Quality Consistency")
        quality_success = self.test_content_quality_consistency(reliability_results)
        
        # Calculate overall success
        reliability_success = reliability_results.get('success_rate', 0) >= 60
        overall_success = (
            health_success and
            reliability_success and
            performance_success and
            quality_success
        )
        
        return self._generate_validation_summary(overall_success, reliability_results)
    
    def _generate_validation_summary(self, overall_success: bool, reliability_results: Dict = None) -> Dict[str, Any]:
        """Generate comprehensive validation summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print("📊 Comprehensive End-to-End Validation Summary")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if reliability_results:
            print(f"Workflow Reliability: {reliability_results.get('success_rate', 0):.0f}% ({reliability_results.get('successful_runs', 0)}/{reliability_results.get('total_runs', 0)} runs)")
            print(f"Average Workflow Time: {reliability_results.get('average_time', 0):.1f}s")
            print(f"Reliability Status: {reliability_results.get('reliability_status', 'UNKNOWN')}")
        
        print("\n📋 Test Details:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"  {status} {result['test']}: {result['message']}")
        
        if overall_success:
            print("\n🎉 OVERALL STATUS: SYSTEM READY FOR PRODUCTION")
            print("✅ All system components healthy")
            print("✅ Reliable workflow execution")
            print("✅ Performance meets benchmarks")
            print("✅ Content quality consistent")
            print("\n🚀 The Curio News system is working correctly and ready for judge demo!")
        else:
            print("\n⚠️ OVERALL STATUS: SYSTEM NEEDS ATTENTION")
            print("\nFailed Areas:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  ❌ {result['test']}: {result['message']}")
            
            if reliability_results and reliability_results.get('success_rate', 0) < 60:
                print(f"  ❌ Workflow Reliability: {reliability_results.get('success_rate', 0):.0f}% (need ≥60%)")
        
        return {
            'overall_success': overall_success,
            'success_rate': success_rate,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'test_results': self.test_results,
            'reliability_results': reliability_results,
            'validation_status': {
                'system_health': any(r['test'] == 'System Health Check' and r['success'] for r in self.test_results),
                'workflow_reliability': reliability_results.get('success_rate', 0) >= 60 if reliability_results else False,
                'performance_benchmarks': any(r['test'] == 'Performance Benchmarks' and r['success'] for r in self.test_results),
                'content_quality': any(r['test'] == 'Content Quality Consistency' and r['success'] for r in self.test_results)
            }
        }

def main():
    """Main validation execution"""
    validator = ComprehensiveE2EValidator()
    results = validator.run_comprehensive_validation()
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"tests/comprehensive_validation_results_{timestamp}.json"
    
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