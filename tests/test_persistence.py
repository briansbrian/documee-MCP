"""
Tests for Persistence Manager.

Tests saving/loading analysis results, file hash tracking, and directory management.
"""

import pytest
import os
import json
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
    
    def test_save_codebase_analysis(self, persistence_manager, sample_codebase_analysis):
        """Test saving a complete codebase analysis."""
        codebase_id = "test_codebase_123"
        
        # Save analysis
        persistence_manager.save_analysis(codebase_id, sample_codebase_analysis)
        
        # Verify main analysis file exists
        analysis_file = os.path.join(
            persistence_manager.base_path,
            codebase_id,
            "analysis.json"
        )
        assert os.path.exists(analysis_file)
        
        # Verify file can be read as JSON
        with open(analysis_file, 'r') as f:
            data = json.load(f)
        
        assert data['codebase_id'] == codebase_id
        assert 'file_analyses' in data
        assert 'dependency_graph' in data
        assert 'metrics' in data
    
    def test_save_creates_directory(self, temp_dir, sample_codebase_analysis):
        """Test that save_analysis creates necessary directories."""
        base_path = os.path.join(temp_dir, "new_analysis_dir")
        manager = PersistenceManager(base_path=base_path)
        
        codebase_id = "test_codebase_456"
        manager.save_analysis(codebase_id, sample_codebase_analysis)
        
        # Verify directory structure
        assert os.path.exists(base_path)
        assert os.path.exists(os.path.join(base_path, codebase_id))
        assert os.path.exists(os.path.join(base_path, codebase_id, "analysis.json"))
    
    def test_save_individual_file_analyses(self, persistence_manager, sample_codebase_analysis):
        """Test that individual file analyses are saved."""
        codebase_id = "test_codebase_789"
        
        persistence_manager.save_analysis(codebase_id, sample_codebase_analysis)
        
        # Check that individual file analysis files exist
        analysis_dir = os.path.join(persistence_manager.base_path, codebase_id)
        files = os.listdir(analysis_dir)
        
        # Should have analysis.json and at least one file_*.json
        assert "analysis.json" in files
        file_analyses = [f for f in files if f.startswith("file_")]
        assert len(file_analyses) > 0


class TestLoadAnalysis:
    """Test loading analysis results."""
    
    def test_load_existing_analysis(self, persistence_manager, sample_codebase_analysis):
        """Test loading a previously saved analysis."""
        codebase_id = "test_load_123"
        
        # Update the codebase_id in the sample
        sample_codebase_analysis.codebase_id = codebase_id
        
        # Save first
        persistence_manager.save_analysis(codebase_id, sample_codebase_analysis)
        
        # Load
        loaded_analysis = persistence_manager.load_analysis(codebase_id)
        
        assert loaded_analysis is not None
        assert loaded_analysis.codebase_id == codebase_id
        assert len(loaded_analysis.file_analyses) == len(sample_codebase_analysis.file_analyses)
        assert loaded_analysis.metrics.total_files == sample_codebase_analysis.metrics.total_files
    
    def test_load_nonexistent_analysis(self, persistence_manager):
        """Test loading an analysis that doesn't exist."""
        result = persistence_manager.load_analysis("nonexistent_codebase")
        assert result is None
    
    def test_load_preserves_data_types(self, persistence_manager, sample_codebase_analysis):
        """Test that loading preserves all data types correctly."""
        codebase_id = "test_types_123"
        
        # Save and load
        persistence_manager.save_analysis(codebase_id, sample_codebase_analysis)
        loaded = persistence_manager.load_analysis(codebase_id)
        
        assert loaded is not None
        
        # Check file analysis
        file_path = "test/sample.py"
        assert file_path in loaded.file_analyses
        
        file_analysis = loaded.file_analyses[file_path]
        assert file_analysis.language == "python"
        assert file_analysis.documentation_coverage == 0.8
        assert file_analysis.has_errors is False
        
        # Check symbol info
        assert len(file_analysis.symbol_info.functions) == 1
        assert file_analysis.symbol_info.functions[0].name == "test_func"
        
        # Check metrics
        assert loaded.metrics.total_files == 1
        assert loaded.metrics.total_functions == 1


class TestFileHashTracking:
    """Test file hash tracking for incremental analysis."""
    
    def test_save_file_hashes(self, persistence_manager):
        """Test saving file hashes."""
        codebase_id = "test_hashes_123"
        hashes = {
            "file1.py": "abc123",
            "file2.py": "def456",
            "file3.js": "ghi789"
        }
        
        persistence_manager.save_file_hashes(codebase_id, hashes)
        
        # Verify file exists
        hash_file = os.path.join(
            persistence_manager.base_path,
            codebase_id,
            "file_hashes.json"
        )
        assert os.path.exists(hash_file)
        
        # Verify content
        with open(hash_file, 'r') as f:
            saved_hashes = json.load(f)
        
        assert saved_hashes == hashes
    
    def test_get_file_hashes(self, persistence_manager):
        """Test retrieving file hashes."""
        codebase_id = "test_get_hashes_123"
        original_hashes = {
            "file1.py": "hash1",
            "file2.py": "hash2"
        }
        
        # Save first
        persistence_manager.save_file_hashes(codebase_id, original_hashes)
        
        # Retrieve
        loaded_hashes = persistence_manager.get_file_hashes(codebase_id)
        
        assert loaded_hashes == original_hashes
    
    def test_get_nonexistent_hashes(self, persistence_manager):
        """Test getting hashes for non-existent codebase."""
        result = persistence_manager.get_file_hashes("nonexistent")
        assert result == {}
    
    def test_update_file_hashes(self, persistence_manager):
        """Test updating file hashes."""
        codebase_id = "test_update_hashes"
        
        # Save initial hashes
        initial_hashes = {"file1.py": "hash1"}
        persistence_manager.save_file_hashes(codebase_id, initial_hashes)
        
        # Update with new hashes
        updated_hashes = {"file1.py": "hash1_updated", "file2.py": "hash2"}
        persistence_manager.save_file_hashes(codebase_id, updated_hashes)
        
        # Verify update
        loaded = persistence_manager.get_file_hashes(codebase_id)
        assert loaded == updated_hashes
        assert len(loaded) == 2


class TestDirectoryManagement:
    """Test directory creation and management."""
    
    def test_directory_creation_on_init(self, temp_dir):
        """Test that base directory is created on initialization."""
        base_path = os.path.join(temp_dir, "new_base")
        manager = PersistenceManager(base_path=base_path)
        
        assert os.path.exists(base_path)
        assert os.path.isdir(base_path)
    
    def test_codebase_directory_creation(self, persistence_manager, sample_codebase_analysis):
        """Test that codebase-specific directories are created."""
        codebase_id = "test_dir_creation"
        
        persistence_manager.save_analysis(codebase_id, sample_codebase_analysis)
        
        codebase_dir = os.path.join(persistence_manager.base_path, codebase_id)
        assert os.path.exists(codebase_dir)
        assert os.path.isdir(codebase_dir)


class TestDeleteAnalysis:
    """Test deleting analysis data."""
    
    def test_delete_existing_analysis(self, persistence_manager, sample_codebase_analysis):
        """Test deleting an existing analysis."""
        codebase_id = "test_delete_123"
        
        # Save first
        persistence_manager.save_analysis(codebase_id, sample_codebase_analysis)
        persistence_manager.save_file_hashes(codebase_id, {"file.py": "hash"})
        
        # Verify it exists
        assert persistence_manager.load_analysis(codebase_id) is not None
        
        # Delete
        result = persistence_manager.delete_analysis(codebase_id)
        
        assert result is True
        assert persistence_manager.load_analysis(codebase_id) is None
    
    def test_delete_nonexistent_analysis(self, persistence_manager):
        """Test deleting a non-existent analysis."""
        result = persistence_manager.delete_analysis("nonexistent")
        assert result is False


class TestListCodebases:
    """Test listing stored codebases."""
    
    def test_list_empty(self, persistence_manager):
        """Test listing when no codebases exist."""
        codebases = persistence_manager.list_codebases()
        assert codebases == []
    
    def test_list_multiple_codebases(self, persistence_manager, sample_codebase_analysis):
        """Test listing multiple codebases."""
        # Save multiple analyses
        codebase_ids = ["codebase1", "codebase2", "codebase3"]
        
        for codebase_id in codebase_ids:
            persistence_manager.save_analysis(codebase_id, sample_codebase_analysis)
        
        # List
        listed = persistence_manager.list_codebases()
        
        assert len(listed) == 3
        for codebase_id in codebase_ids:
            assert codebase_id in listed
    
    def test_list_ignores_incomplete_directories(self, persistence_manager):
        """Test that listing ignores directories without analysis.json."""
        # Create a directory without analysis.json
        incomplete_dir = os.path.join(persistence_manager.base_path, "incomplete")
        os.makedirs(incomplete_dir, exist_ok=True)
        
        # List should be empty
        codebases = persistence_manager.list_codebases()
        assert "incomplete" not in codebases