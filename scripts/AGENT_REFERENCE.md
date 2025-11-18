# Bedrock Agent Quick Reference

## Agent Overview

| Agent Key | Agent Name | Purpose | Model |
|-----------|------------|---------|-------|
| `content_curator` | curio-news-content-curator | Curate relevant news stories | Claude 3.5 Sonnet v2 |
| `social_impact_analyzer` | curio-news-social-impact-analyzer | Analyze social impact & generational appeal | Claude 3.5 Sonnet v2 |
| `story_selector` | curio-news-story-selector | Select most impactful favorite story | Claude 3.5 Sonnet v2 |
| `script_writer` | curio-news-script-writer | Create conversational audio scripts | Claude 3.5 Sonnet v2 |
| `entertainment_curator` | curio-news-entertainment-curator | Recommend socially relevant entertainment | Claude 3.5 Sonnet v2 |
| `media_enhancer` | curio-news-media-enhancer | Optimize visuals & accessibility | Claude 3.5 Sonnet v2 |

## Agent Collaboration Flow

```
Phase 1: Analysis (Parallel)
├─ Content Curator → Curated news list
└─ Social Impact Analyzer → Impact scores

Phase 2: Selection (Sequential)
└─ Story Selector (uses Phase 1) → Favorite story

Phase 3: Content Creation (Sequential)
└─ Script Writer (uses Favorite) → Audio script

Phase 4: Enhancement (Parallel)
├─ Entertainment Curator → Weekend recommendations
└─ Media Enhancer → Visual enhancements

Phase 5: Aggregation (Lambda)
└─ Combine all outputs → Final response
```

## Parameter Store Locations

```bash
# Individual agent IDs
/curio-news/bedrock-agents/content_curator/agent-id
/curio-news/bedrock-agents/content_curator/alias-id

/curio-news/bedrock-agents/social_impact_analyzer/agent-id
/curio-news/bedrock-agents/social_impact_analyzer/alias-id

/curio-news/bedrock-agents/story_selector/agent-id
/curio-news/bedrock-agents/story_selector/alias-id

/curio-news/bedrock-agents/script_writer/agent-id
/curio-news/bedrock-agents/script_writer/alias-id

/curio-news/bedrock-agents/entertainment_curator/agent-id
/curio-news/bedrock-agents/entertainment_curator/alias-id

/curio-news/bedrock-agents/media_enhancer/agent-id
/curio-news/bedrock-agents/media_enhancer/alias-id

# Consolidated JSON
/curio-news/bedrock-agents/all-agents
```

## IAM Role Names

```
CurioNewsBedrockAgent-content-curator
CurioNewsBedrockAgent-social-impact-analyzer
CurioNewsBedrockAgent-story-selector
CurioNewsBedrockAgent-script-writer
CurioNewsBedrockAgent-entertainment-curator
CurioNewsBedrockAgent-media-enhancer
```

## Agent Invocation (boto3)

```python
import boto3
import json

bedrock_agent_runtime = boto3.client('bedrock-agent-runtime')

response = bedrock_agent_runtime.invoke_agent(
    agentId='<agent-id>',
    agentAliasId='<alias-id>',  # Use 'LIVE' alias ID
    sessionId=f"session-{int(time.time())}",
    inputText=json.dumps({
        "news_items": [...],
        "context": {...}
    })
)

# Process streaming response
result = ""
for event in response['completion']:
    if 'chunk' in event:
        result += event['chunk']['bytes'].decode('utf-8')

output = json.loads(result)
```

## Expected Output Formats

### Content Curator
```json
{
  "curated_stories": [
    {
      "title": "Story title",
      "summary": "Brief summary",
      "category": "Category",
      "source": "Source name",
      "curator_score": 8.5,
      "social_impact_areas": ["community", "health"]
    }
  ],
  "total_analyzed": 15,
  "total_curated": 7
}
```

### Social Impact Analyzer
```json
{
  "high_impact_stories": [
    {
      "title": "Story title",
      "impact_score": 9.2,
      "impact_areas": ["environment", "community"],
      "generational_appeal": 8.5,
      "reasoning": "Why this matters"
    }
  ],
  "social_themes": {
    "community_impact": 3,
    "environmental_progress": 5
  }
}
```

### Story Selector
```json
{
  "favorite_story": {
    "title": "Selected story",
    "summary": "Summary",
    "category": "Category",
    "source": "Source",
    "image": "URL",
    "reasoning": "Why selected",
    "social_impact_score": 9.5,
    "generational_appeal": 8.8
  }
}
```

### Script Writer
```json
{
  "script": "Full audio script (250-300 words)",
  "word_count": 275,
  "estimated_duration_seconds": 110,
  "tone": "conversational, optimistic",
  "key_themes": ["community", "progress"]
}
```

### Entertainment Curator
```json
{
  "entertainment_recommendations": {
    "top_movies": [
      {
        "title": "Movie Title",
        "genre": "Documentary",
        "rating": "8.5/10",
        "platform": "Netflix",
        "description": "Why it matters",
        "social_themes": ["environment"]
      }
    ]
  }
}
```

### Media Enhancer
```json
{
  "media_enhancements": {
    "stories": [
      {
        "title": "Story title",
        "media_recommendations": {
          "images": [
            {
              "url": "Image URL",
              "alt_text": "Accessibility text"
            }
          ],
          "social_media_optimization": {
            "hashtags": ["#SocialImpact"],
            "suggested_caption": "Caption"
          }
        }
      }
    ]
  }
}
```

## AWS CLI Commands

### List Agents
```bash
aws bedrock-agent list-agents --region us-east-1
```

### Get Agent Details
```bash
aws bedrock-agent get-agent --agent-id <agent-id> --region us-east-1
```

### List Agent Aliases
```bash
aws bedrock-agent list-agent-aliases --agent-id <agent-id> --region us-east-1
```

### Get Parameter from Store
```bash
aws ssm get-parameter --name /curio-news/bedrock-agents/content_curator/agent-id --region us-east-1
```

### Get All Agents (Consolidated)
```bash
aws ssm get-parameter --name /curio-news/bedrock-agents/all-agents --region us-east-1 --query 'Parameter.Value' --output text | jq .
```

## Troubleshooting

### Agent Not Found
```bash
# Check if agent exists
aws bedrock-agent list-agents --region us-east-1 | grep curio-news

# Check Parameter Store
aws ssm get-parameter --name /curio-news/bedrock-agents/all-agents --region us-east-1
```

### Permission Denied
```bash
# Check IAM role
aws iam get-role --role-name CurioNewsBedrockAgent-content-curator

# Check role policy
aws iam get-role-policy --role-name CurioNewsBedrockAgent-content-curator --policy-name CurioNewsBedrockAgent-content-curator-permissions
```

### Agent Not Prepared
```bash
# Check agent status
aws bedrock-agent get-agent --agent-id <agent-id> --region us-east-1 --query 'agent.agentStatus'

# Prepare agent manually
aws bedrock-agent prepare-agent --agent-id <agent-id> --region us-east-1
```

## Performance Targets

- **Individual Agent**: < 2 seconds per invocation
- **Full Pipeline**: < 10 seconds total
- **Success Rate**: > 90%
- **Parallel Phases**: Execute simultaneously for speed

## Demo Checklist

- [ ] All 6 agents visible in AWS Bedrock Console
- [ ] Each agent has LIVE alias
- [ ] All agents show PREPARED status
- [ ] Parameter Store contains all agent IDs
- [ ] IAM roles properly configured
- [ ] Test invocation succeeds for each agent
- [ ] Multi-agent collaboration flow works end-to-end
