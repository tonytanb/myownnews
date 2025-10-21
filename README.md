# Curio News - AI-Powered Morning News Platform

> **🏆 AWS Agent Hackathon Submission** - A production-ready news platform powered by 6 specialized AWS Bedrock agents

An intelligent news platform that generates personalized morning briefings using multi-agent orchestration with AWS Bedrock, featuring real-time audio generation and interactive transcripts.

## 🚀 Live Demo

- **🌐 Frontend**: http://curio-news-frontend-1760997974.s3-website-us-west-2.amazonaws.com
- **🔧 API**: https://nqot0dir0h.execute-api.us-west-2.amazonaws.com/prod
- **📊 Debugging Dashboard**: Available in the frontend for real-time agent monitoring

## ✨ Key Features

- **🤖 Multi-Agent Orchestration**: 6 specialized Bedrock agents working in harmony
- **🎵 Audio Generation**: High-quality neural voice synthesis with Amazon Polly
- **📝 Interactive Transcripts**: Click-to-play with word-level timing synchronization
- **📊 Real-time Monitoring**: Live agent execution tracking and debugging dashboard
- **📱 Responsive Design**: Seamless experience across desktop and mobile devices
- **⚡ Performance Optimized**: Sub-second response times with comprehensive caching

## 🤖 Agent Architecture

### The 6 Specialized Agents

| Agent | Purpose | Technology |
|-------|---------|------------|
| **NEWS_FETCHER** | Gathers latest news from multiple sources | Claude Haiku |
| **CONTENT_CURATOR** | Selects and prioritizes relevant stories | Claude Haiku |
| **FAVORITE_SELECTOR** | Identifies the most engaging story | Claude Haiku |
| **SCRIPT_GENERATOR** | Creates conversational, podcast-style scripts | Claude Haiku |
| **MEDIA_ENHANCER** | Adds visual elements and optimizations | Claude Haiku |
| **WEEKEND_EVENTS** | Generates weekend recommendations | Claude Haiku |

### Orchestration Flow

```
User Request → Agent Orchestrator → 6 Parallel Agents → Content Assembly → Audio Generation → Response
```

## 🛠 Technical Stack

### AWS Services
- **AWS Bedrock** (Claude Haiku) - AI agent processing
- **Amazon Polly** (Neural Joanna) - Text-to-speech synthesis
- **AWS Lambda** - Serverless compute
- **Amazon DynamoDB** - Agent status and content storage
- **Amazon S3** - Static hosting and audio storage
- **Amazon API Gateway** - RESTful API endpoints
- **AWS SAM** - Infrastructure as Code

### Frontend Technologies
- **React 18** with TypeScript
- **Modern CSS** with responsive design
- **Web Audio API** for interactive playback
- **Real-time WebSocket** connections for agent monitoring

## 📊 Performance Metrics

Based on comprehensive testing (see `/tests` directory):

| Metric | Result | Status |
|--------|--------|--------|
| Bootstrap Response Time | 0.39s average | ✅ Excellent |
| Content Quality Score | 1.00/1.00 | ✅ Perfect |
| System Reliability | 3/3 components healthy | ✅ Robust |
| Concurrent Load Handling | 5+ users, 100% success | ✅ Scalable |

## 🚀 Quick Start

### Prerequisites
- AWS CLI configured with appropriate permissions
- Node.js 18+ and npm
- Python 3.9+
- AWS SAM CLI

### 1. Deploy Backend Infrastructure
```bash
# Clone and navigate to project
git clone [repository-url]
cd curio-news

# Build and deploy with SAM
sam build
sam deploy --guided

# Note the API Gateway URL from outputs
```

### 2. Deploy Frontend
```bash
cd curio-news-ui

# Install dependencies and build
npm install
npm run build

# Deploy to S3 (replace with your bucket name)
aws s3 sync build/ s3://your-frontend-bucket --delete
aws s3 website s3://your-frontend-bucket --index-document index.html
```

### 3. Configure Environment
```bash
# Update frontend environment variables
echo "REACT_APP_API_URL=your-api-gateway-url" > curio-news-ui/.env.production
```

## 🔧 Local Development

### Backend Development
```bash
# Start local API server
sam local start-api --port 3001

# Run tests
python tests/run_performance_reliability_tests.py
```

### Frontend Development
```bash
cd curio-news-ui

# Start development server
npm start

# Run frontend tests
npm test
```

## 📁 Project Structure

```
curio-news/
├── 📁 api/                          # Lambda functions and core logic
│   ├── handlers.py                  # Main API handlers
│   ├── agent_orchestrator.py        # Multi-agent coordination
│   ├── audio_generator.py           # Polly integration
│   ├── debugging_dashboard.py       # Real-time monitoring
│   └── ...
├── 📁 curio-news-ui/               # React frontend application
│   ├── src/
│   │   ├── components/              # Reusable UI components
│   │   ├── App.tsx                  # Main application component
│   │   └── ...
│   └── public/                      # Static assets
├── 📁 tests/                       # Comprehensive test suite
│   ├── performance_reliability_test.py
│   ├── comprehensive_e2e_validation.py
│   └── ...
├── 📁 docs/                        # Documentation
│   ├── architecture/
│   ├── development/
│   └── deployment/
├── 📄 template.yaml                # SAM infrastructure template
├── 📄 HACKATHON_SUBMISSION.md      # Detailed hackathon submission
└── 📄 README.md                    # This file
```

## 🧪 Testing & Quality Assurance

### Comprehensive Test Suite

Run the full test suite:
```bash
# Performance and reliability testing
python tests/run_performance_reliability_tests.py

# Generate performance analysis report
python tests/performance_analysis_report.py

# End-to-end validation
python tests/comprehensive_e2e_validation.py
```

### Test Coverage
- ✅ **Performance Testing**: Concurrent load handling
- ✅ **Reliability Testing**: Multi-run consistency validation
- ✅ **Integration Testing**: End-to-end workflow validation
- ✅ **Agent Testing**: Individual agent performance monitoring

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [🏗 Architecture Overview](docs/architecture-diagram.md) | System design and component interaction |
| [💻 Development Guide](docs/development/DEVELOPMENT.md) | Local setup and development workflow |
| [🚀 Deployment Guide](docs/deployment/) | Production deployment instructions |
| [🏆 Hackathon Submission](HACKATHON_SUBMISSION.md) | Detailed project overview for judges |

## 🎯 Hackathon Highlights

### 🚀 Innovation
- **Multi-Agent Orchestration**: Complex coordination of 6 specialized agents
- **Real-time Debugging**: Live agent execution monitoring dashboard
- **Interactive Audio**: Word-level timing for seamless user experience

### 🛠 Technical Excellence
- **Production Ready**: Fully deployed and operational
- **Performance Optimized**: Excellent response times and reliability
- **Comprehensive Testing**: Extensive test suite with detailed reporting

### 👥 User Experience
- **Instant Access**: Pre-generated content loads immediately
- **Engaging Content**: Conversational, podcast-style delivery
- **Mobile Responsive**: Works seamlessly across all devices

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`python tests/run_performance_reliability_tests.py`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **AWS Bedrock Team** for the powerful Claude Haiku model
- **Amazon Polly Team** for high-quality neural voice synthesis
- **AWS SAM Team** for excellent infrastructure-as-code tooling

---

**🏆 Built with ❤️ for the AWS Agent Hackathon**

*Demonstrating the power of multi-agent systems with AWS Bedrock*