# Architecture Consolidation Implementation Plan

**⚠️ PROJECT SCOPE WARNING ⚠️**
This consolidation is ONLY for the **MyOwnNews MVP** project (stack: `myownnews-mvp`).
DO NOT modify, delete, or interfere with any other Curio projects (like Curio Reels).
All changes are scoped to this project's files and AWS resources only.

- [x] 1. Create unified main handler

  - Create single `api/main_handler.py` that handles all API endpoints
  - Consolidate bootstrap, generate-fresh, and latest endpoints into one file
  - Remove complex routing and use simple if/elif logic for endpoint handling
  - _Requirements: 1.1, 1.2, 1.4_

- [x] 2. Implement simple content generator

  - [x] 2.1 Create linear content generation flow

    - Write `api/content_generator.py` with single generate_content() function
    - Implement news fetching, script generation, and content assembly in sequence
    - Remove all parallel processing and complex orchestration logic
    - _Requirements: 2.1, 2.2, 2.3_

  - [x] 2.2 Add simple error handling
    - Implement try/catch with direct fallback to cached or hardcoded content
    - Remove complex retry mechanisms and error recovery systems
    - _Requirements: 2.4, 2.5_

- [x] 3. Streamline audio generation

  - [x] 3.1 Implement direct Polly audio service

    - Create `api/audio_service.py` using AWS Polly direct streaming URLs
    - Remove S3 upload complexity and file management
    - Return immediate audio URLs without storage delays
    - _Requirements: 3.1, 3.2, 3.4_

  - [x] 3.2 Add simple audio fallback
    - Implement basic retry logic for Polly failures
    - Use hardcoded fallback audio URL if generation fails
    - _Requirements: 3.3, 3.5_

- [x] 4. Create minimal cache service

  - Create `api/cache_service.py` with simple DynamoDB operations
  - Implement get/set operations with TTL-based expiration
  - Remove complex cache invalidation and management logic
  - _Requirements: 1.3, 2.4_

- [x] 5. Consolidate SAM template and deployment (MyOwnNews MVP only)

  - [x] 5.1 Simplify SAM template for this project only

    - Update `template.yaml` to replace API Lambda functions with single `CurioNewsMainFunction`
    - Remove only the redundant API functions: BootstrapFunction, GenerateFreshFunction, AgentStatusFunction, etc.
    - Keep existing CurioTable, AssetsBucket, and NewsToAudioFunction unchanged
    - DO NOT modify any resources that might be shared with other Curio projects
    - _Requirements: 4.1, 4.2, 4.3_

  - [x] 5.2 Clean up requirements and dependencies
    - Consolidate `requirements.txt` to minimal necessary packages
    - Remove unused dependencies and complex library requirements
    - _Requirements: 1.5, 4.4_

- [x] 6. Remove redundant files and code (within this project only)

  - [x] 6.1 Delete overlapping service files from MyOwnNews MVP

    - Remove ONLY files within this project: `api/agent_orchestrator.py`, `api/enhanced_*.py`, performance optimization files
    - Delete redundant error handling, logging, and monitoring files from THIS project's api/ directory
    - Clean up test files with overlapping functionality within THIS project scope
    - DO NOT delete any files that might be shared across Curio projects
    - _Requirements: 5.1, 5.2, 5.3_

  - [x] 6.2 Update imports and references
    - Update all import statements to reference new consolidated files
    - Remove references to deleted services and handlers
    - _Requirements: 5.4, 5.5_

- [x] 7. Test and validate consolidated system

  - [x] 7.1 Create simple integration test

    - Write single end-to-end test covering bootstrap and content generation
    - Test audio URL accessibility and content delivery
    - _Requirements: 1.1, 2.1, 3.1_

  - [x] 7.2 Deploy and validate - Deploy consolidated system using simplified SAM template - Run health checks and smoke tests on all endpoints - Verify deployment completes successfully within 5 minutes - _Requirements: 4.1, 4.5_
        `
