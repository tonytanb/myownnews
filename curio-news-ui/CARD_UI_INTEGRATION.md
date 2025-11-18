# Card UI Integration Guide

## Overview

The mobile card UI has been successfully integrated into the Curio app with a feature flag system. This allows for easy A/B testing and gradual rollout.

## Feature Flag

The card UI is controlled by the `REACT_APP_ENABLE_CARD_UI` environment variable.

### Enabling Card UI

**Development (.env.local):**
```bash
REACT_APP_ENABLE_CARD_UI=true
```

**Production (.env.production):**
```bash
REACT_APP_ENABLE_CARD_UI=true
```

### Default State

By default, the card UI is **disabled** (`false`) to preserve the existing UI for rollback safety.

## Implementation Details

### Subtask 11.1: Feature Flag
- ✅ Added `REACT_APP_ENABLE_CARD_UI` environment variable to `.env.local` and `.env.production`
- ✅ Conditional rendering in `App.tsx` based on feature flag
- ✅ Existing UI components preserved for rollback

### Subtask 11.2: Bootstrap Data Transformation
- ✅ Bootstrap data stored in state (`bootstrapData`)
- ✅ Data passed to `CurioCardStack` component
- ✅ `transformToCards()` function called within `CurioCardStack`
- ✅ Full compatibility with existing API maintained

### Subtask 11.3: Agent Trace and Analytics
- ✅ Analytics overlay added for card UI mode
- ✅ `AgentCollaborationTrace` component accessible in overlay
- ✅ `AgentTrace` component accessible in overlay
- ✅ Floating analytics toggle button (📊) in bottom-right corner
- ✅ `DebuggingDashboard` modal still accessible

## Usage

### Traditional UI (Default)
When `REACT_APP_ENABLE_CARD_UI=false` or not set:
- Full scrollable news feed
- Audio player with transcript
- Weekend recommendations
- Media gallery (dev mode)
- Agent provenance section

### Card UI Mode
When `REACT_APP_ENABLE_CARD_UI=true`:
- Full-screen swipeable story cards
- Mobile-first design (380px × 680px)
- Video/image backgrounds
- Per-card audio playback
- Smooth Framer Motion animations
- Floating analytics button (📊)
- Analytics overlay with agent traces

## Analytics in Card UI

Click the floating 📊 button (bottom-right) to open the analytics overlay:
- **Agent Collaboration**: Real-time multi-agent collaboration trace
- **Detailed Trace**: Full AWS Bedrock agent execution trace
- **Debug Dashboard**: Comprehensive debugging tools (via modal)

## Desktop vs Mobile

### Desktop (>768px)
- Card centered on black background
- 380px × 680px card dimensions
- Border radius and box shadow
- Keyboard navigation (arrow keys)

### Mobile (≤767px)
- Full viewport card (100vw × 100vh)
- Touch-optimized swipe gestures
- 44px minimum touch targets

## Testing

### Build Test
```bash
cd curio-news-ui
npm run build
```

### Development Test
```bash
cd curio-news-ui
npm start
```

Then toggle `REACT_APP_ENABLE_CARD_UI` in `.env.local` and refresh.

## Rollback Plan

If issues arise with the card UI:

1. Set `REACT_APP_ENABLE_CARD_UI=false` in environment files
2. Rebuild and redeploy
3. Traditional UI will be restored immediately
4. No data loss or API changes required

## Requirements Met

- ✅ **Requirement 9.7**: Maintain compatibility with existing Bedrock orchestrator API endpoints
- ✅ **Requirement 13.1**: Center card interface on screens larger than mobile dimensions
- ✅ **Requirement 13.2**: Maintain 380px × 680px card dimensions on desktop displays
- ✅ **Requirement 13.4**: Use black background outside card area on larger screens

## Next Steps

1. Enable feature flag in staging environment
2. Conduct A/B testing with 10% of users
3. Gather user feedback and metrics
4. Optimize based on performance data
5. Gradual rollout to 100% of users
6. Remove old UI components after 2 weeks of stable operation

## Files Modified

- `curio-news-ui/.env.local` - Added feature flag
- `curio-news-ui/.env.production` - Added feature flag
- `curio-news-ui/src/App.tsx` - Conditional rendering logic
- `curio-news-ui/src/App.css` - Card UI and analytics overlay styles

## Files Used (No Changes)

- `curio-news-ui/src/components/cards/CurioCardStack.tsx` - Main card container
- `curio-news-ui/src/utils/cardTransformer.ts` - Data transformation
- `curio-news-ui/src/components/AgentTrace.tsx` - Agent trace component
- `curio-news-ui/src/components/AgentCollaborationTrace.tsx` - Collaboration trace
- `curio-news-ui/src/components/DebuggingDashboard.tsx` - Debug dashboard

## Support

For issues or questions:
1. Check console logs for errors
2. Verify environment variables are set correctly
3. Ensure bootstrap API returns valid data
4. Test with feature flag disabled to isolate issues
