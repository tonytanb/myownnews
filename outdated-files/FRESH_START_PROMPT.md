# 🏆 AWS Agent Hackathon: Curio News - Complete Project Build

I need you to build a complete, production-ready AWS Agent Hackathon submission from scratch. This is a sophisticated AI-powered news curation system that demonstrates 6 specialized Bedrock Agents working together.

## 🎯 PROJECT OVERVIEW
**Name**: Curio News  
**Tagline**: "Your world in 5 minutes" - AI-curated news for Gen Z/Millennials  
**Goal**: Showcase 6 Bedrock Agents collaborating to solve real-world news consumption challenges  
**Demo URL Target**: Judge-ready system with full provenance tracking  

## 🏗️ COMPLETE ARCHITECTURE

### Backend: AWS SAM Infrastructure
```yaml
# Required AWS Services:
- AWS Lambda (Python 3.9)
- Amazon Bedrock (Claude 3 Haiku)
- Amazon Polly (Neural voices)
- Amazon S3 (Audio/script storage)
- Amazon DynamoDB (Caching/status)
- API Gateway (CORS-enabled REST API)
```

### 6 Specialized Bedrock Agents
1. **📰 News Fetcher Agent**
   - Gathers trending stories from RSS feeds + NewsAPI
   - Filters for Gen Z/Millennial relevance
   - Categories: tech, culture, politics, science, viral trends

2. **🎯 Content Curator Agent**
   - Selects exactly 5 stories for balanced briefing
   - Ensures diversity across categories
   - Optimizes for engagement and narrative flow

3. **⭐ Favorite Selector Agent**
   - Identifies the most fascinating "wow factor" story
   - Focuses on university research, discoveries, cultural phenomena
   - Creates "shareable moments"

4. **📝 Script Generator Agent**
   - Transforms news into conversational 90-second audio script
   - Millennial tone: "honestly", "lowkey", "ngl", "get this", "plot twist"
   - Structure: Opening → Stories → Team Favorite → Closing

5. **🎨 Media Enhancer Agent**
   - Curates visual content and social media optimization
   - Suggests compelling images and video clips
   - Accessibility and engagement focus

6. **🎉 Weekend Events Agent**
   - Recommends books, movies, events, cultural trends
   - BookTok trends, streaming releases, local events
   - Social media phenomena integration

## 🔧 TECHNICAL SPECIFICATIONS

### API Endpoints (All CORS-enabled)
- `GET /bootstrap` - Smart caching with instant UX
- `POST /generate-fresh` - Real agent orchestration 
- `GET /agent-status?runId=X` - Real-time progress tracking
- `GET /latest` - Most recent content with presigned URLs
- `GET /sign?key=X` - S3 presigned URL generation

### Smart Caching System
- **Instant Gratification**: Serve cached audio immediately
- **Background Generation**: Start fresh content generation
- **Hot Swap**: Replace audio when fresh content ready
- **Real-time Updates**: Show agent progress with emojis

### Agent Orchestration Flow
```
📰 FETCHING_NEWS → 🎯 CURATING → ⭐ SELECTING_FAVORITE → 
📝 GENERATING_SCRIPT → 🎨 ENHANCING_MEDIA → 🎉 WEEKEND_EVENTS → ✅ COMPLETED
```

## 🎨 FRONTEND: Judge-Ready React Demo

### Professional UI Components
- **Header**: Logo, agent status indicator, menu
- **Hero Section**: "Agent-Powered News Demo" with play button
- **Audio Player**: Custom controls with word-by-word highlighting
- **News Grid**: Curated stories with categories and relevance scores
- **Interactive Transcript**: Clickable words with karaoke-style highlighting
- **Agent Provenance**: Visual pipeline showing all 6 agents working
- **Real-time Status**: Live updates as agents process content

### Styling Requirements
- **Modern Design**: Gradients, shadows, smooth animations
- **Mobile Responsive**: Works on all devices
- **Professional Polish**: Judge-ready presentation quality
- **Color Scheme**: Purple/blue gradients with orange accents
- **Typography**: Clean, readable fonts with proper hierarchy

## 📊 WORKING CREDENTIALS & RESOURCES

### API Keys & Configuration
```
NewsAPI Key: 56e5f744fdb04e1e8e45a450851e442d
AWS Region: us-west-2
Bedrock Model: anthropic.claude-3-haiku-20240307-v1:0
Polly Voice: Joanna (Neural)
```

### Existing Infrastructure (Reference Only)
```
Previous API: https://nqot0dir0h.execute-api.us-west-2.amazonaws.com/prod
Previous S3: curio-news-frontend-1760730768
Test Page: http://curio-news-frontend-1760730768.s3-website-us-west-2.amazonaws.com/test.html
```

## 🚀 DEPLOYMENT REQUIREMENTS

### SAM Template Features
- Complete infrastructure as code
- Proper IAM permissions for all services
- Environment variables for all configurations
- CORS configuration for API Gateway
- DynamoDB with TTL for caching
- S3 bucket with public read access

### Build & Deploy Commands
```bash
sam build
sam deploy --guided
npm run build (for frontend)
aws s3 sync build/ s3://bucket-name
```

## 🎯 SUCCESS CRITERIA

### Judge Demo Requirements
1. **Instant Audio Playback** - Click play → immediate audio
2. **Visible Agent Progress** - Watch 6 agents work in real-time
3. **Professional UI** - Production-quality interface
4. **Real Bedrock Integration** - Actual Claude 3 Haiku responses
5. **Complete Provenance** - Full transparency of AI decisions
6. **Error Handling** - Graceful fallbacks and loading states

### Technical Excellence
- **Scalable Architecture** - Production-ready AWS infrastructure
- **Real-time Updates** - WebSocket-like experience with polling
- **Smart Caching** - Optimal user experience with background processing
- **CORS Compliance** - Proper cross-origin resource sharing
- **Mobile Responsive** - Works perfectly on all devices

## 📝 DELIVERABLES

Create these files in a complete, working project:

### Backend Files
1. **`template.yaml`** - Complete SAM infrastructure with all Lambda functions
2. **`api/handlers.py`** - All API endpoint handlers with proper CORS
3. **`api/agent_orchestrator.py`** - 6 Bedrock Agents implementation
4. **`api/requirements.txt`** - Python dependencies

### Frontend Files
5. **`frontend/src/App.tsx`** - Main React application with all components
6. **`frontend/src/components/AudioPlayer.tsx`** - Custom audio player with real-time updates
7. **`frontend/src/components/NewsItems.tsx`** - News grid component
8. **`frontend/src/components/InteractiveTranscript.tsx`** - Transcript with karaoke highlighting
9. **`frontend/src/App.css`** - Complete professional styling
10. **`frontend/package.json`** - React dependencies and scripts
11. **`frontend/.env`** - Environment variables for API URL

### Documentation
12. **`README.md`** - Complete setup and deployment instructions
13. **`AWS_AGENT_HACKATHON_SUBMISSION.md`** - Detailed submission document

## 🎪 DEMO FLOW FOR JUDGES

1. **Landing Page**: Professional UI with "Agent-Powered News Demo"
2. **Click Play**: Instant audio starts (cached content)
3. **Agent Progress**: Real-time updates showing 6 agents working
4. **News Grid**: Curated stories appear with categories
5. **Interactive Transcript**: Words highlight as audio plays
6. **Agent Provenance**: Complete transparency of AI decision-making
7. **Fresh Content**: Hot-swap to newly generated content when ready

## 🏆 FINAL GOAL

Build a complete, judge-ready AWS Agent Hackathon submission that demonstrates the future of AI-powered content curation. This should be a production-quality system that showcases 6 specialized Bedrock Agents working in harmony to solve real-world challenges for Gen Z/Millennial news consumption.

**Key Success Metrics:**
- ✅ All 6 Bedrock Agents working together
- ✅ Real-time progress tracking with emojis
- ✅ Professional, responsive UI
- ✅ Instant audio playback with smart caching
- ✅ Complete provenance and transparency
- ✅ Production-ready AWS infrastructure
- ✅ Mobile-responsive design
- ✅ Error handling and graceful fallbacks

**Make this the winning entry that shows the true power of AWS Bedrock Agents! 🚀**

---

## 🚀 IMPLEMENTATION PRIORITY

**Phase 1: Core Infrastructure**
1. SAM template with Lambda functions
2. Basic API endpoints with CORS
3. DynamoDB and S3 setup

**Phase 2: Agent Orchestration**
1. 6 Bedrock Agents implementation
2. Agent status tracking
3. Real-time progress updates

**Phase 3: Frontend Excellence**
1. React app with professional UI
2. Audio player with transcript highlighting
3. News grid and agent provenance

**Phase 4: Integration & Polish**
1. End-to-end testing
2. Error handling and fallbacks
3. Mobile responsiveness
4. Final deployment

**Start building this complete system now - every component working together seamlessly!**