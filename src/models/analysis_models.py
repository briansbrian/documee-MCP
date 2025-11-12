"""
Data models for analysis results.

This module defines dataclasses for analysis results that can be persisted
to disk and cached in memory.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime


@dataclass
class FunctionInfo:
    """Information about a function extracted from code."""
    name: str
    parameters: List[str]
    return_type: Optional[str]
    docstring: Optional[str]
    start_line: int
    end_line: int
    complexity: int
    is_async: bool
    decorators: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FunctionInfo':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class ClassInfo:
    """Information about a class extracted from code."""
    name: str
    methods: List[FunctionInfo]
    base_classes: List[str]
    docstring: Optional[str]
    start_line: int
    end_line: int
    decorators: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        result['methods'] = [m.to_dict() if hasattr(m, 'to_dict') else m 
                            for m in self.methods]
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ClassInfo':
        """Create from dictionary."""
        methods = [FunctionInfo.from_dict(m) if isinstance(m, dict) else m 
                  for m in data.get('methods', [])]
        data_copy = data.copy()
        data_copy['methods'] = methods
        return cls(**data_copy)


@dataclass
class ImportInfo:
    """Information about an import statement."""
    module: str
    imported_symbols: List[str]
    is_relative: bool
    import_type: str  # "import", "from_import", "require", "es6_import"
    line_number: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ImportInfo':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class SymbolInfo:
    """Extracted symbols from a file."""
    functions: List[FunctionInfo]
    classes: List[ClassInfo]
    imports: List[ImportInfo]
    exports: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'functions': [f.to_dict() for f in self.functions],
            'classes': [c.to_dict() for c in self.classes],
            'imports': [i.to_dict() for i in self.imports],
            'exports': self.exports
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SymbolInfo':
        """Create from dictionary."""
        return cls(
            functions=[FunctionInfo.from_dict(f) for f in data.get('functions', [])],
            classes=[ClassInfo.from_dict(c) for c in data.get('classes', [])],
            imports=[ImportInfo.from_dict(i) for i in data.get('imports', [])],
            exports=data.get('exports', [])
        )


@dataclass
class DetectedPattern:
    """A detected coding pattern."""
    pattern_type: str  # "react_component", "api_route", etc.
    file_path: str
    confidence: float  # 0.0-1.0
    evidence: List[str]  # What triggered detection
    line_numbers: List[int]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DetectedPattern':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class ComplexityMetrics:
    """Code complexity metrics."""
    avg_complexity: float
    max_complexity: int
    min_complexity: int
    high_complexity_functions: List[str]  # Function names
    trivial_functions: List[str]  # Function names
    avg_nesting_depth: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComplexityMetrics':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class TeachingValueScore:
    """Teaching value score for a file."""
    total_score: float  # 0.0-1.0
    documentation_score: float
    complexity_score: float
    pattern_score: float
    structure_score: float
    explanation: str  # Human-readable explanation
    factors: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TeachingValueScore':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class LinterIssue:
    """Issue reported by a linter."""
    tool: str  # 'pylint', 'eslint'
    severity: str  # 'error', 'warning', 'info'
    message: str
    line: int
    column: int
    rule: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LinterIssue':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class FileAnalysis:
    """Complete analysis result for a single file."""
    file_path: str
    language: str
    symbol_info: SymbolInfo
    patterns: List[DetectedPattern]
    teaching_value: TeachingValueScore
    complexity_metrics: ComplexityMetrics
    documentation_coverage: float
    linter_issues: List[LinterIssue]
    has_errors: bool
    errors: List[str]
    analyzed_at: str  # ISO format datetime string
    cache_hit: bool
    is_notebook: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'file_path': self.file_path,
            'language': self.language,
            'symbol_info': self.symbol_info.to_dict(),
            'patterns': [p.to_dict() for p in self.patterns],
            'teaching_value': self.teaching_value.to_dict(),
            'complexity_metrics': self.complexity_metrics.to_dict(),
            'documentation_coverage': self.documentation_coverage,
            'linter_issues': [li.to_dict() for li in self.linter_issues],
            'has_errors': self.has_errors,
            'errors': self.errors,
            'analyzed_at': self.analyzed_at,
            'cache_hit': self.cache_hit,
            'is_notebook': self.is_notebook
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FileAnalysis':
        """Create from dictionary."""
        return cls(
            file_path=data['file_path'],
            language=data['language'],
            symbol_info=SymbolInfo.from_dict(data['symbol_info']),
            patterns=[DetectedPattern.from_dict(p) for p in data.get('patterns', [])],
            teaching_value=TeachingValueScore.from_dict(data['teaching_value']),
            complexity_metrics=ComplexityMetrics.from_dict(data['complexity_metrics']),
            documentation_coverage=data['documentation_coverage'],
            linter_issues=[LinterIssue.from_dict(li) for li in data.get('linter_issues', [])],
            has_errors=data['has_errors'],
            errors=data.get('errors', []),
            analyzed_at=data['analyzed_at'],
            cache_hit=data.get('cache_hit', False),
            is_notebook=data.get('is_notebook', False)
        )


@dataclass
class DependencyEdge:
    """Edge in dependency graph."""
    from_file: str
    to_file: str
    import_count: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DependencyEdge':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class FileNode:
    """Node in dependency graph."""
    file_path: str
    imports: List[str]  # Files this file imports
    imported_by: List[str]  # Files that import this file
    external_imports: List[str]  # External packages
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FileNode':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class CircularDependency:
    """Circular dependency information."""
    cycle: List[str]  # List of file paths forming the cycle
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CircularDependency':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class DependencyGraph:
    """Dependency graph for a codebase."""
    nodes: Dict[str, FileNode]
    edges: List[DependencyEdge]
    circular_dependencies: List[CircularDependency]
    external_dependencies: Dict[str, int]  # package -> usage_count
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'nodes': {k: v.to_dict() for k, v in self.nodes.items()},
            'edges': [e.to_dict() for e in self.edges],
            'circular_dependencies': [cd.to_dict() for cd in self.circular_dependencies],
            'external_dependencies': self.external_dependencies
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DependencyGraph':
        """Create from dictionary."""
        return cls(
            nodes={k: FileNode.from_dict(v) for k, v in data.get('nodes', {}).items()},
            edges=[DependencyEdge.from_dict(e) for e in data.get('edges', [])],
            circular_dependencies=[CircularDependency.from_dict(cd) 
                                  for cd in data.get('circular_dependencies', [])],
            external_dependencies=data.get('external_dependencies', {})
        )


@dataclass
class CodebaseMetrics:
    """Metrics for entire codebase."""
    total_files: int
    total_functions: int
    total_classes: int
    avg_complexity: float
    avg_documentation_coverage: float
    total_patterns_detected: int
    analysis_time_ms: float
    cache_hit_rate: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CodebaseMetrics':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class CodebaseAnalysis:
    """Complete analysis result for a codebase."""
    codebase_id: str
    file_analyses: Dict[str, FileAnalysis]
    dependency_graph: DependencyGraph
    global_patterns: List[DetectedPattern]
    top_teaching_files: List[Tuple[str, float]]  # (file_path, score)
    metrics: CodebaseMetrics
    analyzed_at: str  # ISO format datetime string
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'codebase_id': self.codebase_id,
            'file_analyses': {k: v.to_dict() for k, v in self.file_analyses.items()},
            'dependency_graph': self.dependency_graph.to_dict(),
            'global_patterns': [p.to_dict() for p in self.global_patterns],
            'top_teaching_files': self.top_teaching_files,
            'metrics': self.metrics.to_dict(),
            'analyzed_at': self.analyzed_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CodebaseAnalysis':
        """Create from dictionary."""
        return cls(
            codebase_id=data['codebase_id'],
            file_analyses={k: FileAnalysis.from_dict(v) 
                          for k, v in data.get('file_analyses', {}).items()},
            dependency_graph=DependencyGraph.from_dict(data['dependency_graph']),
            global_patterns=[DetectedPattern.from_dict(p) 
                           for p in data.get('global_patterns', [])],
            top_teaching_files=data.get('top_teaching_files', []),
            metrics=CodebaseMetrics.from_dict(data['metrics']),
            analyzed_at=data['analyzed_at']
        )
