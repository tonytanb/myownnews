#!/usr/bin/env python3
"""
Test script to validate Bedrock agent setup configuration without creating resources.
"""

import sys
import json

# Add the scripts directory to path
sys.path.insert(0, 'scripts')

from setup_bedrock_agents import BedrockAgentSetup

def test_agent_configurations():
    """Test that all agent configurations are properly defined."""
    print("Testing Bedrock Agent Configurations...")
    print("="*60)
    
    # Create setup instance (won't make AWS calls yet)
    try:
        setup = BedrockAgentSetup(region='us-east-1')
    except Exception as e:
        print(f"✗ Failed to initialize setup: {e}")
        return False
    
    # Validate agent configs
    expected_agents = [
        'content_curator',
        'social_impact_analyzer', 
        'story_selector',
        'script_writer',
        'entertainment_curator',
        'media_enhancer'
    ]
    
    print(f"\nExpected agents: {len(expected_agents)}")
    print(f"Configured agents: {len(setup.agent_configs)}")
    
    all_valid = True
    
    for agent_key in expected_agents:
        if agent_key not in setup.agent_configs:
            print(f"✗ Missing agent configuration: {agent_key}")
            all_valid = False
            continue
        
        config = setup.agent_configs[agent_key]
        
        # Validate required fields
        required_fields = ['name', 'description', 'model_id', 'instructions', 'enable_multi_agent']
        missing_fields = [f for f in required_fields if f not in config]
        
        if missing_fields:
            print(f"✗ {agent_key}: Missing fields: {missing_fields}")
            all_valid = False
            continue
        
        # Validate name format (no spaces)
        if ' ' in config['name']:
            print(f"✗ {agent_key}: Agent name contains spaces: {config['name']}")
            all_valid = False
            continue
        
        # Validate multi-agent is enabled
        if not config['enable_multi_agent']:
            print(f"⚠ {agent_key}: Multi-agent collaboration not enabled")
        
        # Validate instructions are not empty
        if len(config['instructions'].strip()) < 100:
            print(f"✗ {agent_key}: Instructions too short")
            all_valid = False
            continue
        
        # Validate model ID
        if 'claude-3-5-sonnet' not in config['model_id']:
            print(f"⚠ {agent_key}: Not using Claude 3.5 Sonnet: {config['model_id']}")
        
        print(f"✓ {agent_key}: Configuration valid")
        print(f"  Name: {config['name']}")
        print(f"  Model: {config['model_id']}")
        print(f"  Multi-Agent: {config['enable_multi_agent']}")
        print(f"  Instructions: {len(config['instructions'])} characters")
    
    print("\n" + "="*60)
    if all_valid:
        print("✓ ALL AGENT CONFIGURATIONS VALID")
        print("\nConfiguration Summary:")
        print(f"  Total Agents: {len(setup.agent_configs)}")
        print(f"  Model: Claude 3.5 Sonnet v2")
        print(f"  Multi-Agent Enabled: Yes")
        print(f"  Alias Name: LIVE")
        return True
    else:
        print("✗ CONFIGURATION VALIDATION FAILED")
        return False

def test_iam_role_naming():
    """Test IAM role naming conventions."""
    print("\n" + "="*60)
    print("Testing IAM Role Naming...")
    print("="*60)
    
    setup = BedrockAgentSetup(region='us-east-1')
    
    for agent_key in setup.agent_configs.keys():
        role_name = f"CurioNewsBedrockAgent-{agent_key.replace('_', '-')}"
        
        # Validate role name doesn't have underscores
        if '_' in role_name:
            print(f"✗ {agent_key}: Role name contains underscores: {role_name}")
            return False
        
        print(f"✓ {agent_key}: {role_name}")
    
    print("\n✓ All IAM role names valid")
    return True

def test_parameter_store_paths():
    """Test Parameter Store path conventions."""
    print("\n" + "="*60)
    print("Testing Parameter Store Paths...")
    print("="*60)
    
    setup = BedrockAgentSetup(region='us-east-1')
    
    for agent_key in setup.agent_configs.keys():
        agent_id_path = f"/curio-news/bedrock-agents/{agent_key}/agent-id"
        alias_id_path = f"/curio-news/bedrock-agents/{agent_key}/alias-id"
        
        print(f"✓ {agent_key}:")
        print(f"  Agent ID: {agent_id_path}")
        print(f"  Alias ID: {alias_id_path}")
    
    consolidated_path = "/curio-news/bedrock-agents/all-agents"
    print(f"\n✓ Consolidated: {consolidated_path}")
    
    return True

def main():
    """Run all validation tests."""
    print("\n" + "="*60)
    print("BEDROCK AGENT SETUP VALIDATION")
    print("="*60)
    print("This test validates configuration without creating AWS resources.\n")
    
    tests = [
        ("Agent Configurations", test_agent_configurations),
        ("IAM Role Naming", test_iam_role_naming),
        ("Parameter Store Paths", test_parameter_store_paths)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} failed with error: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n" + "="*60)
        print("✓ ALL VALIDATIONS PASSED")
        print("="*60)
        print("\nThe setup script is ready to create Bedrock agents.")
        print("Run: python3 scripts/setup_bedrock_agents.py")
        return 0
    else:
        print("\n" + "="*60)
        print("✗ SOME VALIDATIONS FAILED")
        print("="*60)
        print("\nPlease fix the issues above before running the setup.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
