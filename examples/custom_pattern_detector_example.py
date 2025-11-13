"""
Example: Custom Pattern Detector Plugin

This example demonstrates how to create a custom pattern detector plugin
and register it with the Analysis Engine. This shows the extensibility
of the pattern detection system.
"""

import sys
from pathlib import Path
from typing import List
import re

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analysis.pattern_detector import BasePatternDetector, DetectedPattern
from src.analysis.symbol_extractor import SymbolInfo


class ErrorHandlingPatternDetector(BasePatternDetector):
    """
    Custom pattern detector that identifies error handling patterns.
    
    Detects:
    - Try-except blocks
    - Custom exception classes
    - Error logging patterns
    - Retry mechanisms
    """
    
    def detect(self, symbol_info: SymbolInfo, file_content: str, file_path: str) -> List[DetectedPattern]:
        """Detect error handling patterns in code."""
        patterns = []
        
        # Pattern 1: Try-except blocks
        try_except_count = len(re.findall(r'\btry\s*:', file_content))
        if try_except_count > 0:
            patterns.append(DetectedPattern(
                pattern_type="error_handling_try_except",
                file_path=file_path,
                confidence=min(0.9, 0.5 + (try_except_count * 0.1)),
                evidence=[
                    f"Found {try_except_count} try-except blocks",
                    "Uses exception handling for error management"
                ],
                line_numbers=[],
                metadata={
                    "try_except_count": try_except_count,
                    "pattern_category": "error_handling"
                }
            ))
        
        # Pattern 2: Custom exception classes
        custom_exceptions = [
            cls for cls in symbol_info.classes
            if any('Exception' in base or 'Error' in base for base in cls.base_classes)
        ]
        if custom_exceptions:
            patterns.append(DetectedPattern(
                pattern_type="error_handling_custom_exceptions",
                file_path=file_path,
                confidence=0.95,
                evidence=[
                    f"Defines {len(custom_exceptions)} custom exception classes",
                    f"Custom exceptions: {', '.join(e.name for e in custom_exceptions)}"
                ],
                line_numbers=[e.start_line for e in custom_exceptions],
                metadata={
                    "exception_classes": [e.name for e in custom_exceptions],
                    "pattern_category": "error_handling"
                }
            ))
        
        # Pattern 3: Error logging
        has_logging = any(
            'logging' in imp.module or 'logger' in imp.module.lower()
            for imp in symbol_info.imports
        )
        error_log_calls = len(re.findall(r'log(?:ger)?\.(?:error|exception|critical)', file_content))
        
        if has_logging and error_log_calls > 0:
            patterns.append(DetectedPattern(
                pattern_type="error_handling_logging",
                file_path=file_path,
                confidence=0.85,
                evidence=[
                    "Imports logging module",
                    f"Found {error_log_calls} error logging calls"
                ],
                line_numbers=[],
                metadata={
                    "log_calls": error_log_calls,
                    "pattern_category": "error_handling"
                }
            ))
        
        # Pattern 4: Retry mechanism
        has_retry = bool(re.search(r'@retry|@backoff|for\s+\w+\s+in\s+range.*:.*try:', file_content, re.DOTALL))
        if has_retry:
            patterns.append(DetectedPattern(
                pattern_type="error_handling_retry",
                file_path=file_path,
                confidence=0.8,
                evidence=[
                    "Implements retry mechanism",
                    "Uses decorators or loops for retrying operations"
                ],
                line_numbers=[],
                metadata={
                    "pattern_category": "error_handling"
                }
            ))
        
        return patterns


class PerformancePatternDetector(BasePatternDetector):
    """
    Custom pattern detector that identifies performance optimization patterns.
    
    Detects:
    - Caching mechanisms
    - Lazy loading
    - Memoization
    - Async/await patterns
    """
    
    def detect(self, symbol_info: SymbolInfo, file_content: str, file_path: str) -> List[DetectedPattern]:
        """Detect performance optimization patterns."""
        patterns = []
        
        # Pattern 1: Caching
        cache_imports = [
            imp for imp in symbol_info.imports
            if 'cache' in imp.module.lower() or 'lru_cache' in str(imp.imported_symbols)
        ]
        cache_decorators = [
            func for func in symbol_info.functions
            if any('cache' in dec.lower() for dec in func.decorators)
        ]
        
        if cache_imports or cache_decorators:
            patterns.append(DetectedPattern(
                pattern_type="performance_caching",
                file_path=file_path,
                confidence=0.9,
                evidence=[
                    f"Uses caching: {len(cache_decorators)} cached functions",
                    "Imports caching utilities"
                ],
                line_numbers=[f.start_line for f in cache_decorators],
                metadata={
                    "cached_functions": [f.name for f in cache_decorators],
                    "pattern_category": "performance"
                }
            ))
        
        # Pattern 2: Async/await
        async_functions = [f for f in symbol_info.functions if f.is_async]
        has_asyncio = any('asyncio' in imp.module for imp in symbol_info.imports)
        
        if async_functions or has_asyncio:
            patterns.append(DetectedPattern(
                pattern_type="performance_async",
                file_path=file_path,
                confidence=0.95,
                evidence=[
                    f"Uses async/await: {len(async_functions)} async functions",
                    "Implements asynchronous operations"
                ],
                line_numbers=[f.start_line for f in async_functions],
                metadata={
                    "async_functions": [f.name for f in async_functions],
                    "pattern_category": "performance"
                }
            ))
        
        # Pattern 3: Lazy loading
        has_lazy = bool(re.search(r'@lazy|@property.*\bif\b.*\bNone\b', file_content))
        if has_lazy:
            patterns.append(DetectedPattern(
                pattern_type="performance_lazy_loading",
                file_path=file_path,
                confidence=0.75,
                evidence=[
                    "Implements lazy loading pattern",
                    "Defers initialization until needed"
                ],
                line_numbers=[],
                metadata={
                    "pattern_category": "performance"
                }
            ))
        
        return patterns


def main():
    """Demonstrate custom pattern detector usage."""
    print("=" * 70)
    print("Custom Pattern Detector Plugin Example")
    print("=" * 70)
    
    # Example 1: Test ErrorHandlingPatternDetector
    print("\n" + "-" * 70)
    print("Example 1: Error Handling Pattern Detection")
    print("-" * 70)
    
    sample_code = """
import logging

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    \"\"\"Custom validation error.\"\"\"
    pass

class DatabaseError(Exception):
    \"\"\"Custom database error.\"\"\"
    pass

def process_data(data):
    \"\"\"Process data with error handling.\"\"\"
    try:
        validate_data(data)
        result = transform_data(data)
        return result
    except ValidationError as e:
        logger.error(f"Validation failed: {e}")
        raise
    except Exception as e:
        logger.exception("Unexpected error during processing")
        raise DatabaseError("Processing failed") from e

def validate_data(data):
    \"\"\"Validate input data.\"\"\"
    if not data:
        raise ValidationError("Data cannot be empty")
"""
    
    # Create mock symbol info
    from src.analysis.symbol_extractor import FunctionInfo, ClassInfo, ImportInfo
    
    symbol_info = SymbolInfo(
        functions=[
            FunctionInfo(name="process_data", parameters=["data"], start_line=11, end_line=22),
            FunctionInfo(name="validate_data", parameters=["data"], start_line=24, end_line=27)
        ],
        classes=[
            ClassInfo(name="ValidationError", base_classes=["Exception"], start_line=5, end_line=7),
            ClassInfo(name="DatabaseError", base_classes=["Exception"], start_line=9, end_line=11)
        ],
        imports=[
            ImportInfo(module="logging", line_number=1)
        ]
    )
    
    # Detect patterns
    detector = ErrorHandlingPatternDetector()
    patterns = detector.detect(symbol_info, sample_code, "example.py")
    
    print(f"\nDetected {len(patterns)} error handling patterns:\n")
    for pattern in patterns:
        print(f"  Pattern: {pattern.pattern_type}")
        print(f"  Confidence: {pattern.confidence:.2f}")
        print(f"  Evidence:")
        for evidence in pattern.evidence:
            print(f"    - {evidence}")
        print(f"  Metadata: {pattern.metadata}")
        print()
    
    # Example 2: Test PerformancePatternDetector
    print("-" * 70)
    print("Example 2: Performance Pattern Detection")
    print("-" * 70)
    
    sample_code2 = """
import asyncio
from functools import lru_cache

@lru_cache(maxsize=128)
def fibonacci(n):
    \"\"\"Calculate fibonacci number with caching.\"\"\"
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

async def fetch_data(url):
    \"\"\"Fetch data asynchronously.\"\"\"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

async def process_urls(urls):
    \"\"\"Process multiple URLs concurrently.\"\"\"
    tasks = [fetch_data(url) for url in urls]
    results = await asyncio.gather(*tasks)
    return results
"""
    
    symbol_info2 = SymbolInfo(
        functions=[
            FunctionInfo(
                name="fibonacci",
                parameters=["n"],
                start_line=4,
                end_line=9,
                decorators=["@lru_cache(maxsize=128)"]
            ),
            FunctionInfo(
                name="fetch_data",
                parameters=["url"],
                start_line=11,
                end_line=15,
                is_async=True
            ),
            FunctionInfo(
                name="process_urls",
                parameters=["urls"],
                start_line=17,
                end_line=21,
                is_async=True
            )
        ],
        imports=[
            ImportInfo(module="asyncio", line_number=1),
            ImportInfo(module="functools", imported_symbols=["lru_cache"], line_number=2)
        ]
    )
    
    detector2 = PerformancePatternDetector()
    patterns2 = detector2.detect(symbol_info2, sample_code2, "example2.py")
    
    print(f"\nDetected {len(patterns2)} performance patterns:\n")
    for pattern in patterns2:
        print(f"  Pattern: {pattern.pattern_type}")
        print(f"  Confidence: {pattern.confidence:.2f}")
        print(f"  Evidence:")
        for evidence in pattern.evidence:
            print(f"    - {evidence}")
        print(f"  Metadata: {pattern.metadata}")
        print()
    
    # Example 3: Registering custom detectors
    print("-" * 70)
    print("Example 3: Registering Custom Detectors")
    print("-" * 70)
    
    from src.analysis.pattern_detector import PatternDetector
    
    # Create pattern detector and register custom detectors
    pattern_detector = PatternDetector()
    pattern_detector.register_detector(ErrorHandlingPatternDetector())
    pattern_detector.register_detector(PerformancePatternDetector())
    
    print(f"\n✓ Registered {len(pattern_detector.detectors)} pattern detectors:")
    for detector in pattern_detector.detectors:
        print(f"  - {detector.__class__.__name__}")
    
    # Detect all patterns in a file
    all_patterns = pattern_detector.detect_patterns_in_file(
        symbol_info2, sample_code2, "example2.py"
    )
    
    print(f"\n✓ Detected {len(all_patterns)} total patterns")
    
    print("\n" + "=" * 70)
    print("Example complete!")
    print("=" * 70)
    print("\nKey Takeaways:")
    print("  1. Extend BasePatternDetector to create custom detectors")
    print("  2. Implement the detect() method with your pattern logic")
    print("  3. Return DetectedPattern objects with confidence scores")
    print("  4. Register detectors with PatternDetector.register_detector()")
    print("  5. Custom detectors integrate seamlessly with the engine")


if __name__ == "__main__":
    main()
