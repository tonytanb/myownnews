# Architecture Consolidation Design

## Overview

This design consolidates the Curio News application into a simple, reliable monolithic architecture that eliminates complexity and ensures consistent deployments. We'll remove all redundant services and create a single, unified system.

## Architecture

### Current Problems
- Multiple overlapping Lambda functions
- Complex agent orchestration with parallel processing
- Redundant error handling and fallback systems
- S3 audio upload complexity causing failures
- Multiple configuration files and dependencies

### New Simplified Architecture
```
Frontend (React) → API Gateway → Single Lambda Function → AWS Polly (direct)
                                      ↓
                               DynamoDB (simple cache)
```

## Components and Interfaces

### 1. Unified Lambda Function
**File**: `api/main_handler.py`
- Single entry point for all API requests
- Handles: `/bootstrap`, `/generate-fresh`, `/latest`
- No complex orchestration or parallel processing
- Direct, linear execution flow

### 2. Simple Content Generator
**File**: `api/content_generator.py`
- Replaces all agent classes with one unified generator
- Linear flow: fetch news → generate script → create audio
- Simple error handling with immediate fallbacks
- No complex state management

### 3. Direct Audio Service
**File**: `api/audio_service.py`
- Uses AWS Polly's direct streaming URLs
- No S3 upload complexity
- Immediate audio URL generation
- Simple retry logic for failures

### 4. Minimal Cache Layer
**File**: `api/cache_service.py`
- Simple DynamoDB table for content caching
- TTL-based expiration (24 hours)
- No complex cache invalidation logic

## Data Models

### Content Model
```python
{
    "id": "daily-brief-2025-10-29",
    "script": "Today's news script...",
    "audio_url": "https://polly.amazonaws.com/...",
    "news_items": [...],
    "generated_at": "2025-10-29T21:00:00Z",
    "ttl": 1730332800
}
```

### News Item Model
```python
{
    "title": "News Title",
    "summary": "Brief summary",
    "source": "Source Name",
    "url": "https://..."
}
```

## Implementation Strategy

**IMPORTANT**: This consolidation is ONLY for the **MyOwnNews MVP** project (stack: `myownnews-mvp`). 
We will NOT touch any other Curio projects (like Curio Reels or other services).

### Phase 1: Consolidate Handlers
1. Create single `main_handler.py` with all endpoints for MyOwnNews MVP only
2. Remove redundant Lambda functions from THIS project's SAM template only
3. Consolidate all imports and dependencies within this project scope

### Phase 2: Simplify Content Generation
1. Replace agent orchestration with linear content generator
2. Remove parallel processing and complex state management
3. Implement direct news fetching and script generation

### Phase 3: Streamline Audio
1. Replace S3 audio upload with Polly direct URLs
2. Remove complex audio file management
3. Implement simple audio generation with immediate response

### Phase 4: Clean Deployment
1. Simplify SAM template to single Lambda + DynamoDB
2. Consolidate requirements.txt
3. Remove unused configuration files

## Error Handling

### Simple Error Strategy
- Try primary operation
- If fails, use cached content (if available)
- If no cache, use hardcoded fallback
- Log error and continue
- No complex retry orchestration

### Fallback Content
```python
FALLBACK_CONTENT = {
    "script": "Welcome to Curio News. We're updating our content and will be back shortly.",
    "audio_url": "https://polly.amazonaws.com/fallback-audio",
    "news_items": [],
    "sources": ["System"]
}
```

## Testing Strategy

### Integration Testing
- Single end-to-end test covering full flow
- Test each endpoint with simple assertions
- Validate audio URL accessibility
- No complex unit testing for individual components

### Deployment Testing
- Automated deployment validation
- Health check after deployment
- Simple smoke test for all endpoints

## File Cleanup Plan

### Files to Remove
- `api/agent_orchestrator.py`
- `api/enhanced_*.py` (all enhanced modules)
- `api/performance_optimizer.py`
- `api/debugging_dashboard.py`
- `api/agent_metrics.py`
- `api/agent_logger.py`
- All redundant error handling files
- Multiple test files with overlapping functionality

### Files to Consolidate
- All handlers → `api/main_handler.py`
- All agent logic → `api/content_generator.py`
- Audio logic → `api/audio_service.py`
- Cache logic → `api/cache_service.py`

### SAM Template Simplification (MyOwnNews MVP Only)
```yaml
# Keep existing CurioTable and AssetsBucket - only consolidate Lambda functions
Resources:
  # Consolidated function replacing all the individual API functions
  CurioNewsMainFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: api/
      Handler: main_handler.lambda_handler
      Runtime: python3.9
      Environment:
        Variables:
          BUCKET: !Ref AssetsBucket
          CURIO_TABLE: !Ref CurioTable
          # ... existing environment variables
      Events:
        ApiGateway:
          Type: Api
          Properties:
            RestApiId: !Ref NewsApi
            Path: /{proxy+}
            Method: ANY
  
  # Keep existing NewsToAudioFunction for scheduled generation
  # Keep existing CurioTable and AssetsBucket unchanged
```

## Success Metrics

### Reliability Improvements
- Deployment success rate: 100%
- Audio loading success rate: >95%
- Response time: <3 seconds consistently
- Error rate: <5%

### Complexity Reduction
- Lines of code: Reduce by 60%
- Number of files: Reduce by 70%
- Dependencies: Reduce to <10 packages
- Lambda functions: Reduce from 9 to 1

This design prioritizes reliability and simplicity over complex features, ensuring the system works consistently for the hackathon demo.