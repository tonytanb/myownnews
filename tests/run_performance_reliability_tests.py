#!/usr/bin/env python3
"""
Performance and Reliability Test Runner
Executes comprehensive performance and reliability testing for Task 7.3

This script runs all performance and reliability tests and generates a comprehensive report.
"""

import subprocess
import sys
import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any

class PerformanceReliabilityTestRunner:
    def __init__(self):
        self.test_results = {}
        self.start_time = datetime.now()
        
    def run_test_script(self, script_name: str, description: str) -> Dict[str, Any]:
        """Run a test script and capture results"""
        print(f"\n{'='*60}")
        print(f"🧪 Running {description}")
        print(f"Script: {script_name}")
        print(f"{'='*60}")
        
        script_path = os.path.join("tests", script_name)
        
        if not os.path.exists(script_path):
            return {
                'success': False,
                'error': f"Test script not found: {script_path}",
                'execution_time': 0
            }
        
        start_time = time.time()
        
        try:
            # Run the test script
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                timeout=1800  # 30 minute timeout
            )
            
            execution_time = time.time() - start_time
            
            # Parse output
            stdout = result.stdout
            stderr = result.stderr
            return_code = result.returncode
            
            print(f"📊 Test completed in {execution_time:.1f} seconds")
            print(f"Return code: {return_code}")
            
            if stdout:
                print("STDOUT:")
                print(stdout)
            
            if stderr:
                print("STDERR:")
                print(stderr)
            
            return {
                'success': return_code == 0,
                'return_code': return_code,
                'stdout': stdout,
                'stderr': stderr,
                'execution_time': execution_time
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Test timed out after 30 minutes',
                'execution_time': time.time() - start_time
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'execution_time': time.time() - start_time
            }
    
    def load_latest_test_results(self, pattern: str) -> Dict[str, Any]:
        """Load the most recent test results file matching pattern"""
        try:
            test_files = [f for f in os.listdir("tests") if f.startswith(pattern) and f.endswith(".json")]
            
            if not test_files:
                return {}
            
            # Get the most recent file
            latest_file = max(test_files, key=lambda f: os.path.getctime(os.path.join("tests", f)))
            
            with open(os.path.join("tests", latest_file), 'r') as f:
                return json.load(f)
                
        except Exception as e:
            print(f"⚠️ Could not load test results: {e}")
            return {}
    
    def run_all_performance_reliability_tests(self) -> Dict[str, Any]:
        """Run all performance and reliability tests"""
        print("🚀 Starting Comprehensive Performance and Reliability Testing")
        print(f"Start time: {self.start_time.isoformat()}")
        print("="*80)
        
        # Test 1: Core Performance and Reliability Test
        print("\n🎯 Test Suite 1: Core Performance and Reliability")
        perf_reliability_result = self.run_test_script(
            "performance_reliability_test.py",
            "Core Performance and Reliability Testing"
        )
        self.test_results['performance_reliability'] = perf_reliability_result
        
        # Load detailed results if available
        if perf_reliability_result['success']:
            detailed_results = self.load_latest_test_results("performance_reliability_results_")
            if detailed_results:
                self.test_results['performance_reliability']['detailed_results'] = detailed_results
        
        # Test 2: Comprehensive E2E Validation (for comparison)
        print("\n🎯 Test Suite 2: Comprehensive E2E Validation")
        e2e_result = self.run_test_script(
            "comprehensive_e2e_validation.py",
            "Comprehensive End-to-End Validation"
        )
        self.test_results['comprehensive_e2e'] = e2e_result
        
        # Load detailed results if available
        if e2e_result['success']:
            detailed_results = self.load_latest_test_results("comprehensive_validation_results_")
            if detailed_results:
                self.test_results['comprehensive_e2e']['detailed_results'] = detailed_results
        
        # Test 3: Agent Orchestration E2E (for agent-specific performance)
        print("\n🎯 Test Suite 3: Agent Orchestration Performance")
        agent_result = self.run_test_script(
            "agent_orchestration_e2e_test.py",
            "Agent Orchestration Performance Testing"
        )
        self.test_results['agent_orchestration'] = agent_result
        
        # Load detailed results if available
        if agent_result['success']:
            detailed_results = self.load_latest_test_results("agent_orchestration_results_")
            if detailed_results:
                self.test_results['agent_orchestration']['detailed_results'] = detailed_results
        
        # Test 4: Performance Test (existing)
        print("\n🎯 Test Suite 4: Performance Benchmarks")
        performance_result = self.run_test_script(
            "performance_test.py",
            "Performance Benchmarks and Optimization"
        )
        self.test_results['performance_benchmarks'] = performance_result
        
        # Load detailed results if available
        if performance_result['success']:
            detailed_results = self.load_latest_test_results("performance_results_")
            if detailed_results:
                self.test_results['performance_benchmarks']['detailed_results'] = detailed_results
        
        return self.generate_comprehensive_report()
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance and reliability report"""
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()
        
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE PERFORMANCE AND RELIABILITY REPORT")
        print("="*80)
        print(f"Test Duration: {total_duration:.1f} seconds ({total_duration/60:.1f} minutes)")
        print(f"Start Time: {self.start_time.isoformat()}")
        print(f"End Time: {end_time.isoformat()}")
        
        # Analyze results
        test_summary = {}
        overall_success = True
        
        for test_name, result in self.test_results.items():
            success = result.get('success', False)
            execution_time = result.get('execution_time', 0)
            
            test_summary[test_name] = {
                'success': success,
                'execution_time': execution_time,
                'status': '✅ PASS' if success else '❌ FAIL'
            }
            
            if not success:
                overall_success = False
            
            print(f"\n📋 {test_name.replace('_', ' ').title()}:")
            print(f"   Status: {'✅ PASS' if success else '❌ FAIL'}")
            print(f"   Execution Time: {execution_time:.1f}s")
            
            if not success:
                error = result.get('error', 'Unknown error')
                print(f"   Error: {error}")
        
        # Extract key performance metrics
        performance_metrics = self.extract_performance_metrics()
        
        print("\n📈 KEY PERFORMANCE METRICS:")
        for metric_name, metric_value in performance_metrics.items():
            print(f"   {metric_name}: {metric_value}")
        
        # Requirements validation
        requirements_status = self.validate_requirements()
        
        print("\n📋 REQUIREMENTS VALIDATION:")
        for req_id, status in requirements_status.items():
            print(f"   {'✅' if status else '❌'} {req_id}")
        
        # Overall assessment
        print(f"\n🎯 OVERALL ASSESSMENT:")
        if overall_success:
            print("✅ ALL PERFORMANCE AND RELIABILITY TESTS PASSED")
            print("🚀 System is ready for production deployment")
            print("📊 Performance meets all requirements")
            print("🔄 Reliability validated under various conditions")
        else:
            print("⚠️ SOME PERFORMANCE OR RELIABILITY ISSUES DETECTED")
            print("🔧 Review failed tests and address issues before deployment")
        
        # Generate final report
        final_report = {
            'overall_success': overall_success,
            'test_duration': total_duration,
            'start_time': self.start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'test_summary': test_summary,
            'performance_metrics': performance_metrics,
            'requirements_validation': requirements_status,
            'detailed_results': self.test_results,
            'task_completion': {
                'task_id': '7.3',
                'task_name': 'Conduct performance and reliability testing',
                'requirements_tested': ['5.1', '5.2', '5.3'],
                'completion_status': 'COMPLETED' if overall_success else 'ISSUES_DETECTED'
            }
        }
        
        return final_report
    
    def extract_performance_metrics(self) -> Dict[str, str]:
        """Extract key performance metrics from test results"""
        metrics = {}
        
        # From performance reliability test
        perf_rel_details = self.test_results.get('performance_reliability', {}).get('detailed_results', {})
        if perf_rel_details:
            perf_metrics = perf_rel_details.get('performance_metrics', {})
            metrics['Concurrent Users Tested'] = str(perf_metrics.get('concurrent_users_tested', 'N/A'))
            metrics['Reliability Runs'] = str(perf_metrics.get('reliability_runs_tested', 'N/A'))
            metrics['Max Agent Time Limit'] = f"{perf_metrics.get('max_agent_time_limit', 'N/A')}s"
            metrics['Max Total Time Limit'] = f"{perf_metrics.get('max_total_time_limit', 'N/A')}s"
        
        # From comprehensive E2E test
        e2e_details = self.test_results.get('comprehensive_e2e', {}).get('detailed_results', {})
        if e2e_details:
            reliability = e2e_details.get('reliability_results', {})
            if reliability:
                metrics['Workflow Success Rate'] = f"{reliability.get('success_rate', 0):.0f}%"
                metrics['Average Workflow Time'] = f"{reliability.get('average_time', 0):.1f}s"
                metrics['Reliability Status'] = reliability.get('reliability_status', 'Unknown')
        
        # From performance benchmarks
        perf_bench_details = self.test_results.get('performance_benchmarks', {}).get('detailed_results', {})
        if perf_bench_details:
            critical_perf = perf_bench_details.get('critical_performance', {})
            metrics['Bootstrap Performance'] = 'Good' if critical_perf.get('bootstrap') else 'Needs Improvement'
            metrics['Demo Ready'] = 'Yes' if critical_perf.get('demo_ready') else 'No'
        
        return metrics
    
    def validate_requirements(self) -> Dict[str, bool]:
        """Validate that all requirements are met"""
        requirements = {
            'Requirement 5.1: Fast and reliable content generation': False,
            'Requirement 5.2: Accurate progress indicators': False,
            'Requirement 5.3: Complete loading state replacement': False
        }
        
        # Check performance reliability test results
        perf_rel_details = self.test_results.get('performance_reliability', {}).get('detailed_results', {})
        if perf_rel_details:
            req_validation = perf_rel_details.get('requirements_validation', {})
            requirements['Requirement 5.1: Fast and reliable content generation'] = req_validation.get('requirement_5_1', False)
            requirements['Requirement 5.2: Accurate progress indicators'] = req_validation.get('requirement_5_2', False)
            requirements['Requirement 5.3: Complete loading state replacement'] = req_validation.get('requirement_5_3', False)
        
        return requirements

def main():
    """Main test runner execution"""
    runner = PerformanceReliabilityTestRunner()
    
    try:
        final_report = runner.run_all_performance_reliability_tests()
        
        # Save comprehensive report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"tests/performance_reliability_comprehensive_report_{timestamp}.json"
        
        try:
            os.makedirs("tests", exist_ok=True)
            with open(report_file, 'w') as f:
                json.dump(final_report, f, indent=2)
            print(f"\n📄 Comprehensive report saved to: {report_file}")
        except Exception as e:
            print(f"⚠️ Could not save report file: {e}")
        
        # Exit with appropriate code
        sys.exit(0 if final_report['overall_success'] else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️ Test execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()