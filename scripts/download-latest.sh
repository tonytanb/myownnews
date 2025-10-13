#!/bin/bash
# Download and organize the latest generated content from S3

set -e

# Get the latest function execution
FUNCTION_NAME=$(aws cloudformation describe-stacks --stack-name myownnews-mvp --region us-west-2 --query 'Stacks[0].Outputs[?OutputKey==`FunctionName`].OutputValue' --output text)
BUCKET_NAME=$(aws cloudformation describe-stacks --stack-name myownnews-mvp --region us-west-2 --query 'Stacks[0].Outputs[?OutputKey==`BucketName`].OutputValue' --output text)

echo "🎙️ Downloading latest MyOwnNews content..."
echo "Function: $FUNCTION_NAME"
echo "Bucket: $BUCKET_NAME"

# Test the function to generate new content
echo "📡 Generating new content..."
aws lambda invoke --function-name "$FUNCTION_NAME" --region us-west-2 response.json

if [ $? -eq 0 ]; then
    echo "✅ Function executed successfully!"
    
    # Extract file keys from response
    SCRIPT_KEY=$(cat response.json | jq -r '.body | fromjson | .script_key')
    AUDIO_KEY=$(cat response.json | jq -r '.body | fromjson | .audio_key')
    META_KEY=$(cat response.json | jq -r '.body | fromjson | .meta_key')
    
    # Create timestamp for local files
    TIMESTAMP=$(date +"%Y-%m-%d_%H-%M")
    
    echo "📄 Downloading script..."
    aws s3 cp "s3://$BUCKET_NAME/$SCRIPT_KEY" "generated/scripts/working/${TIMESTAMP}_claude-haiku_latest.txt" --region us-west-2
    
    echo "🎵 Downloading audio..."
    aws s3 cp "s3://$BUCKET_NAME/$AUDIO_KEY" "generated/audio/working/${TIMESTAMP}_joanna-neural_latest.mp3" --region us-west-2
    
    echo "📊 Downloading metadata..."
    aws s3 cp "s3://$BUCKET_NAME/$META_KEY" "generated/metadata/working/${TIMESTAMP}_metadata.json" --region us-west-2
    
    echo "📋 Script preview:"
    head -n 5 "generated/scripts/working/${TIMESTAMP}_claude-haiku_latest.txt"
    
    echo ""
    echo "🎉 Latest content downloaded to generated/*/working/"
    echo "🎧 Play audio: generated/audio/working/${TIMESTAMP}_joanna-neural_latest.mp3"
    
    # Clean up
    rm -f response.json
    
else
    echo "❌ Function failed. Check response.json for details."
fi