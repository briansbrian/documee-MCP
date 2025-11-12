"""
Test script for multi-language symbol extraction.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analysis.config import AnalysisConfig
from src.analysis.ast_parser import ASTParserManager
from src.analysis.symbol_extractor import SymbolExtractor


def test_language(language, extension, code):
    """Test symbol extraction for a language."""
    test_file = Path(f'test_symbols{extension}')
    test_file.write_text(code)
    
    try:
        config = AnalysisConfig()
        parser = ASTParserManager(config)
        extractor = SymbolExtractor()
        
        parse_result = parser.parse_file(str(test_file))
        symbols = extractor.extract_symbols(parse_result)
        
        print(f"\n{language}:")
        print(f"  Functions: {len(symbols.functions)}")
        print(f"  Classes: {len(symbols.classes)}")
        print(f"  ✓ PASSED")
        return True
    
    except Exception as e:
        print(f"\n{language}:")
        print(f"  ✗ ERROR: {e}")
        return False
    
    finally:
        if test_file.exists():
            test_file.unlink()


def main():
    """Test all supported languages."""
    print("=" * 60)
    print("MULTI-LANGUAGE SYMBOL EXTRACTION TEST")
    print("=" * 60)
    
    results = []
    
    # Python
    python_code = '''
class Calculator:
    def add(self, a, b):
        return a + b

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
'''
    results.append(test_language("Python", ".py", python_code))
    
    # JavaScript
    js_code = '''
class Calculator {
    add(a, b) {
        return a + b;
    }
}

function fibonacci(n) {
    if (n <= 1) return n;
    return fibonacci(n-1) + fibonacci(n-2);
}
'''
    results.append(test_language("JavaScript", ".js", js_code))
    
    # Java
    java_code = '''
public class Calculator {
    public int add(int a, int b) {
        return a + b;
    }
}
'''
    results.append(test_language("Java", ".java", java_code))
    
    # Go
    go_code = '''
package main

func Fibonacci(n int) int {
    if n <= 1 {
        return n
    }
    return Fibonacci(n-1) + Fibonacci(n-2)
}
'''
    results.append(test_language("Go", ".go", go_code))
    
    # Rust
    rust_code = '''
fn fibonacci(n: i32) -> i32 {
    if n <= 1 {
        n
    } else {
        fibonacci(n-1) + fibonacci(n-2)
    }
}
'''
    results.append(test_language("Rust", ".rs", rust_code))
    
    # Summary
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"RESULTS: {passed}/{total} languages passed")
    print("=" * 60)


if __name__ == '__main__':
    main()
