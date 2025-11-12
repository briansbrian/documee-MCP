"""Tests for the discover_features tool."""

import os
import pytest
import pytest_asyncio
import tempfile
import shutil
from src.tools.discover_features import discover_features
from src.tools.scan_codebase import scan_codebase
from src.cache.unified_cache import UnifiedCacheManager


@pytest_asyncio.fixture
async def cache_manager():
    """Create a temporary cache manager for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_path = os.path.join(temp_dir, "test_cache.db")
        manager = UnifiedCacheManager(
            max_memory_mb=10,
            sqlite_path=cache_path,
            redis_url=None
        )
        await manager.initialize()
        yield manager
        await manager.close()


@pytest.fixture
def test_codebase():
    """Create a temporary test codebase with feature directories."""
    temp_dir = tempfile.mkdtemp()
    
    # Create feature directories
    os.makedirs(os.path.join(temp_dir, "src", "routes"))
    os.makedirs(os.path.join(temp_dir, "src", "components"))
    os.makedirs(os.path.join(temp_dir, "src", "api"))
    os.makedirs(os.path.join(temp_dir, "src", "utils"))
    os.makedirs(os.path.join(temp_dir, "src", "hooks"))
    
    # Create some files to make it a valid codebase
    with open(os.path.join(temp_dir, "src", "routes", "index.js"), "w") as f:
        f.write("// routes file")
    with open(os.path.join(temp_dir, "src", "components", "Button.jsx"), "w") as f:
        f.write("// component file")
    with open(os.path.join(temp_dir, "src", "api", "users.js"), "w") as f:
        f.write("// api file")
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.mark.asyncio
async def test_discover_features_basic(test_codebase, cache_manager):
    """Test basic feature discovery."""
    # First scan the codebase
    scan_result = await scan_codebase(
        path=test_codebase,
        max_depth=10,
        use_cache=False,
        cache_manager=cache_manager
    )
    
    codebase_id = scan_result["codebase_id"]
    
    # Discover features
    result = await discover_features(
        codebase_id=codebase_id,
        categories=None,
        use_cache=False,
        cache_manager=cache_manager
    )
    
    # Verify result structure
    assert "features" in result
    assert "total_features" in result
    assert "categories" in result
    assert "from_cache" in result
    
    # Should find at least some features
    assert result["total_features"] > 0
    assert len(result["features"]) > 0
    
    # Check feature structure
    feature = result["features"][0]
    assert "id" in feature
    assert "name" in feature
    assert "category" in feature
    assert "path" in feature
    assert "priority" in feature
    
    # Verify feature ID is 16 characters
    assert len(feature["id"]) == 16


@pytest.mark.asyncio
async def test_discover_features_with_categories(test_codebase, cache_manager):
    """Test feature discovery with category filtering."""
    # First scan the codebase
    scan_result = await scan_codebase(
        path=test_codebase,
        max_depth=10,
        use_cache=False,
        cache_manager=cache_manager
    )
    
    codebase_id = scan_result["codebase_id"]
    
    # Discover only routes and api features
    result = await discover_features(
        codebase_id=codebase_id,
        categories=["routes", "api"],
        use_cache=False,
        cache_manager=cache_manager
    )
    
    # Verify only routes and api categories are returned
    for feature in result["features"]:
        assert feature["category"] in ["routes", "api"]
    
    # Verify categories list
    assert all(cat in ["routes", "api"] for cat in result["categories"])


@pytest.mark.asyncio
async def test_discover_features_with_cache(test_codebase, cache_manager):
    """Test that feature discovery uses cache correctly."""
    # First scan the codebase
    scan_result = await scan_codebase(
        path=test_codebase,
        max_depth=10,
        use_cache=False,
        cache_manager=cache_manager
    )
    
    codebase_id = scan_result["codebase_id"]
    
    # First discovery (not cached)
    result1 = await discover_features(
        codebase_id=codebase_id,
        categories=None,
        use_cache=True,
        cache_manager=cache_manager
    )
    
    assert result1["from_cache"] is False
    
    # Second discovery (should be cached)
    result2 = await discover_features(
        codebase_id=codebase_id,
        categories=None,
        use_cache=True,
        cache_manager=cache_manager
    )
    
    assert result2["from_cache"] is True
    assert result2["total_features"] == result1["total_features"]


@pytest.mark.asyncio
async def test_discover_features_without_scan(cache_manager):
    """Test that discovery fails if codebase hasn't been scanned."""
    with pytest.raises(ValueError, match="Codebase not scanned"):
        await discover_features(
            codebase_id="nonexistent_id",
            categories=None,
            use_cache=False,
            cache_manager=cache_manager
        )


@pytest.mark.asyncio
async def test_discover_features_priority_assignment(test_codebase, cache_manager):
    """Test that priorities are assigned correctly."""
    # First scan the codebase
    scan_result = await scan_codebase(
        path=test_codebase,
        max_depth=10,
        use_cache=False,
        cache_manager=cache_manager
    )
    
    codebase_id = scan_result["codebase_id"]
    
    # Discover features
    result = await discover_features(
        codebase_id=codebase_id,
        categories=None,
        use_cache=False,
        cache_manager=cache_manager
    )
    
    # Check priorities
    for feature in result["features"]:
        if feature["category"] in ["routes", "api"]:
            assert feature["priority"] == "high"
        else:
            assert feature["priority"] == "medium"
