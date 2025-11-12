"""
Tests for Persistence Manager.

Tests saving/loading analysis results, file hash tracking, and directory management.
"""

import pytest
import os
import tempfile
import shutil
from datetime import datetime

from src.analysis.persistence import PersistenceManager
from src.models.analysis_models import (
    CodebaseAnalysis,
    FileAnalysis,
    SymbolInfo,
    FunctionInfo,
    ClassInfo,
    ImportInfo,
    DetectedPattern,
    ComplexityMetrics,
    TeachingValueScore,
    LinterIssue,
    DependencyGraph,
    FileNode,
    DependencyEdge,
    CircularDependency,
    CodebaseMetrics
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    # Cleanup
    try:
        shutil.rmtree(temp_path)
    except:
        pass


@pytest.fixture
def persistence_manager(temp_dir):
    """Create a persistence manager with temporary directory."""
    return PersistenceManager(base_path=temp_dir)


@pytest.fixture
def sample_file_analysis():
    """Create a sample FileAnalysis object for testing."""
    return FileAnalysis(
        file_path="test/sample.py",
        language="python",
        symbol_info=SymbolInfo(
            functions=[
                FunctionInfo(
                    name="test_func",
                    parameters=["x", "y"],
                    return_type="int",
                    docstring="Test function",
                    start_line=1,
                    end_line=5,
                    complexity=2,
                    is_async=False,
                    decorators=[]
                )
            ],
            classes=[],
            imports=[
                ImportInfo(
                    module="os",
                    imported_symbols=["path"],
                    is_relative=False,
                    import_type="from_import",
                    line_number=1
                )
            ],
            exports=[]
        ),
        patterns=[
            DetectedPattern(
                pattern_type="test_pattern",
                file_path="test/sample.py",
                confidence=0.9,
                evidence=["test evidence"],
                line_numbers=[1, 2],
                metadata={}
            )
        ],
        teaching_value=TeachingValueScore(
            total_score=0.75,
            documentation_score=0.8,
            complexity_score=0.7,
            pattern_score=0.8,
            structure_score=0.7,
            explanation="Good teaching value",
            factors={}
        ),
        complexity_metrics=ComplexityMetrics(
            avg_complexity=2.0,
            max_complexity=2,
            min_complexity=2,
            high_complexity_functions=[],
            trivial_functions=[],
            avg_nesting_depth=1.0
        ),
        documentation_coverage=0.8,
        linter_issues=[],
        has_errors=False,
        errors=[],
        analyzed_at=datetime.now().isoformat(),
        cache_hit=False,
        is_notebook=False
    )


@pytest.fixture
def sample_codebase_analysis(sample_file_analysis):
    """Create a sample CodebaseAnalysis object for testing."""
    return CodebaseAnalysis(
        codebase_id="test_codebase_123",
        file_analyses={
            "test/sample.py": sample_file_analysis
        },
        dependency_graph=DependencyGraph(
            nodes={
                "test/sample.py": FileNode(
                    file_path="test/sample.py",
                    imports=[],
                    imported_by=[],
                    external_imports=["os"]
                )
            },
            edges=[],
            circular_dependencies=[],
            external_dependencies={"os": 1}
        ),
        global_patterns=[],
        top_teaching_files=[("test/sample.py", 0.75)],
        metrics=CodebaseMetrics(
            total_files=1,
            total_functions=1,
            total_classes=0,
            avg_complexity=2.0,
            avg_documentation_coverage=0.8,
            total_patterns_detected=1,
            analysis_time_ms=100.0,
            cache_hit_rate=0.0
        ),
        analyzed_at=datetime.now().isoformat()
    )


class TestPersistenceManagerInitialization:
    """Test PersistenceManager initialization."""
    
    def test_initialization_creates_directory(self, temp_dir):
        """Test that initialization creates the base directory."""
        base_path = os.path.join(temp_dir, "test_analysis")
        manager = PersistenceManager(base_path=base_path)
        
        assert os.path.exists(base_path)
        assert os.path.isdir(base_path)
    
    def test_initialization_with_existing_directory(self, temp_dir):
        """Test initialization with existing directory."""
        # Create directory first
        os.makedirs(temp_dir, exist_ok=True)
        
        # Should not raise error
        manager = PersistenceManager(base_path=temp_dir)
        assert os.path.exists(temp_dir)


class TestSaveAnalysis:
    """Test saving analysis results."""
    
    def test_save_codebase_analysi