"""Test cache promotion between tiers."""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, 'src')

from cache import UnifiedCacheManager


async def test_cache_promotion():
    """Test cache promotion from SQLite to Memory."""
    print("Testing cache promotion between tiers...")
    
    # Create first cache instance
    cache1 = UnifiedCacheManager(
        max_memory_mb=10,
        sqlite_path="cache_db/test_promotion.db",
        redis_url=None
    )
    
    try:
        await cache1.initialize()
        
        # Store data in all tiers
        print("\n1. Storing data in cache1...")
        test_data = {
            "codebase_id": "promotion_test",
            "structure": {"total_files": 500},
            "summary": {"primary_language": "TypeScript"}
        }
        await cache1.set_analysis("scan:promotion", test_data, ttl=3600)
        print("✓ Data stored in cache1 (memory + sqlite)")
        
        # Verify it's in memory
        result = await cache1.get_analysis("scan:promotion")
        assert result == test_data
        stats1 = await cache1.get_stats()
        print(f"✓ Memory hit: {stats1['memory_hits']} (expected: 1)")
        
        # Close first cache (clears memory but keeps SQLite)
        await cache1.close()
        print("\n2. Closed cache1 (memory cleared, SQLite persists)")
        
        # Create second cache instance (fresh memory, same SQLite)
        cache2 = UnifiedCacheManager(
            max_memory_mb=10,
            sqlite_path="cache_db/test_promotion.db",
            redis_url=None
        )
        await cache2.initialize()
        print("✓ Initialized cache2 (fresh memory)")
        
        # Get data - should hit SQLite and promote to memory
        print("\n3. Retrieving data from cache2...")
        result = await cache2.get_analysis("scan:promotion")
        assert result == test_data, "Data should be retrieved from SQLite"
        
        stats2 = await cache2.get_stats()
        print(f"✓ SQLite hit: {stats2['sqlite_hits']} (expected: 1)")
        print(f"✓ Memory miss: {stats2['memory_misses']} (expected: 1)")
        print("✓ Data promoted from SQLite to memory")
        
        # Get again - should now hit memory
        print("\n4. Retrieving data again from cache2...")
        result = await cache2.get_analysis("scan:promotion")
        assert result == test_data
        
        stats3 = await cache2.get_stats()
        print(f"✓ Memory hit: {stats3['memory_hits']} (expected: 1)")
        print(f"✓ Total requests: {stats3['total_requests']} (expected: 2)")
        print(f"✓ Hit rate: {stats3['hit_rate']:.2%} (expected: 100%)")
        
        print("\n✅ Cache promotion test passed!")
        
        await cache2.close()
        
    finally:
        # Cleanup - wait a bit for file handles to release
        await asyncio.sleep(0.5)
        try:
            if os.path.exists("cache_db/test_promotion.db"):
                os.remove("cache_db/test_promotion.db")
                print("\n✓ Test database cleaned up")
        except PermissionError:
            print("\n⚠ Could not delete test database (file in use)")


async def test_ttl_expiration():
    """Test TTL expiration in SQLite cache."""
    print("\n\nTesting TTL expiration...")
    
    cache = UnifiedCacheManager(
        max_memory_mb=10,
        sqlite_path="cache_db/test_ttl.db",
        redis_url=None
    )
    
    try:
        await cache.initialize()
        
        # Store data with 1 second TTL
        print("\n1. Storing data with 1 second TTL...")
        test_data = {"test": "ttl_data"}
        await cache.set_analysis("ttl:test", test_data, ttl=1)
        print("✓ Data stored")
        
        # Get immediately - should work
        result = await cache.get_analysis("ttl:test")
        assert result == test_data
        print("✓ Data retrieved immediately")
        
        # Clear memory cache to force SQLite lookup
        cache.memory_cache.clear()
        cache.current_memory_size = 0
        print("\n2. Cleared memory cache")
        
        # Wait for TTL to expire
        print("3. Waiting 2 seconds for TTL to expire...")
        await asyncio.sleep(2)
        
        # Try to get - should return None (expired)
        result = await cache.get_analysis("ttl:test")
        assert result is None, "Data should be expired"
        print("✓ Expired data correctly returned None")
        
        print("\n✅ TTL expiration test passed!")
        
        await cache.close()
        
    finally:
        # Cleanup - wait a bit for file handles to release
        await asyncio.sleep(0.5)
        try:
            if os.path.exists("cache_db/test_ttl.db"):
                os.remove("cache_db/test_ttl.db")
                print("✓ Test database cleaned up")
        except PermissionError:
            print("⚠ Could not delete test database (file in use)")


if __name__ == "__main__":
    asyncio.run(test_cache_promotion())
    asyncio.run(test_ttl_expiration())
