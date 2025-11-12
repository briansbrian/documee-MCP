"""
Unit tests for language-specific pattern detectors.

Tests Python and JavaScript pattern detectors with sample files.
Verifies pattern detection, confidence scoring, and end-to-end integration.

Requirements: 3.5, 14.3
"""

import pytest
from dataclasses import dataclass, field
from typing import List, Optional

from src.analysis.language_pattern_detector import (
    PythonPatternDetector,
    JavaScriptPatternDetector
)
from src.analysis.pattern_detector import DetectedPattern


# Mock SymbolInfo and related classes for testing
@dataclass
class ImportInfo:
    module: str
    imported_symbols: List[str] = field(default_factory=list)
    is_relative: bool = False
    import_type: str = "import"
    line_number: int = 1


@dataclass
class FunctionInfo:
    name: str
    parameters: List[str] = field(default_factory=list)
    return_type: Optional[str] = None
    docstring: Optional[str] = None
    start_line: int = 1
    end_line: int = 10
    complexity: int = 1
    is_async: bool = False
    decorators: List[str] = field(default_factory=list)


@dataclass
class ClassInfo:
    name: str
    methods: List[FunctionInfo] = field(default_factory=list)
    base_classes: List[str] = field(default_factory=list)
    docstring: Optional[str] = None
    start_line: int = 1
    end_line: int = 20
    decorators: List[str] = field(default_factory=list)


@dataclass
class SymbolInfo:
    functions: List[FunctionInfo] = field(default_factory=list)
    classes: List[ClassInfo] = field(default_factory=list)
    imports: List[ImportInfo] = field(default_factory=list)
    exports: List[str] = field(default_factory=list)


# ============================================================================
# Python Pattern Detection Tests
# ============================================================================

class TestPythonPatternDetector:
    """Test Python-specific pattern detection."""
    
    def test_detect_builtin_decorators(self):
        """Test detection of built-in decorators (property, staticmethod, classmethod)."""
        detector = PythonPatternDetector()
        
        symbol_info = SymbolInfo(
            classes=[
                ClassInfo(
                    name="MyClass",
                    methods=[
                        FunctionInfo(name="get_value", decorators=["property"], start_line=5),
                        FunctionInfo(name="static_method", decorators=["staticmethod"], start_line=10),
                        FunctionInfo(name="class_method", decorators=["classmethod"], start_line=15)
                    ]
                )
            ]
        )
        
        file_content = """class MyClass:
    def __init__(self):
        self._value = 0
    
    @property
    def get_value(self):
        return self._value
    
    @staticmethod
    def static_method():
        return "static"
    
    @classmethod
    def class_method(cls):
        return cls()
"""
        
        patterns = detector.detect(symbol_info, file_content, "test.py")
        
        decorator_patterns = [p for p in patterns if p.pattern_type == "python_decorators"]
        assert len(decorator_patterns) == 1
        
        pattern = decorator_patterns[0]
        assert pattern.confidence > 0.0
        assert "property" in pattern.metadata["builtin_decorators"]
        assert "staticmethod" in pattern.metadata["builtin_decorators"]
        assert "classmethod" in pattern.metadata["builtin_decorators"]
        assert pattern.metadata["decorator_count"] == 3
    
    def test_detect_custom_decorators(self):
        """Test detection of custom decorators."""
        detector = PythonPatternDetector()
        
        symbol_info = SymbolInfo(
            functions=[
                FunctionInfo(name="my_func", decorators=["@app.route('/test')", "@login_required"], start_line=5)
            ]
        )
        
        file_content = """@app.route('/test')
@login_required
def my_func():
    return "Hello"
"""
        
        patterns = detector.detect(symbol_info, file_content, "test.py")
        
        decorator_patterns = [p for p in patterns if p.pattern_type == "python_decorators"]
        assert len(decorator_patterns) == 1
        
        pattern = decorator_patterns[0]
        assert pattern.confidence > 0.0
        assert pattern.metadata["custom_decorator_count"] == 2
    
    def test_detect_context_managers(self):
        """Test detection of context managers (with statements)."""
        detector = PythonPatternDetector()
        
        symbol_info = SymbolInfo()
        
        file_content = """with open('file.txt', 'r') as f:
    content = f.read()

with lock:
    shared_resource.update()

with threading.Lock():
    critical_section()
"""
        
        patterns = detector.detect(symbol_info, file_content, "test.py")
        
        context_patterns = [p for p in patterns if p.pattern_type == "python_context_managers"]
        assert len(context_patterns) == 1
        
        pattern = context_patterns[0]
        assert pattern.confidence > 0.0
        assert pattern.metadata["with_statement_count"] == 3
        assert any("File handling" in e for e in pattern.evidence)
    
    def test_detect_generators(self):
        """Test detection of generator functions (yield statements)."""
        detector = PythonPatternDetector()
        
        symbol_info = SymbolInfo(
            functions=[
                FunctionInfo(name="my_generator", start_line=1)
            ]
        )
        
        file_content = """def my_generator():
    for i in range(10):
        yield i * 2

def another_gen():
    yield from range(5)
"""
        
        patterns = detector.detect(symbol_info, file_content, "test.py")
        
        generator_patterns = [p for p in patterns if p.pattern_type == "python_generators"]
        assert len(generator_patterns) == 1
        
        pattern = generator_patterns[0]
        assert pattern.confidence > 0.0
        assert pattern.metadata["yield_count"] == 2
    
    def test_detect_async_await(self):
        """Test detection of async/await patterns."""
        detector = PythonPatternDetector()
        
        symbol_info = SymbolInfo(
            imports=[ImportInfo(module="asyncio", line_number=1)],
            functions=[
                FunctionInfo(name="fetch_data", is_async=True, start_line=3),
                FunctionInfo(name="process_data", is_async=True, start_line=8)
            ]
        )
        
        file_content = """import asyncio

async def fetch_data():
    await asyncio.sleep(1)
    return "data"

async def process_data():
    result = await fetch_data()
    return result
"""
        
        patterns = detector.detect(symbol_info, file_content, "test.py")
        
        async_patterns = [p for p in patterns if p.pattern_type == "python_async_await"]
        assert len(async_patterns) == 1
        
        pattern = async_patterns[0]
        assert pattern.confidence > 0.0
        assert pattern.metadata["async_function_count"] == 2
        assert pattern.metadata["await_count"] == 2
        assert any("asyncio" in e for e in pattern.evidence)
    
    def test_detect_comprehensions(self):
        """Test detection of list/dict/set comprehensions."""
        detector = PythonPatternDetector()
        
        symbol_info = SymbolInfo()
        
        file_content = """squares = [x**2 for x in range(10)]
evens = {x for x in range(20) if x % 2 == 0}
mapping = {k: v for k, v in items}
"""
        
        patterns = detector.detect(symbol_info, file_content, "test.py")
        
        comprehension_patterns = [p for p in patterns if p.pattern_type == "python_comprehensions"]
        assert len(comprehension_patterns) == 1
        
        pattern = comprehension_patterns[0]
        assert pattern.confidence > 0.0
        assert pattern.metadata["comprehension_count"] == 3
    
    def test_no_patterns_in_simple_python(self):
        """Test that simple Python code doesn't trigger false positives."""
        detector = PythonPatternDetector()
        
        symbol_info = SymbolInfo(
            functions=[FunctionInfo(name="add", start_line=1)]
        )
        
        file_content = """def add(a, b):
    return a + b
"""
        
        patterns = detector.detect(symbol_info, file_content, "test.py")
        
        # Should not detect any patterns
        assert len(patterns) == 0
    
    def test_pattern_scores_non_zero(self):
        """Verify pattern scores are non-zero for files with patterns."""
        detector = PythonPatternDetector()
        
        symbol_info = SymbolInfo(
            functions=[
                FunctionInfo(name="my_func", decorators=["@property"], start_line=1)
            ]
        )
        
        file_content = """@property
def my_func(self):
    return self._value
"""
        
        patterns = detector.detect(symbol_info, file_content, "test.py")
        
        assert len(patterns) > 0
        for pattern in patterns:
            assert pattern.confidence > 0.0, f"Pattern {pattern.pattern_type} has zero confidence"


# ============================================================================
# JavaScript Pattern Detection Tests
# ============================================================================

class TestJavaScriptPatternDetector:
    """Test JavaScript/TypeScript-specific pattern detection."""
    
    def test_detect_promises(self):
        """Test detection of Promise usage."""
        detector = JavaScriptPatternDetector()
        
        symbol_info = SymbolInfo()
        
        file_content = """function fetchData() {
    return fetch('/api/data')
        .then(response => response.json())
        .catch(error => console.error(error));
}

const promise = new Promise((resolve, reject) => {
    setTimeout(() => resolve('done'), 1000);
});

Promise.all([promise1, promise2]).then(results => {
    console.log(results);
});
"""
        
        patterns = detector.detect(symbol_info, file_content, "test.js")
        
        promise_patterns = [p for p in patterns if p.pattern_type == "javascript_promises"]
        assert len(promise_patterns) == 1
        
        pattern = promise_patterns[0]
        assert pattern.confidence > 0.0
        assert pattern.metadata["promise_count"] > 0
        assert any(".then()" in e for e in pattern.evidence)
        assert any(".catch()" in e for e in pattern.evidence)
        assert any("Promise.all()" in e for e in pattern.evidence)
    
    def test_detect_async_await(self):
        """Test detection of async/await patterns."""
        detector = JavaScriptPatternDetector()
        
        symbol_info = SymbolInfo(
            functions=[
                FunctionInfo(name="fetchData", is_async=True, start_line=1),
                FunctionInfo(name="processData", is_async=True, start_line=6)
            ]
        )
        
        file_content = """async function fetchData() {
    const response = await fetch('/api/data');
    return await response.json();
}

async function processData() {
    const data = await fetchData();
    return data;
}
"""
        
        patterns = detector.detect(symbol_info, file_content, "test.js")
        
        async_patterns = [p for p in patterns if p.pattern_type == "javascript_async_await"]
        assert len(async_patterns) == 1
        
        pattern = async_patterns[0]
        assert pattern.confidence > 0.0
        assert pattern.metadata["async_function_count"] == 2
        assert pattern.metadata["await_count"] == 3
    
    def test_detect_arrow_functions(self):
        """Test detection of arrow functions."""
        detector = JavaScriptPatternDetector()
        
        symbol_info = SymbolInfo()
        
        file_content = """const add = (a, b) => a + b;
const multiply = (x, y) => {
    return x * y;
};
const numbers = [1, 2, 3].map(n => n * 2);
"""
        
        patterns = detector.detect(symbol_info, file_content, "test.js")
        
        arrow_patterns = [p for p in patterns if p.pattern_type == "javascript_arrow_functions"]
        assert len(arrow_patterns) == 1
        
        pattern = arrow_patterns[0]
        assert pattern.confidence > 0.0
        assert pattern.metadata["arrow_function_count"] >= 3
    
    def test_detect_destructuring(self):
        """Test detection of destructuring patterns."""
        detector = JavaScriptPatternDetector()
        
        symbol_info = SymbolInfo()
        
        file_content = """const { name, age } = user;
const [first, second] = array;
let { x, y, z } = coordinates;
var [a, b, ...rest] = items;
"""
        
        patterns = detector.detect(symbol_info, file_content, "test.js")
        
        destructuring_patterns = [p for p in patterns if p.pattern_type == "javascript_destructuring"]
        assert len(destructuring_patterns) == 1
        
        pattern = destructuring_patterns[0]
        assert pattern.confidence > 0.0
        assert pattern.metadata["destructuring_count"] == 4
    
    def test_detect_spread_operators(self):
        """Test detection of spread operator usage."""
        detector = JavaScriptPatternDetector()
        
        symbol_info = SymbolInfo()
        
        file_content = """const newArray = [...oldArray, 4, 5];
const merged = { ...obj1, ...obj2 };
function sum(...numbers) {
    return numbers.reduce((a, b) => a + b);
}
"""
        
        patterns = detector.detect(symbol_info, file_content, "test.js")
        
        spread_patterns = [p for p in patterns if p.pattern_type == "javascript_spread_operator"]
        assert len(spread_patterns) == 1
        
        pattern = spread_patterns[0]
        assert pattern.confidence > 0.0
        assert pattern.metadata["spread_count"] >= 3
    
    def test_no_patterns_in_simple_javascript(self):
        """Test that simple JavaScript code doesn't trigger false positives."""
        detector = JavaScriptPatternDetector()
        
        symbol_info = SymbolInfo(
            functions=[FunctionInfo(name="add", start_line=1)]
        )
        
        file_content = """function add(a, b) {
    return a + b;
}
"""
        
        patterns = detector.detect(symbol_info, file_content, "test.js")
        
        # Should not detect any patterns
        assert len(patterns) == 0
    
    def test_pattern_scores_non_zero(self):
        """Verify pattern scores are non-zero for files with patterns."""
        detector = JavaScriptPatternDetector()
        
        symbol_info = SymbolInfo()
        
        file_content = """const add = (a, b) => a + b;"""
        
        patterns = detector.detect(symbol_info, file_content, "test.js")
        
        assert len(patterns) > 0
        for pattern in patterns:
            assert pattern.confidence > 0.0, f"Pattern {pattern.pattern_type} has zero confidence"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
