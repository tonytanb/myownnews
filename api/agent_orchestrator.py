import json
import boto3
import time
import requests
import feedparser
import os
import asyncio
import concurrent.futures
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
from audio_generator import AudioGenerator
from content_validator import ContentValidator, ValidationResult
from fallback_manager import FallbackManager
from error_handler import ErrorHandler, ErrorContext, RecoveryResult
from agent_logger import AgentLogger, PerformanceTracker, LogLevel, AgentStatus
from agent_metrics import AgentPerformanceMonitor

bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')
dynamodb = boto3.client('dynamodb')

# NewsAPI configuration
NEWS_API_KEY = os.getenv('NEWS_API_KEY', '56e5f744fdb04e1e8e45a450851e442d')
NEWS_API_BASE_URL = 'https://newsapi.org/v2'

class AgentExecutionResult:
    """Result of agent execution with comprehensive status tracking"""
    def __init__(self, agent_name: str, success: bool, content: str = None, 
                 error: str = None, execution_time: float = 0, retry_count: int = 0):
        self.agent_name = agent_name
        self.success = success
        self.content = content
        self.error = error
        self.execution_time = execution_time
        self.retry_count = retry_count
        self.timestamp = datetime.utcnow().isoformat()

class AgentOrchestrator:
    def __init__(self, curio_table: str, bucket: str = None):
        self.curio_table = curio_table
        self.bucket = bucket or os.getenv('BUCKET')
        self.audio_generator = AudioGenerator(self.bucket) if self.bucket else None
        self.agents = [
            "NEWS_FETCHER",
            "CONTENT_CURATOR", 
            "FAVORITE_SELECTOR",
            "SCRIPT_GENERATOR",
            "MEDIA_ENHANCER",
            "WEEKEND_EVENTS"
        ]
        # Initialize trace storage for comprehensive logging
        self.trace_data = {}
        
        # Enhanced orchestration settings
        self.agent_timeout = 60  # 60 seconds per agent
        self.max_retries = 3
        self.parallel_execution_enabled = True
        
        # Agent execution tracking
        self.agent_status = {}
        self.execution_lock = threading.Lock()
        
        # Agent execution monitoring
        self.execution_monitors = {}
        self.monitor_lock = threading.Lock()
        
        # Initialize new systems
        self.content_validator = ContentValidator()
        self.fallback_manager = FallbackManager(curio_table)
        self.error_handler = ErrorHandler(curio_table)
        
        # Initialize comprehensive logging system
        self.agent_logger = AgentLogger(curio_table, enable_cloudwatch=True)
        self.performance_tracker = PerformanceTracker(self.agent_logger)
        
        # Initialize performance monitoring
        self.performance_monitor = AgentPerformanceMonitor(
            namespace="CurioNews/Agents",
            enable_detailed_monitoring=True
        )
    
    def update_agent_status(self, run_id: str, agent: str, status: str, data: Dict = None, 
                           execution_time: float = None, retry_count: int = None, error: str = None):
        """Update the current agent status in DynamoDB with enhanced tracking"""
        try:
            # Validate inputs
            if not run_id or not agent or not status:
                print(f"❌ Invalid parameters for agent status update: run_id={run_id}, agent={agent}, status={status}")
                return False
            
            # Update in-memory tracking
            with self.execution_lock:
                if run_id not in self.agent_status:
                    self.agent_status[run_id] = {}
                
                self.agent_status[run_id][agent] = {
                    'status': status,
                    'updated_at': datetime.utcnow().isoformat(),
                    'execution_time': execution_time,
                    'retry_count': retry_count or 0,
                    'error': error
                }
            
            item = {
                'pk': {'S': f'generation'},
                'sk': {'S': run_id},
                'currentAgent': {'S': agent},
                'status': {'S': status},
                'updatedAt': {'S': datetime.utcnow().isoformat()},
                'expiresAt': {'N': str(int(time.time()) + 3600)},  # 1 hour TTL
                'gsi1pk': {'S': f'status#{status}'},
                'gsi1sk': {'S': datetime.utcnow().isoformat()}
            }
            
            # Add enhanced tracking data
            if execution_time is not None:
                item['executionTime'] = {'N': str(execution_time)}
            if retry_count is not None:
                item['retryCount'] = {'N': str(retry_count)}
            if error:
                item['error'] = {'S': error}
            
            if data:
                try:
                    item['data'] = {'S': json.dumps(data, ensure_ascii=False)}
                except (TypeError, ValueError) as e:
                    print(f"❌ Error serializing agent data: {e}")
                    item['data'] = {'S': json.dumps({'error': 'Data serialization failed'})}
            
            dynamodb.put_item(TableName=self.curio_table, Item=item)
            print(f"✅ Agent status updated: {agent} - {status} (execution_time: {execution_time}s, retries: {retry_count})")
            return True
            
        except Exception as e:
            print(f"❌ Error updating agent status: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def execute_agent_with_retry(self, agent_name: str, prompt: str, context: Dict = None, 
                                run_id: str = None, max_retries: int = None) -> AgentExecutionResult:
        """Execute agent with timeout handling and retry logic with comprehensive logging"""
        max_retries = max_retries or self.max_retries
        start_time = time.time()
        
        # Start comprehensive logging
        execution_id = self.agent_logger.log_agent_start(
            run_id=run_id or 'unknown',
            agent_name=agent_name,
            input_data={
                'prompt_length': len(prompt) if prompt else 0,
                'context_keys': list(context.keys()) if context else [],
                'max_retries': max_retries
            },
            context={'timeout': self.agent_timeout}
        )
        
        for attempt in range(max_retries + 1):
            try:
                print(f"🤖 Executing {agent_name} (attempt {attempt + 1}/{max_retries + 1})")
                
                # Log retry attempt
                if attempt > 0:
                    self.agent_logger.log_agent_progress(
                        execution_id, 
                        AgentStatus.RETRYING,
                        f"Retry attempt {attempt + 1}"
                    )
                else:
                    self.agent_logger.log_agent_progress(
                        execution_id, 
                        AgentStatus.RUNNING,
                        "Starting execution"
                    )
                
                if run_id:
                    self.update_agent_status(run_id, agent_name, "RUNNING", 
                                           retry_count=attempt)
                
                # Execute with timeout
                result = self._execute_agent_with_timeout(agent_name, prompt, context)
                execution_time = time.time() - start_time
                
                if result['success']:
                    if run_id:
                        self.update_agent_status(run_id, agent_name, "COMPLETED", 
                                               execution_time=execution_time, 
                                               retry_count=attempt)
                    
                    # Log successful completion
                    self.agent_logger.log_agent_completion(
                        execution_id=execution_id,
                        success=True,
                        output_data={
                            'content_length': len(result.get('content', '')) if result.get('content') else 0,
                            'result_keys': list(result.keys())
                        },
                        retry_count=attempt
                    )
                    
                    # Track performance
                    input_size = len(json.dumps({'prompt': prompt, 'context': context}))
                    output_size = len(json.dumps(result))
                    self.performance_tracker.track_agent_performance(
                        run_id or 'unknown', agent_name, execution_time * 1000, 
                        True, input_size, output_size
                    )
                    
                    # Record CloudWatch metrics
                    self.performance_monitor.record_agent_execution(
                        run_id=run_id or 'unknown',
                        agent_name=agent_name,
                        execution_time_ms=execution_time * 1000,
                        success=True,
                        retry_count=attempt,
                        input_size_bytes=input_size,
                        output_size_bytes=output_size
                    )
                    
                    return AgentExecutionResult(
                        agent_name=agent_name,
                        success=True,
                        content=result['content'],
                        execution_time=execution_time,
                        retry_count=attempt
                    )
                else:
                    error_msg = result.get('error', 'Unknown error')
                    error_category = self._categorize_agent_error(error_msg)
                    print(f"❌ {agent_name} attempt {attempt + 1} failed: {error_msg}")
                    
                    if attempt < max_retries:
                        # Exponential backoff
                        wait_time = min(2 ** attempt, 10)  # Max 10 seconds
                        print(f"⏳ Waiting {wait_time}s before retry...")
                        
                        # Log retry delay
                        self.agent_logger.log_agent_progress(
                            execution_id,
                            AgentStatus.RETRYING,
                            f"Waiting {wait_time}s before retry. Error: {error_msg}",
                            performance_metrics={'wait_time_s': wait_time}
                        )
                        
                        time.sleep(wait_time)
                        continue
                    else:
                        # Final failure
                        execution_time = time.time() - start_time
                        if run_id:
                            self.update_agent_status(run_id, agent_name, "FAILED", 
                                                   execution_time=execution_time,
                                                   retry_count=attempt,
                                                   error=error_msg)
                        
                        # Log final failure
                        self.agent_logger.log_agent_completion(
                            execution_id=execution_id,
                            success=False,
                            error_message=error_msg,
                            error_category=error_category,
                            retry_count=attempt
                        )
                        
                        # Track failed performance
                        input_size = len(json.dumps({'prompt': prompt, 'context': context}))
                        self.performance_tracker.track_agent_performance(
                            run_id or 'unknown', agent_name, execution_time * 1000, 
                            False, input_size, 0
                        )
                        
                        # Record failed execution metrics
                        self.performance_monitor.record_agent_execution(
                            run_id=run_id or 'unknown',
                            agent_name=agent_name,
                            execution_time_ms=execution_time * 1000,
                            success=False,
                            retry_count=attempt,
                            error_category=error_category,
                            input_size_bytes=input_size,
                            output_size_bytes=0
                        )
                        
                        return AgentExecutionResult(
                            agent_name=agent_name,
                            success=False,
                            error=error_msg,
                            execution_time=execution_time,
                            retry_count=attempt
                        )
                        
            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                error_category = "EXECUTION_EXCEPTION"
                print(f"❌ {agent_name} attempt {attempt + 1} exception: {error_msg}")
                
                # Log exception
                self.agent_logger.log_agent_progress(
                    execution_id,
                    AgentStatus.FAILED,
                    f"Exception on attempt {attempt + 1}: {error_msg}"
                )
                
                if attempt >= max_retries:
                    execution_time = time.time() - start_time
                    if run_id:
                        self.update_agent_status(run_id, agent_name, "FAILED",
                                               execution_time=execution_time,
                                               retry_count=attempt,
                                               error=error_msg)
                    
                    # Log final exception
                    self.agent_logger.log_agent_completion(
                        execution_id=execution_id,
                        success=False,
                        error_message=error_msg,
                        error_category=error_category,
                        retry_count=attempt
                    )
                    
                    return AgentExecutionResult(
                        agent_name=agent_name,
                        success=False,
                        error=error_msg,
                        execution_time=execution_time,
                        retry_count=attempt
                    )
        
        # Should never reach here, but safety fallback
        return AgentExecutionResult(
            agent_name=agent_name,
            success=False,
            error="Maximum retries exceeded",
            execution_time=time.time() - start_time,
            retry_count=max_retries
        )
    
    def orchestrate_with_validation_and_fallbacks(self, run_id: str) -> Dict[str, Any]:
        """
        Enhanced orchestration with content validation, error handling, and fallback mechanisms
        
        Args:
            run_id: Unique identifier for this orchestration run
            
        Returns:
            Complete content with validation results and fallback information
        """
        try:
            print(f"🚀 Starting enhanced orchestration for run {run_id}")
            
            # Start comprehensive orchestration logging
            self.agent_logger.log_orchestration_event(
                run_id=run_id,
                event_type="ORCHESTRATION_START",
                message=f"Starting enhanced orchestration with {len(self.agents)} agents",
                level=LogLevel.INFO,
                context={
                    'agents': self.agents,
                    'timeout': self.agent_timeout,
                    'max_retries': self.max_retries
                }
            )
            
            # Start performance tracking
            self.performance_tracker.start_tracking(run_id)
            
            # Step 1: Execute all agents with error handling
            agent_results = {}
            successful_sections = {}
            failed_sections = []
            
            for agent_name in self.agents:
                try:
                    print(f"🤖 Executing {agent_name} with error handling...")
                    
                    # Log agent execution start
                    self.agent_logger.log_orchestration_event(
                        run_id=run_id,
                        event_type="AGENT_EXECUTION_START",
                        message=f"Starting execution of {agent_name}",
                        level=LogLevel.INFO,
                        context={'agent_name': agent_name}
                    )
                    
                    # Create error context
                    error_context = ErrorContext(
                        agent_name=agent_name,
                        run_id=run_id,
                        operation=f"execute_{agent_name.lower()}",
                        attempt_number=1,
                        max_attempts=self.max_retries,
                        start_time=time.time(),
                        context_data={'orchestration_run': run_id}
                    )
                    
                    # Execute agent with comprehensive error handling
                    def agent_operation():
                        return self.execute_agent_with_retry(
                            agent_name, 
                            self._get_agent_prompt(agent_name), 
                            context={'run_id': run_id},
                            run_id=run_id
                        )
                    
                    recovery_result = self.error_handler.handle_with_recovery(
                        agent_operation, 
                        error_context
                    )
                    
                    if recovery_result.success:
                        agent_results[agent_name] = recovery_result.result
                        section_name = self._map_agent_to_section(agent_name)
                        successful_sections[section_name] = recovery_result.result.content
                        print(f"✅ {agent_name} completed successfully")
                        
                        # Log successful agent completion
                        self.agent_logger.log_orchestration_event(
                            run_id=run_id,
                            event_type="AGENT_EXECUTION_SUCCESS",
                            message=f"{agent_name} completed successfully",
                            level=LogLevel.INFO,
                            context={
                                'agent_name': agent_name,
                                'section_name': section_name,
                                'execution_time': recovery_result.result.execution_time
                            }
                        )
                    else:
                        agent_results[agent_name] = {
                            'success': False,
                            'error': recovery_result.error,
                            'recovery_metadata': recovery_result.metadata
                        }
                        section_name = self._map_agent_to_section(agent_name)
                        failed_sections.append(section_name)
                        print(f"❌ {agent_name} failed after all recovery attempts")
                        
                        # Log agent failure
                        self.agent_logger.log_orchestration_event(
                            run_id=run_id,
                            event_type="AGENT_EXECUTION_FAILURE",
                            message=f"{agent_name} failed after all recovery attempts: {recovery_result.error}",
                            level=LogLevel.ERROR,
                            context={
                                'agent_name': agent_name,
                                'section_name': section_name,
                                'error': recovery_result.error,
                                'recovery_metadata': recovery_result.metadata
                            }
                        )
                        
                except Exception as e:
                    print(f"❌ Critical error executing {agent_name}: {e}")
                    agent_results[agent_name] = {'success': False, 'error': str(e)}
                    section_name = self._map_agent_to_section(agent_name)
                    failed_sections.append(section_name)
                    
                    # Log critical error
                    self.agent_logger.log_orchestration_event(
                        run_id=run_id,
                        event_type="AGENT_CRITICAL_ERROR",
                        message=f"Critical error executing {agent_name}: {str(e)}",
                        level=LogLevel.CRITICAL,
                        context={
                            'agent_name': agent_name,
                            'section_name': section_name,
                            'exception': str(e)
                        }
                    )
            
            # Step 2: Analyze orchestration errors
            error_analysis = self.error_handler.handle_agent_orchestration_errors(run_id, agent_results)
            
            # Step 3: Create content structure from successful agents
            content_structure = self._build_content_structure(successful_sections, run_id)
            
            # Step 4: Handle failed sections with fallbacks
            if failed_sections:
                print(f"🔄 Handling {len(failed_sections)} failed sections with fallbacks")
                
                # Create graceful degradation plan
                degradation_plan = self.error_handler.create_graceful_degradation_plan(
                    failed_sections, 
                    successful_sections
                )
                
                # Get partial content delivery with fallbacks
                complete_content = self.fallback_manager.get_partial_content_delivery(
                    successful_sections, 
                    failed_sections
                )
                
                # Merge with existing content structure
                content_structure.update(complete_content)
                content_structure['degradation_plan'] = degradation_plan
            
            # Step 5: Validate complete content
            print(f"🔍 Validating complete content structure")
            validation_results = self.content_validator.validate_complete_content(content_structure)
            
            # Step 6: Handle validation failures with additional fallbacks
            critical_validation_issues = []
            for section_name, validation_result in validation_results.items():
                if validation_result.has_critical_issues():
                    critical_validation_issues.append(section_name)
            
            if critical_validation_issues:
                print(f"⚠️ Critical validation issues in: {critical_validation_issues}")
                
                # Apply additional fallbacks for validation failures
                for section_name in critical_validation_issues:
                    if section_name not in failed_sections:  # Don't double-process
                        fallback_result = self.fallback_manager.get_fallback_content(
                            section_name, 
                            context=content_structure
                        )
                        
                        if fallback_result and fallback_result.get('content'):
                            content_key = self.fallback_manager._get_content_key_for_section(section_name)
                            if '.' in content_key:
                                # Handle nested keys like 'agentOutputs.favoriteStory'
                                keys = content_key.split('.')
                                target = content_structure
                                for key in keys[:-1]:
                                    if key not in target:
                                        target[key] = {}
                                    target = target[key]
                                target[keys[-1]] = fallback_result['content']
                            else:
                                content_structure[content_key] = fallback_result['content']
            
            # Step 7: Generate validation report
            validation_report = self.content_validator.generate_validation_report(validation_results)
            
            # Step 8: Finalize enhanced content structure
            enhanced_content = {
                **content_structure,
                'orchestration_metadata': {
                    'run_id': run_id,
                    'successful_agents': len([r for r in agent_results.values() if r.get('success')]),
                    'failed_agents': len([r for r in agent_results.values() if not r.get('success')]),
                    'successful_sections': list(successful_sections.keys()),
                    'failed_sections': failed_sections,
                    'validation_summary': validation_results.get('_summary'),
                    'error_analysis': error_analysis,
                    'completion_timestamp': datetime.utcnow().isoformat(),
                    'quality_score': validation_results.get('_summary', {}).score if validation_results.get('_summary') else 0
                },
                'validation_report': validation_report,
                'agent_results': agent_results
            }
            
            # Step 9: Generate performance report
            performance_report = self.performance_tracker.finish_tracking(run_id)
            enhanced_content['performance_report'] = performance_report
            
            # Record orchestration metrics
            self.performance_monitor.record_orchestration_metrics(
                run_id=run_id,
                total_time_ms=performance_report.get('total_orchestration_time_ms', 0),
                successful_agents=enhanced_content['orchestration_metadata']['successful_agents'],
                failed_agents=enhanced_content['orchestration_metadata']['failed_agents'],
                total_agents=len(self.agents),
                parallel_efficiency=performance_report.get('parallel_efficiency', 0)
            )
            
            # Record system metrics
            self.performance_monitor.record_system_metrics(run_id)
            
            # Step 10: Store enhanced results
            self._store_enhanced_orchestration_results(run_id, enhanced_content)
            
            # Step 11: Log orchestration completion
            self.agent_logger.log_orchestration_event(
                run_id=run_id,
                event_type="ORCHESTRATION_COMPLETE",
                message=f"Enhanced orchestration completed successfully",
                level=LogLevel.INFO,
                agents_status={
                    'successful': enhanced_content['orchestration_metadata']['successful_agents'],
                    'failed': enhanced_content['orchestration_metadata']['failed_agents'],
                    'total': len(self.agents)
                },
                performance_data=performance_report,
                context={
                    'quality_score': enhanced_content['orchestration_metadata']['quality_score'],
                    'successful_sections': enhanced_content['orchestration_metadata']['successful_sections'],
                    'failed_sections': enhanced_content['orchestration_metadata']['failed_sections']
                }
            )
            
            # Flush all pending metrics to CloudWatch
            self.performance_monitor.flush_metrics()
            
            print(f"🎉 Enhanced orchestration completed for run {run_id}")
            print(f"📊 Quality Score: {enhanced_content['orchestration_metadata']['quality_score']:.1f}")
            print(f"✅ Successful: {enhanced_content['orchestration_metadata']['successful_agents']}/{len(self.agents)} agents")
            print(f"⚡ Performance: {performance_report.get('parallel_efficiency', 0):.2f} parallel efficiency")
            
            return enhanced_content
            
        except Exception as e:
            print(f"❌ Critical error in enhanced orchestration: {e}")
            import traceback
            traceback.print_exc()
            
            # Log critical orchestration failure
            self.agent_logger.log_orchestration_event(
                run_id=run_id,
                event_type="ORCHESTRATION_CRITICAL_FAILURE",
                message=f"Critical orchestration failure: {str(e)}",
                level=LogLevel.CRITICAL,
                context={
                    'exception': str(e),
                    'traceback': traceback.format_exc()
                }
            )
            
            # Finish performance tracking even on failure
            try:
                performance_report = self.performance_tracker.finish_tracking(run_id)
            except:
                performance_report = {'error': 'Performance tracking failed'}
            
            # Return emergency fallback content with error information
            emergency_content = self.fallback_manager._create_emergency_content()
            emergency_content['orchestration_error'] = {
                'error': str(e),
                'performance_report': performance_report,
                'timestamp': datetime.utcnow().isoformat()
            }
            return emergency_content
    
    def _map_agent_to_section(self, agent_name: str) -> str:
        """Map agent name to content section name"""
        mapping = {
            'NEWS_FETCHER': 'news_stories',
            'CONTENT_CURATOR': 'news_stories',  # Also contributes to news stories
            'FAVORITE_SELECTOR': 'favorite_story',
            'SCRIPT_GENERATOR': 'script_content',
            'MEDIA_ENHANCER': 'visual_enhancements',
            'WEEKEND_EVENTS': 'weekend_recommendations'
        }
        return mapping.get(agent_name, agent_name.lower())
    
    def _get_agent_prompt(self, agent_name: str) -> str:
        """Get appropriate prompt for agent (placeholder - would use actual prompts)"""
        prompts = {
            'NEWS_FETCHER': "Fetch and analyze current news stories relevant to Gen Z/Millennial audiences",
            'CONTENT_CURATOR': "Curate the most relevant and engaging news stories",
            'FAVORITE_SELECTOR': "Select the most fascinating story with 'wow factor'",
            'SCRIPT_GENERATOR': "Generate engaging script with millennial tone",
            'MEDIA_ENHANCER': "Enhance content with visual elements and accessibility",
            'WEEKEND_EVENTS': "Curate cultural recommendations and trending activities"
        }
        return prompts.get(agent_name, f"Execute {agent_name} operation")
    
    def _build_content_structure(self, successful_sections: Dict[str, Any], run_id: str) -> Dict[str, Any]:
        """Build basic content structure from successful agent results"""
        content = {
            'run_id': run_id,
            'generatedAt': datetime.utcnow().isoformat(),
            'sources': ['AI Agents', 'NewsAPI', 'RSS Feeds'],
            'why': 'Content generated by specialized AI agents with validation and fallback systems',
            'traceId': f'enhanced-{run_id}',
            'news_items': [],
            'script': '',
            'audioUrl': '',
            'word_timings': [],
            'agentOutputs': {}
        }
        
        # Map successful sections to content structure
        for section_name, section_content in successful_sections.items():
            if section_name == 'news_stories':
                content['news_items'] = section_content if isinstance(section_content, list) else []
            elif section_name == 'script_content':
                content['script'] = section_content if isinstance(section_content, str) else ''
            elif section_name == 'favorite_story':
                content['agentOutputs']['favoriteStory'] = section_content
            elif section_name == 'weekend_recommendations':
                content['agentOutputs']['weekendRecommendations'] = section_content
            elif section_name == 'visual_enhancements':
                content['agentOutputs']['mediaEnhancements'] = section_content
        
        return content
    
    def _store_enhanced_orchestration_results(self, run_id: str, enhanced_content: Dict[str, Any]):
        """Store enhanced orchestration results in DynamoDB"""
        try:
            # Store main content
            item = {
                'pk': {'S': 'enhanced_brief'},
                'sk': {'S': run_id},
                'content': {'S': json.dumps(enhanced_content, ensure_ascii=False)},
                'qualityScore': {'N': str(enhanced_content['orchestration_metadata']['quality_score'])},
                'successfulAgents': {'N': str(enhanced_content['orchestration_metadata']['successful_agents'])},
                'failedAgents': {'N': str(enhanced_content['orchestration_metadata']['failed_agents'])},
                'timestamp': {'S': enhanced_content['orchestration_metadata']['completion_timestamp']},
                'expiresAt': {'N': str(int(time.time()) + (24 * 3600))},  # 24 hour TTL
                'gsi1pk': {'S': f'quality#{int(enhanced_content["orchestration_metadata"]["quality_score"])}'},
                'gsi1sk': {'S': enhanced_content['orchestration_metadata']['completion_timestamp']}
            }
            
            dynamodb.put_item(TableName=self.curio_table, Item=item)
            
            # Also update the latest brief for backward compatibility
            self._update_latest_brief_with_enhanced_content(enhanced_content)
            
            print(f"💾 Stored enhanced orchestration results for run {run_id}")
            
        except Exception as e:
            print(f"❌ Error storing enhanced orchestration results: {e}")
    
    def _update_latest_brief_with_enhanced_content(self, enhanced_content: Dict[str, Any]):
        """Update the latest brief with enhanced content for backward compatibility"""
        try:
            # Extract core content for the existing brief format
            brief_content = {
                'audioUrl': enhanced_content.get('audioUrl', ''),
                'sources': enhanced_content.get('sources', []),
                'generatedAt': enhanced_content.get('generatedAt', ''),
                'why': enhanced_content.get('why', ''),
                'traceId': enhanced_content.get('traceId', ''),
                'script': enhanced_content.get('script', ''),
                'news_items': enhanced_content.get('news_items', []),
                'word_timings': enhanced_content.get('word_timings', [])
            }
            
            # Add quality and orchestration metadata
            brief_content['quality_score'] = enhanced_content['orchestration_metadata']['quality_score']
            brief_content['enhanced_orchestration'] = True
            brief_content['validation_passed'] = enhanced_content['orchestration_metadata']['quality_score'] >= 70
            
            item = {
                'pk': {'S': 'brief'},
                'sk': {'S': 'latest'},
                'audioUrl': {'S': brief_content['audioUrl']},
                'sources': {'S': json.dumps(brief_content['sources'])},
                'generatedAt': {'S': brief_content['generatedAt']},
                'why': {'S': brief_content['why']},
                'traceId': {'S': brief_content['traceId']},
                'script': {'S': brief_content['script']},
                'news_items': {'S': json.dumps(brief_content['news_items'])},
                'word_timings': {'S': json.dumps(brief_content['word_timings'])},
                'qualityScore': {'N': str(brief_content['quality_score'])},
                'enhancedOrchestration': {'BOOL': True},
                'validationPassed': {'BOOL': brief_content['validation_passed']},
                'expiresAt': {'N': str(int(time.time()) + (24 * 3600))}
            }
            
            dynamodb.put_item(TableName=self.curio_table, Item=item)
            
        except Exception as e:
            print(f"❌ Error updating latest brief: {e}")
    
    def _execute_agent_with_timeout(self, agent_name: str, prompt: str, context: Dict = None) -> Dict:
        """Execute agent with timeout handling"""
        def timeout_handler():
            return {
                'success': False,
                'error': f'Agent {agent_name} timed out after {self.agent_timeout} seconds',
                'agent': agent_name,
                'timestamp': datetime.utcnow().isoformat()
            }
        
        try:
            # Use ThreadPoolExecutor for timeout handling
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(self.invoke_bedrock_agent, agent_name, prompt, context)
                
                try:
                    result = future.result(timeout=self.agent_timeout)
                    return result
                except concurrent.futures.TimeoutError:
                    print(f"⏰ {agent_name} timed out after {self.agent_timeout} seconds")
                    return timeout_handler()
                    
        except Exception as e:
            return {
                'success': False,
                'error': f'Execution error: {str(e)}',
                'agent': agent_name,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def get_orchestration_summary(self, run_id: str) -> Dict[str, Any]:
        """Get comprehensive orchestration summary for monitoring"""
        try:
            with self.execution_lock:
                agent_statuses = self.agent_status.get(run_id, {})
            
            summary = {
                'run_id': run_id,
                'total_agents': len(self.agents),
                'completed_agents': 0,
                'failed_agents': 0,
                'running_agents': 0,
                'agents': {},
                'overall_status': 'UNKNOWN',
                'total_execution_time': 0,
                'total_retries': 0
            }
            
            for agent_name in self.agents:
                agent_info = agent_statuses.get(agent_name, {})
                status = agent_info.get('status', 'NOT_STARTED')
                
                summary['agents'][agent_name] = {
                    'status': status,
                    'execution_time': agent_info.get('execution_time', 0),
                    'retry_count': agent_info.get('retry_count', 0),
                    'error': agent_info.get('error'),
                    'updated_at': agent_info.get('updated_at')
                }
                
                if status == 'COMPLETED':
                    summary['completed_agents'] += 1
                elif status == 'FAILED':
                    summary['failed_agents'] += 1
                elif status in ['RUNNING', 'STARTING']:
                    summary['running_agents'] += 1
                
                summary['total_execution_time'] += agent_info.get('execution_time', 0)
                summary['total_retries'] += agent_info.get('retry_count', 0)
            
            # Determine overall status
            if summary['completed_agents'] == len(self.agents):
                summary['overall_status'] = 'COMPLETED'
            elif summary['failed_agents'] > 0 and summary['running_agents'] == 0:
                summary['overall_status'] = 'FAILED'
            elif summary['running_agents'] > 0:
                summary['overall_status'] = 'RUNNING'
            else:
                summary['overall_status'] = 'NOT_STARTED'
            
            return summary
            
        except Exception as e:
            print(f"❌ Error getting orchestration summary: {e}")
            return {
                'run_id': run_id,
                'error': str(e),
                'overall_status': 'ERROR'
            }
    
    def get_comprehensive_debugging_info(self, run_id: str) -> Dict[str, Any]:
        """Get comprehensive debugging information for a run"""
        try:
            # Get orchestration summary
            orchestration_summary = self.get_orchestration_summary(run_id)
            
            # Get detailed agent execution history
            agent_execution_history = self.agent_logger.get_agent_execution_history(run_id)
            
            # Get orchestration logs summary
            orchestration_logs_summary = self.agent_logger.get_orchestration_summary(run_id)
            
            # Get performance metrics
            try:
                response = self.dynamodb.query(
                    TableName=self.curio_table,
                    KeyConditionExpression='pk = :pk',
                    ExpressionAttributeValues={
                        ':pk': {'S': 'performance_metrics'}
                    },
                    FilterExpression='contains(sk, :run_id)',
                    ExpressionAttributeValues={
                        ':pk': {'S': 'performance_metrics'},
                        ':run_id': {'S': run_id}
                    }
                )
                
                performance_metrics = []
                for item in response.get('Items', []):
                    metrics_data = json.loads(item.get('metrics', {}).get('S', '{}'))
                    performance_metrics.append({
                        'timestamp': item.get('timestamp', {}).get('S', ''),
                        'metrics': metrics_data
                    })
            except Exception as e:
                performance_metrics = [{'error': f'Could not retrieve performance metrics: {e}'}]
            
            # Analyze common failure patterns
            failure_analysis = self._analyze_failure_patterns(agent_execution_history)
            
            # Generate debugging recommendations
            debugging_recommendations = self._generate_debugging_recommendations(
                orchestration_summary, agent_execution_history, failure_analysis
            )
            
            return {
                'run_id': run_id,
                'orchestration_summary': orchestration_summary,
                'agent_execution_history': agent_execution_history,
                'orchestration_logs_summary': orchestration_logs_summary,
                'performance_metrics': performance_metrics,
                'failure_analysis': failure_analysis,
                'debugging_recommendations': debugging_recommendations,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error generating debugging info: {e}")
            return {
                'run_id': run_id,
                'error': str(e),
                'generated_at': datetime.utcnow().isoformat()
            }
    
    def _analyze_failure_patterns(self, agent_execution_history: List[Dict]) -> Dict[str, Any]:
        """Analyze common failure patterns in agent execution"""
        try:
            failure_patterns = {
                'timeout_failures': 0,
                'throttling_failures': 0,
                'validation_failures': 0,
                'network_failures': 0,
                'most_failing_agent': None,
                'average_retry_count': 0,
                'common_error_categories': {}
            }
            
            failed_agents = {}
            total_retries = 0
            error_categories = {}
            
            for log_entry in agent_execution_history:
                if log_entry.get('status') == 'FAILED':
                    agent_name = log_entry.get('agent_name')
                    error_category = log_entry.get('error_category', 'UNKNOWN')
                    retry_count = log_entry.get('retry_count', 0)
                    
                    # Count failures per agent
                    failed_agents[agent_name] = failed_agents.get(agent_name, 0) + 1
                    
                    # Count error categories
                    error_categories[error_category] = error_categories.get(error_category, 0) + 1
                    
                    # Count specific failure types
                    if error_category == 'TIMEOUT_ERROR':
                        failure_patterns['timeout_failures'] += 1
                    elif error_category == 'THROTTLING_ERROR':
                        failure_patterns['throttling_failures'] += 1
                    elif error_category == 'VALIDATION_ERROR':
                        failure_patterns['validation_failures'] += 1
                    elif error_category == 'NETWORK_ERROR':
                        failure_patterns['network_failures'] += 1
                    
                    total_retries += retry_count
            
            # Find most failing agent
            if failed_agents:
                failure_patterns['most_failing_agent'] = max(failed_agents, key=failed_agents.get)
                failure_patterns['average_retry_count'] = total_retries / len(failed_agents)
            
            failure_patterns['common_error_categories'] = error_categories
            failure_patterns['agent_failure_counts'] = failed_agents
            
            return failure_patterns
            
        except Exception as e:
            return {'error': f'Could not analyze failure patterns: {e}'}
    
    def _generate_debugging_recommendations(self, orchestration_summary: Dict, 
                                          agent_history: List[Dict], 
                                          failure_analysis: Dict) -> List[str]:
        """Generate debugging recommendations based on analysis"""
        recommendations = []
        
        try:
            # Check overall success rate
            if orchestration_summary.get('overall_status') == 'FAILED':
                recommendations.append("🔍 Multiple agents failed - check system resources and network connectivity")
            
            # Check for timeout issues
            if failure_analysis.get('timeout_failures', 0) > 0:
                recommendations.append("⏰ Timeout failures detected - consider increasing agent timeout or optimizing prompts")
            
            # Check for throttling
            if failure_analysis.get('throttling_failures', 0) > 0:
                recommendations.append("🚦 Throttling detected - implement exponential backoff or reduce concurrent requests")
            
            # Check for specific agent issues
            most_failing_agent = failure_analysis.get('most_failing_agent')
            if most_failing_agent:
                recommendations.append(f"🎯 {most_failing_agent} is failing most frequently - review its specific implementation")
            
            # Check retry patterns
            avg_retries = failure_analysis.get('average_retry_count', 0)
            if avg_retries > 2:
                recommendations.append("🔄 High retry count suggests systemic issues - review error handling logic")
            
            # Check for validation issues
            if failure_analysis.get('validation_failures', 0) > 0:
                recommendations.append("✅ Validation failures detected - review content validation rules and agent outputs")
            
            # Performance recommendations
            total_time = orchestration_summary.get('total_execution_time', 0)
            if total_time > 300000:  # 5 minutes
                recommendations.append("⚡ Long execution time - consider parallel execution or prompt optimization")
            
            if not recommendations:
                recommendations.append("✅ No specific issues detected - system appears to be functioning normally")
            
            return recommendations
            
        except Exception as e:
            return [f"❌ Could not generate recommendations: {e}"]
    
    def get_agent_performance_dashboard(self, agent_name: str = None, hours_back: int = 24) -> Dict[str, Any]:
        """Get comprehensive performance dashboard data"""
        try:
            if agent_name:
                # Get performance summary for specific agent
                return self.performance_monitor.get_agent_performance_summary(agent_name, hours_back)
            else:
                # Get performance summary for all agents
                dashboard_data = {
                    'agents': {},
                    'system_overview': {},
                    'dashboard_config': self.performance_monitor.create_performance_dashboard(),
                    'generated_at': datetime.utcnow().isoformat()
                }
                
                for agent in self.agents:
                    dashboard_data['agents'][agent] = self.performance_monitor.get_agent_performance_summary(
                        agent, hours_back
                    )
                
                return dashboard_data
                
        except Exception as e:
            return {'error': f'Could not generate performance dashboard: {e}'}
    
    def setup_monitoring_and_alerts(self):
        """Set up comprehensive monitoring and alerting"""
        try:
            print("🔧 Setting up CloudWatch alarms...")
            self.performance_monitor.setup_cloudwatch_alarms()
            
            print("📊 Performance monitoring configured successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error setting up monitoring: {e}")
            return False
    
    def get_real_time_metrics(self, run_id: str) -> Dict[str, Any]:
        """Get real-time metrics for active orchestration"""
        try:
            # Get current orchestration status
            orchestration_summary = self.get_orchestration_summary(run_id)
            
            # Get recent agent logs
            recent_logs = self.agent_logger.get_agent_execution_history(run_id)
            
            # Calculate real-time metrics
            running_agents = [
                agent for agent, status in orchestration_summary.get('agents', {}).items()
                if status.get('status') in ['RUNNING', 'STARTING']
            ]
            
            completed_agents = [
                agent for agent, status in orchestration_summary.get('agents', {}).items()
                if status.get('status') == 'COMPLETED'
            ]
            
            failed_agents = [
                agent for agent, status in orchestration_summary.get('agents', {}).items()
                if status.get('status') == 'FAILED'
            ]
            
            # Calculate progress percentage
            total_agents = len(self.agents)
            completed_count = len(completed_agents)
            progress_percentage = (completed_count / total_agents) * 100 if total_agents > 0 else 0
            
            # Estimate remaining time based on current performance
            if running_agents and completed_agents:
                avg_completion_time = sum(
                    orchestration_summary.get('agents', {}).get(agent, {}).get('execution_time', 0)
                    for agent in completed_agents
                ) / len(completed_agents)
                
                estimated_remaining_time = avg_completion_time * len(running_agents)
            else:
                estimated_remaining_time = 0
            
            return {
                'run_id': run_id,
                'overall_status': orchestration_summary.get('overall_status', 'UNKNOWN'),
                'progress_percentage': progress_percentage,
                'running_agents': running_agents,
                'completed_agents': completed_agents,
                'failed_agents': failed_agents,
                'estimated_remaining_time_ms': estimated_remaining_time,
                'total_execution_time_ms': orchestration_summary.get('total_execution_time', 0),
                'total_retries': orchestration_summary.get('total_retries', 0),
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'run_id': run_id,
                'error': str(e),
                'last_updated': datetime.utcnow().isoformat()
            }

class AgentExecutionMonitor:
    """Real-time agent execution monitoring with timeout detection"""
    
    def __init__(self, agent_name: str, run_id: str, timeout: int = 60):
        self.agent_name = agent_name
        self.run_id = run_id
        self.timeout = timeout
        self.start_time = time.time()
        self.status = 'STARTING'
        self.error_category = None
        self.execution_id = f"{run_id}_{agent_name}_{int(self.start_time)}"
        
    def start_monitoring(self):
        """Start monitoring agent execution"""
        self.start_time = time.time()
        self.status = 'RUNNING'
        print(f"🔍 Started monitoring {self.agent_name} (ID: {self.execution_id})")
        
    def check_timeout(self) -> bool:
        """Check if agent execution has timed out"""
        elapsed = time.time() - self.start_time
        if elapsed > self.timeout:
            self.status = 'TIMEOUT'
            self.error_category = 'TIMEOUT_ERROR'
            print(f"⏰ {self.agent_name} timed out after {elapsed:.1f}s")
            return True
        return False
        
    def mark_completed(self, success: bool, error: str = None):
        """Mark agent execution as completed"""
        elapsed = time.time() - self.start_time
        if success:
            self.status = 'COMPLETED'
            print(f"✅ {self.agent_name} completed in {elapsed:.1f}s")
        else:
            self.status = 'FAILED'
            self.error_category = self._categorize_error(error)
            print(f"❌ {self.agent_name} failed after {elapsed:.1f}s: {error}")
            
    def _categorize_agent_error(self, error: str) -> str:
        """Categorize agent error for better debugging"""
        if not error:
            return "UNKNOWN_ERROR"
        
        error_lower = error.lower()
        
        if "timeout" in error_lower:
            return "TIMEOUT_ERROR"
        elif "throttl" in error_lower or "rate limit" in error_lower:
            return "THROTTLING_ERROR"
        elif "bedrock" in error_lower:
            return "BEDROCK_SERVICE_ERROR"
        elif "validation" in error_lower:
            return "VALIDATION_ERROR"
        elif "network" in error_lower or "connection" in error_lower:
            return "NETWORK_ERROR"
        elif "permission" in error_lower or "access" in error_lower:
            return "PERMISSION_ERROR"
        elif "json" in error_lower or "parsing" in error_lower:
            return "PARSING_ERROR"
        else:
            return "GENERAL_ERROR"
    
    def _categorize_error(self, error: str) -> str:
        """Categorize error for better debugging"""
        if not error:
            return 'UNKNOWN_ERROR'
            
        error_lower = error.lower()
        
        if 'timeout' in error_lower:
            return 'TIMEOUT_ERROR'
        elif 'throttl' in error_lower or 'rate limit' in error_lower:
            return 'THROTTLING_ERROR'
        elif 'bedrock' in error_lower or 'model' in error_lower:
            return 'MODEL_ERROR'
        elif 'json' in error_lower or 'parse' in error_lower:
            return 'PARSING_ERROR'
        elif 'network' in error_lower or 'connection' in error_lower:
            return 'NETWORK_ERROR'
        elif 'permission' in error_lower or 'access' in error_lower:
            return 'PERMISSION_ERROR'
        else:
            return 'EXECUTION_ERROR'
    
    def get_status_summary(self) -> Dict:
        """Get current monitoring status"""
        elapsed = time.time() - self.start_time
        return {
            'execution_id': self.execution_id,
            'agent_name': self.agent_name,
            'run_id': self.run_id,
            'status': self.status,
            'elapsed_time': round(elapsed, 1),
            'timeout_threshold': self.timeout,
            'error_category': self.error_category,
            'is_timeout_risk': elapsed > (self.timeout * 0.8)  # 80% of timeout
        }
    
    def log_agent_decision(self, run_id: str, agent_name: str, input_data: Dict, output_data: Dict, processing_details: Dict = None):
        """Log comprehensive agent decision data for provenance tracking"""
        try:
            if run_id not in self.trace_data:
                self.trace_data[run_id] = {
                    'runId': run_id,
                    'startTime': datetime.utcnow().isoformat(),
                    'agents': [],
                    'status': 'IN_PROGRESS'
                }
            
            agent_trace = {
                'name': agent_name,
                'emoji': self.get_agent_emoji(agent_name),
                'description': self.get_agent_description(agent_name),
                'startTime': datetime.utcnow().isoformat(),
                'input': {
                    'prompt': input_data.get('prompt', ''),
                    'context': input_data.get('context', {}),
                    'contextSize': len(str(input_data.get('context', {})))
                },
                'processing': processing_details or {},
                'output': {
                    'success': output_data.get('success', False),
                    'content': output_data.get('content', ''),
                    'contentLength': len(output_data.get('content', '')),
                    'error': output_data.get('error', None)
                },
                'endTime': datetime.utcnow().isoformat(),
                'status': 'COMPLETED' if output_data.get('success') else 'FAILED'
            }
            
            # Calculate duration
            try:
                start_time = datetime.fromisoformat(agent_trace['startTime'].replace('Z', '+00:00'))
                end_time = datetime.fromisoformat(agent_trace['endTime'].replace('Z', '+00:00'))
                duration = (end_time - start_time).total_seconds()
                agent_trace['duration'] = f"{duration:.1f}s"
            except:
                agent_trace['duration'] = "0.0s"
            
            # Add agent-specific decision details
            agent_trace['decisionDetails'] = self.extract_decision_details(agent_name, input_data, output_data)
            
            self.trace_data[run_id]['agents'].append(agent_trace)
            
            # Store trace data in DynamoDB for persistence
            self.store_trace_data(run_id, agent_trace)
            
        except Exception as e:
            print(f"❌ Error logging agent decision for {agent_name}: {e}")

    def extract_decision_details(self, agent_name: str, input_data: Dict, output_data: Dict) -> Dict:
        """Extract agent-specific decision details for transparency"""
        details = {}
        
        try:
            if agent_name == "NEWS_FETCHER":
                details = {
                    'sourcesChecked': ['NewsAPI', 'BBC RSS', 'Reuters RSS', 'TechCrunch RSS', 'The Verge RSS', 'NPR RSS'],
                    'articlesFound': len(input_data.get('context', {}).get('current_news', [])),
                    'filterCriteria': 'Gen Z/Millennial relevance, trending topics, category diversity',
                    'selectionReason': 'Prioritized technology, culture, and politics affecting young adults'
                }
            
            elif agent_name == "CONTENT_CURATOR":
                try:
                    content = output_data.get('content', '[]')
                    if isinstance(content, str) and content.startswith('['):
                        curated_items = json.loads(content)
                        details = {
                            'storiesConsidered': len(input_data.get('context', {}).get('news_stories', [])),
                            'storiesSelected': len(curated_items),
                            'selectionCriteria': 'Category balance, engagement potential, narrative flow',
                            'categories': [item.get('category', 'UNKNOWN') for item in curated_items],
                            'averageRelevance': sum(item.get('relevance_score', 0) for item in curated_items) / len(curated_items) if curated_items else 0
                        }
                except:
                    details = {'error': 'Could not parse curator output for analysis'}
            
            elif agent_name == "FAVORITE_SELECTOR":
                details = {
                    'selectionCriteria': '"Wow factor", shareability, curiosity spark',
                    'analysisFactors': ['Scientific breakthrough potential', 'Cultural impact', 'Viral potential', 'Educational value'],
                    'reasoning': 'Selected story most likely to generate "that\'s actually really cool!" response'
                }
            
            elif agent_name == "SCRIPT_GENERATOR":
                script_content = output_data.get('content', '')
                word_count = len(script_content.split()) if script_content else 0
                millennial_phrases = ['honestly', 'lowkey', 'ngl', 'get this', 'wild', 'plot twist']
                phrases_used = [phrase for phrase in millennial_phrases if phrase in script_content.lower()]
                
                details = {
                    'targetLength': '90 seconds (225-250 words)',
                    'actualWordCount': word_count,
                    'millennialPhrases': phrases_used,
                    'toneElements': ['Conversational', 'Authentic', 'Engaging', 'Friend-to-friend'],
                    'structureUsed': 'Opening → Main story → Quick hits → Favorite story → Closing',
                    'languageChoices': 'Contractions, casual tone, no formal attributions'
                }
            
            elif agent_name == "MEDIA_ENHANCER":
                details = {
                    'enhancementTypes': ['Visual hierarchy', 'Category tags', 'Relevance scores', 'Accessibility features'],
                    'visualElements': 'Color-coded categories, engagement indicators, responsive design',
                    'accessibilityFeatures': 'Screen reader support, keyboard navigation, high contrast'
                }
            
            elif agent_name == "WEEKEND_EVENTS":
                details = {
                    'curationFocus': 'BookTok trends, streaming releases, local events, social media phenomena',
                    'targetAudience': 'Gen Z/Millennial cultural interests',
                    'recommendationTypes': ['Books', 'Movies', 'Events', 'Trending topics'],
                    'culturalContext': 'Current social media trends and viral content'
                }
        
        except Exception as e:
            details = {'error': f'Could not extract decision details: {str(e)}'}
        
        return details

    def get_agent_emoji(self, agent_name: str) -> str:
        """Get emoji for agent visualization"""
        emojis = {
            "NEWS_FETCHER": "📰",
            "CONTENT_CURATOR": "🎯", 
            "FAVORITE_SELECTOR": "⭐",
            "SCRIPT_GENERATOR": "📝",
            "MEDIA_ENHANCER": "🎨",
            "WEEKEND_EVENTS": "🎉"
        }
        return emojis.get(agent_name, "🤖")

    def get_agent_description(self, agent_name: str) -> str:
        """Get human-readable description of agent's role"""
        descriptions = {
            "NEWS_FETCHER": "Gathers trending stories from multiple news sources",
            "CONTENT_CURATOR": "Selects most relevant stories for target audience", 
            "FAVORITE_SELECTOR": "Identifies most fascinating story with 'wow factor'",
            "SCRIPT_GENERATOR": "Creates engaging script with millennial tone",
            "MEDIA_ENHANCER": "Enhances content with visual elements and accessibility",
            "WEEKEND_EVENTS": "Curates cultural recommendations and trending activities"
        }
        return descriptions.get(agent_name, "AI agent processing")

    def store_detailed_agent_status(self, run_id: str, agent_name: str, status_data: Dict):
        """Store detailed agent status with comprehensive tracking"""
        try:
            timestamp = datetime.utcnow().isoformat()
            
            # Store individual agent status record
            item = {
                'pk': {'S': f'agent_status'},
                'sk': {'S': f'{run_id}#{agent_name}#{timestamp}'},
                'runId': {'S': run_id},
                'agentName': {'S': agent_name},
                'status': {'S': status_data.get('status', 'UNKNOWN')},
                'timestamp': {'S': timestamp},
                'executionTime': {'N': str(status_data.get('execution_time', 0))},
                'retryCount': {'N': str(status_data.get('retry_count', 0))},
                'expiresAt': {'N': str(int(time.time()) + 86400)},  # 24 hour TTL
                'gsi1pk': {'S': f'run#{run_id}'},
                'gsi1sk': {'S': timestamp}
            }
            
            if status_data.get('error'):
                item['error'] = {'S': status_data['error']}
            
            if status_data.get('content'):
                # Store content summary (first 500 chars)
                content_summary = str(status_data['content'])[:500]
                item['contentSummary'] = {'S': content_summary}
                item['contentLength'] = {'N': str(len(str(status_data['content'])))}
            
            dynamodb.put_item(TableName=self.curio_table, Item=item)
            
            # Also update the latest status for this agent
            self._update_latest_agent_status(run_id, agent_name, status_data)
            
            print(f"✅ Stored detailed status for {agent_name}: {status_data.get('status')}")
            
        except Exception as e:
            print(f"❌ Error storing detailed agent status for {agent_name}: {e}")
    
    def _update_latest_agent_status(self, run_id: str, agent_name: str, status_data: Dict):
        """Update the latest status record for quick polling"""
        try:
            item = {
                'pk': {'S': f'latest_status'},
                'sk': {'S': f'{run_id}#{agent_name}'},
                'runId': {'S': run_id},
                'agentName': {'S': agent_name},
                'status': {'S': status_data.get('status', 'UNKNOWN')},
                'lastUpdated': {'S': datetime.utcnow().isoformat()},
                'executionTime': {'N': str(status_data.get('execution_time', 0))},
                'retryCount': {'N': str(status_data.get('retry_count', 0))},
                'expiresAt': {'N': str(int(time.time()) + 3600)},  # 1 hour TTL
                'gsi1pk': {'S': f'status_poll#{run_id}'},
                'gsi1sk': {'S': datetime.utcnow().isoformat()}
            }
            
            if status_data.get('error'):
                item['error'] = {'S': status_data['error']}
            
            dynamodb.put_item(TableName=self.curio_table, Item=item)
            
        except Exception as e:
            print(f"❌ Error updating latest agent status for {agent_name}: {e}")
    
    def get_real_time_status(self, run_id: str) -> Dict:
        """Get real-time status of all agents for monitoring"""
        try:
            # Query latest status records for this run
            response = dynamodb.query(
                TableName=self.curio_table,
                IndexName='GSI1',  # Assuming GSI1 exists
                KeyConditionExpression='gsi1pk = :pk',
                ExpressionAttributeValues={
                    ':pk': {'S': f'status_poll#{run_id}'}
                },
                ScanIndexForward=False,  # Get latest first
                Limit=50
            )
            
            agent_statuses = {}
            for item in response.get('Items', []):
                agent_name = item['agentName']['S']
                if agent_name not in agent_statuses:  # Only keep the latest
                    agent_statuses[agent_name] = {
                        'status': item['status']['S'],
                        'last_updated': item['lastUpdated']['S'],
                        'execution_time': float(item.get('executionTime', {}).get('N', '0')),
                        'retry_count': int(item.get('retryCount', {}).get('N', '0')),
                        'error': item.get('error', {}).get('S')
                    }
            
            # Calculate overall progress
            total_agents = len(self.agents)
            completed = sum(1 for status in agent_statuses.values() if status['status'] == 'COMPLETED')
            failed = sum(1 for status in agent_statuses.values() if status['status'] == 'FAILED')
            running = sum(1 for status in agent_statuses.values() if status['status'] == 'RUNNING')
            
            return {
                'run_id': run_id,
                'agents': agent_statuses,
                'progress': {
                    'total': total_agents,
                    'completed': completed,
                    'failed': failed,
                    'running': running,
                    'percentage': round((completed / total_agents) * 100, 1) if total_agents > 0 else 0
                },
                'overall_status': self._determine_overall_status(completed, failed, running, total_agents),
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error getting real-time status: {e}")
            return {
                'run_id': run_id,
                'error': str(e),
                'overall_status': 'ERROR'
            }
    
    def _determine_overall_status(self, completed: int, failed: int, running: int, total: int) -> str:
        """Determine overall orchestration status"""
        if completed == total:
            return 'COMPLETED'
        elif failed > 0 and running == 0:
            return 'FAILED'
        elif running > 0:
            return 'RUNNING'
        elif completed + failed + running == 0:
            return 'NOT_STARTED'
        else:
            return 'PARTIAL'
    
    def store_trace_data(self, run_id: str, agent_trace: Dict):
        """Store individual agent trace data in DynamoDB with enhanced tracking"""
        try:
            # Store the original trace data
            item = {
                'pk': {'S': f'trace'},
                'sk': {'S': f'{run_id}#{agent_trace["name"]}'},
                'runId': {'S': run_id},
                'agentName': {'S': agent_trace['name']},
                'traceData': {'S': json.dumps(agent_trace, ensure_ascii=False)},
                'status': {'S': agent_trace['status']},
                'timestamp': {'S': agent_trace['endTime']},
                'expiresAt': {'N': str(int(time.time()) + 86400)},  # 24 hour TTL
                'gsi1pk': {'S': f'run#{run_id}'},
                'gsi1sk': {'S': agent_trace['endTime']}
            }
            
            dynamodb.put_item(TableName=self.curio_table, Item=item)
            
            # Also store detailed status tracking
            status_data = {
                'status': agent_trace['status'],
                'execution_time': float(agent_trace.get('duration', '0s').replace('s', '')),
                'retry_count': 0,  # Will be updated by retry logic
                'content': agent_trace.get('output', {}).get('content'),
                'error': agent_trace.get('output', {}).get('error')
            }
            
            self.store_detailed_agent_status(run_id, agent_trace['name'], status_data)
            
            print(f"✅ Stored trace data for {agent_trace['name']}")
            
        except Exception as e:
            print(f"❌ Error storing trace data for {agent_trace['name']}: {e}")

    def start_agent_execution_monitoring(self, agent_name: str, run_id: str) -> str:
        """Start monitoring a specific agent execution"""
        try:
            monitor = AgentExecutionMonitor(agent_name, run_id, self.agent_timeout)
            monitor.start_monitoring()
            
            with self.monitor_lock:
                self.execution_monitors[monitor.execution_id] = monitor
            
            # Log monitoring start
            self._log_monitoring_event(run_id, agent_name, 'MONITORING_STARTED', {
                'execution_id': monitor.execution_id,
                'timeout_threshold': self.agent_timeout
            })
            
            return monitor.execution_id
            
        except Exception as e:
            print(f"❌ Error starting monitoring for {agent_name}: {e}")
            return None
    
    def check_agent_execution_status(self, execution_id: str) -> Dict:
        """Check the current status of an agent execution"""
        try:
            with self.monitor_lock:
                monitor = self.execution_monitors.get(execution_id)
            
            if not monitor:
                return {
                    'success': False,
                    'error': 'Execution monitor not found',
                    'status': 'UNKNOWN'
                }
            
            # Check for timeout
            if monitor.check_timeout():
                self._log_monitoring_event(monitor.run_id, monitor.agent_name, 'TIMEOUT_DETECTED', {
                    'execution_id': execution_id,
                    'elapsed_time': time.time() - monitor.start_time
                })
            
            return {
                'success': True,
                'status': monitor.get_status_summary()
            }
            
        except Exception as e:
            print(f"❌ Error checking execution status for {execution_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'status': 'ERROR'
            }
    
    def handle_agent_timeout(self, execution_id: str) -> None:
        """Handle agent timeout with automatic cleanup"""
        try:
            with self.monitor_lock:
                monitor = self.execution_monitors.get(execution_id)
            
            if monitor:
                monitor.mark_completed(False, f"Timeout after {self.agent_timeout} seconds")
                
                # Log timeout handling
                self._log_monitoring_event(monitor.run_id, monitor.agent_name, 'TIMEOUT_HANDLED', {
                    'execution_id': execution_id,
                    'timeout_duration': self.agent_timeout,
                    'actual_duration': time.time() - monitor.start_time
                })
                
                # Update agent status
                self.update_agent_status(
                    monitor.run_id, 
                    monitor.agent_name, 
                    "TIMEOUT",
                    execution_time=time.time() - monitor.start_time,
                    error=f"Agent timed out after {self.agent_timeout} seconds"
                )
                
                print(f"🔧 Handled timeout for {monitor.agent_name}")
            
        except Exception as e:
            print(f"❌ Error handling timeout for {execution_id}: {e}")
    
    def log_agent_error(self, agent_name: str, error: Exception, run_id: str = None, 
                       execution_id: str = None) -> None:
        """Log agent error with categorization and detailed information"""
        try:
            error_str = str(error)
            error_category = self._categorize_agent_error(error_str)
            
            error_details = {
                'agent_name': agent_name,
                'error_message': error_str,
                'error_category': error_category,
                'error_type': type(error).__name__,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            if execution_id:
                error_details['execution_id'] = execution_id
                
                # Update monitor if exists
                with self.monitor_lock:
                    monitor = self.execution_monitors.get(execution_id)
                    if monitor:
                        monitor.mark_completed(False, error_str)
            
            # Store error in DynamoDB for analysis
            if run_id:
                self._store_agent_error(run_id, agent_name, error_details)
                
                # Log monitoring event
                self._log_monitoring_event(run_id, agent_name, 'ERROR_LOGGED', error_details)
            
            print(f"📝 Logged error for {agent_name}: {error_category} - {error_str}")
            
        except Exception as e:
            print(f"❌ Error logging agent error for {agent_name}: {e}")
    
    def _categorize_agent_error(self, error_str: str) -> str:
        """Categorize agent errors for better analysis"""
        error_lower = error_str.lower()
        
        if 'timeout' in error_lower:
            return 'TIMEOUT_ERROR'
        elif 'throttl' in error_lower or 'rate limit' in error_lower:
            return 'THROTTLING_ERROR'
        elif 'bedrock' in error_lower:
            return 'BEDROCK_API_ERROR'
        elif 'model' in error_lower or 'anthropic' in error_lower:
            return 'MODEL_ERROR'
        elif 'json' in error_lower or 'parse' in error_lower:
            return 'PARSING_ERROR'
        elif 'network' in error_lower or 'connection' in error_lower:
            return 'NETWORK_ERROR'
        elif 'permission' in error_lower or 'access' in error_lower:
            return 'PERMISSION_ERROR'
        elif 'validation' in error_lower:
            return 'VALIDATION_ERROR'
        else:
            return 'EXECUTION_ERROR'
    
    def _log_monitoring_event(self, run_id: str, agent_name: str, event_type: str, details: Dict):
        """Log monitoring events for debugging and analysis"""
        try:
            event_record = {
                'pk': {'S': f'monitoring_event'},
                'sk': {'S': f'{run_id}#{agent_name}#{datetime.utcnow().isoformat()}'},
                'runId': {'S': run_id},
                'agentName': {'S': agent_name},
                'eventType': {'S': event_type},
                'eventDetails': {'S': json.dumps(details, ensure_ascii=False)},
                'timestamp': {'S': datetime.utcnow().isoformat()},
                'expiresAt': {'N': str(int(time.time()) + 86400)},  # 24 hour TTL
                'gsi1pk': {'S': f'monitoring#{run_id}'},
                'gsi1sk': {'S': datetime.utcnow().isoformat()}
            }
            
            dynamodb.put_item(TableName=self.curio_table, Item=event_record)
            
        except Exception as e:
            print(f"❌ Error logging monitoring event: {e}")
    
    def _store_agent_error(self, run_id: str, agent_name: str, error_details: Dict):
        """Store agent error details for analysis"""
        try:
            error_record = {
                'pk': {'S': f'agent_error'},
                'sk': {'S': f'{run_id}#{agent_name}#{datetime.utcnow().isoformat()}'},
                'runId': {'S': run_id},
                'agentName': {'S': agent_name},
                'errorCategory': {'S': error_details['error_category']},
                'errorMessage': {'S': error_details['error_message']},
                'errorType': {'S': error_details['error_type']},
                'errorDetails': {'S': json.dumps(error_details, ensure_ascii=False)},
                'timestamp': {'S': error_details['timestamp']},
                'expiresAt': {'N': str(int(time.time()) + 86400)},  # 24 hour TTL
                'gsi1pk': {'S': f'errors#{run_id}'},
                'gsi1sk': {'S': error_details['timestamp']}
            }
            
            dynamodb.put_item(TableName=self.curio_table, Item=error_record)
            
        except Exception as e:
            print(f"❌ Error storing agent error: {e}")
    
    def get_monitoring_summary(self, run_id: str) -> Dict:
        """Get comprehensive monitoring summary for a run"""
        try:
            active_monitors = []
            completed_monitors = []
            
            with self.monitor_lock:
                for execution_id, monitor in self.execution_monitors.items():
                    if monitor.run_id == run_id:
                        status_summary = monitor.get_status_summary()
                        if monitor.status in ['RUNNING', 'STARTING']:
                            active_monitors.append(status_summary)
                        else:
                            completed_monitors.append(status_summary)
            
            return {
                'run_id': run_id,
                'active_monitors': active_monitors,
                'completed_monitors': completed_monitors,
                'total_monitors': len(active_monitors) + len(completed_monitors),
                'monitoring_summary': {
                    'active_count': len(active_monitors),
                    'completed_count': len(completed_monitors),
                    'timeout_risks': sum(1 for m in active_monitors if m.get('is_timeout_risk', False))
                },
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error getting monitoring summary: {e}")
            return {
                'run_id': run_id,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _execute_agents_parallel(self, run_id: str, agent_configs: List[tuple]) -> Dict:
        """Execute multiple agents in parallel using ThreadPoolExecutor"""
        results = {}
        
        def execute_single_agent(agent_config):
            agent_name, agent_input = agent_config
            execution_id = self.start_agent_execution_monitoring(agent_name, run_id)
            
            try:
                result = self.execute_agent_with_retry(
                    agent_name,
                    agent_input['prompt'],
                    context=agent_input['context'],
                    run_id=run_id
                )
                
                agent_result = {
                    'success': result.success,
                    'content': result.content,
                    'error': result.error,
                    'execution_time': result.execution_time,
                    'retry_count': result.retry_count
                }
                
                # Log comprehensive decision data
                self.log_agent_decision(run_id, agent_name, agent_input, agent_result)
                
                return agent_name.lower(), agent_result
                
            except Exception as e:
                self.log_agent_error(agent_name, e, run_id, execution_id)
                return agent_name.lower(), {
                    'success': False,
                    'content': None,
                    'error': str(e),
                    'execution_time': 0,
                    'retry_count': 0
                }
        
        try:
            # Use ThreadPoolExecutor for parallel execution
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                # Submit all agents for parallel execution
                future_to_agent = {
                    executor.submit(execute_single_agent, config): config[0] 
                    for config in agent_configs
                }
                
                # Collect results as they complete
                for future in concurrent.futures.as_completed(future_to_agent, timeout=self.agent_timeout * 2):
                    agent_name = future_to_agent[future]
                    try:
                        agent_key, result = future.result()
                        results[agent_key] = result
                        print(f"✅ Parallel execution completed for {agent_name}")
                    except Exception as e:
                        print(f"❌ Parallel execution failed for {agent_name}: {e}")
                        results[agent_name.lower()] = {
                            'success': False,
                            'content': None,
                            'error': str(e),
                            'execution_time': 0,
                            'retry_count': 0
                        }
                        
        except concurrent.futures.TimeoutError:
            print("⏰ Parallel execution timed out, some agents may not have completed")
            # Fill in missing results with timeout errors
            for agent_name, _ in agent_configs:
                if agent_name.lower() not in results:
                    results[agent_name.lower()] = {
                        'success': False,
                        'content': None,
                        'error': 'Parallel execution timeout',
                        'execution_time': self.agent_timeout * 2,
                        'retry_count': 0
                    }
        
        return results
    
    def _execute_agents_sequential(self, run_id: str, curator_result: Dict) -> Dict:
        """Execute agents sequentially as fallback"""
        results = {}
        
        # Agent 3: Script Generator
        execution_id = self.start_agent_execution_monitoring("SCRIPT_GENERATOR", run_id)
        script_input = {
            'prompt': "Create an engaging 90-second news script with millennial tone using the curated stories.",
            'context': {
                'stories': curator_result.get('content', '[]'),
                'tone': 'millennial with phrases like honestly, lowkey, ngl'
            }
        }
        
        script_result = self.execute_agent_with_retry(
            "SCRIPT_GENERATOR",
            script_input['prompt'],
            context=script_input['context'],
            run_id=run_id
        )
        results['script_generator'] = {
            'success': script_result.success,
            'content': script_result.content,
            'error': script_result.error,
            'execution_time': script_result.execution_time,
            'retry_count': script_result.retry_count
        }
        self.log_agent_decision(run_id, "SCRIPT_GENERATOR", script_input, results['script_generator'])
        
        # Agent 4: Favorite Selector
        execution_id = self.start_agent_execution_monitoring("FAVORITE_SELECTOR", run_id)
        favorite_input = {
            'prompt': "From the curated stories, identify the most fascinating one with 'wow factor' that will spark curiosity and conversation.",
            'context': {'curated_stories': curator_result.get('content', '[]')}
        }
        
        favorite_result = self.execute_agent_with_retry(
            "FAVORITE_SELECTOR",
            favorite_input['prompt'],
            context=favorite_input['context'],
            run_id=run_id
        )
        results['favorite_selector'] = {
            'success': favorite_result.success,
            'content': favorite_result.content,
            'error': favorite_result.error,
            'execution_time': favorite_result.execution_time,
            'retry_count': favorite_result.retry_count
        }
        self.log_agent_decision(run_id, "FAVORITE_SELECTOR", favorite_input, results['favorite_selector'])
        
        # Agent 5: Media Enhancer
        execution_id = self.start_agent_execution_monitoring("MEDIA_ENHANCER", run_id)
        media_input = {
            'prompt': "Enhance the news stories with visual elements, accessibility features, and social media optimization recommendations.",
            'context': {
                'stories': curator_result.get('content', '[]')
            }
        }
        
        media_result = self.execute_agent_with_retry(
            "MEDIA_ENHANCER",
            media_input['prompt'],
            context=media_input['context'],
            run_id=run_id
        )
        results['media_enhancer'] = {
            'success': media_result.success,
            'content': media_result.content,
            'error': media_result.error,
            'execution_time': media_result.execution_time,
            'retry_count': media_result.retry_count
        }
        self.log_agent_decision(run_id, "MEDIA_ENHANCER", media_input, results['media_enhancer'])
        
        # Agent 6: Weekend Events
        execution_id = self.start_agent_execution_monitoring("WEEKEND_EVENTS", run_id)
        weekend_input = {
            'prompt': "Curate weekend cultural recommendations including BookTok trends, streaming releases, local events, and social media phenomena for Gen Z/Millennial audiences.",
            'context': {
                'current_trends': 'Focus on books, movies, events, and cultural activities',
                'target_audience': 'Gen Z and Millennial interests'
            }
        }
        
        weekend_result = self.execute_agent_with_retry(
            "WEEKEND_EVENTS",
            weekend_input['prompt'],
            context=weekend_input['context'],
            run_id=run_id
        )
        results['weekend_events'] = {
            'success': weekend_result.success,
            'content': weekend_result.content,
            'error': weekend_result.error,
            'execution_time': weekend_result.execution_time,
            'retry_count': weekend_result.retry_count
        }
        self.log_agent_decision(run_id, "WEEKEND_EVENTS", weekend_input, results['weekend_events'])
        
        return results

    def invoke_bedrock_agent(self, agent_name: str, prompt: str, context: Dict = None) -> Dict:
        """Invoke a specialized Bedrock agent with comprehensive logging and validation"""
        start_time = datetime.utcnow()
        
        try:
            # Validate inputs
            if not agent_name or not prompt:
                result = {
                    'success': False,
                    'error': 'Invalid agent_name or prompt',
                    'agent': agent_name,
                    'timestamp': datetime.utcnow().isoformat()
                }
                return result
            
            # Create agent-specific prompt
            system_prompt = self.get_agent_system_prompt(agent_name)
            
            # Safely serialize context
            context_str = 'None'
            if context:
                try:
                    context_str = json.dumps(context, ensure_ascii=False)
                except (TypeError, ValueError) as e:
                    print(f"❌ Error serializing context for {agent_name}: {e}")
                    context_str = 'Context serialization failed'
            
            full_prompt = f"{system_prompt}\n\nContext: {context_str}\n\nTask: {prompt}"
            
            # Limit prompt length to avoid Bedrock limits
            original_length = len(full_prompt)
            if len(full_prompt) > 8000:
                print(f"⚠️ Prompt too long for {agent_name}, truncating...")
                full_prompt = full_prompt[:8000] + "... [truncated]"
            
            processing_details = {
                'model': 'anthropic.claude-3-haiku-20240307-v1:0',
                'promptLength': original_length,
                'truncated': original_length > 8000,
                'temperature': 0.1,
                'maxTokens': 1500  # Increased for better JSON responses
            }
            
            try:
                # Invoke Bedrock with optimized settings for JSON responses
                response = bedrock.invoke_model(
                    modelId='anthropic.claude-3-haiku-20240307-v1:0',
                    body=json.dumps({
                        'anthropic_version': 'bedrock-2023-05-31',
                        'max_tokens': 1500,  # Increased for complete JSON responses
                        'temperature': 0.1,  # Lower temperature for more consistent JSON
                        'messages': [
                            {
                                'role': 'user',
                                'content': full_prompt
                            }
                        ]
                    })
                )
            except Exception as e:
                print(f"❌ Bedrock API error for {agent_name}: {e}")
                result = {
                    'success': False,
                    'error': f'Bedrock API error: {str(e)}',
                    'agent': agent_name,
                    'timestamp': datetime.utcnow().isoformat()
                }
                return result
            
            try:
                result = json.loads(response['body'].read())
                content = result.get('content', [{}])[0].get('text', '')
                
                if not content:
                    result = {
                        'success': False,
                        'error': 'Empty response from Bedrock',
                        'agent': agent_name,
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    return result
                
                # Validate and clean the response for JSON-expecting agents
                validated_content = self._validate_agent_response(agent_name, content)
                
                result = {
                    'success': True,
                    'content': validated_content,
                    'agent': agent_name,
                    'timestamp': datetime.utcnow().isoformat(),
                    'raw_content': content  # Keep original for debugging
                }
                
                return result
                
            except (json.JSONDecodeError, KeyError, IndexError) as e:
                print(f"❌ Error parsing Bedrock response for {agent_name}: {e}")
                result = {
                    'success': False,
                    'error': f'Response parsing error: {str(e)}',
                    'agent': agent_name,
                    'timestamp': datetime.utcnow().isoformat()
                }
                return result
            
        except Exception as e:
            print(f"❌ Unexpected error invoking {agent_name}: {e}")
            import traceback
            traceback.print_exc()
            result = {
                'success': False,
                'error': f'Unexpected error: {str(e)}',
                'agent': agent_name,
                'timestamp': datetime.utcnow().isoformat()
            }
            return result
    
    def _validate_agent_response(self, agent_name: str, content: str) -> str:
        """Validate and clean agent responses, especially for JSON-expecting agents"""
        try:
            # For agents that should return JSON, validate and clean the response
            json_agents = ['NEWS_FETCHER', 'CONTENT_CURATOR', 'FAVORITE_SELECTOR', 'MEDIA_ENHANCER', 'WEEKEND_EVENTS']
            
            if agent_name in json_agents:
                # Try to extract JSON from the response
                content = content.strip()
                
                # Look for JSON content within the response
                import re
                
                # Try to find JSON objects or arrays
                json_patterns = [
                    r'\{.*\}',  # JSON object
                    r'\[.*\]'   # JSON array
                ]
                
                for pattern in json_patterns:
                    match = re.search(pattern, content, re.DOTALL)
                    if match:
                        json_candidate = match.group()
                        try:
                            # Validate it's proper JSON
                            json.loads(json_candidate)
                            print(f"✅ Extracted valid JSON for {agent_name}")
                            return json_candidate
                        except json.JSONDecodeError:
                            continue
                
                # If no valid JSON found, create fallback based on agent type
                print(f"⚠️ No valid JSON found for {agent_name}, creating fallback")
                return self._create_fallback_response(agent_name, content)
            
            # For non-JSON agents (like SCRIPT_GENERATOR), return as-is
            return content
            
        except Exception as e:
            print(f"❌ Error validating response for {agent_name}: {e}")
            return content
    
    def _create_fallback_response(self, agent_name: str, original_content: str) -> str:
        """Create fallback JSON responses when agent doesn't return valid JSON"""
        try:
            if agent_name == 'NEWS_FETCHER':
                return json.dumps([{
                    "title": "Breaking News Update",
                    "summary": "Latest news curated by AI agents",
                    "category": "GENERAL",
                    "relevance_score": 0.8,
                    "source": "AI Curated"
                }])
            
            elif agent_name == 'CONTENT_CURATOR':
                return json.dumps([{
                    "title": "Curated News Story",
                    "summary": "Selected for relevance to Gen Z/Millennial audiences",
                    "category": "GENERAL",
                    "relevance_score": 0.85,
                    "source": "Curated",
                    "selection_reason": "Selected by AI for audience relevance"
                }])
            
            elif agent_name == 'FAVORITE_SELECTOR':
                return json.dumps({
                    "selected_story": {
                        "title": "Fascinating Discovery",
                        "summary": "An interesting development worth sharing",
                        "category": "SCIENCE",
                        "wow_factor": "This discovery could change how we think about the world"
                    },
                    "reasoning": "This story was selected for its potential to spark curiosity and generate conversation among young adults."
                })
            
            elif agent_name == 'MEDIA_ENHANCER':
                return json.dumps({
                    "stories": [{
                        "title": "Enhanced Story",
                        "media_recommendations": {
                            "images": [{
                                "url": "https://source.unsplash.com/800x400/?news,modern",
                                "alt_text": "News story illustration",
                                "caption": "Visual enhancement for story"
                            }],
                            "videos": [{
                                "url": "https://www.youtube.com/embed/dQw4w9WgXcQ",
                                "caption": "Related video content"
                            }],
                            "social_media_optimization": {
                                "hashtags": ["#news", "#trending", "#update"],
                                "suggested_platforms": ["Twitter", "Instagram"],
                                "engagement_tips": "Share with compelling visuals"
                            }
                        },
                        "accessibility_features": {
                            "screen_reader_summary": "Accessible news content",
                            "high_contrast_available": True,
                            "keyboard_navigation": True
                        }
                    }],
                    "overall_visual_theme": {
                        "color_scheme": "Modern, accessible colors",
                        "typography": "Clean, readable fonts",
                        "layout_principles": "Mobile-first design"
                    }
                })
            
            elif agent_name == 'WEEKEND_EVENTS':
                return json.dumps({
                    "books": [{
                        "title": "Trending Book",
                        "author": "Popular Author",
                        "description": "A book that's gaining popularity among young readers",
                        "genre": "Fiction",
                        "trending_reason": "Social media buzz"
                    }],
                    "movies_and_shows": [{
                        "title": "Must-Watch Show",
                        "platform": "Streaming",
                        "description": "A show worth binge-watching this weekend",
                        "genre": "Drama",
                        "release_info": "Recently released"
                    }],
                    "events": [{
                        "name": "Weekend Activity",
                        "location": "Check local listings",
                        "date": "This weekend",
                        "description": "Fun activities for young adults",
                        "link": "https://example.com"
                    }],
                    "cultural_insights": {
                        "booktok_trends": "Romance and fantasy novels continue to dominate",
                        "social_media_phenomena": "Short-form video content drives cultural trends",
                        "streaming_highlights": "Genre-blending content appeals to diverse audiences"
                    }
                })
            
            else:
                return original_content
                
        except Exception as e:
            print(f"❌ Error creating fallback for {agent_name}: {e}")
            return original_content
    
    def get_agent_system_prompt(self, agent_name: str) -> str:
        """Get the specialized system prompt for each agent"""
        prompts = {
            "NEWS_FETCHER": """You are the News Fetcher Agent, specialized in gathering and filtering news for Gen Z/Millennial audiences. 
            Your role is to identify the most relevant, engaging, and trending news stories from multiple sources.
            Focus on: Technology, culture, politics that affects young adults, science breakthroughs, and viral trends.
            
            IMPORTANT: You must respond with ONLY a valid JSON array. No other text or explanation.
            
            Format your response exactly like this:
            [
              {
                "title": "Story title here",
                "summary": "Brief engaging summary",
                "category": "TECHNOLOGY|CULTURE|POLITICS|SCIENCE|GENERAL",
                "relevance_score": 0.95,
                "source": "Source name"
              }
            ]""",
            
            "CONTENT_CURATOR": """You are the Content Curator Agent, expert at selecting the perfect mix of news stories.
            Your role is to choose exactly 5 stories that create a balanced, engaging briefing.
            Ensure diversity across categories and optimize for engagement. Consider the narrative flow.
            
            IMPORTANT: You must respond with ONLY a valid JSON array of exactly 5 stories. No other text.
            
            Format your response exactly like this:
            [
              {
                "title": "Selected story title",
                "summary": "Engaging summary for young adults",
                "category": "TECHNOLOGY|CULTURE|POLITICS|SCIENCE|GENERAL",
                "relevance_score": 0.92,
                "source": "Source name",
                "selection_reason": "Why this story was chosen"
              }
            ]""",
            
            "FAVORITE_SELECTOR": """You are the Favorite Selector Agent, specialized in finding the most interesting story of the day.
            Your role is to identify content that sparks curiosity - university research, science discoveries, cultural phenomena.
            Look for "wow, that's actually really cool!" moments that people will want to share.
            
            IMPORTANT: You must respond with ONLY a valid JSON object. No other text or explanation.
            
            Format your response exactly like this:
            {
              "selected_story": {
                "title": "Story title from the provided stories",
                "summary": "Brief summary of why this is fascinating",
                "category": "TECHNOLOGY|CULTURE|POLITICS|SCIENCE|GENERAL",
                "wow_factor": "Specific reason this will make people say 'wow, that's actually really cool!'"
              },
              "reasoning": "Detailed explanation of why this story was selected as the most fascinating, focusing on its potential to spark curiosity and conversation. Mention specific elements that make it shareable and engaging for Gen Z/Millennial audiences."
            }""",
            
            "SCRIPT_GENERATOR": """You are the Script Generator Agent, expert at creating engaging 90-second news scripts for Gen Z/Millennial audiences.

CRITICAL REQUIREMENTS:
- Write EXACTLY 225-250 words (90 seconds when read aloud)
- Use millennial language: "honestly", "lowkey", "ngl" (not gonna lie), "get this", "wild", "plot twist"
- Conversational tone like talking to college friends
- NO source attributions (don't say "CNN reports" or "according to BBC")
- Use contractions: "we're", "it's", "can't", "won't"

STRUCTURE (must follow exactly):
1. Opening: "Alright, let's dive into what's happening today..."
2. Main story (biggest news): 2-3 sentences with details
3. Quick hits: 2-3 more stories, 1-2 sentences each
4. Favorite/interesting story: "And honestly, this next one is pretty wild..." 
5. Closing: "And that's what's moving the world today. Stay curious!"

TONE EXAMPLES:
- "Honestly, this is kind of a big deal..."
- "Get this - apparently..."
- "Lowkey, this is actually pretty important..."
- "Ngl, I didn't see this coming..."
- "Plot twist: it turns out..."
- "Wild, right?"

IMPORTANT: Respond with ONLY the complete script text. No JSON, no formatting, no explanations - just the script that will be read aloud. Make it exactly 90 seconds worth of content.""",
            
            "MEDIA_ENHANCER": """You are the Media Enhancer Agent, specialized in visual content curation and accessibility.
            Your role is to enhance news stories with visual elements, accessibility features, and social media optimization.
            Focus on creating engaging visual experiences that are accessible to all users.
            
            IMPORTANT: You must respond with ONLY a valid JSON object. No other text or explanation.
            
            For images, use these real Unsplash URLs based on story content:
            - Technology: https://source.unsplash.com/800x400/?technology,computer,ai
            - Business: https://source.unsplash.com/800x400/?business,office,finance  
            - Science: https://source.unsplash.com/800x400/?science,laboratory,research
            - Politics: https://source.unsplash.com/800x400/?government,politics,law
            - Culture: https://source.unsplash.com/800x400/?culture,art,entertainment
            - General: https://source.unsplash.com/800x400/?news,abstract,modern
            
            Format your response exactly like this:
            {
              "stories": [
                {
                  "title": "Story title from provided stories",
                  "media_recommendations": {
                    "images": [
                      {
                        "url": "https://source.unsplash.com/800x400/?[relevant-keywords]",
                        "alt_text": "Descriptive alt text for accessibility",
                        "caption": "Brief caption explaining the image relevance"
                      }
                    ],
                    "videos": [
                      {
                        "url": "https://www.youtube.com/embed/dQw4w9WgXcQ",
                        "caption": "Suggested video content related to the story",
                        "thumbnail": "https://source.unsplash.com/400x300/?video,media"
                      }
                    ],
                    "social_media_optimization": {
                      "hashtags": ["#relevant", "#hashtags", "#for", "#story"],
                      "suggested_platforms": ["Twitter", "Instagram", "TikTok"],
                      "engagement_tips": "Tips for maximizing social media engagement"
                    }
                  },
                  "accessibility_features": {
                    "screen_reader_summary": "Brief summary optimized for screen readers",
                    "high_contrast_available": true,
                    "keyboard_navigation": true
                  }
                }
              ],
              "overall_visual_theme": {
                "color_scheme": "Modern, accessible color palette",
                "typography": "Clean, readable fonts",
                "layout_principles": "Mobile-first, accessible design"
              }
            }""",
            
            "WEEKEND_EVENTS": """You are the Weekend Events Agent, expert at curating lifestyle and cultural content.
            Your role is to recommend books, movies, events, and trending cultural phenomena for Gen Z/Millennial audiences.
            Focus on BookTok trends, streaming releases, local events, and social media phenomena.
            
            IMPORTANT: You must respond with ONLY a valid JSON object. No other text or explanation.
            
            Format your response exactly like this:
            {
              "books": [
                {
                  "title": "Book title",
                  "author": "Author name",
                  "description": "Why this book is trending on BookTok or relevant to young adults",
                  "genre": "Romance|Thriller|Fantasy|Non-fiction|etc",
                  "trending_reason": "Specific reason it's popular (e.g., 'Viral on BookTok', 'Award winner')"
                }
              ],
              "movies_and_shows": [
                {
                  "title": "Movie/Show title",
                  "platform": "Netflix|Hulu|HBO|Disney+|Theater|etc",
                  "description": "Brief description and why it's worth watching",
                  "genre": "Comedy|Drama|Thriller|Documentary|etc",
                  "release_info": "New release|Trending|Classic worth revisiting"
                }
              ],
              "events": [
                {
                  "name": "Event name",
                  "location": "Location or 'Virtual' or 'Nationwide'",
                  "date": "Date range or 'Ongoing'",
                  "description": "What makes this event interesting for young adults",
                  "link": "https://example.com or 'Check local listings'"
                }
              ],
              "cultural_insights": {
                "booktok_trends": "Current BookTok trends and popular genres",
                "social_media_phenomena": "What's trending on social media that young adults care about",
                "streaming_highlights": "Notable streaming content and platform trends"
              }
            }"""
        }
        
        return prompts.get(agent_name, "You are a helpful AI assistant.")
    
    def fetch_current_news(self) -> List[Dict]:
        """Fetch current news from NewsAPI and RSS feeds"""
        try:
            news_items = []
            
            # 1. Try NewsAPI first (primary source with provided key)
            if NEWS_API_KEY:
                print(f"🔑 Using NewsAPI with key: {NEWS_API_KEY[:8]}...")
                newsapi_items = self._fetch_from_newsapi()
                news_items.extend(newsapi_items)
                print(f"📰 NewsAPI returned {len(newsapi_items)} articles")
            
            # 2. Supplement with RSS feeds for diversity
            rss_items = self._fetch_from_rss()
            news_items.extend(rss_items)
            print(f"📡 RSS feeds returned {len(rss_items)} articles")
            
            # 3. Remove duplicates and limit results
            unique_items = self._deduplicate_news(news_items)
            print(f"✨ Total unique articles: {len(unique_items)}")
            
            # If still no news, provide fallback
            if not unique_items:
                unique_items = self._get_fallback_news()
                print("⚠️ Using fallback news content")
            
            return unique_items[:15]  # Return top 15 for agent processing
            
        except Exception as e:
            print(f"❌ Error in fetch_current_news: {e}")
            return self._get_fallback_news()
    
    def _fetch_from_newsapi(self) -> List[Dict]:
        """Fetch news from NewsAPI.org using the provided API key"""
        try:
            # Get top headlines
            headlines_url = f"{NEWS_API_BASE_URL}/top-headlines"
            headlines_params = {
                'apiKey': NEWS_API_KEY,
                'language': 'en',
                'country': 'us',
                'pageSize': 20,
                'category': 'general'
            }
            
            print(f"🌐 Fetching headlines from NewsAPI...")
            response = requests.get(headlines_url, params=headlines_params, timeout=10)
            response.raise_for_status()
            
            headlines_data = response.json()
            news_items = []
            
            if headlines_data.get('status') == 'ok':
                for article in headlines_data.get('articles', []):
                    if self._is_valid_article(article):
                        news_items.append({
                            'title': article.get('title', ''),
                            'summary': article.get('description', ''),
                            'link': article.get('url', ''),
                            'published': article.get('publishedAt', ''),
                            'source': article.get('source', {}).get('name', 'NewsAPI'),
                            'category': self._categorize_article(article.get('title', ''), article.get('description', '')),
                            'image': article.get('urlToImage', '')
                        })
            
            # Fetch diverse categories for balanced news
            categories = ['business', 'science', 'health', 'sports']
            for category in categories:
                cat_url = f"{NEWS_API_BASE_URL}/top-headlines"
                cat_params = {
                    'apiKey': NEWS_API_KEY,
                    'language': 'en',
                    'category': category,
                    'pageSize': 5  # Fewer per category for diversity
                }
                
                print(f"📰 Fetching {category} news from NewsAPI...")
                try:
                    cat_response = requests.get(cat_url, params=cat_params, timeout=10)
                    cat_response.raise_for_status()
                    
                    cat_data = cat_response.json()
                    if cat_data.get('status') == 'ok':
                        for article in cat_data.get('articles', []):
                            if self._is_valid_article(article):
                                news_items.append({
                                    'title': article.get('title', ''),
                                    'summary': article.get('description', ''),
                                    'link': article.get('url', ''),
                                    'published': article.get('publishedAt', ''),
                                    'source': article.get('source', {}).get('name', 'NewsAPI'),
                                    'category': category,
                                    'image': article.get('urlToImage', '')
                                })
                except Exception as e:
                    print(f"Error fetching {category} news: {e}")
                    continue
            
            # Also search for breaking tech news (AWS, major outages, etc.)
            breaking_url = f"{NEWS_API_BASE_URL}/everything"
            breaking_params = {
                'apiKey': NEWS_API_KEY,
                'q': 'AWS outage OR Amazon down OR Google down OR Microsoft outage OR "service disruption"',
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': 5
            }
            
            print(f"🚨 Fetching breaking tech news from NewsAPI...")
            try:
                breaking_response = requests.get(breaking_url, params=breaking_params, timeout=10)
                breaking_response.raise_for_status()
                
                breaking_data = breaking_response.json()
                if breaking_data.get('status') == 'ok':
                    for article in breaking_data.get('articles', []):
                        if self._is_valid_article(article):
                            news_items.append({
                                'title': article.get('title', ''),
                                'summary': article.get('description', ''),
                                'link': article.get('url', ''),
                                'published': article.get('publishedAt', ''),
                                'source': article.get('source', {}).get('name', 'NewsAPI'),
                                'category': 'technology',
                                'image': article.get('urlToImage', '')
                            })
            except Exception as e:
                print(f"Error fetching breaking news: {e}")
            
            return news_items
            
        except requests.exceptions.RequestException as e:
            print(f"❌ NewsAPI request error: {e}")
            return []
        except Exception as e:
            print(f"❌ NewsAPI processing error: {e}")
            return []
    
    def _fetch_from_rss(self) -> List[Dict]:
        """Fetch news from RSS feeds as backup/supplement"""
        try:
            news_items = []
            
            # Curated RSS feeds for Gen Z/Millennial audiences
            rss_feeds = {
                'BBC News': 'https://feeds.bbci.co.uk/news/rss.xml',
                'Reuters': 'https://feeds.reuters.com/reuters/topNews',
                'TechCrunch': 'https://techcrunch.com/feed/',
                'The Verge': 'https://www.theverge.com/rss/index.xml',
                'Ars Technica': 'http://feeds.arstechnica.com/arstechnica/index',
                'NPR': 'https://feeds.npr.org/1001/rss.xml'
            }
            
            for source_name, feed_url in rss_feeds.items():
                try:
                    print(f"📡 Fetching RSS from {source_name}...")
                    feed = feedparser.parse(feed_url)
                    
                    for entry in feed.entries[:3]:  # Limit per feed
                        if hasattr(entry, 'title') and hasattr(entry, 'summary'):
                            news_items.append({
                                'title': entry.title,
                                'summary': entry.summary[:300],  # Limit length
                                'link': getattr(entry, 'link', ''),
                                'published': getattr(entry, 'published', ''),
                                'source': source_name,
                                'category': self._categorize_article(entry.title, entry.summary),
                                'image': ''
                            })
                            
                except Exception as e:
                    print(f"❌ RSS error for {source_name}: {e}")
                    continue
            
            return news_items
            
        except Exception as e:
            print(f"❌ RSS processing error: {e}")
            return []
    
    def _is_valid_article(self, article: Dict) -> bool:
        """Check if article has required fields and content"""
        title = article.get('title', '')
        description = article.get('description', '')
        
        # Filter out removed/deleted articles
        if '[Removed]' in title or not title or not description:
            return False
        
        # Ensure minimum content length
        if len(title) < 10 or len(description) < 30:
            return False
        
        return True
    
    def _categorize_article(self, title: str, description: str) -> str:
        """Categorize article based on content for Gen Z/Millennial relevance"""
        text = (title + " " + description).lower()
        
        # Technology & Digital Culture
        if any(word in text for word in ['tech', 'ai', 'artificial intelligence', 'software', 'app', 'digital', 'cyber', 'crypto', 'blockchain', 'social media', 'tiktok', 'instagram', 'twitter', 'meta', 'google', 'apple', 'microsoft']):
            return 'technology'
        
        # Politics & Social Issues (relevant to young adults)
        elif any(word in text for word in ['climate', 'environment', 'student loan', 'housing', 'rent', 'election', 'voting', 'rights', 'equality', 'justice', 'protest']):
            return 'politics'
        
        # Business & Economy (career/finance relevant)
        elif any(word in text for word in ['job', 'employment', 'salary', 'economy', 'inflation', 'market', 'stock', 'startup', 'company', 'business', 'finance']):
            return 'business'
        
        # Science & Health
        elif any(word in text for word in ['science', 'research', 'study', 'health', 'medical', 'vaccine', 'covid', 'mental health', 'wellness']):
            return 'science'
        
        # Culture & Entertainment
        elif any(word in text for word in ['music', 'movie', 'netflix', 'streaming', 'celebrity', 'culture', 'art', 'fashion', 'gaming', 'esports']):
            return 'culture'
        
        else:
            return 'general'
    
    def _deduplicate_news(self, news_items: List[Dict]) -> List[Dict]:
        """Remove duplicate articles based on title similarity"""
        unique_items = []
        seen_titles = set()
        
        for item in news_items:
            # Create a normalized title for comparison
            title_key = item['title'][:50].lower().strip()
            title_key = ''.join(c for c in title_key if c.isalnum() or c.isspace())
            
            if title_key not in seen_titles and len(title_key) > 10:
                seen_titles.add(title_key)
                unique_items.append(item)
        
        # Sort by relevance with balanced category representation
        def relevance_score(item):
            category = item.get('category', 'general')
            title = item.get('title', '').lower()
            
            score = 0
            # Balanced scoring - no category gets excessive preference
            if category in ['technology', 'science', 'politics', 'business']:
                score += 1
            elif category in ['culture', 'international']:
                score += 0.5
            
            # Boost major breaking news keywords
            breaking_keywords = ['outage', 'down', 'crash', 'breaking', 'emergency', 'alert', 'major', 'massive']
            for keyword in breaking_keywords:
                if keyword in title:
                    score += 2  # High priority for breaking news
            
            # Boost trending topics but with lower weight
            trending_keywords = ['ai', 'climate', 'crypto', 'streaming', 'gaming', 'aws', 'google', 'apple', 'microsoft']
            for keyword in trending_keywords:
                if keyword in title:
                    score += 0.5
            
            return score
        
        unique_items.sort(key=relevance_score, reverse=True)
        return unique_items
    
    def _get_fallback_news(self) -> List[Dict]:
        """Provide fallback news when all sources fail"""
        return [
            {
                'title': 'AI Technology Continues Rapid Development Across Industries',
                'summary': 'Artificial intelligence applications are expanding into new sectors, transforming how businesses operate and creating new opportunities for innovation.',
                'link': '',
                'published': datetime.utcnow().isoformat(),
                'source': 'Tech Analysis',
                'category': 'technology',
                'image': ''
            },
            {
                'title': 'Climate Action Initiatives Gain Momentum Among Young Adults',
                'summary': 'Environmental activism and sustainable practices are becoming increasingly important to Gen Z and Millennial demographics worldwide.',
                'link': '',
                'published': datetime.utcnow().isoformat(),
                'source': 'Environmental Report',
                'category': 'politics',
                'image': ''
            },
            {
                'title': 'Digital Culture Shapes Modern Communication Trends',
                'summary': 'Social media platforms and digital communication tools continue to evolve, influencing how people connect and share information.',
                'link': '',
                'published': datetime.utcnow().isoformat(),
                'source': 'Culture Watch',
                'category': 'culture',
                'image': ''
            }
        ]
    
    def orchestrate_agents(self, run_id: str) -> Dict:
        """Orchestrate all 6 agents with enhanced timeout handling and parallel execution"""
        try:
            results = {}
            
            print(f"🚀 Starting enhanced agent orchestration for run_id: {run_id}")
            
            # Phase 1: Sequential agents that depend on each other
            print("📰 Phase 1: News fetching and curation")
            
            # Agent 1: News Fetcher (Essential - must complete first)
            execution_id = self.start_agent_execution_monitoring("NEWS_FETCHER", run_id)
            
            # Get real news data for the agent to work with
            current_news = self.fetch_current_news()
            
            # Prepare input data for logging
            news_input = {
                'prompt': "Analyze these current news stories and select the most relevant ones for Gen Z/Millennial audiences. Focus on technology, culture, politics that affects young adults, science breakthroughs, and viral trends. Return a JSON array of the best stories with title, summary, category, and relevance_score.",
                'context': {'current_news': current_news}
            }
            
            news_result = self.execute_agent_with_retry(
                "NEWS_FETCHER",
                news_input['prompt'],
                context=news_input['context'],
                run_id=run_id
            )
            results['news_fetcher'] = {
                'success': news_result.success,
                'content': news_result.content,
                'error': news_result.error,
                'execution_time': news_result.execution_time,
                'retry_count': news_result.retry_count
            }
            
            # Log comprehensive decision data
            self.log_agent_decision(run_id, "NEWS_FETCHER", news_input, results['news_fetcher'])
            
            if not news_result.success:
                print(f"❌ News fetcher failed: {news_result.error}")
                # Continue with fallback data instead of failing completely
                fallback_content = '[{"title":"Tech Innovation Continues","summary":"Latest developments in technology","category":"TECHNOLOGY","relevance_score":0.9,"source":"Tech News"}]'
                results['news_fetcher'] = {
                    'success': True,
                    'content': fallback_content,
                    'error': None,
                    'execution_time': news_result.execution_time,
                    'retry_count': news_result.retry_count
                }
            
            # Agent 2: Content Curator (Essential - depends on news fetcher)
            execution_id = self.start_agent_execution_monitoring("CONTENT_CURATOR", run_id)
            
            curator_input = {
                'prompt': "Select the best 5 stories from the fetched news for a balanced, engaging briefing.",
                'context': {'news_stories': results['news_fetcher']['content']}
            }
            
            curator_result = self.execute_agent_with_retry(
                "CONTENT_CURATOR",
                curator_input['prompt'],
                context=curator_input['context'],
                run_id=run_id
            )
            results['content_curator'] = {
                'success': curator_result.success,
                'content': curator_result.content,
                'error': curator_result.error,
                'execution_time': curator_result.execution_time,
                'retry_count': curator_result.retry_count
            }
            
            # Log comprehensive decision data
            self.log_agent_decision(run_id, "CONTENT_CURATOR", curator_input, results['content_curator'])
            
            # Phase 2: Parallel execution of independent agents
            print("🔄 Phase 2: Parallel execution of independent agents")
            
            if self.parallel_execution_enabled:
                # Execute remaining agents in parallel using ThreadPoolExecutor
                parallel_agents = [
                    ("SCRIPT_GENERATOR", {
                        'prompt': "Create an engaging 90-second news script with millennial tone using the curated stories.",
                        'context': {
                            'stories': results['content_curator'].get('content', '[]'),
                            'tone': 'millennial with phrases like honestly, lowkey, ngl'
                        }
                    }),
                    ("FAVORITE_SELECTOR", {
                        'prompt': "From the curated stories, identify the most fascinating one with 'wow factor' that will spark curiosity and conversation.",
                        'context': {'curated_stories': results['content_curator'].get('content', '[]')}
                    }),
                    ("MEDIA_ENHANCER", {
                        'prompt': "Enhance the news stories with visual elements, accessibility features, and social media optimization recommendations.",
                        'context': {
                            'stories': results['content_curator'].get('content', '[]')
                        }
                    }),
                    ("WEEKEND_EVENTS", {
                        'prompt': "Curate weekend cultural recommendations including BookTok trends, streaming releases, local events, and social media phenomena for Gen Z/Millennial audiences.",
                        'context': {
                            'current_trends': 'Focus on books, movies, events, and cultural activities',
                            'target_audience': 'Gen Z and Millennial interests'
                        }
                    })
                ]
                
                # Execute agents in parallel
                parallel_results = self._execute_agents_parallel(run_id, parallel_agents)
                results.update(parallel_results)
                
            else:
                # Sequential execution fallback
                print("⚠️ Parallel execution disabled, running sequentially")
                results.update(self._execute_agents_sequential(run_id, results['content_curator']))
            
            # Phase 3: Audio generation (if script was successful)
            print("🎙️ Phase 3: Audio generation")
            if results.get('script_generator', {}).get('success') and self.audio_generator:
                self.update_agent_status(run_id, "AUDIO_GENERATOR", "RUNNING")
                print("🎙️ Generating audio with Polly...")
                
                script_content = results['script_generator']['content']
                # Clean up script if it contains JSON or extra formatting
                if script_content and script_content.startswith('{'):
                    try:
                        script_json = json.loads(script_content)
                        script_content = script_json.get('script', script_content)
                    except:
                        pass
                
                if script_content:
                    audio_result = self.audio_generator.generate_audio(script_content, run_id)
                    results['audio_generator'] = audio_result
                    
                    if audio_result.get('success'):
                        print(f"✅ Audio generated: {audio_result['audio_url']}")
                        self.update_agent_status(run_id, "AUDIO_GENERATOR", "COMPLETED")
                    else:
                        print(f"❌ Audio generation failed: {audio_result.get('error')}")
                        self.update_agent_status(run_id, "AUDIO_GENERATOR", "FAILED", error=audio_result.get('error'))
                else:
                    print("⚠️ No script content available for audio generation")
                    self.update_agent_status(run_id, "AUDIO_GENERATOR", "SKIPPED", error="No script content")
            else:
                print("⚠️ Skipping audio generation - script failed or audio generator not available")
                self.update_agent_status(run_id, "AUDIO_GENERATOR", "SKIPPED", error="Script failed or no audio generator")
            
            # Phase 4: Finalization and summary
            print("📊 Phase 4: Finalization and orchestration summary")
            
            # Get comprehensive orchestration summary
            orchestration_summary = self.get_orchestration_summary(run_id)
            monitoring_summary = self.get_monitoring_summary(run_id)
            
            # Finalize trace data
            if run_id in self.trace_data:
                self.trace_data[run_id]['status'] = 'COMPLETED'
                self.trace_data[run_id]['endTime'] = datetime.utcnow().isoformat()
                self.trace_data[run_id]['orchestration_summary'] = orchestration_summary
                self.trace_data[run_id]['monitoring_summary'] = monitoring_summary
                
                # Calculate total duration
                try:
                    start_time = datetime.fromisoformat(self.trace_data[run_id]['startTime'].replace('Z', '+00:00'))
                    end_time = datetime.fromisoformat(self.trace_data[run_id]['endTime'].replace('Z', '+00:00'))
                    total_duration = (end_time - start_time).total_seconds()
                    self.trace_data[run_id]['totalDuration'] = f"{total_duration:.1f}s"
                except:
                    self.trace_data[run_id]['totalDuration'] = "0.0s"
                
                # Store complete trace data
                self.store_complete_trace(run_id)
            
            # Determine overall success
            successful_agents = sum(1 for result in results.values() if result.get('success', False))
            total_agents = len(results)
            success_rate = successful_agents / total_agents if total_agents > 0 else 0
            
            overall_success = success_rate >= 0.5  # At least 50% of agents must succeed
            
            # Mark as completed with appropriate status
            final_status = "SUCCESS" if overall_success else "PARTIAL_SUCCESS"
            self.update_agent_status(run_id, "ORCHESTRATION", final_status, {
                'successful_agents': successful_agents,
                'total_agents': total_agents,
                'success_rate': round(success_rate * 100, 1)
            })
            
            print(f"🎯 Orchestration completed: {successful_agents}/{total_agents} agents successful ({success_rate*100:.1f}%)")
            
            return {
                'success': overall_success,
                'run_id': run_id,
                'results': results,
                'orchestration_summary': orchestration_summary,
                'monitoring_summary': monitoring_summary,
                'completed_at': datetime.utcnow().isoformat(),
                'trace_id': f"agents-{run_id}",
                'success_rate': success_rate,
                'successful_agents': successful_agents,
                'total_agents': total_agents
            }
            
        except Exception as e:
            print(f"❌ Critical orchestration error: {e}")
            import traceback
            traceback.print_exc()
            
            # Log error with comprehensive details
            self.log_agent_error("ORCHESTRATION", e, run_id)
            
            # Log error in trace data
            if run_id in self.trace_data:
                self.trace_data[run_id]['status'] = 'FAILED'
                self.trace_data[run_id]['error'] = str(e)
                self.trace_data[run_id]['endTime'] = datetime.utcnow().isoformat()
                self.store_complete_trace(run_id)
            
            # Get partial results summary
            orchestration_summary = self.get_orchestration_summary(run_id)
            monitoring_summary = self.get_monitoring_summary(run_id)
            
            self.update_agent_status(run_id, "ORCHESTRATION", "FAILED", {
                'error': str(e),
                'partial_results': len(results),
                'error_type': type(e).__name__
            })
            
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__,
                'run_id': run_id,
                'results': results,
                'orchestration_summary': orchestration_summary,
                'monitoring_summary': monitoring_summary,
                'failed_at': datetime.utcnow().isoformat()
            }

    def store_complete_trace(self, run_id: str):
        """Store complete trace data for the entire orchestration"""
        try:
            if run_id not in self.trace_data:
                return
            
            trace_data = self.trace_data[run_id]
            
            item = {
                'pk': {'S': f'complete_trace'},
                'sk': {'S': f'agents-{run_id}'},
                'traceId': {'S': f'agents-{run_id}'},
                'runId': {'S': run_id},
                'completeTrace': {'S': json.dumps(trace_data, ensure_ascii=False)},
                'status': {'S': trace_data['status']},
                'timestamp': {'S': trace_data.get('endTime', datetime.utcnow().isoformat())},
                'expiresAt': {'N': str(int(time.time()) + 86400)},  # 24 hour TTL
                'gsi1pk': {'S': f'trace_complete'},
                'gsi1sk': {'S': trace_data.get('endTime', datetime.utcnow().isoformat())}
            }
            
            dynamodb.put_item(TableName=self.curio_table, Item=item)
            print(f"✅ Stored complete trace data for run {run_id}")
            
        except Exception as e:
            print(f"❌ Error storing complete trace data for {run_id}: {e}")

    def get_trace_data(self, trace_id: str) -> Dict:
        """Retrieve comprehensive trace data for a specific trace ID"""
        try:
            # Try to get complete trace data first
            response = dynamodb.get_item(
                TableName=self.curio_table,
                Key={
                    'pk': {'S': 'complete_trace'},
                    'sk': {'S': trace_id}
                }
            )
            
            if 'Item' in response:
                trace_data = json.loads(response['Item']['completeTrace']['S'])
                return {
                    'success': True,
                    'trace': trace_data
                }
            
            # Fallback: try to reconstruct from individual agent traces
            run_id = trace_id.replace('agents-', '')
            
            # Query for all agent traces for this run
            response = dynamodb.query(
                TableName=self.curio_table,
                KeyConditionExpression='pk = :pk AND begins_with(sk, :sk_prefix)',
                ExpressionAttributeValues={
                    ':pk': {'S': 'trace'},
                    ':sk_prefix': {'S': f'{run_id}#'}
                }
            )
            
            if not response.get('Items'):
                return {
                    'success': False,
                    'error': 'Trace data not found'
                }
            
            # Reconstruct trace from individual agent data
            agents = []
            for item in response['Items']:
                agent_trace = json.loads(item['traceData']['S'])
                agents.append(agent_trace)
            
            # Sort agents by completion time
            agents.sort(key=lambda x: x.get('endTime', ''))
            
            reconstructed_trace = {
                'runId': run_id,
                'traceId': trace_id,
                'agents': agents,
                'status': 'COMPLETED' if all(a.get('status') == 'COMPLETED' for a in agents) else 'PARTIAL',
                'startTime': agents[0].get('startTime') if agents else datetime.utcnow().isoformat(),
                'endTime': agents[-1].get('endTime') if agents else datetime.utcnow().isoformat()
            }
            
            # Calculate total duration
            try:
                start_time = datetime.fromisoformat(reconstructed_trace['startTime'].replace('Z', '+00:00'))
                end_time = datetime.fromisoformat(reconstructed_trace['endTime'].replace('Z', '+00:00'))
                total_duration = (end_time - start_time).total_seconds()
                reconstructed_trace['totalDuration'] = f"{total_duration:.1f}s"
            except:
                reconstructed_trace['totalDuration'] = "0.0s"
            
            return {
                'success': True,
                'trace': reconstructed_trace
            }
            
        except Exception as e:
            print(f"❌ Error retrieving trace data for {trace_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }