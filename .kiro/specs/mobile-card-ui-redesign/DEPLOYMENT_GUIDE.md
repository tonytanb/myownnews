# Mobile Card UI Deployment Guide

## Overview

This guide covers the deployment process for the mobile card UI redesign feature. The card UI is controlled by a feature flag and can be enabled/disabled without code changes.

## Prerequisites

- Node.js 16+ installed
- AWS Amplify CLI configured
- Access to the production environment
- All tasks 1-14 completed

## Deployment Steps

### 1. Enable Feature Flag

Update the production environment variable:

```bash
# Edit curio-news-ui/.env.production
REACT_APP_ENABLE_CARD_UI=true
```

### 2. Build Production Bundle

```bash
cd curio-news-ui
npm run build
```

**Expected Output:**
- Build completes successfully
- Bundle size: ~120KB (gzipped)
- No critical errors (warnings are acceptable)

### 3. Test Build Locally

```bash
# Install serve if not already installed
npm install -g serve

# Serve the production build
serve -s build -p 3000
```

Visit `http://localhost:3000` and verify:
- Card UI loads correctly
- Swipe gestures work
- Audio playback functions
- Media loads properly

### 4. Deploy to Amplify

The deployment happens automatically via git:

```bash
# Commit changes
git add curio-news-ui/.env.production
git commit -m "Enable mobile card UI feature flag"

# Push to deploy
git push origin main
```

Amplify will automatically:
1. Detect the push
2. Run the build process
3. Deploy to production
4. Invalidate CloudFront cache

### 5. Monitor Deployment

**AWS Amplify Console:**
1. Go to AWS Amplify Console
2. Select your app
3. Monitor the build progress
4. Check for any errors

**Expected Timeline:**
- Build: 3-5 minutes
- Deploy: 1-2 minutes
- Total: 5-7 minutes

### 6. Validate Deployment

Run the validation script:

```bash
python3 .kiro/specs/mobile-card-ui-redesign/validate-deployment.py
```

**Success Criteria:**
- ✅ Feature flag enabled
- ✅ All card UI components present
- ✅ API health check passes
- ✅ Card data transformation works
- ⚠️  Performance metrics within acceptable range

### 7. Monitor Performance

Run continuous monitoring:

```bash
python3 .kiro/specs/mobile-card-ui-redesign/monitor-performance.py
```

This will monitor for 5 minutes and report:
- API response times
- Error rates
- Response sizes
- Alerts for threshold violations

## Rollback Procedure

If issues are detected, rollback immediately:

### Quick Rollback (Feature Flag)

```bash
# Disable feature flag
echo "REACT_APP_ENABLE_CARD_UI=false" > curio-news-ui/.env.production

# Commit and push
git add curio-news-ui/.env.production
git commit -m "Disable card UI feature flag"
git push origin main
```

This will revert to the traditional UI without losing any code.

### Full Rollback (Git)

```bash
# Revert to previous commit
git revert HEAD

# Push to deploy
git push origin main
```

## Performance Benchmarks

### Target Metrics

| Metric | Target | Acceptable | Critical |
|--------|--------|------------|----------|
| API Response Time | < 2s | < 3s | > 5s |
| First Card Load | < 1s | < 2s | > 3s |
| Card Transition | 500ms | 700ms | > 1s |
| Memory Usage | < 80MB | < 100MB | > 150MB |

### Monitoring Tools

1. **AWS CloudWatch**
   - Lambda execution times
   - API Gateway latency
   - Error rates

2. **Browser DevTools**
   - Network tab for load times
   - Performance tab for rendering
   - Memory profiler

3. **Custom Scripts**
   - `validate-deployment.py` - One-time validation
   - `monitor-performance.py` - Continuous monitoring

## Troubleshooting

### Issue: Build Fails

**Symptoms:**
- npm build command fails
- TypeScript errors
- Missing dependencies

**Solution:**
```bash
# Clean install
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Issue: Feature Flag Not Working

**Symptoms:**
- Card UI doesn't appear
- Traditional UI still showing

**Solution:**
1. Verify `.env.production` has correct value
2. Clear browser cache
3. Check browser console for errors
4. Verify build includes updated env file

### Issue: API Errors

**Symptoms:**
- Cards don't load
- "Failed to fetch" errors
- Empty card stack

**Solution:**
1. Check API endpoint is accessible
2. Verify CORS configuration
3. Check Lambda function logs in CloudWatch
4. Validate API Gateway configuration

### Issue: Media Not Loading

**Symptoms:**
- Blank backgrounds
- Fallback images showing
- Video playback fails

**Solution:**
1. Check media URLs are accessible
2. Verify CORS headers on media sources
3. Check browser console for blocked requests
4. Test with different media sources

### Issue: Performance Degradation

**Symptoms:**
- Slow card transitions
- High memory usage
- Laggy animations

**Solution:**
1. Check number of preloaded cards
2. Verify media file sizes
3. Monitor memory leaks in DevTools
4. Reduce animation complexity if needed

## Post-Deployment Checklist

- [ ] Feature flag enabled in production
- [ ] Build completed successfully
- [ ] Deployment verified in Amplify Console
- [ ] Validation script passes
- [ ] Performance metrics within targets
- [ ] Mobile devices tested (iOS & Android)
- [ ] Desktop browsers tested (Chrome, Firefox, Safari)
- [ ] Error monitoring active
- [ ] Team notified of deployment
- [ ] Documentation updated

## Monitoring Schedule

### First 24 Hours
- Check metrics every 2 hours
- Monitor error rates closely
- Review user feedback
- Watch for performance issues

### First Week
- Daily metric reviews
- Weekly performance reports
- User feedback analysis
- Bug triage and fixes

### Ongoing
- Weekly performance reviews
- Monthly optimization reviews
- Quarterly feature enhancements
- Continuous user feedback monitoring

## Support Contacts

- **Technical Issues:** Check CloudWatch logs
- **Deployment Issues:** AWS Amplify Console
- **Performance Issues:** Run monitoring scripts
- **User Feedback:** Analytics dashboard

## Additional Resources

- [AWS Amplify Documentation](https://docs.amplify.aws/)
- [React Performance Optimization](https://react.dev/learn/render-and-commit)
- [Framer Motion Docs](https://www.framer.com/motion/)
- [Web Vitals](https://web.dev/vitals/)

## Success Metrics

Track these KPIs post-deployment:

1. **User Engagement**
   - Time spent per card
   - Cards viewed per session
   - Audio playback rate
   - Swipe vs tap navigation ratio

2. **Technical Performance**
   - Page load time
   - Time to interactive
   - Memory usage
   - Error rate

3. **User Satisfaction**
   - User feedback scores
   - Feature adoption rate
   - Return user rate
   - Session duration

## Conclusion

The mobile card UI is now deployed and ready for production use. Monitor the metrics closely for the first 24-48 hours and be prepared to rollback if critical issues arise.

For questions or issues, refer to the troubleshooting section or check the validation scripts for detailed diagnostics.
