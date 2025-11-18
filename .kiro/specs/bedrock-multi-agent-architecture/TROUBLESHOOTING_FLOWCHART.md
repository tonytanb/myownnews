# Bedrock Multi-Agent Troubleshooting Flowchart

## Quick Diagnosis Guide

### Problem: Agent Setup Script Fails

```
START: Agent setup script fails
    |
    ├─> Error: "AccessDeniedException"
    |   └─> Check AWS credentials
    |       ├─> Run: aws sts get-caller-identity
    |       ├─> Verify Bedrock permissions
    |       └─> Add required IAM policies
    |
    ├─> Error: "ResourceNotFoundException" (model)
    |   └─> Check model availability
    |       ├─> Run: aws bedrock list-foundation-models
    |       ├─> Verify region (use us-east-1)
    |       └─> Update model ID in script
    |
    ├─> Error: "ValidationException"
    |   └─> Check agent configuration
    |       ├─> Verify agent name format
    |       ├─> Check instruction length (<10000 chars)
    |       └─> Validate IAM role ARN format
    |
    └─> Error: "ThrottlingException"
        └─> Rate limit exceeded
            ├─> Wait 60 seconds
            ├─> Add retry logic with backoff
            └─> Reduce concurrent agent creation
```

### Problem: Agents Not Visible in Console

```
START: Agents not showing in Bedrock console
    |
    ├─> Check correct AWS region
    |   └─> Agents created in us-east-1?
    |       ├─> YES: Continue
    |       └─> NO: Switch region or recreate
    |
    ├─> Check agent creation status
    |   └─> Run: aws bedrock-agent list-agents
    |       ├─> Agents listed: Console refresh issue
    |       └─> No agents: Creation failed
    |
    └─> Verify IAM permissions
        └─> Can you view Bedrock resources?
            ├─> YES: Contact AWS support
            └─> NO: Add bedrock:ListAgents permission
```

### Problem: Agent Invocation Fails

```
START: Agent invocation fails in Lambda
    |
    ├─> Error: "ResourceNotFoundException"
    |   └─> Agent ID incorrect
    |       ├─> Check Parameter Store values
    |       ├─> Verify environment variables
    |       └─> Confirm agent exists in console
    |
    ├─> Error: "AccessDeniedException"
    |   └─> Lambda lacks permissions
    |       ├─> Check Lambda execution role
    |       ├─> Add bedrock:InvokeAgent permission
    |       └─> Verify agent resource ARN
    |
    ├─> Error: "ValidationException"
    |   └─> Invalid input format
    |       ├─> Check input is valid JSON
    |       ├─> Verify input size (<25KB)
    |       └─> Review agent instructions
    |
    └─> Error: "ThrottlingException"
        └─> Rate limit exceeded
            ├─> Implement exponential backoff
            ├─> Add request queuing
            └─> Request quota increase
```

### Problem: Agent Returns Malformed Response

```
START: Agent response not valid JSON
    |
    ├─> Response contains extra text
    |   └─> Agent instructions unclear
    |       ├─> Add: "MUST return ONLY valid JSON"
    |       ├─> Add: "No text before/after JSON"
    |       └─> Update and prepare agent
    |
    ├─> Response is truncated
    |   └─> Output too large
    |       ├─> Reduce output requirements
    |       ├─> Simplify response format
    |       └─> Split into multiple calls
    |
    └─> Response format inconsistent
        └─> Agent instructions ambiguous
            ├─> Provide explicit JSON schema
            ├─> Add example outputs
            └─> Test with various inputs
```

### Problem: Performance Issues

```
START: Multi-agent pipeline too slow (>10s)
    |
    ├─> Individual agent slow (>3s)
    |   └─> Optimize agent
    |       ├─> Simplify instructions
    |       ├─> Reduce input data size
    |       ├─> Check model performance
    |       └─> Consider faster model
    |
    ├─> Sequential execution bottleneck
    |   └─> Optimize orchestration
    |       ├─> Identify independent agents
    |       ├─> Run in parallel with asyncio
    |       └─> Review phase dependencies
    |
    └─> Network latency
        └─> Infrastructure optimization
            ├─> Use same region for all resources
            ├─> Increase Lambda memory (faster CPU)
            └─> Enable VPC endpoints for Bedrock
```

### Problem: Social Impact Scoring Not Working

```
START: Wrong stories being selected
    |
    ├─> Financial news prioritized
    |   └─> Check Social Impact Analyzer
    |       ├─> Review scoring criteria
    |       ├─> Verify negative scores for finance
    |       └─> Update instructions
    |
    ├─> Low-quality stories selected
    |   └─> Check Content Curator
    |       ├─> Review filtering logic
    |       ├─> Adjust quality thresholds
    |       └─> Add source credibility check
    |
    └─> Story Selector ignoring scores
        └─> Check Story Selector agent
            ├─> Verify it receives impact scores
            ├─> Review selection criteria
            └─> Add explicit social impact priority
```

## Diagnostic Commands

### Check Agent Status
```bash
# List all agents
aws bedrock-agent list-agents --region us-east-1

# Get specific agent details
aws bedrock-agent get-agent --agent-id <AGENT_ID> --region us-east-1

# Check agent aliases
aws bedrock-agent list-agent-aliases --agent-id <AGENT_ID> --region us-east-1
```

### Check Parameter Store
```bash
# List all agent parameters
aws ssm get-parameters-by-path --path /curio-news/agents/ --region us-east-1

# Get specific parameter
aws ssm get-parameter --name /curio-news/agents/content-curator --region us-east-1
```

### Check Lambda Configuration
```bash
# Get Lambda function details
aws lambda get-function --function-name curio-news-bootstrap

# Check environment variables
aws lambda get-function-configuration --function-name curio-news-bootstrap \
  --query 'Environment.Variables'

# View recent logs
aws logs tail /aws/lambda/curio-news-bootstrap --follow
```

### Test Agent Invocation
```bash
# Invoke agent directly (for testing)
aws bedrock-agent-runtime invoke-agent \
  --agent-id <AGENT_ID> \
  --agent-alias-id PROD \
  --session-id test-$(date +%s) \
  --input-text '{"test": "data"}' \
  --region us-east-1 \
  output.txt

# View response
cat output.txt
```

## Common Error Messages

### "Agent not prepared"
**Cause:** Agent created but not prepared for invocation  
**Fix:** Run `aws bedrock-agent prepare-agent --agent-id <AGENT_ID>`  
**Wait:** 30-60 seconds for preparation to complete

### "Session not found"
**Cause:** Invalid or expired session ID  
**Fix:** Generate new session ID: `session-$(date +%s)`  
**Note:** Each invocation should use unique session ID

### "Input text too large"
**Cause:** Input exceeds 25KB limit  
**Fix:** Reduce input size or split into multiple calls  
**Alternative:** Use S3 for large inputs (requires action group)

### "Model not found"
**Cause:** Foundation model not available in region  
**Fix:** Check available models with `aws bedrock list-foundation-models`  
**Alternative:** Use different model or region

### "Quota exceeded"
**Cause:** Too many concurrent invocations  
**Fix:** Implement rate limiting and retry logic  
**Long-term:** Request quota increase from AWS

## Health Check Script

Create `check_agent_health.py`:

```python
import boto3
import json

def check_agent_health():
    bedrock = boto3.client('bedrock-agent', region_name='us-east-1')
    ssm = boto3.client('ssm', region_name='us-east-1')
    
    print("🔍 Checking Agent Health...\n")
    
    # Check Parameter Store
    try:
        params = ssm.get_parameters_by_path(Path='/curio-news/agents/')
        agent_ids = {p['Name'].split('/')[-1]: p['Value'] for p in params['Parameters']}
        print(f"✅ Found {len(agent_ids)} agent IDs in Parameter Store")
    except Exception as e:
        print(f"❌ Parameter Store error: {e}")
        return
    
    # Check each agent
    for name, agent_id in agent_ids.items():
        try:
            response = bedrock.get_agent(agentId=agent_id)
            status = response['agent']['agentStatus']
            
            if status == 'PREPARED':
                print(f"✅ {name}: {status}")
            else:
                print(f"⚠️  {name}: {status} (needs preparation)")
        except Exception as e:
            print(f"❌ {name}: {e}")
    
    print("\n✅ Health check complete!")

if __name__ == '__main__':
    check_agent_health()
```

Run with: `python check_agent_health.py`

## Escalation Path

### Level 1: Self-Service (5-10 minutes)
1. Check this troubleshooting guide
2. Review CloudWatch logs
3. Run diagnostic commands
4. Check AWS Service Health Dashboard

### Level 2: Documentation (10-20 minutes)
1. Review [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
2. Check [design.md](design.md) for architecture details
3. Review AWS Bedrock documentation
4. Search GitHub issues

### Level 3: Testing (20-30 minutes)
1. Run `test_bedrock_setup.py` with verbose output
2. Test individual agents in AWS console
3. Check Lambda function locally with SAM
4. Review integration test results

### Level 4: Support (30+ minutes)
1. Create detailed issue report with:
   - Error messages and stack traces
   - CloudWatch log excerpts
   - Agent configurations
   - Steps to reproduce
2. Contact AWS Support for Bedrock issues
3. Post in AWS Bedrock forums
4. Consult with team members

## Prevention Checklist

### Before Deployment
- [ ] Test all agents individually in console
- [ ] Run full integration test suite
- [ ] Verify Parameter Store values
- [ ] Check Lambda IAM permissions
- [ ] Confirm all agents are PREPARED status
- [ ] Test with sample inputs
- [ ] Measure performance (<10s target)

### After Deployment
- [ ] Monitor CloudWatch metrics
- [ ] Set up alarms for failures
- [ ] Review logs for errors
- [ ] Test end-to-end flow
- [ ] Verify agent collaboration trace
- [ ] Check social impact scoring
- [ ] Measure success rate (>90% target)

### Regular Maintenance
- [ ] Weekly: Review CloudWatch logs
- [ ] Weekly: Check agent performance metrics
- [ ] Monthly: Update agent instructions if needed
- [ ] Monthly: Review and optimize costs
- [ ] Quarterly: Test disaster recovery
- [ ] Quarterly: Update documentation

---

**Quick Help:** For immediate assistance, run `python check_agent_health.py` to diagnose common issues.
