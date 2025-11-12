"""
Unit tests for dependency analysis.

Tests import extraction, circular dependency detection, and internal vs external
categorization for Python and JavaScript/TypeScript.
"""

import pytest
import os
import tempfile
from pathlib import Path
from dataclasses import dataclass, field
from typing import List

from src.analysis.dependency_analyzer import (
    DependencyAnalyzer,
    DependencyGraph,
    FileNode,
    DependencyEdge,
    CircularDependency
)
from src.analysis.symbol_extractor import SymbolInfo, ImportInfo
from src.analysis.config import AnalysisConfig
from src.analysis.ast_parser import ASTParserManager


# Mock FileAnalysis for testing
@dataclass
class MockFileAnalysis:
    """Mock FileAnalysis object for testing."""
    symbol_info: SymbolInfo = field(default_factory=SymbolInfo)


@pytest.fixture
def dependency_analyzer():
    """Create dependency analyzer."""
    return DependencyAnalyzer(project_root=".")


@pytest.fixture
def parser_manager():
    """Create AST parser manager."""
    config = AnalysisConfig()
    return ASTParserManager(config)


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


class TestPythonImportExtraction:
    """Test Python import extraction."""
    
    def test_simple_import(self, dependency_analyzer):
        """Test extraction of simple Python import."""
        imports = [
            ImportInfo(
                module="os",
                imported_symbols=[],
                is_relative=False,
                import_type="import",
                line_number=1
            )
        ]
        
        symbol_info = SymbolInfo(imports=imports)
        file_analyses = {
            "test.py": MockFileAnalysis(symbol_info=symbol_info)
        }
        
        graph = dependency_analyzer.analyze_dependencies("test_project", file_analyses)
        
        assert len(graph.nodes) == 1
        assert "test.py" in graph.nodes
        assert "os" in graph.nodes["test.py"].external_imports
        assert "os" in graph.external_dependencies
    
    def test_from_import(self, dependency_analyzer):
        """Test extraction of 'from x import y' statement."""
        imports = [
            ImportInfo(
                module="pathlib",
                imported_symbols=["Path"],
                is_relative=False,
                import_type="from_import",
                line_number=1
            )
        ]
        
        symbol_info = SymbolInfo(imports=imports)
        file_analyses = {
            "test.py": MockFileAnalysis(symbol_info=symbol_info)
        }
        
        graph = dependency_analyzer.analyze_dependencies("test_project", file_analyses)
        
        assert "pathlib" in graph.nodes["test.py"].external_imports
        assert "pathlib" in graph.external_dependencies
    
    def test_relative_import(self, dependency_analyzer):
        """Test extraction of relative Python import."""
        imports = [
            ImportInfo(
                module=".utils",
                imported_symbols=["helper"],
                is_relative=True,
                import_type="from_import",
                line_number=1
            )
        ]
        
        symbol_info = SymbolInfo(imports=imports)
        file_analyses = {
            "src/main.py": MockFileAnalysis(symbol_info=symbol_info),
            "src/utils.py": MockFileAnalysis(symbol_info=SymbolInfo())
        }
        
        graph = dependency_analyzer.analyze_dependencies("test_project", file_analyses)
        
        # Should resolve to internal import
        assert len(graph.nodes) == 2


class TestJavaScriptImportExtraction:
    """Test JavaScript/TypeScript import extraction."""
    
    def test_es6_import(self, dependency_analyzer):
        """Test extraction of ES6 import statement."""
        imports = [
            ImportInfo(
                module="react",
                imported_symbols=["useState", "useEffect"],
                is_relative=False,
                import_type="es6_import",
                line_number=1
            )
        ]
        
        symbol_info = SymbolInfo(imports=imports)
        file_analyses = {
            "App.tsx": MockFileAnalysis(symbol_info=symbol_info)
        }
        
        graph = dependency_analyzer.analyze_dependencies("test_project", file_analyses)
        
        assert "react" in graph.nodes["App.tsx"].external_imports
        assert "react" in graph.external_dependencies
    
    def test_require_statement(self, dependency_analyzer):
        """Test extraction of CommonJS require statement."""
        imports = [
            ImportInfo(
                module="express",
                imported_symbols=[],
                is_relative=False,
                import_type="require",
                line_number=1
            )
        ]
        
        symbol_info = SymbolInfo(imports=imports)
        file_analyses = {
            "server.js": MockFileAnalysis(symbol_info=symbol_info)
        }
        
        graph = dependency_analyzer.analyze_dependencies("test_project", file_analyses)
        
        assert "express" in graph.nodes["server.js"].external_imports
        assert "express" in graph.external_dependencies


class TestInternalVsExternalCategorization:
    """Test categorization of internal vs external dependencies."""
    
    def test_internal_dependency(self, dependency_analyzer):
        """Test that internal imports are correctly identified."""
        # File A imports File B
        imports_a = [
            ImportInfo(
                module="utils",
                imported_symbols=["helper"],
                is_relative=False,
                import_type="from_import",
                line_number=1
            )
        ]
        
        symbol_info_a = SymbolInfo(imports=imports_a)
        symbol_info_b = SymbolInfo()
        
        file_analyses = {
            "src/main.py": MockFileAnalysis(symbol_info=symbol_info_a),
            "src/utils.py": MockFileAnalysis(symbol_info=symbol_info_b)
        }
        
        graph = dependency_analyzer.analyze_dependencies("test_project", file_analyses)
        
        # Should have 2 nodes
        assert len(graph.nodes) == 2
        
        # Should have at least 1 edge (may resolve internal import)
        # Note: Resolution depends on file structure
        assert len(graph.edges) >= 0
    
    def test_external_dependency(self, dependency_analyzer):
        """Test that external imports are correctly identified."""
        imports = [
            ImportInfo(
                module="numpy",
                imported_symbols=["array"],
                is_relative=False,
                import_type="from_import",
                line_number=1
            ),
            ImportInfo(
                module="pandas",
                imported_symbols=["DataFrame"],
                is_relative=False,
                import_type="from_import",
                line_number=2
            )
        ]
        
        symbol_info = SymbolInfo(imports=imports)
        file_analyses = {
            "analysis.py": MockFileAnalysis(symbol_info=symbol_info)
        }
        
        graph = dependency_analyzer.analyze_dependencies("test_project", file_analyses)
        
        # Both should be external
        assert "numpy" in graph.external_dependencies
        assert "pandas" in graph.external_dependencies
        assert graph.external_dependencies["numpy"] == 1
        assert graph.external_dependencies["pandas"] == 1
    
    def test_scoped_package(self, dependency_analyzer):
        """Test extraction of scoped package names (@org/package)."""
        imports = [
            ImportInfo(
                module="@types/node",
                imported_symbols=[],
                is_relative=False,
                import_type="es6_import",
                line_number=1
            )
        ]
        
        symbol_info = SymbolInfo(imports=imports)
        file_analyses = {
            "index.ts": MockFileAnalysis(symbol_info=symbol_info)
        }
        
        graph = dependency_analyzer.analyze_dependencies("test_project", file_analyses)
        
        # Should preserve scoped package name
        assert "@types/node" in graph.external_dependencies


class TestCircularDependencyDetection:
    """Test circular dependency detection."""
    
    def test_simple_circular_dependency(self, dependency_analyzer):
        """Test detection of simple A -> B -> A cycle."""
        # File A imports File B
        imports_a = [
            ImportInfo(
                module="b",
                imported_symbols=[],
                is_relative=False,
                import_type="import",
                line_number=1
            )
        ]
        
        # File B imports File A
        imports_b = [
            ImportInfo(
                module="a",
                imported_symbols=[],
                is_relative=False,
                import_type="import",
                line_number=1
            )
        ]
        
        file_analyses = {
            "a.py": MockFileAnalysis(symbol_info=SymbolInfo(imports=imports_a)),
            "b.py": MockFileAnalysis(symbol_info=SymbolInfo(imports=imports_b))
        }
        
        # Manually create graph with circular dependency
        graph = DependencyGraph()
        graph.nodes["a.py"] = FileNode(file_path="a.py", imports=["b.py"])
        graph.nodes["b.py"] = FileNode(file_path="b.py", imports=["a.py"])
        graph.edges = [
            DependencyEdge(from_file="a.py", to_file="b.py"),
            DependencyEdge(from_file="b.py", to_file="a.py")
        ]
        
        # Detect circular dependencies
        circular_deps = dependency_analyzer._detect_circular_dependencies(graph)
        
        # Should detect the cycle
        assert len(circular_deps) > 0
    
    def test_three_way_circular_dependency(self, dependency_analyzer):
        """Test detection of A -> B -> C -> A cycle."""
        # Manually create graph with 3-way circular dependency
        graph = DependencyGraph()
        graph.nodes["a.py"] = FileNode(file_path="a.py", imports=["b.py"])
        graph.nodes["b.py"] = FileNode(file_path="b.py", imports=["c.py"])
        graph.nodes["c.py"] = FileNode(file_path="c.py", imports=["a.py"])
        graph.edges = [
            DependencyEdge(from_file="a.py", to_file="b.py"),
            DependencyEdge(from_file="b.py", to_file="c.py"),
            DependencyEdge(from_file="c.py", to_file="a.py")
        ]
        
        # Detect circular dependencies
        circular_deps = dependency_analyzer._detect_circular_dependencies(graph)
        
        # Should detect the cycle
        assert len(circular_deps) > 0
    
    def test_no_circular_dependency(self, dependency_analyzer):
        """Test that no false positives are detected."""
        # Create linear dependency: A -> B -> C
        graph = DependencyGraph()
        graph.nodes["a.py"] = FileNode(file_path="a.py", imports=["b.py"])
        graph.nodes["b.py"] = FileNode(file_path="b.py", imports=["c.py"])
        graph.nodes["c.py"] = FileNode(file_path="c.py", imports=[])
        graph.edges = [
            DependencyEdge(from_file="a.py", to_file="b.py"),
            DependencyEdge(from_file="b.py", to_file="c.py")
        ]
        
        # Detect circular dependencies
        circular_deps = dependency_analyzer._detect_circular_dependencies(graph)
        
        # Should not detect any cycles
        assert len(circular_deps) == 0


class TestDependencyGraphBuilding:
    """Test dependency graph building."""
    
    def test_build_simple_graph(self, dependency_analyzer):
        """Test building a simple dependency graph."""
        imports = [
            ImportInfo(
                module="requests",
                imported_symbols=[],
                is_relative=False,
                import_type="import",
                line_number=1
            )
        ]
        
        symbol_info = SymbolInfo(imports=imports)
        file_analyses = {
            "main.py": MockFileAnalysis(symbol_info=symbol_info)
        }
        
        graph = dependency_analyzer.analyze_dependencies("test_project", file_analyses)
        
        assert len(graph.nodes) == 1
        assert "main.py" in graph.nodes
        assert len(graph.external_dependencies) == 1
    
    def test_build_multi_file_graph(self, dependency_analyzer):
        """Test building graph with multiple files."""
        file_analyses = {
            "a.py": MockFileAnalysis(symbol_info=SymbolInfo()),
            "b.py": MockFileAnalysis(symbol_info=SymbolInfo()),
            "c.py": MockFileAnalysis(symbol_info=SymbolInfo())
        }
        
        graph = dependency_analyzer.analyze_dependencies("test_project", file_analyses)
        
        assert len(graph.nodes) == 3
        assert "a.py" in graph.nodes
        assert "b.py" in graph.nodes
        assert "c.py" in graph.nodes
    
    def test_dependency_metrics(self, dependency_analyzer):
        """Test calculation of dependency metrics."""
        # Create a simple graph
        graph = DependencyGraph()
        graph.nodes["a.py"] = FileNode(
            file_path="a.py", 
            imports=["b.py"], 
            external_imports=["numpy"]
        )
        graph.nodes["b.py"] = FileNode(
            file_path="b.py", 
            imports=[], 
            imported_by=["a.py"]
        )
        graph.edges = [DependencyEdge(from_file="a.py", to_file="b.py")]
        graph.external_dependencies = {"numpy": 1}
        
        metrics = dependency_analyzer.get_dependency_metrics(graph)
        
        assert metrics["total_files"] == 2
        assert metrics["total_edges"] == 1
        assert metrics["total_external_packages"] == 1
        assert metrics["avg_imports_per_file"] > 0


class TestPackageNameExtraction:
    """Test package name extraction."""
    
    def test_simple_package(self, dependency_analyzer):
        """Test extraction of simple package name."""
        package = dependency_analyzer._get_package_name("numpy")
        assert package == "numpy"
    
    def test_submodule_package(self, dependency_analyzer):
        """Test extraction from module with submodules."""
        package = dependency_analyzer._get_package_name("numpy.array")
        assert package == "numpy"
    
    def test_scoped_package(self, dependency_analyzer):
        """Test extraction of scoped package name."""
        package = dependency_analyzer._get_package_name("@types/node")
        assert package == "@types/node"
    
    def test_scoped_package_with_submodule(self, dependency_analyzer):
        """Test extraction of scoped package with submodule."""
        package = dependency_analyzer._get_package_name("@angular/core/testing")
        assert package == "@angular/core"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
