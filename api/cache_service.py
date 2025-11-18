"""
Minimal Cache Service for Curio News

Simple DynamoDB-based caching with TTL expiration.
Provides basic get/set operations without complex cache management.
"""

import boto3
import json
import time
from typing import Optional, Dict, Any
import os

# Initialize DynamoDB client
dynamodb = boto3.client('dynamodb')

class CacheService:
    """Simple cache service using DynamoDB with TTL-based expiration"""
    
    def __init__(self, table_name: str = None):
        self.table_name = table_name or os.environ.get('CURIO_TABLE', 'CurioTable')
        self.default_ttl_hours = 24  # Default 24 hour TTL
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get cached content by key
        
        Args:
            key: Cache key to retrieve
            
        Returns:
            Cached content if found and not expired, None otherwise
        """
        try:
            response = dynamodb.get_item(
                TableName=self.table_name,
                Key={
                    'pk': {'S': f'cache#{key}'},
                    'sk': {'S': 'content'}
                }
            )
            
            if 'Item' not in response:
                return None
            
            item = response['Item']
            
            # Check if item has expired (DynamoDB TTL might not have cleaned it up yet)
            expires_at = int(item.get('expiresAt', {}).get('N', '0'))
            if expires_at > 0 and time.time() > expires_at:
                return None
            
            # Parse and return the cached content
            content = {
                'data': json.loads(item.get('data', {}).get('S', '{}')),
                'cached_at': item.get('cachedAt', {}).get('S', ''),
                'expires_at': expires_at
            }
            
            return content
            
        except Exception as e:
            print(f"❌ Error getting cached content for key '{key}': {e}")
            return None
    
    def set(self, key: str, data: Dict[str, Any], ttl_hours: int = None) -> bool:
        """
        Set cached content with TTL expiration
        
        Args:
            key: Cache key to store under
            data: Data to cache
            ttl_hours: Time to live in hours (defaults to 24)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            ttl_hours = ttl_hours or self.default_ttl_hours
            expires_at = int(time.time()) + (ttl_hours * 3600)  # Convert hours to seconds
            cached_at = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            
            item = {
                'pk': {'S': f'cache#{key}'},
                'sk': {'S': 'content'},
                'data': {'S': json.dumps(data, default=str)},
                'cachedAt': {'S': cached_at},
                'expiresAt': {'N': str(expires_at)}
            }
            
            dynamodb.put_item(
                TableName=self.table_name,
                Item=item
            )
            
            print(f"✅ Cached content for key '{key}' (expires in {ttl_hours} hours)")
            return True
            
        except Exception as e:
            print(f"❌ Error caching content for key '{key}': {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete cached content by key
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            dynamodb.delete_item(
                TableName=self.table_name,
                Key={
                    'pk': {'S': f'cache#{key}'},
                    'sk': {'S': 'content'}
                }
            )
            
            print(f"✅ Deleted cached content for key '{key}'")
            return True
            
        except Exception as e:
            print(f"❌ Error deleting cached content for key '{key}': {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """
        Check if a cache key exists and is not expired
        
        Args:
            key: Cache key to check
            
        Returns:
            True if key exists and is not expired, False otherwise
        """
        return self.get(key) is not None
    
    def clear_expired(self) -> int:
        """
        Manually clear expired cache entries (DynamoDB TTL handles this automatically)
        This is mainly for testing or manual cleanup
        
        Returns:
            Number of items cleared
        """
        try:
            current_time = int(time.time())
            cleared_count = 0
            
            # Scan for cache entries
            response = dynamodb.scan(
                TableName=self.table_name,
                FilterExpression='begins_with(pk, :cache_prefix)',
                ExpressionAttributeValues={
                    ':cache_prefix': {'S': 'cache#'}
                }
            )
            
            for item in response.get('Items', []):
                expires_at = int(item.get('expiresAt', {}).get('N', '0'))
                if expires_at > 0 and current_time > expires_at:
                    # Delete expired item
                    dynamodb.delete_item(
                        TableName=self.table_name,
                        Key={
                            'pk': item['pk'],
                            'sk': item['sk']
                        }
                    )
                    cleared_count += 1
            
            if cleared_count > 0:
                print(f"✅ Cleared {cleared_count} expired cache entries")
            
            return cleared_count
            
        except Exception as e:
            print(f"❌ Error clearing expired cache entries: {e}")
            return 0


# Global cache instance for easy import
cache = CacheService()

# Convenience functions for direct use
def get_cached(key: str) -> Optional[Dict[str, Any]]:
    """Get cached content by key"""
    return cache.get(key)

def set_cached(key: str, data: Dict[str, Any], ttl_hours: int = 24) -> bool:
    """Set cached content with TTL"""
    return cache.set(key, data, ttl_hours)

def delete_cached(key: str) -> bool:
    """Delete cached content by key"""
    return cache.delete(key)

def cache_exists(key: str) -> bool:
    """Check if cache key exists"""
    return cache.exists(key)