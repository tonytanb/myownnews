"""
Comprehensive Agent Execution Logging System

This module provides detailed logging for agent orchestration with structured logs,
timing information, and debugging capabilities.
"""

import json
import time
import logging
import boto3
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class AgentStatus(Enum):
    NOT_STARTED = "NOT_STARTED"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    RETRYING = "RETRYING"

@dataclass
class AgentExecutionLog:
    """Structured log entry for agent execution"""
    run_id: str
    agent_name: str
    execution_id: str
    status: AgentStatus
    timestamp: str
    execution_time_ms: Optional[float] = None
    retry_count: int = 0
    error_message: Optional[str] = None
    error_category: Optional[str] = None
    input_data: Optional[Dict] = None
    output_data: Optional[Dict] = None
    performance_metrics: Optional[Dict] = None
    context: Optional[Dict] = None

@dataclass
class OrchestrationLog:
    """Structured log entry for orchestration events"""
    run_id: str
    event_type: str
    timestamp: str
    message: str
    level: LogLevel
    agents_status: Optional[Dict] = None
    performance_data: Optional[Dict] = None
    context: Optional[Dict] = None

class AgentLogger:
    """Comprehensive logging system for agent execution"""
    
    def __init__(self, curio_table: str, enable_cloudwatch: bool = True):
        self.curio_table = curio_table
        self.enable_cloudwatch = enable_cloudwatch
        self.dynamodb = boto3.client('dynamodb')
        
        # Initialize loggers
        self.agent_logger = logging.getLogger('agent_execution')
        self.orchestration_logger = logging.getLogger('orchestration')
        self.performance_logger = logging.getLogger('performance')
        
        # CloudWatch logs client
        if enable_cloudwatch:
            try:
                self.cloudwatch_logs = boto3.client('logs')
                self.log_group_name = '/aws/lambda/curio-news-agents'
                self._ensure_log_group_exists()
            except Exception as e:
                print(f"⚠️ CloudWatch logging not available: {e}")
                self.enable_cloudwatch = False
        
        # In-memory log storage for debugging
        self.execution_logs: Dict[str, List[AgentExecutionLog]] = {}
        self.orchestration_logs: Dict[str, List[OrchestrationLog]] = {}
        
    def _ensure_log_group_exists(self):
        """Ensure CloudWatch log group exists"""
        try:
            self.cloudwatch_logs.describe_log_groups(
                logGroupNamePrefix=self.log_group_name
            )
        except self.cloudwatch_logs.exceptions.ResourceNotFoundException:
            try:
                self.cloudwatch_logs.create_log_group(
                    logGroupName=self.log_group_name,
                    tags={'Project': 'CurioNews', 'Component': 'AgentOrchestration'}
                )
            except Exception as e:
                print(f"⚠️ Could not create log group: {e}")
    
    def log_agent_start(self, run_id: str, agent_name: str, input_data: Dict = None, 
                       context: Dict = None) -> str:
        """Log agent execution start"""
        execution_id = f"{run_id}_{agent_name}_{int(time.time() * 1000)}"
        timestamp = datetime.utcnow().isoformat()
        
        log_entry = AgentExecutionLog(
            run_id=run_id,
            agent_name=agent_name,
            execution_id=execution_id,
            status=AgentStatus.STARTING,
            timestamp=timestamp,
            input_data=input_data,
            context=context
        )
        
        # Store in memory
        if run_id not in self.execution_logs:
            self.execution_logs[run_id] = []
        self.execution_logs[run_id].append(log_entry)
        
        # Log to standard logger
        self.agent_logger.info(
            f"Agent {agent_name} starting",
            extra={
                'run_id': run_id,
                'agent_name': agent_name,
                'execution_id': execution_id,
                'input_size': len(json.dumps(input_data)) if input_data else 0
            }
        )
        
        # Store in DynamoDB
        self._store_execution_log(log_entry)
        
        # Send to CloudWatch
        if self.enable_cloudwatch:
            self._send_to_cloudwatch('agent_start', {
                'run_id': run_id,
                'agent_name': agent_name,
                'execution_id': execution_id,
                'timestamp': timestamp
            })
        
        return execution_id
    
    def log_agent_progress(self, execution_id: str, status: AgentStatus, 
                          message: str = None, performance_metrics: Dict = None):
        """Log agent execution progress"""
        timestamp = datetime.utcnow().isoformat()
        
        # Find existing log entry
        log_entry = self._find_log_entry(execution_id)
        if log_entry:
            log_entry.status = status
            log_entry.timestamp = timestamp
            if performance_metrics:
                log_entry.performance_metrics = performance_metrics
        
        self.agent_logger.info(
            f"Agent progress: {status.value}" + (f" - {message}" if message else ""),
            extra={
                'execution_id': execution_id,
                'status': status.value,
                'performance_metrics': performance_metrics
            }
        )
        
        # Update in DynamoDB
        if log_entry:
            self._store_execution_log(log_entry)
    
    def log_agent_completion(self, execution_id: str, success: bool, 
                           output_data: Dict = None, error_message: str = None,
                           error_category: str = None, retry_count: int = 0):
        """Log agent execution completion"""
        timestamp = datetime.utcnow().isoformat()
        
        # Find existing log entry
        log_entry = self._find_log_entry(execution_id)
        if log_entry:
            # Calculate execution time
            start_time = datetime.fromisoformat(log_entry.timestamp.replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            execution_time_ms = (end_time - start_time).total_seconds() * 1000
            
            log_entry.status = AgentStatus.COMPLETED if success else AgentStatus.FAILED
            log_entry.timestamp = timestamp
            log_entry.execution_time_ms = execution_time_ms
            log_entry.output_data = output_data
            log_entry.error_message = error_message
            log_entry.error_category = error_category
            log_entry.retry_count = retry_count
            
            # Log completion
            if success:
                self.agent_logger.info(
                    f"Agent {log_entry.agent_name} completed successfully",
                    extra={
                        'execution_id': execution_id,
                        'execution_time_ms': execution_time_ms,
                        'output_size': len(json.dumps(output_data)) if output_data else 0,
                        'retry_count': retry_count
                    }
                )
            else:
                self.agent_logger.error(
                    f"Agent {log_entry.agent_name} failed: {error_message}",
                    extra={
                        'execution_id': execution_id,
                        'execution_time_ms': execution_time_ms,
                        'error_category': error_category,
                        'retry_count': retry_count
                    }
                )
            
            # Store final log
            self._store_execution_log(log_entry)
            
            # Send to CloudWatch
            if self.enable_cloudwatch:
                self._send_to_cloudwatch('agent_completion', {
                    'execution_id': execution_id,
                    'agent_name': log_entry.agent_name,
                    'success': success,
                    'execution_time_ms': execution_time_ms,
                    'error_category': error_category,
                    'retry_count': retry_count
                })
    
    def log_orchestration_event(self, run_id: str, event_type: str, message: str,
                               level: LogLevel = LogLevel.INFO, agents_status: Dict = None,
                               performance_data: Dict = None, context: Dict = None):
        """Log orchestration events"""
        timestamp = datetime.utcnow().isoformat()
        
        log_entry = OrchestrationLog(
            run_id=run_id,
            event_type=event_type,
            timestamp=timestamp,
            message=message,
            level=level,
            agents_status=agents_status,
            performance_data=performance_data,
            context=context
        )
        
        # Store in memory
        if run_id not in self.orchestration_logs:
            self.orchestration_logs[run_id] = []
        self.orchestration_logs[run_id].append(log_entry)
        
        # Log to appropriate logger
        log_method = getattr(self.orchestration_logger, level.value.lower())
        log_method(
            f"[{event_type}] {message}",
            extra={
                'run_id': run_id,
                'event_type': event_type,
                'agents_status': agents_status,
                'performance_data': performance_data
            }
        )
        
        # Store in DynamoDB
        self._store_orchestration_log(log_entry)
    
    def log_performance_metrics(self, run_id: str, metrics: Dict[str, Any]):
        """Log performance metrics"""
        timestamp = datetime.utcnow().isoformat()
        
        self.performance_logger.info(
            f"Performance metrics for run {run_id}",
            extra={
                'run_id': run_id,
                'timestamp': timestamp,
                **metrics
            }
        )
        
        # Store performance metrics in DynamoDB
        try:
            item = {
                'pk': {'S': f'performance_metrics'},
                'sk': {'S': f"{run_id}_{timestamp}"},
                'runId': {'S': run_id},
                'timestamp': {'S': timestamp},
                'metrics': {'S': json.dumps(metrics, ensure_ascii=False)},
                'expiresAt': {'N': str(int(time.time()) + (7 * 24 * 3600))}  # 7 days TTL
            }
            
            self.dynamodb.put_item(TableName=self.curio_table, Item=item)
            
        except Exception as e:
            print(f"❌ Error storing performance metrics: {e}")
    
    def get_agent_execution_history(self, run_id: str, agent_name: str = None) -> List[Dict]:
        """Get agent execution history for debugging"""
        try:
            # Query from DynamoDB
            if agent_name:
                response = self.dynamodb.query(
                    TableName=self.curio_table,
                    KeyConditionExpression='pk = :pk AND begins_with(sk, :sk)',
                    ExpressionAttributeValues={
                        ':pk': {'S': f'agent_log_{run_id}'},
                        ':sk': {'S': agent_name}
                    }
                )
            else:
                response = self.dynamodb.query(
                    TableName=self.curio_table,
                    KeyConditionExpression='pk = :pk',
                    ExpressionAttributeValues={
                        ':pk': {'S': f'agent_log_{run_id}'}
                    }
                )
            
            logs = []
            for item in response.get('Items', []):
                log_data = json.loads(item.get('logData', {}).get('S', '{}'))
                logs.append(log_data)
            
            return sorted(logs, key=lambda x: x.get('timestamp', ''))
            
        except Exception as e:
            print(f"❌ Error retrieving agent execution history: {e}")
            # Fallback to in-memory logs
            if run_id in self.execution_logs:
                logs = [asdict(log) for log in self.execution_logs[run_id]]
                if agent_name:
                    logs = [log for log in logs if log['agent_name'] == agent_name]
                return logs
            return []
    
    def get_orchestration_summary(self, run_id: str) -> Dict[str, Any]:
        """Get comprehensive orchestration summary"""
        try:
            # Get all agent logs for this run
            agent_logs = self.get_agent_execution_history(run_id)
            
            # Get orchestration logs
            orchestration_logs = self.orchestration_logs.get(run_id, [])
            
            # Calculate summary statistics
            agents = {}
            total_execution_time = 0
            total_retries = 0
            
            for log in agent_logs:
                agent_name = log['agent_name']
                if agent_name not in agents:
                    agents[agent_name] = {
                        'status': log['status'],
                        'execution_time_ms': log.get('execution_time_ms', 0),
                        'retry_count': log.get('retry_count', 0),
                        'error_category': log.get('error_category'),
                        'last_updated': log['timestamp']
                    }
                else:
                    # Update with latest status
                    if log['timestamp'] > agents[agent_name]['last_updated']:
                        agents[agent_name].update({
                            'status': log['status'],
                            'execution_time_ms': log.get('execution_time_ms', 0),
                            'retry_count': log.get('retry_count', 0),
                            'error_category': log.get('error_category'),
                            'last_updated': log['timestamp']
                        })
                
                total_execution_time += log.get('execution_time_ms', 0)
                total_retries += log.get('retry_count', 0)
            
            # Count statuses
            status_counts = {}
            for agent_data in agents.values():
                status = agent_data['status']
                status_counts[status] = status_counts.get(status, 0) + 1
            
            return {
                'run_id': run_id,
                'agents': agents,
                'summary': {
                    'total_agents': len(agents),
                    'completed': status_counts.get('COMPLETED', 0),
                    'failed': status_counts.get('FAILED', 0),
                    'running': status_counts.get('RUNNING', 0),
                    'total_execution_time_ms': total_execution_time,
                    'total_retries': total_retries,
                    'status_distribution': status_counts
                },
                'orchestration_events': len(orchestration_logs),
                'last_updated': max([log['timestamp'] for log in agent_logs]) if agent_logs else None
            }
            
        except Exception as e:
            print(f"❌ Error generating orchestration summary: {e}")
            return {'run_id': run_id, 'error': str(e)}
    
    def _find_log_entry(self, execution_id: str) -> Optional[AgentExecutionLog]:
        """Find log entry by execution ID"""
        for run_logs in self.execution_logs.values():
            for log_entry in run_logs:
                if log_entry.execution_id == execution_id:
                    return log_entry
        return None
    
    def _store_execution_log(self, log_entry: AgentExecutionLog):
        """Store execution log in DynamoDB"""
        try:
            item = {
                'pk': {'S': f'agent_log_{log_entry.run_id}'},
                'sk': {'S': f'{log_entry.agent_name}_{log_entry.execution_id}'},
                'logData': {'S': json.dumps(asdict(log_entry), ensure_ascii=False)},
                'agentName': {'S': log_entry.agent_name},
                'status': {'S': log_entry.status.value},
                'timestamp': {'S': log_entry.timestamp},
                'expiresAt': {'N': str(int(time.time()) + (7 * 24 * 3600))}  # 7 days TTL
            }
            
            if log_entry.execution_time_ms:
                item['executionTimeMs'] = {'N': str(log_entry.execution_time_ms)}
            if log_entry.retry_count:
                item['retryCount'] = {'N': str(log_entry.retry_count)}
            if log_entry.error_category:
                item['errorCategory'] = {'S': log_entry.error_category}
            
            self.dynamodb.put_item(TableName=self.curio_table, Item=item)
            
        except Exception as e:
            print(f"❌ Error storing execution log: {e}")
    
    def _store_orchestration_log(self, log_entry: OrchestrationLog):
        """Store orchestration log in DynamoDB"""
        try:
            item = {
                'pk': {'S': f'orchestration_log_{log_entry.run_id}'},
                'sk': {'S': f'{log_entry.timestamp}_{log_entry.event_type}'},
                'logData': {'S': json.dumps(asdict(log_entry), ensure_ascii=False)},
                'eventType': {'S': log_entry.event_type},
                'level': {'S': log_entry.level.value},
                'timestamp': {'S': log_entry.timestamp},
                'message': {'S': log_entry.message},
                'expiresAt': {'N': str(int(time.time()) + (7 * 24 * 3600))}  # 7 days TTL
            }
            
            self.dynamodb.put_item(TableName=self.curio_table, Item=item)
            
        except Exception as e:
            print(f"❌ Error storing orchestration log: {e}")
    
    def _send_to_cloudwatch(self, event_type: str, data: Dict):
        """Send log event to CloudWatch"""
        if not self.enable_cloudwatch:
            return
            
        try:
            log_stream_name = f"agent-execution-{datetime.utcnow().strftime('%Y-%m-%d')}"
            
            # Ensure log stream exists
            try:
                self.cloudwatch_logs.create_log_stream(
                    logGroupName=self.log_group_name,
                    logStreamName=log_stream_name
                )
            except self.cloudwatch_logs.exceptions.ResourceAlreadyExistsException:
                pass
            
            # Send log event
            self.cloudwatch_logs.put_log_events(
                logGroupName=self.log_group_name,
                logStreamName=log_stream_name,
                logEvents=[{
                    'timestamp': int(time.time() * 1000),
                    'message': json.dumps({
                        'event_type': event_type,
                        **data
                    })
                }]
            )
            
        except Exception as e:
            print(f"⚠️ Error sending to CloudWatch: {e}")

class PerformanceTracker:
    """Track and analyze agent performance metrics"""
    
    def __init__(self, logger: AgentLogger):
        self.logger = logger
        self.metrics = {}
    
    def start_tracking(self, run_id: str):
        """Start performance tracking for a run"""
        self.metrics[run_id] = {
            'start_time': time.time(),
            'agents': {},
            'memory_usage': self._get_memory_usage(),
            'cpu_usage': self._get_cpu_usage()
        }
    
    def track_agent_performance(self, run_id: str, agent_name: str, 
                               execution_time_ms: float, success: bool,
                               input_size: int = 0, output_size: int = 0):
        """Track individual agent performance"""
        if run_id not in self.metrics:
            self.start_tracking(run_id)
        
        self.metrics[run_id]['agents'][agent_name] = {
            'execution_time_ms': execution_time_ms,
            'success': success,
            'input_size_bytes': input_size,
            'output_size_bytes': output_size,
            'throughput_bytes_per_ms': (input_size + output_size) / max(execution_time_ms, 1)
        }
    
    def finish_tracking(self, run_id: str) -> Dict[str, Any]:
        """Finish tracking and generate performance report"""
        if run_id not in self.metrics:
            return {}
        
        metrics = self.metrics[run_id]
        total_time = time.time() - metrics['start_time']
        
        # Calculate aggregate metrics
        agent_times = [agent['execution_time_ms'] for agent in metrics['agents'].values()]
        successful_agents = sum(1 for agent in metrics['agents'].values() if agent['success'])
        
        performance_report = {
            'run_id': run_id,
            'total_orchestration_time_ms': total_time * 1000,
            'total_agent_execution_time_ms': sum(agent_times),
            'parallel_efficiency': (sum(agent_times) / (total_time * 1000)) if total_time > 0 else 0,
            'success_rate': successful_agents / len(metrics['agents']) if metrics['agents'] else 0,
            'average_agent_time_ms': sum(agent_times) / len(agent_times) if agent_times else 0,
            'memory_usage': {
                'start': metrics['memory_usage'],
                'end': self._get_memory_usage()
            },
            'cpu_usage': {
                'start': metrics['cpu_usage'],
                'end': self._get_cpu_usage()
            },
            'agents': metrics['agents']
        }
        
        # Log performance metrics
        self.logger.log_performance_metrics(run_id, performance_report)
        
        # Clean up
        del self.metrics[run_id]
        
        return performance_report
    
    def _get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            return {
                'rss_mb': memory_info.rss / 1024 / 1024,
                'vms_mb': memory_info.vms / 1024 / 1024
            }
        except ImportError:
            return {'rss_mb': 0, 'vms_mb': 0}
    
    def _get_cpu_usage(self) -> float:
        """Get current CPU usage percentage"""
        try:
            import psutil
            return psutil.cpu_percent(interval=0.1)
        except ImportError:
            return 0.0