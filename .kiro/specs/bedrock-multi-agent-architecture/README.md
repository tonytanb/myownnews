# Bedrock Multi-Agent Architecture - Documentation Index

## 📚 Documentation Overview

This directory contains comprehensive documentation for the Curio News Bedrock Multi-Agent Architecture. Use this index to find the right document for your needs.

## 🗂️ Document Guide

### Core Specification Documents

#### [requirements.md](requirements.md)
**Purpose:** System requirements and acceptance criteria  
**Use when:** Understanding what the system must do  
**Key sections:**
- User stories for each requirement
- EARS-compliant acceptance criteria
- Social impact focus requirements
- Performance and reliability targets

#### [design.md](design.md)
**Purpose:** Detailed technical architecture and design  
**Use when:** Understanding how the system works  
**Key sections:**
- High-level architecture diagrams
- Agent definitions and instructions
- Data models and interfaces
- Error handling strategies
- Testing approach

#### [tasks.md](tasks.md)
**Purpose:** Implementation task list and progress tracking  
**Use when:** Implementing or tracking development progress  
**Key sections:**
- Numbered task list with checkboxes
- Sub-tasks for each major task
- Requirement references
- Implementation status

### Deployment & Operations

#### [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) ⭐ **START HERE**
**Purpose:** Complete guide for deploying the multi-agent system  
**Use when:** Setting up agents for the first time or troubleshooting  
**Key sections:**
- Prerequisites and environment setup
- Step-by-step agent setup instructions
- AWS console verification steps
- Troubleshooting common issues
- Updating agent instructions
- Demo presentation guide

**Quick Start:**
```bash
# 1. Install dependencies
pip install boto3 requests

# 2. Run agent setup
cd scripts
python setup_bedrock_agents.py

# 3. Verify agents
python test_bedrock_setup.py

# 4. Deploy Lambda
sam build && sam deploy
```

#### [DEMO_QUICK_REFERENCE.md](DEMO_QUICK_REFERENCE.md) 🎯
**Purpose:** Quick reference for hackathon demo presentations  
**Use when:** Preparing for or giving a demo to judges  
**Key sections:**
- 5-minute demo script
- Pre-demo checklist
- Key talking points
- Common questions and answers
- Backup plan if demo fails

**Perfect for:** Last-minute demo prep or rehearsal

#### [TROUBLESHOOTING_FLOWCHART.md](TROUBLESHOOTING_FLOWCHART.md) 🔧
**Purpose:** Diagnostic flowcharts and problem resolution  
**Use when:** Something isn't working and you need to fix it  
**Key sections:**
- Problem diagnosis flowcharts
- Common error messages and fixes
- Diagnostic commands
- Health check scripts
- Escalation path

**Quick diagnosis:** Run `python check_agent_health.py`

### Supporting Documents

#### [AGENT_COLLABORATION_UI_GUIDE.md](AGENT_COLLABORATION_UI_GUIDE.md)
**Purpose:** Frontend implementation guide for agent trace UI  
**Use when:** Working on the React frontend components  
**Key sections:**
- Component architecture
- Real-time status updates
- Visual design guidelines
- Integration with backend

#### [TASK_5_COMPLETION_SUMMARY.md](TASK_5_COMPLETION_SUMMARY.md)
**Purpose:** Summary of Task 5 (Frontend UI) completion  
**Use when:** Understanding what was implemented in Task 5

#### [TASK_7_COMPLETION.md](TASK_7_COMPLETION.md)
**Purpose:** Summary of Task 7 (SAM Template) completion  
**Use when:** Understanding Lambda configuration and permissions

#### [TASK_7_SAM_TEMPLATE_UPDATE.md](TASK_7_SAM_TEMPLATE_UPDATE.md)
**Purpose:** Detailed SAM template changes for Bedrock integration  
**Use when:** Modifying Lambda configuration or IAM permissions

## 🚀 Quick Navigation

### I want to...

#### Deploy the system for the first time
→ Read [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) sections:
1. Prerequisites
2. Agent Setup
3. Verification

#### Prepare for a demo
→ Read [DEMO_QUICK_REFERENCE.md](DEMO_QUICK_REFERENCE.md)
→ Practice with the 5-minute demo script
→ Complete the pre-demo checklist

#### Fix a problem
→ Read [TROUBLESHOOTING_FLOWCHART.md](TROUBLESHOOTING_FLOWCHART.md)
→ Find your error message or symptom
→ Follow the diagnostic flowchart

#### Understand the architecture
→ Read [design.md](design.md) sections:
1. Overview
2. Architecture
3. Agent Collaboration Flow

#### Update agent instructions
→ Read [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) section:
- "Updating Agent Instructions"

#### Verify everything is working
→ Run these commands:
```bash
python test_bedrock_setup.py
python check_agent_health.py
python test_bedrock_integration.py
```

#### Understand requirements
→ Read [requirements.md](requirements.md)
→ Focus on acceptance criteria for each requirement

#### Track implementation progress
→ Read [tasks.md](tasks.md)
→ Check task completion status

## 📋 Common Workflows

### First-Time Setup Workflow
1. Read [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Prerequisites
2. Run `python setup_bedrock_agents.py`
3. Verify in AWS console (see Verification section)
4. Run `python test_bedrock_setup.py`
5. Deploy Lambda with `sam build && sam deploy`
6. Test end-to-end with `python test_bedrock_integration.py`

### Demo Preparation Workflow
1. Read [DEMO_QUICK_REFERENCE.md](DEMO_QUICK_REFERENCE.md)
2. Complete pre-demo checklist
3. Run test: `python test_bedrock_integration.py`
4. Open AWS console to Bedrock Agents page
5. Open frontend application
6. Rehearse 5-minute demo script
7. Prepare backup screenshots/video

### Troubleshooting Workflow
1. Identify the problem (error message or symptom)
2. Read [TROUBLESHOOTING_FLOWCHART.md](TROUBLESHOOTING_FLOWCHART.md)
3. Follow diagnostic flowchart for your issue
4. Run diagnostic commands
5. Check CloudWatch logs
6. Apply suggested fixes
7. Verify with health check: `python check_agent_health.py`

### Agent Update Workflow
1. Read [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - "Updating Agent Instructions"
2. Update instructions in `setup_bedrock_agents.py` or AWS console
3. Prepare agent (if using console)
4. Test agent individually in console
5. Run integration test: `python test_bedrock_integration.py`
6. Monitor CloudWatch logs for issues
7. Update [design.md](design.md) with changes

## 🎯 Document Purpose Matrix

| Document | Setup | Demo | Troubleshoot | Understand | Update |
|----------|-------|------|--------------|------------|--------|
| DEPLOYMENT_GUIDE.md | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| DEMO_QUICK_REFERENCE.md | ⭐ | ⭐⭐⭐ | - | ⭐ | - |
| TROUBLESHOOTING_FLOWCHART.md | ⭐ | ⭐ | ⭐⭐⭐ | ⭐ | ⭐ |
| design.md | ⭐⭐ | ⭐⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐ |
| requirements.md | ⭐ | ⭐ | - | ⭐⭐⭐ | ⭐ |
| tasks.md | ⭐⭐ | - | - | ⭐⭐ | ⭐⭐ |

⭐⭐⭐ = Essential | ⭐⭐ = Very Helpful | ⭐ = Useful | - = Not Applicable

## 🔗 External Resources

### AWS Documentation
- [AWS Bedrock Agents](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html)
- [Bedrock Agent Runtime API](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_Operations_Agents_for_Amazon_Bedrock_Runtime.html)
- [Claude 3.5 Sonnet Model](https://docs.anthropic.com/claude/docs/models-overview)
- [AWS SAM Documentation](https://docs.aws.amazon.com/serverless-application-model/)

### Related Project Files
- `scripts/setup_bedrock_agents.py` - Agent creation script
- `scripts/test_bedrock_setup.py` - Agent verification script
- `api/bedrock_orchestrator.py` - Lambda orchestrator
- `api/test_bedrock_integration.py` - Integration tests
- `template.yaml` - SAM template with Lambda configuration

## 📞 Getting Help

### Quick Help
1. Run health check: `python check_agent_health.py`
2. Check [TROUBLESHOOTING_FLOWCHART.md](TROUBLESHOOTING_FLOWCHART.md)
3. Review CloudWatch logs

### Detailed Help
1. Read relevant documentation section
2. Run diagnostic commands
3. Check AWS Service Health Dashboard
4. Review GitHub issues
5. Contact AWS Support (for Bedrock issues)

## 🎓 Learning Path

### For New Team Members
1. Start with [requirements.md](requirements.md) - Understand the goals
2. Read [design.md](design.md) - Learn the architecture
3. Review [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - See how it's deployed
4. Practice with [DEMO_QUICK_REFERENCE.md](DEMO_QUICK_REFERENCE.md) - Prepare to demo

### For Judges/Reviewers
1. Read [DEMO_QUICK_REFERENCE.md](DEMO_QUICK_REFERENCE.md) - Quick overview
2. Review [design.md](design.md) - Technical architecture
3. Check [requirements.md](requirements.md) - Social impact focus
4. View AWS console - See real agents

### For Developers
1. Read [design.md](design.md) - Understand architecture
2. Review [tasks.md](tasks.md) - See implementation plan
3. Study `api/bedrock_orchestrator.py` - Learn orchestration
4. Read [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Deploy and test

## 📊 System Overview

### The 6 Agents
1. **Content Curator** - Discovers and filters news
2. **Social Impact Analyzer** - Scores social relevance
3. **Story Selector** - Chooses most impactful story
4. **Script Writer** - Creates audio scripts
5. **Entertainment Curator** - Recommends culturally significant content
6. **Media Enhancer** - Optimizes visuals and accessibility

### Key Metrics
- **Execution Time:** <10 seconds for full pipeline
- **Success Rate:** >90% for multi-agent orchestration
- **Agent Count:** 6 specialized Bedrock agents
- **Phases:** 5 execution phases with parallel optimization

### Social Impact Focus
- Prioritizes community benefit and social justice
- Deprioritizes financial market news
- Emphasizes Gen Z and Millennial values
- Highlights environmental and health progress

## 🔄 Document Maintenance

### When to Update
- After agent instruction changes → Update [design.md](design.md)
- After deployment process changes → Update [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- After discovering new issues → Update [TROUBLESHOOTING_FLOWCHART.md](TROUBLESHOOTING_FLOWCHART.md)
- After demo improvements → Update [DEMO_QUICK_REFERENCE.md](DEMO_QUICK_REFERENCE.md)

### Version History
- **v1.0** (Oct 31, 2025) - Initial documentation complete
  - All 8 tasks implemented
  - Comprehensive deployment guide
  - Demo preparation materials
  - Troubleshooting resources

---

## 🎯 Quick Start (TL;DR)

**First time setup:**
```bash
pip install boto3 requests
cd scripts
python setup_bedrock_agents.py
python test_bedrock_setup.py
sam build && sam deploy
```

**Before demo:**
```bash
python test_bedrock_integration.py
# Read DEMO_QUICK_REFERENCE.md
# Open AWS console to Bedrock Agents
```

**If something breaks:**
```bash
python check_agent_health.py
# Read TROUBLESHOOTING_FLOWCHART.md
```

**For more details:** Read [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

---

**Last Updated:** October 31, 2025  
**Maintained By:** Curio News Development Team  
**Questions?** Check [TROUBLESHOOTING_FLOWCHART.md](TROUBLESHOOTING_FLOWCHART.md) or run `python check_agent_health.py`
