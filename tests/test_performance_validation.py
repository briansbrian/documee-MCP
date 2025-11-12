"""
Performance validation tests for Analysis Engine.

Tests validate that the analysis engine meets performance targets:
- Single file analysis: <500ms for 1000-line file
- Codebase analysis: <30s for 100 files (first run)
- Cached analysis: <3s for 100 files
- Parallel processing: 10+ files concurrently
"""

import asyncio
import os
import tempfile
import time
from pathlib import Path

import pytest
import pytest_asyncio

from src.analysis.config import AnalysisConfig
from src.analysis.engine import AnalysisEngine
from src.cache.unified_cache import UnifiedCacheManager


# Test fixtures for performance testing
SAMPLE_PYTHON_CODE_1000_LINES = '''
"""Sample Python module for performance testing."""

def function_1():
    """Function 1 docstring."""
    x = 1
    if x > 0:
        return x * 2
    return 0

def function_2():
    """Function 2 docstring."""
    y = 2
    for i in range(10):
        y += i
    return y

class SampleClass:
    """Sample class docstring."""
    
    def method_1(self):
        """Method 1 docstring."""
        return "method1"
    
    def method_2(self, param):
        """Method 2 docstring."""
        if param > 0:
            return param * 2
        return 0

''' + '\n'.join([f'# Line {i}' for i in range(4, 1001)])


@pytest_asyncio.fixture
async def cache_manager():
    """Create a cache manager for testing."""
    # Use temporary database for testing
    temp_db = tempfile.mktemp(suffix='.db')
    cache = UnifiedCacheManager(
        max_memory_mb=100,
        sqlite_path=temp_db,
        redis_url=None
    )
    await cache.initialize()
    yield cache
    await cache.close()
    # Cleanup
    if os.path.exists(temp_db):
        os.remove(temp_db)


@pytest.fixture
def analysis_config():
    """Create analysis configuration for testing."""
    return AnalysisConfig(
        max_complexity_threshold=10,
        min_documentation_coverage=0.5,
        max_file_size_mb=10,
        supported_languages=["python", "javascript", "typescript"],
        max_parallel_files=10,
        cache_ttl_seconds=3600,
        enable_linters=False,  # Disable linters for performance tests
        enable_incremental=True,
        persistence_path=tempfile.mkdtemp()
    )


@pytest_asyncio.fixture
async def analysis_engine(cache_manager, analysis_config):
    """Create analysis engine for testing."""
    engine = AnalysisEngine(cache_manager, analysis_config)
    return engine


@pytest.fixture
def temp_python_file_1000_lines():
    """Create a temporary Python file with 1000 lines."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(SAMPLE_PYTHON_CODE_1000_LINES)
        temp_path = f.name
    yield temp_path
    os.remove(temp_path)


@pytest.fixture
def temp_codebase_100_files():
    """Create a temporary codebase with 100 Python files."""
    temp_dir = tempfile.mkdtemp()
    file_paths = []
    
    for i in range(100):
        file_path = os.path.join(temp_dir, f'file_{i:03d}.py')
        with open(file_path, 'w') as f:
            # Create files with varying complexity
            f.write(f'''
"""Module {i} for performance testing."""

def function_{i}_1():
    """Function docstring."""
    x = {i}
    if x > 0:
        return x * 2
    return 0

def function_{i}_2():
    """Another function."""
    y = {i}
    for j in range(10):
        y += j
    return y

class Class_{i}:
    """Class docstring."""
    
    def method_1(self):
        """Method docstring."""
        return "method1"
    
    def method_2(self, param):
        """Method docstring."""
        if param > 0:
            return param * 2
        return 0
''')
        file_paths.append(file_path)
    
    yield temp_dir, file_paths
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)


@pytest.mark.asyncio
async def test_single_file_analysis_performance(analysis_engine, temp_python_file_1000_lines):
    """
    Test: Single file analysis should complete in <500ms for 1000-line file.
    
    Requirement: 10.1 - Single file analysis: <500ms for 1000-line file
    """
    # Warm up (first run may be slower due to initialization)
    await analysis_engine.analyze_file(temp_python_file_1000_lines)
    
    # Reset metrics
    analysis_engine.reset_performance_metrics()
    
    # Measure performance
    start_time = time.time()
    result = await analysis_engine.analyze_file(temp_python_file_1000_lines, force=True)
    elapsed_ms = (time.time() - start_time) * 1000
    
    # Validate result
    assert result is not None
    assert result.file_path == temp_python_file_1000_lines
    assert not result.cache_hit  # Force=True bypasses cache
    
    # Validate performance target: <500ms
    print(f"\nSingle file analysis time: {elapsed_ms:.2f}ms")
    assert elapsed_ms < 500, f"Single file analysis took {elapsed_ms:.2f}ms, expected <500ms"


@pytest.mark.asyncio
async def test_cached_file_analysis_performance(analysis_engine, temp_python_file_1000_lines):
    """
    Test: Cached file analysis should be very fast (<100ms).
    
    Requirement: 10.4 - Cached analysis should be fast
    """
    # First analysis (cache miss)
    await analysis_engine.analyze_file(temp_python_file_1000_lines)
    
    # Second analysis (cache hit)
    start_time = time.time()
    result = await analysis_engine.analyze_file(temp_python_file_1000_lines)
    elapsed_ms = (time.time() - start_time) * 1000
    
    # Validate result
    assert result is not None
    assert result.cache_hit is True
    
    # Validate performance: cached should be <100ms
    print(f"\nCached file analysis time: {elapsed_ms:.2f}ms")
    assert elapsed_ms < 100, f"Cached analysis took {elapsed_ms:.2f}ms, expected <100ms"


@pytest.mark.asyncio
async def test_parallel_file_processing(analysis_engine, temp_codebase_100_files):
    """
    Test: Parallel processing should handle 10+ files concurrently.
    
    Requirement: 10.4 - Parallel processing: 10+ files concurrently
    """
    temp_dir, file_paths = temp_codebase_100_files
    
    # Take first 20 files for parallel test
    test_files = file_paths[:20]
    
    # Analyze files in parallel
    start_time = time.time()
    tasks = [analysis_engine.analyze_file(fp) for fp in test_files]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    elapsed_ms = (time.time() - start_time) * 1000
    
    # Validate results
    successful_results = [r for r in results if not isinstance(r, Exception)]
    assert len(successful_results) >= 18, f"Expected at least 18 successful analyses, got {len(successful_results)}"
    
    # Validate parallel processing
    # If truly parallel, 20 files should take less than 20x single file time
    # With max_parallel_files workers, should be roughly 2x single file time
    avg_time_per_file = elapsed_ms / len(test_files)
    print(f"\nParallel processing: {len(test_files)} files in {elapsed_ms:.2f}ms")
    print(f"Average time per file: {avg_time_per_file:.2f}ms")
    
    # Verify parallelism: total time should be much less than sequential
    # Sequential would be ~20 * 500ms = 10,000ms
    # Parallel with 10 workers should be ~2 * 500ms = 1,000ms
    assert elapsed_ms < 5000, f"Parallel processing took {elapsed_ms:.2f}ms, expected <5000ms"


@pytest.mark.asyncio
async def test_codebase_analysis_first_run_performance(
    analysis_engine,
    cache_manager,
    temp_codebase_100_files
):
    """
    Test: Codebase analysis should complete in <30s for 100 files (first run).
    
    Requirement: 10.2 - Codebase analysis: <30s for 100 files (first run)
    """
    temp_dir, file_paths = temp_codebase_100_files
    
    # Create a scan result for the codebase
    codebase_id = "test_codebase_100"
    scan_result = {
        "path": temp_dir,
        "total_files": len(file_paths),
        "files": file_paths
    }
    await cache_manager.set_analysis(f"scan:{codebase_id}", scan_result)
    
    # Reset metrics
    analysis_engine.reset_performance_metrics()
    
    # Measure first run performance
    start_time = time.time()
    result = await analysis_engine.analyze_codebase(codebase_id, incremental=False)
    elapsed_ms = (time.time() - start_time) * 1000
    elapsed_s = elapsed_ms / 1000
    
    # Validate result
    assert result is not None
    assert result.codebase_id == codebase_id
    assert result.metrics.total_files > 0
    
    # Validate performance target: <30s for 100 files
    print(f"\nCodebase analysis (first run): {elapsed_s:.2f}s for {result.metrics.total_files} files")
    print(f"Average time per file: {result.metrics.analysis_time_ms / result.metrics.total_files:.2f}ms")
    assert elapsed_s < 30, f"Codebase analysis took {elapsed_s:.2f}s, expected <30s"


@pytest.mark.asyncio
async def test_codebase_analysis_cached_performance(
    analysis_engine,
    cache_manager,
    temp_codebase_100_files
):
    """
    Test: Cached codebase analysis should complete in <3s for 100 files.
    
    Requirement: 10.3 - Cached analysis: <3s for 100 files
    """
    temp_dir, file_paths = temp_codebase_100_files
    
    # Create a scan result for the codebase
    codebase_id = "test_codebase_cached"
    scan_result = {
        "path": temp_dir,
        "total_files": len(file_paths),
        "files": file_paths
    }
    await cache_manager.set_analysis(f"scan:{codebase_id}", scan_result)
    
    # First run (populate cache)
    await analysis_engine.analyze_codebase(codebase_id, incremental=False)
    
    # Reset metrics
    analysis_engine.reset_performance_metrics()
    
    # Second run (should use cache)
    start_time = time.time()
    result = await analysis_engine.analyze_codebase(codebase_id, incremental=True)
    elapsed_ms = (time.time() - start_time) * 1000
    elapsed_s = elapsed_ms / 1000
    
    # Validate result
    assert result is not None
    assert result.metrics.cache_hit_rate > 0.8, f"Cache hit rate {result.metrics.cache_hit_rate:.2%} is too low"
    
    # Validate performance target: <3s for cached analysis
    print(f"\nCodebase analysis (cached): {elapsed_s:.2f}s for {result.metrics.total_files} files")
    print(f"Cache hit rate: {result.metrics.cache_hit_rate:.2%}")
    assert elapsed_s < 3, f"Cached codebase analysis took {elapsed_s:.2f}s, expected <3s"


@pytest.mark.asyncio
async def test_performance_metrics_tracking(analysis_engine, temp_python_file_1000_lines):
    """
    Test: Performance metrics should be tracked correctly.
    
    Requirement: 10.5 - Log performance metrics
    """
    # Reset metrics
    analysis_engine.reset_performance_metrics()
    
    # Perform some analyses
    await analysis_engine.analyze_file(temp_python_file_1000_lines)  # First analysis (cache miss)
    await analysis_engine.analyze_file(temp_python_file_1000_lines, force=True)  # Force re-analysis (cache miss)
    
    # Get metrics
    metrics = analysis_engine.get_performance_metrics()
    
    # Validate metrics
    # total_files_analyzed counts actual analysis operations (not cache hits)
    assert metrics['total_files_analyzed'] == 2
    assert metrics['total_cache_misses'] >= 1  # At least one cache miss
    assert metrics['total_analysis_time_ms'] > 0
    assert metrics['avg_time_per_file_ms'] > 0
    assert len(metrics['file_analysis_times']) == 2
    
    print(f"\nPerformance metrics:")
    print(f"  Total files analyzed: {metrics['total_files_analyzed']}")
    print(f"  Cache hits: {metrics['total_cache_hits']}")
    print(f"  Cache misses: {metrics['total_cache_misses']}")
    print(f"  Cache hit rate: {metrics['cache_hit_rate']:.2%}")
    print(f"  Total analysis time: {metrics['total_analysis_time_ms']:.2f}ms")
    print(f"  Average time per file: {metrics['avg_time_per_file_ms']:.2f}ms")


@pytest.mark.asyncio
async def test_slow_operation_detection(analysis_engine, temp_python_file_1000_lines):
    """
    Test: Slow operations (>1000ms) should be detected and logged.
    
    Requirement: 13.4 - Log slow operations (>1000ms)
    """
    # Reset metrics
    analysis_engine.reset_performance_metrics()
    
    # Perform analysis
    await analysis_engine.analyze_file(temp_python_file_1000_lines, force=True)
    
    # Get metrics
    metrics = analysis_engine.get_performance_metrics()
    
    # Check if slow operations are tracked
    # (May or may not have slow operations depending on system performance)
    print(f"\nSlow operations detected: {metrics['slow_operations_count']}")
    
    # Verify the tracking mechanism exists
    assert 'slow_operations_count' in metrics
    assert isinstance(metrics['slow_operations_count'], int)


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])
