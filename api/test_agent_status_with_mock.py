"""
Test script for the /agent-status endpoint with mocked agent configuration
Verifies the complete response structure when agents are configured
"""
import json
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# Set up environment
os.environ['CURIO_TABLE'] = 'CurioTable'
os.environ['USE_BEDROCK_AGENTS'] = 'true'
os.environ['ENABLE_MULTI_AGENT'] = 'true'

def test_agent_status_with_mocked_agents():
    """Test the agent status endpoint with mocked agent configuration"""
    print("🧪 Testing /agent-status endpoint with mocked agents...")
    print("=" * 60)
    
    # Mock agent IDs
    mock_agent_ids = {
        'content_curator': 'agent-curator-123',
        'social_impact_analyzer': 'agent-impact-456',
        'story_selector': 'agent-selector-789',
        'script_writer': 'agent-writer-012',
        'entertainment_curator': 'agent-entertainment-345',
        'media_enhancer': 'agent-media-678'
    }
    
    # Mock orchestration trace
    mock_trace = [
        {
            'agent': 'content_curator',
            'agent_id': 'agent-curator-123',
            'status': 'success',
            'execution_time': 1.2,
            'timestamp': '2025-10-31T04:00:00Z'
        },
        {
            'agent': 'social_impact_analyzer',
            'agent_id': 'agent-impact-456',
            'status': 'success',
            'execution_time': 0.9,
            'timestamp': '2025-10-31T04:00:01Z'
        }
    ]
    
    # Mock orchestration statistics
    mock_stats = {
        'total_runs': 50,
        'successful_runs': 47,
        'failed_runs': 3,
        'success_rate': 94.0,
        'average_execution_time': 5.8,
        'last_run': {
            'timestamp': '2025-10-31T03:55:00Z',
            'status': 'success',
            'execution_time': 5.5,
            'agents_used': 6
        },
        'statistics_period': 'Last 100 runs'
    }
    
    # Mock cache to return None (fresh request)
    with patch('cache_service.get_cached', return_value=None):
        with patch('cache_service.set_cached', return_value=True):
            with patch('main_handler.BedrockAgentOrchestrator') as MockOrchestrator:
                with patch('main_handler.get_orchestration_statistics', return_value=mock_stats):
                    # Configure the mock orchestrator
                    mock_instance = MockOrchestrator.return_value
                    mock_instance.agent_ids = mock_agent_ids
                    mock_instance.orchestration_trace = mock_trace
                    mock_instance.session_id = 'session-test-123'
                    
                    # Mock get_agent_status method
                    mock_instance.get_agent_status.return_value = {
                        'agents': [
                            {
                                'name': name,
                                'agent_id': agent_id,
                                'status': 'available',
                                'last_execution': next((t for t in mock_trace if t['agent'] == name), None)
                            }
                            for name, agent_id in mock_agent_ids.items()
                        ],
                        'total_agents': len(mock_agent_ids),
                        'session_id': 'session-test-123',
                        'orchestration_trace': mock_trace,
                        'timestamp': '2025-10-31T04:00:00Z'
                    }
                    
                    # Import and call the handler
                    from main_handler import handle_agent_status
                    
                    event = {
                        'httpMethod': 'GET',
                        'path': '/agent-status',
                        'headers': {}
                    }
                    
                    try:
                        response = handle_agent_status(event)
                        
                        print(f"\n✅ Status Code: {response['statusCode']}")
                        
                        # Parse the body
                        body = json.loads(response['body'])
                        
                        print(f"\n📊 Response Structure:")
                        print(json.dumps(body, indent=2))
                        
                        # Verify all required fields
                        print(f"\n🔍 Verification:")
                        
                        # Check basic fields
                        assert body.get('bedrock_agents_enabled') == True, "Bedrock agents should be enabled"
                        print(f"  ✅ bedrock_agents_enabled: {body['bedrock_agents_enabled']}")
                        
                        assert body.get('agents_configured') == True, "Agents should be configured"
                        print(f"  ✅ agents_configured: {body['agents_configured']}")
                        
                        assert body.get('agent_count') == 6, "Should have 6 agents"
                        print(f"  ✅ agent_count: {body['agent_count']}")
                        
                        # Check agents array
                        agents = body.get('agents', [])
                        assert len(agents) == 6, "Should have 6 agents in array"
                        print(f"  ✅ agents array length: {len(agents)}")
                        
                        # Verify agent metadata
                        print(f"\n👥 Agent Details:")
                        for agent in agents:
                            print(f"\n  Agent: {agent.get('name')}")
                            assert 'role' in agent, f"Agent {agent.get('name')} should have role"
                            print(f"    ✅ Role: {agent.get('role')}")
                            
                            assert 'description' in agent, f"Agent {agent.get('name')} should have description"
                            print(f"    ✅ Description: {agent.get('description')[:50]}...")
                            
                            assert 'responsibilities' in agent, f"Agent {agent.get('name')} should have responsibilities"
                            print(f"    ✅ Responsibilities: {len(agent.get('responsibilities', []))} items")
                            
                            assert 'status' in agent, f"Agent {agent.get('name')} should have status"
                            print(f"    ✅ Status: {agent.get('status')}")
                        
                        # Check orchestration statistics
                        stats = body.get('orchestration_statistics', {})
                        assert stats, "Should have orchestration statistics"
                        print(f"\n📈 Orchestration Statistics:")
                        
                        assert 'total_runs' in stats, "Should have total_runs"
                        print(f"  ✅ Total Runs: {stats.get('total_runs')}")
                        
                        assert 'success_rate' in stats, "Should have success_rate"
                        print(f"  ✅ Success Rate: {stats.get('success_rate')}%")
                        
                        assert 'average_execution_time' in stats, "Should have average_execution_time"
                        print(f"  ✅ Average Execution Time: {stats.get('average_execution_time')}s")
                        
                        assert 'last_run' in stats, "Should have last_run"
                        if stats.get('last_run'):
                            print(f"  ✅ Last Run:")
                            print(f"    Status: {stats['last_run'].get('status')}")
                            print(f"    Execution Time: {stats['last_run'].get('execution_time')}s")
                            print(f"    Agents Used: {stats['last_run'].get('agents_used')}")
                        
                        # Check caching info
                        assert 'cached' in body, "Should have cached field"
                        print(f"\n💾 Caching:")
                        print(f"  ✅ Cached: {body.get('cached')}")
                        
                        # Check environment info
                        env = body.get('environment', {})
                        assert env, "Should have environment info"
                        print(f"\n🌍 Environment:")
                        print(f"  ✅ USE_BEDROCK_AGENTS: {env.get('USE_BEDROCK_AGENTS')}")
                        print(f"  ✅ ENABLE_MULTI_AGENT: {env.get('ENABLE_MULTI_AGENT')}")
                        
                        print(f"\n{'=' * 60}")
                        print(f"✅ All tests passed successfully!")
                        
                        return True
                        
                    except AssertionError as e:
                        print(f"\n❌ Assertion failed: {e}")
                        return False
                    except Exception as e:
                        print(f"\n❌ Test failed with error: {e}")
                        import traceback
                        traceback.print_exc()
                        return False

if __name__ == '__main__':
    success = test_agent_status_with_mocked_agents()
    sys.exit(0 if success else 1)
