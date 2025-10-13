#!/bin/bash
# Quick deployment script for MyOwnNews

set -e

echo "🚀 Building MyOwnNews..."
sam build --use-container

echo "📦 Deploying to AWS..."
sam deploy

echo "✅ Deployment complete!"
echo "Function: $(aws cloudformation describe-stacks --stack-name myownnews-mvp --query 'Stacks[0].Outputs[?OutputKey==`FunctionName`].OutputValue' --output text)"
echo "Bucket: $(aws cloudformation describe-stacks --stack-name myownnews-mvp --query 'Stacks[0].Outputs[?OutputKey==`BucketName`].OutputValue' --output text)"