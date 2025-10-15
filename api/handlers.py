import json
import boto3
import os
from datetime import datetime
from botocore.exceptions import ClientError

s3 = boto3.client('s3')
BUCKET = os.getenv('BUCKET')
CORS_ALLOW_ORIGIN = os.getenv('CORS_ALLOW_ORIGIN', '*')
PRESIGN_EXPIRES = int(os.getenv('PRESIGN_EXPIRES', '1200'))

def cors_headers():
    return {
        'Access-Control-Allow-Origin': CORS_ALLOW_ORIGIN,
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Access-Control-Max-Age': '86400'
    }

def list_latest(event, context):
    """Get the most recent audio/script files with presigned URLs"""
    try:
        # Get today's date for folder structure
        today = datetime.utcnow().strftime("%Y-%m-%d")
        
        # List objects in runs folder for today
        runs_prefix = f"runs/{today}/"
        
        try:
            response = s3.list_objects_v2(
                Bucket=BUCKET,
                Prefix=runs_prefix,
                MaxKeys=50
            )
        except ClientError as e:
            print(f"Error listing objects: {e}")
            # Fallback to list all runs if today's folder doesn't exist
            response = s3.list_objects_v2(
                Bucket=BUCKET,
                Prefix="runs/",
                MaxKeys=50
            )
        
        if 'Contents' not in response:
            return {
                'statusCode': 404,
                'headers': cors_headers(),
                'body': json.dumps({'error': 'No content found'})
            }
        
        # Sort by last modified, get the most recent
        objects = sorted(response['Contents'], key=lambda x: x['LastModified'], reverse=True)
        
        if not objects:
            return {
                'statusCode': 404,
                'headers': cors_headers(),
                'body': json.dumps({'error': 'No runs found'})
            }
        
        # Get the most recent run metadata
        latest_run_key = objects[0]['Key']
        
        try:
            # Download the metadata file
            meta_response = s3.get_object(Bucket=BUCKET, Key=latest_run_key)
            meta_data = json.loads(meta_response['Body'].read().decode('utf-8'))
            
            # Generate presigned URLs for audio and script
            audio_key = meta_data.get('audio_key')
            script_key = meta_data.get('script_key')
            
            presigned_urls = {}
            
            if audio_key:
                try:
                    presigned_urls['audio_url'] = s3.generate_presigned_url(
                        'get_object',
                        Params={'Bucket': BUCKET, 'Key': audio_key},
                        ExpiresIn=PRESIGN_EXPIRES
                    )
                except ClientError as e:
                    print(f"Error generating presigned URL for audio: {e}")
            
            if script_key:
                try:
                    # Get the script content
                    script_response = s3.get_object(Bucket=BUCKET, Key=script_key)
                    script_content = script_response['Body'].read().decode('utf-8')
                    meta_data['script'] = script_content
                except ClientError as e:
                    print(f"Error getting script content: {e}")
            
            # Merge presigned URLs into metadata
            result = {**meta_data, **presigned_urls}
            
            # Add some mock news items if not present
            if 'news_items' not in result:
                result['news_items'] = [
                    {
                        "title": "Breaking: Latest News Update",
                        "category": "GENERAL",
                        "summary": "Stay informed with the latest developments from around the world.",
                        "full_text": "This is a comprehensive update on the latest news developments. Our AI-powered system has curated the most important stories for your daily briefing.",
                        "image": "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=400"
                    }
                ]
            
            # Add word timings if not present (estimated)
            if 'word_timings' not in result and 'script' in result:
                words = result['script'].split()
                result['word_timings'] = [
                    {
                        'word': word,
                        'start': i * 0.4,
                        'end': (i + 1) * 0.4
                    }
                    for i, word in enumerate(words)
                ]
            
            return {
                'statusCode': 200,
                'headers': cors_headers(),
                'body': json.dumps(result)
            }
            
        except ClientError as e:
            print(f"Error getting metadata: {e}")
            return {
                'statusCode': 500,
                'headers': cors_headers(),
                'body': json.dumps({'error': 'Failed to get metadata'})
            }
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {
            'statusCode': 500,
            'headers': cors_headers(),
            'body': json.dumps({'error': str(e)})
        }

def sign_key(event, context):
    """Generate a presigned URL for a specific S3 key"""
    try:
        # Get the key from query parameters
        key = event.get('queryStringParameters', {}).get('key')
        
        if not key:
            return {
                'statusCode': 400,
                'headers': cors_headers(),
                'body': json.dumps({'error': 'Missing key parameter'})
            }
        
        # Generate presigned URL
        try:
            presigned_url = s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': BUCKET, 'Key': key},
                ExpiresIn=PRESIGN_EXPIRES
            )
            
            return {
                'statusCode': 200,
                'headers': cors_headers(),
                'body': json.dumps({
                    'presigned_url': presigned_url,
                    'expires_in': PRESIGN_EXPIRES
                })
            }
            
        except ClientError as e:
            print(f"Error generating presigned URL: {e}")
            return {
                'statusCode': 404,
                'headers': cors_headers(),
                'body': json.dumps({'error': 'Object not found or access denied'})
            }
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {
            'statusCode': 500,
            'headers': cors_headers(),
            'body': json.dumps({'error': str(e)})
        }