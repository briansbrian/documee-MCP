"""
Unit tests for the framework detection tool.
"""

import os
import json
import pytest
import pytest_asyncio
import tempfile
import shutil
from pathlib import Path

from src.tools.detect_frameworks import detect_frameworks
from src.tools.scan_codebase import scan_codebase
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
def react_codebase():
    """Create a temporary React codebase."""
    tmpdir = tempfile.mkdtemp()
    
    # Create directory structure
    os.makedirs(os.path.join(tmpdir, "src"))
    
    # Create package.json with React and Next.js
    package_json = {
        "name": "test-react-app",
        "version": "1.0.0",
        "dependencies": {
            "react": "^18.2.0",
            "next": "^13.0.0"
        },
        "devDependencies": {
            "typescript": "^5.0.0"
        }
    }
    
    with open(os.path.join(tmpdir, "package.json"), "w") as f:
        json.dump(package_json, f)
    
    # Create some TypeScript files
    Path(os.path.join(tmpdir, "src", "App.tsx")).write_text("export default function App() {}")
    
    yield tmpdir
    
    # Cleanup
    shutil.rmtree(tmpdir, ignore_errors=True)


@pytest.fixture
def python_codebase():
    """Create a temporary Python codebase."""
    tmpdir = tempfile.mkdtemp()
    
    # Create directory structure
    os.makedirs(os.path.join(tmpdir, "src"))
    
    # Create requirements.txt with Django and Flask
    requirements = """django==4.2.0
flask>=2.3.0
pytest==7.4.0
# This is a comment
requests==2.31.0
"""
    
    with open(os.path.join(tmpdir, "requirements.txt"), "w") as f:
        f.write(requirements)
    
    # Create some Python files
    Path(os.path.join(tmpdir, "src", "main.py")).write_text("print('hello')")
    
    yield tmpdir
    
    # Cleanup
    shutil.rmtree(tmpdir, ignore_errors=True)


@pytest.mark.asyncio
async def test_detect_frameworks_without_scan(cache_manager):
    """Test that detection fails if codebase hasn't been scanned."""
    with pytest.raises(ValueError, match="Codebase not scanned"):
        await detect_frameworks(
            codebase_id="nonexistent123",
            cache_manager=cache_manager
        )


@pytest.mark.asyncio
async def test_detect_react_frameworks(react_codebase, cache_manager):
    """Test detection of React and Next.js frameworks."""
    # First scan the codebase
    scan_result = await scan_codebase(
        path=react_codebase,
        cache_manager=cache_manager
    )
    
    codebase_id = scan_result["codebase_id"]
    
    # Detect frameworks
    result = await detect_frameworks(
        codebase_id=codebase_id,
        confidence_threshold=0.7,
        cache_manager=cache_manager
    )
    
    assert "frameworks" in result
    assert "total_detected" in result
    assert result["from_cache"] is False
    assert result["total_detected"] == 2  # React and Next.js
    
    # Check framework details
    framework_names = [f["name"] for f in result["frameworks"]]
    assert "React" in framework_names
    assert "Next.js" in framework_names
    
    # Check confidence scores
    for framework in result["frameworks"]:
        assert framework["confidence"] == 0.99
        assert "package.json dependency" in framework["evidence"]
        assert framework["version"] != "detected"  # Should have actual version


@pytest.mark.asyncio
async def test_detect_python_frameworks(python_codebase, cache_manager):
    """Test detection of Python frameworks."""
    # First scan the codebase
    scan_result = await scan_codebase(
        path=python_codebase,
        cache_manager=cache_manager
    )
    
    codebase_id = scan_result["codebase_id"]
    
    # Detect frameworks
    result = await detect_frameworks(
        codebase_id=codebase_id,
        confidence_threshold=0.7,
        cache_manager=cache_manager
    )
    
    assert result["total_detected"] == 3  # Django, Flask, Pytest
    
    # Check framework details
    framework_names = [f["name"] for f in result["frameworks"]]
    assert "Django" in framework_names
    assert "Flask" in framework_names
    assert "Pytest" in framework_names
    
    # Check confidence scores
    for framework in result["frameworks"]:
        assert framework["confidence"] == 0.95
        assert "requirements.txt dependency" in framework["evidence"]


@pytest.mark.asyncio
async def test_detect_frameworks_with_cache(react_codebase, cache_manager):
    """Test caching functionality."""
    # First scan the codebase
    scan_result = await scan_codebase(
        path=react_codebase,
        cache_manager=cache_manager
    )
    
    codebase_id = scan_result["codebase_id"]
    
    # First detection
    result1 = await detect_frameworks(
        codebase_id=codebase_id,
        use_cache=True,
        cache_manager=cache_manager
    )
    assert result1["from_cache"] is False
    
    # Second detection (should be cached)
    result2 = await detect_frameworks(
        codebase_id=codebase_id,
        use_cache=True,
        cache_manager=cache_manager
    )
    assert result2["from_cache"] is True
    assert result2["total_detected"] == result1["total_detected"]


@pytest.mark.asyncio
async def test_confidence_threshold_filtering(react_codebase, cache_manager):
    """Test confidence threshold filtering."""
    # First scan the codebase
    scan_result = await scan_codebase(
        path=react_codebase,
        cache_manager=cache_manager
    )
    
    codebase_id = scan_result["codebase_id"]
    
    # Detect with high threshold (should still get results since confidence is 0.99)
    result = await detect_frameworks(
        codebase_id=codebase_id,
        confidence_threshold=0.95,
        cache_manager=cache_manager
    )
    
    assert result["total_detected"] == 2
    assert result["confidence_threshold"] == 0.95
    
    # All frameworks should meet the threshold
    for framework in result["frameworks"]:
        assert framework["confidence"] >= 0.95


@pytest.mark.asyncio
async def test_frameworks_sorted_by_confidence(python_codebase, cache_manager):
    """Test that frameworks are sorted by confidence descending."""
    # First scan the codebase
    scan_result = await scan_codebase(
        path=python_codebase,
        cache_manager=cache_manager
    )
    
    codebase_id = scan_result["codebase_id"]
    
    # Detect frameworks
    result = await detect_frameworks(
        codebase_id=codebase_id,
        cache_manager=cache_manager
    )
    
    # Check that frameworks are sorted by confidence
    confidences = [f["confidence"] for f in result["frameworks"]]
    assert confidences == sorted(confidences, reverse=True)


@pytest.mark.asyncio
async def test_no_frameworks_detected(cache_manager):
    """Test when no frameworks are detected."""
    tmpdir = tempfile.mkdtemp()
    
    try:
        # Create a simple codebase with no frameworks
        os.makedirs(os.path.join(tmpdir, "src"))
        Path(os.path.join(tmpdir, "src", "main.py")).write_text("print('hello')")
        
        # Scan the codebase
        scan_result = await scan_codebase(
            path=tmpdir,
            cache_manager=cache_manager
        )
        
        codebase_id = scan_result["codebase_id"]
        
        # Detect frameworks
        result = await detect_frameworks(
            codebase_id=codebase_id,
            cache_manager=cache_manager
        )
        
        assert result["total_detected"] == 0
        assert result["frameworks"] == []
        
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


@pytest.mark.asyncio
async def test_malformed_package_json(cache_manager):
    """Test graceful handling of malformed package.json."""
    tmpdir = tempfile.mkdtemp()
    
    try:
        # Create a codebase with malformed package.json
        os.makedirs(os.path.join(tmpdir, "src"))
        Path(os.path.join(tmpdir, "src", "App.tsx")).write_text("export default function App() {}")
        
        # Write malformed JSON
        with open(os.path.join(tmpdir, "package.json"), "w") as f:
            f.write("{ invalid json }")
        
        # Scan the codebase
        scan_result = await scan_codebase(
            path=tmpdir,
            cache_manager=cache_manager
        )
        
        codebase_id = scan_result["codebase_id"]
        
        # Detect frameworks - should not fail
        result = await detect_frameworks(
            codebase_id=codebase_id,
            cache_manager=cache_manager
        )
        
        # Should return empty results without crashing
        assert result["total_detected"] == 0
        assert result["frameworks"] == []
        
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
