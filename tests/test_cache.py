"""
Unit tests for the UnifiedCacheManager.

Tests memory cache, SQLite cache, LRU eviction, cache promotion, and statistics.
"""

import os
import pytest
import pytest_asyncio
import tempfile
import time
from src.cache.unified_cache import UnifiedCacheManager


@pytest_asyncio.fixture
async def cache_manager():
    """Create a temporary cache manager for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_path = os.path.join(tmpdir, "test_cache.db")
        manager = UnifiedCacheManager(
            max_memory_mb=1,  # Small memory for testing eviction
            sqlite_path=cache_path,
            redis_url=None
        )
        await manager.initialize()
        yield manager
        await manager.close()


@pytest.mark.asyncio
async def test_cache_initialization():
    """Test cache manager initialization."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_path = os.path.join(tmpdir, "test_cache.db")
        manager = UnifiedCacheManager(
            max_memory_mb=10,
            sqlite_path=cache_path,
            redis_url=None
        )
        
        assert manager._initialized is False
        await manager.initialize()
        assert manager._initialized is True
        
        # Check SQLite connection
        assert manager.sqlite_conn is not None
        
        await manager.close()
        assert manager._initialized is False


@pytest.mark.asyncio
async def test_memory_cache_basic(cache_manager):
    """Test basic memory cache operations."""
    # Store data
    test_data = {"key": "value", "number": 42}
    await cache_manager.set_analysis("test_key", test_data, ttl=3600)
    
    # Retrieve data
    result = await cache_manager.get_analysis("test_key")
    assert result == test_data
    
    # Check statistics
    stats = await cache_manager.get_stats()
    assert stats["memory_hits"] == 1
    assert stats["total_requests"] == 1


@pytest.mark.asyncio
async def test_memory_cache_miss(cache_manager):
    """Test memory cache miss."""
    result = await cache_manager.get_analysis("nonexistent_key")
    assert result is None
    
    # Check statistics
    stats = await cache_manager.get_stats()
    assert stats["memory_misses"] == 1
    assert stats["sqlite_misses"] == 1


@pytest.mark.asyncio
async def test_sqlite_cache_persistence(cache_manager):
    """Test SQLite cache persistence."""
    # Store data
    test_data = {"key": "value", "persisted": True}
    await cache_manager.set_analysis("persist_key", test_data, ttl=3600)
    
    # Clear memory cache to force SQLite lookup
    cache_manager.memory_cache.clear()
    cache_manager.current_memory_size = 0
    
    # Retrieve from SQLite
    result = await cache_manager.get_analysis("persist_key")
    assert result == test_data
    
    # Check statistics
    stats = await cache_manager.get_stats()
    assert stats["sqlite_hits"] == 1


@pytest.mark.asyncio
async def test_lru_eviction(cache_manager):
    """Test LRU eviction when memory limit is exceeded."""
    # Fill cache with data that exceeds memory limit
    # Each entry is roughly 100 bytes, memory limit is 1MB
    large_data = {"data": "x" * 100000}  # ~100KB per entry
    
    # Add multiple entries
    for i in range(15):
        await cache_manager.set_analysis(f"key_{i}", large_data, ttl=3600)
    
    # Check that evictions occurred
    stats = await cache_manager.get_stats()
    assert stats["evictions"] > 0
    
    # Verify memory is within limit
    assert stats["current_memory_mb"] <= stats["max_memory_mb"]


@pytest.mark.asyncio
async def test_cache_promotion_from_sqlite(cache_manager):
    """Test cache promotion from SQLite to memory."""
    # Store data
    test_data = {"promoted": True}
    await cache_manager.set_analysis("promote_key", test_data, ttl=3600)
    
    # Clear memory cache
    cache_manager.memory_cache.clear()
    cache_manager.current_memory_size = 0
    
    # Retrieve from SQLite (should promote to memory)
    result = await cache_manager.get_analysis("promote_key")
    assert result == test_data
    
    # Verify it's now in memory
    assert "promote_key" in cache_manager.memory_cache
    
    # Next access should be from memory
    result2 = await cache_manager.get_analysis("promote_key")
    assert result2 == test_data
    
    stats = await cache_manager.get_stats()
    assert stats["memory_hits"] >= 1


@pytest.mark.asyncio
async def test_session_state_management(cache_manager):
    """Test session state storage and retrieval."""
    # Store session state
    session_data = {"phase": "scanned", "timestamp": time.time()}
    await cache_manager.set_session("codebase_123", session_data)
    
    # Retrieve session state
    result = await cache_manager.get_session("codebase_123")
    assert result == session_data
    assert result["phase"] == "scanned"


@pytest.mark.asyncio
async def test_session_state_persistence(cache_manager):
    """Test session state persistence in SQLite."""
    # Store session state
    session_data = {"phase": "analyzed", "files": 100}
    await cache_manager.set_session("codebase_456", session_data)
    
    # Clear memory
    cache_manager.session_state.clear()
    
    # Retrieve from SQLite
    result = await cache_manager.get_session("codebase_456")
    assert result == session_data


@pytest.mark.asyncio
async def test_resource_storage(cache_manager):
    """Test MCP resource storage and retrieval."""
    # Store resource
    resource_data = {"structure": {"files": 100}, "summary": {"language": "Python"}}
    await cache_manager.set_resource("structure", resource_data)
    
    # Retrieve resource
    result = await cache_manager.get_resource("structure")
    assert result == resource_data


@pytest.mark.asyncio
async def test_cache_statistics(cache_manager):
    """Test cache statistics tracking."""
    # Perform various operations
    await cache_manager.set_analysis("key1", {"data": 1}, ttl=3600)
    await cache_manager.get_analysis("key1")  # Hit
    await cache_manager.get_analysis("key2")  # Miss
    
    # Get statistics
    stats = await cache_manager.get_stats()
    
    # Verify statistics structure
    assert "hit_rate" in stats
    assert "memory_hits" in stats
    assert "memory_misses" in stats
    assert "sqlite_hits" in stats
    assert "sqlite_misses" in stats
    assert "redis_hits" in stats
    assert "redis_misses" in stats
    assert "evictions" in stats
    assert "total_requests" in stats
    assert "current_memory_mb" in stats
    assert "max_memory_mb" in stats
    assert "file_cache_entries" in stats
    assert "analysis_cache_entries" in stats
    assert "active_sessions" in stats
    
    # Verify hit rate calculation
    assert stats["total_requests"] > 0
    assert 0.0 <= stats["hit_rate"] <= 1.0


@pytest.mark.asyncio
async def test_cache_ttl_expiration():
    """Test cache TTL expiration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_path = os.path.join(tmpdir, "test_cache.db")
        manager = UnifiedCacheManager(
            max_memory_mb=10,
            sqlite_path=cache_path,
            redis_url=None
        )
        await manager.initialize()
        
        try:
            # Store data with short TTL
            test_data = {"expires": True}
            await manager.set_analysis("expire_key", test_data, ttl=1)
            
            # Clear memory to force SQLite lookup
            manager.memory_cache.clear()
            manager.current_memory_size = 0
            
            # Wait for expiration
            time.sleep(2)
            
            # Try to retrieve (should be expired)
            result = await manager.get_analysis("expire_key")
            assert result is None
            
        finally:
            await manager.close()


@pytest.mark.asyncio
async def test_context_manager_protocol():
    """Test async context manager protocol."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_path = os.path.join(tmpdir, "test_cache.db")
        
        async with UnifiedCacheManager(
            max_memory_mb=10,
            sqlite_path=cache_path,
            redis_url=None
        ) as manager:
            assert manager._initialized is True
            
            # Use the cache
            await manager.set_analysis("test", {"data": 1}, ttl=3600)
            result = await manager.get_analysis("test")
            assert result == {"data": 1}
        
        # After exiting context, should be closed
        assert manager._initialized is False


@pytest.mark.asyncio
async def test_multiple_cache_entries(cache_manager):
    """Test storing and retrieving multiple cache entries."""
    # Store multiple entries
    for i in range(10):
        await cache_manager.set_analysis(f"key_{i}", {"index": i}, ttl=3600)
    
    # Retrieve all entries
    for i in range(10):
        result = await cache_manager.get_analysis(f"key_{i}")
        assert result == {"index": i}
    
    # Check statistics
    stats = await cache_manager.get_stats()
    assert stats["memory_hits"] == 10


@pytest.mark.asyncio
async def test_cache_with_complex_data(cache_manager):
    """Test caching complex nested data structures."""
    complex_data = {
        "structure": {
            "total_files": 100,
            "languages": {"Python": 50, "JavaScript": 30},
            "nested": {
                "deep": {
                    "value": [1, 2, 3, 4, 5]
                }
            }
        },
        "summary": {
            "primary_language": "Python",
            "has_tests": True
        }
    }
    
    await cache_manager.set_analysis("complex_key", complex_data, ttl=3600)
    result = await cache_manager.get_analysis("complex_key")
    
    assert result == complex_data
    assert result["structure"]["languages"]["Python"] == 50
    assert result["structure"]["nested"]["deep"]["value"] == [1, 2, 3, 4, 5]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
