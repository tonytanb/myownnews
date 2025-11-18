# Bedrock Multi-Agent Setup Guide

This guide explains how to set up the 6 specialized Bedrock agents for Curio News.

## Prerequisites

1. AWS CLI configured with appropriate credentials
2. Python 3.8+ with boto3 installed
3. IAM permissions to:
   - Create IAM roles and policies
   - Create and manage Bedrock agents
   - Write to Systems Manager Parameter Store

## Agent Architecture

The setup creates 6 specialized agents:

1. **Content Curator** (`curio-news-content-curator`)
   - Discovers and curates relevant news stories
   - Scores stories based on social impact

2. **Social Impact Analyzer** (`curio-news-social-impact-analyzer`)
   - Analyzes stories for community benefit
   - Prioritizes Gen Z/Millennial values

3. **Story Selector** (`curio-news-story-selector`)
   - Selects the most impactful favorite story
   - Generates compelling reasoning

4. **Script Writer** (`curio-news-script-writer`)
   - Creates conversational audio scripts
   - Emphasizes social impact themes

5. **Entertainment Curator** (`curio-news-entertainment-curator`)
   - Recommends socially relevant entertainment
   - Connects to current news themes

6. **Media Enhancer** (`curio-news-media-enhancer`)
   - Optimizes visual content
   - Generates accessibility features

## Running the Setup

### Full Setup (Create All Agents)

```bash
python3 scripts/setup_bedrock_agents.py
```

### Specify AWS Region

```bash
python3 scripts/setup_bedrock_agents.py --region us-west-2
```

### Validate Existing Agents

```bash
python3 scripts/setup_bedrock_agents.py --validate-only
```

## What the Script Does

1. **Creates IAM Roles**: Each agent gets a dedicated IAM role with:
   - Trust policy for Bedrock service
   - Permissions to invoke Claude 3.5 Sonnet
   - CloudWatch logging permissions

2. **Creates Bedrock Agents**: Each agent is created with:
   - Unique name (no spaces, kebab-case)
   - Detailed instructions from design document
   - Multi-agent collaboration enabled
   - Claude 3.5 Sonnet v2 model

3. **Prepares Agents**: Creates working drafts for each agent

4. **Creates LIVE Aliases**: Production aliases for Lambda invocation

5. **Stores in Parameter Store**: Agent IDs saved at:
   - `/curio-news/bedrock-agents/{agent_key}/agent-id`
   - `/curio-news/bedrock-agents/{agent_key}/alias-id`
   - `/curio-news/bedrock-agents/all-agents` (consolidated JSON)

6. **Validates Setup**: Confirms all agents are ready

## Expected Output

```
============================================================
CURIO NEWS BEDROCK MULTI-AGENT SETUP
============================================================
Region: us-east-1
Account: 123456789012
Agents to create: 6
============================================================

STEP 1: Creating Bedrock Agents
------------------------------------------------------------
✓ Created IAM role: CurioNewsBedrockAgent-content-curator
✓ Created agent: curio-news-content-curator (ID: ABC123...)
...

STEP 2: Preparing Agents
------------------------------------------------------------
✓ Agent prepared: curio-news-content-curator
...

STEP 3: Creating Production Aliases
------------------------------------------------------------
✓ Alias created: LIVE (ID: XYZ789...)
...

STEP 4: Storing Agent IDs in Parameter Store
------------------------------------------------------------
✓ Stored parameter: /curio-news/bedrock-agents/content_curator/agent-id
...

STEP 5: Validating Agent Setup
------------------------------------------------------------
✓ curio-news-content-curator: READY
  Agent ID: ABC123...
  Alias ID: XYZ789...
...

============================================================
✓ ALL AGENTS CREATED SUCCESSFULLY!
============================================================
```

## Verifying in AWS Console

1. Navigate to AWS Bedrock Console
2. Go to "Agents" section
3. You should see 6 agents with names starting with `curio-news-`
4. Each agent should have:
   - Status: PREPARED
   - Model: Claude 3.5 Sonnet v2
   - Alias: LIVE

## Troubleshooting

### "NoSuchEntity" Error
- IAM role doesn't exist yet (script will create it)
- Wait 10 seconds for IAM propagation

### "ThrottlingException"
- Too many API calls
- Script will retry with exponential backoff

### "AccessDeniedException"
- Check IAM permissions for your AWS credentials
- Ensure you have Bedrock agent creation permissions

### Agent Preparation Timeout
- Bedrock service may be slow
- Script waits up to 60 seconds per agent
- Check AWS Bedrock console for agent status

## Next Steps

After successful setup:

1. **Verify in Console**: Check all 6 agents in AWS Bedrock
2. **Update Lambda**: Deploy the Bedrock orchestrator
3. **Test Pipeline**: Run end-to-end test with multi-agent flow
4. **Monitor Performance**: Check agent execution times

## Cleanup (If Needed)

To delete all agents and resources:

```bash
# Delete agents from AWS Console or use AWS CLI
aws bedrock-agent delete-agent --agent-id <agent-id> --region us-east-1

# Delete IAM roles
aws iam delete-role-policy --role-name CurioNewsBedrockAgent-content-curator --policy-name CurioNewsBedrockAgent-content-curator-permissions
aws iam delete-role --role-name CurioNewsBedrockAgent-content-curator

# Delete Parameter Store entries
aws ssm delete-parameter --name /curio-news/bedrock-agents/content_curator/agent-id
```

## Cost Considerations

- Agent creation: One-time, no cost
- Agent invocations: Charged per request
- Model usage: Claude 3.5 Sonnet pricing applies
- Estimated cost: ~$0.01-0.05 per full pipeline execution

## Support

For issues or questions:
1. Check AWS Bedrock documentation
2. Review CloudWatch logs for agent execution
3. Validate IAM permissions
4. Check Parameter Store for stored agent IDs
