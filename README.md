# Curio News - AI-Powered News Briefing

A modern news briefing application that uses AI to curate and narrate daily news in a millennial-friendly format.

## Features

- 🤖 **AI-Powered Curation**: Uses AWS Bedrock (Claude) to select and summarize trending news
- 🎙️ **High-Quality Audio**: ElevenLabs voice synthesis with Polly fallback
- 📰 **Multi-Source News**: RSS feeds from BBC, Reuters, CNN, TechCrunch, and more
- 🎵 **Interactive Transcript**: Click any word to jump to that point in the audio
- 📱 **Responsive Design**: Works great on desktop and mobile
- ⚡ **Real-time**: Fresh content generated on-demand

## Architecture

### Backend (AWS)
- **AWS Lambda**: News processing and audio generation
- **AWS S3**: Audio file storage with presigned URLs
- **AWS API Gateway**: RESTful API endpoints
- **AWS Bedrock**: Claude AI for content curation
- **Amazon Polly**: Fallback text-to-speech
- **ElevenLabs**: Premium voice synthesis

### Frontend (React)
- **React 18**: Modern UI framework
- **TypeScript**: Type-safe development
- **CSS Grid**: Responsive 2-column layout
- **Web Audio API**: Audio playback controls

## Deployment

### Backend
```bash
# Deploy AWS infrastructure
sam build --use-container
sam deploy --parameter-overrides ElevenLabsApiKey="your-key" VoiceProvider="elevenlabs"
```

### Frontend
Deploy to AWS Amplify by connecting your GitHub repository.

## API Endpoints

- `GET /latest` - Get the most recent news briefing with presigned audio URL
- `GET /sign?key=<s3-key>` - Get presigned URL for any S3 object

## Environment Variables

### Backend (Lambda)
- `ELEVENLABS_API_KEY` - ElevenLabs API key for premium voices
- `NEWSDATA_API_KEY` - NewsData.io API key (optional)
- `VOICE_PROVIDER` - "elevenlabs" or "polly"
- `VOICE_ID` - Voice ID for the selected provider

### Frontend (React)
- `REACT_APP_API_URL` - API Gateway endpoint URL

## Development

```bash
# Install dependencies
cd curio-news-ui
npm install

# Start development server
npm start

# Build for production
npm run build
```

## News Sources

- BBC World News
- Reuters
- CNN
- Associated Press
- NPR
- The Guardian
- TechCrunch
- Ars Technica

## License

MIT License - see LICENSE file for details