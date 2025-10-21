# Requirements Document

## Introduction

The Curio News system is currently experiencing critical reliability issues with 0% success rate on content generation workflows. The primary issues are timeout-related problems where the synchronous `/generate-fresh` endpoint exceeds API Gateway's 30-second limit, causing all workflow runs to fail. This spec addresses the core architectural issues preventing reliable content generation and delivery.

## Requirements

### Requirement 1: Asynchronous Content Generation

**User Story:** As a system user, I want content generation to work reliably without timing out, so that I can consistently access fresh news content.

#### Acceptance Criteria

1. WHEN a user requests fresh content generation THEN the system SHALL return immediately with a run ID and status tracking URL
2. WHEN content generation is initiated THEN the system SHALL process agents asynchronously without blocking the API response
3. WHEN the API Gateway 30-second timeout is approached THEN the system SHALL have already returned a response to the client
4. IF content generation takes longer than 30 seconds THEN the system SHALL continue processing in the background
5. WHEN asynchronous processing completes THEN the system SHALL update the status and make content available via the bootstrap endpoint

### Requirement 2: Robust Timeout and Retry Configuration

**User Story:** As a system administrator, I want proper timeout and retry mechanisms configured throughout the system, so that temporary failures don't cause complete system breakdown.

#### Acceptance Criteria

1. WHEN an individual agent execution exceeds 60 seconds THEN the system SHALL timeout that agent and attempt retry
2. WHEN an agent fails after 3 retry attempts THEN the system SHALL continue with fallback content for that agent
3. WHEN the total orchestration exceeds 5 minutes THEN the system SHALL complete with partial content rather than failing entirely
4. IF external API calls (NewsAPI, Bedrock, Polly) timeout THEN the system SHALL retry with exponential backoff
5. WHEN network issues occur THEN the system SHALL implement circuit breaker patterns to prevent cascade failures

### Requirement 3: Improved Status Tracking and Polling

**User Story:** As a frontend application, I want reliable status updates during content generation, so that I can show accurate progress to users.

#### Acceptance Criteria

1. WHEN content generation is in progress THEN the `/agent-status` endpoint SHALL return current agent and progress information
2. WHEN polling for status updates THEN the system SHALL respond within 2 seconds with current state
3. WHEN an agent completes or fails THEN the status SHALL be updated immediately in the database
4. IF a client polls for a non-existent run ID THEN the system SHALL return appropriate 404 status
5. WHEN orchestration completes THEN the final status SHALL indicate success/failure and content availability

### Requirement 4: Enhanced Error Handling and Fallbacks

**User Story:** As an end user, I want to receive some content even when parts of the system fail, so that I'm not left with completely empty results.

#### Acceptance Criteria

1. WHEN individual agents fail THEN the system SHALL continue processing remaining agents
2. WHEN critical agents (NEWS_FETCHER, SCRIPT_GENERATOR) fail THEN the system SHALL use cached or fallback content
3. WHEN non-critical agents (MEDIA_ENHANCER, WEEKEND_EVENTS) fail THEN the system SHALL complete without those sections
4. IF all agents fail THEN the system SHALL return emergency fallback content with error information
5. WHEN partial failures occur THEN the system SHALL indicate which sections are fallback content

### Requirement 5: Performance Optimization and Monitoring

**User Story:** As a system operator, I want comprehensive monitoring and performance optimization, so that I can identify and resolve issues quickly.

#### Acceptance Criteria

1. WHEN agents execute THEN the system SHALL log execution times and success rates to CloudWatch
2. WHEN performance degrades THEN the system SHALL automatically adjust timeouts and retry counts
3. WHEN error rates exceed 20% THEN the system SHALL trigger alerts and enable enhanced logging
4. IF system resources are constrained THEN the system SHALL prioritize critical agents over optional ones
5. WHEN debugging is needed THEN the system SHALL provide detailed execution traces and performance metrics

### Requirement 6: Test Configuration Alignment

**User Story:** As a developer running tests, I want test timeouts and expectations aligned with actual system behavior, so that tests accurately reflect system health.

#### Acceptance Criteria

1. WHEN running reliability tests THEN the test timeout SHALL be at least 6 minutes to accommodate full orchestration
2. WHEN testing individual endpoints THEN the test SHALL use appropriate timeouts for each endpoint type
3. WHEN measuring performance THEN the tests SHALL account for asynchronous processing patterns
4. IF content generation is asynchronous THEN tests SHALL poll for completion rather than expecting immediate results
5. WHEN validating system health THEN tests SHALL verify both immediate response and eventual content delivery