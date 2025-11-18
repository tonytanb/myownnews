#!/bin/bash

# Test Card UI Integration
# This script verifies the card UI integration is working correctly

echo "🧪 Testing Card UI Integration..."
echo ""

# Check if environment files exist
echo "1. Checking environment files..."
if [ -f ".env.local" ]; then
    echo "   ✅ .env.local exists"
    if grep -q "REACT_APP_ENABLE_CARD_UI" .env.local; then
        echo "   ✅ REACT_APP_ENABLE_CARD_UI found in .env.local"
        grep "REACT_APP_ENABLE_CARD_UI" .env.local
    else
        echo "   ❌ REACT_APP_ENABLE_CARD_UI not found in .env.local"
        exit 1
    fi
else
    echo "   ❌ .env.local not found"
    exit 1
fi

if [ -f ".env.production" ]; then
    echo "   ✅ .env.production exists"
    if grep -q "REACT_APP_ENABLE_CARD_UI" .env.production; then
        echo "   ✅ REACT_APP_ENABLE_CARD_UI found in .env.production"
        grep "REACT_APP_ENABLE_CARD_UI" .env.production
    else
        echo "   ❌ REACT_APP_ENABLE_CARD_UI not found in .env.production"
        exit 1
    fi
else
    echo "   ❌ .env.production not found"
    exit 1
fi

echo ""

# Check if App.tsx has the integration
echo "2. Checking App.tsx integration..."
if grep -q "enableCardUI" src/App.tsx; then
    echo "   ✅ enableCardUI variable found"
else
    echo "   ❌ enableCardUI variable not found"
    exit 1
fi

if grep -q "CurioCardStack" src/App.tsx; then
    echo "   ✅ CurioCardStack import found"
else
    echo "   ❌ CurioCardStack import not found"
    exit 1
fi

if grep -q "bootstrapData" src/App.tsx; then
    echo "   ✅ bootstrapData state found"
else
    echo "   ❌ bootstrapData state not found"
    exit 1
fi

echo ""

# Check if CSS has card UI styles
echo "3. Checking App.css styles..."
if grep -q "app--card-ui" src/App.css; then
    echo "   ✅ Card UI styles found"
else
    echo "   ❌ Card UI styles not found"
    exit 1
fi

if grep -q "analytics-overlay" src/App.css; then
    echo "   ✅ Analytics overlay styles found"
else
    echo "   ❌ Analytics overlay styles not found"
    exit 1
fi

if grep -q "analytics-toggle-btn--floating" src/App.css; then
    echo "   ✅ Floating analytics button styles found"
else
    echo "   ❌ Floating analytics button styles not found"
    exit 1
fi

echo ""

# Check if CurioCardStack component exists
echo "4. Checking CurioCardStack component..."
if [ -f "src/components/cards/CurioCardStack.tsx" ]; then
    echo "   ✅ CurioCardStack.tsx exists"
else
    echo "   ❌ CurioCardStack.tsx not found"
    exit 1
fi

if [ -f "src/components/cards/CurioCardStack.css" ]; then
    echo "   ✅ CurioCardStack.css exists"
else
    echo "   ❌ CurioCardStack.css not found"
    exit 1
fi

echo ""

# Check if cardTransformer utility exists
echo "5. Checking cardTransformer utility..."
if [ -f "src/utils/cardTransformer.ts" ]; then
    echo "   ✅ cardTransformer.ts exists"
    if grep -q "transformToCards" src/utils/cardTransformer.ts; then
        echo "   ✅ transformToCards function found"
    else
        echo "   ❌ transformToCards function not found"
        exit 1
    fi
else
    echo "   ❌ cardTransformer.ts not found"
    exit 1
fi

echo ""

# Try to build the project
echo "6. Testing build..."
echo "   Building project (this may take a moment)..."
if npm run build > /dev/null 2>&1; then
    echo "   ✅ Build successful"
else
    echo "   ❌ Build failed"
    echo "   Run 'npm run build' to see detailed errors"
    exit 1
fi

echo ""
echo "✅ All integration tests passed!"
echo ""
echo "📝 Next steps:"
echo "   1. Set REACT_APP_ENABLE_CARD_UI=true in .env.local to enable card UI"
echo "   2. Run 'npm start' to test in development"
echo "   3. Navigate to http://localhost:3000"
echo "   4. You should see the card UI if enabled, or traditional UI if disabled"
echo ""
echo "🎉 Integration complete!"
