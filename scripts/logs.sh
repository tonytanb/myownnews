#!/bin/bash
# View recent CloudWatch logs for debugging

FUNCTION_NAME=$(aws cloudformation describe-stacks --stack-name myownnews-mvp --query 'Stacks[0].Outputs[?OutputKey==`FunctionName`].OutputValue' --output text)
LOG_GROUP="/aws/lambda/$FUNCTION_NAME"

echo "📋 Recent logs for: $FUNCTION_NAME"
echo "Log group: $LOG_GROUP"
echo "----------------------------------------"

# Get the latest log stream
LATEST_STREAM=$(aws logs describe-log-streams --log-group-name "$LOG_GROUP" --order-by LastEventTime --descending --max-items 1 --query 'logStreams[0].logStreamName' --output text)

if [ "$LATEST_STREAM" != "None" ]; then
    echo "Latest stream: $LATEST_STREAM"
    echo "----------------------------------------"
    aws logs get-log-events --log-group-name "$LOG_GROUP" --log-stream-name "$LATEST_STREAM" --query 'events[].message' --output text
else
    echo "No log streams found. Function may not have been invoked yet."
fi