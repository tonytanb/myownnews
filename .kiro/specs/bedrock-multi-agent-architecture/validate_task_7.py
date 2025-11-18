#!/usr/bin/env python3
"""
Validation script for Task 7: SAM Template Update
Verifies that all required changes have been made to template.yaml
"""

import yaml
import sys

def validate_template():
    """Validate the SAM template has all required Bedrock agent configurations."""
    print("="*60)
    print("TASK 7 VALIDATION: SAM Template for Bedrock Agents")
    print("="*60)
    
    with open('template.yaml', 'r') as f:
        template = yaml.safe_load(f)
    
    validation_results = []
    
    # 1. Check CloudWatch Metrics Namespace Parameter
    print("\n1. Checking CloudWatch Metrics Namespace Parameter...")
    if 'CloudWatchMetricsNamespace' in template.get('Parameters', {}):
        namespace = template['Parameters']['CloudWatchMetricsNamespace']
        if namespace.get('Default') == 'CurioNews/BedrockAgents':
            print("   ✅ CloudWatch metrics namespace parameter exists with correct default")
            validation_results.append(True)
        else:
            print(f"   ❌ CloudWatch metrics namespace has wrong default: {namespace.get('Default')}")
            validation_results.append(False)
    else:
        print("   ❌ CloudWatch metrics namespace parameter missing")
        validation_results.append(False)
    
    # 2. Check Lambda Function Configuration
    print("\n2. Checking CurioNewsMainFunction configuration...")
    main_function = template.get('Resources', {}).get('CurioNewsMainFunction', {})
    properties = main_function.get('Properties', {})
    
    # Check timeout
    timeout = properties.get('Timeout')
    if timeout == 180:
        print("   ✅ Lambda timeout set to 180 seconds")
        validation_results.append(True)
    else:
        print(f"   ❌ Lambda timeout is {timeout}, should be 180")
        validation_results.append(False)
    
    # 3. Check Environment Variables
    print("\n3. Checking Bedrock Agent environment variables...")
    env_vars = properties.get('Environment', {}).get('Variables', {})
    
    required_agent_vars = [
        'BEDROCK_AGENT_CONTENT_CURATOR_ID',
        'BEDROCK_AGENT_SOCIAL_IMPACT_ANALYZER_ID',
        'BEDROCK_AGENT_STORY_SELECTOR_ID',
        'BEDROCK_AGENT_SCRIPT_WRITER_ID',
        'BEDROCK_AGENT_ENTERTAINMENT_CURATOR_ID',
        'BEDROCK_AGENT_MEDIA_ENHANCER_ID'
    ]
    
    missing_vars = []
    for var in required_agent_vars:
        if var in env_vars:
            print(f"   ✅ {var} exists")
        else:
            print(f"   ❌ {var} missing")
            missing_vars.append(var)
    
    validation_results.append(len(missing_vars) == 0)
    
    # Check CloudWatch metrics env vars
    print("\n4. Checking CloudWatch metrics environment variables...")
    if 'CLOUDWATCH_METRICS_NAMESPACE' in env_vars:
        print("   ✅ CLOUDWATCH_METRICS_NAMESPACE exists")
        validation_results.append(True)
    else:
        print("   ❌ CLOUDWATCH_METRICS_NAMESPACE missing")
        validation_results.append(False)
    
    if env_vars.get('ENABLE_AGENT_METRICS') == 'true':
        print("   ✅ ENABLE_AGENT_METRICS set to 'true'")
        validation_results.append(True)
    else:
        print(f"   ❌ ENABLE_AGENT_METRICS is '{env_vars.get('ENABLE_AGENT_METRICS')}', should be 'true'")
        validation_results.append(False)
    
    # 4. Check IAM Policies
    print("\n5. Checking IAM policies...")
    policies = properties.get('Policies', [])
    
    # Find the Statement policy
    statement_policy = None
    for policy in policies:
        if 'Statement' in policy:
            statement_policy = policy['Statement']
            break
    
    if not statement_policy:
        print("   ❌ No Statement policy found")
        validation_results.append(False)
    else:
        # Check for Bedrock Agent permissions
        bedrock_agent_policy = None
        ssm_policy = None
        
        for statement in statement_policy:
            if statement.get('Sid') == 'AllowBedrockAgents':
                bedrock_agent_policy = statement
            elif statement.get('Sid') == 'AllowSSMParameterAccess':
                ssm_policy = statement
        
        # Validate Bedrock Agent policy
        if bedrock_agent_policy:
            required_actions = [
                'bedrock-agent-runtime:InvokeAgent',
                'bedrock-agent:GetAgent',
                'bedrock-agent:ListAgents'
            ]
            actions = bedrock_agent_policy.get('Action', [])
            
            missing_actions = [a for a in required_actions if a not in actions]
            if not missing_actions:
                print("   ✅ Bedrock Agent IAM permissions exist")
                validation_results.append(True)
            else:
                print(f"   ❌ Missing Bedrock Agent actions: {missing_actions}")
                validation_results.append(False)
        else:
            print("   ❌ AllowBedrockAgents policy statement missing")
            validation_results.append(False)
        
        # Validate SSM Parameter Store policy
        if ssm_policy:
            required_ssm_actions = [
                'ssm:GetParameter',
                'ssm:GetParameters',
                'ssm:GetParametersByPath'
            ]
            ssm_actions = ssm_policy.get('Action', [])
            
            missing_ssm = [a for a in required_ssm_actions if a not in ssm_actions]
            if not missing_ssm:
                print("   ✅ SSM Parameter Store IAM permissions exist")
                validation_results.append(True)
            else:
                print(f"   ❌ Missing SSM actions: {missing_ssm}")
                validation_results.append(False)
        else:
            print("   ❌ AllowSSMParameterAccess policy statement missing")
            validation_results.append(False)
    
    # Summary
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    
    total_checks = len(validation_results)
    passed_checks = sum(validation_results)
    
    print(f"Passed: {passed_checks}/{total_checks} checks")
    
    if all(validation_results):
        print("\n✅ ALL VALIDATIONS PASSED - Task 7 Complete!")
        print("\nNext Steps:")
        print("1. Deploy the updated template: sam build && sam deploy")
        print("2. Run agent setup script: python3 scripts/setup_bedrock_agents.py")
        print("3. Test agent invocations")
        return 0
    else:
        print("\n❌ SOME VALIDATIONS FAILED")
        print("Please review the errors above and fix the template.yaml")
        return 1

if __name__ == '__main__':
    try:
        sys.exit(validate_template())
    except Exception as e:
        print(f"\n❌ Validation error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
