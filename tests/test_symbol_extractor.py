"""
Unit tests for symbol extraction across multiple languages.

Tests function and class extraction, docstring/comment extraction,
and complexity calculation for Python, JavaScript, TypeScript.
"""

import pytest
import os
import tempfile

from src.analysis.config import AnalysisConfig
from src.analysis.ast_parser import ASTParserManager
from src.analysis.symbol_extractor import SymbolExtractor


@pytest.fixture
def parser_manager():
    """Create AST parser manager."""
    config = AnalysisConfig()
    return ASTParserManager(config)


@pytest.fixture
def symbol_extractor():
    """Create symbol extractor."""
    return SymbolExtractor()


def create_test_file(code, suffix):
    """Create a test file and return its path."""
    fd, path = tempfile.mkstemp(suffix=suffix, text=True)
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(code)
    except:
        os.close(fd)
        raise
    return path


class TestPythonSymbolExtraction:
    """Test Python symbol extraction."""
    
    def test_extract_simple_function(self, parser_manager, symbol_extractor):
        """Test extraction of a simple Python function."""
        code = '''def add(a, b):
    """Add two numbers."""
    return a + b
'''
        path = create_test_file(code, '.py')
        try:
            parse_result = parser_manager.parse_file(path)
            symbols = symbol_extractor.extract_symbols(parse_result)
            
            assert len(symbols.functions) == 1
            func = symbols.functions[0]
            assert func.name == 'add'
            assert func.parameters == ['a', 'b']
            assert func.docstring == 'Add two numbers.'
            assert func.complexity >= 1
            assert not func.is_async
        finally:
            try:
                os.unlink(path)
            except:
                pass
    
    def test_extract_class_with_methods(self, parser_manager, symbol_extractor):
        """Test extraction of Python class with methods."""
        code = '''class Calculator:
    """A simple calculator."""
    
    def add(self, a, b):
        """Add two numbers."""
        return a + b
'''
        path = create_test_file(code, '.py')
        try:
            parse_result = parser_manager.parse_file(path)
            symbols = symbol_extractor.extract_symbols(parse_result)
            
            assert len(symbols.classes) == 1
            cls = symbols.classes[0]
            assert cls.name == 'Calculator'
            assert cls.docstring == 'A simple calculator.'
            assert len(cls.methods) >= 1
        finally:
            try:
                os.unlink(path)
            except:
                pass
    
    def test_complexity_calculation(self, parser_manager, symbol_extractor):
        """Test cyclomatic complexity calculation."""
        code = '''def complex_function(x, y):
    """Function with multiple decision points."""
    if x > 0:
        if y > 0:
            return x + y
    return 0
'''
        path = create_test_file(code, '.py')
        try:
            parse_result = parser_manager.parse_file(path)
            symbols = symbol_extractor.extract_symbols(parse_result)
            
            assert len(symbols.functions) == 1
            func = symbols.functions[0]
            assert func.complexity > 1
        finally:
            try:
                os.unlink(path)
            except:
                pass


class TestJavaScriptSymbolExtraction:
    """Test JavaScript symbol extraction."""
    
    def test_extract_function_declaration(self, parser_manager, symbol_extractor):
        """Test extraction of JavaScript function declaration."""
        code = '''function add(a, b) {
    return a + b;
}
'''
        path = create_test_file(code, '.js')
        try:
            parse_result = parser_manager.parse_file(path)
            symbols = symbol_extractor.extract_symbols(parse_result)
            
            assert len(symbols.functions) == 1
            func = symbols.functions[0]
            assert func.name == 'add'
            assert func.parameters == ['a', 'b']
        finally:
            try:
                os.unlink(path)
            except:
                pass
    
    def test_extract_class_with_methods(self, parser_manager, symbol_extractor):
        """Test extraction of JavaScript class."""
        code = '''class Calculator {
    add(a, b) {
        return a + b;
    }
}
'''
        path = create_test_file(code, '.js')
        try:
            parse_result = parser_manager.parse_file(path)
            symbols = symbol_extractor.extract_symbols(parse_result)
            
            assert len(symbols.classes) == 1
            cls = symbols.classes[0]
            assert cls.name == 'Calculator'
            assert len(cls.methods) >= 1
        finally:
            try:
                os.unlink(path)
            except:
                pass


class TestDocstringExtraction:
    """Test docstring and comment extraction."""
    
    def test_python_docstring_extraction(self, parser_manager, symbol_extractor):
        """Test Python docstring extraction."""
        code = '''def documented():
    """This is a docstring."""
    pass
'''
        path = create_test_file(code, '.py')
        try:
            parse_result = parser_manager.parse_file(path)
            symbols = symbol_extractor.extract_symbols(parse_result)
            
            assert len(symbols.functions) == 1
            func = symbols.functions[0]
            assert func.docstring is not None
            assert 'docstring' in func.docstring
        finally:
            try:
                os.unlink(path)
            except:
                pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
