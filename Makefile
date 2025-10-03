# ===== MyOwnNews Dev Shortcuts =====
SHELL := /bin/bash

PROFILE ?= work-nvirginia
STACK   ?= myownnews-mvp
REGION  ?= us-east-1
VOICE   ?= Joanna

# CloudFormation Outputs (resolved dynamically)
FUNC_NAME  := $(shell aws cloudformation describe-stacks --profile $(PROFILE) --region $(REGION) --stack-name $(STACK) --query "Stacks[0].Outputs[?OutputKey=='FunctionName'].OutputValue" --output text 2>/dev/null)
BUCKET     := $(shell aws cloudformation describe-stacks --profile $(PROFILE) --region $(REGION) --stack-name $(STACK) --query "Stacks[0].Outputs[?OutputKey=='BucketName'].OutputValue" --output text 2>/dev/null)

.PHONY: help
help:
	@echo "Make targets:"
	@echo "  make login            # SSO login for $(PROFILE)"
	@echo "  make build            # SAM build (containerized)"
	@echo "  make deploy           # SAM deploy with VOICE=$(VOICE)"
	@echo "  make invoke           # Invoke Lambda, write response.json"
	@echo "  make urls             # Print presigned URLs for last run (script/audio)"
	@echo "  make logs             # Tail Lambda logs"
	@echo "  make setvoice VOICE=Kendra  # Re-deploy with a new voice"
	@echo "  make all              # build + deploy + invoke + urls"
	@echo "  make status           # Show resolved stack outputs"

.PHONY: login
login:
	aws sso login --profile $(PROFILE)
	@echo "Active profile: $(PROFILE)"
	aws sts get-caller-identity --profile $(PROFILE)

.PHONY: build
build:
	sam build --use-container

.PHONY: deploy
deploy:
	sam deploy --profile $(PROFILE) --region $(REGION) --parameter-overrides VoiceId=$(VOICE)

.PHONY: setvoice
setvoice: deploy

.PHONY: invoke
invoke:
	@if [ -z "$(FUNC_NAME)" ]; then echo "Function not found. Run: make status"; exit 1; fi
	aws lambda invoke \
	  --profile $(PROFILE) --region $(REGION) \
	  --function-name "$(FUNC_NAME)" \
	  response.json >/dev/null
	@cat response.json | jq .

.PHONY: urls
urls:
	@SCRIPT_KEY=$$(jq -r 'try (.body | fromjson | .script_key) // empty' response.json); \
	AUDIO_KEY=$$( jq -r 'try (.body | fromjson | .audio_key ) // empty' response.json); \
	if [ -z "$$SCRIPT_KEY" ] || [ -z "$$AUDIO_KEY" ]; then \
	  echo "No keys found in response.json — try \`make logs\`"; exit 1; \
	fi; \
	echo "Bucket: $(BUCKET)"; \
	echo "Script URL:"; aws s3 presign "s3://$(BUCKET)/$$SCRIPT_KEY" --expires-in 3600 --profile $(PROFILE) --region $(REGION); \
	echo "Audio URL:";  aws s3 presign "s3://$(BUCKET)/$$AUDIO_KEY"  --expires-in 3600 --profile $(PROFILE) --region $(REGION);

.PHONY: logs
logs:
	@if [ -z "$(FUNC_NAME)" ]; then echo "Function not found. Run: make status"; exit 1; fi
	aws logs tail "/aws/lambda/$(FUNC_NAME)" --follow --profile $(PROFILE) --region $(REGION)

.PHONY: all
all: build deploy invoke urls

.PHONY: status
status:
	@echo "Profile: $(PROFILE)  Region: $(REGION)  Stack: $(STACK)"
	@echo "Function: $(FUNC_NAME)"
	@echo "Bucket:   $(BUCKET)"
