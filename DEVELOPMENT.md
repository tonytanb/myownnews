# Development Workflow

## 🚀 Quick Commands

```bash
# Deploy changes
./scripts/deploy.sh

# Test the function
./scripts/test.sh

# View logs for debugging
./scripts/logs.sh

# Local development
sam local invoke NewsToAudioFunction --event events/event.json
```

## 📋 Development Workflow

### 1. **Feature Development**
```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes to code
# Test locally if possible
sam local invoke NewsToAudioFunction --event events/event.json

# Deploy to test
./scripts/deploy.sh

# Test in AWS
./scripts/test.sh
```

### 2. **Commit & Push**
```bash
# Stage changes
git add .

# Commit with conventional format
git commit -m "feat: add new feature description"
# or
git commit -m "fix: resolve issue description"
# or  
git commit -m "docs: update documentation"

# Push to GitHub
git push origin feature/your-feature-name
```

### 3. **Merge to Main**
```bash
# Switch to main
git checkout main

# Merge feature
git merge feature/your-feature-name

# Push to main
git push origin main

# Deploy production
./scripts/deploy.sh
```

## 🔧 Common Tasks

### Update News Categories
Edit `template.yaml` parameter `NewsCategories` default value, then:
```bash
./scripts/deploy.sh
```

### Change Voice
Edit `template.yaml` parameter `VoiceId` default value, then:
```bash
./scripts/deploy.sh
```

### Debug Issues
```bash
# Check logs
./scripts/logs.sh

# Test function
./scripts/test.sh

# Check AWS resources
aws cloudformation describe-stacks --stack-name myownnews-mvp
```

### Clean Up Test Files
```bash
rm -f latest-*.txt latest-*.mp3 response.json generated-*.txt metadata.json news-brief.mp3
```

## 📦 Dependencies

- AWS CLI configured
- SAM CLI installed  
- Docker running (for containerized builds)
- jq installed (for JSON parsing in scripts)

## 🏷️ Commit Message Format

Use conventional commits:
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance tasks