# Social Impact Story Curation

## Overview
Enhanced the favorite story selection algorithm to prioritize stories with social impact over financial/market news that benefits fewer people.

## Changes Made

### 1. Increased Social Impact Scoring (6.0 points - HIGHEST)
Stories with social impact keywords now receive the highest score boost:
- Community, society, social justice, equality, diversity
- Mental health awareness, education reform, accessibility
- Healthcare access, affordable housing, food security
- Youth programs, elderly care, disability rights
- Poverty reduction, literacy, job training
- Social change, activism, grassroots initiatives
- **Added**: helping, support, aid, assistance, outreach, service, empowerment, advocacy, awareness

### 2. Increased Financial News Penalty (3.0 points per keyword)
Financial and stock market stories now receive heavier penalties:
- Stock market, trading, investors, Wall Street
- Earnings reports, share prices, dividends
- IPOs, mergers, acquisitions
- Fed rate decisions, market movements
- **Added**: bull market, bear market, portfolio, hedge fund, venture capital

### 3. Adjusted Category Bonuses
- **HEALTH**: 3.0 points (increased from 2.5) - broad social impact
- **GENERAL**: 2.0 points (increased from 1.0) - often covers social issues
- **TECHNOLOGY**: 1.5 points - can have social benefits
- **BUSINESS**: -1.5 points (increased penalty from -0.5) - limited social impact

## Scoring Priority Hierarchy

1. **Social Impact Stories** (6.0 points) - HIGHEST
2. **Scientific Discoveries** (5.0 points)
3. **Good News & Achievements** (4.0 points)
4. **Curiosities & Phenomena** (3.5 points)
5. **Innovation & Technology** (3.0 points)
6. **Environmental Stories** (2.5 points)

## Penalties

- **Negative News**: -3.0 points per keyword (death, violence, disasters)
- **Financial Focus**: -3.0 points per keyword (stocks, trading, markets)
- **Business Category**: -1.5 points baseline

## Test Results

✅ **Test Passed**: The algorithm successfully selected a health story about sleeping aids for older adults over other available stories, demonstrating proper social impact prioritization.

### Selected Story
- **Title**: "New study finds that common sleeping aids worsen sleep in older adults"
- **Category**: HEALTH
- **Social Keywords**: 1 (health-related)
- **Financial Keywords**: 0
- **Reasoning**: Chosen for its potential to positively impact society and spark important conversations

## Why This Matters

Gen Z and Millennials care about:
- **Social justice and equality**
- **Community impact and helping others**
- **Mental health and wellness**
- **Education and accessibility**
- **Environmental sustainability**
- **Positive change and progress**

They care less about:
- Stock market fluctuations
- Corporate earnings reports
- Financial market movements
- Investment returns

## API Deployment

The updated scoring algorithm has been deployed to:
- **API URL**: https://nqot0dir0h.execute-api.us-west-2.amazonaws.com/prod
- **Deployment Time**: 2025-11-06 21:25:00 UTC
- **Status**: ✅ Active

## Verification

Run the test script to verify social impact prioritization:
```bash
python3 test_social_impact_priority.py
```

The test analyzes:
- Total news items available
- Selected favorite story
- Social impact vs financial keyword counts
- Category distribution
- Selection reasoning

## Future Enhancements

Potential improvements:
1. Add more social impact keywords based on user feedback
2. Implement user preference learning
3. Add location-based social impact scoring
4. Include diversity and representation metrics
5. Track long-term impact of selected stories
