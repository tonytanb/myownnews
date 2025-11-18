# Bedrock Agent Orchestrator Integration Flow

## Request Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         API Gateway                              │
│                  /bootstrap, /generate-fresh                     │
│                     /latest, /agent-status                       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Lambda Handler (main_handler.py)               │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Environment Variable Check:                                │ │
│  │ - USE_BEDROCK_AGENTS=true/false                           │ │
│  │ - ENABLE_MULTI_AGENT=true/false                           │ │
│  │ - BEDROCK_ORCHESTRATOR_AVAILABLE flag                     │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Priority 1: Bedrock Agent Orchestrator                     │ │
│  │ IF USE_BEDROCK_AGENTS=true AND agents configured           │ │
│  │ THEN invoke BedrockAgentOrchestrator                       │ │
│  │   ├─ Load agent IDs from env or Parameter Store           │ │
│  │   ├─ Run 5-phase orchestration with 6 agents              │ │
│  │   ├─ Add orchestration_trace to response                  │ │
│  │   └─ Add agent_attribution metadata                       │ │
│  │ ON SUCCESS: Return with bedrock_agents_used=true          │ │
│  │ ON FAILURE: Fall through to Priority 2                    │ │
│  └────────────────────────────────────────────────────────────┘ │
│                         │                                        │
│                         ▼ (if Priority 1 fails)                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Priority 2: Standard Multi-Agent Orchestrator              │ │
│  │ IF ENABLE_MULTI_AGENT=true                                 │ │
│  │ THEN invoke CurioMultiAgentOrchestrator                    │ │
│  │   ├─ Use existing multi-agent logic                        │ │
│  │   └─ Add orchestration_type='standard_multi_agent'         │ │
│  │ ON SUCCESS: Return with bedrock_agents_used=false         │ │
│  │ ON FAILURE: Fall through to Priority 3                    │ │
│  └────────────────────────────────────────────────────────────┘ │
│                         │                                        │
│                         ▼ (if Priority 2 fails)                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Priority 3: Single-Agent Content Generator                 │ │
│  │ ALWAYS AVAILABLE                                           │ │
│  │ THEN invoke generate_content()                             │ │
│  │   ├─ Use consolidated content generator                    │ │
│  │   └─ Add orchestration_type='single_agent'                 │ │
│  │ ON SUCCESS: Return with bedrock_agents_used=false         │ │
│  │ ON FAILURE: Fall through to Priority 4                    │ │
│  └────────────────────────────────────────────────────────────┘ │
│                         │                                        │
│                         ▼ (if Priority 3 fails)                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Priority 4: Real News Fallback                             │ │
│  │ ALWAYS AVAILABLE (last resort)                             │ │
│  │ THEN invoke create_content_with_real_news()                │ │
│  │   ├─ Fetch real news from NewsAPI                          │ │
│  │   ├─ Generate basic content structure                      │ │
│  │   └─ Add orchestration_type='fallback'                     │ │
│  │ ALWAYS SUCCEEDS: Return basic content                     │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Response with Metadata                      │
│                                                                  │
│  {                                                               │
│    "script": "...",                                              │
│    "news_items": [...],                                          │
│    "agentOutputs": {...},                                        │
│    "orchestration_type": "bedrock_agents",                       │
│    "bedrock_agents_used": true,                                  │
│    "agent_count": 6,                                             │
│    "orchestration_trace": [                                      │
│      {                                                           │
│        "agent": "content_curator",                               │
│        "status": "success",                                      │
│        "execution_time": 1.2,                                    │
│        "output_summary": "7 stories curated"                     │
│      },                                                          │
│      ...                                                         │
│    ],                                                            │
│    "agent_attribution": {                                        │
│      "news_curation": {                                          │
│        "agent": "content_curator",                               │
│        "contribution": "Curated and scored news stories"         │
│      },                                                          │
│      ...                                                         │
│    },                                                            │
│    "data_flow_summary": {                                        │
│      "phase_1_to_phase_2": {                                     │
│        "from_agents": ["content_curator", "social_impact_..."], │
│        "to_agent": "story_selector",                             │
│        "data_passed": "Curated stories and social impact..."    │
│      },                                                          │
│      ...                                                         │
│    }                                                             │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
```

## Agent Status Endpoint Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    GET /agent-status                             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              handle_agent_status() in main_handler.py            │
│                                                                  │
│  1. Check USE_BEDROCK_AGENTS environment variable               │
│     ├─ If false: Return "not enabled" message                   │
│     └─ If true: Continue to step 2                              │
│                                                                  │
│  2. Check BEDROCK_ORCHESTRATOR_AVAILABLE flag                   │
│     ├─ If false: Return "not available" message                 │
│     └─ If true: Continue to step 3                              │
│                                                                  │
│  3. Create BedrockAgentOrchestrator instance                    │
│     └─ Loads agent IDs from env vars or Parameter Store         │
│                                                                  │
│  4. Check if agent IDs are configured                           │
│     ├─ If none: Return "not configured" message                 │
│     └─ If configured: Continue to step 5                        │
│                                                                  │
│  5. Call orchestrator.get_agent_status()                        │
│     ├─ Returns list of all agents with metadata                 │
│     ├─ Includes last execution details from trace               │
│     └─ Includes session ID and orchestration trace              │
│                                                                  │
│  6. Add environment metadata                                    │
│     └─ Include USE_BEDROCK_AGENTS and ENABLE_MULTI_AGENT        │
│                                                                  │
│  7. Return comprehensive status response                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Status Response                             │
│                                                                  │
│  {                                                               │
│    "bedrock_agents_enabled": true,                               │
│    "agents_configured": true,                                    │
│    "agents": [                                                   │
│      {                                                           │
│        "name": "content_curator",                                │
│        "agent_id": "AGENT123",                                   │
│        "status": "available",                                    │
│        "last_execution": {                                       │
│          "execution_time": 1.2,                                  │
│          "timestamp": "2025-10-30T...",                          │
│          "status": "success"                                     │
│        }                                                         │
│      },                                                          │
│      ... (5 more agents)                                         │
│    ],                                                            │
│    "total_agents": 6,                                            │
│    "session_id": "session-uuid",                                 │
│    "orchestration_trace": [...],                                 │
│    "environment": {                                              │
│      "USE_BEDROCK_AGENTS": true,                                 │
│      "ENABLE_MULTI_AGENT": true                                  │
│    }                                                             │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
```

## Error Handling Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Any Orchestration Level                       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
                    ┌─────────┐
                    │ Try     │
                    │ Execute │
                    └────┬────┘
                         │
                ┌────────┴────────┐
                │                 │
                ▼                 ▼
           ┌─────────┐      ┌──────────┐
           │ Success │      │ Exception│
           └────┬────┘      └────┬─────┘
                │                │
                │                ▼
                │         ┌──────────────┐
                │         │ Log Error    │
                │         │ with Stack   │
                │         │ Trace        │
                │         └──────┬───────┘
                │                │
                │                ▼
                │         ┌──────────────┐
                │         │ Set Result   │
                │         │ to None      │
                │         └──────┬───────┘
                │                │
                └────────┬───────┘
                         │
                         ▼
                  ┌──────────────┐
                  │ Check Result │
                  └──────┬───────┘
                         │
                ┌────────┴────────┐
                │                 │
                ▼                 ▼
         ┌──────────┐      ┌─────────────┐
         │ Valid    │      │ None/Empty  │
         │ Result   │      │ Result      │
         └────┬─────┘      └──────┬──────┘
              │                   │
              │                   ▼
              │            ┌──────────────┐
              │            │ Fall Through │
              │            │ to Next      │
              │            │ Priority     │
              │            └──────┬───────┘
              │                   │
              └────────┬──────────┘
                       │
                       ▼
                ┌──────────────┐
                │ Return       │
                │ Response     │
                │ with         │
                │ Metadata     │
                └──────────────┘
```

## Key Integration Points

### 1. Import Section
```python
# Import Bedrock Agent Orchestrator
try:
    from bedrock_orchestrator import BedrockAgentOrchestrator
    BEDROCK_ORCHESTRATOR_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Bedrock orchestrator not available: {e}")
    BEDROCK_ORCHESTRATOR_AVAILABLE = False
```

### 2. Environment Variable Checks
```python
use_bedrock_agents = os.getenv('USE_BEDROCK_AGENTS', 'false').lower() == 'true'
use_multi_agent = os.getenv('ENABLE_MULTI_AGENT', 'true').lower() == 'true'
```

### 3. Orchestrator Invocation
```python
if use_bedrock_agents and BEDROCK_ORCHESTRATOR_AVAILABLE:
    bedrock_orchestrator = BedrockAgentOrchestrator()
    if bedrock_orchestrator.agent_ids:
        fresh_content = asyncio.run(
            bedrock_orchestrator.orchestrate_content_generation(initial_news)
        )
```

### 4. Response Enhancement
```python
fresh_content.update({
    'orchestration_type': 'bedrock_agents',
    'bedrock_agents_used': True,
    'agent_count': len(bedrock_orchestrator.agent_ids)
})
```

## Benefits of This Integration

1. **Graceful Degradation**: 4-level fallback ensures service reliability
2. **Observability**: Detailed traces show exactly what happened
3. **Flexibility**: Easy to enable/disable via environment variable
4. **Backward Compatible**: Existing functionality preserved
5. **Demo-Ready**: Agent status endpoint perfect for demonstrations
6. **Production-Ready**: Comprehensive error handling and logging
