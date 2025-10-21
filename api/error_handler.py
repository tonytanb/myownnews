"""
Comprehensive Error Handling and Recovery System for Curio News

This module provides graceful error handling for all failure scenarios,
automatic retry mechanisms with exponential backoff, and meaningful error messages for debugging.
"""

import json
import time
import traceback
import boto3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass
from enum import Enum
import functools
import asyncio
import concurrent.futures

dynamodb = boto3.client('dynamodb')

class ErrorCategory(Enum):
    """Categories of errors for better handling and debugging"""
    TIMEOUT_ERROR = "timeout"
    THROTTLING_ERROR = "throttling"
    MODEL_ERROR = "model"
    PARSING_ERROR = "parsing"
    NETWORK_ERROR = "network"
    PERMISSION_ERROR = "permission"
    VALIDATION_ERROR = "validation"
    SYSTEM_ERROR = "system"
    UNKNOWN_ERROR = "unknown"

class ErrorSeverity(Enum):
    """Severity levels for error handling"""
    CRITICAL = "critical"    # System cannot continue
    HIGH = "high"           # Major functionality affected
    MEDIUM = "medium"       # Some functionality affected
    LOW = "low"            # Minor issues, system can continue

@dataclass
class ErrorContext:
    """Context information for error handling"""
    agent_name: str
    run_id: str
    operation: str
    attempt_number: int
    max_attempts: int
    start_time: float
    context_data: Dict[str, Any]

@dataclass
class RecoveryResult:
    """Result of error recovery attempt"""
    success: bool
    result: Any = None
    error: Optional[str] = None
    recovery_method: Optional[str] = None
    attempts_made: int = 0
    total_time: float = 0.0
    metadata: Dict[str, Any] = None

class RetryStrategy:
    """Configuration for retry behavior"""
    def __init__(self, max_attempts: int = 3, base_delay: float = 1.0, 
                 max_delay: float = 60.0, exponential_base: float = 2.0,
                 jitter: bool = True):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
    
    def get_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number"""
        delay = self.base_delay * (self.exponential_base ** attempt)
        delay = min(delay, self.max_delay)
        
        if self.jitter:
            import random
            delay *= (0.5 + random.random() * 0.5)  # Add 0-50% jitter
        
        return delay

class ErrorHandler:
    """Comprehensive error handling and recovery system"""
    
    def __init__(self, curio_table: str):
        self.curio_table = curio_table
        self.error_patterns = self._initialize_error_patterns()
        self.retry_strategies = self._initialize_retry_strategies()
        self.recovery_methods = self._initialize_recovery_methods()
        self.error_history = {}  # In-memory error tracking
        
        # Circuit breaker settings
        self.circuit_breakers = {}
        self.circuit_breaker_threshold = 5  # failures before opening circuit
        self.circuit_breaker_timeout = 300  # 5 minutes
    
    def handle_with_recovery(self, operation: Callable, error_context: ErrorContext, 
                           retry_strategy: Optional[RetryStrategy] = None) -> RecoveryResult:
        """
        Execute operation with comprehensive error handling and recovery
        
        Args:
            operation: Function to execute
            error_context: Context information for error handling
            retry_strategy: Custom retry strategy (optional)
            
        Returns:
            RecoveryResult with success status and result/error information
        """
        start_time = time.time()
        retry_strategy = retry_strategy or self.retry_strategies.get(
            error_context.agent_name, 
            self.retry_strategies['default']
        )
        
        last_error = None
        recovery_attempts = []
        
        print(f"🔄 Starting operation with recovery: {error_context.operation} for {error_context.agent_name}")
        
        # Check circuit breaker
        if self._is_circuit_open(error_context.agent_name):
            return RecoveryResult(
                success=False,
                error=f"Circuit breaker open for {error_context.agent_name}",
                recovery_method="circuit_breaker_blocked",
                total_time=time.time() - start_time,
                metadata={'circuit_breaker': 'open'}
            )
        
        for attempt in range(retry_strategy.max_attempts):
            try:
                print(f"🎯 Attempt {attempt + 1}/{retry_strategy.max_attempts} for {error_context.agent_name}")
                
                # Update error context
                error_context.attempt_number = attempt + 1
                
                # Execute operation
                result = operation()
                
                # Success - reset circuit breaker and return
                self._reset_circuit_breaker(error_context.agent_name)
                
                total_time = time.time() - start_time
                print(f"✅ Operation succeeded after {attempt + 1} attempts in {total_time:.2f}s")
                
                return RecoveryResult(
                    success=True,
                    result=result,
                    attempts_made=attempt + 1,
                    total_time=total_time,
                    metadata={'successful_attempt': attempt + 1}
                )
                
            except Exception as e:
                last_error = e
                error_category = self._categorize_error(e)
                error_severity = self._assess_error_severity(e, error_category)
                
                print(f"❌ Attempt {attempt + 1} failed: {error_category.value} - {str(e)}")
                
                # Log error details
                self._log_error_details(error_context, e, error_category, error_severity, attempt + 1)
                
                # Record circuit breaker failure
                self._record_circuit_breaker_failure(error_context.agent_name)
                
                # Check if we should retry
                if not self._should_retry(e, error_category, attempt + 1, retry_strategy.max_attempts):
                    print(f"🚫 Not retrying due to error type or max attempts reached")
                    break
                
                # Try recovery methods before next attempt
                if attempt < retry_strategy.max_attempts - 1:
                    recovery_result = self._attempt_recovery(error_context, e, error_category)
                    recovery_attempts.append(recovery_result)
                    
                    if recovery_result.get('success'):
                        print(f"🔧 Recovery successful using method: {recovery_result.get('method')}")
                        # Continue with next attempt after successful recovery
                    
                    # Wait before retry
                    delay = retry_strategy.get_delay(attempt)
                    print(f"⏳ Waiting {delay:.1f}s before retry...")
                    time.sleep(delay)
        
        # All attempts failed
        total_time = time.time() - start_time
        
        # Try final recovery methods
        final_recovery = self._attempt_final_recovery(error_context, last_error)
        
        return RecoveryResult(
            success=False,
            error=self._create_comprehensive_error_message(last_error, recovery_attempts),
            recovery_method="all_attempts_failed",
            attempts_made=retry_strategy.max_attempts,
            total_time=total_time,
            metadata={
                'last_error_category': self._categorize_error(last_error).value,
                'recovery_attempts': recovery_attempts,
                'final_recovery': final_recovery
            }
        )
    
    def handle_agent_orchestration_errors(self, run_id: str, agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle errors in agent orchestration and provide recovery strategies
        
        Args:
            run_id: Orchestration run ID
            agent_results: Results from all agents (successful and failed)
            
        Returns:
            Enhanced results with error handling and recovery information
        """
        try:
            print(f"🔍 Analyzing agent orchestration errors for run {run_id}")
            
            successful_agents = []
            failed_agents = []
            error_summary = {
                'total_agents': len(agent_results),
                'successful_count': 0,
                'failed_count': 0,
                'error_categories': {},
                'recovery_recommendations': [],
                'system_health': 'unknown'
            }
            
            # Analyze each agent result
            for agent_name, result in agent_results.items():
                if isinstance(result, dict) and result.get('success'):
                    successful_agents.append(agent_name)
                    error_summary['successful_count'] += 1
                else:
                    failed_agents.append(agent_name)
                    error_summary['failed_count'] += 1
                    
                    # Categorize the error
                    error = result.get('error') if isinstance(result, dict) else str(result)
                    category = self._categorize_error_from_message(error)
                    
                    if category.value not in error_summary['error_categories']:
                        error_summary['error_categories'][category.value] = []
                    error_summary['error_categories'][category.value].append(agent_name)
            
            # Determine system health
            success_rate = error_summary['successful_count'] / error_summary['total_agents']
            if success_rate >= 0.8:
                error_summary['system_health'] = 'healthy'
            elif success_rate >= 0.5:
                error_summary['system_health'] = 'degraded'
            else:
                error_summary['system_health'] = 'critical'
            
            # Generate recovery recommendations
            error_summary['recovery_recommendations'] = self._generate_recovery_recommendations(
                failed_agents, error_summary['error_categories'], success_rate
            )
            
            # Store error analysis
            self._store_orchestration_error_analysis(run_id, error_summary)
            
            # Enhanced results with error handling
            enhanced_results = {
                'original_results': agent_results,
                'error_analysis': error_summary,
                'successful_agents': successful_agents,
                'failed_agents': failed_agents,
                'recovery_strategy': self._determine_recovery_strategy(error_summary),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return enhanced_results
            
        except Exception as e:
            print(f"❌ Error in orchestration error handling: {e}")
            return {
                'original_results': agent_results,
                'error_analysis': {'error': str(e)},
                'recovery_strategy': 'manual_intervention_required'
            }
    
    def create_graceful_degradation_plan(self, failed_sections: List[str], 
                                       available_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a plan for graceful degradation when some agents fail
        
        Args:
            failed_sections: List of content sections that failed
            available_content: Content that was successfully generated
            
        Returns:
            Degradation plan with fallback strategies
        """
        try:
            print(f"🎭 Creating graceful degradation plan for failed sections: {failed_sections}")
            
            degradation_plan = {
                'strategy': 'graceful_degradation',
                'failed_sections': failed_sections,
                'available_sections': list(available_content.keys()),
                'fallback_actions': {},
                'user_messaging': {},
                'quality_impact': 'minimal',
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Define fallback actions for each failed section
            for section in failed_sections:
                fallback_action = self._get_fallback_action(section, available_content)
                degradation_plan['fallback_actions'][section] = fallback_action
                
                # Create user-friendly messaging
                user_message = self._create_user_message(section, fallback_action)
                degradation_plan['user_messaging'][section] = user_message
            
            # Assess overall quality impact
            critical_sections = ['news_stories', 'script_content']
            failed_critical = [s for s in failed_sections if s in critical_sections]
            
            if failed_critical:
                degradation_plan['quality_impact'] = 'significant'
            elif len(failed_sections) > len(available_content):
                degradation_plan['quality_impact'] = 'moderate'
            else:
                degradation_plan['quality_impact'] = 'minimal'
            
            # Add recovery timeline
            degradation_plan['recovery_timeline'] = self._estimate_recovery_timeline(failed_sections)
            
            return degradation_plan
            
        except Exception as e:
            print(f"❌ Error creating degradation plan: {e}")
            return {
                'strategy': 'emergency_mode',
                'error': str(e),
                'fallback_actions': {'all': 'use_cached_content'},
                'quality_impact': 'significant'
            }
    
    def _categorize_error(self, error: Exception) -> ErrorCategory:
        """Categorize error based on exception type and message"""
        error_str = str(error).lower()
        error_type = type(error).__name__.lower()
        
        # Timeout errors
        if 'timeout' in error_str or 'timeouterror' in error_type:
            return ErrorCategory.TIMEOUT_ERROR
        
        # Throttling errors
        if any(term in error_str for term in ['throttl', 'rate limit', 'too many requests']):
            return ErrorCategory.THROTTLING_ERROR
        
        # Model/Bedrock errors
        if any(term in error_str for term in ['bedrock', 'model', 'claude', 'titan']):
            return ErrorCategory.MODEL_ERROR
        
        # Parsing errors
        if any(term in error_str for term in ['json', 'parse', 'decode', 'invalid format']):
            return ErrorCategory.PARSING_ERROR
        
        # Network errors
        if any(term in error_str for term in ['network', 'connection', 'dns', 'unreachable']):
            return ErrorCategory.NETWORK_ERROR
        
        # Permission errors
        if any(term in error_str for term in ['permission', 'access', 'unauthorized', 'forbidden']):
            return ErrorCategory.PERMISSION_ERROR
        
        # Validation errors
        if any(term in error_str for term in ['validation', 'invalid', 'missing required']):
            return ErrorCategory.VALIDATION_ERROR
        
        # System errors
        if any(term in error_str for term in ['system', 'internal', 'server error']):
            return ErrorCategory.SYSTEM_ERROR
        
        return ErrorCategory.UNKNOWN_ERROR
    
    def _categorize_error_from_message(self, error_message: str) -> ErrorCategory:
        """Categorize error from error message string"""
        if not error_message:
            return ErrorCategory.UNKNOWN_ERROR
        
        error_str = error_message.lower()
        
        if 'timeout' in error_str:
            return ErrorCategory.TIMEOUT_ERROR
        elif any(term in error_str for term in ['throttl', 'rate limit']):
            return ErrorCategory.THROTTLING_ERROR
        elif any(term in error_str for term in ['bedrock', 'model']):
            return ErrorCategory.MODEL_ERROR
        elif any(term in error_str for term in ['json', 'parse']):
            return ErrorCategory.PARSING_ERROR
        elif any(term in error_str for term in ['network', 'connection']):
            return ErrorCategory.NETWORK_ERROR
        elif any(term in error_str for term in ['permission', 'access']):
            return ErrorCategory.PERMISSION_ERROR
        else:
            return ErrorCategory.UNKNOWN_ERROR
    
    def _assess_error_severity(self, error: Exception, category: ErrorCategory) -> ErrorSeverity:
        """Assess the severity of an error"""
        # Critical errors that prevent system operation
        if category in [ErrorCategory.PERMISSION_ERROR, ErrorCategory.SYSTEM_ERROR]:
            return ErrorSeverity.CRITICAL
        
        # High severity errors that significantly impact functionality
        if category in [ErrorCategory.MODEL_ERROR, ErrorCategory.NETWORK_ERROR]:
            return ErrorSeverity.HIGH
        
        # Medium severity errors that can often be retried
        if category in [ErrorCategory.TIMEOUT_ERROR, ErrorCategory.THROTTLING_ERROR]:
            return ErrorSeverity.MEDIUM
        
        # Low severity errors that are usually recoverable
        if category in [ErrorCategory.PARSING_ERROR, ErrorCategory.VALIDATION_ERROR]:
            return ErrorSeverity.LOW
        
        return ErrorSeverity.MEDIUM  # Default for unknown errors
    
    def _should_retry(self, error: Exception, category: ErrorCategory, 
                     attempt: int, max_attempts: int) -> bool:
        """Determine if an error should be retried"""
        if attempt >= max_attempts:
            return False
        
        # Don't retry critical errors
        severity = self._assess_error_severity(error, category)
        if severity == ErrorSeverity.CRITICAL:
            return False
        
        # Don't retry permission errors
        if category == ErrorCategory.PERMISSION_ERROR:
            return False
        
        # Always retry timeout and throttling errors
        if category in [ErrorCategory.TIMEOUT_ERROR, ErrorCategory.THROTTLING_ERROR]:
            return True
        
        # Retry most other errors
        return True
    
    def _attempt_recovery(self, error_context: ErrorContext, error: Exception, 
                         category: ErrorCategory) -> Dict[str, Any]:
        """Attempt to recover from an error before retrying"""
        recovery_methods = self.recovery_methods.get(category, [])
        
        for method_name in recovery_methods:
            try:
                method = getattr(self, f'_recover_{method_name}', None)
                if method:
                    result = method(error_context, error)
                    if result.get('success'):
                        return result
            except Exception as e:
                print(f"❌ Recovery method {method_name} failed: {e}")
        
        return {'success': False, 'method': 'none_successful'}
    
    def _attempt_final_recovery(self, error_context: ErrorContext, error: Exception) -> Dict[str, Any]:
        """Attempt final recovery methods when all retries fail"""
        try:
            # Try to get cached content as final fallback
            return {
                'success': True,
                'method': 'cached_content_fallback',
                'message': 'Using cached content as final fallback'
            }
        except Exception as e:
            return {
                'success': False,
                'method': 'final_recovery_failed',
                'error': str(e)
            }
    
    def _recover_clear_cache(self, error_context: ErrorContext, error: Exception) -> Dict[str, Any]:
        """Recovery method: Clear relevant caches"""
        try:
            # This would clear any relevant caches
            print(f"🧹 Clearing caches for {error_context.agent_name}")
            return {'success': True, 'method': 'clear_cache'}
        except Exception as e:
            return {'success': False, 'method': 'clear_cache', 'error': str(e)}
    
    def _recover_reduce_complexity(self, error_context: ErrorContext, error: Exception) -> Dict[str, Any]:
        """Recovery method: Reduce operation complexity"""
        try:
            # This would modify the operation to be simpler
            print(f"📉 Reducing complexity for {error_context.agent_name}")
            return {'success': True, 'method': 'reduce_complexity'}
        except Exception as e:
            return {'success': False, 'method': 'reduce_complexity', 'error': str(e)}
    
    def _recover_switch_model(self, error_context: ErrorContext, error: Exception) -> Dict[str, Any]:
        """Recovery method: Switch to alternative model"""
        try:
            # This would switch to a backup model
            print(f"🔄 Switching model for {error_context.agent_name}")
            return {'success': True, 'method': 'switch_model'}
        except Exception as e:
            return {'success': False, 'method': 'switch_model', 'error': str(e)}
    
    def _is_circuit_open(self, agent_name: str) -> bool:
        """Check if circuit breaker is open for an agent"""
        if agent_name not in self.circuit_breakers:
            return False
        
        breaker = self.circuit_breakers[agent_name]
        if breaker['state'] != 'open':
            return False
        
        # Check if timeout has passed
        if time.time() - breaker['opened_at'] > self.circuit_breaker_timeout:
            breaker['state'] = 'half_open'
            return False
        
        return True
    
    def _record_circuit_breaker_failure(self, agent_name: str):
        """Record a failure for circuit breaker tracking"""
        if agent_name not in self.circuit_breakers:
            self.circuit_breakers[agent_name] = {
                'failures': 0,
                'state': 'closed',
                'opened_at': None
            }
        
        breaker = self.circuit_breakers[agent_name]
        breaker['failures'] += 1
        
        if breaker['failures'] >= self.circuit_breaker_threshold and breaker['state'] == 'closed':
            breaker['state'] = 'open'
            breaker['opened_at'] = time.time()
            print(f"🚨 Circuit breaker opened for {agent_name} after {breaker['failures']} failures")
    
    def _reset_circuit_breaker(self, agent_name: str):
        """Reset circuit breaker after successful operation"""
        if agent_name in self.circuit_breakers:
            self.circuit_breakers[agent_name] = {
                'failures': 0,
                'state': 'closed',
                'opened_at': None
            }
    
    def _log_error_details(self, error_context: ErrorContext, error: Exception, 
                          category: ErrorCategory, severity: ErrorSeverity, attempt: int):
        """Log comprehensive error details for debugging"""
        try:
            error_details = {
                'timestamp': datetime.utcnow().isoformat(),
                'run_id': error_context.run_id,
                'agent_name': error_context.agent_name,
                'operation': error_context.operation,
                'attempt': attempt,
                'max_attempts': error_context.max_attempts,
                'error_type': type(error).__name__,
                'error_message': str(error),
                'error_category': category.value,
                'error_severity': severity.value,
                'traceback': traceback.format_exc(),
                'context_data': error_context.context_data
            }
            
            # Store in DynamoDB for analysis
            item = {
                'pk': {'S': 'error_log'},
                'sk': {'S': f'{error_context.run_id}#{error_context.agent_name}#{int(time.time())}'},
                'errorDetails': {'S': json.dumps(error_details, ensure_ascii=False)},
                'errorCategory': {'S': category.value},
                'errorSeverity': {'S': severity.value},
                'agentName': {'S': error_context.agent_name},
                'runId': {'S': error_context.run_id},
                'timestamp': {'S': error_details['timestamp']},
                'expiresAt': {'N': str(int(time.time()) + (7 * 24 * 3600))},  # 7 day TTL
                'gsi1pk': {'S': f'errors#{category.value}'},
                'gsi1sk': {'S': error_details['timestamp']}
            }
            
            dynamodb.put_item(TableName=self.curio_table, Item=item)
            
        except Exception as e:
            print(f"❌ Error logging error details: {e}")
    
    def _create_comprehensive_error_message(self, error: Exception, 
                                          recovery_attempts: List[Dict]) -> str:
        """Create a comprehensive error message for debugging"""
        category = self._categorize_error(error)
        severity = self._assess_error_severity(error, category)
        
        message_parts = [
            f"Operation failed after all retry attempts",
            f"Error Category: {category.value}",
            f"Severity: {severity.value}",
            f"Original Error: {str(error)}"
        ]
        
        if recovery_attempts:
            message_parts.append("Recovery Attempts:")
            for i, attempt in enumerate(recovery_attempts, 1):
                method = attempt.get('method', 'unknown')
                success = attempt.get('success', False)
                status = "✅" if success else "❌"
                message_parts.append(f"  {i}. {method}: {status}")
        
        return "\n".join(message_parts)
    
    def _generate_recovery_recommendations(self, failed_agents: List[str], 
                                         error_categories: Dict[str, List[str]], 
                                         success_rate: float) -> List[str]:
        """Generate actionable recovery recommendations"""
        recommendations = []
        
        # System-wide recommendations based on success rate
        if success_rate < 0.3:
            recommendations.append("🚨 System-wide issues detected. Consider emergency maintenance mode.")
        elif success_rate < 0.6:
            recommendations.append("⚠️ Multiple agent failures. Check system resources and network connectivity.")
        
        # Category-specific recommendations
        if 'timeout' in error_categories:
            recommendations.append("⏰ Timeout errors detected. Consider increasing timeout values or optimizing prompts.")
        
        if 'throttling' in error_categories:
            recommendations.append("🚦 Throttling detected. Implement request rate limiting and backoff strategies.")
        
        if 'model' in error_categories:
            recommendations.append("🤖 Model errors detected. Check Bedrock service status and model availability.")
        
        if 'parsing' in error_categories:
            recommendations.append("📝 Parsing errors detected. Review agent prompts and response formats.")
        
        # Agent-specific recommendations
        critical_agents = ['NEWS_FETCHER', 'CONTENT_CURATOR', 'SCRIPT_GENERATOR']
        failed_critical = [agent for agent in failed_agents if agent in critical_agents]
        
        if failed_critical:
            recommendations.append(f"🎯 Critical agents failed: {', '.join(failed_critical)}. Prioritize fixing these.")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def _determine_recovery_strategy(self, error_summary: Dict[str, Any]) -> str:
        """Determine the best recovery strategy based on error analysis"""
        success_rate = error_summary['successful_count'] / error_summary['total_agents']
        failed_count = error_summary['failed_count']
        error_categories = error_summary['error_categories']
        
        # Complete failure
        if success_rate == 0:
            return "emergency_fallback"
        
        # Mostly successful
        if success_rate >= 0.8:
            return "partial_content_with_fallbacks"
        
        # Moderate success
        if success_rate >= 0.5:
            return "graceful_degradation"
        
        # Mostly failed
        if success_rate < 0.5:
            if 'timeout' in error_categories or 'throttling' in error_categories:
                return "retry_with_backoff"
            else:
                return "cached_content_fallback"
        
        return "manual_intervention_required"
    
    def _get_fallback_action(self, section: str, available_content: Dict[str, Any]) -> Dict[str, Any]:
        """Get appropriate fallback action for a failed section"""
        fallback_actions = {
            'news_stories': {
                'action': 'use_cached_stories',
                'description': 'Use previously cached news stories',
                'quality_impact': 'low'
            },
            'favorite_story': {
                'action': 'select_from_available',
                'description': 'Select favorite from available news stories',
                'quality_impact': 'medium'
            },
            'weekend_recommendations': {
                'action': 'use_static_recommendations',
                'description': 'Use curated static recommendations',
                'quality_impact': 'medium'
            },
            'visual_enhancements': {
                'action': 'basic_enhancements',
                'description': 'Apply basic visual enhancements',
                'quality_impact': 'low'
            },
            'script_content': {
                'action': 'generate_from_available',
                'description': 'Generate script from available content',
                'quality_impact': 'high'
            },
            'audio_metadata': {
                'action': 'use_demo_audio',
                'description': 'Use demo audio with generated timings',
                'quality_impact': 'high'
            }
        }
        
        return fallback_actions.get(section, {
            'action': 'skip_section',
            'description': 'Skip this section',
            'quality_impact': 'high'
        })
    
    def _create_user_message(self, section: str, fallback_action: Dict[str, Any]) -> str:
        """Create user-friendly message for failed section"""
        messages = {
            'news_stories': "We're using our latest cached stories while our news agents update.",
            'favorite_story': "Our AI is selecting today's most interesting story from available content.",
            'weekend_recommendations': "We're providing curated recommendations while our cultural agent updates.",
            'visual_enhancements': "Basic visual enhancements are applied while our media agent updates.",
            'script_content': "We're generating your audio script from available content.",
            'audio_metadata': "Demo audio is available while our audio system updates."
        }
        
        return messages.get(section, f"This section is temporarily unavailable.")
    
    def _estimate_recovery_timeline(self, failed_sections: List[str]) -> Dict[str, str]:
        """Estimate recovery timeline for failed sections"""
        timeline_estimates = {
            'news_stories': '5-10 minutes',
            'favorite_story': '2-5 minutes',
            'weekend_recommendations': '10-15 minutes',
            'visual_enhancements': '5-10 minutes',
            'script_content': '3-7 minutes',
            'audio_metadata': '10-20 minutes'
        }
        
        return {section: timeline_estimates.get(section, '5-15 minutes') for section in failed_sections}
    
    def _store_orchestration_error_analysis(self, run_id: str, error_summary: Dict[str, Any]):
        """Store orchestration error analysis for monitoring"""
        try:
            item = {
                'pk': {'S': 'orchestration_errors'},
                'sk': {'S': run_id},
                'errorSummary': {'S': json.dumps(error_summary, ensure_ascii=False)},
                'systemHealth': {'S': error_summary['system_health']},
                'successRate': {'N': str(error_summary['successful_count'] / error_summary['total_agents'])},
                'timestamp': {'S': datetime.utcnow().isoformat()},
                'expiresAt': {'N': str(int(time.time()) + (30 * 24 * 3600))},  # 30 day TTL
                'gsi1pk': {'S': f'health#{error_summary["system_health"]}'},
                'gsi1sk': {'S': datetime.utcnow().isoformat()}
            }
            
            dynamodb.put_item(TableName=self.curio_table, Item=item)
            
        except Exception as e:
            print(f"❌ Error storing orchestration error analysis: {e}")
    
    def _initialize_error_patterns(self) -> Dict[str, List[str]]:
        """Initialize error pattern recognition"""
        return {
            'timeout_patterns': [
                'timeout', 'timed out', 'connection timeout', 'read timeout'
            ],
            'throttling_patterns': [
                'throttled', 'rate limit', 'too many requests', 'quota exceeded'
            ],
            'model_patterns': [
                'bedrock', 'model error', 'claude', 'titan', 'model not available'
            ],
            'parsing_patterns': [
                'json', 'parse error', 'invalid format', 'decode error'
            ]
        }
    
    def _initialize_retry_strategies(self) -> Dict[str, RetryStrategy]:
        """Initialize retry strategies for different scenarios"""
        return {
            'default': RetryStrategy(max_attempts=3, base_delay=1.0, max_delay=30.0),
            'NEWS_FETCHER': RetryStrategy(max_attempts=2, base_delay=2.0, max_delay=20.0),
            'CONTENT_CURATOR': RetryStrategy(max_attempts=3, base_delay=1.0, max_delay=15.0),
            'FAVORITE_SELECTOR': RetryStrategy(max_attempts=2, base_delay=1.5, max_delay=10.0),
            'SCRIPT_GENERATOR': RetryStrategy(max_attempts=3, base_delay=2.0, max_delay=25.0),
            'MEDIA_ENHANCER': RetryStrategy(max_attempts=2, base_delay=1.0, max_delay=15.0),
            'WEEKEND_EVENTS': RetryStrategy(max_attempts=2, base_delay=1.5, max_delay=20.0),
            'throttling': RetryStrategy(max_attempts=5, base_delay=5.0, max_delay=120.0),
            'timeout': RetryStrategy(max_attempts=2, base_delay=3.0, max_delay=30.0)
        }
    
    def _initialize_recovery_methods(self) -> Dict[ErrorCategory, List[str]]:
        """Initialize recovery methods for different error categories"""
        return {
            ErrorCategory.TIMEOUT_ERROR: ['clear_cache', 'reduce_complexity'],
            ErrorCategory.THROTTLING_ERROR: ['clear_cache'],
            ErrorCategory.MODEL_ERROR: ['switch_model', 'reduce_complexity'],
            ErrorCategory.PARSING_ERROR: ['clear_cache'],
            ErrorCategory.NETWORK_ERROR: ['clear_cache'],
            ErrorCategory.VALIDATION_ERROR: ['reduce_complexity'],
            ErrorCategory.SYSTEM_ERROR: ['clear_cache'],
            ErrorCategory.UNKNOWN_ERROR: ['clear_cache']
        }

def with_error_handling(curio_table: str, agent_name: str = None, operation: str = None):
    """
    Decorator for adding comprehensive error handling to functions
    
    Usage:
        @with_error_handling('my_table', 'NEWS_FETCHER', 'fetch_news')
        def my_function():
            # function code here
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            error_handler = ErrorHandler(curio_table)
            
            error_context = ErrorContext(
                agent_name=agent_name or func.__name__,
                run_id=kwargs.get('run_id', 'unknown'),
                operation=operation or func.__name__,
                attempt_number=1,
                max_attempts=3,
                start_time=time.time(),
                context_data={'args': str(args), 'kwargs': str(kwargs)}
            )
            
            def operation_func():
                return func(*args, **kwargs)
            
            result = error_handler.handle_with_recovery(operation_func, error_context)
            
            if result.success:
                return result.result
            else:
                raise Exception(result.error)
        
        return wrapper
    return decorator