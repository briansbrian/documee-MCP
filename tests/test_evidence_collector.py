"""
Tests for Evidence Collector module.

Tests the evidence collection utilities for gathering source code,
tests, documentation, and dependency information.
"""

import pytest
import asyncio
from pathlib import Path
from src.course.evidence_collector import EvidenceCollector, create_evidence_collector
from src.course.models import Lesson, LessonContent, CodeExample, CodeHighlight
from src.models.analysis_models import (
    FileAnalysis, SymbolInfo, FunctionInfo, ClassInfo, ImportInfo,
    ComplexityMetrics, TeachingValueScore
)


@pytest.fixture
def repo_path():
    """Get the repository root path."""
    return str(Path(__file__).parent.parent)


@pytest.fixture
def evidence_collector(repo_path):
    """Create an evidence collector instance."""
    return create_evidence_collector(repo_path)


@pytest.fixture
def sample_lesson():
    """Create a sample lesson for testing."""
    return Lesson(
        lesson_id="test-lesson-1",
        title="Test Lesson",
        description="A test lesson",
        order=1,
        difficulty="beginner",
        duration_minutes=30,
        file_path="src/course/evidence_collector.py",
        teaching_value=0.8,
        learning_objectives=["Learn evidence collection"],
        content=LessonContent(
            introduction="Introduction",
            explanation="Explanation",
            code_example=CodeExample(
                code="def test(): pass",
                language="python",
                filename="src/course/evidence_collector.py",
                highlights=[
                    CodeHighlight(
                        start_line=1,
                        end_line=10,
                        description="Module docstring"
                    )
                ]
            ),
            walkthrough="Walkthrough",
            summary="Summary"
        )
    )


@pytest.fixture
def sample_file_analysis():
    """Create a sample file analysis for testing."""
    return FileAnalysis(
        file_path="src/course/evidence_collector.py",
        language="python",
        symbol_info=SymbolInfo(
            functions=[
                FunctionInfo(
                    name="collect_source_evidence",
                    parameters=["self", "lesson"],
                    return_type="List[Dict[str, Any]]",
                    docstring="Gather source code with line numbers for a lesson.",
                    start_line=50,
                    end_line=100,
                    complexity=5,
                    is_async=True,
                    decorators=[]
                )
            ],
            classes=[
                ClassInfo(
                    name="EvidenceCollector",
                    methods=[],
                    base_classes=[],
                    docstring="Collects evidence from multiple sources.",
                    start_line=20,
                    end_line=500,
                    decorators=[]
                )
            ],
            imports=[
                ImportInfo(
                    module="logging",
                    imported_symbols=[],
                    is_relative=False,
                    import_type="import",
                    line_number=5
                ),
                ImportInfo(
                    module="pathlib",
                    imported_symbols=["Path"],
                    is_relative=False,
                    import_type="from_import",
                    line_number=6
                )
            ],
            exports=[]
        ),
        patterns=[],
        teaching_value=TeachingValueScore(
            total_score=0.8,
            documentation_score=0.9,
            complexity_score=0.7,
            pattern_score=0.8,
            structure_score=0.8,
            explanation="Well-documented utility module"
        ),
        complexity_metrics=ComplexityMetrics(
            avg_complexity=5.0,
            max_complexity=10,
            min_complexity=1,
            high_complexity_functions=[],
            trivial_functions=[],
            avg_nesting_depth=2.0
        ),
        documentation_coverage=0.9,
        linter_issues=[],
        has_errors=False,
        errors=[],
        analyzed_at="2024-01-01T00:00:00",
        cache_hit=False,
        is_notebook=False
    )


class TestEvidenceCollector:
    """Test suite for EvidenceCollector class."""
    
    def test_initialization(self, evidence_collector, repo_path):
        """Test evidence collector initialization."""
        assert evidence_collector is not None
        assert evidence_collector.repo_path == Path(repo_path).resolve()
    
    def test_factory_function(self, repo_path):
        """Test factory function creates valid instance."""
        collector = create_evidence_collector(repo_path)
        assert isinstance(collector, EvidenceCollector)
    
    def test_detect_language(self, evidence_collector):
        """Test language detection from file extensions."""
        assert evidence_collector._detect_language("test.py") == "python"
        assert evidence_collector._detect_language("test.js") == "javascript"
        assert evidence_collector._detect_language("test.ts") == "typescript"
        assert evidence_collector._detect_language("test.java") == "java"
        assert evidence_collector._detect_language("test.go") == "go"
        assert evidence_collector._detect_language("test.rs") == "rust"
        assert evidence_collector._detect_language("test.unknown") == "unknown"
    
    @pytest.mark.asyncio
    async def test_collect_source_evidence(self, evidence_collector, sample_lesson):
        """Test collecting source code evidence."""
        source_files = await evidence_collector.collect_source_evidence(sample_lesson)
        
        assert isinstance(source_files, list)
        assert len(source_files) > 0
        
        # Check structure of first file
        first_file = source_files[0]
        assert 'path' in first_file
        assert 'code' in first_file
        assert 'lines' in first_file
        assert 'language' in first_file
        assert 'sections' in first_file
        
        assert first_file['language'] == 'python'
        assert first_file['lines'] > 0
    
    @pytest.mark.asyncio
    async def test_collect_test_evidence(self, evidence_collector, sample_lesson):
        """Test collecting test file evidence."""
        # Modify lesson to point to a file that has tests
        sample_lesson.file_path = "src/cache/unified_cache.py"
        
        test_files = await evidence_collector.collect_test_evidence(sample_lesson)
        
        assert isinstance(test_files, list)
        # May or may not find tests depending on file structure
    
    def test_detect_test_framework(self, evidence_collector):
        """Test test framework detection."""
        pytest_content = "import pytest\n\ndef test_something():\n    pass"
        assert evidence_collector._detect_test_framework(pytest_content, "test.py") == "pytest"
        
        unittest_content = "import unittest\n\nclass TestCase(unittest.TestCase):\n    pass"
        assert evidence_collector._detect_test_framework(unittest_content, "test.py") == "unittest"
        
        jest_content = "describe('test', () => {\n  it('should work', () => {});\n});"
        assert evidence_collector._detect_test_framework(jest_content, "test.spec.js") == "jest"
    
    def test_extract_test_cases_pytest(self, evidence_collector):
        """Test extracting pytest test cases."""
        content = '''
def test_something():
    """Test something important."""
    assert True

def test_another_thing():
    assert False
'''
        test_cases = evidence_collector._extract_test_cases(content, "pytest")
        
        assert len(test_cases) == 2
        assert test_cases[0]['name'] == 'test_something'
        assert 'Test something important' in test_cases[0]['description']
        assert test_cases[1]['name'] == 'test_another_thing'
    
    def test_extract_test_cases_jest(self, evidence_collector):
        """Test extracting Jest test cases."""
        content = '''
describe('MyComponent', () => {
  it('should render correctly', () => {
    expect(true).toBe(true);
  });
  
  test('should handle clicks', () => {
    expect(false).toBe(false);
  });
});
'''
        test_cases = evidence_collector._extract_test_cases(content, "jest")
        
        assert len(test_cases) == 2
        assert test_cases[0]['description'] == 'should render correctly'
        assert test_cases[1]['description'] == 'should handle clicks'
    
    def test_collect_documentation_evidence(self, evidence_collector, sample_file_analysis):
        """Test collecting documentation evidence."""
        documentation = evidence_collector.collect_documentation_evidence(sample_file_analysis)
        
        assert isinstance(documentation, list)
        assert len(documentation) > 0
        
        # Check structure
        first_doc = documentation[0]
        assert 'type' in first_doc
        assert 'content' in first_doc
        assert 'location' in first_doc
        assert 'context' in first_doc
        
        # Should have docstrings from functions and classes
        doc_types = [doc['type'] for doc in documentation]
        assert 'docstring' in doc_types
    
    def test_collect_dependency_evidence(self, evidence_collector, sample_file_analysis):
        """Test collecting dependency evidence."""
        dependencies = evidence_collector.collect_dependency_evidence(sample_file_analysis)
        
        assert isinstance(dependencies, list)
        assert len(dependencies) > 0
        
        # Check structure
        first_dep = dependencies[0]
        assert 'name' in first_dep
        assert 'symbols' in first_dep
        assert 'reason' in first_dep
        assert 'evidence' in first_dep
        assert 'type' in first_dep
        
        # Check dependency classification
        dep_types = [dep['type'] for dep in dependencies]
        assert 'standard_library' in dep_types
    
    def test_classify_dependency(self, evidence_collector):
        """Test dependency classification."""
        assert evidence_collector._classify_dependency("os") == "standard_library"
        assert evidence_collector._classify_dependency("logging") == "standard_library"
        assert evidence_collector._classify_dependency("pathlib") == "standard_library"
        assert evidence_collector._classify_dependency("numpy") == "third_party"
        assert evidence_collector._classify_dependency("pandas") == "third_party"
        assert evidence_collector._classify_dependency(".models") == "local"
        assert evidence_collector._classify_dependency("src.utils") == "local"
    
    def test_infer_import_reason(self, evidence_collector):
        """Test inferring import reasons."""
        reason = evidence_collector._infer_import_reason("logging", [])
        assert "logging" in reason.lower()
        
        reason = evidence_collector._infer_import_reason("config", [])
        assert "configuration" in reason.lower()
        
        # When module name matches a pattern, it takes precedence
        reason = evidence_collector._infer_import_reason("utils", ["helper_func"])
        assert "util" in reason.lower()  # "Utility functions"
        
        # When no pattern matches, it uses symbols
        reason = evidence_collector._infer_import_reason("mymodule", ["User", "Post"])
        assert "User" in reason and "Post" in reason


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
