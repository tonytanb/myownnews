"""
Simple test for the cache service
"""

import json
import time
from cache_service import CacheService, get_cached, set_cached, cache_exists

def test_cache_service():
    """Test basic cache operations"""
    print("🧪 Testing Cache Service...")
    
    # Initialize cache service
    cache = CacheService()
    
    # Test data
    test_key = "test_content"
    test_data = {
        "title": "Test News",
        "content": "This is test content",
        "timestamp": time.time()
    }
    
    print(f"📝 Testing cache set operation...")
    success = cache.set(test_key, test_data, ttl_hours=1)
    print(f"Set result: {success}")
    
    print(f"📖 Testing cache get operation...")
    cached_content = cache.get(test_key)
    if cached_content:
        print(f"✅ Retrieved cached content: {json.dumps(cached_content['data'], indent=2)}")
    else:
        print("❌ Failed to retrieve cached content")
    
    print(f"🔍 Testing cache exists operation...")
    exists = cache.exists(test_key)
    print(f"Cache exists: {exists}")
    
    print(f"🗑️ Testing cache delete operation...")
    deleted = cache.delete(test_key)
    print(f"Delete result: {deleted}")
    
    print(f"🔍 Testing cache exists after delete...")
    exists_after_delete = cache.exists(test_key)
    print(f"Cache exists after delete: {exists_after_delete}")
    
    # Test convenience functions
    print(f"📝 Testing convenience functions...")
    convenience_success = set_cached("convenience_test", {"message": "Hello World"})
    convenience_content = get_cached("convenience_test")
    convenience_exists = cache_exists("convenience_test")
    
    print(f"Convenience set: {convenience_success}")
    print(f"Convenience get: {convenience_content is not None}")
    print(f"Convenience exists: {convenience_exists}")
    
    print("✅ Cache service test completed!")

if __name__ == "__main__":
    test_cache_service()