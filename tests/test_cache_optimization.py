"""
Cache optimization validation tests for Analysis Engine.

Tests validate that the 3-tier caching strategy works correctly:
- Verify 3-tier cache working (memory, SQLite, Redis)
- Verify cache promotion on hits
- Verify TTL expiration
- Target >80% cache hit rate
"""

import asyncio
import os
import tempfile
import time

import pytest
import pytest_asyncio

from src.cache.unified_cache import UnifiedCacheManager


@pytest_asyncio.fixture
async def cache_manager():
    """Create a cache manager for testing."""
    temp_db = tempfile.mktemp(suffix='.db')
    cache = UnifiedCacheManager(
        max_memory_mb=10,  # Small memory cache for testing eviction
        sqlite_path=temp_db,
        redis_url=None  # No Redis for basic tests
    )
    await cache.initialize()
    yield cache
    await cache.close()
    if os.path.exists(temp_db):
        os.remove(temp_db)


@pytest.mark.asyncio
async def test_memory_cache_tier(cache_manager):
    """
    Test: Memory cache (Tier 1) should work correctly.
    
    Requirement: 8.1 - Cache AST with key "ast:{file_hash}"
    """
    # Store data in cache
    test_data = {"file_path": "test.py", "content": "print('hello')"}
    await cache_manager.set_analysis("test_key_1", test_data, ttl=3600)
    
    # Retrieve from cache (should be in memory)
    result = await cache_manager.get_analysis("test_key_1")
    
    # Validate
    assert result is not None
    assert result["file_path"] == "test.py"
    assert result["content"] == "print('hello')"
    
    # Check stats
    stats = await cache_manager.get_stats()
    assert stats["memory_hits"] >= 1
    print(f"\nMemory cache stats: {stats['memory_hits']} hits, {stats['memory_misses']} misses")


@pytest.mark.asyncio
async def test_sqlite_cache_tier(cache_manager):
    """
    Test: SQLite cache (Tier 2) should work correctly.
    
    Requirement: 8.2 - Cache symbols with key "symbols:{file_hash}"
    """
    # Store data in cache
    test_data = {"symbols": ["func1", "func2"], "classes": ["Class1"]}
    await cache_manager.set_analysis("test_key_2", test_data, ttl=3600)
    
    # Clear memory cache to force SQLite lookup
    cache_manager.memory_cache.clear()
    cache_manager.current_memory_size = 0
    
    # Retrieve from cache (should come from SQLite)
    result = await cache_manager.get_analysis("test_key_2")
    
    # Validate
    assert result is not None
    assert result["symbols"] == ["func1", "func2"]
    assert result["classes"] == ["Class1"]
    
    # Check stats
    stats = await cache_manager.get_stats()
    assert stats["sqlite_hits"] >= 1
    print(f"\nSQLite cache stats: {stats['sqlite_hits']} hits, {stats['sqlite_misses']} misses")


@pytest.mark.asyncio
async def test_cache_promotion(cache_manager):
    """
    Test: Cache promotion should move data from SQLite to memory on hit.
    
    Requirement: 8.2 - Verify cache promotion on hits
    """
    # Store data in cache
    test_data = {"teaching_value": 0.85, "complexity": 5}
    await cache_manager.set_analysis("test_key_3", test_data, ttl=3600)
    
    # Clear memory cache
    cache_manager.memory_cache.clear()
    cache_manager.current_memory_size = 0
    
    # First retrieval (from SQLite)
    result1 = await cache_manager.get_analysis("test_key_3")
    assert result1 is not None
    
    # Check that it's now in memory cache
    assert "test_key_3" in cache_manager.memory_cache
    
    # Second retrieval (from memory)
    result2 = await cache_manager.get_analysis("test_key_3")
    assert result2 is not None
    assert result2 == result1
    
    # Check stats - should have memory hit on second retrieval
    stats = await cache_manager.get_stats()
    assert stats["memory_hits"] >= 1
    print(f"\nCache promotion verified: memory hits = {stats['memory_hits']}")


@pytest.mark.asyncio
async def test_lru_eviction(cache_manager):
    """
    Test: LRU eviction should work when memory cache is full.
    
    Requirement: 8.4 - Cache should handle memory limits
    """
    # Fill memory cache with data
    for i in range(20):
        large_data = {"data": "x" * 100000, "index": i}  # ~100KB each
        await cache_manager.set_analysis(f"large_key_{i}", large_data, ttl=3600)
    
    # Check that evictions occurred
    stats = await cache_manager.get_stats()
    assert stats["evictions"] > 0
    print(f"\nLRU evictions: {stats['evictions']}")
    
    # Verify memory size is within limits
    assert cache_manager.current_memory_size <= cache_manager.max_memory_bytes


@pytest.mark.asyncio
async def test_ttl_expiration(cache_manager):
    """
    Test: TTL expiration should work correctly.
    
    Requirement: 8.3 - Verify TTL expiration
    """
    # Store data with short TTL
    test_data = {"expires": "soon"}
    await cache_manager.set_analysis("test_key_ttl", test_data, ttl=1)  # 1 second TTL
    
    # Immediate retrieval should work
    result1 = await cache_manager.get_analysis("test_key_ttl")
    assert result1 is not None
    
    # Wait for TTL to expire
    await asyncio.sleep(2)
    
    # Clear memory cache to force SQLite lookup (where TTL is checked)
    cache_manager.memory_cache.clear()
    cache_manager.current_memory_size = 0
    
    # Retrieval after expiration should return None
    result2 = await cache_manager.get_analysis("test_key_ttl")
    assert result2 is None
    print("\nTTL expiration verified")


@pytest.mark.asyncio
async def test_cache_hit_rate_target(cache_manager):
    """
    Test: Cache hit rate should exceed 80% for repeated access patterns.
    
    Requirement: 8.5 - Target >80% cache hit rate
    """
    # Store 10 items
    for i in range(10):
        data = {"item": i, "value": f"data_{i}"}
        await cache_manager.set_analysis(f"item_{i}", data, ttl=3600)
    
    # Access items multiple times (simulating repeated analysis)
    for _ in range(5):  # 5 rounds of access
        for i in range(10):
            result = await cache_manager.get_analysis(f"item_{i}")
            assert result is not None
    
    # Calculate hit rate
    stats = await cache_manager.get_stats()
    hit_rate = stats["hit_rate"]
    
    print(f"\nCache hit rate: {hit_rate:.2%}")
    print(f"Memory hits: {stats['memory_hits']}")
    print(f"SQLite hits: {stats['sqlite_hits']}")
    print(f"Total requests: {stats['total_requests']}")
    
    # Verify hit rate exceeds 80%
    assert hit_rate > 0.8, f"Cache hit rate {hit_rate:.2%} is below 80% target"


@pytest.mark.asyncio
async def test_cache_statistics_tracking(cache_manager):
    """
    Test: Cache statistics should be tracked accurately.
    
    Requirement: 10.5 - Log cache hit/miss statistics
    """
    # Perform various cache operations
    await cache_manager.set_analysis("stat_key_1", {"data": "test1"}, ttl=3600)
    await cache_manager.set_analysis("stat_key_2", {"data": "test2"}, ttl=3600)
    
    # Cache hits
    await cache_manager.get_analysis("stat_key_1")
    await cache_manager.get_analysis("stat_key_2")
    
    # Cache miss
    await cache_manager.get_analysis("nonexistent_key")
    
    # Get stats
    stats = await cache_manager.get_stats()
    
    # Validate stats structure
    assert "hit_rate" in stats
    assert "memory_hits" in stats
    assert "memory_misses" in stats
    assert "sqlite_hits" in stats
    assert "sqlite_misses" in stats
    assert "evictions" in stats
    assert "total_requests" in stats
    assert "current_memory_mb" in stats
    assert "max_memory_mb" in stats
    
    # Validate stats values
    assert stats["total_requests"] > 0
    assert stats["memory_hits"] + stats["memory_misses"] > 0
    
    print(f"\nCache statistics:")
    print(f"  Hit rate: {stats['hit_rate']:.2%}")
    print(f"  Memory: {stats['memory_hits']} hits, {stats['memory_misses']} misses")
    print(f"  SQLite: {stats['sqlite_hits']} hits, {stats['sqlite_misses']} misses")
    print(f"  Evictions: {stats['evictions']}")
    print(f"  Memory usage: {stats['current_memory_mb']:.2f}MB / {stats['max_memory_mb']:.2f}MB")


@pytest.mark.asyncio
async def test_concurrent_cache_access(cache_manager):
    """
    Test: Cache should handle concurrent access correctly.
    
    Requirement: 10.4 - Parallel processing with caching
    """
    # Store initial data
    for i in range(20):
        data = {"concurrent": i}
        await cache_manager.set_analysis(f"concurrent_{i}", data, ttl=3600)
    
    # Concurrent reads
    async def read_item(key):
        return await cache_manager.get_analysis(key)
    
    # Create 50 concurrent read tasks
    tasks = [read_item(f"concurrent_{i % 20}") for i in range(50)]
    results = await asyncio.gather(*tasks)
    
    # Validate all reads succeeded
    assert all(r is not None for r in results)
    assert len(results) == 50
    
    # Check stats
    stats = await cache_manager.get_stats()
    print(f"\nConcurrent access: {stats['total_requests']} requests, hit rate: {stats['hit_rate']:.2%}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
