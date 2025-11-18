#!/bin/bash

# Deploy Card UI to Production
# This script builds and deploys the mobile card UI redesign

set -e

echo "🚀 Starting Card UI Deployment Process..."
echo ""

# Step 1: Enable Card UI feature flag
echo "📝 Step 1: Enabling Card UI feature flag..."
cd curio-news-ui

# Update .env.production to enable card UI
cat > .env.production << EOF
REACT_APP_API_URL=https://nqot0dir0h.execute-api.us-west-2.amazonaws.com/prod
REACT_APP_ENABLE_CARD_UI=true
EOF

echo "✅ Feature flag enabled in .env.production"
echo ""

# Step 2: Build production bundle
echo "🔨 Step 2: Building production bundle..."
npm run build

if [ $? -eq 0 ]; then
    echo "✅ Production build completed successfully"
else
    echo "❌ Build failed"
    exit 1
fi
echo ""

# Step 3: Check build size
echo "📊 Step 3: Analyzing build size..."
BUILD_SIZE=$(du -sh build | cut -f1)
echo "Build size: $BUILD_SIZE"

# Check if build directory exists and has files
if [ -d "build" ] && [ "$(ls -A build)" ]; then
    echo "✅ Build directory contains files"
else
    echo "❌ Build directory is empty or missing"
    exit 1
fi
echo ""

# Step 4: Deploy to Amplify
echo "🌐 Step 4: Deploying to AWS Amplify..."
echo "Note: Amplify will automatically deploy on git push"
echo ""

# Step 5: Display deployment info
echo "📋 Deployment Summary:"
echo "  - Feature Flag: REACT_APP_ENABLE_CARD_UI=true"
echo "  - Build Size: $BUILD_SIZE"
echo "  - API Endpoint: https://nqot0dir0h.execute-api.us-west-2.amazonaws.com/prod"
echo ""

echo "✅ Deployment preparation complete!"
echo ""
echo "Next steps:"
echo "  1. Commit changes: git add . && git commit -m 'Enable card UI feature'"
echo "  2. Push to deploy: git push"
echo "  3. Monitor deployment in AWS Amplify Console"
echo "  4. Run validation: python3 .kiro/specs/mobile-card-ui-redesign/validate-deployment.py"
echo ""
