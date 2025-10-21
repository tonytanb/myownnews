"""
Comprehensive Debugging Dashboard for Agent Analysis

This module provides a web-based debugging dashboard with tools for analyzing
agent execution patterns, visualizing performance metrics, and troubleshooting
common failures.
"""

import json
import boto3
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from agent_logger import AgentLogger
from agent_metrics import AgentPerformanceMonitor
from error_handler import ErrorHandler

@dataclass
class AgentAnalysisResult:
    """Result of agent pattern analysis"""
    agent_name: str
    analysis_period: str
    total_executions: int
    success_rate: float
    average_execution_time: float
    common_failures: List[Dict[str, Any]]
    performance_trends: Dict[str, Any]
    recommendations: List[str]
    health_score: float

@dataclass
class TroubleshootingGuide:
    """Troubleshooting guide for common issues"""
    issue_type: str
    symptoms: List[str]
    root_causes: List[str]
    solutions: List[str]
    prevention_tips: List[str]
    related_metrics: List[str]

class DebuggingDashboard:
    """Comprehensive debugging dashboard for agent analysis"""
    
    def __init__(self, curio_table: str, bucket: str = None):
        self.curio_table = curio_table
        self.bucket = bucket or os.getenv('BUCKET')
        self.dynamodb = boto3.client('dynamodb')
        self.cloudwatch = boto3.client('cloudwatch')
        
        # Initialize monitoring components
        self.agent_logger = AgentLogger(curio_table, enable_cloudwatch=True)
        self.performance_monitor = AgentPerformanceMonitor(
            namespace="CurioNews/Agents",
            enable_detailed_monitoring=True
        )
        self.error_handler = ErrorHandler(curio_table)
        
        # Dashboard configuration
        self.dashboard_config = {
            'refresh_interval_seconds': 30,
            'max_history_days': 7,
            'performance_thresholds': {
                'execution_time_warning_ms': 30000,  # 30 seconds
                'execution_time_critical_ms': 60000,  # 60 seconds
                'success_rate_warning': 0.85,  # 85%
                'success_rate_critical': 0.70,  # 70%
                'timeout_rate_warning': 0.05,  # 5%
                'timeout_rate_critical': 0.15   # 15%
            }
        }
        
        # Troubleshooting guides
        self.troubleshooting_guides = self._initialize_troubleshooting_guides()
    
    def generate_agent_analysis_report(self, agent_name: str = None, 
                                     hours_back: int = 24) -> Dict[str, Any]:
        """Generate comprehensive agent analysis report"""
        try:
            print(f"📊 Generating agent analysis report (hours_back: {hours_back})")
            
            # Get agent performance data
            if agent_name:
                agents_to_analyze = [agent_name]
            else:
                agents_to_analyze = [
                    "NEWS_FETCHER", "CONTENT_CURATOR", "FAVORITE_SELECTOR",
                    "SCRIPT_GENERATOR", "MEDIA_ENHANCER", "WEEKEND_EVENTS"
                ]
            
            analysis_results = {}
            overall_metrics = {
                'total_executions': 0,
                'total_successes': 0,
                'total_failures': 0,
                'average_execution_time': 0,
                'health_score': 0
            }
            
            for agent in agents_to_analyze:
                try:
                    # Get performance summary
                    performance_summary = self.performance_monitor.get_agent_performance_summary(
                        agent, hours_back
                    )
                    
                    # Get execution history
                    execution_history = self._get_agent_execution_history(agent, hours_back)
                    
                    # Analyze patterns
                    pattern_analysis = self._analyze_agent_patterns(agent, execution_history)
                    
                    # Generate recommendations
                    recommendations = self._generate_agent_recommendations(
                        agent, performance_summary, pattern_analysis
                    )
                    
                    # Calculate health score
                    health_score = self._calculate_agent_health_score(
                        performance_summary, pattern_analysis
                    )
                    
                    analysis_result = AgentAnalysisResult(
                        agent_name=agent,
                        analysis_period=f"{hours_back} hours",
                        total_executions=performance_summary.get('total_executions', 0),
                        success_rate=performance_summary.get('success_rate', 0),
                        average_execution_time=performance_summary.get('average_execution_time_ms', 0),
                        common_failures=pattern_analysis.get('common_failures', []),
                        performance_trends=pattern_analysis.get('trends', {}),
                        recommendations=recommendations,
                        health_score=health_score
                    )
                    
                    analysis_results[agent] = asdict(analysis_result)
                    
                    # Update overall metrics
                    overall_metrics['total_executions'] += analysis_result.total_executions
                    overall_metrics['total_successes'] += int(
                        analysis_result.total_executions * analysis_result.success_rate
                    )
                    overall_metrics['total_failures'] += int(
                        analysis_result.total_executions * (1 - analysis_result.success_rate)
                    )
                    
                except Exception as e:
                    print(f"❌ Error analyzing agent {agent}: {e}")
                    analysis_results[agent] = {
                        'error': str(e),
                        'health_score': 0
                    }
            
            # Calculate overall metrics
            if overall_metrics['total_executions'] > 0:
                overall_metrics['success_rate'] = (
                    overall_metrics['total_successes'] / overall_metrics['total_executions']
                )
                overall_metrics['failure_rate'] = (
                    overall_metrics['total_failures'] / overall_metrics['total_executions']
                )
                overall_metrics['health_score'] = sum(
                    result.get('health_score', 0) for result in analysis_results.values()
                ) / len(analysis_results)
            
            # Get system-wide issues
            system_issues = self._identify_system_issues(analysis_results)
            
            # Generate dashboard data
            dashboard_data = {
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'analysis_period': f"{hours_back} hours",
                'overall_metrics': overall_metrics,
                'agent_analysis': analysis_results,
                'system_issues': system_issues,
                'troubleshooting_guides': self._get_relevant_troubleshooting_guides(system_issues),
                'performance_visualization': self._generate_performance_visualization_data(
                    analysis_results, hours_back
                ),
                'dashboard_config': self.dashboard_config
            }
            
            return dashboard_data
            
        except Exception as e:
            print(f"❌ Error generating agent analysis report: {e}")
            import traceback
            traceback.print_exc()
            return {
                'error': str(e),
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
    
    def get_real_time_dashboard_data(self, run_id: str = None) -> Dict[str, Any]:
        """Get real-time dashboard data for active orchestration"""
        try:
            current_time = datetime.utcnow()
            
            # Get active orchestrations
            active_orchestrations = self._get_active_orchestrations()
            
            # Get recent performance metrics
            recent_metrics = self._get_recent_performance_metrics(minutes_back=30)
            
            # Get current system health
            system_health = self._get_current_system_health()
            
            # Get active alerts
            active_alerts = self._get_active_alerts()
            
            # If specific run_id provided, get detailed info
            run_specific_data = {}
            if run_id:
                run_specific_data = self._get_run_specific_data(run_id)
            
            dashboard_data = {
                'timestamp': current_time.isoformat(),
                'active_orchestrations': active_orchestrations,
                'recent_metrics': recent_metrics,
                'system_health': system_health,
                'active_alerts': active_alerts,
                'run_specific_data': run_specific_data,
                'refresh_interval': self.dashboard_config['refresh_interval_seconds']
            }
            
            return dashboard_data
            
        except Exception as e:
            print(f"❌ Error getting real-time dashboard data: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def get_troubleshooting_guide(self, issue_type: str = None) -> Dict[str, Any]:
        """Get troubleshooting guides for specific issues or all guides"""
        try:
            if issue_type:
                guide = self.troubleshooting_guides.get(issue_type)
                if guide:
                    return {
                        'guide': asdict(guide),
                        'timestamp': datetime.utcnow().isoformat()
                    }
                else:
                    return {
                        'error': f'No troubleshooting guide found for issue type: {issue_type}',
                        'available_guides': list(self.troubleshooting_guides.keys())
                    }
            else:
                return {
                    'guides': {k: asdict(v) for k, v in self.troubleshooting_guides.items()},
                    'timestamp': datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            print(f"❌ Error getting troubleshooting guide: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def generate_performance_visualization_data(self, hours_back: int = 24) -> Dict[str, Any]:
        """Generate data for performance visualization charts"""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=hours_back)
            
            # Get CloudWatch metrics for visualization
            visualization_data = {
                'time_series': {},
                'distribution_charts': {},
                'comparison_charts': {},
                'heatmaps': {}
            }
            
            agents = ["NEWS_FETCHER", "CONTENT_CURATOR", "FAVORITE_SELECTOR",
                     "SCRIPT_GENERATOR", "MEDIA_ENHANCER", "WEEKEND_EVENTS"]
            
            # Time series data for execution times
            for agent in agents:
                try:
                    execution_time_data = self.cloudwatch.get_metric_statistics(
                        Namespace='CurioNews/Agents',
                        MetricName='AgentExecutionTime',
                        Dimensions=[{'Name': 'AgentName', 'Value': agent}],
                        StartTime=start_time,
                        EndTime=end_time,
                        Period=3600,  # 1 hour periods
                        Statistics=['Average', 'Maximum', 'Minimum']
                    )
                    
                    success_rate_data = self.cloudwatch.get_metric_statistics(
                        Namespace='CurioNews/Agents',
                        MetricName='AgentExecutionSuccess',
                        Dimensions=[{'Name': 'AgentName', 'Value': agent}],
                        StartTime=start_time,
                        EndTime=end_time,
                        Period=3600,
                        Statistics=['Average']
                    )
                    
                    visualization_data['time_series'][agent] = {
                        'execution_times': [
                            {
                                'timestamp': point['Timestamp'].isoformat(),
                                'average': point['Average'],
                                'maximum': point['Maximum'],
                                'minimum': point['Minimum']
                            }
                            for point in execution_time_data['Datapoints']
                        ],
                        'success_rates': [
                            {
                                'timestamp': point['Timestamp'].isoformat(),
                                'success_rate': point['Average']
                            }
                            for point in success_rate_data['Datapoints']
                        ]
                    }
                    
                except Exception as e:
                    print(f"⚠️ Error getting visualization data for {agent}: {e}")
                    visualization_data['time_series'][agent] = {'error': str(e)}
            
            # Generate distribution charts
            visualization_data['distribution_charts'] = self._generate_distribution_charts(agents)
            
            # Generate comparison charts
            visualization_data['comparison_charts'] = self._generate_comparison_charts(agents)
            
            # Generate heatmaps
            visualization_data['heatmaps'] = self._generate_performance_heatmaps(agents, hours_back)
            
            return {
                'visualization_data': visualization_data,
                'generated_at': datetime.utcnow().isoformat(),
                'time_range': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat(),
                    'hours_back': hours_back
                }
            }
            
        except Exception as e:
            print(f"❌ Error generating performance visualization data: {e}")
            return {
                'error': str(e),
                'generated_at': datetime.utcnow().isoformat()
            }
    
    def _get_agent_execution_history(self, agent_name: str, hours_back: int) -> List[Dict]:
        """Get agent execution history from DynamoDB"""
        try:
            # Query agent logs from DynamoDB
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=hours_back)
            
            response = self.dynamodb.query(
                TableName=self.curio_table,
                IndexName='gsi1pk-gsi1sk-index',  # Assuming GSI exists
                KeyConditionExpression='gsi1pk = :pk AND gsi1sk BETWEEN :start AND :end',
                ExpressionAttributeValues={
                    ':pk': {'S': f'agent_logs_{agent_name}'},
                    ':start': {'S': start_time.isoformat()},
                    ':end': {'S': end_time.isoformat()}
                },
                ScanIndexForward=False,  # Most recent first
                Limit=1000
            )
            
            execution_history = []
            for item in response.get('Items', []):
                try:
                    log_data = json.loads(item.get('logData', {}).get('S', '{}'))
                    execution_history.append(log_data)
                except json.JSONDecodeError:
                    continue
            
            return execution_history
            
        except Exception as e:
            print(f"❌ Error getting agent execution history: {e}")
            return []
    
    def _analyze_agent_patterns(self, agent_name: str, execution_history: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns in agent execution history"""
        try:
            if not execution_history:
                return {'common_failures': [], 'trends': {}}
            
            # Analyze failure patterns
            failures = [log for log in execution_history if log.get('status') == 'FAILED']
            failure_analysis = {}
            
            if failures:
                # Group failures by error category
                error_categories = {}
                for failure in failures:
                    error_category = failure.get('error_category', 'UNKNOWN')
                    if error_category not in error_categories:
                        error_categories[error_category] = []
                    error_categories[error_category].append(failure)
                
                # Find most common failures
                common_failures = []
                for category, category_failures in error_categories.items():
                    common_failures.append({
                        'error_category': category,
                        'count': len(category_failures),
                        'percentage': len(category_failures) / len(failures) * 100,
                        'recent_examples': category_failures[:3],  # Last 3 examples
                        'first_occurrence': min(f.get('timestamp', '') for f in category_failures),
                        'last_occurrence': max(f.get('timestamp', '') for f in category_failures)
                    })
                
                # Sort by frequency
                common_failures.sort(key=lambda x: x['count'], reverse=True)
                failure_analysis['common_failures'] = common_failures[:5]  # Top 5
            else:
                failure_analysis['common_failures'] = []
            
            # Analyze performance trends
            execution_times = [
                log.get('execution_time_ms', 0) for log in execution_history 
                if log.get('execution_time_ms') is not None
            ]
            
            trends = {}
            if execution_times:
                trends['execution_time'] = {
                    'average': sum(execution_times) / len(execution_times),
                    'min': min(execution_times),
                    'max': max(execution_times),
                    'trend': self._calculate_trend(execution_times)
                }
            
            # Analyze retry patterns
            retry_counts = [log.get('retry_count', 0) for log in execution_history]
            if retry_counts:
                trends['retry_rate'] = {
                    'average': sum(retry_counts) / len(retry_counts),
                    'max': max(retry_counts),
                    'high_retry_percentage': len([r for r in retry_counts if r > 1]) / len(retry_counts) * 100
                }
            
            return {
                'common_failures': failure_analysis.get('common_failures', []),
                'trends': trends,
                'total_analyzed': len(execution_history),
                'analysis_period': f"{len(execution_history)} executions"
            }
            
        except Exception as e:
            print(f"❌ Error analyzing agent patterns: {e}")
            return {'common_failures': [], 'trends': {}}
    
    def _generate_agent_recommendations(self, agent_name: str, performance_summary: Dict, 
                                      pattern_analysis: Dict) -> List[str]:
        """Generate recommendations based on agent analysis"""
        recommendations = []
        
        try:
            # Performance-based recommendations
            avg_time = performance_summary.get('average_execution_time_ms', 0)
            success_rate = performance_summary.get('success_rate', 1.0)
            
            if avg_time > self.dashboard_config['performance_thresholds']['execution_time_critical_ms']:
                recommendations.append(
                    f"🚨 CRITICAL: {agent_name} execution time ({avg_time:.0f}ms) is critically high. "
                    "Consider optimizing prompts, increasing timeout, or reviewing model configuration."
                )
            elif avg_time > self.dashboard_config['performance_thresholds']['execution_time_warning_ms']:
                recommendations.append(
                    f"⚠️ WARNING: {agent_name} execution time ({avg_time:.0f}ms) is above optimal. "
                    "Monitor for performance degradation and consider optimization."
                )
            
            if success_rate < self.dashboard_config['performance_thresholds']['success_rate_critical']:
                recommendations.append(
                    f"🚨 CRITICAL: {agent_name} success rate ({success_rate:.1%}) is critically low. "
                    "Immediate investigation required. Check error patterns and model availability."
                )
            elif success_rate < self.dashboard_config['performance_thresholds']['success_rate_warning']:
                recommendations.append(
                    f"⚠️ WARNING: {agent_name} success rate ({success_rate:.1%}) is below target. "
                    "Review error patterns and consider improving error handling."
                )
            
            # Pattern-based recommendations
            common_failures = pattern_analysis.get('common_failures', [])
            if common_failures:
                top_failure = common_failures[0]
                error_category = top_failure['error_category']
                
                if error_category == 'TIMEOUT':
                    recommendations.append(
                        f"🔧 OPTIMIZATION: {agent_name} has frequent timeouts ({top_failure['percentage']:.1f}% of failures). "
                        "Consider increasing timeout values or optimizing prompt complexity."
                    )
                elif error_category == 'BEDROCK_THROTTLING':
                    recommendations.append(
                        f"🔧 OPTIMIZATION: {agent_name} experiencing Bedrock throttling ({top_failure['percentage']:.1f}% of failures). "
                        "Implement exponential backoff or request quota increase."
                    )
                elif error_category == 'CONTENT_VALIDATION':
                    recommendations.append(
                        f"🔧 OPTIMIZATION: {agent_name} has content validation issues ({top_failure['percentage']:.1f}% of failures). "
                        "Review prompt engineering and output format requirements."
                    )
            
            # Trend-based recommendations
            trends = pattern_analysis.get('trends', {})
            execution_trend = trends.get('execution_time', {}).get('trend')
            if execution_trend == 'increasing':
                recommendations.append(
                    f"📈 TREND ALERT: {agent_name} execution times are increasing over time. "
                    "Monitor for performance degradation and investigate root causes."
                )
            
            retry_rate = trends.get('retry_rate', {}).get('high_retry_percentage', 0)
            if retry_rate > 20:  # More than 20% of executions require retries
                recommendations.append(
                    f"🔄 RELIABILITY: {agent_name} has high retry rate ({retry_rate:.1f}%). "
                    "Investigate root causes of initial failures to improve first-attempt success rate."
                )
            
            # General recommendations
            if not recommendations:
                recommendations.append(
                    f"✅ HEALTHY: {agent_name} is performing within acceptable parameters. "
                    "Continue monitoring for any changes in performance patterns."
                )
            
        except Exception as e:
            print(f"❌ Error generating recommendations for {agent_name}: {e}")
            recommendations.append(f"❌ Error generating recommendations: {str(e)}")
        
        return recommendations
    
    def _calculate_agent_health_score(self, performance_summary: Dict, pattern_analysis: Dict) -> float:
        """Calculate overall health score for an agent (0-100)"""
        try:
            score = 100.0
            
            # Success rate impact (40% of score)
            success_rate = performance_summary.get('success_rate', 0)
            score *= (0.6 + 0.4 * success_rate)
            
            # Execution time impact (30% of score)
            avg_time = performance_summary.get('average_execution_time_ms', 0)
            time_threshold = self.dashboard_config['performance_thresholds']['execution_time_warning_ms']
            if avg_time > 0:
                time_score = max(0, 1 - (avg_time / time_threshold - 1) * 0.5)
                score *= (0.7 + 0.3 * time_score)
            
            # Error pattern impact (20% of score)
            common_failures = pattern_analysis.get('common_failures', [])
            if common_failures:
                # Reduce score based on failure diversity and frequency
                failure_impact = min(0.3, len(common_failures) * 0.05)
                score *= (1 - failure_impact)
            
            # Retry rate impact (10% of score)
            retry_rate = pattern_analysis.get('trends', {}).get('retry_rate', {}).get('high_retry_percentage', 0)
            if retry_rate > 0:
                retry_impact = min(0.2, retry_rate / 100 * 0.5)
                score *= (1 - retry_impact)
            
            return max(0, min(100, score))
            
        except Exception as e:
            print(f"❌ Error calculating health score: {e}")
            return 0.0
    
    def _identify_system_issues(self, analysis_results: Dict) -> List[Dict[str, Any]]:
        """Identify system-wide issues from agent analysis"""
        issues = []
        
        try:
            # Check for widespread failures
            failed_agents = [
                agent for agent, result in analysis_results.items()
                if result.get('success_rate', 1.0) < 0.8
            ]
            
            if len(failed_agents) >= 3:
                issues.append({
                    'type': 'WIDESPREAD_FAILURES',
                    'severity': 'CRITICAL',
                    'description': f'Multiple agents experiencing failures: {", ".join(failed_agents)}',
                    'affected_agents': failed_agents,
                    'recommended_actions': [
                        'Check Bedrock service status',
                        'Verify network connectivity',
                        'Review system resource usage',
                        'Check for recent configuration changes'
                    ]
                })
            
            # Check for performance degradation
            slow_agents = [
                agent for agent, result in analysis_results.items()
                if result.get('average_execution_time', 0) > 45000  # 45 seconds
            ]
            
            if len(slow_agents) >= 2:
                issues.append({
                    'type': 'PERFORMANCE_DEGRADATION',
                    'severity': 'WARNING',
                    'description': f'Multiple agents showing slow performance: {", ".join(slow_agents)}',
                    'affected_agents': slow_agents,
                    'recommended_actions': [
                        'Monitor system resources',
                        'Check Bedrock model performance',
                        'Review prompt complexity',
                        'Consider scaling adjustments'
                    ]
                })
            
            # Check for orchestration issues
            low_health_agents = [
                agent for agent, result in analysis_results.items()
                if result.get('health_score', 100) < 60
            ]
            
            if len(low_health_agents) >= 4:
                issues.append({
                    'type': 'ORCHESTRATION_ISSUES',
                    'severity': 'WARNING',
                    'description': 'Multiple agents showing poor health scores',
                    'affected_agents': low_health_agents,
                    'recommended_actions': [
                        'Review orchestration logic',
                        'Check agent dependencies',
                        'Verify timeout configurations',
                        'Analyze error handling effectiveness'
                    ]
                })
            
        except Exception as e:
            print(f"❌ Error identifying system issues: {e}")
            issues.append({
                'type': 'ANALYSIS_ERROR',
                'severity': 'ERROR',
                'description': f'Error during system issue analysis: {str(e)}',
                'recommended_actions': ['Check dashboard logs', 'Retry analysis']
            })
        
        return issues
    
    def _initialize_troubleshooting_guides(self) -> Dict[str, TroubleshootingGuide]:
        """Initialize comprehensive troubleshooting guides"""
        guides = {}
        
        # Agent timeout issues
        guides['AGENT_TIMEOUT'] = TroubleshootingGuide(
            issue_type='AGENT_TIMEOUT',
            symptoms=[
                'Agents consistently timing out after 60 seconds',
                'Incomplete content generation',
                'High retry rates',
                'User reports of slow loading'
            ],
            root_causes=[
                'Bedrock model latency spikes',
                'Complex prompts requiring more processing time',
                'Network connectivity issues',
                'Insufficient timeout configuration',
                'Model throttling or capacity limits'
            ],
            solutions=[
                'Increase agent timeout from 60s to 90s or 120s',
                'Implement progressive timeout strategy',
                'Optimize prompts to reduce complexity',
                'Add circuit breaker pattern for failing models',
                'Implement fallback to faster models',
                'Monitor Bedrock service health dashboard'
            ],
            prevention_tips=[
                'Set up CloudWatch alarms for timeout rates',
                'Regularly review and optimize prompts',
                'Implement health checks for Bedrock models',
                'Use exponential backoff for retries',
                'Monitor model performance trends'
            ],
            related_metrics=[
                'AgentExecutionTime',
                'AgentTimeoutRate',
                'BedrockModelLatency',
                'RetryCount'
            ]
        )
        
        # Bedrock throttling
        guides['BEDROCK_THROTTLING'] = TroubleshootingGuide(
            issue_type='BEDROCK_THROTTLING',
            symptoms=[
                'HTTP 429 errors from Bedrock',
                'Increased retry attempts',
                'Sporadic agent failures',
                'Performance degradation during peak hours'
            ],
            root_causes=[
                'Exceeded Bedrock service quotas',
                'High concurrent request volume',
                'Insufficient request rate limits',
                'Burst traffic patterns',
                'Model-specific throttling limits'
            ],
            solutions=[
                'Implement exponential backoff with jitter',
                'Request quota increase from AWS',
                'Distribute load across multiple models',
                'Implement request queuing system',
                'Add circuit breaker for throttled models',
                'Use different models for different agents'
            ],
            prevention_tips=[
                'Monitor quota utilization regularly',
                'Implement rate limiting at application level',
                'Set up CloudWatch alarms for throttling',
                'Plan for traffic spikes',
                'Use multiple AWS regions if needed'
            ],
            related_metrics=[
                'BedrockThrottleRate',
                'RequestsPerSecond',
                'QuotaUtilization',
                'ErrorRate'
            ]
        )
        
        # Content validation failures
        guides['CONTENT_VALIDATION'] = TroubleshootingGuide(
            issue_type='CONTENT_VALIDATION',
            symptoms=[
                'Generated content fails validation checks',
                'Malformed JSON responses',
                'Missing required content sections',
                'Content quality issues'
            ],
            root_causes=[
                'Inconsistent model outputs',
                'Prompt engineering issues',
                'Model hallucination',
                'Insufficient output constraints',
                'Temperature settings too high'
            ],
            solutions=[
                'Improve prompt engineering with examples',
                'Add stricter output format requirements',
                'Implement content post-processing',
                'Use lower temperature settings',
                'Add multiple validation layers',
                'Implement content sanitization'
            ],
            prevention_tips=[
                'Test prompts thoroughly before deployment',
                'Use structured output formats (JSON schema)',
                'Implement comprehensive validation rules',
                'Monitor content quality metrics',
                'Regular prompt optimization reviews'
            ],
            related_metrics=[
                'ContentValidationFailureRate',
                'OutputFormatErrors',
                'ContentQualityScore',
                'ValidationTime'
            ]
        )
        
        # Orchestration failures
        guides['ORCHESTRATION_FAILURE'] = TroubleshootingGuide(
            issue_type='ORCHESTRATION_FAILURE',
            symptoms=[
                'Multiple agents failing simultaneously',
                'Incomplete orchestration runs',
                'Inconsistent agent execution order',
                'Resource contention issues'
            ],
            root_causes=[
                'Race conditions in parallel execution',
                'Resource exhaustion (memory, CPU)',
                'Database connection issues',
                'Network connectivity problems',
                'Insufficient error handling'
            ],
            solutions=[
                'Implement proper synchronization mechanisms',
                'Add resource monitoring and limits',
                'Improve error handling and recovery',
                'Implement graceful degradation',
                'Add comprehensive logging',
                'Use database connection pooling'
            ],
            prevention_tips=[
                'Load test orchestration under various conditions',
                'Monitor system resources continuously',
                'Implement health checks for all dependencies',
                'Use proper error boundaries',
                'Regular system maintenance and updates'
            ],
            related_metrics=[
                'OrchestrationSuccessRate',
                'SystemResourceUsage',
                'DatabaseConnectionErrors',
                'ConcurrentExecutions'
            ]
        )
        
        # Performance degradation
        guides['PERFORMANCE_DEGRADATION'] = TroubleshootingGuide(
            issue_type='PERFORMANCE_DEGRADATION',
            symptoms=[
                'Gradually increasing execution times',
                'Reduced throughput over time',
                'Memory usage growth',
                'CPU utilization spikes'
            ],
            root_causes=[
                'Memory leaks in application code',
                'Database query performance degradation',
                'Increased data volume over time',
                'Inefficient caching strategies',
                'Resource contention'
            ],
            solutions=[
                'Profile application for memory leaks',
                'Optimize database queries and indexes',
                'Implement proper caching strategies',
                'Add resource cleanup procedures',
                'Scale resources based on demand',
                'Implement performance monitoring'
            ],
            prevention_tips=[
                'Regular performance testing',
                'Monitor key performance indicators',
                'Implement automated scaling',
                'Regular code reviews for performance',
                'Capacity planning based on growth trends'
            ],
            related_metrics=[
                'ExecutionTimePercentiles',
                'MemoryUsage',
                'CPUUtilization',
                'ThroughputRate'
            ]
        )
        
        return guides
    
    def _get_relevant_troubleshooting_guides(self, system_issues: List[Dict]) -> List[Dict]:
        """Get troubleshooting guides relevant to current system issues"""
        relevant_guides = []
        
        for issue in system_issues:
            issue_type = issue.get('type', '')
            
            # Map issue types to troubleshooting guides
            guide_mapping = {
                'WIDESPREAD_FAILURES': ['BEDROCK_THROTTLING', 'ORCHESTRATION_FAILURE'],
                'PERFORMANCE_DEGRADATION': ['PERFORMANCE_DEGRADATION', 'AGENT_TIMEOUT'],
                'ORCHESTRATION_ISSUES': ['ORCHESTRATION_FAILURE', 'CONTENT_VALIDATION']
            }
            
            guide_types = guide_mapping.get(issue_type, [])
            for guide_type in guide_types:
                if guide_type in self.troubleshooting_guides:
                    guide_data = asdict(self.troubleshooting_guides[guide_type])
                    guide_data['relevance_reason'] = f"Related to {issue_type}"
                    relevant_guides.append(guide_data)
        
        # Remove duplicates
        seen_types = set()
        unique_guides = []
        for guide in relevant_guides:
            if guide['issue_type'] not in seen_types:
                seen_types.add(guide['issue_type'])
                unique_guides.append(guide)
        
        return unique_guides
    
    def _generate_performance_visualization_data(self, analysis_results: Dict, 
                                               hours_back: int) -> Dict[str, Any]:
        """Generate data for performance visualization charts"""
        try:
            visualization_data = {
                'agent_health_radar': {},
                'execution_time_comparison': {},
                'success_rate_trends': {},
                'failure_distribution': {}
            }
            
            # Agent health radar chart data
            agents = list(analysis_results.keys())
            health_scores = [analysis_results[agent].get('health_score', 0) for agent in agents]
            
            visualization_data['agent_health_radar'] = {
                'agents': agents,
                'health_scores': health_scores,
                'chart_type': 'radar',
                'title': 'Agent Health Score Comparison'
            }
            
            # Execution time comparison
            execution_times = [
                analysis_results[agent].get('average_execution_time', 0) 
                for agent in agents
            ]
            
            visualization_data['execution_time_comparison'] = {
                'agents': agents,
                'execution_times': execution_times,
                'chart_type': 'bar',
                'title': 'Average Execution Time by Agent (ms)',
                'thresholds': {
                    'warning': self.dashboard_config['performance_thresholds']['execution_time_warning_ms'],
                    'critical': self.dashboard_config['performance_thresholds']['execution_time_critical_ms']
                }
            }
            
            # Success rate trends
            success_rates = [
                analysis_results[agent].get('success_rate', 0) * 100 
                for agent in agents
            ]
            
            visualization_data['success_rate_trends'] = {
                'agents': agents,
                'success_rates': success_rates,
                'chart_type': 'line',
                'title': 'Success Rate by Agent (%)',
                'thresholds': {
                    'warning': self.dashboard_config['performance_thresholds']['success_rate_warning'] * 100,
                    'critical': self.dashboard_config['performance_thresholds']['success_rate_critical'] * 100
                }
            }
            
            # Failure distribution
            failure_data = {}
            for agent, result in analysis_results.items():
                common_failures = result.get('common_failures', [])
                for failure in common_failures:
                    error_category = failure['error_category']
                    if error_category not in failure_data:
                        failure_data[error_category] = 0
                    failure_data[error_category] += failure['count']
            
            visualization_data['failure_distribution'] = {
                'categories': list(failure_data.keys()),
                'counts': list(failure_data.values()),
                'chart_type': 'pie',
                'title': 'Failure Distribution by Error Category'
            }
            
            return visualization_data
            
        except Exception as e:
            print(f"❌ Error generating performance visualization data: {e}")
            return {}
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from a list of values"""
        if len(values) < 2:
            return 'stable'
        
        # Simple linear trend calculation
        n = len(values)
        x_sum = sum(range(n))
        y_sum = sum(values)
        xy_sum = sum(i * values[i] for i in range(n))
        x2_sum = sum(i * i for i in range(n))
        
        slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum * x_sum)
        
        if slope > 0.1:
            return 'increasing'
        elif slope < -0.1:
            return 'decreasing'
        else:
            return 'stable'
    
    def _get_active_orchestrations(self) -> List[Dict]:
        """Get currently active orchestrations"""
        try:
            # Query for active orchestrations from the last hour
            current_time = datetime.utcnow()
            one_hour_ago = current_time - timedelta(hours=1)
            
            response = self.dynamodb.query(
                TableName=self.curio_table,
                IndexName='gsi1pk-gsi1sk-index',
                KeyConditionExpression='gsi1pk = :status AND gsi1sk > :time',
                ExpressionAttributeValues={
                    ':status': {'S': 'status#RUNNING'},
                    ':time': {'S': one_hour_ago.isoformat()}
                }
            )
            
            active_orchestrations = []
            for item in response.get('Items', []):
                orchestration = {
                    'run_id': item.get('sk', {}).get('S', ''),
                    'current_agent': item.get('currentAgent', {}).get('S', ''),
                    'status': item.get('status', {}).get('S', ''),
                    'updated_at': item.get('updatedAt', {}).get('S', ''),
                    'execution_time': item.get('executionTime', {}).get('N'),
                    'retry_count': item.get('retryCount', {}).get('N', '0')
                }
                active_orchestrations.append(orchestration)
            
            return active_orchestrations
            
        except Exception as e:
            print(f"❌ Error getting active orchestrations: {e}")
            return []
    
    def _get_recent_performance_metrics(self, minutes_back: int = 30) -> Dict[str, Any]:
        """Get recent performance metrics from CloudWatch"""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(minutes=minutes_back)
            
            # Get recent orchestration metrics
            orchestration_metrics = self.cloudwatch.get_metric_statistics(
                Namespace='CurioNews/Agents',
                MetricName='OrchestrationTime',
                StartTime=start_time,
                EndTime=end_time,
                Period=300,  # 5-minute periods
                Statistics=['Average', 'Maximum', 'SampleCount']
            )
            
            # Get recent success rates
            success_metrics = self.cloudwatch.get_metric_statistics(
                Namespace='CurioNews/Agents',
                MetricName='OrchestrationSuccessRate',
                StartTime=start_time,
                EndTime=end_time,
                Period=300,
                Statistics=['Average']
            )
            
            return {
                'orchestration_times': [
                    {
                        'timestamp': point['Timestamp'].isoformat(),
                        'average': point['Average'],
                        'maximum': point['Maximum'],
                        'count': point['SampleCount']
                    }
                    for point in orchestration_metrics['Datapoints']
                ],
                'success_rates': [
                    {
                        'timestamp': point['Timestamp'].isoformat(),
                        'success_rate': point['Average']
                    }
                    for point in success_metrics['Datapoints']
                ],
                'time_range': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat(),
                    'minutes_back': minutes_back
                }
            }
            
        except Exception as e:
            print(f"❌ Error getting recent performance metrics: {e}")
            return {}
    
    def _get_current_system_health(self) -> Dict[str, Any]:
        """Get current system health status"""
        try:
            # Get system resource metrics
            system_metrics = self.cloudwatch.get_metric_statistics(
                Namespace='CurioNews/Agents',
                MetricName='SystemMemoryPercent',
                StartTime=datetime.utcnow() - timedelta(minutes=5),
                EndTime=datetime.utcnow(),
                Period=300,
                Statistics=['Average']
            )
            
            cpu_metrics = self.cloudwatch.get_metric_statistics(
                Namespace='CurioNews/Agents',
                MetricName='SystemCPUUsage',
                StartTime=datetime.utcnow() - timedelta(minutes=5),
                EndTime=datetime.utcnow(),
                Period=300,
                Statistics=['Average']
            )
            
            # Calculate health status
            memory_usage = system_metrics['Datapoints'][-1]['Average'] if system_metrics['Datapoints'] else 0
            cpu_usage = cpu_metrics['Datapoints'][-1]['Average'] if cpu_metrics['Datapoints'] else 0
            
            health_status = 'HEALTHY'
            if memory_usage > 80 or cpu_usage > 80:
                health_status = 'CRITICAL'
            elif memory_usage > 60 or cpu_usage > 60:
                health_status = 'WARNING'
            
            return {
                'status': health_status,
                'memory_usage_percent': memory_usage,
                'cpu_usage_percent': cpu_usage,
                'last_updated': datetime.utcnow().isoformat(),
                'thresholds': {
                    'memory_warning': 60,
                    'memory_critical': 80,
                    'cpu_warning': 60,
                    'cpu_critical': 80
                }
            }
            
        except Exception as e:
            print(f"❌ Error getting system health: {e}")
            return {
                'status': 'UNKNOWN',
                'error': str(e),
                'last_updated': datetime.utcnow().isoformat()
            }
    
    def _get_active_alerts(self) -> List[Dict]:
        """Get active CloudWatch alarms"""
        try:
            response = self.cloudwatch.describe_alarms(
                StateValue='ALARM',
                AlarmNamePrefix='CurioNews'
            )
            
            active_alerts = []
            for alarm in response.get('MetricAlarms', []):
                alert = {
                    'alarm_name': alarm['AlarmName'],
                    'description': alarm.get('AlarmDescription', ''),
                    'metric_name': alarm['MetricName'],
                    'state_reason': alarm.get('StateReason', ''),
                    'state_updated': alarm.get('StateUpdatedTimestamp', '').isoformat() if alarm.get('StateUpdatedTimestamp') else '',
                    'threshold': alarm.get('Threshold', 0),
                    'comparison_operator': alarm.get('ComparisonOperator', ''),
                    'severity': 'CRITICAL' if 'Critical' in alarm['AlarmName'] else 'WARNING'
                }
                active_alerts.append(alert)
            
            return active_alerts
            
        except Exception as e:
            print(f"❌ Error getting active alerts: {e}")
            return []
    
    def _get_run_specific_data(self, run_id: str) -> Dict[str, Any]:
        """Get detailed data for a specific orchestration run"""
        try:
            # Get orchestration summary
            orchestration_summary = self.agent_logger.get_orchestration_summary(run_id)
            
            # Get agent execution history
            execution_history = self.agent_logger.get_agent_execution_history(run_id)
            
            return {
                'run_id': run_id,
                'orchestration_summary': orchestration_summary,
                'execution_history': execution_history,
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error getting run-specific data: {e}")
            return {
                'run_id': run_id,
                'error': str(e),
                'last_updated': datetime.utcnow().isoformat()
            }
    
    def _generate_distribution_charts(self, agents: List[str]) -> Dict[str, Any]:
        """Generate distribution chart data"""
        # This would typically query historical data for distribution analysis
        # For now, return placeholder structure
        return {
            'execution_time_distribution': {
                'chart_type': 'histogram',
                'title': 'Execution Time Distribution',
                'data': {}  # Would contain histogram data
            },
            'success_rate_distribution': {
                'chart_type': 'box_plot',
                'title': 'Success Rate Distribution by Agent',
                'data': {}  # Would contain box plot data
            }
        }
    
    def _generate_comparison_charts(self, agents: List[str]) -> Dict[str, Any]:
        """Generate comparison chart data"""
        # This would typically compare agents across different metrics
        # For now, return placeholder structure
        return {
            'agent_comparison': {
                'chart_type': 'multi_bar',
                'title': 'Agent Performance Comparison',
                'metrics': ['execution_time', 'success_rate', 'retry_rate'],
                'data': {}  # Would contain comparison data
            }
        }
    
    def _generate_performance_heatmaps(self, agents: List[str], hours_back: int) -> Dict[str, Any]:
        """Generate performance heatmap data"""
        # This would typically generate time-based heatmaps
        # For now, return placeholder structure
        return {
            'time_performance_heatmap': {
                'chart_type': 'heatmap',
                'title': 'Performance Over Time Heatmap',
                'x_axis': 'time_periods',
                'y_axis': 'agents',
                'data': {}  # Would contain heatmap data
            }
        }