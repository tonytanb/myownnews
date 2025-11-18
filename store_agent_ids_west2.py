#!/usr/bin/env python3
"""Store Bedrock agent IDs in Parameter Store for us-west-2"""
import boto3
import json

bedrock = boto3.client('bedrock-agent', region_name='us-west-2')
ssm = boto3.client('ssm', region_name='us-west-2')

# Get all curio-news agents
response = bedrock.list_agents(maxResults=50)
agents = [a for a in response['agentSummaries'] if 'curio-news' in a['agentName'].lower()]

agent_data = {}
for agent in agents:
    agent_name = agent['agentName']
    agent_id = agent['agentId']
    
    # Map to our naming convention
    key_name = agent_name.replace('curio-news-', '').replace('-', '_')
    
    # Get alias ID
    try:
        aliases = bedrock.list_agent_aliases(agentId=agent_id)
        alias_id = None
        for alias in aliases['agentAliasSummaries']:
            if alias['agentAliasName'] == 'LIVE':
                alias_id = alias['agentAliasId']
                break
    except:
        alias_id = None
    
    agent_data[key_name] = {
        'agent_id': agent_id,
        'agent_name': agent_name,
        'alias_id': alias_id or '',
        'status': agent['agentStatus']
    }
    
    print(f"Found: {key_name} -> {agent_id}")

# Store individual agent IDs
for key, data in agent_data.items():
    param_name = f"/curio-news/bedrock-agents/{key}/agent-id"
    try:
        ssm.put_parameter(
            Name=param_name,
            Value=data['agent_id'],
            Type='String',
            Overwrite=True
        )
        print(f"✅ Stored {param_name}")
    except Exception as e:
        print(f"❌ Error storing {param_name}: {e}")
    
    if data['alias_id']:
        alias_param = f"/curio-news/bedrock-agents/{key}/alias-id"
        try:
            ssm.put_parameter(
                Name=alias_param,
                Value=data['alias_id'],
                Type='String',
                Overwrite=True
            )
            print(f"✅ Stored {alias_param}")
        except Exception as e:
            print(f"❌ Error storing {alias_param}: {e}")

# Store consolidated JSON
try:
    ssm.put_parameter(
        Name="/curio-news/bedrock-agents/all-agents",
        Value=json.dumps(agent_data),
        Type='String',
        Overwrite=True
    )
    print(f"✅ Stored /curio-news/bedrock-agents/all-agents")
except Exception as e:
    print(f"❌ Error storing all-agents: {e}")

print(f"\n✅ Stored {len(agent_data)} agent configurations in Parameter Store (us-west-2)")
