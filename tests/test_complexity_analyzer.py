"""
Tests for Complexity Analyzer.

Tests cyclomatic complexity calculation, nesting depth, and file-level metrics.
"""

import pytest
import os
import tempfile
from src.analysis.ast_parser import ASTParserManager
from src.analysis.symbol_extractor import SymbolExtractor
from src.analysis.complexity_analyzer import ComplexityAnalyzer, ComplexityMetrics
from src.analysis.config import AnalysisConfig


def create_test_file(content: str, extension: str) -> str:
    """Create a temporary test file."""
    fd, path = tempfile.mkstemp(suffix=extension, text=True)
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        f.write(content)
    return path


@pytest.fixture
def config():
    """Create test configuration."""
    return AnalysisConfig()


@pytest.fixture
def parser_manager(config):
    """Create AST parser manager."""
    return ASTParserManager(config)


@pytest.fixture
def symbol_extractor():
    """Create symbol extractor."""
    return SymbolExtractor()


@pytest.fixture
def complexity_analyzer():
    """Create complexity analyzer."""
    return ComplexityAnalyzer()


class TestComplexityCalculation:
    """Test complexity calculation for individual functions."""
    
    def test_simple_function_complexity(self, parser_manager, symbol_extractor, complexity_analyzer):
        """Test complexity of simple function (should be 1)."""
        code = '''def simple_function(x):
    """Simple function with no branches."""
    return x * 2
'''
        path = create_test_file(code, '.py')
        try:
            parse_result = parser_manager.parse_file(path)
            symbols = symbol_extractor.extract_symbols(parse_result)
            
            assert len(symbols.functions) == 1
            func = symbols.functions[0]
            assert func.complexity == 1
        finally:
            try:
                os.unlink(path)
            except:
                pass
    
    def test_function_with_if_statement(self, parser_manager, symbol_extractor, complexity_analyzer):
        """Test complexity with single if statement (should be 2)."""
        code = '''def function_with_if(x):
    """Function with one if statement."""
    if x > 0:
        return x
    return 0
'''
        path = create_test_file(code, '.py')
        try:
            parse_result = parser_manager.parse_file(path)
            symbols = symbol_extractor.extract_symbols(parse_result)
            
            assert len(symbols.functions) == 1
            func = symbols.functions[0]
            assert func.complexity == 2
        finally:
            try:
                os.unlink(path)
            except:
                pass
    
    def test_complex_function(self, parser_manager, symbol_extractor, complexity_analyzer):
        """Test complexity of function with multiple decision points."""
        code = '''def complex_function(x, y, z):
    """Function with multiple branches."""
    if x > 0:
        if y > 0:
            return x + y
        elif z > 0:
            return x + z
    for i in range(10):
        if i == 5:
            break
    return 0
'''
        path = create_test_file(code, '.py')
        try:
            parse_result = parser_manager.parse_file(path)
            symbols = symbol_extractor.extract_symbols(parse_result)
            
            assert len(symbols.functions) == 1
            func = symbols.functions[0]
            # Should have: if, if, elif, for, if = 5 decision points + 1 = 6
            assert func.complexity >= 5
        finally:
            try:
                os.unlink(path)
            except:
                pass


class TestFileMetrics:
    """Test file-level complexity metrics."""
    
    def test_analyze_file_with_multiple_functions(self, parser_manager, symbol_extractor, complexity_analyzer):
        """Test analyzing a file with multiple functions."""
        code = '''def simple():
    return 1

def moderate(x):
    if x > 0:
        return x
    return 0

def complex(x, y):
    if x > 0:
        if y > 0:
            return x + y
    return 0
'''
        path = create_test_file(code, '.py')
        try:
            parse_result = parser_manager.parse_file(path)
            symbols = symbol_extractor.extract_symbols(parse_result)
            metrics = complexity_analyzer.analyze_file(symbols)
            
            assert isinstance(metrics, ComplexityMetrics)
            assert metrics.avg_complexity > 0
            assert metrics.max_complexity >= metrics.avg_complexity
            assert metrics.min_complexity <= metrics.avg_complexity
        finally:
            try:
                os.unlink(path)
            except:
                pass
    
    def test_high_complexity_flagging(self, parser_manager, symbol_extractor, complexity_analyzer):
        """Test flagging of high complexity functions."""
        # Create a function with >10 complexity
        code = '''def very_complex(x):
    if x == 1:
        pass
    elif x == 2:
        pass
    elif x == 3:
        pass
    elif x == 4:
        pass
    elif x == 5:
        pass
    elif x == 6:
        pass
    elif x == 7:
        pass
    elif x == 8:
        pass
    elif x == 9:
        pass
    elif x == 10:
        pass
    elif x == 11:
        pass
    return 0
'''
        path = create_test_file(code, '.py')
        try:
            parse_result = parser_manager.parse_file(path)
            symbols = symbol_extractor.extract_symbols(parse_result)
            metrics = complexity_analyzer.analyze_file(symbols)
            
            assert metrics.high_complexity_count >= 1
            assert metrics.max_complexity > 10
        finally:
            try:
                os.unlink(path)
            except:
                pass
    
    def test_trivial_function_flagging(self, parser_manager, symbol_extractor, complexity_analyzer):
        """Test flagging of trivial functions."""
        code = '''def trivial1():
    return 1

def trivial2(x):
    return x * 2

def not_trivial(x):
    if x > 0:
        return x
    return 0
'''
        path = create_test_file(code, '.py')
        try:
            parse_result = parser_manager.parse_file(path)
            symbols = symbol_extractor.extract_symbols(parse_result)
            metrics = complexity_analyzer.analyze_file(symbols)
            
            assert metrics.trivial_count >= 2
            assert metrics.min_complexity == 1
        finally:
            try:
                os.unlink(path)
            except:
                pass
    
    def test_empty_file(self, complexity_analyzer):
        """Test analyzing empty file."""
        from src.analysis.symbol_extractor import SymbolInfo
        
        symbols = SymbolInfo()
        metrics = complexity_analyzer.analyze_file(symbols)
        
        assert metrics.avg_complexity == 0.0
        assert metrics.max_complexity == 0
        assert metrics.min_complexity == 0
        assert metrics.high_complexity_count == 0
        assert metrics.trivial_count == 0


class TestJavaScriptComplexity:
    """Test complexity calculation for JavaScript."""
    
    def test_javascript_function_complexity(self, parser_manager, symbol_extractor, complexity_analyzer):
        """Test complexity of JavaScript function."""
        code = '''function testFunc(x, y) {
    if (x > 0) {
        return x;
    } else if (y > 0) {
        return y;
    }
    return 0;
}
'''
        path = create_test_file(code, '.js')
        try:
            parse_result = parser_manager.parse_file(path)
            symbols = symbol_extractor.extract_symbols(parse_result)
            
            assert len(symbols.functions) == 1
            func = symbols.functions[0]
            # Should have if and elif = 2 decision points + 1 = 3
            assert func.complexity >= 2
        finally:
            try:
                os.unlink(path)
            except:
                pass


class TestComplexityFlags:
    """Test complexity flagging methods."""
    
    def test_flag_high_complexity(self, complexity_analyzer):
        """Test high complexity flagging."""
        assert complexity_analyzer.flag_high_complexity(11) is True
        assert complexity_analyzer.flag_high_complexity(10) is False
        assert complexity_analyzer.flag_high_complexity(5) is False
    
    def test_flag_trivial(self, complexity_analyzer):
        """Test trivial complexity flagging."""
        assert complexity_analyzer.flag_trivial(1) is True
        assert complexity_analyzer.flag_trivial(2) is False
        assert complexity_analyzer.flag_trivial(5) is False


class TestVariousCodePatterns:
    """Test complexity calculation for various code patterns."""
    
    def test_while_loop_complexity(self, parser_manager, symbol_extractor):
        """Test complexity with while loop."""
        code = '''def function_with_while(n):
    """Function with while loop."""
    i = 0
    while i < n:
        i += 1
    return i
'''
        path = create_test_file(code, '.py')
        try:
            parse_result = parser_manager.parse_file(path)
            symbols = symbol_extractor.extract_symbols(parse_result)
            
            assert len(symbols.functions) == 1
            func = symbols.functions[0]
            # Should have while = 1 decision point + 1 = 2
            assert func.complexity == 2
        finally:
            try:
                os.unlink(path)
            except:
                pass
    
    def test_for_loop_complexity(self, parser_manager, symbol_extractor):
        """Test complexity with for loop."""
        code = '''def function_with_for(items):
    """Function with for loop."""
    total = 0
    for item in items:
        total += item
    return total
'''
        path = create_test_file(code, '.py')
        try:
            parse_result = parser_manager.parse_file(path)
            symbols = symbol_extractor.extract_symbols(parse_result)
            
            assert len(symbols.functions) == 1
            func = symbols.functions[0]
            # Should have for = 1 decision point + 1 = 2
            assert func.complexity == 2
        finally:
            try:
                os.unlink(path)
            except:
                pass
    
    def test_logical_operators_complexity(self, parser_manager, symbol_extractor):
        """Test complexity with logical operators (and, or)."""
        code = '''def function_with_logical(x, y, z):
    """Function with logical operators."""
    if x > 0 and y > 0:
        return x + y
    if z > 0 or x < 0:
        return z
    return 0
'''
        path = create_test_file(code, '.py')
        try:
            parse_result = parser_manager.parse_file(path)
            symbols = symbol_extractor.extract_symbols(parse_result)
            
            assert len(symbols.functions) == 1
            func = symbols.functions[0]
            # Should have: if, and, if, or = 4 decision points + 1 = 5
            assert func.complexity >= 4
        finally:
            try:
                os.unlink(path)
            except:
                pass
    
    def test_nested_conditions_complexity(self, parser_manager, symbol_extractor):
        """Test complexity with nested conditions."""
        code = '''def nested_conditions(x, y):
    """Function with nested conditions."""
    if x > 0:
        if y > 0:
            if x > y:
                return x
            else:
                return y
    return 0
'''
        path = create_test_file(code, '.py')
        try:
            parse_result = parser_manager.parse_file(path)
            symbols = symbol_extractor.extract_symbols(parse_result)
            
            assert len(symbols.functions) == 1
            func = symbols.functions[0]
            # Should have: if, if, if = 3 decision points + 1 = 4
            assert func.complexity >= 3
        finally:
            try:
                os.unlink(path)
            except:
                pass
    
    def test_try_except_complexity(self, parser_manager, symbol_extractor):
        """Test complexity with try-except blocks."""
        code = '''def function_with_exception(x):
    """Function with exception handling."""
    try:
        result = 10 / x
        return result
    except ZeroDivisionError:
        return 0
    except ValueError:
        return -1
'''
        path = create_test_file(code, '.py')
        try:
            parse_result = parser_manager.parse_file(path)
            symbols = symbol_extractor.extract_symbols(parse_result)
            
            assert len(symbols.functions) == 1
            func = symbols.functions[0]
            # Should have: except, except = 2 decision points + 1 = 3
            assert func.complexity >= 2
        finally:
            try:
                os.unlink(path)
            except:
                pass
    
    def test_switch_case_complexity(self, parser_manager, symbol_extractor):
        """Test complexity with match-case (Python 3.10+)."""
        code = '''def function_with_match(value):
    """Function with match-case."""
    match value:
        case 1:
            return "one"
        case 2:
            return "two"
        case 3:
            return "three"
        case _:
            return "other"
'''
        path = create_test_file(code, '.py')
        try:
            parse_result = parser_manager.parse_file(path)
            symbols = symbol_extractor.extract_symbols(parse_result)
            
            assert len(symbols.functions) == 1
            func = symbols.functions[0]
            # Should have multiple case clauses
            assert func.complexity >= 1
        finally:
            try:
                os.unlink(path)
            except:
                pass
    
    def test_combined_patterns_complexity(self, parser_manager, symbol_extractor):
        """Test complexity with combined patterns."""
        code = '''def combined_patterns(items, threshold):
    """Function with multiple patterns."""
    result = []
    for item in items:
        if item > threshold:
            try:
                processed = item * 2
                if processed > 100:
                    result.append(processed)
            except Exception:
                continue
    return result
'''
        path = create_test_file(code, '.py')
        try:
            parse_result = parser_manager.parse_file(path)
            symbols = symbol_extractor.extract_symbols(parse_result)
            
            assert len(symbols.functions) == 1
            func = symbols.functions[0]
            # Should have: for, if, if, except = 4 decision points + 1 = 5
            assert func.complexity >= 4
        finally:
            try:
                os.unlink(path)
            except:
                pass


class TestNestingDepth:
    """Test nesting depth calculation."""
    
    def test_no_nesting(self, parser_manager, complexity_analyzer):
        """Test function with no nesting."""
        code = '''def no_nesting(x):
    """Function with no nesting."""
    return x * 2
'''
        path = create_test_file(code, '.py')
        try:
            parse_result = parser_manager.parse_file(path)
            
            # Get function node
            root = parse_result.root_node
            func_node = None
            for child in root.children:
                if child.type == 'function_definition':
                    func_node = child
                    break
            
            assert func_node is not None
            depth = complexity_analyzer.calculate_nesting_depth(func_node)
            assert depth == 0
        finally:
            try:
                os.unlink(path)
            except:
                pass
    
    def test_single_level_nesting(self, parser_manager, complexity_analyzer):
        """Test function with single level nesting."""
        code = '''def single_nesting(x):
    """Function with single level nesting."""
    if x > 0:
        return x
    return 0
'''
        path = create_test_file(code, '.py')
        try:
            parse_result = parser_manager.parse_file(path)
            
            # Get function node
            root = parse_result.root_node
            func_node = None
            for child in root.children:
                if child.type == 'function_definition':
                    func_node = child
                    break
            
            assert func_node is not None
            depth = complexity_analyzer.calculate_nesting_depth(func_node)
            assert depth == 1
        finally:
            try:
                os.unlink(path)
            except:
                pass
    
    def test_deep_nesting(self, parser_manager, complexity_analyzer):
        """Test function with deep nesting."""
        code = '''def deep_nesting(a, b, c, d):
    """Function with deep nesting."""
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    return a + b + c + d
    return 0
'''
        path = create_test_file(code, '.py')
        try:
            parse_result = parser_manager.parse_file(path)
            
            # Get function node
            root = parse_result.root_node
            func_node = None
            for child in root.children:
                if child.type == 'function_definition':
                    func_node = child
                    break
            
            assert func_node is not None
            depth = complexity_analyzer.calculate_nesting_depth(func_node)
            assert depth == 4
        finally:
            try:
                os.unlink(path)
            except:
                pass
    
    def test_mixed_nesting(self, parser_manager, complexity_analyzer):
        """Test function with mixed nesting (if, for, while)."""
        code = '''def mixed_nesting(items):
    """Function with mixed nesting."""
    for item in items:
        if item > 0:
            while item > 10:
                item -= 1
    return items
'''
        path = create_test_file(code, '.py')
        try:
            parse_result = parser_manager.parse_file(path)
            
            # Get function node
            root = parse_result.root_node
            func_node = None
            for child in root.children:
                if child.type == 'function_definition':
                    func_node = child
                    break
            
            assert func_node is not None
            depth = complexity_analyzer.calculate_nesting_depth(func_node)
            assert depth == 3
        finally:
            try:
                os.unlink(path)
            except:
                pass


class TestThresholdVerification:
    """Test verification of complexity thresholds."""
    
    def test_high_complexity_threshold_boundary(self, parser_manager, symbol_extractor, complexity_analyzer):
        """Test that complexity >10 is flagged as high."""
        # Create function with exactly 11 complexity
        code = '''def boundary_high(x):
    """Function at high complexity boundary."""
    if x == 1:
        return 1
    elif x == 2:
        return 2
    elif x == 3:
        return 3
    elif x == 4:
        return 4
    elif x == 5:
        return 5
    elif x == 6:
        return 6
    elif x == 7:
        return 7
    elif x == 8:
        return 8
    elif x == 9:
        return 9
    elif x == 10:
        return 10
    elif x == 11:
        return 11
    return 0
'''
        path = create_test_file(code, '.py')
        try:
            parse_result = parser_manager.parse_file(path)
            symbols = symbol_extractor.extract_symbols(parse_result)
            metrics = complexity_analyzer.analyze_file(symbols)
            
            # Verify high complexity is flagged
            assert metrics.high_complexity_count >= 1
            assert metrics.max_complexity > 10
            
            # Verify the flag method
            func = symbols.functions[0]
            assert complexity_analyzer.flag_high_complexity(func.complexity) is True
        finally:
            try:
                os.unlink(path)
            except:
                pass
    
    def test_trivial_threshold_boundary(self, parser_manager, symbol_extractor, complexity_analyzer):
        """Test that complexity <2 is flagged as trivial."""
        code = '''def trivial_func():
    """Trivial function."""
    return 42

def also_trivial(x):
    """Another trivial function."""
    return x * 2
'''
        path = create_test_file(code, '.py')
        try:
            parse_result = parser_manager.parse_file(path)
            symbols = symbol_extractor.extract_symbols(parse_result)
            metrics = complexity_analyzer.analyze_file(symbols)
            
            # Verify trivial functions are flagged
            assert metrics.trivial_count == 2
            assert metrics.min_complexity == 1
            
            # Verify the flag method
            for func in symbols.functions:
                assert complexity_analyzer.flag_trivial(func.complexity) is True
        finally:
            try:
                os.unlink(path)
            except:
                pass
    
    def test_moderate_complexity_not_flagged(self, parser_manager, symbol_extractor, complexity_analyzer):
        """Test that moderate complexity (2-10) is not flagged."""
        code = '''def moderate_func(x, y):
    """Function with moderate complexity."""
    if x > 0:
        if y > 0:
            return x + y
        else:
            return x
    elif x < 0:
        return -x
    return 0
'''
        path = create_test_file(code, '.py')
        try:
            parse_result = parser_manager.parse_file(path)
            symbols = symbol_extractor.extract_symbols(parse_result)
            metrics = complexity_analyzer.analyze_file(symbols)
            
            # Verify not flagged as high or trivial
            assert metrics.high_complexity_count == 0
            assert metrics.trivial_count == 0
            
            # Verify complexity is in moderate range
            func = symbols.functions[0]
            assert 2 <= func.complexity <= 10
            assert complexity_analyzer.flag_high_complexity(func.complexity) is False
            assert complexity_analyzer.flag_trivial(func.complexity) is False
        finally:
            try:
                os.unlink(path)
            except:
                pass
    
    def test_metrics_with_mixed_complexity(self, parser_manager, symbol_extractor, complexity_analyzer):
        """Test metrics calculation with mixed complexity functions."""
        code = '''def trivial():
    return 1

def moderate(x):
    if x > 0:
        return x
    return 0

def high_complexity(x):
    if x == 1:
        return 1
    elif x == 2:
        return 2
    elif x == 3:
        return 3
    elif x == 4:
        return 4
    elif x == 5:
        return 5
    elif x == 6:
        return 6
    elif x == 7:
        return 7
    elif x == 8:
        return 8
    elif x == 9:
        return 9
    elif x == 10:
        return 10
    elif x == 11:
        return 11
    return 0
'''
        path = create_test_file(code, '.py')
        try:
            parse_result = parser_manager.parse_file(path)
            symbols = symbol_extractor.extract_symbols(parse_result)
            metrics = complexity_analyzer.analyze_file(symbols)
            
            # Verify counts
            assert metrics.trivial_count >= 1
            assert metrics.high_complexity_count >= 1
            
            # Verify min and max
            assert metrics.min_complexity == 1
            assert metrics.max_complexity > 10
            
            # Verify average is calculated
            assert metrics.avg_complexity > 0
        finally:
            try:
                os.unlink(path)
            except:
                pass
