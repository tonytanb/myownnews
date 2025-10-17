#!/bin/bash

# Simple S3 frontend deployment
BUCKET_NAME="curio-news-frontend-$(date +%s)"
REGION="us-west-2"

echo "🚀 Creating S3 bucket for frontend..."
aws s3 mb s3://$BUCKET_NAME --region $REGION

echo "🌐 Configuring bucket for static website hosting..."
aws s3 website s3://$BUCKET_NAME --index-document index.html --error-document index.html

echo "📝 Setting bucket policy for public access..."
cat > /tmp/bucket-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::$BUCKET_NAME/*"
        }
    ]
}
EOF

aws s3api put-bucket-policy --bucket $BUCKET_NAME --policy file:///tmp/bucket-policy.json

echo "📦 Uploading frontend build..."
cd curio-news-ui
aws s3 sync build/ s3://$BUCKET_NAME --delete

echo "✅ Frontend deployed!"
echo "🌐 Website URL: http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com"

# Save the URL for later
echo "http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com" > ../frontend-url.txt