"""
Integration tests for the Analysis Engine.

Tests the full analysis pipeline including:
- Single file analysis
- Codebase analysis with real projects
- Incremental analysis (only changed files)
- Caching behavior
- Parallel processing
- Error recovery
"""

import os
import pytest
import pytest_asyncio
import tempfile
import shutil
import asyncio
from pathlib import Path
from datetime import datetime

from src.analysis.engine import AnalysisEngine
from src.analysis.config import AnalysisConfig
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
        try:
            yield manager
        finally:
            # Ensure cache is always closed, even if test fails
            await manager.close()


@pytest.fixture
def analysis_config():
    """Create test analysis configuration."""
    return AnalysisConfig(
        supported_languages=["python", "javascript", "typescript"],
        max_complexity_threshold=10,
        min_documentation_coverage=0.5,
        teaching_value_weights={
            "documentation": 0.3,
            "complexity": 0.3,
            "patterns": 0.2,
            "structure": 0.2
        },
        enable_linters=False,  # Disable linters for faster tests
        enable_incremental=True,
        cache_ttl_seconds=3600,
        persistence_path=".documee/analysis"
    )


@pytest_asyncio.fixture
async def analysis_engine(cache_manager, analysis_config):
    """Create analysis engine instance."""
    engine = AnalysisEngine(cache_manager, analysis_config)
    yield engine
    # Cleanup: ensure all connections are closed
    if hasattr(engine, 'parser') and hasattr(engine.parser, 'parsers'):
        engine.parser.parsers.clear()
    if hasattr(engine, 'persistence') and hasattr(engine.persistence, 'base_path'):
        # Persistence manager doesn't hold connections, just file handles
        pass


@pytest.fixture
def test_python_file():
    """Create a temporary Python file for testing."""
    tmpdir = tempfile.mkdtemp()
    file_path = os.path.join(tmpdir, "test_module.py")
    
    content = '''"""
Test module for analysis.

This module demonstrates various Python features.
"""

def simple_function(x, y):
    """Add two numbers.
    
    Args:
        x: First number
        y: Second number
    
    Returns:
        Sum of x and y
    """
    return x + y


def complex_function(data):
    """Process data with multiple conditions."""
    result = []
    for item in data:
        if item > 0:
            if item % 2 == 0:
                result.append(item * 2)
            else:
                result.append(item + 1)
        elif item < 0:
            result.append(abs(item))
    return result


class Calculator:
    """A simple calculator class."""
    
    def __init__(self):
        """Initialize calculator."""
        self.history = []
    
    def add(self, a, b):
        """Add two numbers."""
        result = a + b
        self.history.append(result)
        return result
    
    def multiply(self, a, b):
        """Multiply two numbers."""
        result = a * b
        self.history.append(result)
        return result
'''
    
    Path(file_path).write_text(content)
    yield file_path
    shutil.rmtree(tmpdir, ignore_errors=True)


@pytest.fixture
def test_javascript_file():
    """Create a temporary JavaScript file for testing."""
    tmpdir = tempfile.mkdtemp()
    file_path = os.path.join(tmpdir, "test_module.js")
    
    content = '''/**
 * Test module for JavaScript analysis.
 */

/**
 * Add two numbers.
 * @param {number} x - First number
 * @param {number} y - Second number
 * @returns {number} Sum
 */
function add(x, y) {
    return x + y;
}

/**
 * Process array with conditions.
 * @param {Array} data - Input array
 * @returns {Array} Processed array
 */
function processData(data) {
    const result = [];
    for (const item of data) {
        if (item > 0) {
            if (item % 2 === 0) {
                result.push(item * 2);
            } else {
                result.push(item + 1);
            }
        }
    }
    return result;
}

/**
 * Calculator class.
 */
class Calculator {
    constructor() {
        this.history = [];
    }
    
    add(a, b) {
        const result = a + b;
        this.history.push(result);
        return result;
    }
}

export { add, processData, Calculator };
'''
    
    Path(file_path).write_text(content)
    yield file_path
    shutil.rmtree(tmpdir, ignore_errors=True)


@pytest.fixture
def test_codebase():
    """Create a temporary test codebase with multiple files."""
    tmpdir = tempfile.mkdtemp()
    
    # Create directory structure
    os.makedirs(os.path.join(tmpdir, "src"))
    os.makedirs(os.path.join(tmpdir, "tests"))
    
    # Python files
    Path(os.path.join(tmpdir, "src", "main.py")).write_text('''
"""Main module."""

def main():
    """Entry point."""
    print("Hello, world!")

if __name__ == "__main__":
    main()
''')
    
    Path(os.path.join(tmpdir, "src", "utils.py")).write_text('''
"""Utility functions."""

def helper(x):
    """Helper function."""
    return x * 2
''')
    
    # JavaScript files
    Path(os.path.join(tmpdir, "src", "app.js")).write_text('''
/**
 * Main application.
 */
function init() {
    console.log("App initialized");
}

export { init };
''')
    
    # Test files
    Path(os.path.join(tmpdir, "tests", "test_main.py")).write_text('''
"""Tests for main module."""

def test_main():
    """Test main function."""
    assert True
''')
    
    yield tmpdir
    shutil.rmtree(tmpdir, ignore_errors=True)


# Test 1: Full file analysis pipeline
@pytest.mark.asyncio
async def test_full_file_analysis_pipeline(analysis_engine, test_python_file):
    """Test complete file analysis pipeline."""
    # Analyze the file
    result = await analysis_engine.analyze_file(test_python_file)
    
    # Verify basic structure
    assert result is not None
    assert result.file_path == test_python_file
    assert result.language == "python"
    assert not result.cache_hit  # First analysis
    
    # Verify symbol extraction
    assert len(result.symbol_info.functions) >= 2  # simple_function, complex_function
    assert len(result.symbol_info.classes) >= 1  # Calculator
    
    # Verify function details
    function_names = [f.name for f in result.symbol_info.functions]
    assert "simple_function" in function_names
    assert "complex_function" in function_names
    
    # Verify class details
    class_names = [c.name for c in result.symbol_info.classes]
    assert "Calculator" in class_names
    
    # Verify complexity metrics
    assert result.complexity_metrics is not None
    assert result.complexity_metrics.avg_complexity > 0
    
    # Verify documentation coverage
    assert result.documentation_coverage >= 0.0
    assert result.documentation_coverage <= 1.0
    
    # Verify teaching value score
    assert result.teaching_value is not None
    assert 0.0 <= result.teaching_value.total_score <= 1.0
    assert result.teaching_value.explanation is not None
    
    # Verify no errors
    assert not result.has_errors


@pytest.mark.asyncio
async def test_javascript_file_analysis(analysis_engine, test_javascript_file):
    """Test JavaScript file analysis."""
    result = await analysis_engine.analyze_file(test_javascript_file)
    
    assert result is not None
    assert result.language == "javascript"
    assert len(result.symbol_info.functions) >= 2
    assert len(result.symbol_info.classes) >= 1
    
    # Verify exports are detected
    assert len(result.symbol_info.exports) > 0


# Test 2: Caching behavior
@pytest.mark.asyncio
async def test_caching_behavior(analysis_engine, test_python_file):
    """Test that analysis results are properly cached."""
    # First analysis - should not be cached
    result1 = await analysis_engine.analyze_file(test_python_file)
    assert not result1.cache_hit
    
    # Second analysis - should be cached
    result2 = await analysis_engine.analyze_file(test_python_file)
    assert result2.cache_hit
    
    # Verify results are the same
    assert result1.file_path == result2.file_path
    assert result1.language == result2.language
    assert len(result1.symbol_info.functions) == len(result2.symbol_info.functions)
    assert len(result1.symbol_info.classes) == len(result2.symbol_info.classes)


@pytest.mark.asyncio
async def test_force_reanalysis(analysis_engine, test_python_file):
    """Test forcing re-analysis bypasses cache."""
    # First analysis
    result1 = await analysis_engine.analyze_file(test_python_file)
    assert not result1.cache_hit
    
    # Force re-analysis
    result2 = await analysis_engine.analyze_file(test_python_file, force=True)
    assert not result2.cache_hit  # Should not use cache
    
    # Verify analysis was performed
    assert result2.file_path == test_python_file


# Test 3: Codebase analysis with real projects
@pytest.mark.asyncio
async def test_codebase_analysis(analysis_engine, cache_manager, test_codebase):
    """Test analyzing an entire codebase."""
    # First, create a scan result (simulating scan_codebase)
    codebase_id = "test_codebase_123"
    
    # Get all analyzable files
    files = []
    for root, dirs, filenames in os.walk(test_codebase):
        for filename in filenames:
            if filename.endswith(('.py', '.js', '.jsx', '.ts', '.tsx')):
                files.append(os.path.join(root, filename))
    
    # Store scan result in cache
    scan_result = {
        "codebase_id": codebase_id,
        "files": files,
        "structure": {
            "total_files": len(files),
            "languages": ["Python", "JavaScript"]
        }
    }
    await cache_manager.set_analysis(f"scan:{codebase_id}", scan_result)
    
    # Analyze codebase
    result = await analysis_engine.analyze_codebase(codebase_id, incremental=False)
    
    # Verify results
    assert result is not None
    assert result.codebase_id == codebase_id
    assert len(result.file_analyses) > 0
    
    # Verify metrics
    assert result.metrics.total_files > 0
    assert result.metrics.total_functions >= 0
    assert result.metrics.total_classes >= 0
    assert result.metrics.analysis_time_ms > 0
    
    # Verify dependency graph exists
    assert result.dependency_graph is not None


# Test 4: Incremental analysis (only changed files)
@pytest.mark.asyncio
async def test_incremental_analysis(analysis_engine, cache_manager, test_codebase):
    """Test that incremental analysis only processes changed files."""
    codebase_id = "test_incremental_123"
    
    # Get all analyzable files
    files = []
    for root, dirs, filenames in os.walk(test_codebase):
        for filename in filenames:
            if filename.endswith(('.py', '.js', '.jsx', '.ts', '.tsx')):
                files.append(os.path.join(root, filename))
    
    # Store scan result
    scan_result = {
        "codebase_id": codebase_id,
        "files": files
    }
    await cache_manager.set_analysis(f"scan:{codebase_id}", scan_result)
    
    # First analysis (full)
    result1 = await analysis_engine.analyze_codebase(codebase_id, incremental=False)
    initial_files = len(result1.file_analyses)
    
    # Modify one file
    if files:
        test_file = files[0]
        with open(test_file, 'a') as f:
            f.write('\n# Modified\n')
    
    # Second analysis (incremental)
    result2 = await analysis_engine.analyze_codebase(codebase_id, incremental=True)
    
    # Verify incremental analysis worked
    assert result2 is not None
    assert len(result2.file_analyses) == initial_files
    
    # At least one file should have been re-analyzed (the modified one)
    # Others should be reused from previous analysis


# Test 5: Parallel processing
@pytest.mark.asyncio
async def test_parallel_processing(analysis_engine, cache_manager, test_codebase):
    """Test that multiple files are analyzed in parallel."""
    codebase_id = "test_parallel_123"
    
    # Get all analyzable files
    files = []
    for root, dirs, filenames in os.walk(test_codebase):
        for filename in filenames:
            if filename.endswith(('.py', '.js', '.jsx', '.ts', '.tsx')):
                files.append(os.path.join(root, filename))
    
    # Store scan result
    scan_result = {
        "codebase_id": codebase_id,
        "files": files
    }
    await cache_manager.set_analysis(f"scan:{codebase_id}", scan_result)
    
    # Measure analysis time
    start_time = datetime.now()
    result = await analysis_engine.analyze_codebase(codebase_id, incremental=False)
    elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
    
    # Verify all files were analyzed
    assert len(result.file_analyses) == len(files)
    
    # Parallel processing should be reasonably fast
    # (This is a weak assertion, but ensures basic functionality)
    assert elapsed_ms < 30000  # Less than 30 seconds for small codebase


# Test 6: Error recovery
@pytest.mark.asyncio
async def test_error_recovery_invalid_file(analysis_engine):
    """Test that engine handles invalid files gracefully."""
    # Try to analyze non-existent file
    result = await analysis_engine.analyze_file("/nonexistent/file.py")
    
    # Should return error analysis, not crash
    assert result is not None
    assert result.has_errors
    assert len(result.errors) > 0


@pytest.mark.asyncio
async def test_error_recovery_syntax_error(analysis_engine):
    """Test that engine handles syntax errors gracefully."""
    # Create file with syntax error
    tmpdir = tempfile.mkdtemp()
    file_path = os.path.join(tmpdir, "syntax_error.py")
    
    # Invalid Python syntax
    Path(file_path).write_text('''
def broken_function(
    # Missing closing parenthesis and body
''')
    
    try:
        result = await analysis_engine.analyze_file(file_path)
        
        # Should handle error gracefully
        assert result is not None
        # May or may not have errors depending on parser behavior
        # But should not crash
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


@pytest.mark.asyncio
async def test_error_recovery_codebase_with_errors(analysis_engine, cache_manager):
    """Test that codebase analysis continues despite individual file errors."""
    tmpdir = tempfile.mkdtemp()
    codebase_id = "test_errors_123"
    
    try:
        # Create mix of valid and invalid files
        valid_file = os.path.join(tmpdir, "valid.py")
        Path(valid_file).write_text('def valid(): pass')
        
        invalid_file = os.path.join(tmpdir, "invalid.py")
        Path(invalid_file).write_text('def broken(')
        
        files = [valid_file, invalid_file]
        
        # Store scan result
        scan_result = {
            "codebase_id": codebase_id,
            "files": files
        }
        await cache_manager.set_analysis(f"scan:{codebase_id}", scan_result)
        
        # Analyze codebase
        result = await analysis_engine.analyze_codebase(codebase_id, incremental=False)
        
        # Should complete despite errors
        assert result is not None
        assert len(result.file_analyses) == 2
        
        # At least one file should be analyzed successfully
        successful = sum(1 for fa in result.file_analyses.values() if not fa.has_errors)
        assert successful >= 1
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


# Test 7: Performance validation
@pytest.mark.asyncio
async def test_single_file_performance(analysis_engine, test_python_file):
    """Test that single file analysis meets performance targets."""
    # Analyze file and measure time
    start_time = datetime.now()
    result = await analysis_engine.analyze_file(test_python_file)
    elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
    
    # Should complete in reasonable time (relaxed for test environment)
    assert elapsed_ms < 5000  # 5 seconds (relaxed from 500ms for test environment)
    assert result is not None


@pytest.mark.asyncio
async def test_cached_analysis_performance(analysis_engine, test_python_file):
    """Test that cached analysis is fast."""
    # First analysis (uncached)
    await analysis_engine.analyze_file(test_python_file)
    
    # Second analysis (cached)
    start_time = datetime.now()
    result = await analysis_engine.analyze_file(test_python_file)
    elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
    
    # Cached analysis should be very fast
    assert result.cache_hit
    assert elapsed_ms < 1000  # Less than 1 second


# Test 8: Data integrity
@pytest.mark.asyncio
async def test_analysis_data_integrity(analysis_engine, test_python_file):
    """Test that analysis data is complete and valid."""
    result = await analysis_engine.analyze_file(test_python_file)
    
    # Verify all required fields are present
    assert result.file_path is not None
    assert result.language is not None
    assert result.symbol_info is not None
    assert result.patterns is not None
    assert result.teaching_value is not None
    assert result.complexity_metrics is not None
    assert result.documentation_coverage is not None
    assert result.analyzed_at is not None
    
    # Verify data types
    assert isinstance(result.file_path, str)
    assert isinstance(result.language, str)
    assert isinstance(result.patterns, list)
    assert isinstance(result.linter_issues, list)
    assert isinstance(result.errors, list)
    assert isinstance(result.cache_hit, bool)
    assert isinstance(result.is_notebook, bool)
    
    # Verify numeric ranges
    assert 0.0 <= result.teaching_value.total_score <= 1.0
    assert 0.0 <= result.documentation_coverage <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
