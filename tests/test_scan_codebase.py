"""
Unit tests for the codebase scanner tool.
"""

import os
import pytest
import pytest_asyncio
import tempfile
import shutil
from pathlib import Path

from src.tools.scan_codebase import scan_codebase, LANGUAGE_EXTENSIONS, IGNORE_PATTERNS
from src.cache.unified_cache import UnifiedCacheManager


@pytest_asyncio.fixture
async def cache_manager():
    """Create a temporary cache manager for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_path = os.path.join(tmpdir, "test_cache.db")
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
    """Create a temporary test codebase."""
    tmpdir = tempfile.mkdtemp()
    
    # Create directory structure
    os.makedirs(os.path.join(tmpdir, "src"))
    os.makedirs(os.path.join(tmpdir, "tests"))
    os.makedirs(os.path.join(tmpdir, "node_modules"))  # Should be ignored
    
    # Create some files
    Path(os.path.join(tmpdir, "src", "main.py")).write_text("print('hello')")
    Path(os.path.join(tmpdir, "src", "utils.js")).write_text("console.log('test')")
    Path(os.path.join(tmpdir, "tests", "test_main.py")).write_text("def test(): pass")
    Path(os.path.join(tmpdir, "README.md")).write_text("# Test Project")
    Path(os.path.join(tmpdir, "node_modules", "package.js")).write_text("// ignored")
    
    yield tmpdir
    
    # Cleanup
    shutil.rmtree(tmpdir, ignore_errors=True)


@pytest.mark.asyncio
async def test_scan_basic_structure(test_codebase, cache_manager):
    """Test basic directory scanning."""
    result = await scan_codebase(
        path=test_codebase,
        max_depth=10,
        use_cache=False,
        cache_manager=cache_manager
    )
    
    assert "codebase_id" in result
    assert len(result["codebase_id"]) == 16
    assert "structure" in result
    assert "summary" in result
    assert "scan_time_ms" in result
    assert result["from_cache"] is False
    
    structure = result["structure"]
    assert structure["total_files"] == 4  # Should not count node_modules
    assert structure["total_directories"] >= 2  # src and tests
    assert "Python" in structure["languages"]
    assert "JavaScript" in structure["languages"]


@pytest.mark.asyncio
async def test_scan_with_cache(test_codebase, cache_manager):
    """Test caching functionality."""
    # First scan
    result1 = await scan_codebase(
        path=test_codebase,
        use_cache=True,
        cache_manager=cache_manager
    )
    assert result1["from_cache"] is False
    
    # Second scan (should be cached)
    result2 = await scan_codebase(
        path=test_codebase,
        use_cache=True,
        cache_manager=cache_manager
    )
    assert result2["from_cache"] is True
    assert result2["codebase_id"] == result1["codebase_id"]
    # Verify structure is the same
    assert result2["structure"]["total_files"] == result1["structure"]["total_files"]


@pytest.mark.asyncio
async def test_scan_invalid_path(cache_manager):
    """Test error handling for invalid paths."""
    with pytest.raises(ValueError, match="Path does not exist"):
        await scan_codebase(
            path="/nonexistent/path/12345",
            cache_manager=cache_manager
        )


@pytest.mark.asyncio
async def test_scan_summary_generation(test_codebase, cache_manager):
    """Test summary generation."""
    result = await scan_codebase(
        path=test_codebase,
        cache_manager=cache_manager
    )
    
    summary = result["summary"]
    assert "primary_language" in summary
    assert summary["primary_language"] in ["Python", "JavaScript"]
    assert "project_type" in summary
    assert "has_tests" in summary
    assert "size_category" in summary
    assert summary["size_category"] == "small"  # Less than 100 files


@pytest.mark.asyncio
async def test_scan_ignores_patterns(test_codebase, cache_manager):
    """Test that ignored directories are skipped."""
    result = await scan_codebase(
        path=test_codebase,
        cache_manager=cache_manager
    )
    
    # node_modules should be ignored, so we shouldn't count its files
    structure = result["structure"]
    # We created 5 files total, but 1 is in node_modules
    assert structure["total_files"] == 4


@pytest.mark.asyncio
async def test_scan_max_depth(test_codebase, cache_manager):
    """Test max_depth parameter."""
    # Create a deep directory structure
    deep_path = test_codebase
    for i in range(15):
        deep_path = os.path.join(deep_path, f"level{i}")
        os.makedirs(deep_path, exist_ok=True)
        Path(os.path.join(deep_path, f"file{i}.py")).write_text(f"# Level {i}")
    
    # Scan with max_depth=5
    result = await scan_codebase(
        path=test_codebase,
        max_depth=5,
        cache_manager=cache_manager
    )
    
    # Should not scan all 15 levels
    structure = result["structure"]
    # Original 4 files + some from the first 5 levels
    assert structure["total_files"] < 19  # Less than all files


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
