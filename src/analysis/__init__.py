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
from .dependency_analyzer import (
    DependencyAnalyzer,
    DependencyGraph,
    FileNode,
    DependencyEdge,
    CircularDependency
)
from .persistence import PersistenceManager

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
    'DependencyAnalyzer',
    'DependencyGraph',
    'FileNode',
    'DependencyEdge',
    'CircularDependency',
    'PersistenceManager'
]
