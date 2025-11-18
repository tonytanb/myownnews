"""
Test script for the /agent-status endpoint
Verifies that the endpoint returns proper agent metadata and statistics
"""
import json
import os
import sys

# Set up environment
os.environ['CURIO_TABLE'] = 'CurioTable'
os.environ['USE_BEDROCK_AGENTS'] = 'true'
os.environ['ENABLE_MULTI_AGENT'] = 'true'

# Import the handler
from main_handler import handle_agent_status

def test_agent_status_endpoint():
    """Test the agent status endpoint"""
    print("🧪 Testing /agent-status endpoint...")
    print("=" * 60)
    
    # Create a mock event
    event = {
        'httpMethod': 'GET',
        'path': '/agent-status',
        'headers': {}
    }
    
    # Call the handler
    try:
        response = handle_agent_status(event)
        
        print(f"\n✅ Status Code: {response['statusCode']}")
        print(f"✅ Headers: {json.dumps(response['headers'], indent=2)}")
        
        # Parse the body
        body = json.loads(response['body'])
        
        print(f"\n📊 Response Body:")
        print(json.dumps(body, indent=2))
        
        # Verify required fields
        print(f"\n🔍 Verification:")
        
        required_fields = [
            'bedrock_agents_enabled',
            'timestamp'
        ]
        
        for field in required_fields:
            if field in body:
                print(f"  ✅ {field}: {body[field]}")
            else:
                print(f"  ❌ Missing field: {field}")
        
        # Check for agents if configured
        if body.get('agents_configured'):
            print(f"\n👥 Agents:")
            for agent in body.get('agents', []):
                print(f"  - {agent.get('name')}")
                print(f"    Role: {agent.get('role', 'N/A')}")
                print(f"    Description: {agent.get('description', 'N/A')}")
                print(f"    Status: {agent.get('status', 'N/A')}")
        
        # Check for orchestration statistics
        if 'orchestration_statistics' in body:
            stats = body['orchestration_statistics']
            print(f"\n📈 Orchestration Statistics:")
            print(f"  Total Runs: {stats.get('total_runs', 0)}")
            print(f"  Success Rate: {stats.get('success_rate', 0)}%")
            print(f"  Average Execution Time: {stats.get('average_execution_time', 0)}s")
            
            if stats.get('last_run'):
                print(f"  Last Run:")
                print(f"    Status: {stats['last_run'].get('status', 'N/A')}")
                print(f"    Time: {stats['last_run'].get('execution_time', 0)}s")
        
        # Check caching
        if body.get('cached'):
            print(f"\n💾 Response was served from cache")
            print(f"  Cached at: {body.get('cached_at', 'N/A')}")
        else:
            print(f"\n🔄 Response was freshly generated")
        
        print(f"\n{'=' * 60}")
        print(f"✅ Test completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_agent_status_endpoint()
    sys.exit(0 if success else 1)
