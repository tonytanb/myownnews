#!/bin/bash

echo "🚨 EMERGENCY: Shutting down AWS resources to prevent charges"

# 1. Disable Lambda function
echo "Disabling Lambda function..."
aws lambda put-function-configuration \
  --function-name myownnews-mvp-NewsToAudioFunction-KbBGbIXlm0l7 \
  --environment Variables='{DISABLED=true}'

# 2. Delete Amplify app (optional - only if desperate)
# aws amplify delete-app --app-id d347ijk5pbyj

# 3. Delete all S3 objects (keep bucket)
echo "Deleting S3 objects..."
aws s3 rm s3://myownnews-mvp-assetsbucket-kozbz1eooh6q --recursive

echo "✅ Emergency shutdown complete. Contact AWS support if needed."