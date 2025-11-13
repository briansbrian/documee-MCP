"""
Example: Analyze Entire Codebase

This example demonstrates how to analyze an entire codebase using the Analysis Engine.
It shows parallel processing, dependency analysis, pattern detection, and teaching value ranking.
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analysis import AnalysisEngine, AnalysisConfig
from src.cache import CacheManager
from src.tools.scan_codebase import scan_codebase


async def main():
    """Demonstrate codebase analysis."""
    print("=" * 70)
    print("Analysis Engine - Codebase Analysis Example")
    print("=" * 70)
    
    # Initialize components
    config = AnalysisConfig()
    cache_manager = CacheManager()
    engine = AnalysisEngine(cache_manager, config)
    
    print("\n✓ Initialized Analysis Engine")
    
    # Step 1: Scan the codebase first
    print("\n" + "-" * 70)
    print("Step 1: Scanning codebase")
    print("-" * 70)
    
    # Use the src directory as example
    codebase_path = str(Path(__file__).parent.parent / "src")
    
    try:
        print(f"\nScanning: {codebase_path}")
        scan_result = await scan_codebase(codebase_path)
        
        print(f"\n✓ Scan complete!")
        print(f"  Codebase ID: {scan_result.codebase_id}")
        print(f"  Total files: {scan_result.total_files}")
        print(f"  Total size: {scan_result.total_size_bytes / 1024 / 1024:.2f} MB")
        print(f"  Languages: {', '.join(scan_result.languages[:5])}")
        
        # Cache the scan result
        cache_manager.set(f"scan:{scan_result.codebase_id}", scan_result, ttl=3600)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return
    
    # Step 2: Analyze the codebase
    print("\n" + "-" * 70)
    print("Step 2: Analyzing codebase (first run)")
    print("-" * 70)
    
    try:
        print(f"\nAnalyzing codebase: {scan_result.codebase_id}")
        print("This may take a moment for the first run...")
        
        analysis = await engine.analyze_codebase(
            scan_result.codebase_id,
            incremental=False  # Full analysis first time
        )
        
        print(f"\n✓ Analysis complete!")
        print(f"  Files analyzed: {analysis.metrics.total_files}")
        print(f"  Total functions: {analysis.metrics.total_functions}")
        print(f"  Total classes: {analysis.metrics.total_classes}")
        print(f"  Analysis time: {analysis.metrics.analysis_time_ms / 1000:.2f}s")
        print(f"  Cache hit rate: {analysis.metrics.cache_hit_rate:.1%}")
        
        # Show top teaching files
        print(f"\n  Top 10 files by teaching value:")
        for i, (file_path, score) in enumerate(analysis.top_teaching_files[:10], 1):
            file_name = Path(file_path).name
            print(f"    {i}. {file_name}: {score:.2f}")
        
        # Show global patterns
        print(f"\n  Global patterns detected: {len(analysis.global_patterns)}")
        pattern_types = {}
        for pattern in analysis.global_patterns:
            pattern_types[pattern.pattern_type] = pattern_types.get(pattern.pattern_type, 0) + 1
        
        for pattern_type, count in sorted(pattern_types.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"    - {pattern_type}: {count} occurrences")
        
        # Show dependency graph stats
        print(f"\n  Dependency Graph:")
        print(f"    Files: {len(analysis.dependency_graph.nodes)}")
        print(f"    Dependencies: {len(analysis.dependency_graph.edges)}")
        print(f"    Circular dependencies: {len(analysis.dependency_graph.circular_dependencies)}")
        
        if analysis.dependency_graph.circular_dependencies:
            print(f"\n    ⚠️  Circular dependencies found:")
            for circ in analysis.dependency_graph.circular_dependencies[:3]:
                print(f"      - {' -> '.join([Path(f).name for f in circ.cycle])}")
        
        # Show external dependencies
        print(f"\n  Top external dependencies:")
        top_deps = sorted(
            analysis.dependency_graph.external_dependencies.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        for dep, count in top_deps:
            print(f"    - {dep}: {count} imports")
        
        # Show complexity metrics
        print(f"\n  Codebase Metrics:")
        print(f"    Average complexity: {analysis.metrics.avg_complexity:.2f}")
        print(f"    Average documentation: {analysis.metrics.avg_documentation_coverage:.1%}")
        print(f"    Patterns detected: {analysis.metrics.total_patterns_detected}")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 3: Incremental analysis (only changed files)
    print("\n" + "-" * 70)
    print("Step 3: Incremental analysis (cached)")
    print("-" * 70)
    
    try:
        print(f"\nRe-analyzing with incremental=True...")
        print("This should be much faster (using cache)...")
        
        analysis = await engine.analyze_codebase(
            scan_result.codebase_id,
            incremental=True  # Only analyze changed files
        )
        
        print(f"\n✓ Incremental analysis complete!")
        print(f"  Files analyzed: {analysis.metrics.total_files}")
        print(f"  Analysis time: {analysis.metrics.analysis_time_ms / 1000:.2f}s")
        print(f"  Cache hit rate: {analysis.metrics.cache_hit_rate:.1%}")
        print(f"  Speedup: {analysis.metrics.analysis_time_ms / 1000:.2f}s vs previous")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
    
    # Step 4: Explore specific file analysis
    print("\n" + "-" * 70)
    print("Step 4: Exploring specific file details")
    print("-" * 70)
    
    if analysis.top_teaching_files:
        top_file_path, top_score = analysis.top_teaching_files[0]
        file_analysis = analysis.file_analyses.get(top_file_path)
        
        if file_analysis:
            print(f"\nTop teaching file: {Path(top_file_path).name}")
            print(f"  Teaching value: {top_score:.2f}")
            print(f"  Language: {file_analysis.language}")
            
            print(f"\n  Functions ({len(file_analysis.symbol_info.functions)}):")
            for func in file_analysis.symbol_info.functions[:5]:
                print(f"    - {func.name}()")
                print(f"      Lines: {func.start_line}-{func.end_line}")
                print(f"      Complexity: {func.complexity}")
                if func.docstring:
                    doc_preview = func.docstring[:60] + "..." if len(func.docstring) > 60 else func.docstring
                    print(f"      Doc: {doc_preview}")
            
            print(f"\n  Patterns ({len(file_analysis.patterns)}):")
            for pattern in file_analysis.patterns[:5]:
                print(f"    - {pattern.pattern_type} (confidence: {pattern.confidence:.2f})")
            
            print(f"\n  Teaching Value Breakdown:")
            print(f"    Documentation: {file_analysis.teaching_value.documentation_score:.2f}")
            print(f"    Complexity: {file_analysis.teaching_value.complexity_score:.2f}")
            print(f"    Pattern: {file_analysis.teaching_value.pattern_score:.2f}")
            print(f"    Structure: {file_analysis.teaching_value.structure_score:.2f}")
            
            print(f"\n  Explanation:")
            print(f"    {file_analysis.teaching_value.explanation}")
    
    print("\n" + "=" * 70)
    print("Example complete!")
    print("=" * 70)
    print("\nKey Takeaways:")
    print("  1. First run analyzes all files (slower)")
    print("  2. Incremental runs only analyze changed files (much faster)")
    print("  3. Results are cached for quick re-access")
    print("  4. Teaching value helps prioritize which code to teach")
    print("  5. Dependency graph shows code relationships")


if __name__ == "__main__":
    asyncio.run(main())
