#!/bin/bash
# Test the deployed function and download results

set -e

FUNCTION_NAME=$(aws cloudformation describe-stacks --stack-name myownnews-mvp --query 'Stacks[0].Outputs[?OutputKey==`FunctionName`].OutputValue' --output text)
BUCKET_NAME=$(aws cloudformation describe-stacks --stack-name myownnews-mvp --query 'Stacks[0].Outputs[?OutputKey==`BucketName`].OutputValue' --output text)

echo "🧪 Testing function: $FUNCTION_NAME"
aws lambda invoke --function-name "$FUNCTION_NAME" response.json

if [ $? -eq 0 ]; then
    echo "✅ Function executed successfully!"
    
    # Extract file keys from response
    SCRIPT_KEY=$(cat response.json | jq -r '.body | fromjson | .script_key')
    AUDIO_KEY=$(cat response.json | jq -r '.body | fromjson | .audio_key')
    
    echo "📄 Downloading script..."
    aws s3 cp "s3://$BUCKET_NAME/$SCRIPT_KEY" ./latest-script.txt
    
    echo "🎵 Downloading audio..."
    aws s3 cp "s3://$BUCKET_NAME/$AUDIO_KEY" ./latest-news.mp3
    
    echo "📊 Script preview:"
    head -n 5 ./latest-script.txt
    
    echo "🎉 Test complete! Files: latest-script.txt, latest-news.mp3"
else
    echo "❌ Function failed. Check response.json for details."
fi