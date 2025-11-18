# Bedrock Multi-Agent Architecture - Deployment Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Agent Setup](#agent-setup)
3. [Verification](#verification)
4. [Troubleshooting](#troubleshooting)
5. [Updating Agent Instructions](#updating-agent-instructions)
6. [Demo Presentation Guide](#demo-presentation-guide)

---

## Prerequisites

Before deploying the Bedrock multi-agent architecture, ensure you have:

### AWS Requirements
- AWS Account with appropriate permissions
- AWS CLI configured with credentials
- Access to AWS Bedrock service in your region
- IAM permissions to:
  - Create and manage Bedrock agents
  - Create IAM roles and policies
  - Write to Systems Manager Parameter Store
  - Invoke Bedrock agents

### Software Requirements
- Python 3.9 or higher
- boto3 library installed (`pip install boto3`)
- AWS SAM CLI (for Lambda deployment)

### Environment Setup
```bash
# Install required Python packages
pip install boto3 requests

# Verify AWS credentials
aws sts get-caller-identity

# Check Bedrock service availability in your region
aws bedrock list-foundation-models --region us-east-1
```

---

## Agent Setup

This step-by-step guide walks you through deploying the Bedrock multi-agent architecture.

### Step 1: Run the Agent Setup Script

The agent setup script creates all 6 Bedrock agents with their configurations.

```bash
# Navigate to the scripts directory
cd scripts

# Run the setup script
python setup_bedrock_agents.py
```

**Expected Output:**
```
🚀 Starting Bedrock Agent Setup...

Creating IAM roles for agents...
✅ Created IAM role: CurioNewsContentCuratorRole
✅ Created IAM role: CurioNewsSocialImpactAnalyzerRole
✅ Created IAM role: CurioNewsStorySelectorRole
✅ Created IAM role: CurioNewsScriptWriterRole
✅ Created IAM role: CurioNewsEntertainmentCuratorRole
✅ Created IAM role: CurioNewsMediaEnhancerRole

Creating Bedrock agents...
✅ Created agent: CurioNews-ContentCurator (agent-id: ABC123XYZ)
✅ Created agent: CurioNews-SocialImpactAnalyzer (agent-id: DEF456UVW)
✅ Created agent: CurioNews-StorySelector (agent-id: GHI789RST)
✅ Created agent: CurioNews-ScriptWriter (agent-id: JKL012OPQ)
✅ Created agent: CurioNews-EntertainmentCurator (agent-id: MNO345LMN)
✅ Created agent: CurioNews-MediaEnhancer (agent-id: PQR678IJK)

Preparing agents (creating aliases)...
✅ Prepared agent: CurioNews-ContentCurator
✅ Prepared agent: CurioNews-SocialImpactAnalyzer
✅ Prepared agent: CurioNews-StorySelector
✅ Prepared agent: CurioNews-ScriptWriter
✅ Prepared agent: CurioNews-EntertainmentCurator
✅ Prepared agent: CurioNews-MediaEnhancer

Storing agent IDs in Parameter Store...
✅ Stored parameter: /curio-news/agents/content-curator
✅ Stored parameter: /curio-news/agents/social-impact-analyzer
✅ Stored parameter: /curio-news/agents/story-selector
✅ Stored parameter: /curio-news/agents/script-writer
✅ Stored parameter: /curio-news/agents/entertainment-curator
✅ Stored parameter: /curio-news/agents/media-enhancer

🎉 All agents created successfully!

Agent Summary:
- Total agents created: 6
- All agents prepared with PROD aliases
- Agent IDs stored in Parameter Store
- Ready for Lambda integration
```

### Step 2: Verify Agent Creation

After running the setup script, verify the agents were created successfully:

```bash
# Run the verification test
python test_bedrock_setup.py
```

**Expected Output:**
```
Testing Bedrock Agent Setup...

✅ All 6 agents found in Parameter Store
✅ Content Curator agent accessible
✅ Social Impact Analyzer agent accessible
✅ Story Selector agent accessible
✅ Script Writer agent accessible
✅ Entertainment Curator agent accessible
✅ Media Enhancer agent accessible

All agents verified successfully!
```

### Step 3: Deploy Lambda Orchestrator

Update the Lambda function with the new orchestrator:

```bash
# Build and deploy with SAM
sam build
sam deploy --guided

# Or use the deployment script
./scripts/deploy.sh
```

### Step 4: Test End-to-End Flow

Verify the complete multi-agent pipeline:

```bash
# Run integration test
cd api
python test_bedrock_integration.py
```

---

## Verification

### Verify Agents in AWS Bedrock Console

1. **Navigate to AWS Bedrock Console**
   - Open AWS Console
   - Go to Services → Amazon Bedrock
   - Click "Agents" in the left sidebar

2. **Check Agent List**
   
   You should see 6 agents:
   - `CurioNews-ContentCurator`
   - `CurioNews-SocialImpactAnalyzer`
   - `CurioNews-StorySelector`
   - `CurioNews-ScriptWriter`
   - `CurioNews-EntertainmentCurator`
   - `CurioNews-MediaEnhancer`

3. **Verify Agent Configuration**
   
   For each agent, click to view details and verify:
   - **Status**: Should be "Prepared" or "Ready"
   - **Model**: Claude 3.5 Sonnet (anthropic.claude-3-5-sonnet-20241022-v2:0)
   - **Instructions**: Should contain detailed role-specific instructions
   - **Alias**: Should have a "PROD" alias

4. **Check IAM Roles**
   
   Navigate to IAM → Roles and verify:
   - Each agent has a corresponding IAM role
   - Roles have appropriate Bedrock permissions
   - Trust relationships are configured correctly

5. **Verify Parameter Store**
   
   Navigate to Systems Manager → Parameter Store:
   ```
   /curio-news/agents/content-curator
   /curio-news/agents/social-impact-analyzer
   /curio-news/agents/story-selector
   /curio-news/agents/script-writer
   /curio-news/agents/entertainment-curator
   /curio-news/agents/media-enhancer
   ```

### Test Individual Agents

Test each agent independently using the AWS Console:

1. Go to Bedrock → Agents → Select an agent
2. Click "Test" tab
3. Enter sample input:
   ```json
   {
     "news_items": [
       {
         "title": "Community Garden Initiative Transforms Urban Neighborhood",
         "summary": "Local residents create sustainable food source",
         "category": "Community",
         "source": "Local News"
       }
     ]
   }
   ```
4. Click "Run" and verify the agent responds appropriately

---

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: "AccessDeniedException" when creating agents

**Symptom:**
```
botocore.exceptions.ClientError: An error occurred (AccessDeniedException) 
when calling the CreateAgent operation
```

**Solution:**
1. Verify your AWS credentials have Bedrock permissions:
   ```bash
   aws bedrock list-foundation-models --region us-east-1
   ```

2. Add required IAM permissions to your user/role:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "bedrock:CreateAgent",
           "bedrock:GetAgent",
           "bedrock:PrepareAgent",
           "bedrock:CreateAgentAlias",
           "iam:CreateRole",
           "iam:AttachRolePolicy",
           "iam:PassRole",
           "ssm:PutParameter"
         ],
         "Resource": "*"
       }
     ]
   }
   ```

3. Ensure Bedrock is available in your region (us-east-1 recommended)

#### Issue 2: "ResourceNotFoundException" for foundation model

**Symptom:**
```
Model 'anthropic.claude-3-5-sonnet-20241022-v2:0' not found
```

**Solution:**
1. Check available models in your region:
   ```bash
   aws bedrock list-foundation-models --region us-east-1 \
     --query 'modelSummaries[?contains(modelId, `claude`)].modelId'
   ```

2. Update the model ID in `setup_bedrock_agents.py` if needed:
   ```python
   foundation_model = "anthropic.claude-3-5-sonnet-20240620-v1:0"  # Fallback model
   ```

3. Request model access in Bedrock console if not available

#### Issue 3: Agent creation succeeds but agent not "Prepared"

**Symptom:**
```
Agent created but status is 'NOT_PREPARED'
```

**Solution:**
1. The setup script should automatically prepare agents
2. If not, manually prepare in console or run:
   ```bash
   aws bedrock-agent prepare-agent --agent-id <AGENT_ID>
   ```

3. Wait 30-60 seconds for preparation to complete
4. Verify status:
   ```bash
   aws bedrock-agent get-agent --agent-id <AGENT_ID>
   ```

#### Issue 4: Lambda can't find agent IDs

**Symptom:**
```
KeyError: 'CONTENT_CURATOR_AGENT_ID' in Lambda logs
```

**Solution:**
1. Verify Parameter Store values exist:
   ```bash
   aws ssm get-parameters-by-path --path /curio-news/agents/
   ```

2. Update Lambda environment variables in SAM template:
   ```yaml
   Environment:
     Variables:
       CONTENT_CURATOR_AGENT_ID: '{{resolve:ssm:/curio-news/agents/content-curator}}'
   ```

3. Redeploy Lambda:
   ```bash
   sam build && sam deploy
   ```

#### Issue 5: Agent invocation times out

**Symptom:**
```
Agent invocation exceeded 30 second timeout
```

**Solution:**
1. Increase Lambda timeout in template.yaml:
   ```yaml
   Timeout: 180  # 3 minutes
   ```

2. Check agent instructions aren't too complex
3. Reduce input data size if very large
4. Monitor CloudWatch logs for bottlenecks

#### Issue 6: Agents return malformed JSON

**Symptom:**
```
JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

**Solution:**
1. Review agent instructions to ensure JSON output format is clear
2. Add JSON validation in agent instructions:
   ```
   CRITICAL: Your response MUST be valid JSON. Do not include any text before or after the JSON object.
   ```

3. Update orchestrator to handle partial responses:
   ```python
   try:
       result = json.loads(response_text)
   except json.JSONDecodeError:
       # Extract JSON from response
       json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
       if json_match:
           result = json.loads(json_match.group())
   ```

### Debug Mode

Enable detailed logging for troubleshooting:

```python
# In bedrock_orchestrator.py
import logging
logging.basicConfig(level=logging.DEBUG)

# Or set environment variable
export BEDROCK_DEBUG=true
```

### Getting Help

If issues persist:

1. Check CloudWatch Logs for Lambda function
2. Review Bedrock agent execution logs in console
3. Run validation script with verbose output:
   ```bash
   python test_bedrock_setup.py --verbose
   ```

4. Check AWS Service Health Dashboard for Bedrock issues

---

## Updating Agent Instructions

### When to Update Instructions

Update agent instructions when you need to:
- Refine agent behavior or output format
- Add new capabilities or features
- Fix issues with agent responses
- Improve social impact scoring criteria
- Adjust tone or style guidelines

### Method 1: Update via AWS Console (Recommended for Testing)

1. **Navigate to Agent**
   - AWS Console → Bedrock → Agents
   - Click on the agent you want to update

2. **Edit Instructions**
   - Scroll to "Instructions" section
   - Click "Edit"
   - Modify the instructions text
   - Click "Save"

3. **Prepare Agent**
   - After saving, click "Prepare agent"
   - Wait for preparation to complete (30-60 seconds)
   - Status should change to "Prepared"

4. **Test Changes**
   - Use the "Test" tab to verify new behavior
   - Ensure output format remains consistent

### Method 2: Update via Script (Recommended for Production)

1. **Update Instructions in Script**
   
   Edit `scripts/setup_bedrock_agents.py`:
   ```python
   # Find the agent configuration
   agents_config = {
       'content_curator': {
           'name': 'CurioNews-ContentCurator',
           'instructions': '''
           [Your updated instructions here]
           ''',
           'model': 'anthropic.claude-3-5-sonnet-20241022-v2:0'
       }
   }
   ```

2. **Run Update Script**
   ```bash
   python setup_bedrock_agents.py --update-only
   ```

3. **Verify Changes**
   ```bash
   python test_bedrock_setup.py
   ```

### Method 3: Update via AWS CLI

```bash
# Update agent instructions
aws bedrock-agent update-agent \
  --agent-id <AGENT_ID> \
  --agent-name "CurioNews-ContentCurator" \
  --foundation-model "anthropic.claude-3-5-sonnet-20241022-v2:0" \
  --instruction "$(cat updated_instructions.txt)"

# Prepare the updated agent
aws bedrock-agent prepare-agent --agent-id <AGENT_ID>
```

### Best Practices for Instruction Updates

1. **Test in Development First**
   - Create a test agent with new instructions
   - Validate behavior before updating production

2. **Version Control**
   - Keep instruction versions in git
   - Document changes in commit messages

3. **Gradual Rollout**
   - Update one agent at a time
   - Monitor performance after each update

4. **Maintain Output Format**
   - Ensure JSON structure remains consistent
   - Don't break downstream dependencies

5. **Document Changes**
   - Update design.md with instruction changes
   - Note the reason for updates

### Example: Updating Social Impact Scoring

```python
# Original instructions
'''
SCORING CRITERIA:
- Social Impact: +5 points
- Scientific Breakthroughs: +4 points
'''

# Updated instructions
'''
SCORING CRITERIA:
- Social Impact: +5 points (community benefit, social justice, environmental progress)
- Scientific Breakthroughs: +4 points (medical advances, research discoveries)
- Educational Value: +3 points (learning opportunities, skill development)
- Cultural Significance: +3 points (arts, diversity, representation)
- Financial/Market News: -2 points (limited social impact)
'''
```

---

## Demo Presentation Guide

### Overview

This guide helps you present the Bedrock multi-agent architecture to hackathon judges, highlighting the technical sophistication and social impact focus.

### Pre-Demo Checklist

- [ ] All 6 agents visible in AWS Bedrock console
- [ ] Lambda orchestrator deployed and tested
- [ ] Frontend agent collaboration UI working
- [ ] Test run completed successfully (<10 seconds)
- [ ] AWS console open to Bedrock Agents page
- [ ] Demo script prepared and rehearsed

### Demo Flow (5 minutes)

#### 1. Introduction (30 seconds)

**Script:**
> "Curio News uses a sophisticated multi-agent architecture powered by AWS Bedrock. Instead of a single AI model, we have 6 specialized agents that collaborate to create socially impactful news content for Gen Z and Millennials."

**Show:**
- Open AWS Bedrock console
- Display list of 6 agents

#### 2. Agent Architecture Overview (1 minute)

**Script:**
> "Let me show you our agent collaboration flow. Each agent has a specific role:"

**Show AWS Console - Click through each agent:**

1. **Content Curator Agent**
   - "Discovers and filters news from multiple sources"
   - "Scores stories based on social impact criteria"

2. **Social Impact Analyzer Agent**
   - "Evaluates stories for community benefit"
   - "Prioritizes environmental, health, and social justice themes"

3. **Story Selector Agent**
   - "Chooses the most impactful story of the day"
   - "Explains why it matters to younger generations"

4. **Script Writer Agent**
   - "Creates engaging, conversational audio scripts"
   - "Emphasizes positive change and community progress"

5. **Entertainment Curator Agent**
   - "Recommends culturally significant entertainment"
   - "Connects recommendations to current social themes"

6. **Media Enhancer Agent**
   - "Optimizes visual content and accessibility"
   - "Generates social media optimization"

#### 3. Live Agent Collaboration (2 minutes)

**Script:**
> "Now let's see these agents work together in real-time."

**Show Frontend:**
1. Click "Generate Today's News"
2. Point out Agent Collaboration Trace appearing
3. Highlight each agent as it executes:
   - "Content Curator is analyzing 15 news sources..."
   - "Social Impact Analyzer is scoring stories..."
   - "Story Selector is choosing the most impactful story..."
   - "Script Writer is creating the audio script..."

**Key Points to Emphasize:**
- Agents execute in parallel where possible (Phases 1 & 4)
- Each agent builds on previous agents' work
- Total execution time under 10 seconds
- Real AWS Bedrock agents, not simulated

#### 4. Social Impact Focus (1 minute)

**Script:**
> "What makes this special is our focus on social impact. Let me show you the selected story."

**Show:**
- Favorite story with social impact reasoning
- Point out: "Selected as today's most socially impactful story"
- Highlight social themes: community, environment, health, justice

**Explain:**
> "Our agents actively deprioritize financial market news and corporate earnings. Instead, they surface stories about community initiatives, environmental progress, and social change that Gen Z and Millennials care about."

#### 5. Technical Deep Dive (30 seconds)

**Script:**
> "From a technical perspective, this is a true multi-agent system:"

**Show AWS Console:**
- Click on one agent to show configuration
- Point out detailed instructions
- Show Claude 3.5 Sonnet model
- Mention IAM roles and security

**Key Technical Points:**
- 6 independent Bedrock agents
- Lightweight Lambda orchestrator (<300 lines)
- Agent-to-agent data flow
- Graceful error handling
- Sub-10-second performance

### Demo Tips

#### Do's
✅ Practice the demo multiple times before presenting
✅ Have AWS console and frontend open in separate tabs
✅ Emphasize the social impact mission
✅ Show actual agent execution, not mocked data
✅ Be prepared to explain technical architecture
✅ Highlight the multi-agent collaboration visually

#### Don'ts
❌ Don't skip showing the AWS Bedrock console
❌ Don't rush through the agent collaboration trace
❌ Don't forget to mention social impact scoring
❌ Don't use cached/pre-generated content
❌ Don't ignore if an agent fails (explain graceful degradation)

### Handling Questions

**Q: "Why use multiple agents instead of one?"**
> "Each agent is specialized for a specific task, making the system more maintainable and allowing us to optimize each agent's instructions independently. It also demonstrates true multi-agent collaboration, which is a key AWS Bedrock capability."

**Q: "How do you ensure social impact focus?"**
> "Our Social Impact Analyzer agent uses explicit scoring criteria that prioritize community benefit, environmental progress, and social justice. Stories about stock markets or corporate earnings are actively deprioritized."

**Q: "What happens if an agent fails?"**
> "Our orchestrator implements graceful degradation. If one agent fails, the system continues with the remaining agents and uses fallback logic to ensure users still get content."

**Q: "How fast is the system?"**
> "The complete multi-agent pipeline executes in under 10 seconds. We optimize by running independent agents in parallel - for example, Content Curator and Social Impact Analyzer run simultaneously."

**Q: "Can you show the agent instructions?"**
> [Open AWS console, click an agent, scroll to instructions]
> "Each agent has detailed instructions defining its role, responsibilities, and output format. For example, the Story Selector has explicit criteria to prioritize social impact over financial news."

### Backup Plan

If live demo fails:
1. Have screenshots/video of successful run ready
2. Show CloudWatch logs demonstrating agent execution
3. Walk through agent configurations in AWS console
4. Explain the architecture using the design document

### Post-Demo

After the demo, be ready to:
- Share GitHub repository with judges
- Provide architecture diagrams
- Discuss scalability and future enhancements
- Answer technical implementation questions

---

## Agent Collaboration Flow Diagram

### Visual Flow for Presentation

```
┌─────────────────────────────────────────────────────────────────┐
│                    CURIO NEWS MULTI-AGENT SYSTEM                 │
└─────────────────────────────────────────────────────────────────┘

PHASE 1: PARALLEL ANALYSIS (1.5s)
┌──────────────────────┐         ┌──────────────────────┐
│  Content Curator     │         │ Social Impact        │
│  Agent               │         │ Analyzer Agent       │
│                      │         │                      │
│ • Discover news      │         │ • Score social       │
│ • Filter quality     │         │   impact             │
│ • Curate stories     │         │ • Identify themes    │
└──────────┬───────────┘         └──────────┬───────────┘
           │                                 │
           └────────────┬────────────────────┘
                        ▼
              ┌─────────────────────┐
              │   Curated Stories   │
              │   + Impact Scores   │
              └──────────┬──────────┘
                         │
                         ▼
PHASE 2: STORY SELECTION (0.7s)
              ┌──────────────────────┐
              │  Story Selector      │
              │  Agent               │
              │                      │
              │ • Choose favorite    │
              │ • Explain impact     │
              │ • Gen Z focus        │
              └──────────┬───────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │   Favorite Story    │
              │   + Reasoning       │
              └──────────┬──────────┘
                         │
                         ▼
PHASE 3: SCRIPT CREATION (1.8s)
              ┌──────────────────────┐
              │  Script Writer       │
              │  Agent               │
              │                      │
              │ • Write script       │
              │ • Conversational     │
              │ • Social focus       │
              └──────────┬───────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │   Audio Script      │
              └──────────┬──────────┘
                         │
                         ▼
PHASE 4: PARALLEL ENHANCEMENT (1.2s)
┌──────────────────────┐         ┌──────────────────────┐
│  Entertainment       │         │  Media Enhancer      │
│  Curator Agent       │         │  Agent               │
│                      │         │                      │
│ • Recommend shows    │         │ • Alt text           │
│ • Cultural themes    │         │ • Social media       │
│ • Social relevance   │         │ • Accessibility      │
└──────────┬───────────┘         └──────────┬───────────┘
           │                                 │
           └────────────┬────────────────────┘
                        ▼
              ┌─────────────────────┐
              │  Final Response     │
              │  • News stories     │
              │  • Audio script     │
              │  • Entertainment    │
              │  • Media assets     │
              └─────────────────────┘

TOTAL EXECUTION TIME: ~5.8 seconds
```

### Key Metrics for Judges

- **6 Specialized Agents**: Each with distinct role and instructions
- **5 Execution Phases**: Optimized for parallel processing
- **Sub-10 Second Performance**: Fast enough for real-time use
- **Social Impact Focus**: Explicit scoring and prioritization
- **Graceful Degradation**: System continues if agents fail
- **True Multi-Agent**: Real AWS Bedrock agents, not simulated

---

## Appendix

### Agent ID Reference

After setup, your agent IDs will be stored in Parameter Store:

```
/curio-news/agents/content-curator          → AGENT_ID_1
/curio-news/agents/social-impact-analyzer   → AGENT_ID_2
/curio-news/agents/story-selector           → AGENT_ID_3
/curio-news/agents/script-writer            → AGENT_ID_4
/curio-news/agents/entertainment-curator    → AGENT_ID_5
/curio-news/agents/media-enhancer           → AGENT_ID_6
```

### Useful AWS CLI Commands

```bash
# List all Bedrock agents
aws bedrock-agent list-agents

# Get agent details
aws bedrock-agent get-agent --agent-id <AGENT_ID>

# List agent aliases
aws bedrock-agent list-agent-aliases --agent-id <AGENT_ID>

# Invoke agent (for testing)
aws bedrock-agent-runtime invoke-agent \
  --agent-id <AGENT_ID> \
  --agent-alias-id PROD \
  --session-id test-session \
  --input-text '{"test": "data"}'

# Get Parameter Store values
aws ssm get-parameters-by-path --path /curio-news/agents/

# View CloudWatch logs
aws logs tail /aws/lambda/curio-news-bootstrap --follow
```

### Related Documentation

- [Design Document](design.md) - Detailed architecture and agent instructions
- [Requirements Document](requirements.md) - System requirements and acceptance criteria
- [Agent Setup Summary](../../scripts/AGENT_SETUP_SUMMARY.md) - Quick reference for agent setup
- [Agent Reference](../../scripts/AGENT_REFERENCE.md) - Agent IDs and configurations

### Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review CloudWatch logs for error details
3. Consult AWS Bedrock documentation
4. Check the GitHub repository issues

---

**Document Version**: 1.0  
**Last Updated**: October 31, 2025  
**Maintained By**: Curio News Development Team
