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

__all__ = [
    'AnalysisEngine',
    'AnalysisConfig',
    'ASTParserManager',
    'ParseResult',
    'ComplexityAnalyzer',
    'ComplexityMetrics',
    'DocumentationCoverageAnalyzer',
    'DocumentationCoverage'
]
