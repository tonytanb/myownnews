# Architecture Consolidation and Simplification Requirements

## Introduction

The Curio News application has grown into a complex system with multiple overlapping services, handlers, and components that are causing deployment failures and reliability issues. We need to consolidate into a simple, monolithic architecture that works reliably.

## Glossary

- **Monolithic_Service**: A single, unified service that handles all core functionality
- **Core_Handler**: The main request handler that processes all API endpoints
- **Unified_Agent**: A single agent system that handles all content generation
- **Simple_Audio**: A streamlined audio generation system without complex orchestration
- **Direct_Deploy**: A deployment approach that minimizes dependencies and complexity

## Requirements

### Requirement 1

**User Story:** As a developer, I want a single, consolidated service architecture, so that I can deploy and debug the system reliably.

#### Acceptance Criteria

1. THE Monolithic_Service SHALL handle all API endpoints in a single Lambda function
2. THE Core_Handler SHALL eliminate redundant error handling and fallback systems
3. THE Monolithic_Service SHALL remove all duplicate agent orchestration code
4. THE Core_Handler SHALL consolidate all content generation into one clear flow
5. THE Monolithic_Service SHALL use a single requirements.txt with minimal dependencies

### Requirement 2

**User Story:** As a developer, I want simplified content generation without complex agent orchestration, so that the system works predictably.

#### Acceptance Criteria

1. THE Unified_Agent SHALL replace all separate agent classes with one content generator
2. THE Unified_Agent SHALL fetch news, generate script, and create audio in a linear flow
3. THE Unified_Agent SHALL NOT use parallel processing or complex orchestration
4. THE Unified_Agent SHALL have simple error handling with direct fallbacks
5. THE Unified_Agent SHALL complete all operations within a single function call

### Requirement 3

**User Story:** As a user, I want reliable audio generation without S3 complexity, so that audio always works.

#### Acceptance Criteria

1. THE Simple_Audio SHALL generate audio directly using AWS Polly
2. THE Simple_Audio SHALL return audio URLs immediately without S3 upload delays
3. THE Simple_Audio SHALL use Polly's direct streaming URLs for immediate playback
4. THE Simple_Audio SHALL NOT depend on complex S3 bucket configurations
5. THE Simple_Audio SHALL handle audio generation failures with simple retry logic

### Requirement 4

**User Story:** As a developer, I want a clean deployment process without overlapping configurations, so that deployments succeed consistently.

#### Acceptance Criteria

1. THE Direct_Deploy SHALL use a single SAM template with minimal resources
2. THE Direct_Deploy SHALL eliminate redundant Lambda functions and API endpoints
3. THE Direct_Deploy SHALL use environment variables instead of complex configuration files
4. THE Direct_Deploy SHALL have a single build process without multiple dependencies
5. THE Direct_Deploy SHALL complete deployment in under 5 minutes with clear success/failure feedback

### Requirement 5

**User Story:** As a developer, I want to remove all redundant code and services, so that the codebase is maintainable.

#### Acceptance Criteria

1. THE Monolithic_Service SHALL consolidate all handlers into handlers.py
2. THE Monolithic_Service SHALL remove duplicate error handling, logging, and monitoring files
3. THE Monolithic_Service SHALL eliminate unused API endpoints and functions
4. THE Monolithic_Service SHALL use a single configuration approach throughout
5. THE Monolithic_Service SHALL have clear separation between frontend and backend with no overlap