# MyOwnNews 🎙️

**AI-Powered International News Podcast Generator**

A serverless application that transforms breaking global news into engaging audio briefings using Claude AI and AWS services. Inspired by AM Podcast style - casual, witty, and internationally focused.

## 🚀 Features

### Current Implementation
- **Claude AI Script Generation**: Uses Anthropic Claude 3 Haiku for creative, conversational news scripts
- **AM Podcast Style**: Engaging, witty tone inspired by Spanish AM Podcast format
- **International News Focus**: Global perspective with BBC, Reuters, Al Jazeera, Guardian sources
- **Neural Voice Synthesis**: Joanna's natural-sounding voice via Amazon Polly Neural
- **Smart News Curation**: Quality filtering and popularity-based article selection
- **Serverless Architecture**: Fully managed AWS infrastructure with automatic scaling
- **Multi-Region Deployment**: Optimized for us-west-2 where Claude access is available
- **Organized Storage**: Date-based file organization in S3 for scripts, audio, and metadata

### Technical Highlights
- **Claude AI Integration**: Advanced conversational AI for engaging content creation
- **Cross-Region Architecture**: Deployed in us-west-2 for optimal Claude access
- **Neural Voice Technology**: Premium Polly Neural voices for podcast-quality audio
- **International News Pipeline**: Multi-source aggregation with quality filtering
- **Zero Server Management**: Built on AWS Lambda with SAM framework
- **Cost-Effective**: Pay-per-execution model with AWS Free Tier compatibility
- **Scalable**: Handles traffic spikes automatically
- **Secure**: IAM-based permissions with encrypted API keys

## 🔧 Prerequisites

### Required API Keys
1. **News API Key**: Get free key at [newsapi.org](https://newsapi.org)
   - 1,000 requests/day on free tier
   - Access to 80,000+ news sources
   
2. **AWS Account**: Required for Claude, Polly, Lambda, and S3
   - **Claude access in us-west-2 region** (critical!)
   - Bedrock model access for Anthropic Claude 3 Haiku
   - IAM permissions for deployment

### Required Tools
- AWS CLI configured with credentials
- AWS SAM CLI installed
- Python 3.11+
- Docker (for containerized builds)

## 📦 Deployment

### 1. Clone and Configure
```bash
git clone <your-repo>
cd myownnews

# Configure your News API key in template.yaml
# Or set as parameter during deployment
```

### 2. Enable Claude Access in AWS Bedrock
**Critical Step**: Request Claude model access in us-west-2
```bash
# Go to AWS Bedrock Console in us-west-2
https://us-west-2.console.aws.amazon.com/bedrock/home?region=us-west-2#/modelaccess

# Request access for:
# - Claude 3 Haiku
# - Claude 3.5 Sonnet (optional)
```

### 3. Build and Deploy
```bash
# Build the application
sam build --use-container

# Deploy to us-west-2 (where Claude is available)
sam deploy --region us-west-2 \
  --parameter-overrides \
    NewsApiKey=your-news-api-key \
    NewsCategories=general,technology,business,science \
    VoiceId=Joanna \
    MaxArticles=5
```

### 3. Test the Function
```bash
# Invoke the function manually
sam local invoke NewsToAudioFunction --event events/event.json

# Or test in AWS Console
aws lambda invoke --function-name <function-name> response.json
```

## 🏗️ Architecture

```
News API → Lambda Function → Claude AI → Polly Neural → S3 Storage
    ↓           ↓              ↓           ↓            ↓
Global Sources  Python 3.11   AM Podcast  Joanna Voice  Organized Files
(BBC, Reuters)  (us-west-2)   Style       (Natural)     (Date-based)
```

### AWS Services Used
- **Lambda**: Serverless compute for news processing (us-west-2)
- **Bedrock**: Claude AI for creative, conversational script generation
- **Polly Neural**: Premium text-to-speech with Joanna voice
- **S3**: Secure storage for audio files and metadata
- **CloudFormation**: Infrastructure as Code via SAM
- **IAM**: Fine-grained security permissions

### File Organization
```
S3 Bucket Structure:
├── scripts/YYYY-MM-DD/script-{timestamp}-{id}.txt
├── audio/YYYY-MM-DD/voice-{timestamp}-{id}.mp3
└── runs/YYYY-MM-DD/run-{timestamp}-{id}.json
```

## 🎯 Roadmap & Future Enhancements

### Phase 1: Core Features ✅
- [x] Claude AI integration for creative scripts
- [x] AM Podcast-style conversational tone
- [x] International news aggregation
- [x] Neural voice synthesis with Joanna
- [x] Multi-region deployment (us-west-2)
- [x] Quality news filtering and curation

### Phase 2: Enhanced AI & Personalization
- [ ] Claude 3.5 Sonnet for even better scripts
- [ ] Country-specific news personalization
- [ ] Multiple voice options (different personalities)
- [ ] CloudWatch Events for daily automation
- [ ] Email/SMS delivery of audio links

### Phase 3: Advanced Features
- [ ] Multi-language support
- [ ] Custom news source filtering
- [ ] Podcast RSS feed generation
- [ ] Mobile app integration
- [ ] Analytics and usage tracking

### Phase 4: Enterprise Features
- [ ] Team/organization accounts
- [ ] Custom branding and voices
- [ ] API for third-party integrations
- [ ] Advanced AI models (Claude, GPT)
- [ ] Real-time breaking news alerts

## 💰 Cost Estimation

### AWS Free Tier (Monthly)
- **Lambda**: 1M requests free
- **Bedrock**: Claude usage (pay-per-token, very affordable)
- **Polly Neural**: 1M characters free for neural voices
- **S3**: 5GB storage free

### Estimated Monthly Cost (Beyond Free Tier)
- Daily Claude briefs (30/month): ~$3-8
- Neural voice synthesis: ~$1-3
- Storage (1 year): ~$1-2
- **Total**: Under $15/month for personal use

## 🏆 Hackathon Highlights

### Innovation
- **Claude AI Integration**: First-class conversational AI for engaging content
- **AM Podcast Style**: Brings Spanish podcast energy to international news
- **Cross-Cultural Bridge**: Global news with accessible, witty presentation
- **Serverless-Native**: Built for cloud scalability from day one

### Technical Excellence
- **Production-Ready**: Proper error handling, logging, and security
- **Well-Documented**: Clear code structure and comprehensive README
- **Testable**: Includes test events and local development setup

### Business Potential
- **Scalable Model**: Can serve millions of users with minimal infrastructure
- **Monetization Ready**: Clear path to premium features and enterprise sales
- **Market Fit**: Addresses growing demand for AI-powered content curation

## 📝 Learning Notes

This project demonstrates mastery of:
- **AWS SAM**: Infrastructure as Code for serverless applications
- **AWS AI Services**: Bedrock for text generation, Polly for speech synthesis
- **Event-Driven Architecture**: Lambda functions triggered by schedules or API calls
- **Cloud Storage**: S3 best practices for file organization and security
- **Cost Optimization**: Leveraging AWS Free Tier and pay-per-use pricing

---

*Built with ❤️ for the AWS Hackathon by Tony Narvaez*
