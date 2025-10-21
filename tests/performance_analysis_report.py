#!/usr/bin/env python3
"""
Performance Analysis Report Generator
Task 7.3: Conduct performance and reliability testing

Generates a comprehensive performance analysis report based on test results.
"""

import json
import os
import glob
import statistics
from datetime import datetime
from typing import Dict, List, Any, Optional

class PerformanceAnalysisReporter:
    def __init__(self):
        self.test_results_dir = "tests"
        self.analysis_data = {}
        
    def load_latest_test_results(self) -> Dict[str, Any]:
        """Load the most recent test results from various test files"""
        results = {}
        
        # Load enhanced performance reliability results
        enhanced_files = glob.glob(os.path.join(self.test_results_dir, "enhanced_performance_reliability_results_*.json"))
        if enhanced_files:
            latest_enhanced = max(enhanced_files, key=os.path.getctime)
            try:
                with open(latest_enhanced, 'r') as f:
                    results['enhanced_performance'] = json.load(f)
                    results['enhanced_performance']['file'] = latest_enhanced
            except Exception as e:
                print(f"⚠️ Could not load enhanced performance results: {e}")
        
        # Load comprehensive validation results
        comprehensive_files = glob.glob(os.path.join(self.test_results_dir, "comprehensive_validation_results_*.json"))
        if comprehensive_files:
            latest_comprehensive = max(comprehensive_files, key=os.path.getctime)
            try:
                with open(latest_comprehensive, 'r') as f:
                    results['comprehensive_validation'] = json.load(f)
                    results['comprehensive_validation']['file'] = latest_comprehensive
            except Exception as e:
                print(f"⚠️ Could not load comprehensive validation results: {e}")
        
        # Load performance benchmark results
        performance_files = glob.glob(os.path.join(self.test_results_dir, "performance_results_*.json"))
        if performance_files:
            latest_performance = max(performance_files, key=os.path.getctime)
            try:
                with open(latest_performance, 'r') as f:
                    results['performance_benchmarks'] = json.load(f)
                    results['performance_benchmarks']['file'] = latest_performance
            except Exception as e:
                print(f"⚠️ Could not load performance benchmark results: {e}")
        
        return results
    
    def analyze_bootstrap_performance(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze bootstrap endpoint performance across all tests"""
        bootstrap_analysis = {
            'response_times': [],
            'success_rates': [],
            'concurrent_performance': {},
            'consistency_metrics': {}
        }
        
        # From enhanced performance test
        enhanced = results.get('enhanced_performance', {})
        if enhanced:
            for test_result in enhanced.get('test_results', []):
                if 'Bootstrap Performance Under Load' in test_result.get('test', ''):
                    data = test_result.get('data', {})
                    if data:
                        bootstrap_analysis['response_times'].append(data.get('avg_response_time', 0))
                        bootstrap_analysis['success_rates'].append(data.get('success_rate', 0))
                        bootstrap_analysis['concurrent_performance'] = {
                            'avg_response_time': data.get('avg_response_time', 0),
                            'max_response_time': data.get('max_response_time', 0),
                            'min_response_time': data.get('min_response_time', 0),
                            'concurrent_users': data.get('concurrent_users', 0),
                            'success_rate': data.get('success_rate', 0)
                        }
        
        # From performance benchmarks
        perf_bench = results.get('performance_benchmarks', {})
        if perf_bench:
            bootstrap_perf = perf_bench.get('bootstrap_performance', {})
            if bootstrap_perf:
                bootstrap_analysis['benchmark_performance'] = {
                    'avg_response_time': bootstrap_perf.get('avg_response_time', 0),
                    'samples': bootstrap_perf.get('samples', 0),
                    'status': bootstrap_perf.get('status', 'Unknown')
                }
        
        # Calculate overall metrics
        if bootstrap_analysis['response_times']:
            bootstrap_analysis['overall_metrics'] = {
                'avg_response_time': statistics.mean(bootstrap_analysis['response_times']),
                'min_response_time': min(bootstrap_analysis['response_times']),
                'max_response_time': max(bootstrap_analysis['response_times']),
                'response_time_consistency': statistics.stdev(bootstrap_analysis['response_times']) if len(bootstrap_analysis['response_times']) > 1 else 0
            }
        
        if bootstrap_analysis['success_rates']:
            bootstrap_analysis['overall_metrics']['avg_success_rate'] = statistics.mean(bootstrap_analysis['success_rates'])
        
        return bootstrap_analysis
    
    def analyze_content_quality(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content quality metrics across tests"""
        quality_analysis = {
            'consistency_scores': [],
            'content_completeness': {},
            'quality_trends': {}
        }
        
        # From enhanced performance test
        enhanced = results.get('enhanced_performance', {})
        if enhanced:
            for test_result in enhanced.get('test_results', []):
                if 'Content Quality Consistency' in test_result.get('test', ''):
                    data = test_result.get('data', {})
                    if data:
                        quality_scores = data.get('quality_scores', {})
                        quality_analysis['consistency_scores'].append(quality_scores.get('avg', 0))
                        quality_analysis['content_completeness'] = {
                            'news_items_avg': data.get('news_items', {}).get('avg', 0),
                            'script_length_avg': data.get('script_length', {}).get('avg', 0),
                            'audio_success_rate': data.get('audio_success_rate', 0),
                            'success_rate': data.get('success_rate', 0)
                        }
        
        # Calculate overall quality metrics
        if quality_analysis['consistency_scores']:
            quality_analysis['overall_quality'] = {
                'avg_quality_score': statistics.mean(quality_analysis['consistency_scores']),
                'quality_consistency': statistics.stdev(quality_analysis['consistency_scores']) if len(quality_analysis['consistency_scores']) > 1 else 0
            }
        
        return quality_analysis
    
    def analyze_system_reliability(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze overall system reliability"""
        reliability_analysis = {
            'component_health': {},
            'failure_patterns': [],
            'uptime_metrics': {}
        }
        
        # From enhanced performance test
        enhanced = results.get('enhanced_performance', {})
        if enhanced:
            # System health check
            for test_result in enhanced.get('test_results', []):
                if 'System Health Check' in test_result.get('test', ''):
                    data = test_result.get('data', {})
                    if data:
                        reliability_analysis['component_health'] = {
                            'bootstrap_api': data.get('bootstrap', {}).get('status_code') == 200,
                            'frontend': data.get('frontend', {}).get('status_code') == 200,
                            'agent_status_api': data.get('agent_status', {}).get('accessible', False)
                        }
            
            # Overall test success rate
            total_tests = enhanced.get('total_tests', 0)
            passed_tests = enhanced.get('passed_tests', 0)
            reliability_analysis['test_success_rate'] = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # From comprehensive validation
        comprehensive = results.get('comprehensive_validation', {})
        if comprehensive:
            reliability_analysis['workflow_reliability'] = {
                'success_rate': comprehensive.get('workflow_success_rate', 0),
                'average_time': comprehensive.get('average_workflow_time', 0),
                'reliability_status': comprehensive.get('reliability_status', 'Unknown')
            }
        
        return reliability_analysis
    
    def analyze_performance_trends(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance trends and identify bottlenecks"""
        trends_analysis = {
            'bottlenecks': [],
            'performance_grades': {},
            'recommendations': []
        }
        
        # Identify bottlenecks
        enhanced = results.get('enhanced_performance', {})
        if enhanced:
            enhanced_analysis = enhanced.get('enhanced_analysis', {})
            
            if enhanced_analysis.get('generation_timeout_detected'):
                trends_analysis['bottlenecks'].append({
                    'component': 'Content Generation',
                    'issue': 'Timeout during generation process',
                    'impact': 'High',
                    'description': 'Agent orchestration is taking longer than expected'
                })
            
            if not enhanced_analysis.get('bootstrap_performance_good', True):
                trends_analysis['bottlenecks'].append({
                    'component': 'Bootstrap API',
                    'issue': 'Slow response times',
                    'impact': 'Medium',
                    'description': 'Content delivery may be slower than optimal'
                })
        
        # Performance grades
        perf_bench = results.get('performance_benchmarks', {})
        if perf_bench:
            critical_perf = perf_bench.get('critical_performance', {})
            trends_analysis['performance_grades'] = {
                'bootstrap': 'A' if critical_perf.get('bootstrap') else 'B',
                'demo_readiness': 'A' if critical_perf.get('demo_ready') else 'C',
                'overall_performance': perf_bench.get('performance_status', 'Unknown')
            }
        
        # Generate recommendations
        if trends_analysis['bottlenecks']:
            for bottleneck in trends_analysis['bottlenecks']:
                if bottleneck['component'] == 'Content Generation':
                    trends_analysis['recommendations'].extend([
                        'Implement agent timeout monitoring and alerting',
                        'Consider parallel agent execution optimization',
                        'Add agent performance profiling',
                        'Implement graceful degradation for slow agents'
                    ])
                elif bottleneck['component'] == 'Bootstrap API':
                    trends_analysis['recommendations'].extend([
                        'Implement response caching',
                        'Optimize database queries',
                        'Add CDN for static content'
                    ])
        else:
            trends_analysis['recommendations'].append('System performance is within acceptable ranges')
        
        return trends_analysis
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance analysis report"""
        print("📊 Generating Comprehensive Performance Analysis Report")
        print("=" * 80)
        
        # Load all test results
        results = self.load_latest_test_results()
        
        if not results:
            print("⚠️ No test results found. Please run performance tests first.")
            return {}
        
        print(f"📁 Loaded {len(results)} test result files")
        for test_type, data in results.items():
            print(f"   • {test_type}: {data.get('file', 'Unknown file')}")
        
        # Perform analysis
        bootstrap_analysis = self.analyze_bootstrap_performance(results)
        quality_analysis = self.analyze_content_quality(results)
        reliability_analysis = self.analyze_system_reliability(results)
        trends_analysis = self.analyze_performance_trends(results)
        
        # Generate report
        report = {
            'report_generated': datetime.now().isoformat(),
            'test_files_analyzed': len(results),
            'bootstrap_performance': bootstrap_analysis,
            'content_quality': quality_analysis,
            'system_reliability': reliability_analysis,
            'performance_trends': trends_analysis,
            'raw_results': results
        }
        
        # Print summary
        self.print_report_summary(report)
        
        return report
    
    def print_report_summary(self, report: Dict[str, Any]):
        """Print a human-readable summary of the performance analysis"""
        print("\n" + "=" * 80)
        print("📈 PERFORMANCE ANALYSIS SUMMARY")
        print("=" * 80)
        
        # Bootstrap Performance
        bootstrap = report.get('bootstrap_performance', {})
        overall_metrics = bootstrap.get('overall_metrics', {})
        
        print("\n🚀 Bootstrap Performance:")
        if overall_metrics:
            avg_time = overall_metrics.get('avg_response_time', 0)
            success_rate = overall_metrics.get('avg_success_rate', 0)
            print(f"   Average Response Time: {avg_time:.3f}s")
            print(f"   Success Rate: {success_rate:.1f}%")
            
            if avg_time < 1.0:
                print("   ✅ Excellent response times")
            elif avg_time < 3.0:
                print("   ✅ Good response times")
            else:
                print("   ⚠️ Response times could be improved")
        
        # Content Quality
        quality = report.get('content_quality', {})
        overall_quality = quality.get('overall_quality', {})
        
        print("\n📝 Content Quality:")
        if overall_quality:
            avg_quality = overall_quality.get('avg_quality_score', 0)
            print(f"   Average Quality Score: {avg_quality:.2f}/1.00")
            
            if avg_quality >= 0.9:
                print("   ✅ Excellent content quality")
            elif avg_quality >= 0.7:
                print("   ✅ Good content quality")
            else:
                print("   ⚠️ Content quality could be improved")
        
        completeness = quality.get('content_completeness', {})
        if completeness:
            print(f"   News Items (avg): {completeness.get('news_items_avg', 0):.1f}")
            print(f"   Audio Success Rate: {completeness.get('audio_success_rate', 0):.1%}")
        
        # System Reliability
        reliability = report.get('system_reliability', {})
        component_health = reliability.get('component_health', {})
        
        print("\n🏥 System Reliability:")
        if component_health:
            healthy_components = sum(1 for status in component_health.values() if status)
            total_components = len(component_health)
            print(f"   Component Health: {healthy_components}/{total_components} healthy")
            
            for component, status in component_health.items():
                status_icon = "✅" if status else "❌"
                print(f"   {status_icon} {component.replace('_', ' ').title()}")
        
        test_success = reliability.get('test_success_rate', 0)
        print(f"   Test Success Rate: {test_success:.1f}%")
        
        # Performance Trends
        trends = report.get('performance_trends', {})
        bottlenecks = trends.get('bottlenecks', [])
        
        print("\n🔍 Performance Analysis:")
        if bottlenecks:
            print("   Identified Bottlenecks:")
            for bottleneck in bottlenecks:
                impact_icon = "🔴" if bottleneck['impact'] == 'High' else "🟡"
                print(f"   {impact_icon} {bottleneck['component']}: {bottleneck['issue']}")
        else:
            print("   ✅ No significant bottlenecks identified")
        
        grades = trends.get('performance_grades', {})
        if grades:
            print("   Performance Grades:")
            for component, grade in grades.items():
                grade_icon = "🏆" if grade == 'A' else "✅" if grade == 'B' else "⚠️"
                print(f"   {grade_icon} {component.replace('_', ' ').title()}: Grade {grade}")
        
        # Recommendations
        recommendations = trends.get('recommendations', [])
        if recommendations:
            print("\n💡 Recommendations:")
            for i, rec in enumerate(recommendations[:5], 1):  # Show top 5
                print(f"   {i}. {rec}")
        
        # Overall Assessment
        print("\n🎯 Overall Assessment:")
        
        # Calculate overall score
        scores = []
        if overall_metrics.get('avg_success_rate', 0) >= 90:
            scores.append(1)
        elif overall_metrics.get('avg_success_rate', 0) >= 70:
            scores.append(0.7)
        else:
            scores.append(0.3)
        
        if overall_quality.get('avg_quality_score', 0) >= 0.8:
            scores.append(1)
        elif overall_quality.get('avg_quality_score', 0) >= 0.6:
            scores.append(0.7)
        else:
            scores.append(0.3)
        
        if test_success >= 80:
            scores.append(1)
        elif test_success >= 60:
            scores.append(0.7)
        else:
            scores.append(0.3)
        
        overall_score = statistics.mean(scores) if scores else 0
        
        if overall_score >= 0.9:
            print("   🏆 EXCELLENT - System performing at optimal levels")
        elif overall_score >= 0.7:
            print("   ✅ GOOD - System performing well with minor areas for improvement")
        elif overall_score >= 0.5:
            print("   ⚠️ ACCEPTABLE - System functional but needs attention")
        else:
            print("   🔴 NEEDS IMPROVEMENT - System has significant performance issues")
        
        print(f"   Overall Performance Score: {overall_score:.1%}")

def main():
    """Main report generation"""
    reporter = PerformanceAnalysisReporter()
    
    try:
        report = reporter.generate_comprehensive_report()
        
        if report:
            # Save comprehensive report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"tests/performance_analysis_report_{timestamp}.json"
            
            try:
                os.makedirs("tests", exist_ok=True)
                with open(report_file, 'w') as f:
                    json.dump(report, f, indent=2)
                print(f"\n📄 Comprehensive analysis report saved to: {report_file}")
            except Exception as e:
                print(f"⚠️ Could not save report file: {e}")
            
            # Determine exit code based on overall performance
            bootstrap_good = report.get('bootstrap_performance', {}).get('overall_metrics', {}).get('avg_success_rate', 0) >= 80
            quality_good = report.get('content_quality', {}).get('overall_quality', {}).get('avg_quality_score', 0) >= 0.6
            reliability_good = report.get('system_reliability', {}).get('test_success_rate', 0) >= 60
            
            overall_good = sum([bootstrap_good, quality_good, reliability_good]) >= 2
            
            sys.exit(0 if overall_good else 1)
        else:
            print("❌ Could not generate performance analysis report")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Report generation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import sys
    main()