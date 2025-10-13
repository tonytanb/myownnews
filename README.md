# MyOwnNews 🎙️

**AI-Powered Daily News Brief Generator**

A serverless application that transforms breaking news into personalized audio briefings using AWS AI services. Built for busy professionals who want to stay informed without the noise.

## 🚀 Features

### Current Implementation
- **Smart News Aggregation**: Fetches top headlines from News API across multiple categories
- **AI-Powered Summarization**: Uses Amazon Bedrock (Titan) to create concise, witty news scripts
- **Natural Audio Generation**: Converts text to lifelike speech using Amazon Polly
- **Serverless Architecture**: Fully managed AWS infrastructure with automatic scaling
- **Organized Storage**: Date-based file organization in S3 for scripts, audio, and metadata
- **Multi-Category Support**: Technology, business, and general news in one brief
- **Professional Tone**: Morning Brew-inspired writing style for engaging content

### Technical Highlights
- **Zero Server Management**: Built on AWS Lambda with SAM framework
- **Cost-Effective**: Pay-per-execution model with AWS Free Tier compatibility
- **Scalable**: Handles traffic spikes automatically
- **Secure**: IAM-based permissions with encrypted API keys
- **Maintainable**: Infrastructure as Code with CloudFormation

## 🔧 Prerequisites

### Required API Keys
1. **News API Key**: Get free key at [newsapi.org](https://newsapi.org)
   - 1,000 requests/day on free tier
   - Access to 80,000+ news sources
   
2. **AWS Account**: Required for Bedrock, Polly, Lambda, and S3
   - Bedrock access in us-east-1 region
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

### 2. Build and Deploy
```bash
# Build the application
sam build --use-container

# Deploy with guided setup (first time)
sam deploy --guided

# Or deploy with parameters
sam deploy \
  --parameter-overrides \
    NewsApiKey=your-news-api-key \
    NewsCategories=general,technology,business \
    VoiceId=Matthew \
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
News API → Lambda Function → Bedrock (AI Summary) → Polly (Audio) → S3 Storage
    ↓           ↓                    ↓                  ↓           ↓
Categories   Python 3.11        Titan Model      Neural Voice   Organized Files
```

### AWS Services Used
- **Lambda**: Serverless compute for news processing
- **Bedrock**: AI text generation and summarization
- **Polly**: Neural text-to-speech conversion
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
- [x] News API integration
- [x] AI summarization with Bedrock
- [x] Audio generation with Polly
- [x] S3 storage and organization
- [x] Serverless deployment

### Phase 2: Automation & Scheduling
- [ ] CloudWatch Events for daily automation
- [ ] Multiple voice options and personalization
- [ ] Email/SMS delivery of audio links
- [ ] Web dashboard for managing preferences

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
- **Bedrock**: 20K input tokens free (Titan Text)
- **Polly**: 5M characters free
- **S3**: 5GB storage free

### Estimated Monthly Cost (Beyond Free Tier)
- Daily briefs (30/month): ~$2-5
- Storage (1 year): ~$1-2
- **Total**: Under $10/month for personal use

## 🏆 Hackathon Highlights

### Innovation
- **AI-First Approach**: Leverages cutting-edge AWS AI services
- **Serverless-Native**: Built for cloud scalability from day one
- **User-Centric**: Solves real problem of information overload

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
