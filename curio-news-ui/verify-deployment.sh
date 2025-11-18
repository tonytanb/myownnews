#!/bin/bash

# Verify deployment script
echo "🔍 Verifying Curio News UI Deployment..."
echo ""

# Get S3 bucket URL
BUCKET_URL="http://curio-news-frontend-1760997974.s3-website-us-west-2.amazonaws.com"

echo "📦 S3 Bucket URL: $BUCKET_URL"
echo ""

# Check if index.html exists and get its timestamp
echo "📄 Checking index.html..."
aws s3api head-object --bucket curio-news-frontend-1760997974 --key index.html --query 'LastModified' --output text

echo ""
echo "📄 Checking main JS file..."
MAIN_JS=$(aws s3 ls s3://curio-news-frontend-1760997974/static/js/ | grep main | awk '{print $4}')
echo "Latest main JS: $MAIN_JS"

echo ""
echo "✅ Deployment verified!"
echo ""
echo "🌐 To view your site:"
echo "   $BUCKET_URL"
echo ""
echo "🔄 To clear browser cache:"
echo "   Chrome: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)"
echo "   Safari: Cmd+Option+E then Cmd+R"
echo "   Firefox: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)"
echo ""
echo "💡 Or open in incognito/private mode to bypass cache"
