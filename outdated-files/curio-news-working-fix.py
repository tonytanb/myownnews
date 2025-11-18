# Quick fix for your curio-news-working Lambda
# Replace the lambda_handler function with this:

def lambda_handler(event, context):
    """Main lambda handler that routes requests"""
    logger.info(f"Lambda invoked with event: {json.dumps(event)}")
    
    # For API Gateway events, route based on path
    path = event.get('path', '')
    
    # Handle any path that contains 'latest' or is the main path
    if 'latest' in path or path in ['/', '/curio-news-working']:
        return list_latest(event, context)
    elif 'sign' in path:
        return sign_key(event, context)
    else:
        # Default to list_latest for any unrecognized path
        logger.info(f"Unknown path '{path}', defaulting to list_latest")
        return list_latest(event, context)