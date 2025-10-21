# Design Document

## Overview

The Curio News platform is experiencing incomplete content generation where only basic news stories are generated while other sections (Favorite Story, Weekend Recommendations, Visual Enhancements) remain in loading states. This indicates failures in the agent orchestration system where some of the 6 specialized Bedrock agents are not completing successfully.

The design focuses on improving agent reliability, implementing proper error handling, adding comprehensive monitoring, and ensuring all content sections are generated consistently.

## Architecture

### Current Agent Flow
```
generate-fresh → agent_orchestrator → 6 Bedrock Agents → DynamoDB status → bootstrap endpoint
```

### Identified Issues
1. **Agent Timeout/Failure**: Some agents may be timing out or failing silently
2. **Orchestration Gaps**: The orchestrator may not be properly coordinating all 6 agents
3. **Error Handling**: Insufficient error handling and retry mechanisms
4. **Status Tracking**: Incomplete or inaccurate agent status updates

### Improved Architecture
```
generate-fresh → Enhanced Orchestrator → Monitored Agent Execution → Validated Results → Complete Bootstrap Response
```

## Components and Interfaces

### Enhanced Agent Orchestrator

**Purpose**: Coordinate all 6 agents with robust error handling and monitoring

**Key Improvements**:
- Individual agent timeout management (30-60 seconds per agent)
- Retry logic for failed agents (up to 3 attempts)
- Parallel execution where possible to reduce total time
- Comprehensive status tracking in DynamoDB
- Fallback content for critical failures

**Interface**:
```python
class EnhancedAgentOrchestrator:
    def orchestrate_all_agents(self, run_id: str) -> Dict[str, Any]
    def execute_agent_with_retry(self, agent_name: str, max_retries: int = 3) -> Dict
    def update_agent_status(self, run_id: str, agent: str, status: str, result: Any)
    def get_orchestration_summary(self, run_id: str) -> Dict[str, Any]
```

### Agent Execution Monitor

**Purpose**: Track individual agent performance and detect failures

**Features**:
- Real-time execution monitoring
- Timeout detection and handling
- Error categorization and logging
- Performance metrics collection

**Interface**:
```python
class AgentMonitor:
    def start_agent_execution(self, agent_name: str, run_id: str) -> str
    def check_agent_status(self, execution_id: str) -> AgentStatus
    def handle_agent_timeout(self, execution_id: str) -> None
    def log_agent_error(self, agent_name: str, error: Exception) -> None
```

### Content Validation System

**Purpose**: Ensure all required content sections are generated and valid

**Validation Rules**:
- News stories: Minimum 3 stories with proper structure
- Favorite story: Single story with enhanced details
- Weekend recommendations: List of activities/events
- Visual enhancements: Media URLs and metadata

**Interface**:
```python
class ContentValidator:
    def validate_complete_content(self, content: Dict) -> ValidationResult
    def validate_news_stories(self, stories: List[Dict]) -> bool
    def validate_favorite_story(self, story: Dict) -> bool
    def validate_weekend_recommendations(self, recommendations: List) -> bool
    def validate_visual_enhancements(self, visuals: Dict) -> bool
```

## Data Models

### Agent Execution Status
```python
{
    "run_id": "string",
    "agent_name": "string",
    "status": "pending|running|completed|failed|timeout",
    "start_time": "timestamp",
    "end_time": "timestamp",
    "execution_time_ms": "number",
    "result": "object|null",
    "error_message": "string|null",
    "retry_count": "number"
}
```

### Complete Content Structure
```python
{
    "run_id": "string",
    "generation_time": "timestamp",
    "news_items": [
        {
            "title": "string",
            "summary": "string",
            "category": "string",
            "relevance_score": "number"
        }
    ],
    "favorite_story": {
        "title": "string",
        "content": "string",
        "reasoning": "string",
        "engagement_score": "number"
    },
    "weekend_recommendations": [
        {
            "title": "string",
            "description": "string",
            "category": "string",
            "location": "string|null"
        }
    ],
    "visual_enhancements": {
        "featured_image": "string",
        "gallery_items": ["string"],
        "optimization_notes": "string"
    },
    "script_content": "string",
    "audio_url": "string",
    "word_timings": "array"
}
```

## Error Handling

### Agent Failure Scenarios

1. **Timeout Handling**
   - Set 60-second timeout per agent
   - Implement graceful timeout with partial results
   - Log timeout events for monitoring

2. **Bedrock Service Errors**
   - Handle throttling with exponential backoff
   - Retry on transient failures
   - Fallback to cached content when available

3. **Content Generation Failures**
   - Validate generated content structure
   - Retry with modified prompts if content is invalid
   - Use fallback templates for critical sections

4. **Orchestration Failures**
   - Continue with successful agents if some fail
   - Provide partial content rather than complete failure
   - Clear error messages for debugging

### Fallback Strategies

1. **News Stories**: Use RSS feed content if agents fail
2. **Favorite Story**: Select highest-scoring story from news items
3. **Weekend Recommendations**: Use cached recommendations from previous runs
4. **Visual Enhancements**: Use default images and standard optimization

## Testing Strategy

### Agent Reliability Testing
- Individual agent timeout testing
- Concurrent agent execution testing
- Failure scenario simulation
- Recovery mechanism validation

### Integration Testing
- End-to-end content generation flow
- Bootstrap endpoint response validation
- Frontend integration with complete content
- Error state handling in UI

### Performance Testing
- Agent execution time monitoring
- Parallel vs sequential execution comparison
- Memory and resource usage optimization
- Load testing with multiple concurrent requests

### Monitoring and Alerting
- CloudWatch metrics for agent success rates
- DynamoDB query performance monitoring
- Error rate tracking and alerting
- Content quality metrics collection

This design ensures reliable generation of all content sections by implementing robust agent orchestration, comprehensive error handling, and thorough monitoring of the content generation process.