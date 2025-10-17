# MyOwnNews Deployment Action

A GitHub Action to deploy the MyOwnNews serverless application using AWS SAM.

## Features

- 🚀 **One-click deployment** of MyOwnNews to AWS
- 🎙️ **Voice provider flexibility** (Amazon Polly or ElevenLabs)
- 🔧 **Configurable parameters** for different environments
- 📡 **Automatic function URL creation** with proper permissions
- 🧪 **Built-in testing** of deployed endpoints

## Usage

### Basic Usage

```yaml
- name: Deploy MyOwnNews
  uses: tonytanb/myownnews@v1
  with:
    aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
    aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    news-api-key: ${{ secrets.NEWS_API_KEY }}
```

### Advanced Usage

```yaml
- name: Deploy MyOwnNews with ElevenLabs
  uses: tonytanb/myownnews@v1
  with:
    aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
    aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    aws-region: 'us-west-2'
    stack-name: 'myownnews-prod'
    news-api-key: ${{ secrets.NEWS_API_KEY }}
    elevenlabs-api-key: ${{ secrets.ELEVENLABS_API_KEY }}
    voice-provider: 'elevenlabs'
    voice-id: '21m00Tcm4TlvDq8ikWAM'
```

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `aws-access-key-id` | AWS Access Key ID | ✅ | - |
| `aws-secret-access-key` | AWS Secret Access Key | ✅ | - |
| `aws-region` | AWS Region | ❌ | `us-west-2` |
| `stack-name` | CloudFormation stack name | ❌ | `myownnews-mvp` |
| `news-api-key` | News API Key from newsapi.org | ✅ | - |
| `elevenlabs-api-key` | ElevenLabs API Key | ❌ | `''` |
| `voice-provider` | Voice provider (polly or elevenlabs) | ❌ | `polly` |
| `voice-id` | Voice ID | ❌ | `Joanna` |

## Outputs

| Output | Description |
|--------|-------------|
| `function-url` | The deployed Lambda function URL |
| `bucket-name` | The S3 bucket name for assets |

## Required Secrets

Set these secrets in your repository settings:

- `AWS_ACCESS_KEY_ID` - Your AWS access key
- `AWS_SECRET_ACCESS_KEY` - Your AWS secret key  
- `NEWS_API_KEY` - Your News API key from [newsapi.org](https://newsapi.org/)
- `ELEVENLABS_API_KEY` - Your ElevenLabs API key (optional)

## Prerequisites

- AWS account with appropriate permissions
- News API key from [newsapi.org](https://newsapi.org/)
- ElevenLabs account (optional, for premium voices)

## What This Action Does

1. **Builds** your SAM application using containers
2. **Deploys** to AWS using CloudFormation
3. **Creates** a Lambda function URL for public access
4. **Configures** proper permissions for the function URL
5. **Tests** the deployment to ensure it's working
6. **Outputs** the function URL and S3 bucket information

## Example Workflow

```yaml
name: Deploy MyOwnNews

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - name: Deploy MyOwnNews
      uses: tonytanb/myownnews@v1
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        news-api-key: ${{ secrets.NEWS_API_KEY }}
        elevenlabs-api-key: ${{ secrets.ELEVENLABS_API_KEY }}
        voice-provider: 'elevenlabs'
```

## License

MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.