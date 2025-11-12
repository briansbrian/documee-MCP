"""
Test script for JavaScript/TypeScript symbol extraction.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analysis.config import AnalysisConfig
from src.analysis.ast_parser import ASTParserManager
from src.analysis.symbol_extractor import SymbolExtractor


def test_javascript_extraction():
    """Test JavaScript symbol extraction."""
    # Create test file
    test_code = '''
import React, { useState, useEffect } from 'react';
import { fetchData } from './api';

/**
 * A simple calculator class
 */
class Calculator {
    /**
     * Add two numbers
     */
    add(a, b) {
        if (a > 0 && b > 0) {
            return a + b;
        }
        return 0;
    }
    
    /**
     * Subtract two numbers
     */
    subtract(a, b) {
        return a - b;
    }
}

/**
 * Calculate fibonacci number
 */
function fibonacci(n) {
    if (n <= 1) {
        return n;
    } else {
        return fibonacci(n-1) + fibonacci(n-2);
    }
}

/**
 * Fetch data from URL
 */
const fetchDataAsync = async (url) => {
    for (let i = 0; i < 3; i++) {
        if (i > 0) {
            console.log(`Retry ${i}`);
        }
    }
    return null;
};

/**
 * Process items
 */
const processItems = (items) => {
    return items.map(item => item * 2);
};

export { Calculator, fibonacci, fetchDataAsync };
export default processItems;
'''
    
    # Write test file
    test_file = Path('test_symbols.js')
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
        print("JAVASCRIPT SYMBOL EXTRACTION TEST")
        print("=" * 60)
        
        print(f"\nImports: {len(symbols.imports)}")
        for imp in symbols.imports:
            print(f"  - {imp.import_type}: {imp.module}")
            if imp.imported_symbols:
                print(f"    Symbols: {', '.join(imp.imported_symbols)}")
        
        print(f"\nExports: {len(symbols.exports)}")
        for exp in symbols.exports:
            print(f"  - {exp}")
        
        print(f"\nClasses: {len(symbols.classes)}")
        for cls in symbols.classes:
            print(f"  - {cls.name} (lines {cls.start_line}-{cls.end_line})")
            print(f"    Docstring: {cls.docstring[:50] if cls.docstring else 'None'}...")
            print(f"    Methods: {len(cls.methods)}")
            for method in cls.methods:
                print(f"      - {method.name}({', '.join(method.parameters)})")
                print(f"        Complexity: {method.complexity}")
                print(f"        Docstring: {method.docstring[:30] if method.docstring else 'None'}...")
        
        print(f"\nFunctions: {len(symbols.functions)}")
        for func in symbols.functions:
            print(f"  - {func.name}({', '.join(func.parameters)})")
            print(f"    Lines: {func.start_line}-{func.end_line}")
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
    test_javascript_extraction()
