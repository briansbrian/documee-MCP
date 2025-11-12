"""
Test script for symbol extraction.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analysis.config import AnalysisConfig
from src.analysis.ast_parser import ASTParserManager
from src.analysis.symbol_extractor import SymbolExtractor


def test_python_extraction():
    """Test Python symbol extraction."""
    # Create test file
    test_code = '''
"""Module docstring."""

import os
from typing import List, Optional

class Calculator:
    """A simple calculator class."""
    
    def __init__(self):
        """Initialize calculator."""
        self.result = 0
    
    def add(self, a: int, b: int) -> int:
        """Add two numbers."""
        if a > 0 and b > 0:
            return a + b
        return 0

def fibonacci(n: int) -> int:
    """Calculate fibonacci number."""
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)

async def fetch_data(url: str) -> Optional[str]:
    """Fetch data from URL."""
    for attempt in range(3):
        if attempt > 0:
            print(f"Retry {attempt}")
    return None
'''
    
    # Write test file
    test_file = Path('test_symbols.py')
    test_file.write_text(test_code)
    
    try:
        # Parse and extract
        config = AnalysisConfig()
        parser = ASTParserManager(config)
        extractor = SymbolExtractor()
        
        parse_result = parser.parse_file(str(test_file))
        symbols = extractor.extract_symbols(parse_result)
        
        # Print results
        print("=" * 60)
        print("SYMBOL EXTRACTION TEST")
        print("=" * 60)
        
        print(f"\nImports: {len(symbols.imports)}")
        for imp in symbols.imports:
            print(f"  - {imp.import_type}: {imp.module}")
            if imp.imported_symbols:
                print(f"    Symbols: {', '.join(imp.imported_symbols)}")
        
        print(f"\nClasses: {len(symbols.classes)}")
        for cls in symbols.classes:
            print(f"  - {cls.name} (lines {cls.start_line}-{cls.end_line})")
            print(f"    Docstring: {cls.docstring[:50] if cls.docstring else 'None'}...")
            print(f"    Methods: {len(cls.methods)}")
            for method in cls.methods:
                print(f"      - {method.name}({', '.join(method.parameters)})")
                print(f"        Complexity: {method.complexity}")
        
        print(f"\nFunctions: {len(symbols.functions)}")
        for func in symbols.functions:
            print(f"  - {func.name}({', '.join(func.parameters)})")
            print(f"    Lines: {func.start_line}-{func.end_line}")
            print(f"    Return type: {func.return_type}")
            print(f"    Complexity: {func.complexity}")
            print(f"    Async: {func.is_async}")
            print(f"    Docstring: {func.docstring[:50] if func.docstring else 'None'}...")
        
        print("\n" + "=" * 60)
        print("TEST PASSED!")
        print("=" * 60)
        
    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()


if __name__ == '__main__':
    test_python_extraction()
