"""
Example demonstrating the Complexity Analyzer.

This example shows how to:
1. Parse a Python file
2. Extract symbols
3. Analyze complexity metrics
4. Flag high complexity and trivial functions
"""

import sys
import os
import tempfile

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.analysis.ast_parser import ASTParserManager
from src.analysis.symbol_extractor import SymbolExtractor
from src.analysis.complexity_analyzer import ComplexityAnalyzer
from src.analysis.config import AnalysisConfig


def main():
    """Run complexity analysis example."""
    
    # Sample code with varying complexity
    sample_code = '''
def simple_function(x):
    """A simple function with no branches."""
    return x * 2

def moderate_function(x, y):
    """A function with moderate complexity."""
    if x > 0:
        if y > 0:
            return x + y
        return x
    return 0

def complex_function(a, b, c, d):
    """A complex function with many branches."""
    result = 0
    
    if a > 0:
        result += a
    elif a < 0:
        result -= a
    
    if b > 0:
        result += b
    elif b < 0:
        result -= b
    
    for i in range(10):
        if i % 2 == 0:
            result += i
        else:
            result -= i
    
    while c > 0:
        result += c
        c -= 1
    
    if d and result > 0:
        return result
    
    return 0

class Calculator:
    """A simple calculator class."""
    
    def add(self, x, y):
        """Add two numbers."""
        return x + y
    
    def divide(self, x, y):
        """Divide with error handling."""
        if y == 0:
            return None
        return x / y
'''
    
    # Create temporary file
    fd, path = tempfile.mkstemp(suffix='.py', text=True)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(sample_code)
        
        # Initialize components
        config = AnalysisConfig()
        parser = ASTParserManager(config)
        extractor = SymbolExtractor()
        analyzer = ComplexityAnalyzer()
        
        print("=" * 70)
        print("Complexity Analyzer Example")
        print("=" * 70)
        
        # Parse file
        print("\n1. Parsing file...")
        parse_result = parser.parse_file(path)
        print(f"   Language: {parse_result.language}")
        print(f"   Parse time: {parse_result.parse_time_ms:.2f}ms")
        
        # Extract symbols
        print("\n2. Extracting symbols...")
        symbols = extractor.extract_symbols(parse_result)
        print(f"   Functions: {len(symbols.functions)}")
        print(f"   Classes: {len(symbols.classes)}")
        
        # Analyze complexity
        print("\n3. Analyzing complexity...")
        metrics = analyzer.analyze_file(symbols)
        
        print(f"\n   File Metrics:")
        print(f"   - Average complexity: {metrics.avg_complexity}")
        print(f"   - Max complexity: {metrics.max_complexity}")
        print(f"   - Min complexity: {metrics.min_complexity}")
        print(f"   - High complexity functions: {metrics.high_complexity_count}")
        print(f"   - Trivial functions: {metrics.trivial_count}")
        print(f"   - Total decision points: {metrics.total_decision_points}")
        
        # Show individual function complexities
        print("\n4. Individual Function Complexities:")
        for func in symbols.functions:
            flag = ""
            if analyzer.flag_high_complexity(func.complexity):
                flag = " [HIGH COMPLEXITY]"
            elif analyzer.flag_trivial(func.complexity):
                flag = " [TRIVIAL]"
            
            print(f"   - {func.name}: {func.complexity}{flag}")
        
        # Show class method complexities
        if symbols.classes:
            print("\n5. Class Method Complexities:")
            for cls in symbols.classes:
                print(f"   Class: {cls.name}")
                for method in cls.methods:
                    flag = ""
                    if analyzer.flag_high_complexity(method.complexity):
                        flag = " [HIGH COMPLEXITY]"
                    elif analyzer.flag_trivial(method.complexity):
                        flag = " [TRIVIAL]"
                    
                    print(f"     - {method.name}: {method.complexity}{flag}")
        
        print("\n" + "=" * 70)
        print("Analysis complete!")
        print("=" * 70)
        
    finally:
        # Clean up
        try:
            os.unlink(path)
        except:
            pass


if __name__ == '__main__':
    main()
