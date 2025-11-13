"""
Test pattern detection on real files in the codebase.
This verifies that Python files now get non-zero pattern scores.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.analysis.engine import AnalysisEngine
from src.analysis.config import AnalysisConfig
from src.cache.unified_cache import UnifiedCacheManager


async def test_real_file():
    """Test pattern detection on src/server.py"""
    
    print("Initializing cache and analysis engine...")
    cache = UnifiedCacheManager()
    await cache.initialize()
    
    config = AnalysisConfig()
    engine = AnalysisEngine(cache, config)
    
    # Test with src/server.py (should have async/await patterns)
    test_file = "src/server.py"
    print(f"\nAnalyzing {test_file}...")
    
    try:
        analysis = await engine.analyze_file(test_file, force=True)
        
        print(f"\n{'='*60}")
        print(f"Analysis Results for {test_file}")
        print(f"{'='*60}")
        print(f"Language: {analysis.language}")
        print(f"Functions: {len(analysis.symbol_info.functions)}")
        print(f"Classes: {len(analysis.symbol_info.classes)}")
        print(f"\nPatterns Detected: {len(analysis.patterns)}")
        
        if analysis.patterns:
            for pattern in analysis.patterns:
                print(f"  - {pattern.pattern_type}")
                print(f"    Confidence: {pattern.confidence:.2f}")
                print(f"    Evidence: {', '.join(pattern.evidence[:3])}")
        else:
            print("  (No patterns detected)")
        
        print(f"\nTeaching Value Score: {analysis.teaching_value.total_score:.3f}")
        print(f"  Documentation: {analysis.teaching_value.documentation_score:.3f}")
        print(f"  Complexity: {analysis.teaching_value.complexity_score:.3f}")
        print(f"  Pattern: {analysis.teaching_value.pattern_score:.3f} ← Should be non-zero!")
        print(f"  Structure: {analysis.teaching_value.structure_score:.3f}")
        
        # Check if pattern score is non-zero
        if analysis.teaching_value.pattern_score > 0:
            print(f"\n✓ SUCCESS: Pattern score is {analysis.teaching_value.pattern_score:.3f} (non-zero!)")
        else:
            print(f"\n✗ ISSUE: Pattern score is still 0.0")
            print(f"  Patterns detected: {len(analysis.patterns)}")
            if analysis.patterns:
                print(f"  Pattern types: {[p.pattern_type for p in analysis.patterns]}")
        
    except Exception as e:
        print(f"\n✗ Error analyzing file: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await cache.close()


if __name__ == "__main__":
    asyncio.run(test_real_file())
