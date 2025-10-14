#!/bin/bash

# Simple Lambda deployment script
echo "🚀 Deploying Lambda function..."

# Create deployment package
echo "📦 Creating deployment package..."
rm -f lambda-deployment.zip
zip -r lambda-deployment.zip app.py requirements.txt

# Get the Lambda function name (you'll need to update this)
FUNCTION_NAME="myownnews-function"  # Update this to your actual function name

# Deploy to AWS Lambda
echo "☁️ Uploading to AWS Lambda..."
aws lambda update-function-code \
    --function-name $FUNCTION_NAME \
    --zip-file fileb://lambda-deployment.zip

if [ $? -eq 0 ]; then
    echo "✅ Deployment successful!"
    echo "🎉 Your Lambda function has been updated with word timing support"
else
    echo "❌ Deployment failed. Check your AWS credentials and function name."
fi

# Clean up
rm -f lambda-deployment.zip