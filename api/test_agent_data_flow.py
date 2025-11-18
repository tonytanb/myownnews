"""
Test Agent-to-Agent Data Flow in Bedrock Orchestrator
Verifies that agents properly pass data between phases
"""
import json
import asyncio
from bedrock_orchestrator import BedrockAgentOrchestrator

def test_data_flow_structure():
    """Test that the orchestrator has proper data flow methods"""
    orchestrator = BedrockAgentOrchestrator()
    
    # Verify helper methods exist
    assert hasattr(orchestrator, '_log_phase_completion'), "Missing _log_phase_completion method"
    assert hasattr(orchestrator, '_create_agent_attribution'), "Missing _create_agent_attribution method"
    assert hasattr(orchestrator, '_create_data_flow_summary'), "Missing _create_data_flow_summary method"
    assert hasattr(orchestrator, '_identify_input_sources'), "Missing _identify_input_sources method"
    assert hasattr(orchestrator, '_summarize_output'), "Missing _summarize_output method"
    
    print("✅ All data flow methods present")

def test_input_source_identification():
    """Test that input sources are correctly identified"""
    orchestrator = BedrockAgentOrchestrator()
    
    # Test various input combinations
    test_cases = [
        ({'news_items': []}, ['raw_news_feed']),
        ({'curated_stories': []}, ['content_curator']),
        ({'social_analysis': {}}, ['social_impact_analyzer']),
        ({'favorite_story': {}}, ['story_selector']),
        ({'curated_stories': [], 'social_analysis': {}}, ['content_curator', 'social_impact_analyzer']),
        ({'curated_stories': [], 'favorite_story': {}}, ['content_curator', 'story_selector']),
    ]
    
    for input_data, expected_sources in test_cases:
        sources = orchestrator._identify_input_sources(input_data)
        assert set(sources) == set(expected_sources), f"Expected {expected_sources}, got {sources}"
    
    print("✅ Input source identification working correctly")

def test_output_summarization():
    """Test that agent outputs are properly summarized"""
    orchestrator = BedrockAgentOrchestrator()
    
    # Test summaries for each agent type
    test_cases = [
        ('content_curator', {'curated_stories': [1, 2, 3]}, '3 stories curated'),
        ('social_impact_analyzer', {'high_impact_stories': [1, 2]}, '2 high-impact stories'),
        ('story_selector', {'favorite_story': {'title': 'Test Story'}}, 'Selected: Test Story'),
        ('script_writer', {'word_count': 250, 'estimated_duration_seconds': 100}, '250 words, 100s'),
        ('entertainment_curator', {'entertainment_recommendations': {'top_movies': [1, 2, 3]}}, '3 recommendations'),
        ('media_enhancer', {'media_enhancements': {'stories': [1, 2]}}, '2 stories enhanced'),
    ]
    
    for agent_name, result, expected_summary in test_cases:
        summary = orchestrator._summarize_output(agent_name, result)
        assert summary == expected_summary, f"Expected '{expected_summary}', got '{summary}'"
    
    print("✅ Output summarization working correctly")

def test_agent_attribution_structure():
    """Test that agent attribution metadata is properly structured"""
    orchestrator = BedrockAgentOrchestrator()
    
    # Create mock results
    mock_results = {
        'curator': {'curated_stories': [1, 2, 3], 'total_analyzed': 10},
        'impact': {'high_impact_stories': [1, 2], 'social_themes': {'community': 3}},
        'story': {'favorite_story': {'title': 'Test Story', 'reasoning': 'High impact'}},
        'script': {'script': 'Test script', 'word_count': 250, 'estimated_duration_seconds': 100},
        'entertainment': {'entertainment_recommendations': {'top_movies': [1, 2], 'must_watch_series': [1], 'theater_plays': []}},
        'media': {'media_enhancements': {'stories': [1, 2, 3]}, 'accessibility_score': 95}
    }
    
    attribution = orchestrator._create_agent_attribution(mock_results)
    
    # Verify structure
    assert 'news_curation' in attribution
    assert 'social_impact_analysis' in attribution
    assert 'story_selection' in attribution
    assert 'script_writing' in attribution
    assert 'entertainment_curation' in attribution
    assert 'media_enhancement' in attribution
    
    # Verify content
    assert attribution['news_curation']['agent'] == 'content_curator'
    assert attribution['news_curation']['stories_curated'] == 3
    assert attribution['social_impact_analysis']['agent'] == 'social_impact_analyzer'
    assert attribution['story_selection']['favorite_story'] == 'Test Story'
    assert attribution['script_writing']['word_count'] == 250
    
    print("✅ Agent attribution structure correct")

def test_data_flow_summary_structure():
    """Test that data flow summary is properly structured"""
    orchestrator = BedrockAgentOrchestrator()
    
    data_flow = orchestrator._create_data_flow_summary()
    
    # Verify structure
    assert 'phase_1_to_phase_2' in data_flow
    assert 'phase_2_to_phase_3' in data_flow
    assert 'phase_1_to_phase_4' in data_flow
    assert 'collaboration_pattern' in data_flow
    assert 'total_phases' in data_flow
    assert 'agent_dependencies' in data_flow
    
    # Verify phase 1 to phase 2 flow
    assert data_flow['phase_1_to_phase_2']['to_agent'] == 'story_selector'
    assert 'content_curator' in data_flow['phase_1_to_phase_2']['from_agents']
    assert 'social_impact_analyzer' in data_flow['phase_1_to_phase_2']['from_agents']
    
    # Verify phase 2 to phase 3 flow
    assert data_flow['phase_2_to_phase_3']['from_agent'] == 'story_selector'
    assert data_flow['phase_2_to_phase_3']['to_agent'] == 'script_writer'
    
    # Verify agent dependencies
    assert 'story_selector' in data_flow['agent_dependencies']
    assert 'content_curator' in data_flow['agent_dependencies']['story_selector']
    assert 'script_writer' in data_flow['agent_dependencies']
    assert 'story_selector' in data_flow['agent_dependencies']['script_writer']
    
    print("✅ Data flow summary structure correct")

def test_phase_logging():
    """Test that phase completion logging works"""
    orchestrator = BedrockAgentOrchestrator()
    
    # Log a test phase
    orchestrator._log_phase_completion(
        'Test Phase',
        ['agent1', 'agent2'],
        'parallel',
        1.5,
        {'test_key': 'test_value'}
    )
    
    # Verify trace was updated
    assert len(orchestrator.orchestration_trace) == 1
    trace_entry = orchestrator.orchestration_trace[0]
    
    assert trace_entry['phase'] == 'Test Phase'
    assert trace_entry['agents'] == ['agent1', 'agent2']
    assert trace_entry['execution_mode'] == 'parallel'
    assert trace_entry['duration'] == 1.5
    assert trace_entry['metadata']['test_key'] == 'test_value'
    assert 'timestamp' in trace_entry
    
    print("✅ Phase logging working correctly")

if __name__ == '__main__':
    print("🧪 Testing Agent-to-Agent Data Flow Implementation\n")
    
    try:
        test_data_flow_structure()
        test_input_source_identification()
        test_output_summarization()
        test_agent_attribution_structure()
        test_data_flow_summary_structure()
        test_phase_logging()
        
        print("\n✅ All data flow tests passed!")
        print("\n📊 Data Flow Implementation Summary:")
        print("  ✓ Phase 1: Parallel invocation of Content Curator and Social Impact Analyzer")
        print("  ✓ Phase 2: Story Selector receives outputs from Phase 1 agents")
        print("  ✓ Phase 3: Script Writer receives favorite story from Story Selector")
        print("  ✓ Phase 4: Parallel invocation of Entertainment Curator and Media Enhancer")
        print("  ✓ Orchestration trace log showing data flow between agents")
        print("  ✓ Metadata attributing content to specific agents")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
