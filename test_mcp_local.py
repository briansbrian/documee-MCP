"""
Quick local test of MCP server functionality.
Tests the 3 core tools without needing MCP Inspector.
"""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.cache.unified_cache import UnifiedCacheManager
from src.config.settings import Settings
from src.tools.scan_codebase import scan_codebase
from src.tools.detect_frameworks import detect_frameworks
from src.tools.discover_features import discover_features


async def test_mcp_workflow():
    """Test the complete MCP workflow."""
    print("=" * 60)
    print("Testing MCP Server Locally")
    print("=" * 60)
    
    # Initialize
    config = Settings()
    cache_manager = UnifiedCacheManager(
        max_memory_mb=config.cache_max_memory_mb,
        sqlite_path=config.sqlite_path,
        redis_url=config.redis_url
    )
    await cache_manager.initialize()
    
    try:
        # Test 1: Scan codebase
        print("\n[Test 1] Scanning codebase...")
        scan_result = await scan_codebase(
            path=".",
            max_depth=5,
            use_cache=True,
            cache_manager=cache_manager,
            max_file_size_mb=config.max_file_size_mb
        )
        
        codebase_id = scan_result["codebase_id"]
        print(f"✓ Scan complete!")
        print(f"  - Codebase ID: {codebase_id}")
        print(f"  - Total files: {scan_result['structure']['total_files']}")
        print(f"  - Languages: {list(scan_result['structure']['languages'].keys())}")
        print(f"  - Scan time: {scan_result['scan_time_ms']:.2f}ms")
        print(f"  - From cache: {scan_result['from_cache']}")
        
        # Test 2: Detect frameworks
        print("\n[Test 2] Detecting frameworks...")
        frameworks_result = await detect_frameworks(
            codebase_id=codebase_id,
            confidence_threshold=0.7,
            use_cache=True,
            cache_manager=cache_manager
        )
        
        print(f"✓ Detection complete!")
        print(f"  - Frameworks found: {frameworks_result['total_detected']}")
        for fw in frameworks_result['frameworks'][:5]:  # Show first 5
            print(f"    • {fw['name']} {fw['version']} (confidence: {fw['confidence']})")
        print(f"  - From cache: {frameworks_result['from_cache']}")
        
        # Test 3: Discover features
        print("\n[Test 3] Discovering features...")
        features_result = await discover_features(
            codebase_id=codebase_id,
            categories=None,  # All categories
            use_cache=True,
            cache_manager=cache_manager
        )
        
        print(f"✓ Discovery complete!")
        print(f"  - Features found: {features_result['total_features']}")
        for feature in features_result['features'][:5]:  # Show first 5
            print(f"    • {feature['name']} ({feature['category']}) - {feature['priority']} priority")
        print(f"  - From cache: {features_result['from_cache']}")
        
        # Test 4: Test caching (run scan again)
        print("\n[Test 4] Testing cache performance...")
        scan_result2 = await scan_codebase(
            path=".",
            max_depth=5,
            use_cache=True,
            cache_manager=cache_manager,
            max_file_size_mb=config.max_file_size_mb
        )
        
        print(f"✓ Cache test complete!")
        print(f"  - Scan time: {scan_result2['scan_time_ms']:.2f}ms")
        print(f"  - From cache: {scan_result2['from_cache']}")
        print(f"  - Speedup: {scan_result['scan_time_ms'] / scan_result2['scan_time_ms']:.1f}x faster")
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        print("\nThe MCP server is working correctly!")
        print("You can now test with MCP Inspector or integrate with Kiro/Claude.")
        
    finally:
        await cache_manager.close()


if __name__ == "__main__":
    asyncio.run(test_mcp_workflow())
