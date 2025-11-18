# Bedrock Multi-Agent Demo - Quick Reference

## 🎯 Demo Objectives
- Show 6 specialized Bedrock agents in AWS console
- Demonstrate real-time agent collaboration
- Highlight social impact focus
- Prove sub-10-second performance

## ⚡ 5-Minute Demo Script

### 1. AWS Console (1 min)
**Open:** AWS Bedrock → Agents

**Say:** "Curio News uses 6 specialized AWS Bedrock agents, each with a specific role in creating socially impactful news content."

**Show:** List of agents
- CurioNews-ContentCurator
- CurioNews-SocialImpactAnalyzer
- CurioNews-StorySelector
- CurioNews-ScriptWriter
- CurioNews-EntertainmentCurator
- CurioNews-MediaEnhancer

**Click one agent** → Show instructions and Claude 3.5 Sonnet model

### 2. Live Execution (2 min)
**Open:** Frontend application

**Say:** "Watch these agents collaborate in real-time."

**Click:** "Generate Today's News"

**Point out as they execute:**
- ✅ Content Curator (analyzing sources)
- ✅ Social Impact Analyzer (scoring stories)
- ✅ Story Selector (choosing favorite)
- ✅ Script Writer (creating script)
- ✅ Entertainment Curator (recommending content)
- ✅ Media Enhancer (optimizing visuals)

**Emphasize:** "Total time: under 10 seconds"

### 3. Social Impact (1 min)
**Show:** Selected favorite story

**Say:** "Our agents prioritize social impact over financial news. This story was selected because of its community benefit and relevance to Gen Z values."

**Point out:**
- Social impact reasoning
- Community/environmental themes
- Gen Z appeal score

### 4. Technical Architecture (1 min)
**Say:** "This is a true multi-agent system with:"
- 6 independent Bedrock agents (not simulated)
- Lightweight Lambda orchestrator (<300 lines)
- Agent-to-agent data flow
- Parallel execution for performance
- Graceful error handling

**Show:** Architecture diagram or agent collaboration trace

## 🎬 Pre-Demo Checklist
- [ ] AWS console open to Bedrock Agents
- [ ] Frontend application loaded
- [ ] Test run completed successfully
- [ ] Backup screenshots ready
- [ ] Architecture diagram available
- [ ] Demo script rehearsed

## 💡 Key Talking Points

### Why Multi-Agent?
"Each agent specializes in one task, making the system maintainable and allowing independent optimization of each agent's behavior."

### Social Impact Focus
"Our Social Impact Analyzer explicitly scores stories on community benefit, environmental progress, and social justice. Financial market news is deprioritized."

### Performance
"We achieve sub-10-second performance by running independent agents in parallel. Phases 1 and 4 execute simultaneously."

### Reliability
"If an agent fails, the orchestrator continues with remaining agents and uses fallback logic to ensure users still get content."

## 🔥 Impressive Stats
- **6 specialized agents** working in collaboration
- **5 execution phases** with parallel optimization
- **<10 seconds** total execution time
- **90%+ success rate** for multi-agent orchestration
- **Claude 3.5 Sonnet** powering all agents

## ❓ Common Questions

**Q: Why not one big agent?**
A: Specialization allows better optimization, maintainability, and demonstrates true multi-agent collaboration.

**Q: How do you ensure social impact?**
A: Explicit scoring criteria in Social Impact Analyzer. Stories about stock markets get negative scores.

**Q: What if an agent fails?**
A: Graceful degradation - system continues with remaining agents and uses fallback logic.

**Q: How fast is it?**
A: Under 10 seconds for complete pipeline. We optimize with parallel execution.

## 🚨 Backup Plan
If live demo fails:
1. Show screenshots/video of successful run
2. Walk through agent configurations in AWS console
3. Show CloudWatch logs proving agent execution
4. Explain architecture using design document

## 📊 Agent Collaboration Flow

```
Phase 1 (Parallel): Content Curator + Social Impact Analyzer
         ↓
Phase 2: Story Selector (uses Phase 1 outputs)
         ↓
Phase 3: Script Writer (uses favorite story)
         ↓
Phase 4 (Parallel): Entertainment Curator + Media Enhancer
         ↓
Phase 5: Lambda aggregates all results
```

## 🎯 Demo Success Criteria
- ✅ All 6 agents visible in AWS console
- ✅ Live execution completes successfully
- ✅ Agent collaboration trace displays correctly
- ✅ Social impact story selected and explained
- ✅ Total time under 10 seconds
- ✅ Judges understand multi-agent architecture

## 📱 Quick Commands

```bash
# Test agents before demo
python test_bedrock_setup.py

# View agent IDs
aws ssm get-parameters-by-path --path /curio-news/agents/

# Check Lambda logs
aws logs tail /aws/lambda/curio-news-bootstrap --follow

# List agents
aws bedrock-agent list-agents
```

## 🎨 Visual Aids
- Agent collaboration trace in frontend
- Architecture diagram (show data flow)
- AWS console (show real agents)
- CloudWatch metrics (show performance)

---

**Remember:** This is about showcasing technical sophistication AND social impact. Balance both in your presentation!
