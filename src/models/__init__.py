"""Data models and schemas."""

from .schemas import (
    ScanResult,
    Framework,
    FrameworkDetectionResult,
    Feature,
    FeatureDiscoveryResult,
)

from .analysis_models import (
    FunctionInfo,
    ClassInfo,
    ImportInfo,
    SymbolInfo,
    DetectedPattern,
    ComplexityMetrics,
    TeachingValueScore,
    LinterIssue,
    FileAnalysis,
    DependencyEdge,
    FileNode,
    CircularDependency,
    DependencyGraph,
    CodebaseMetrics,
    CodebaseAnalysis,
)

__all__ = [
    "ScanResult",
    "Framework",
    "FrameworkDetectionResult",
    "Feature",
    "FeatureDiscoveryResult",
    "FunctionInfo",
    "ClassInfo",
    "ImportInfo",
    "SymbolInfo",
    "DetectedPattern",
    "ComplexityMetrics",
    "TeachingValueScore",
    "LinterIssue",
    "FileAnalysis",
    "DependencyEdge",
    "FileNode",
    "CircularDependency",
    "DependencyGraph",
    "CodebaseMetrics",
    "CodebaseAnalysis",
]
