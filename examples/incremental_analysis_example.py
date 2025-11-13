"""
Example: Incremental Analysis

This example demonstrates how incremental analysis works by tracking file changes
and only re-analyzing modified files. This dramatically speeds up repeated analysis.
"""

import sys
import asyncio
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analysis import AnalysisEngine, AnalysisConfig
from src.cache import CacheManager
from src.tools.scan_codebase import scan_codebase


async def main():
    """Demonstrate incremental analysis."""
    print("=" * 70)
    print("Analysis Engine - Incremental Analysis Example")
    print("=" * 70)
    
    # Initialize components
    config = AnalysisConfig()
    cache_manager = CacheManager()
    engine = AnalysisEngine(cache_manager, config)
    
    print("\n✓ Initialized Analysis Engine")
    
    # Create a temporary test directory
    test_dir = Path(__file__).parent / "test_incremental"
    test_dir.mkdir(exist_ok=True)
    
    # Create some sample files
    print("\n" + "-" * 70)
    print("Setup: Creating sample files")
    print("-" * 70)
    
    file1 = test_dir / "module1.py"
    file1.write_text("""
def calculate_sum(a, b):
    \"\"\"Calculate the sum of two numbers.\"\"\"
    return a + b

def calculate_product(a, b):
    \"\"\"Calculate the product of two numbers.\"\"\"
    return a * b
""")
    
    file2 = test_dir / "module2.py"
    file2.write_text("""
class Calculator:
    \"\"\"A simple calculator class.\"\"\"
    
    def add(self, a, b):
        \"\"\"Add two numbers.\"\"\"
        return a + b
    
    def subtract(self, a, b):
        \"\"\"Subtract b from a.\"\"\"
        return a - b
""")
    
    file3 = test_dir / "module3.py"
    file3.write_text("""
from module1 import calculate_sum
from module2 import Calculator

def main():
    \"\"\"Main function.\"\"\"
    calc = Calculator()
    result = calc.add(5, 3)
    print(f"Result: {result}")
""")
    
    print(f"\n✓ Created 3 sample files in {test_dir}")
    
    try:
        # Step 1: Initial scan and analysis
        print("\n" + "-" * 70)
        print("Step 1: Initial full analysis")
        print("-" * 70)
        
        scan_result = await scan_codebase(str(test_dir))
        cache_manager.set(f"scan:{scan_result.codebase_id}", scan_result, ttl=3600)
        
        print(f"\nScanned {scan_result.total_files} files")
        
        start_time = time.time()
        analysis1 = await engine.analyze_codebase(
            scan_result.codebase_id,
            incremental=False  # Full analysis
        )
        time1 = time.time() - start_time
        
        print(f"\n✓ Initial analysis complete!")
        print(f"  Files analyzed: {analysis1.metrics.total_files}")
        print(f"  Functions found: {analysis1.metrics.total_functions}")
        print(f"  Classes found: {analysis1.metrics.total_classes}")
        print(f"  Time taken: {time1:.3f}s")
        print(f"  Cache hit rate: {analysis1.metrics.cache_hit_rate:.1%}")
        
        # Step 2: Re-analyze without changes (should be fast)
        print("\n" + "-" * 70)
        print("Step 2: Re-analyze without changes (incremental)")
        print("-" * 70)
        
        print("\nNo files changed, should use cache...")
        
        start_time = time.time()
        analysis2 = await engine.analyze_codebase(
            scan_result.codebase_id,
            incremental=True  # Incremental mode
        )
        time2 = time.time() - start_time
        
        print(f"\n✓ Incremental analysis complete!")
        print(f"  Files analyzed: {analysis2.metrics.total_files}")
        print(f"  Time taken: {time2:.3f}s")
        print(f"  Cache hit rate: {analysis2.metrics.cache_hit_rate:.1%}")
        print(f"  Speedup: {time1/time2:.1f}x faster")
        
        # Step 3: Modify one file and re-analyze
        print("\n" + "-" * 70)
        print("Step 3: Modify one file and re-analyze")
        print("-" * 70)
        
        print(f"\nModifying {file1.name}...")
        file1.write_text("""
def calculate_sum(a, b):
    \"\"\"Calculate the sum of two numbers.\"\"\"
    return a + b

def calculate_product(a, b):
    \"\"\"Calculate the product of two numbers.\"\"\"
    return a * b

def calculate_difference(a, b):
    \"\"\"Calculate the difference between two numbers.\"\"\"
    return a - b  # NEW FUNCTION ADDED
""")
        
        # Re-scan to detect changes
        scan_result = await scan_codebase(str(test_dir))
        cache_manager.set(f"scan:{scan_result.codebase_id}", scan_result, ttl=3600)
        
        start_time = time.time()
        analysis3 = await engine.analyze_codebase(
            scan_result.codebase_id,
            incremental=True  # Only analyze changed files
        )
        time3 = time.time() - start_time
        
        print(f"\n✓ Incremental analysis complete!")
        print(f"  Files analyzed: {analysis3.metrics.total_files}")
        print(f"  Functions found: {analysis3.metrics.total_functions} (was {analysis2.metrics.total_functions})")
        print(f"  Time taken: {time3:.3f}s")
        print(f"  Cache hit rate: {analysis3.metrics.cache_hit_rate:.1%}")
        
        # Show which file was re-analyzed
        file1_analysis = analysis3.file_analyses.get(str(file1))
        if file1_analysis:
            print(f"\n  {file1.name} was re-analyzed:")
            print(f"    Functions: {len(file1_analysis.symbol_info.functions)}")
            print(f"    Cache hit: {file1_analysis.cache_hit}")
        
        # Step 4: Add a new file
        print("\n" + "-" * 70)
        print("Step 4: Add a new file")
        print("-" * 70)
        
        file4 = test_dir / "module4.py"
        file4.write_text("""
class MathUtils:
    \"\"\"Utility class for math operations.\"\"\"
    
    @staticmethod
    def square(x):
        \"\"\"Calculate the square of a number.\"\"\"
        return x * x
    
    @staticmethod
    def cube(x):
        \"\"\"Calculate the cube of a number.\"\"\"
        return x * x * x
""")
        
        print(f"\nAdded new file: {file4.name}")
        
        # Re-scan to detect new file
        scan_result = await scan_codebase(str(test_dir))
        cache_manager.set(f"scan:{scan_result.codebase_id}", scan_result, ttl=3600)
        
        start_time = time.time()
        analysis4 = await engine.analyze_codebase(
            scan_result.codebase_id,
            incremental=True
        )
        time4 = time.time() - start_time
        
        print(f"\n✓ Incremental analysis complete!")
        print(f"  Files analyzed: {analysis4.metrics.total_files} (was {analysis3.metrics.total_files})")
        print(f"  Classes found: {analysis4.metrics.total_classes} (was {analysis3.metrics.total_classes})")
        print(f"  Time taken: {time4:.3f}s")
        print(f"  Cache hit rate: {analysis4.metrics.cache_hit_rate:.1%}")
        
        # Step 5: Performance comparison
        print("\n" + "-" * 70)
        print("Step 5: Performance Summary")
        print("-" * 70)
        
        print(f"\n  Analysis Times:")
        print(f"    Initial full analysis: {time1:.3f}s")
        print(f"    No changes (cached): {time2:.3f}s ({time1/time2:.1f}x faster)")
        print(f"    One file modified: {time3:.3f}s ({time1/time3:.1f}x faster)")
        print(f"    One file added: {time4:.3f}s ({time1/time4:.1f}x faster)")
        
        print(f"\n  Cache Hit Rates:")
        print(f"    Initial: {analysis1.metrics.cache_hit_rate:.1%}")
        print(f"    No changes: {analysis2.metrics.cache_hit_rate:.1%}")
        print(f"    One modified: {analysis3.metrics.cache_hit_rate:.1%}")
        print(f"    One added: {analysis4.metrics.cache_hit_rate:.1%}")
        
    finally:
        # Clean up test directory
        print("\n" + "-" * 70)
        print("Cleanup")
        print("-" * 70)
        
        import shutil
        if test_dir.exists():
            shutil.rmtree(test_dir)
            print(f"\n✓ Removed test directory: {test_dir}")
    
    print("\n" + "=" * 70)
    print("Example complete!")
    print("=" * 70)
    print("\nKey Takeaways:")
    print("  1. Incremental analysis tracks file hashes")
    print("  2. Only changed files are re-analyzed")
    print("  3. Unchanged files use cached results")
    print("  4. This provides massive speedups for large codebases")
    print("  5. Cache hit rates show how effective caching is")


if __name__ == "__main__":
    asyncio.run(main())
