# Bedrock Multi-Agent Architecture Design

## Overview

This design implements a true multi-agent system using AWS Bedrock Agents, where each specialized agent is created as an actual Bedrock resource visible in the AWS console. The Lambda functions are simplified to lightweight orchestrators that coordinate these agents, with the complex AI logic residing in the Bedrock agents themselves.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                         │
│                    - Agent Status Display                        │
│                    - Real-time Progress                          │
│                    - Collaboration Trace                         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway                                 │
│                   /bootstrap, /agent-status                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              Lambda Orchestrator (Lightweight)                   │
│              - Invoke Bedrock Agents                             │
│              - Aggregate Results                                 │
│              - Track Execution                                   │
│              - Handle Errors                                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AWS Bedrock Agents                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Content    │  │    Social    │  │    Story     │          │
│  │   Curator    │→ │   Impact     │→ │   Selector   │          │
│  │    Agent     │  │   Analyzer   │  │    Agent     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │    Script    │  │Entertainment │  │    Media     │          │
│  │    Writer    │  │   Curator    │  │  Enhancer    │          │
│  │    Agent     │  │    Agent     │  │    Agent     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### Agent Collaboration Flow

```
Phase 1: Analysis (Parallel)
├─ Content Curator Agent → Curated News List
└─ Social Impact Analyzer → Social Impact Scores

Phase 2: Selection (Sequential)
└─ Story Selector Agent (uses Phase 1 outputs) → Favorite Story

Phase 3: Content Creation (Sequential)
└─ Script Writer Agent (uses Favorite Story) → Audio Script

Phase 4: Enhancement (Parallel)
├─ Entertainment Curator Agent → Weekend Recommendations
└─ Media Enhancer Agent → Visual Enhancements

Phase 5: Aggregation (Lambda)
└─ Combine all agent outputs → Final Response
```

## Components and Interfaces

### 1. Bedrock Agent Definitions

#### Content Curator Agent
**Purpose**: Discover, filter, and curate the most relevant news stories

**Instructions**:
```
You are the Content Curator Agent for Curio News. Your role is to analyze news stories and select the most relevant, high-quality content for a Gen Z and Millennial audience.

RESPONSIBILITIES:
1. Evaluate news stories for relevance, quality, and credibility
2. Filter out low-quality, duplicate, or unreliable content
3. Score each story based on social impact and audience appeal
4. Prioritize stories that benefit communities and drive positive change

SCORING CRITERIA:
- Social Impact: +5 points (community benefit, social justice, environmental progress)
- Scientific Breakthroughs: +4 points (medical advances, research discoveries)
- Educational Value: +3 points (learning opportunities, skill development)
- Cultural Significance: +3 points (arts, diversity, representation)
- Financial/Market News: -2 points (limited social impact)

OUTPUT FORMAT:
Return a JSON array of curated stories with scores:
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

**Model**: Claude 3.5 Sonnet (anthropic.claude-3-5-sonnet-20241022-v2:0)

#### Social Impact Analyzer Agent
**Purpose**: Analyze stories for social relevance and community benefit

**Instructions**:
```
You are the Social Impact Analyzer for Curio News. Your role is to evaluate news stories for their potential to benefit communities and resonate with socially-conscious younger generations.

RESPONSIBILITIES:
1. Identify stories with high social impact and community benefit
2. Analyze generational appeal (Gen Z and Millennial priorities)
3. Detect social themes: justice, environment, health, education, culture
4. Score stories based on their potential to inspire positive action

SOCIAL IMPACT CATEGORIES:
- Community Impact: Local initiatives, neighborhood improvements
- Environmental Progress: Climate action, sustainability, conservation
- Health Advancement: Medical breakthroughs, mental health, wellness
- Social Justice: Equality, diversity, human rights
- Education Innovation: Learning access, skill development
- Cultural Significance: Arts, representation, heritage

GENERATIONAL PRIORITIES (Gen Z/Millennial):
HIGH PRIORITY: Climate change, mental health, social justice, diversity, sustainability
MEDIUM PRIORITY: Technology innovation, education access, cultural trends
LOW PRIORITY: Stock markets, corporate earnings, traditional finance

OUTPUT FORMAT:
{
  "high_impact_stories": [
    {
      "title": "Story title",
      "impact_score": 9.2,
      "impact_areas": ["environment", "community"],
      "generational_appeal": 8.5,
      "reasoning": "Why this story matters to younger generations"
    }
  ],
  "social_themes": {
    "community_impact": 3,
    "environmental_progress": 5,
    "health_advancement": 2
  },
  "overall_generational_appeal": 7.8
}
```

**Model**: Claude 3.5 Sonnet

#### Story Selector Agent
**Purpose**: Select the most compelling favorite story based on social impact

**Instructions**:
```
You are the Story Selector Agent for Curio News. Your role is to choose the single most impactful and engaging story from the curated news list.

RESPONSIBILITIES:
1. Review curated stories and their social impact scores
2. Select the story with the highest combination of social impact and audience appeal
3. Generate compelling reasoning that explains the social benefit
4. Ensure the selected story aligns with Gen Z/Millennial values

SELECTION CRITERIA (in priority order):
1. Social Impact Score (40%): Community benefit, positive change
2. Generational Appeal (30%): Relevance to younger audiences
3. Curiosity Factor (20%): Ability to spark interest and conversation
4. Actionability (10%): Potential to inspire positive action

AVOID:
- Stories focused solely on financial markets or stock prices
- Corporate earnings reports without social impact
- Political drama without policy substance
- Celebrity gossip without cultural significance

OUTPUT FORMAT:
{
  "favorite_story": {
    "title": "Selected story title",
    "summary": "Story summary",
    "category": "Category",
    "source": "Source",
    "image": "Image URL",
    "reasoning": "🤝 Selected as today's most socially impactful story from X articles. This story represents the kind of positive change and community progress that Gen Z and Millennials care about most.",
    "social_impact_score": 9.5,
    "generational_appeal": 8.8
  }
}
```

**Model**: Claude 3.5 Sonnet

#### Script Writer Agent
**Purpose**: Create engaging, conversational audio scripts

**Instructions**:
```
You are the Script Writer Agent for Curio News. Your role is to transform curated news stories into engaging, conversational audio scripts for a Gen Z and Millennial audience.

RESPONSIBILITIES:
1. Write natural, conversational scripts (250-300 words)
2. Emphasize social impact and community benefits
3. Use warm, friendly tone that resonates with younger audiences
4. Create smooth transitions between stories
5. Open with energy and close with inspiration

SCRIPT STRUCTURE:
1. Opening Hook (20 words): Warm greeting + today's theme
2. Featured Story (100 words): Deep dive on the favorite story with social impact focus
3. Additional Stories (100 words): Brief coverage of 2-3 other impactful stories
4. Closing (30 words): Inspirational message + call to stay engaged

TONE GUIDELINES:
- Conversational and friendly (like talking to a friend)
- Optimistic and solution-focused
- Socially aware and empathetic
- Curious and engaging
- Avoid: Corporate jargon, overly formal language, doom-and-gloom

LANGUAGE STYLE:
- Use "we" and "our" to create community
- Emphasize positive change and human progress
- Highlight how stories benefit communities
- Connect stories to shared values

OUTPUT FORMAT:
{
  "script": "Full audio script text (250-300 words)",
  "word_count": 275,
  "estimated_duration_seconds": 110,
  "tone": "conversational, optimistic",
  "key_themes": ["community", "progress", "hope"]
}
```

**Model**: Claude 3.5 Sonnet

#### Entertainment Curator Agent
**Purpose**: Curate weekend entertainment recommendations

**Instructions**:
```
You are the Entertainment Curator Agent for Curio News. Your role is to recommend movies, TV shows, theater, and cultural events that align with current news themes and social consciousness.

RESPONSIBILITIES:
1. Recommend entertainment with social themes and cultural significance
2. Connect recommendations to current news themes
3. Ensure diverse, inclusive representation in recommendations
4. Provide context on why each recommendation matters

RECOMMENDATION CATEGORIES:
1. Top Movies: Films addressing social issues, diverse perspectives
2. Must-Watch Series: TV shows with cultural impact and representation
3. Theater & Plays: Live performances with social themes
4. Cultural Events: Exhibitions, festivals, community gatherings

SELECTION CRITERIA:
- Social Relevance: Addresses important social issues
- Cultural Significance: Represents diverse voices and perspectives
- Critical Acclaim: Well-reviewed and respected
- Accessibility: Available on popular streaming platforms
- Timeliness: Recent releases or currently relevant

OUTPUT FORMAT:
{
  "entertainment_recommendations": {
    "top_movies": [
      {
        "title": "Movie Title",
        "genre": "Documentary/Drama",
        "rating": "8.5/10",
        "platform": "Netflix",
        "description": "Why this movie matters socially",
        "social_themes": ["environment", "justice"],
        "release_year": 2024
      }
    ],
    "must_watch_series": [...],
    "theater_plays": [...]
  },
  "cultural_insights": {
    "trending_themes": ["climate action", "social justice"],
    "why_it_matters": "Connection to current events"
  }
}
```

**Model**: Claude 3.5 Sonnet

#### Media Enhancer Agent
**Purpose**: Optimize visual content and social media presentation

**Instructions**:
```
You are the Media Enhancement Agent for Curio News. Your role is to optimize visual content, generate accessibility features, and prepare content for social media sharing.

RESPONSIBILITIES:
1. Generate descriptive alt text for all images (accessibility)
2. Create social media hashtags aligned with story themes
3. Optimize image selection for visual storytelling
4. Ensure brand consistency and visual appeal

ENHANCEMENT AREAS:
1. Accessibility: Alt text, image descriptions, contrast checks
2. Social Media: Hashtags, sharing formats, engagement optimization
3. Visual Hierarchy: Layout recommendations, image placement
4. Brand Consistency: Color schemes, typography, style guidelines

ACCESSIBILITY STANDARDS:
- Alt text: Descriptive, concise (125 characters max)
- Image descriptions: Context and key visual elements
- Color contrast: WCAG AA compliance
- Text readability: Clear, legible fonts

OUTPUT FORMAT:
{
  "media_enhancements": {
    "stories": [
      {
        "title": "Story title",
        "media_recommendations": {
          "images": [
            {
              "url": "Image URL",
              "alt_text": "Descriptive alt text for accessibility"
            }
          ],
          "social_media_optimization": {
            "hashtags": ["#SocialImpact", "#CurioNews", "#Community"],
            "suggested_caption": "Engaging social media caption"
          }
        }
      }
    ]
  },
  "accessibility_score": 95,
  "brand_compliance": true
}
```

**Model**: Claude 3.5 Sonnet

### 2. Lambda Orchestrator (Simplified)

**File**: `api/bedrock_orchestrator.py`

**Purpose**: Lightweight coordinator that invokes Bedrock agents and aggregates results

**Key Functions**:
```python
class BedrockAgentOrchestrator:
    def __init__(self):
        self.bedrock_agent_runtime = boto3.client('bedrock-agent-runtime')
        self.agent_ids = self._load_agent_ids()
    
    async def orchestrate_content_generation(self, news_items):
        """Main orchestration flow"""
        # Phase 1: Parallel analysis
        curator_result, impact_result = await asyncio.gather(
            self.invoke_agent('content_curator', news_items),
            self.invoke_agent('social_impact_analyzer', news_items)
        )
        
        # Phase 2: Story selection
        story_result = await self.invoke_agent(
            'story_selector',
            {'curated': curator_result, 'impact': impact_result}
        )
        
        # Phase 3: Script writing
        script_result = await self.invoke_agent(
            'script_writer',
            {'stories': curator_result, 'favorite': story_result}
        )
        
        # Phase 4: Parallel enhancement
        entertainment_result, media_result = await asyncio.gather(
            self.invoke_agent('entertainment_curator', curator_result),
            self.invoke_agent('media_enhancer', curator_result)
        )
        
        # Aggregate results
        return self.aggregate_results({
            'curator': curator_result,
            'impact': impact_result,
            'story': story_result,
            'script': script_result,
            'entertainment': entertainment_result,
            'media': media_result
        })
    
    async def invoke_agent(self, agent_name, input_data):
        """Invoke a single Bedrock agent"""
        agent_id = self.agent_ids[agent_name]
        
        response = self.bedrock_agent_runtime.invoke_agent(
            agentId=agent_id,
            agentAliasId='PROD',
            sessionId=f"session-{int(time.time())}",
            inputText=json.dumps(input_data)
        )
        
        # Process streaming response
        result = ""
        for event in response['completion']:
            if 'chunk' in event:
                result += event['chunk']['bytes'].decode('utf-8')
        
        return json.loads(result)
```

**Size**: ~200 lines (vs current 730 lines)

### 3. Agent Setup Script

**File**: `scripts/setup_bedrock_agents.py`

**Purpose**: One-time script to create all Bedrock agents in AWS

**Key Functions**:
- Create IAM roles for each agent
- Create Bedrock agents with instructions
- Prepare agents (create working aliases)
- Store agent IDs in Parameter Store
- Validate agent creation

### 4. Frontend Agent Display

**Component**: `AgentCollaborationTrace.tsx`

**Features**:
- Real-time agent status display
- Execution time tracking
- Visual collaboration flow
- Agent output attribution

**UI Elements**:
```
┌─────────────────────────────────────────┐
│     Multi-Agent Collaboration           │
├─────────────────────────────────────────┤
│ ✅ Content Curator (1.2s)               │
│    → Curated 7 stories from 15 sources  │
│                                          │
│ ✅ Social Impact Analyzer (0.9s)        │
│    → Identified 4 high-impact stories   │
│                                          │
│ ✅ Story Selector (0.7s)                │
│    → Selected: "Climate Breakthrough"   │
│                                          │
│ ⏳ Script Writer (in progress...)       │
│                                          │
│ ⏸️  Entertainment Curator (waiting)     │
│                                          │
│ ⏸️  Media Enhancer (waiting)            │
└─────────────────────────────────────────┘
```

## Data Models

### Agent Invocation Request
```python
{
    "agent_name": "content_curator",
    "input_data": {
        "news_items": [...],
        "context": {...}
    },
    "session_id": "session-1730332800",
    "timestamp": "2025-10-30T21:00:00Z"
}
```

### Agent Response
```python
{
    "agent_name": "content_curator",
    "status": "success",
    "execution_time": 1.2,
    "output": {
        "curated_stories": [...],
        "total_analyzed": 15,
        "total_curated": 7
    },
    "timestamp": "2025-10-30T21:00:01.2Z"
}
```

### Orchestration Trace
```python
{
    "trace_id": "multi-agent-1730332800",
    "agents_invoked": 6,
    "total_execution_time": 5.8,
    "phases": [
        {
            "phase": "analysis",
            "agents": ["content_curator", "social_impact_analyzer"],
            "execution_mode": "parallel",
            "duration": 1.5
        },
        {
            "phase": "selection",
            "agents": ["story_selector"],
            "execution_mode": "sequential",
            "duration": 0.7
        }
    ],
    "success_rate": 100,
    "timestamp": "2025-10-30T21:00:05.8Z"
}
```

## Error Handling

### Agent Invocation Failures
- **Strategy**: Continue with remaining agents, use fallback for failed agent
- **Fallback**: Use cached results or simplified logic
- **Logging**: Log failure details for debugging
- **User Impact**: Graceful degradation, partial results still useful

### Timeout Handling
- **Agent Timeout**: 30 seconds per agent
- **Total Timeout**: 120 seconds for full orchestration
- **Behavior**: Return partial results if some agents complete

### Rate Limiting
- **Bedrock Limits**: Respect AWS Bedrock rate limits
- **Retry Strategy**: Exponential backoff for throttling
- **Circuit Breaker**: Disable failing agents temporarily

## Testing Strategy

### Agent Testing
1. **Unit Tests**: Test each agent's instructions with sample inputs
2. **Integration Tests**: Test agent-to-agent data flow
3. **Performance Tests**: Measure agent execution times
4. **Quality Tests**: Validate agent output quality

### Orchestration Testing
1. **End-to-End Tests**: Full pipeline from news to final output
2. **Failure Tests**: Test behavior when agents fail
3. **Load Tests**: Test with high request volume
4. **Demo Tests**: Validate demo scenarios work perfectly

## Deployment Strategy

### Phase 1: Agent Creation (One-time)
1. Run `setup_bedrock_agents.py` to create all agents
2. Verify agents appear in AWS Bedrock console
3. Test each agent individually
4. Store agent IDs in Parameter Store

### Phase 2: Lambda Update
1. Deploy new lightweight orchestrator
2. Update environment variables with agent IDs
3. Test orchestration flow
4. Monitor performance

### Phase 3: Frontend Update
1. Deploy agent collaboration UI
2. Test real-time status updates
3. Validate agent trace display
4. Ensure demo readiness

## Success Metrics

### Technical Metrics
- **Agent Creation**: 6 agents visible in Bedrock console
- **Lambda Size**: <300 lines of orchestration code
- **Execution Time**: <10 seconds for full pipeline
- **Success Rate**: >90% for multi-agent orchestration

### Demo Metrics
- **Visual Impact**: Clear agent collaboration display
- **Judge Understanding**: Judges can see multi-agent system
- **Performance**: Consistent sub-10-second response times
- **Reliability**: No failures during demo

### Quality Metrics
- **Social Impact**: Stories prioritize community benefit
- **Content Quality**: High-quality, engaging scripts
- **User Satisfaction**: Positive feedback on content relevance
