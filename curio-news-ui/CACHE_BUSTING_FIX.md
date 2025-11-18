# Cache Busting Fix - Curio News UI

## Problem
UI changes weren't appearing after S3 deployment due to aggressive browser caching.

## Solution Implemented

### 1. Added Axios for Better HTTP Handling
- Installed `axios` package
- Created `src/utils/api.ts` utility with:
  - Automatic cache-busting via timestamp query parameters (`?_t=timestamp`)
  - Centralized API configuration
  - Better error handling

### 2. Updated App.tsx
- Replaced `fetch` calls with axios-based API utility
- All API requests now include cache-busting timestamps
- Improved error handling with axios interceptors

### 3. Deployment with Aggressive Cache Control
```bash
aws s3 sync curio-news-ui/build/ s3://curio-news-frontend-1760997974/ \
  --delete \
  --cache-control "no-cache, no-store, must-revalidate, max-age=0" \
  --metadata-directive REPLACE
```

## How to See Changes

### Option 1: Hard Refresh (Recommended)
- **Chrome/Firefox**: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows)
- **Safari**: `Cmd+Option+E` then `Cmd+R`

### Option 2: Incognito/Private Mode
Open the site in a private browsing window to bypass all cache

### Option 3: Clear Browser Cache
1. Open DevTools (F12)
2. Right-click the refresh button
3. Select "Empty Cache and Hard Reload"

## Verification
Run the verification script:
```bash
./curio-news-ui/verify-deployment.sh
```

## What Changed
- ✅ Axios installed and configured
- ✅ Cache-busting timestamps on all API calls
- ✅ S3 objects deployed with no-cache headers
- ✅ Better error handling and retry logic
- ✅ Improved API response handling

## Site URL
http://curio-news-frontend-1760997974.s3-website-us-west-2.amazonaws.com

## Next Deployment
For future deployments, use:
```bash
cd curio-news-ui
npm run build
aws s3 sync build/ s3://curio-news-frontend-1760997974/ --delete --cache-control "no-cache, no-store, must-revalidate, max-age=0"
```

The axios cache-busting will handle API-level caching automatically.
