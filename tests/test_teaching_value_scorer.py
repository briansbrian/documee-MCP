"""
Tests for Teaching Value Scorer.

Tests scoring for well-documented code, poorly documented code,
overly complex code, and score consistency.
"""

import pytest
import os
import tempfile
from src.analysis.ast_parser import ASTParserManager
from src.analysis.symbol_extractor import SymbolExtractor
from src.analysis.complexity_analyzer import ComplexityAnalyzer
from src.analysis.documentation_coverage import DocumentationCoverageAnalyzer
from src.analysis.teaching_value_scorer import TeachingValueScorer, TeachingValueScore
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


@pytest.fixture
def doc_coverage_analyzer():
    """Create documentation coverage analyzer."""
    return DocumentationCoverageAnalyzer()


@pytest.fixture
def teaching_value_scorer(config):
    """Create teaching value scorer."""
    return TeachingValueScorer(config)


class TestWellDocumentedCode:
    """Test scoring for well-documented, moderate complexity code."""
    
    def test_well_documented_moderate_complexity(
        self,
        parser_manager,
        symbol_extractor,
        complexity_analyzer,
        doc_coverage_analyzer,
        teaching_value_scorer
    ):
        """Test scoring for ideal teaching code: well-documented with moderate complexity."""
        code = '''def calculate_average(numbers):
    """
    Calculate the average of a list of numbers.
    
    Args:
        numbers: List of numbers to average
    
    Returns:
        Average value as float
    """
    if not numbers:
        return 0.0
    
    total = 0
    for num in numbers:
        total += num
    
    return total / len(numbers)


class Calculator:
    """A simple calculator class for basic operations."""
    
    def add(self, a, b):
        """Add two numbers."""
        return a + b
    
    def subtract(self, a, b):
        """Subtract b from a."""
        return a - b
    
    def multiply(self, a, b):
        """Multiply two numbers."""
        if a == 0 or b == 0:
            return 0
        return a * b
'''
        path = create_test_file(code, '.py')
        try:
            # Parse and extract symbols
            parse_result = parser_manager.parse_file(path)
            symbols = symbol_extractor.extract_symbols(parse_result)
            
            # Calculate metrics
            complexity_metrics = complexity_analyzer.analyze_file(symbols)
            
            # Read file content for documentation analysis
            with open(path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            doc_coverage = doc_coverage_analyzer.calculate_coverage(
                symbols, file_content, 'python'
            )
            
            # Score teaching value
            score = teaching_value_scorer.score_file(
                symbols, [], complexity_metrics, doc_coverage
            )
            
            # Assertions
            assert score.total_score >= 0.65, "Well-documented moderate complexity should score high"
            assert score.documentation_score >= 0.8, "Should have high documentation score"
            assert score.complexity_score >= 0.7, "Should have good complexity score"
            assert "Excellent" in score.explanation or "Good" in score.explanation
            assert score.factors['documentation']['coverage'] > 0.8
            
        finally:
            try:
                os.unlink(path)
            except:
                pass


class TestPoorlyDocumentedCode:
    """Test scoring for poorly documented code."""
    
    def test_no_documentation(
        self,
        parser_manager,
        symbol_extractor,
        complexity_analyzer,
        doc_coverage_analyzer,
        teaching_value_scorer
    ):
        """Test scoring for code with no documentation."""
        code = '''def process_data(data):
    if not data:
        return None
    
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    
    return result


class DataProcessor:
    def __init__(self):
        self.data = []
    
    def add(self, item):
        self.data.append(item)
    
    def process(self):
        return [x * 2 for x in self.data if x > 0]
'''
        path = create_test_file(code, '.py')
        try:
            # Parse and extract symbols
            parse_result = parser_manager.parse_file(path)
            symbols = symbol_extractor.extract_symbols(parse_result)
            
            # Calculate metrics
            complexity_metrics = complexity_analyzer.analyze_file(symbols)
            
            # Read file content
            with open(path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            doc_coverage = doc_coverage_analyzer.calculate_coverage(
                symbols, file_content, 'python'
            )
            
            # Score teaching value
            score = teaching_value_scorer.score_file(
                symbols, [], complexity_metrics, doc_coverage
            )
            
            # Assertions
            assert score.documentation_score < 0.3, "Should have low documentation score"
            assert score.total_score < 0.7, "Poorly documented code should score lower"
            assert "Poor documentation" in score.explanation or "Moderate documentation" in score.explanation
            
        finally:
            try:
                os.unlink(path)
            except:
                pass
    
    def test_minimal_documentation(
        self,
        parser_manager,
        symbol_extractor,
        complexity_analyzer,
        doc_coverage_analyzer,
        teaching_value_scorer
    ):
        """Test scoring for code with minimal/placeholder documentation."""
        code = '''def calculate(x, y):
    """TODO"""
    return x + y


def process(data):
    """..."""
    if data:
        return data * 2
    return 0
'''
        path = create_test_file(code, '.py')
        try:
            # Parse and extract symbols
            parse_result = parser_manager.parse_file(path)
            symbols = symbol_extractor.extract_symbols(parse_result)
            
            # Calculate metrics
            complexity_metrics = complexity_analyzer.analyze_file(symbols)
            
            # Read file content
            with open(path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            doc_coverage = doc_coverage_analyzer.calculate_coverage(
                symbols, file_content, 'python'
            )
            
            # Score teaching value
            score = teaching_value_scorer.score_file(
                symbols, [], complexity_metrics, doc_coverage
            )
            
            # Assertions - placeholder docs should not count
            assert score.documentation_score < 0.3, "Placeholder docs should not count"
            
        finally:
            try:
                os.unlink(path)
            except:
                pass


class TestOverlyComplexCode:
    """Test scoring for overly complex code."""
    
    def test_high_complexity_code(
        self,
        parser_manager,
        symbol_extractor,
        complexity_analyzer,
        doc_coverage_analyzer,
        teaching_value_scorer
    ):
        """Test scoring for code with high complexity (>10)."""
        code = '''def complex_function(a, b, c, d, e, f):
    """
    A very complex function with many branches.
    
    This function has high cyclomatic complexity.
    """
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    if e > 0:
                        if f > 0:
                            return a + b + c + d + e + f
                        else:
                            return a + b + c + d + e
                    else:
                        return a + b + c + d
                else:
                    return a + b + c
            else:
                return a + b
        else:
            return a
    elif a < 0:
        if b < 0:
            if c < 0:
                return a - b - c
            else:
                return a - b
        else:
            return a
    else:
        if b == 0:
            return 0
        else:
            return b
'''
        path = create_test_file(code, '.py')
        try:
            # Parse and extract symbols
            parse_result = parser_manager.parse_file(path)
            symbols = symbol_extractor.extract_symbols(parse_result)
            
            # Calculate metrics
            complexity_metrics = complexity_analyzer.analyze_file(symbols)
            
            # Read file content
            with open(path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            doc_coverage = doc_coverage_analyzer.calculate_coverage(
                symbols, file_content, 'python'
            )
            
            # Score teaching value
            score = teaching_value_scorer.score_file(
                symbols, [], complexity_metrics, doc_coverage
            )
            
            # Assertions
            assert complexity_metrics.avg_complexity > 10, "Should have high complexity"
            assert score.complexity_score <= 0.3, "High complexity should score low"
            assert "complex" in score.explanation.lower()
            
        finally:
            try:
                os.unlink(path)
            except:
                pass
    
    def test_trivial_complexity_code(
        self,
        parser_manager,
        symbol_extractor,
        complexity_analyzer,
        doc_coverage_analyzer,
        teaching_value_scorer
    ):
        """Test scoring for code with trivial complexity (<2)."""
        code = '''def add(a, b):
    """Add two numbers."""
    return a + b


def multiply(a, b):
    """Multiply two numbers."""
    return a * b


def subtract(a, b):
    """Subtract b from a."""
    return a - b
'''
        path = create_test_file(code, '.py')
        try:
            # Parse and extract symbols
            parse_result = parser_manager.parse_file(path)
            symbols = symbol_extractor.extract_symbols(parse_result)
            
            # Calculate metrics
            complexity_metrics = complexity_analyzer.analyze_file(symbols)
            
            # Read file content
            with open(path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            doc_coverage = doc_coverage_analyzer.calculate_coverage(
                symbols, file_content, 'python'
            )
            
            # Score teaching value
            score = teaching_value_scorer.score_file(
                symbols, [], complexity_metrics, doc_coverage
            )
            
            # Assertions
            assert complexity_metrics.avg_complexity < 2, "Should have trivial complexity"
            assert score.complexity_score <= 0.3, "Trivial complexity should score low"
            assert "simple" in score.explanation.lower()
            
        finally:
            try:
                os.unlink(path)
            except:
                pass


class TestScoreConsistency:
    """Test score consistency across multiple runs."""
    
    def test_consistent_scoring(
        self,
        parser_manager,
        symbol_extractor,
        complexity_analyzer,
        doc_coverage_analyzer,
        teaching_value_scorer
    ):
        """Test that the same code produces consistent scores across runs."""
        code = '''def fibonacci(n):
    """
    Calculate the nth Fibonacci number.
    
    Args:
        n: Position in Fibonacci sequence
    
    Returns:
        The nth Fibonacci number
    """
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b
'''
        path = create_test_file(code, '.py')
        try:
            scores = []
            
            # Run scoring 5 times
            for _ in range(5):
                # Parse and extract symbols
                parse_result = parser_manager.parse_file(path)
                symbols = symbol_extractor.extract_symbols(parse_result)
                
                # Calculate metrics
                complexity_metrics = complexity_analyzer.analyze_file(symbols)
                
                # Read file content
                with open(path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                
                doc_coverage = doc_coverage_analyzer.calculate_coverage(
                    symbols, file_content, 'python'
                )
                
                # Score teaching value
                score = teaching_value_scorer.score_file(
                    symbols, [], complexity_metrics, doc_coverage
                )
                
                scores.append(score.total_score)
            
            # Calculate variance
            avg_score = sum(scores) / len(scores)
            variance = sum((s - avg_score) ** 2 for s in scores) / len(scores)
            
            # Assertions
            assert variance < 0.01, f"Score variance {variance} should be < 0.01 (scores: {scores})"
            assert all(s == scores[0] for s in scores), "All scores should be identical"
            
        finally:
            try:
                os.unlink(path)
            except:
                pass
    
    def test_score_determinism(
        self,
        parser_manager,
        symbol_extractor,
        complexity_analyzer,
        doc_coverage_analyzer,
        teaching_value_scorer
    ):
        """Test that scoring is deterministic for the same input."""
        code = '''class MathOperations:
    """A class for mathematical operations."""
    
    def add(self, a, b):
        """Add two numbers."""
        return a + b
    
    def divide(self, a, b):
        """Divide a by b with error handling."""
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
'''
        path = create_test_file(code, '.py')
        try:
            # First run
            parse_result1 = parser_manager.parse_file(path)
            symbols1 = symbol_extractor.extract_symbols(parse_result1)
            complexity1 = complexity_analyzer.analyze_file(symbols1)
            
            with open(path, 'r', encoding='utf-8') as f:
                content1 = f.read()
            doc_coverage1 = doc_coverage_analyzer.calculate_coverage(
                symbols1, content1, 'python'
            )
            score1 = teaching_value_scorer.score_file(
                symbols1, [], complexity1, doc_coverage1
            )
            
            # Second run
            parse_result2 = parser_manager.parse_file(path)
            symbols2 = symbol_extractor.extract_symbols(parse_result2)
            complexity2 = complexity_analyzer.analyze_file(symbols2)
            
            with open(path, 'r', encoding='utf-8') as f:
                content2 = f.read()
            doc_coverage2 = doc_coverage_analyzer.calculate_coverage(
                symbols2, content2, 'python'
            )
            score2 = teaching_value_scorer.score_file(
                symbols2, [], complexity2, doc_coverage2
            )
            
            # Assertions
            assert score1.total_score == score2.total_score
            assert score1.documentation_score == score2.documentation_score
            assert score1.complexity_score == score2.complexity_score
            assert score1.pattern_score == score2.pattern_score
            assert score1.structure_score == score2.structure_score
            
        finally:
            try:
                os.unlink(path)
            except:
                pass


class TestScoringFactors:
    """Test individual scoring factors."""
    
    def test_pattern_scoring(
        self,
        parser_manager,
        symbol_extractor,
        complexity_analyzer,
        doc_coverage_analyzer,
        teaching_value_scorer
    ):
        """Test that patterns increase teaching value score."""
        code = '''def simple_function():
    """A simple function."""
    return 42
'''
        path = create_test_file(code, '.py')
        try:
            # Parse and extract symbols
            parse_result = parser_manager.parse_file(path)
            symbols = symbol_extractor.extract_symbols(parse_result)
            
            # Calculate metrics
            complexity_metrics = complexity_analyzer.analyze_file(symbols)
            
            # Read file content
            with open(path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            doc_coverage = doc_coverage_analyzer.calculate_coverage(
                symbols, file_content, 'python'
            )
            
            # Mock pattern class
            class MockPattern:
                def __init__(self, pattern_type):
                    self.pattern_type = pattern_type
            
            # Score without patterns
            score_no_patterns = teaching_value_scorer.score_file(
                symbols, [], complexity_metrics, doc_coverage
            )
            
            # Score with patterns
            patterns = [MockPattern('test_pattern_1'), MockPattern('test_pattern_2')]
            score_with_patterns = teaching_value_scorer.score_file(
                symbols, patterns, complexity_metrics, doc_coverage
            )
            
            # Assertions
            assert score_with_patterns.pattern_score > score_no_patterns.pattern_score
            assert score_with_patterns.total_score > score_no_patterns.total_score
            assert score_with_patterns.factors['patterns']['pattern_count'] == 2
            
        finally:
            try:
                os.unlink(path)
            except:
                pass
    
    def test_structure_scoring(
        self,
        parser_manager,
        symbol_extractor,
        complexity_analyzer,
        doc_coverage_analyzer,
        teaching_value_scorer
    ):
        """Test structure scoring for well-organized code."""
        # Code with both functions and classes (good structure)
        code_good = '''def helper_function(x):
    """Helper function."""
    return x * 2


class Calculator:
    """Calculator class."""
    
    def add(self, a, b):
        """Add two numbers."""
        return a + b
    
    def multiply(self, a, b):
        """Multiply two numbers."""
        return a * b
'''
        
        # Code with only functions (less structure)
        code_functions_only = '''def func1():
    """Function 1."""
    return 1


def func2():
    """Function 2."""
    return 2
'''
        
        path_good = create_test_file(code_good, '.py')
        path_functions = create_test_file(code_functions_only, '.py')
        
        try:
            # Score good structure
            parse_result_good = parser_manager.parse_file(path_good)
            symbols_good = symbol_extractor.extract_symbols(parse_result_good)
            complexity_good = complexity_analyzer.analyze_file(symbols_good)
            
            with open(path_good, 'r', encoding='utf-8') as f:
                content_good = f.read()
            doc_coverage_good = doc_coverage_analyzer.calculate_coverage(
                symbols_good, content_good, 'python'
            )
            score_good = teaching_value_scorer.score_file(
                symbols_good, [], complexity_good, doc_coverage_good
            )
            
            # Score functions-only structure
            parse_result_func = parser_manager.parse_file(path_functions)
            symbols_func = symbol_extractor.extract_symbols(parse_result_func)
            complexity_func = complexity_analyzer.analyze_file(symbols_func)
            
            with open(path_functions, 'r', encoding='utf-8') as f:
                content_func = f.read()
            doc_coverage_func = doc_coverage_analyzer.calculate_coverage(
                symbols_func, content_func, 'python'
            )
            score_func = teaching_value_scorer.score_file(
                symbols_func, [], complexity_func, doc_coverage_func
            )
            
            # Assertions
            assert score_good.structure_score > score_func.structure_score, \
                "Code with both functions and classes should have better structure score"
            
        finally:
            try:
                os.unlink(path_good)
                os.unlink(path_functions)
            except:
                pass
