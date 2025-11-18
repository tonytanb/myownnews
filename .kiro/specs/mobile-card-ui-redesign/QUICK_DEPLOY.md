# Quick Deployment Reference

## 🚀 Deploy in 5 Steps

### 1. Enable Feature Flag ✅ (Already Done)
```bash
# File: curio-news-ui/.env.production
REACT_APP_ENABLE_CARD_UI=true
```

### 2. Build
```bash
cd curio-news-ui && npm run build
```

### 3. Deploy
```bash
git add .
git commit -m "Enable mobile card UI"
git push origin main
```

### 4. Validate
```bash
python3 .kiro/specs/mobile-card-ui-redesign/validate-deployment.py
```

### 5. Monitor
```bash
python3 .kiro/specs/mobile-card-ui-redesign/monitor-performance.py
```

## 🔄 Quick Rollback

```bash
echo "REACT_APP_ENABLE_CARD_UI=false" > curio-news-ui/.env.production
git add curio-news-ui/.env.production
git commit -m "Disable card UI"
git push origin main
```

## 📊 Key Metrics

- **API Response:** < 3s (target)
- **Card Load:** < 2s
- **Transition:** 500ms
- **Memory:** < 100MB

## ✅ Success Checklist

- [ ] Build completes without errors
- [ ] Validation script passes
- [ ] Mobile devices tested
- [ ] Desktop browsers tested
- [ ] Performance within targets
- [ ] No critical errors in logs

## 🆘 Emergency Contacts

- **Logs:** AWS CloudWatch
- **Deployment:** AWS Amplify Console
- **Validation:** Run validation script
- **Rollback:** Use quick rollback above

## 📚 Full Documentation

See `DEPLOYMENT_GUIDE.md` for complete instructions.
