# MyOwnNews (MVP)

Serverless news summarizer & audio generator built with AWS SAM.

## Quick start
```bash
sam build --use-container
sam deploy --profile work-nvirginia
cat > docs/learning-cards.md << 'EOF'
Learning Cards — MyOwnNews MVP

AWS SAM Basics

What: IaC framework for serverless apps.

Why: Lets us deploy Lambda, S3, IAM, etc. as one stack.

Lambda

Role: Python function fetches RSS, summarizes with Bedrock, generates audio with Polly.

Trigger: Manual now, schedulable later.

S3 Buckets

Purpose: Stores script, audio, metadata.

Keys: Organized by date.

Bedrock (Titan model)

Role: Summarizes RSS into short text.

Learning: IAM must allow model IDs.

Polly

Role: Converts text → lifelike audio.

Why: Creates daily audio brief.

CloudFormation

Role: SAM uses it under the hood.

Pro tip: Apply tags for billing.

Cost Management

Tags: Project=MyOwnNews, Environment=Dev, Owner=Tony.

Billing: Activate tags in Cost Explorer.
