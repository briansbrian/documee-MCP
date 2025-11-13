"""
Example: Analyze a Single File

This example demonstrates how to analyze a single code file using the Analysis Engine.
It shows AST parsing, symbol extraction, pattern detection, and teaching value scoring.
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analysis import AnalysisEngine, AnalysisConfig
from src.cache import CacheManager


async def main():
    """Demonstrate single file analysis."""
    print("=" * 70)
    print("Analysis Engine - Single File Analysis Example")
    print("=" * 70)
    
    # Initialize components
    config = AnalysisConfig()
    cache_manager = CacheManager()
    engine = AnalysisEngine(cache_manager, config)
    
    print("\n✓ Initialized Analysis Engine")
    print(f"  Supported languages: {', '.join(config.supported_languages[:5])}...")
    
    # Example 1: Analyze a Python file
    print("\n" + "-" * 70)
    print("Example 1: Analyzing a Python file")
    print("-" * 70)
    
    # Use this example file itself
    file_path = __file__
    
    try:
        # Analyze the file
        print(f"\nAnalyzing: {Path(file_path).name}")
        result = await engine.analyze_file(file_path)
        
        print(f"\n✓ Analysis complete!")
        print(f"  Language: {result.language}")
        print(f"  Cache hit: {result.cache_hit}")
        print(f"  Has errors: {result.has_errors}")
        
        # Show symbol information
        print(f"\n  Symbols extracted:")
        print(f"    Functions: {len(result.symbol_info.functions)}")
        print(f"    Classes: {len(result.symbol_info.classes)}")
        print(f"    Imports: {len(result.symbol_info.imports)}")
        
        # Show first few functions
        if result.symbol_info.functions:
            print(f"\n  First 3 functions:")
            for func in result.symbol_info.functions[:3]:
                print(f"    - {func.name}() at line {func.start_line}")
                print(f"      Parameters: {', '.join(func.parameters) if func.parameters else 'none'}")
                print(f"      Complexity: {func.complexity}")
        
        # Show patterns detected
        print(f"\n  Patterns detected: {len(result.patterns)}")
        for pattern in result.patterns[:3]:
            print(f"    - {pattern.pattern_type} (confidence: {pattern.confidence:.2f})")
        
        # Show teaching value score
        print(f"\n  Teaching Value Score: {result.teaching_value.total_score:.2f}/1.0")
        print(f"    Documentation: {result.teaching_value.documentation_score:.2f}")
        print(f"    Complexity: {result.teaching_value.complexity_score:.2f}")
        print(f"    Pattern: {result.teaching_value.pattern_score:.2f}")
        print(f"    Structure: {result.teaching_value.structure_score:.2f}")
        
        # Show complexity metrics
        print(f"\n  Complexity Metrics:")
        print(f"    Average complexity: {result.complexity_metrics.avg_complexity:.2f}")
        print(f"    Max complexity: {result.complexity_metrics.max_complexity}")
        print(f"    High complexity functions: {result.complexity_metrics.high_complexity_count}")
        
        # Show documentation coverage
        print(f"\n  Documentation Coverage: {result.documentation_coverage:.1%}")
        
        # Show linter issues (if any)
        if result.linter_issues:
            print(f"\n  Linter Issues: {len(result.linter_issues)}")
            for issue in result.linter_issues[:3]:
                print(f"    - Line {issue.line}: {issue.message}")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Example 2: Analyze with force refresh (bypass cache)
    print("\n" + "-" * 70)
    print("Example 2: Force re-analysis (bypass cache)")
    print("-" * 70)
    
    try:
        print(f"\nRe-analyzing with force=True...")
        result = await engine.analyze_file(file_path, force=True)
        
        print(f"\n✓ Re-analysis complete!")
        print(f"  Cache hit: {result.cache_hit} (should be False)")
        print(f"  Teaching value: {result.teaching_value.total_score:.2f}")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
    
    # Example 3: Analyze a JavaScript file (if available)
    print("\n" + "-" * 70)
    print("Example 3: Analyzing different file types")
    print("-" * 70)
    
    # Create a sample JavaScript file for demonstration
    sample_js = Path(__file__).parent / "sample_code.js"
    sample_js.write_text("""
// Sample React component
import React, { useState } from 'react';

function Counter({ initialValue = 0 }) {
    const [count, setCount] = useState(initialValue);
    
    const increment = () => {
        setCount(count + 1);
    };
    
    return (
        <div>
            <p>Count: {count}</p>
            <button onClick={increment}>Increment</button>
        </div>
    );
}

export default Counter;
""")
    
    try:
        print(f"\nAnalyzing: {sample_js.name}")
        result = await engine.analyze_file(str(sample_js))
        
        print(f"\n✓ Analysis complete!")
        print(f"  Language: {result.language}")
        print(f"  Functions: {len(result.symbol_info.functions)}")
        print(f"  Patterns: {len(result.patterns)}")
        
        # Show React patterns
        react_patterns = [p for p in result.patterns if 'react' in p.pattern_type.lower()]
        if react_patterns:
            print(f"\n  React patterns detected:")
            for pattern in react_patterns:
                print(f"    - {pattern.pattern_type}")
                print(f"      Evidence: {', '.join(pattern.evidence[:2])}")
        
        print(f"\n  Teaching value: {result.teaching_value.total_score:.2f}")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
    finally:
        # Clean up sample file
        if sample_js.exists():
            sample_js.unlink()
    
    print("\n" + "=" * 70)
    print("Example complete!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
