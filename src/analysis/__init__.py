"""
Analysis Engine for Documee MCP Server.

This module provides deep code analysis capabilities including:
- AST parsing for multiple languages
- Symbol extraction (functions, classes)
- Pattern detection
- Dependency analysis
- Teaching value scoring
"""

from .engine import AnalysisEngine
from .config import AnalysisConfig
from .ast_parser import ASTParserManager, ParseResult
from .complexity_analyzer import ComplexityAnalyzer, ComplexityMetrics
from .documentation_coverage import DocumentationCoverageAnalyzer, DocumentationCoverage
from .teaching_value_scorer import TeachingValueScorer, TeachingValueScore
from .pattern_detector import (
    PatternDetector,
    BasePatternDetector,
    DetectedPattern,
    ReactPatternDetector,
    APIPatternDetector,
    DatabasePatternDetector,
    AuthPatternDetector
)
from .language_pattern_detector import (
    PythonPatternDetector,
    JavaScriptPatternDetector
)
from .universal_language_detectors import (
    JavaPatternDetector,
    GoPatternDetector,
    RustPatternDetector,
    CppPatternDetector,
    CSharpPatternDetector,
    RubyPatternDetector,
    PHPPatternDetector
)
from .dependency_analyzer import (
    DependencyAnalyzer,
    DependencyGraph,
    FileNode,
    DependencyEdge,
    CircularDependency
)
from .persistence import PersistenceManager
from .linter_integration import LinterIntegration
from .notebook_analyzer import NotebookAnalyzer, NotebookCode, CodeCell

__all__ = [
    'AnalysisEngine',
    'AnalysisConfig',
    'ASTParserManager',
    'ParseResult',
    'ComplexityAnalyzer',
    'ComplexityMetrics',
    'DocumentationCoverageAnalyzer',
    'DocumentationCoverage',
    'TeachingValueScorer',
    'TeachingValueScore',
    'PatternDetector',
    'BasePatternDetector',
    'DetectedPattern',
    'ReactPatternDetector',
    'APIPatternDetector',
    'DatabasePatternDetector',
    'AuthPatternDetector',
    'PythonPatternDetector',
    'JavaScriptPatternDetector',
    'JavaPatternDetector',
    'GoPatternDetector',
    'RustPatternDetector',
    'CppPatternDetector',
    'CSharpPatternDetector',
    'RubyPatternDetector',
    'PHPPatternDetector',
    'DependencyAnalyzer',
    'DependencyGraph',
    'FileNode',
    'DependencyEdge',
    'CircularDependency',
    'PersistenceManager',
    'LinterIntegration',
    'NotebookAnalyzer',
    'NotebookCode',
    'CodeCell'
]
