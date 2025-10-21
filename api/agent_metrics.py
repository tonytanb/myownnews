"""
Agent Performance Monitoring with CloudWatch Metrics

This module provides comprehensive performance monitoring for agent execution
with CloudWatch metrics, alerting, and resource usage tracking.
"""

import boto3
import time
import json
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class MetricType(Enum):
    COUNTER = "Count"
    GAUGE = "None"
    TIMER = "Seconds"
    BYTES = "Bytes"
    PERCENT = "Percent"

@dataclass
class AgentMetric:
    """Individual agent performance metric"""
    metric_name: str
    value: float
    unit: str
    dimensions: Dict[str, str]
    timestamp: datetime

class AgentPerformanceMonitor:
    """Comprehensive agent performance monitoring with CloudWatch integration"""
    
    def __init__(self, namespace: str = "CurioNews/Agents", enable_detailed_monitoring: bool = True):
        self.namespace = namespace
        self.enable_detailed_monitoring = enable_detailed_monitoring
        
        # Initialize AWS clients
        try:
            self.cloudwatch = boto3.client('cloudwatch')
            self.logs = boto3.client('logs')
            self.cloudwatch_available = True
        except Exception as e:
            print(f"⚠️ CloudWatch not available: {e}")
            self.cloudwatch_available = False
        
        # Metric storage for batch sending
        self.pending_metrics: List[AgentMetric] = []
        self.batch_size = 20  # CloudWatch limit
        
        # Performance baselines
        self.performance_baselines = {
            'NEWS_FETCHER': {'expected_time_ms': 15000, 'success_rate_threshold': 0.95},
            'CONTENT_CURATOR': {'expected_time_ms': 12000, 'success_rate_threshold': 0.95},
            'FAVORITE_SELECTOR': {'expected_time_ms': 10000, 'success_rate_threshold': 0.90},
            'SCRIPT_GENERATOR': {'expected_time_ms': 20000, 'success_rate_threshold': 0.95},
            'MEDIA_ENHANCER': {'expected_time_ms': 8000, 'success_rate_threshold': 0.85},
            'WEEKEND_EVENTS': {'expected_time_ms': 10000, 'success_rate_threshold': 0.90}
        }
        
        # Alert thresholds
        self.alert_thresholds = {
            'agent_failure_rate': 0.2,  # 20% failure rate
            'orchestration_time_ms': 300000,  # 5 minutes
            'memory_usage_mb': 1000,  # 1GB
            'cpu_usage_percent': 80,  # 80%
            'timeout_rate': 0.1  # 10% timeout rate
        }
    
    def record_agent_execution(self, run_id: str, agent_name: str, 
                              execution_time_ms: float, success: bool,
                              retry_count: int = 0, error_category: str = None,
                              input_size_bytes: int = 0, output_size_bytes: int = 0):
        """Record comprehensive agent execution metrics"""
        timestamp = datetime.utcnow()
        
        # Base dimensions for all metrics
        base_dimensions = {
            'AgentName': agent_name,
            'RunId': run_id,
            'Environment': 'production'  # Could be configurable
        }
        
        # Core execution metrics
        metrics_to_record = [
            AgentMetric(
                metric_name='AgentExecutionTime',
                value=execution_time_ms,
                unit=MetricType.TIMER.value,
                dimensions=base_dimensions,
                timestamp=timestamp
            ),
            AgentMetric(
                metric_name='AgentExecutionSuccess',
                value=1.0 if success else 0.0,
                unit=MetricType.COUNTER.value,
                dimensions=base_dimensions,
                timestamp=timestamp
            ),
            AgentMetric(
                metric_name='AgentRetryCount',
                value=float(retry_count),
                unit=MetricType.COUNTER.value,
                dimensions=base_dimensions,
                timestamp=timestamp
            )
        ]
        
        # Add error category if failed
        if not success and error_category:
            error_dimensions = {**base_dimensions, 'ErrorCategory': error_category}
            metrics_to_record.append(
                AgentMetric(
                    metric_name='AgentExecutionError',
                    value=1.0,
                    unit=MetricType.COUNTER.value,
                    dimensions=error_dimensions,
                    timestamp=timestamp
                )
            )
        
        # Add data size metrics if available
        if input_size_bytes > 0:
            metrics_to_record.append(
                AgentMetric(
                    metric_name='AgentInputSize',
                    value=float(input_size_bytes),
                    unit=MetricType.BYTES.value,
                    dimensions=base_dimensions,
                    timestamp=timestamp
                )
            )
        
        if output_size_bytes > 0:
            metrics_to_record.append(
                AgentMetric(
                    metric_name='AgentOutputSize',
                    value=float(output_size_bytes),
                    unit=MetricType.BYTES.value,
                    dimensions=base_dimensions,
                    timestamp=timestamp
                )
            )
        
        # Calculate throughput
        if execution_time_ms > 0:
            throughput = (input_size_bytes + output_size_bytes) / (execution_time_ms / 1000)
            metrics_to_record.append(
                AgentMetric(
                    metric_name='AgentThroughput',
                    value=throughput,
                    unit='Bytes/Second',
                    dimensions=base_dimensions,
                    timestamp=timestamp
                )
            )
        
        # Performance comparison against baseline
        baseline = self.performance_baselines.get(agent_name, {})
        expected_time = baseline.get('expected_time_ms', execution_time_ms)
        if expected_time > 0:
            performance_ratio = execution_time_ms / expected_time
            metrics_to_record.append(
                AgentMetric(
                    metric_name='AgentPerformanceRatio',
                    value=performance_ratio,
                    unit=MetricType.GAUGE.value,
                    dimensions=base_dimensions,
                    timestamp=timestamp
                )
            )
        
        # Add to pending metrics
        self.pending_metrics.extend(metrics_to_record)
        
        # Send metrics if batch is full
        if len(self.pending_metrics) >= self.batch_size:
            self.flush_metrics()
    
    def record_orchestration_metrics(self, run_id: str, total_time_ms: float,
                                   successful_agents: int, failed_agents: int,
                                   total_agents: int, parallel_efficiency: float = 0.0):
        """Record orchestration-level performance metrics"""
        timestamp = datetime.utcnow()
        
        base_dimensions = {
            'RunId': run_id,
            'Environment': 'production'
        }
        
        orchestration_metrics = [
            AgentMetric(
                metric_name='OrchestrationTime',
                value=total_time_ms,
                unit=MetricType.TIMER.value,
                dimensions=base_dimensions,
                timestamp=timestamp
            ),
            AgentMetric(
                metric_name='OrchestrationSuccessRate',
                value=successful_agents / total_agents if total_agents > 0 else 0.0,
                unit=MetricType.PERCENT.value,
                dimensions=base_dimensions,
                timestamp=timestamp
            ),
            AgentMetric(
                metric_name='OrchestrationFailureRate',
                value=failed_agents / total_agents if total_agents > 0 else 0.0,
                unit=MetricType.PERCENT.value,
                dimensions=base_dimensions,
                timestamp=timestamp
            ),
            AgentMetric(
                metric_name='ParallelEfficiency',
                value=parallel_efficiency,
                unit=MetricType.PERCENT.value,
                dimensions=base_dimensions,
                timestamp=timestamp
            )
        ]
        
        self.pending_metrics.extend(orchestration_metrics)
        
        # Check for alert conditions
        self._check_orchestration_alerts(run_id, total_time_ms, failed_agents / total_agents if total_agents > 0 else 0)
    
    def record_system_metrics(self, run_id: str):
        """Record system resource usage metrics"""
        try:
            # Get system metrics
            memory_info = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=1)
            disk_usage = psutil.disk_usage('/')
            
            timestamp = datetime.utcnow()
            base_dimensions = {
                'RunId': run_id,
                'Environment': 'production'
            }
            
            system_metrics = [
                AgentMetric(
                    metric_name='SystemMemoryUsage',
                    value=memory_info.used / 1024 / 1024,  # MB
                    unit=MetricType.BYTES.value,
                    dimensions=base_dimensions,
                    timestamp=timestamp
                ),
                AgentMetric(
                    metric_name='SystemMemoryPercent',
                    value=memory_info.percent,
                    unit=MetricType.PERCENT.value,
                    dimensions=base_dimensions,
                    timestamp=timestamp
                ),
                AgentMetric(
                    metric_name='SystemCPUUsage',
                    value=cpu_percent,
                    unit=MetricType.PERCENT.value,
                    dimensions=base_dimensions,
                    timestamp=timestamp
                ),
                AgentMetric(
                    metric_name='SystemDiskUsage',
                    value=disk_usage.percent,
                    unit=MetricType.PERCENT.value,
                    dimensions=base_dimensions,
                    timestamp=timestamp
                )
            ]
            
            self.pending_metrics.extend(system_metrics)
            
            # Check for system resource alerts
            self._check_system_alerts(run_id, memory_info.used / 1024 / 1024, cpu_percent)
            
        except Exception as e:
            print(f"⚠️ Could not collect system metrics: {e}")
    
    def flush_metrics(self):
        """Send all pending metrics to CloudWatch"""
        if not self.cloudwatch_available or not self.pending_metrics:
            return
        
        try:
            # Convert metrics to CloudWatch format
            metric_data = []
            for metric in self.pending_metrics:
                metric_data.append({
                    'MetricName': metric.metric_name,
                    'Value': metric.value,
                    'Unit': metric.unit,
                    'Timestamp': metric.timestamp,
                    'Dimensions': [
                        {'Name': k, 'Value': v} for k, v in metric.dimensions.items()
                    ]
                })
            
            # Send metrics in batches
            for i in range(0, len(metric_data), self.batch_size):
                batch = metric_data[i:i + self.batch_size]
                
                self.cloudwatch.put_metric_data(
                    Namespace=self.namespace,
                    MetricData=batch
                )
            
            print(f"📊 Sent {len(self.pending_metrics)} metrics to CloudWatch")
            self.pending_metrics.clear()
            
        except Exception as e:
            print(f"❌ Error sending metrics to CloudWatch: {e}")
            # Keep metrics for retry
    
    def get_agent_performance_summary(self, agent_name: str, 
                                    hours_back: int = 24) -> Dict[str, Any]:
        """Get performance summary for a specific agent"""
        if not self.cloudwatch_available:
            return {'error': 'CloudWatch not available'}
        
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=hours_back)
            
            # Get execution time statistics
            execution_time_stats = self.cloudwatch.get_metric_statistics(
                Namespace=self.namespace,
                MetricName='AgentExecutionTime',
                Dimensions=[{'Name': 'AgentName', 'Value': agent_name}],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,  # 1 hour periods
                Statistics=['Average', 'Maximum', 'Minimum', 'SampleCount']
            )
            
            # Get success rate
            success_stats = self.cloudwatch.get_metric_statistics(
                Namespace=self.namespace,
                MetricName='AgentExecutionSuccess',
                Dimensions=[{'Name': 'AgentName', 'Value': agent_name}],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=['Average', 'Sum']
            )
            
            # Get error statistics
            error_stats = self.cloudwatch.get_metric_statistics(
                Namespace=self.namespace,
                MetricName='AgentExecutionError',
                Dimensions=[{'Name': 'AgentName', 'Value': agent_name}],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=['Sum']
            )
            
            # Calculate summary
            total_executions = sum(point['SampleCount'] for point in execution_time_stats['Datapoints'])
            total_successes = sum(point['Sum'] for point in success_stats['Datapoints'])
            total_errors = sum(point['Sum'] for point in error_stats['Datapoints'])
            
            avg_execution_time = sum(point['Average'] for point in execution_time_stats['Datapoints']) / len(execution_time_stats['Datapoints']) if execution_time_stats['Datapoints'] else 0
            
            success_rate = total_successes / total_executions if total_executions > 0 else 0
            
            # Compare against baseline
            baseline = self.performance_baselines.get(agent_name, {})
            performance_assessment = self._assess_agent_performance(
                agent_name, avg_execution_time, success_rate, baseline
            )
            
            return {
                'agent_name': agent_name,
                'time_period_hours': hours_back,
                'total_executions': total_executions,
                'success_rate': success_rate,
                'average_execution_time_ms': avg_execution_time,
                'max_execution_time_ms': max(point['Maximum'] for point in execution_time_stats['Datapoints']) if execution_time_stats['Datapoints'] else 0,
                'min_execution_time_ms': min(point['Minimum'] for point in execution_time_stats['Datapoints']) if execution_time_stats['Datapoints'] else 0,
                'total_errors': total_errors,
                'baseline_comparison': baseline,
                'performance_assessment': performance_assessment,
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {'error': f'Could not retrieve performance summary: {e}'}
    
    def create_performance_dashboard(self) -> Dict[str, Any]:
        """Create a comprehensive performance dashboard"""
        dashboard_config = {
            "widgets": [
                {
                    "type": "metric",
                    "properties": {
                        "metrics": [
                            [self.namespace, "AgentExecutionTime", "AgentName", agent]
                            for agent in self.performance_baselines.keys()
                        ],
                        "period": 300,
                        "stat": "Average",
                        "region": "us-west-2",
                        "title": "Agent Execution Times"
                    }
                },
                {
                    "type": "metric",
                    "properties": {
                        "metrics": [
                            [self.namespace, "AgentExecutionSuccess", "AgentName", agent]
                            for agent in self.performance_baselines.keys()
                        ],
                        "period": 300,
                        "stat": "Average",
                        "region": "us-west-2",
                        "title": "Agent Success Rates"
                    }
                },
                {
                    "type": "metric",
                    "properties": {
                        "metrics": [
                            [self.namespace, "OrchestrationTime"],
                            [self.namespace, "ParallelEfficiency"]
                        ],
                        "period": 300,
                        "stat": "Average",
                        "region": "us-west-2",
                        "title": "Orchestration Performance"
                    }
                },
                {
                    "type": "metric",
                    "properties": {
                        "metrics": [
                            [self.namespace, "SystemMemoryPercent"],
                            [self.namespace, "SystemCPUUsage"]
                        ],
                        "period": 300,
                        "stat": "Average",
                        "region": "us-west-2",
                        "title": "System Resources"
                    }
                }
            ]
        }
        
        return dashboard_config
    
    def setup_cloudwatch_alarms(self):
        """Set up CloudWatch alarms for critical metrics"""
        if not self.cloudwatch_available:
            return
        
        alarms_to_create = [
            {
                'AlarmName': 'CurioNews-HighAgentFailureRate',
                'ComparisonOperator': 'GreaterThanThreshold',
                'EvaluationPeriods': 2,
                'MetricName': 'OrchestrationFailureRate',
                'Namespace': self.namespace,
                'Period': 300,
                'Statistic': 'Average',
                'Threshold': self.alert_thresholds['agent_failure_rate'],
                'ActionsEnabled': True,
                'AlarmDescription': 'Alert when agent failure rate is too high',
                'Unit': 'Percent'
            },
            {
                'AlarmName': 'CurioNews-LongOrchestrationTime',
                'ComparisonOperator': 'GreaterThanThreshold',
                'EvaluationPeriods': 1,
                'MetricName': 'OrchestrationTime',
                'Namespace': self.namespace,
                'Period': 300,
                'Statistic': 'Average',
                'Threshold': self.alert_thresholds['orchestration_time_ms'],
                'ActionsEnabled': True,
                'AlarmDescription': 'Alert when orchestration takes too long',
                'Unit': 'Seconds'
            },
            {
                'AlarmName': 'CurioNews-HighMemoryUsage',
                'ComparisonOperator': 'GreaterThanThreshold',
                'EvaluationPeriods': 2,
                'MetricName': 'SystemMemoryUsage',
                'Namespace': self.namespace,
                'Period': 300,
                'Statistic': 'Average',
                'Threshold': self.alert_thresholds['memory_usage_mb'],
                'ActionsEnabled': True,
                'AlarmDescription': 'Alert when memory usage is too high',
                'Unit': 'Bytes'
            }
        ]
        
        for alarm_config in alarms_to_create:
            try:
                self.cloudwatch.put_metric_alarm(**alarm_config)
                print(f"✅ Created alarm: {alarm_config['AlarmName']}")
            except Exception as e:
                print(f"❌ Error creating alarm {alarm_config['AlarmName']}: {e}")
    
    def _check_orchestration_alerts(self, run_id: str, total_time_ms: float, failure_rate: float):
        """Check for orchestration-level alert conditions"""
        alerts = []
        
        if total_time_ms > self.alert_thresholds['orchestration_time_ms']:
            alerts.append({
                'type': 'ORCHESTRATION_SLOW',
                'message': f'Orchestration took {total_time_ms/1000:.1f}s (threshold: {self.alert_thresholds["orchestration_time_ms"]/1000:.1f}s)',
                'severity': 'WARNING',
                'run_id': run_id
            })
        
        if failure_rate > self.alert_thresholds['agent_failure_rate']:
            alerts.append({
                'type': 'HIGH_FAILURE_RATE',
                'message': f'Agent failure rate {failure_rate:.1%} exceeds threshold {self.alert_thresholds["agent_failure_rate"]:.1%}',
                'severity': 'CRITICAL',
                'run_id': run_id
            })
        
        for alert in alerts:
            print(f"🚨 ALERT [{alert['severity']}]: {alert['message']}")
    
    def _check_system_alerts(self, run_id: str, memory_mb: float, cpu_percent: float):
        """Check for system resource alert conditions"""
        alerts = []
        
        if memory_mb > self.alert_thresholds['memory_usage_mb']:
            alerts.append({
                'type': 'HIGH_MEMORY_USAGE',
                'message': f'Memory usage {memory_mb:.1f}MB exceeds threshold {self.alert_thresholds["memory_usage_mb"]}MB',
                'severity': 'WARNING',
                'run_id': run_id
            })
        
        if cpu_percent > self.alert_thresholds['cpu_usage_percent']:
            alerts.append({
                'type': 'HIGH_CPU_USAGE',
                'message': f'CPU usage {cpu_percent:.1f}% exceeds threshold {self.alert_thresholds["cpu_usage_percent"]}%',
                'severity': 'WARNING',
                'run_id': run_id
            })
        
        for alert in alerts:
            print(f"🚨 ALERT [{alert['severity']}]: {alert['message']}")
    
    def _assess_agent_performance(self, agent_name: str, avg_time_ms: float, 
                                success_rate: float, baseline: Dict) -> Dict[str, Any]:
        """Assess agent performance against baseline"""
        assessment = {
            'overall_status': 'GOOD',
            'issues': [],
            'recommendations': []
        }
        
        # Check execution time
        expected_time = baseline.get('expected_time_ms', avg_time_ms)
        if avg_time_ms > expected_time * 1.5:  # 50% slower than expected
            assessment['overall_status'] = 'POOR'
            assessment['issues'].append(f'Execution time {avg_time_ms:.0f}ms is {((avg_time_ms/expected_time-1)*100):.0f}% slower than expected')
            assessment['recommendations'].append('Consider optimizing prompts or increasing timeout')
        elif avg_time_ms > expected_time * 1.2:  # 20% slower than expected
            assessment['overall_status'] = 'FAIR'
            assessment['issues'].append(f'Execution time slightly above expected')
        
        # Check success rate
        expected_success_rate = baseline.get('success_rate_threshold', 0.95)
        if success_rate < expected_success_rate:
            if success_rate < expected_success_rate * 0.8:  # 20% below threshold
                assessment['overall_status'] = 'POOR'
            elif assessment['overall_status'] == 'GOOD':
                assessment['overall_status'] = 'FAIR'
            
            assessment['issues'].append(f'Success rate {success_rate:.1%} below threshold {expected_success_rate:.1%}')
            assessment['recommendations'].append('Review error patterns and improve error handling')
        
        return assessment