"""Test script for multi-language symbol extraction."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analysis.config import AnalysisConfig
from src.analysis.ast_parser import ASTParserManager
from src.analysis.symbol_extractor import SymbolExtractor


def test_language(language, extension, code, expected_functions=0, expected_classes=0):
    """Test symbol extraction for a specific language."""
    test_file = Path(f'test_symbols{extension}')
    test_file.write_text(code)
    
    try:
        config = AnalysisConfig()
        parser = ASTParserManager(config)
        extractor = SymbolExtractor()
        
        parse_result = parser.parse_file(str(test_file))
        symbols = extractor.extract_symbols(parse_result)
        
        print(f"\n{language.upper()}:")
        print(f"  Functions: {len(symbols.functions)} (expected: {expected_functions})")
        print(f"  Classes: {len(symbols.classes)} (expected: {expected_classes})")
        
        if symbols.functions:
            print(f"  Function names: {', '.join([f.name for f in symbols.functions])}")
        if symbols.classes:
            print(f"  Class names: {', '.join([c.name for c in symbols.classes])}")
        
        success = (len(symbols.functions) >= expected_functions and 
                  len(symbols.classes) >= expected_classes)
        
        print(f"  {'✓ PASSED' if success else '✗ FAILED'}")
        return success
        
    except Exception as e:
        print(f"\n{language.upper()}:")
        print(f"  ✗ ERROR: {e}")
        return False
    finally:
        if test_file.exists():
            test_file.unlink()


def main():
    """Run tests for all supported languages."""
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
    results.append(test_language('Python', '.py', python_code, 1, 1))
    
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

const square = (x) => x * x;
'''
    results.append(test_language('JavaScript', '.js', js_code, 2, 1))
    
    # Java
    java_code = '''
public class Calculator {
    public int add(int a, int b) {
        return a + b;
    }
}
'''
    results.append(test_language('Java', '.java', java_code, 0, 1))
    
    # Go
    go_code = '''
package main

type Calculator struct {
    result int
}

func add(a int, b int) int {
    return a + b
}
'''
    results.append(test_language('Go', '.go', go_code, 1, 0))
    
    # Rust
    rust_code = '''
struct Calculator {
    result: i32,
}

fn fibonacci(n: i32) -> i32 {
    if n <= 1 {
        n
    } else {
        fibonacci(n-1) + fibonacci(n-2)
    }
}
'''
    results.append(test_language('Rust', '.rs', rust_code, 1, 1))
    
    # C++
    cpp_code = '''
class Calculator {
public:
    int add(int a, int b) {
        return a + b;
    }
};

int fibonacci(int n) {
    if (n <= 1) return n;
    return fibonacci(n-1) + fibonacci(n-2);
}
'''
    results.append(test_language('C++', '.cpp', cpp_code, 1, 1))
    
    # C#
    csharp_code = '''
public class Calculator {
    public int Add(int a, int b) {
        return a + b;
    }
}
'''
    results.append(test_language('C#', '.cs', csharp_code, 0, 1))
    
    # Ruby
    ruby_code = '''
class Calculator
  def add(a, b)
    a + b
  end
end

def fibonacci(n)
  return n if n <= 1
  fibonacci(n-1) + fibonacci(n-2)
end
'''
    results.append(test_language('Ruby', '.rb', ruby_code, 1, 1))
    
    # PHP
    php_code = '''<?php
class Calculator {
    public function add($a, $b) {
        return $a + $b;
    }
}

function fibonacci($n) {
    if ($n <= 1) return $n;
    return fibonacci($n-1) + fibonacci($n-2);
}
?>'''
    results.append(test_language('PHP', '.php', php_code, 1, 1))
    
    # Summary
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"RESULTS: {passed}/{total} languages passed")
    print("✓ ALL TESTS PASSED!" if passed == total else f"✗ {total - passed} test(s) failed")
    print("=" * 60)
    
    return passed == total


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
