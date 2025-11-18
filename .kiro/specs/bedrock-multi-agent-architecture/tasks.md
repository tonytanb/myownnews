# Implementation Plan: Bedrock Multi-Agent Architecture

- [x] 1. Create Bedrock Agent Setup Script

  - Write Python script to create all 6 Bedrock agents in AWS
  - Implement IAM role creation for each agent with appropriate permissions
  - Configure each agent with detailed instructions from the design document
  - Prepare agents and create production aliases
  - Store agent IDs in AWS Systems Manager Parameter Store for Lambda access
  - Add validation to verify all agents are created successfully
  - _Requirements: 1.1, 1.4, 1.5_

- [x] 2. Implement Lightweight Lambda Orchestrator

  - Create new `api/bedrock_orchestrator.py` with simplified orchestration logic (<300 lines)
  - Implement `invoke_agent()` method to call Bedrock agents via boto3
  - Build `orchestrate_content_generation()` with 5-phase agent collaboration flow
  - Add agent execution tracking with timestamps and status
  - Implement result aggregation from all agent outputs
  - Add error handling with graceful degradation for agent failures
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 3. Enable Agent-to-Agent Data Flow

  - Implement Phase 1: Parallel invocation of Content Curator and Social Impact Analyzer
  - Implement Phase 2: Story Selector receives outputs from Phase 1 agents
  - Implement Phase 3: Script Writer receives favorite story from Story Selector
  - Implement Phase 4: Parallel invocation of Entertainment Curator and Media Enhancer
  - Create orchestration trace log showing data flow between agents
  - Add metadata to final response attributing content to specific agents
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 4. Update Main Handler to Use Bedrock Orchestrator

  - Modify `api/main_handler.py` to import and use BedrockAgentOrchestrator
  - Update `/bootstrap` endpoint to invoke multi-agent orchestration
  - Add fallback to existing ContentGenerator if Bedrock agents unavailable
  - Update response format to include orchestration trace and agent metadata
  - Add environment variable checks for agent IDs
  - _Requirements: 2.1, 2.5_

- [x] 5. Create Frontend Agent Collaboration Display

  - Create new React component `AgentCollaborationTrace.tsx`
  - Implement real-time agent status display (pending, in-progress, complete)
  - Add execution time tracking for each agent
  - Build visual collaboration flow showing agent sequence
  - Display agent outputs with attribution to specific agents
  - Add loading states and progress indicators
  - Style component to match Curio News design system
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 6. Add Agent Status API Endpoint

  - Create `/agent-status` endpoint in main handler
  - Return list of all agents with their current status
  - Include agent metadata: name, role, last execution time
  - Add orchestration statistics: success rate, average execution time
  - Implement caching to avoid excessive Bedrock API calls
  - _Requirements: 4.1, 4.2_

- [x] 7. Update SAM Template for Bedrock Agents

  - Add IAM permissions for Lambda to invoke Bedrock agents
  - Add environment variables for agent IDs (loaded from Parameter Store)
  - Update Lambda timeout to 180 seconds for multi-agent orchestration
  - Add CloudWatch metrics for agent invocation tracking
  - _Requirements: 1.4, 2.1_

- [x] 8. Create Agent Deployment Documentation

  - Write step-by-step guide for running agent setup script
  - Document how to verify agents in AWS Bedrock console
  - Create troubleshooting guide for common agent creation issues
  - Add instructions for updating agent instructions
  - Document agent collaboration flow for demo presentation
  - _Requirements: 5.4_

- [x] 9. Implement Demo Optimization

  - Add visual diagram of agent collaboration flow to frontend
  - Create demo mode that highlights agent activity
  - Optimize agent execution for sub-10-second total time
  - Add performance monitoring for agent execution times
  - Create demo script showing multi-agent system to judges
  - _Requirements: 5.1, 5.2, 5.3, 5.5_

- [x] 10. Deploy and Validate Multi-Agent System
  - Run agent setup script to create all Bedrock agents
  - Verify all 6 agents appear in AWS Bedrock console
  - Deploy updated Lambda orchestrator
  - Test full multi-agent pipeline end-to-end
  - Validate agent collaboration trace in frontend
  - Measure and optimize performance to meet <10s target
  - Test demo scenarios to ensure reliability
  - _Requirements: 1.1, 2.1, 4.1, 5.1, 5.5_
