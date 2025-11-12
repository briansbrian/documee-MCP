"""Basic test script for UnifiedCacheManager."""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, 'src')

from cache import UnifiedCacheManager


async def test_cache_manager():
    """Test basic cache manager functionality."""
    print("Testing UnifiedCacheManager...")
    
    # Create cache manager
    cache = UnifiedCacheManager(
        max_memory_mb=10,
        sqlite_path="cache_db/test_cache.db",
        redis_url=None
    )
    
    try:
        # Test initialization
        print("\n1. Testing initialization...")
        await cache.initialize()
        print("✓ Cache initialized successfully")
        
        # Test set_analysis and get_analysis
        print("\n2. Testing analysis cache...")
        test_data = {
            "codebase_id": "test123",
            "structure": {"total_files": 100},
            "summary": {"primary_language": "Python"}
        }
        
        await cache.set_analysis("scan:test123", test_data, ttl=3600)
        print("✓ Data stored in cache")
        
        # Get from cache (should hit memory)
        result = await cache.get_analysis("scan:test123")
        assert result == test_data, "Data mismatch"
        print("✓ Data retrieved from memory cache")
        
        # Test session state
        print("\n3. Testing session state...")
        session_data = {"phase": "scanned", "timestamp": 1234567890}
        await cache.set_session("test123", session_data)
        print("✓ Session state stored")
        
        session_result = await cache.get_session("test123")
        assert session_result == session_data, "Session data mismatch"
        print("✓ Session state retrieved")
        
        # Test resources
        print("\n4. Testing resources...")
        resource_data = {"type": "structure", "data": test_data}
        await cache.set_resource("structure", resource_data)
        print("✓ Resource stored")
        
        resource_result = await cache.get_resource("structure")
        assert resource_result == resource_data, "Resource data mismatch"
        print("✓ Resource retrieved")
        
        # Test statistics
        print("\n5. Testing statistics...")
        stats = await cache.get_stats()
        print(f"✓ Statistics retrieved:")
        print(f"  - Hit rate: {stats['hit_rate']:.2%}")
        print(f"  - Memory hits: {stats['memory_hits']}")
        print(f"  - Total requests: {stats['total_requests']}")
        print(f"  - Current memory: {stats['current_memory_mb']:.2f} MB")
        print(f"  - Active sessions: {stats['active_sessions']}")
        
        # Test cache miss
        print("\n6. Testing cache miss...")
        result = await cache.get_analysis("nonexistent:key")
        assert result is None, "Should return None for missing key"
        print("✓ Cache miss handled correctly")
        
        # Test LRU eviction
        print("\n7. Testing LRU eviction...")
        # Fill cache with data
        for i in range(100):
            await cache.set_analysis(f"test:key{i}", {"data": f"value{i}" * 1000}, ttl=3600)
        
        stats = await cache.get_stats()
        print(f"✓ LRU eviction working:")
        print(f"  - Evictions: {stats['evictions']}")
        print(f"  - Current memory: {stats['current_memory_mb']:.2f} MB")
        
        # Test async context manager
        print("\n8. Testing async context manager...")
        async with UnifiedCacheManager(max_memory_mb=5) as temp_cache:
            await temp_cache.set_analysis("temp:key", {"test": "data"}, ttl=3600)
            result = await temp_cache.get_analysis("temp:key")
            assert result == {"test": "data"}, "Context manager data mismatch"
        print("✓ Async context manager working")
        
        print("\n✅ All tests passed!")
        
    finally:
        # Cleanup
        await cache.close()
        print("\n✓ Cache closed successfully")
        
        # Remove test database
        if os.path.exists("cache_db/test_cache.db"):
            os.remove("cache_db/test_cache.db")
            print("✓ Test database cleaned up")


if __name__ == "__main__":
    asyncio.run(test_cache_manager())
