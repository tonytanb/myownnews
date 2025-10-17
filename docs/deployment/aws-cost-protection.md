# AWS Cost Protection Setup

## 1. Billing Alerts (CRITICAL)
- Go to AWS Billing Console
- Set up alerts at: $5, $10, $15, $20
- Enable email notifications

## 2. Budget Setup
- AWS Budgets → Create Budget
- Set $20 monthly limit
- Alert at 80% ($16) and 100% ($20)
- Action: Stop services at 100%

## 3. Service Limits
### Lambda
- Set reserved concurrency: 5 (prevents runaway costs)
- Timeout: 30 seconds max

### S3
- Lifecycle policy: Delete files older than 30 days
- Versioning: Disabled (saves storage)

### Amplify
- Build minutes: Monitor (free tier = 1000 min/month)

## 4. Cost Monitoring Commands
```bash
# Check current month costs
aws ce get-cost-and-usage --time-period Start=2025-10-01,End=2025-10-31 --granularity MONTHLY --metrics BlendedCost

# Check service breakdown
aws ce get-dimension-values --dimension SERVICE --time-period Start=2025-10-01,End=2025-10-31
```

## 5. Emergency Shutdown
If costs spike:
1. Disable Lambda function
2. Stop Amplify app
3. Delete S3 objects
4. Contact AWS support