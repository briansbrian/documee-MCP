"""
Direct test of analysis engine without MCP client.
This helps isolate issues with the analysis engine itself.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.cache.unified_cache import UnifiedCacheManager
from src.config.settings import Settings
from src.analysis.engine import AnalysisEngine
from src.analysis.config import AnalysisConfig


async def test_analysis_engine_direct():
    """Test the analysis engine directly without MCP."""
    
    print("=" * 80)
    print("DIRECT ANALYSIS ENGINE TEST")
    print("=" * 80)
    print()
    
    # Initialize components
    print("[1] Initializing cache manager...")
    config = Settings()
    cache_manager = UnifiedCacheManager(
        max_memory_mb=config.cache_max_memory_mb,
        sqlite_path=config.sqlite_path,
        redis_url=config.redis_url
    )
    await cache_manager.initialize()
    print("[OK] Cache manager initialized\n")
    
    # Initialize analysis engine
    print("[2] Initializing analysis engine...")
    analysis_config = AnalysisConfig()
    engine = AnalysisEngine(cache_manager, analysis_config)
    print("[OK] Analysis engine initialized\n")
    
    # Test 1: Analyze a single file
    print("[3] Testing analyze_file...")
    test_file = "src/server.py"
    
    if not Path(test_file).exists():
        print(f"[FAIL] Test file not found: {test_file}")
        return
    
    try:
        result = await engine.analyze_file(test_file)
        print(f"[OK] File analyzed: {result.file_path}")
        print(f"     Language: {result.language}")
        print(f"     Functions: {len(result.symbol_info.functions)}")
        print(f"     Classes: {len(result.symbol_info.classes)}")
        print(f"     Teaching value: {result.teaching_value.total_score}")
        print(f"     Has errors: {result.has_errors}")
        if result.has_errors:
            print(f"     Errors: {result.errors}")
        print()
    except Exception as e:
        print(f"[FAIL] Error analyzing file: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test 2: Check if file doesn't exist
    print("[4] Testing analyze_file with nonexistent file...")
    try:
        result = await engine.analyze_file("nonexistent_file.py")
        print(f"[WARN] Should have failed but got: {result}")
    except Exception as e:
        print(f"[OK] Correctly raised error: {type(e).__name__}")
    print()
    
    # Test 3: Analyze codebase (this is the one that might be slow/hanging)
    print("[5] Testing analyze_codebase...")
    print("     This may take 10-30 seconds for a full codebase...")
    
    # First, we need a codebase_id from a scan
    # For testing, let's create a minimal scan result
    codebase_id = "test_codebase_123"
    
    # Create a minimal scan result with just a few files
    test_files = [
        "src/server.py",
        "src/cache/unified_cache.py",
        "src/config/settings.py"
    ]
    
    # Filter to only existing files
    existing_files = [f for f in test_files if Path(f).exists()]
    
    if not existing_files:
        print("[FAIL] No test files found")
        return
    
    # Store scan result in cache (must include 'path' key for engine)
    import os
    scan_result = {
        "codebase_id": codebase_id,
        "path": os.getcwd(),  # Add path key that engine expects
        "files": existing_files,
        "structure": {"total_files": len(existing_files)}
    }
    
    await cache_manager.set_analysis(f"scan:{codebase_id}", scan_result, ttl=3600)
    print(f"[OK] Created test scan with {len(existing_files)} files\n")
    
    try:
        print(f"     Analyzing {len(existing_files)} files...")
        result = await engine.analyze_codebase(codebase_id, incremental=False)
        print(f"[OK] Codebase analyzed")
        print(f"     Total files: {result.metrics.total_files}")
        print(f"     Total functions: {result.metrics.total_functions}")
        print(f"     Total classes: {result.metrics.total_classes}")
        print(f"     Patterns detected: {result.metrics.total_patterns_detected}")
        print(f"     Analysis time: {result.metrics.analysis_time_ms:.0f}ms")
        print()
    except Exception as e:
        print(f"[FAIL] Error analyzing codebase: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Cleanup
    print("[6] Cleaning up...")
    await cache_manager.close()
    print("[OK] Cache manager closed\n")
    
    print("=" * 80)
    print("[SUCCESS] All direct tests passed!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_analysis_engine_direct())
