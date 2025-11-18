#!/usr/bin/env python3
"""
Health check script for Bedrock Multi-Agent Architecture.
Verifies all agents are properly configured and accessible.
"""

import boto3
import json
import sys
from datetime import datetime

def print_header(text):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def print_success(text):
    """Print success message"""
    print(f"✅ {text}")

def print_warning(text):
    """Print warning message"""
    print(f"⚠️  {text}")

def print_error(text):
    """Print error message"""
    print(f"❌ {text}")

def check_aws_credentials():
    """Verify AWS credentials are configured"""
    print_header("Checking AWS Credentials")
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print_success(f"AWS Account: {identity['Account']}")
        print_success(f"User/Role: {identity['Arn']}")
        return True
    except Exception as e:
        print_error(f"AWS credentials not configured: {e}")
        return False

def check_parameter_store():
    """Check if agent IDs are stored in Parameter Store"""
    print_header("Checking Parameter Store")
    try:
        ssm = boto3.client('ssm', region_name='us-east-1')
        response = ssm.get_parameters_by_path(
            Path='/curio-news/agents/',
            Recursive=True
        )
        
        if not response['Parameters']:
            print_error("No agent parameters found in Parameter Store")
            print("Run: python scripts/setup_bedrock_agents.py")
            return {}
        
        agent_ids = {}
        for param in response['Parameters']:
            name = param['Name'].split('/')[-1]
            agent_ids[name] = param['Value']
            print_success(f"Found parameter: {name}")
        
        print(f"\n📊 Total parameters: {len(agent_ids)}")
        return agent_ids
        
    except Exception as e:
        print_error(f"Error accessing Parameter Store: {e}")
        return {}

def check_agent_status(agent_name, agent_id):
    """Check status of a specific agent"""
    try:
        bedrock = boto3.client('bedrock-agent', region_name='us-east-1')
        response = bedrock.get_agent(agentId=agent_id)
        
        agent = response['agent']
        status = agent['agentStatus']
        model = agent.get('foundationModel', 'Unknown')
        
        if status == 'PREPARED':
            print_success(f"{agent_name}: {status} (Model: {model})")
            return True
        elif status == 'NOT_PREPARED':
            print_warning(f"{agent_name}: {status} - Agent needs preparation")
            print(f"   Run: aws bedrock-agent prepare-agent --agent-id {agent_id}")
            return False
        else:
            print_warning(f"{agent_name}: {status}")
            return False
            
    except Exception as e:
        print_error(f"{agent_name}: {str(e)}")
        return False

def check_agent_aliases(agent_name, agent_id):
    """Check if agent has PROD alias"""
    try:
        bedrock = boto3.client('bedrock-agent', region_name='us-east-1')
        response = bedrock.list_agent_aliases(agentId=agent_id)
        
        aliases = response.get('agentAliasSummaries', [])
        prod_alias = next((a for a in aliases if a['agentAliasName'] == 'PROD'), None)
        
        if prod_alias:
            print_success(f"{agent_name}: PROD alias exists")
            return True
        else:
            print_warning(f"{agent_name}: No PROD alias found")
            return False
            
    except Exception as e:
        print_error(f"{agent_name} alias check failed: {e}")
        return False

def check_lambda_configuration():
    """Check if Lambda function is configured with agent IDs"""
    print_header("Checking Lambda Configuration")
    try:
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        # Try to find the Lambda function
        function_names = [
            'curio-news-bootstrap',
            'CurioNewsBootstrapFunction',
            'curio-news-api'
        ]
        
        function_found = False
        for function_name in function_names:
            try:
                response = lambda_client.get_function_configuration(
                    FunctionName=function_name
                )
                function_found = True
                print_success(f"Found Lambda function: {function_name}")
                
                # Check environment variables
                env_vars = response.get('Environment', {}).get('Variables', {})
                agent_env_vars = [k for k in env_vars.keys() if 'AGENT' in k]
                
                if agent_env_vars:
                    print_success(f"Found {len(agent_env_vars)} agent environment variables")
                    for var in agent_env_vars:
                        print(f"   - {var}")
                else:
                    print_warning("No agent environment variables found")
                    print("   Update template.yaml and redeploy")
                
                break
                
            except lambda_client.exceptions.ResourceNotFoundException:
                continue
        
        if not function_found:
            print_warning("Lambda function not found")
            print("   Deploy with: sam build && sam deploy")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"Error checking Lambda: {e}")
        return False

def test_agent_invocation(agent_name, agent_id):
    """Test invoking an agent with sample data"""
    try:
        bedrock_runtime = boto3.client('bedrock-agent-runtime', region_name='us-east-1')
        
        # Simple test input
        test_input = json.dumps({
            "test": "health_check",
            "timestamp": datetime.now().isoformat()
        })
        
        response = bedrock_runtime.invoke_agent(
            agentId=agent_id,
            agentAliasId='PROD',
            sessionId=f'health-check-{int(datetime.now().timestamp())}',
            inputText=test_input
        )
        
        # Try to read response
        result = ""
        for event in response.get('completion', []):
            if 'chunk' in event:
                chunk = event['chunk']
                if 'bytes' in chunk:
                    result += chunk['bytes'].decode('utf-8')
        
        if result:
            print_success(f"{agent_name}: Invocation successful")
            return True
        else:
            print_warning(f"{agent_name}: Invocation returned empty response")
            return False
            
    except Exception as e:
        print_error(f"{agent_name} invocation failed: {str(e)}")
        return False

def generate_report(results):
    """Generate summary report"""
    print_header("Health Check Summary")
    
    total_checks = len(results)
    passed_checks = sum(1 for r in results.values() if r)
    failed_checks = total_checks - passed_checks
    
    print(f"📊 Total Checks: {total_checks}")
    print(f"✅ Passed: {passed_checks}")
    print(f"❌ Failed: {failed_checks}")
    
    if failed_checks == 0:
        print("\n🎉 All health checks passed! System is ready.")
        return True
    else:
        print(f"\n⚠️  {failed_checks} health check(s) failed. Review errors above.")
        return False

def main():
    """Main health check routine"""
    print_header("Bedrock Multi-Agent Health Check")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    results = {}
    
    # Check AWS credentials
    if not check_aws_credentials():
        print("\n❌ Cannot proceed without valid AWS credentials")
        sys.exit(1)
    
    # Check Parameter Store
    agent_ids = check_parameter_store()
    if not agent_ids:
        print("\n❌ No agents found. Run setup script first.")
        print("   python scripts/setup_bedrock_agents.py")
        sys.exit(1)
    
    # Check each agent
    print_header("Checking Agent Status")
    for agent_name, agent_id in agent_ids.items():
        status_ok = check_agent_status(agent_name, agent_id)
        alias_ok = check_agent_aliases(agent_name, agent_id)
        results[f"{agent_name}_status"] = status_ok
        results[f"{agent_name}_alias"] = alias_ok
    
    # Check Lambda configuration
    lambda_ok = check_lambda_configuration()
    results['lambda_config'] = lambda_ok
    
    # Optional: Test agent invocation (can be slow)
    test_invocation = input("\n🔬 Test agent invocation? (y/N): ").lower() == 'y'
    if test_invocation:
        print_header("Testing Agent Invocation")
        # Test just one agent to save time
        first_agent = list(agent_ids.items())[0]
        invocation_ok = test_agent_invocation(first_agent[0], first_agent[1])
        results['invocation_test'] = invocation_ok
    
    # Generate report
    all_passed = generate_report(results)
    
    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Health check interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
