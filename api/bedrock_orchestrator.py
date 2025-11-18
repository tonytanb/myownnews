"""
Lightweight Bedrock Agent Orchestrator for Curio News
Coordinates AWS Bedrock Agents working together in a multi-agent architecture
"""
import json
import boto3
import os
import time
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid

bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name='us-west-2')
ssm = boto3.client('ssm', region_name='us-west-2')
dynamodb = boto3.client('dynamodb', region_name='us-west-2')

class BedrockAgentOrchestrator:
    """
    Lightweight orchestrator that coordinates Bedrock agents
    Business logic resides in the agents, not in this code
    """
    
    def __init__(self):
        self.agent_ids = self._load_agent_ids()
        self.orchestration_trace = []
        self.session_id = f"session-{uuid.uuid4()}"
        self.table_name = os.getenv('CURIO_TABLE', 'CurioTable')
        self.performance_target = 10.0  # Target: sub-10-second execution
        self.agent_timeout = 30  # 30 seconds per agent max
    
    def _load_agent_ids(self) -> Dict[str, str]:
        """Load agent IDs and alias IDs from environment variables or Parameter Store"""
        agent_ids = {}
        self.agent_aliases = {}
        agent_names = ['content_curator', 'social_impact_analyzer', 'story_selector',
                       'script_writer', 'entertainment_curator', 'media_enhancer']
        
        for agent_name in agent_names:
            # Try environment variable first
            agent_id = os.getenv(f'BEDROCK_AGENT_{agent_name.upper()}_ID')
            
            # Try Parameter Store if not in env
            if not agent_id:
                try:
                    response = ssm.get_parameter(
                        Name=f'/curio-news/bedrock-agents/{agent_name}/agent-id',
                        WithDecryption=True
                    )
                    agent_id = response['Parameter']['Value']
                except Exception as e:
                    print(f"⚠️  Could not load {agent_name}: {e}")
            
            # Load alias ID
            alias_id = None
            try:
                response = ssm.get_parameter(
                    Name=f'/curio-news/bedrock-agents/{agent_name}/alias-id',
                    WithDecryption=True
                )
                alias_id = response['Parameter']['Value']
            except Exception as e:
                print(f"⚠️  Could not load alias for {agent_name}, using TSTALIASID")
                alias_id = 'TSTALIASID'
            
            if agent_id:
                agent_ids[agent_name] = agent_id
                self.agent_aliases[agent_name] = alias_id
                print(f"✅ Loaded {agent_name} (alias: {alias_id})")
        
        return agent_ids
    
    async def orchestrate_content_generation(self, news_items: List[Dict]) -> Dict[str, Any]:
        """Main orchestration flow - coordinates all Bedrock agents in 5 phases"""
        print(f"🎭 Starting Bedrock Multi-Agent Orchestration ({len(self.agent_ids)} agents)...")
        orchestration_start = time.time()
        self.orchestration_trace = []
        
        try:
            # Phase 1: Parallel Analysis
            phase1_start = time.time()
            print("🔍 Phase 1: Parallel Analysis (Content Curator + Social Impact Analyzer)")
            curator_result, impact_result = await asyncio.gather(
                self._invoke_agent_async('content_curator', {'news_items': news_items, 'task': 'curate_and_score'}),
                self._invoke_agent_async('social_impact_analyzer', {'news_items': news_items, 'task': 'analyze_social_impact'}),
                return_exceptions=True
            )
            curator_result = self._handle_agent_result(curator_result, 'content_curator', {'curated_stories': news_items})
            impact_result = self._handle_agent_result(impact_result, 'social_impact_analyzer', {})
            phase1_time = time.time() - phase1_start
            
            # Log Phase 1 data flow
            self._log_phase_completion('Phase 1: Analysis', ['content_curator', 'social_impact_analyzer'], 
                                       'parallel', phase1_time, {
                'content_curator_output': f"{len(curator_result.get('curated_stories', []))} stories curated",
                'social_impact_output': f"{len(impact_result.get('high_impact_stories', []))} high-impact stories identified"
            })
            
            # Phase 2: Story Selection (receives outputs from Phase 1)
            phase2_start = time.time()
            print("⭐ Phase 2: Story Selection (receives Phase 1 outputs)")
            story_selector_input = {
                'curated_stories': curator_result.get('curated_stories', news_items[:7]),
                'social_analysis': impact_result,
                'task': 'select_favorite_story'
            }
            story_result = await self._invoke_agent_async('story_selector', story_selector_input)
            story_result = self._handle_agent_result(story_result, 'story_selector', {})
            phase2_time = time.time() - phase2_start
            
            # Log Phase 2 data flow
            self._log_phase_completion('Phase 2: Selection', ['story_selector'], 
                                       'sequential', phase2_time, {
                'input_from': ['content_curator', 'social_impact_analyzer'],
                'stories_evaluated': len(story_selector_input['curated_stories']),
                'favorite_selected': story_result.get('favorite_story', {}).get('title', 'None')
            })
            
            # Phase 3: Script Writing (receives favorite story from Story Selector)
            phase3_start = time.time()
            print("📝 Phase 3: Script Writing (receives favorite story from Story Selector)")
            script_writer_input = {
                'curated_stories': curator_result.get('curated_stories', news_items[:7]),
                'favorite_story': story_result.get('favorite_story', {}),
                'task': 'write_audio_script'
            }
            script_result = await self._invoke_agent_async('script_writer', script_writer_input)
            script_result = self._handle_agent_result(script_result, 'script_writer', {})
            phase3_time = time.time() - phase3_start
            
            # Log Phase 3 data flow
            self._log_phase_completion('Phase 3: Script Writing', ['script_writer'], 
                                       'sequential', phase3_time, {
                'input_from': ['story_selector', 'content_curator'],
                'script_length': len(script_result.get('script', '')),
                'word_count': script_result.get('word_count', 0)
            })
            
            # Phase 4: Enhancement (Parallel - Entertainment Curator + Media Enhancer)
            phase4_start = time.time()
            print("🎨 Phase 4: Parallel Enhancement (Entertainment Curator + Media Enhancer)")
            entertainment_result, media_result = await asyncio.gather(
                self._invoke_agent_async('entertainment_curator', {
                    'curated_stories': curator_result.get('curated_stories', news_items[:7]),
                    'social_themes': impact_result.get('social_themes', {}),
                    'task': 'curate_entertainment'
                }),
                self._invoke_agent_async('media_enhancer', {
                    'curated_stories': curator_result.get('curated_stories', news_items[:7]),
                    'favorite_story': story_result.get('favorite_story', {}),
                    'task': 'enhance_media'
                }),
                return_exceptions=True
            )
            entertainment_result = self._handle_agent_result(entertainment_result, 'entertainment_curator', {})
            media_result = self._handle_agent_result(media_result, 'media_enhancer', {})
            phase4_time = time.time() - phase4_start
            
            # Log Phase 4 data flow
            self._log_phase_completion('Phase 4: Enhancement', ['entertainment_curator', 'media_enhancer'], 
                                       'parallel', phase4_time, {
                'entertainment_recommendations': len(entertainment_result.get('entertainment_recommendations', {}).get('top_movies', [])),
                'media_enhancements': len(media_result.get('media_enhancements', {}).get('stories', []))
            })
            
            # Phase 5: Aggregation
            print("📦 Phase 5: Aggregation")
            final_content = self._aggregate_results({
                'curator': curator_result, 'impact': impact_result, 'story': story_result,
                'script': script_result, 'entertainment': entertainment_result, 'media': media_result,
                'news_items': news_items
            })
            
            orchestration_time = time.time() - orchestration_start
            
            # Add comprehensive metadata with agent attribution
            final_content.update({
                'orchestration_trace': self.orchestration_trace,
                'orchestration_time': orchestration_time,
                'agents_used': len(self.agent_ids),
                'multi_agent_enabled': True,
                'bedrock_agents': True,
                'session_id': self.session_id,
                'agent_attribution': self._create_agent_attribution({
                    'curator': curator_result,
                    'impact': impact_result,
                    'story': story_result,
                    'script': script_result,
                    'entertainment': entertainment_result,
                    'media': media_result
                }),
                'data_flow_summary': self._create_data_flow_summary()
            })
            
            print(f"🎉 Complete! ({orchestration_time:.2f}s, {len(self.agent_ids)} agents)")
            
            # Store orchestration statistics
            self._store_orchestration_stats('success', orchestration_time, len(self.agent_ids))
            
            return final_content
            
        except Exception as e:
            print(f"❌ Orchestration error: {e}")
            import traceback
            traceback.print_exc()
            
            # Store failed orchestration statistics
            orchestration_time = time.time() - orchestration_start
            self._store_orchestration_stats('failed', orchestration_time, len(self.agent_ids), str(e))
            
            return self._create_fallback_response(news_items, str(e))
    
    async def _invoke_agent_async(self, agent_name: str, input_data: Dict) -> Dict[str, Any]:
        """Invoke a Bedrock agent asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._invoke_agent, agent_name, input_data)
    
    def _invoke_agent(self, agent_name: str, input_data: Dict) -> Dict[str, Any]:
        """Invoke a single Bedrock agent via AWS Bedrock Agent Runtime"""
        agent_start = time.time()
        print(f"  🤖 {agent_name}...")
        
        if agent_name not in self.agent_ids:
            raise Exception(f"Agent {agent_name} not configured")
        
        agent_id = self.agent_ids[agent_name]
        
        try:
            # Optimize input size for faster processing
            input_text = json.dumps(input_data, separators=(',', ':'))
            
            # Invoke Bedrock agent with timeout handling
            alias_id = self.agent_aliases.get(agent_name, 'TSTALIASID')
            response = bedrock_agent_runtime.invoke_agent(
                agentId=agent_id,
                agentAliasId=alias_id,
                sessionId=self.session_id,
                inputText=input_text
            )
            
            # Process streaming response with timeout
            result_text = ""
            chunk_start = time.time()
            for event in response.get('completion', []):
                # Check for timeout
                if time.time() - agent_start > self.agent_timeout:
                    raise Exception(f"Agent {agent_name} timeout after {self.agent_timeout}s")
                
                if 'chunk' in event and 'bytes' in event['chunk']:
                    result_text += event['chunk']['bytes'].decode('utf-8')
            
            # Parse result
            try:
                result = json.loads(result_text)
            except json.JSONDecodeError:
                result = {'response': result_text, 'raw_output': result_text}
            
            agent_time = time.time() - agent_start
            
            # Track execution with data flow information
            trace_entry = {
                'agent': agent_name,
                'agent_id': agent_id,
                'status': 'success',
                'execution_time': agent_time,
                'timestamp': datetime.utcnow().isoformat(),
                'input_size': len(input_text),
                'output_size': len(result_text),
                'input_sources': self._identify_input_sources(input_data),
                'output_summary': self._summarize_output(agent_name, result)
            }
            self.orchestration_trace.append(trace_entry)
            
            print(f"    ✅ {agent_name} ({agent_time:.2f}s)")
            return result
            
        except Exception as e:
            agent_time = time.time() - agent_start
            self.orchestration_trace.append({
                'agent': agent_name,
                'agent_id': agent_id,
                'status': 'failed',
                'error': str(e),
                'execution_time': agent_time,
                'timestamp': datetime.utcnow().isoformat()
            })
            print(f"    ❌ {agent_name}: {e}")
            raise
    
    def _identify_input_sources(self, input_data: Dict) -> List[str]:
        """Identify which agents' outputs are being used as input"""
        sources = []
        if 'curated_stories' in input_data:
            sources.append('content_curator')
        if 'social_analysis' in input_data or 'social_themes' in input_data:
            sources.append('social_impact_analyzer')
        if 'favorite_story' in input_data:
            sources.append('story_selector')
        if 'news_items' in input_data:
            sources.append('raw_news_feed')
        return sources if sources else ['initial_input']
    
    def _summarize_output(self, agent_name: str, result: Dict) -> str:
        """Create a brief summary of agent output"""
        summaries = {
            'content_curator': f"{len(result.get('curated_stories', []))} stories curated",
            'social_impact_analyzer': f"{len(result.get('high_impact_stories', []))} high-impact stories",
            'story_selector': f"Selected: {result.get('favorite_story', {}).get('title', 'N/A')[:50]}",
            'script_writer': f"{result.get('word_count', 0)} words, {result.get('estimated_duration_seconds', 0)}s",
            'entertainment_curator': f"{len(result.get('entertainment_recommendations', {}).get('top_movies', []))} recommendations",
            'media_enhancer': f"{len(result.get('media_enhancements', {}).get('stories', []))} stories enhanced"
        }
        return summaries.get(agent_name, 'Output generated')
    
    def _handle_agent_result(self, result: Any, agent_name: str, fallback: Any) -> Any:
        """Handle agent result, including exceptions"""
        if isinstance(result, Exception):
            print(f"⚠️  {agent_name} failed, using fallback")
            return fallback
        return result
    
    def _log_phase_completion(self, phase_name: str, agents: List[str], 
                             execution_mode: str, duration: float, metadata: Dict) -> None:
        """Log completion of an orchestration phase with data flow details"""
        phase_log = {
            'phase': phase_name,
            'agents': agents,
            'execution_mode': execution_mode,
            'duration': duration,
            'metadata': metadata,
            'timestamp': datetime.utcnow().isoformat()
        }
        self.orchestration_trace.append(phase_log)
        print(f"  ✅ {phase_name} complete ({duration:.2f}s, {execution_mode})")
    
    def _create_agent_attribution(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Create metadata attributing content to specific agents"""
        attribution = {
            'news_curation': {
                'agent': 'content_curator',
                'contribution': 'Curated and scored news stories',
                'stories_curated': len(results.get('curator', {}).get('curated_stories', [])),
                'total_analyzed': results.get('curator', {}).get('total_analyzed', 0)
            },
            'social_impact_analysis': {
                'agent': 'social_impact_analyzer',
                'contribution': 'Analyzed social impact and generational appeal',
                'high_impact_stories': len(results.get('impact', {}).get('high_impact_stories', [])),
                'social_themes': results.get('impact', {}).get('social_themes', {})
            },
            'story_selection': {
                'agent': 'story_selector',
                'contribution': 'Selected favorite story based on social impact',
                'favorite_story': results.get('story', {}).get('favorite_story', {}).get('title', 'None'),
                'selection_reasoning': results.get('story', {}).get('favorite_story', {}).get('reasoning', '')
            },
            'script_writing': {
                'agent': 'script_writer',
                'contribution': 'Created conversational audio script',
                'script_length': len(results.get('script', {}).get('script', '')),
                'word_count': results.get('script', {}).get('word_count', 0),
                'estimated_duration': results.get('script', {}).get('estimated_duration_seconds', 0)
            },
            'entertainment_curation': {
                'agent': 'entertainment_curator',
                'contribution': 'Curated weekend entertainment recommendations',
                'recommendations': {
                    'movies': len(results.get('entertainment', {}).get('entertainment_recommendations', {}).get('top_movies', [])),
                    'series': len(results.get('entertainment', {}).get('entertainment_recommendations', {}).get('must_watch_series', [])),
                    'theater': len(results.get('entertainment', {}).get('entertainment_recommendations', {}).get('theater_plays', []))
                }
            },
            'media_enhancement': {
                'agent': 'media_enhancer',
                'contribution': 'Enhanced media with accessibility and social optimization',
                'stories_enhanced': len(results.get('media', {}).get('media_enhancements', {}).get('stories', [])),
                'accessibility_score': results.get('media', {}).get('accessibility_score', 0)
            }
        }
        return attribution
    
    def _create_data_flow_summary(self) -> Dict[str, Any]:
        """Create a summary of data flow between agents"""
        data_flow = {
            'phase_1_to_phase_2': {
                'from_agents': ['content_curator', 'social_impact_analyzer'],
                'to_agent': 'story_selector',
                'data_passed': 'Curated stories and social impact analysis'
            },
            'phase_2_to_phase_3': {
                'from_agent': 'story_selector',
                'to_agent': 'script_writer',
                'data_passed': 'Selected favorite story'
            },
            'phase_1_to_phase_4': {
                'from_agents': ['content_curator', 'social_impact_analyzer'],
                'to_agents': ['entertainment_curator', 'media_enhancer'],
                'data_passed': 'Curated stories and social themes'
            },
            'collaboration_pattern': 'Sequential phases with parallel execution within phases',
            'total_phases': 5,
            'agent_dependencies': {
                'story_selector': ['content_curator', 'social_impact_analyzer'],
                'script_writer': ['story_selector', 'content_curator'],
                'entertainment_curator': ['content_curator', 'social_impact_analyzer'],
                'media_enhancer': ['content_curator', 'story_selector']
            }
        }
        return data_flow
    
    def _aggregate_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate all agent outputs into final response"""
        # Extract data from agent results
        curated_stories = results.get('curator', {}).get('curated_stories', results.get('news_items', [])[:7])
        favorite_story = results.get('story', {}).get('favorite_story', {})
        script = results.get('script', {}).get('script', "Welcome to Curio News!")
        
        # Fallback favorite story if needed
        if not favorite_story and curated_stories:
            first = curated_stories[0]
            favorite_story = {k: first.get(k, '') for k in ['title', 'summary', 'category', 'source', 'image']}
            favorite_story['reasoning'] = f"Selected from {len(curated_stories)} stories"
        
        # Build response
        return {
            'script': script,
            'news_items': curated_stories,
            'sources': list(set(item.get('source', 'Unknown') for item in curated_stories)),
            'agentOutputs': {
                'favoriteStory': favorite_story,
                'mediaEnhancements': results.get('media', {}).get('media_enhancements', {'stories': []}),
                'weekendRecommendations': {
                    'books': self._get_defaults('books'),
                    'movies_and_shows': self._get_defaults('movies'),
                    'events': self._get_defaults('events'),
                    'entertainment_recommendations': results.get('entertainment', {}).get('entertainment_recommendations', {})
                }
            },
            'generatedAt': datetime.utcnow().isoformat(),
            'why': f"Generated by {len(self.agent_ids)} Bedrock agents",
            'traceId': f"bedrock-{int(time.time())}"
        }
    
    def _create_fallback_response(self, news_items: List[Dict], error: str) -> Dict[str, Any]:
        """Create a fallback response when orchestration fails"""
        print("⚠️  Creating fallback response...")
        
        favorite_story = {}
        if news_items:
            first = news_items[0]
            favorite_story = {k: first.get(k, '') for k in ['title', 'summary', 'category', 'source', 'image']}
            favorite_story['reasoning'] = 'Selected as featured story'
        
        return {
            'script': "Welcome to Curio News! We're bringing you the latest stories.",
            'news_items': news_items[:7],
            'sources': list(set(item.get('source', 'Unknown') for item in news_items[:7])),
            'agentOutputs': {
                'favoriteStory': favorite_story,
                'mediaEnhancements': {'stories': []},
                'weekendRecommendations': {k: self._get_defaults(k) for k in ['books', 'movies', 'events']}
            },
            'generatedAt': datetime.utcnow().isoformat(),
            'why': f"Fallback: {error}",
            'traceId': f"fallback-{int(time.time())}",
            'orchestration_trace': self.orchestration_trace,
            'error': error,
            'multi_agent_enabled': False
        }
    
    def _get_defaults(self, type: str) -> List[Dict]:
        """Get default recommendations"""
        defaults = {
            'books': [{"title": "The News: A User's Manual", "author": "Alain de Botton", 
                      "description": "A guide to consuming news", "genre": "Non-fiction"}],
            'movies': [{"title": "All the President's Men", "platform": "Various Streaming",
                       "description": "Classic journalism thriller", "genre": "Drama"}],
            'events': [{"name": "Local Community Events", "location": "Check local listings",
                       "date": "Various", "description": "Explore events in your area"}]
        }
        return defaults.get(type, [])
    
    def _store_orchestration_stats(self, status: str, execution_time: float, 
                                   agents_used: int, error: str = None) -> None:
        """Store orchestration statistics in DynamoDB for tracking"""
        try:
            timestamp = datetime.utcnow().isoformat()
            run_id = f"run-{int(time.time())}-{uuid.uuid4().hex[:8]}"
            
            item = {
                'pk': {'S': 'orchestration_stats'},
                'sk': {'S': run_id},
                'timestamp': {'S': timestamp},
                'status': {'S': status},
                'execution_time': {'N': str(execution_time)},
                'agents_used': {'N': str(agents_used)},
                'session_id': {'S': self.session_id},
                'expiresAt': {'N': str(int(time.time()) + (30 * 24 * 3600))}  # 30 day TTL
            }
            
            if error:
                item['error'] = {'S': error}
            
            # Store agent execution details
            agent_executions = []
            for trace in self.orchestration_trace:
                if 'agent' in trace and 'execution_time' in trace:
                    agent_executions.append({
                        'agent': trace['agent'],
                        'status': trace.get('status', 'unknown'),
                        'execution_time': trace.get('execution_time', 0)
                    })
            
            if agent_executions:
                item['agent_executions'] = {'S': json.dumps(agent_executions)}
            
            dynamodb.put_item(
                TableName=self.table_name,
                Item=item
            )
            
            print(f"✅ Stored orchestration statistics: {status} ({execution_time:.2f}s)")
            
        except Exception as e:
            print(f"⚠️ Error storing orchestration statistics: {e}")
            # Don't fail the orchestration if stats storage fails
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get current status of all Bedrock agents"""
        agent_statuses = []
        for agent_name, agent_id in self.agent_ids.items():
            latest = next((t for t in reversed(self.orchestration_trace) if t.get('agent') == agent_name), None)
            agent_statuses.append({
                'name': agent_name,
                'agent_id': agent_id,
                'status': 'available',
                'last_execution': latest
            })
        
        return {
            'agents': agent_statuses,
            'total_agents': len(self.agent_ids),
            'session_id': self.session_id,
            'orchestration_trace': self.orchestration_trace,
            'timestamp': datetime.utcnow().isoformat()
        }
