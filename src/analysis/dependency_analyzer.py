"""
Dependency Analyzer for analyzing import relationships and building dependency graphs.

This module extracts import statements, builds dependency graphs, detects circular
dependencies, and categorizes dependencies as internal vs external.
"""

import logging
from typing import List, Dict, Set, Optional, Tuple, Any
from dataclasses import dataclass, field
from pathlib import Path
import os

from .symbol_extractor import SymbolInfo, ImportInfo

logger = logging.getLogger(__name__)


@dataclass
class FileNode:
    """Node in the dependency graph representing a file.
    
    Attributes:
        file_path: Path to the file
        imports: List of file paths this file imports
        imported_by: List of file paths that import this file
        external_imports: List of external package names
    """
    file_path: str
    imports: List[str] = field(default_factory=list)
    imported_by: List[str] = field(default_factory=list)
    external_imports: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        from dataclasses import asdict
        return asdict(self)


@dataclass
class DependencyEdge:
    """Edge in the dependency graph representing an import relationship.
    
    Attributes:
        from_file: Source file path
        to_file: Target file path
        import_count: Number of imports between these files
    """
    from_file: str
    to_file: str
    import_count: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        from dataclasses import asdict
        return asdict(self)


@dataclass
class CircularDependency:
    """Represents a circular dependency cycle.
    
    Attributes:
        cycle: List of file paths forming the cycle
        severity: Severity level ('warning', 'error')
    """
    cycle: List[str]
    severity: str = 'warning'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        from dataclasses import asdict
        return asdict(self)


@dataclass
class DependencyGraph:
    """Complete dependency graph for a codebase.
    
    Attributes:
        nodes: Dictionary mapping file paths to FileNode objects
        edges: List of dependency edges
        circular_dependencies: List of detected circular dependencies
        external_dependencies: Dictionary mapping package names to usage counts
    """
    nodes: Dict[str, FileNode] = field(default_factory=dict)
    edges: List[DependencyEdge] = field(default_factory=list)
    circular_dependencies: List[CircularDependency] = field(default_factory=list)
    external_dependencies: Dict[str, int] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'nodes': {k: v.to_dict() for k, v in self.nodes.items()},
            'edges': [e.to_dict() for e in self.edges],
            'circular_dependencies': [c.to_dict() for c in self.circular_dependencies],
            'external_dependencies': self.external_dependencies
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DependencyGraph':
        """Create from dictionary."""
        return cls(
            nodes={k: FileNode(**v) if isinstance(v, dict) else v 
                  for k, v in data.get('nodes', {}).items()},
            edges=[DependencyEdge(**e) if isinstance(e, dict) else e 
                  for e in data.get('edges', [])],
            circular_dependencies=[CircularDependency(**c) if isinstance(c, dict) else c 
                                  for c in data.get('circular_dependencies', [])],
            external_dependencies=data.get('external_dependencies', {})
        )


class DependencyAnalyzer:
    """
    Analyzes dependencies between files and builds dependency graphs.
    
    Supports Python and JavaScript/TypeScript import statements.
    Detects circular dependencies and categorizes internal vs external dependencies.
    """
    
    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize the Dependency Analyzer.
        
        Args:
            project_root: Root directory of the project (for resolving relative imports)
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        logger.debug(f"DependencyAnalyzer initialized with project_root: {self.project_root}")
    
    def analyze_dependencies(
        self, 
        codebase_id: str, 
        file_analyses: Dict[str, Any]
    ) -> DependencyGraph:
        """
        Build dependency graph for entire codebase.
        
        Args:
            codebase_id: Identifier for the codebase
            file_analyses: Dictionary mapping file paths to FileAnalysis objects
        
        Returns:
            DependencyGraph with all dependencies mapped
        
        Example:
            >>> graph = analyzer.analyze_dependencies("my_project", file_analyses)
            >>> print(f"Found {len(graph.circular_dependencies)} circular dependencies")
        """
        logger.info(f"Analyzing dependencies for codebase: {codebase_id}")
        
        graph = DependencyGraph()
        
        # Build nodes and extract imports
        for file_path, file_analysis in file_analyses.items():
            node = FileNode(file_path=file_path)
            
            # Extract imports from symbol info
            symbol_info = file_analysis.symbol_info
            for import_info in symbol_info.imports:
                # Categorize as internal or external
                resolved_path = self._resolve_import_path(
                    import_info, 
                    file_path, 
                    file_analyses
                )
                
                if resolved_path:
                    # Internal dependency
                    node.imports.append(resolved_path)
                else:
                    # External dependency
                    node.external_imports.append(import_info.module)
                    
                    # Track external dependency usage
                    package_name = self._get_package_name(import_info.module)
                    graph.external_dependencies[package_name] = \
                        graph.external_dependencies.get(package_name, 0) + 1
            
            graph.nodes[file_path] = node
        
        # Build edges and reverse relationships
        for file_path, node in graph.nodes.items():
            for imported_file in node.imports:
                # Add edge
                edge = DependencyEdge(
                    from_file=file_path,
                    to_file=imported_file,
                    import_count=1
                )
                graph.edges.append(edge)
                
                # Update imported_by relationship
                if imported_file in graph.nodes:
                    graph.nodes[imported_file].imported_by.append(file_path)
        
        # Detect circular dependencies
        graph.circular_dependencies = self._detect_circular_dependencies(graph)
        
        logger.info(
            f"Dependency analysis complete: "
            f"{len(graph.nodes)} files, "
            f"{len(graph.edges)} edges, "
            f"{len(graph.circular_dependencies)} circular dependencies, "
            f"{len(graph.external_dependencies)} external packages"
        )
        
        return graph
    
    def _resolve_import_path(
        self, 
        import_info: ImportInfo, 
        source_file: str,
        file_analyses: Dict[str, Any]
    ) -> Optional[str]:
        """
        Resolve import statement to absolute file path.
        
        Args:
            import_info: Import information
            source_file: Path to file containing the import
            file_analyses: Dictionary of all analyzed files
        
        Returns:
            Absolute file path if internal import, None if external
        """
        module = import_info.module
        
        # Handle relative imports
        if import_info.is_relative:
            return self._resolve_relative_import(module, source_file, file_analyses)
        
        # Handle absolute imports
        return self._resolve_absolute_import(module, source_file, file_analyses)
    
    def _resolve_relative_import(
        self, 
        module: str, 
        source_file: str,
        file_analyses: Dict[str, Any]
    ) -> Optional[str]:
        """
        Resolve relative import to absolute path.
        
        Handles Python relative imports like:
        - from . import module
        - from .. import module
        - from .submodule import function
        
        Args:
            module: Module name (may start with dots)
            source_file: Path to file containing the import
            file_analyses: Dictionary of all analyzed files
        
        Returns:
            Absolute file path if found, None otherwise
        """
        source_dir = Path(source_file).parent
        
        # Count leading dots
        dots = 0
        for char in module:
            if char == '.':
                dots += 1
            else:
                break
        
        # Remove leading dots
        module_name = module[dots:].strip('.')
        
        # Go up directory tree based on dot count
        current_dir = source_dir
        for _ in range(dots - 1):
            current_dir = current_dir.parent
        
        # Try to find the module file
        if module_name:
            # from .module import x
            possible_paths = [
                current_dir / f"{module_name}.py",
                current_dir / module_name / "__init__.py",
            ]
        else:
            # from . import x (imports from __init__.py)
            possible_paths = [
                current_dir / "__init__.py",
            ]
        
        # Check which path exists in file_analyses
        for path in possible_paths:
            normalized_path = str(path).replace('\\', '/')
            for analyzed_file in file_analyses.keys():
                if normalized_path in analyzed_file or analyzed_file in normalized_path:
                    return analyzed_file
        
        return None
    
    def _resolve_absolute_import(
        self, 
        module: str, 
        source_file: str,
        file_analyses: Dict[str, Any]
    ) -> Optional[str]:
        """
        Resolve absolute import to file path.
        
        Handles imports like:
        - import module
        - from package.module import function
        
        Args:
            module: Module name
            source_file: Path to file containing the import
            file_analyses: Dictionary of all analyzed files
        
        Returns:
            Absolute file path if internal import, None if external
        """
        # Convert module path to file path
        # e.g., "src.utils.helpers" -> "src/utils/helpers.py"
        module_path = module.replace('.', '/')
        
        # Try different file extensions and patterns
        possible_paths = [
            f"{module_path}.py",
            f"{module_path}.js",
            f"{module_path}.ts",
            f"{module_path}.tsx",
            f"{module_path}.jsx",
            f"{module_path}/__init__.py",
            f"{module_path}/index.js",
            f"{module_path}/index.ts",
        ]
        
        # Check if any analyzed file matches
        for analyzed_file in file_analyses.keys():
            normalized_analyzed = analyzed_file.replace('\\', '/')
            
            for possible_path in possible_paths:
                if possible_path in normalized_analyzed or normalized_analyzed.endswith(possible_path):
                    return analyzed_file
        
        # Not found in analyzed files - likely external dependency
        return None
    
    def _get_package_name(self, module: str) -> str:
        """
        Extract package name from module path.
        
        Examples:
            "numpy.array" -> "numpy"
            "react" -> "react"
            "@types/node" -> "@types/node"
        
        Args:
            module: Full module path
        
        Returns:
            Package name
        """
        # Handle scoped packages (@org/package)
        if module.startswith('@'):
            parts = module.split('/')
            if len(parts) >= 2:
                return f"{parts[0]}/{parts[1]}"
            return module
        
        # Regular packages
        return module.split('.')[0].split('/')[0]
    
    def _detect_circular_dependencies(self, graph: DependencyGraph) -> List[CircularDependency]:
        """
        Detect circular dependencies using depth-first search.
        
        Uses DFS with a recursion stack to detect cycles in the dependency graph.
        
        Args:
            graph: Dependency graph to analyze
        
        Returns:
            List of detected circular dependencies
        """
        logger.debug("Detecting circular dependencies...")
        
        circular_deps = []
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        path: List[str] = []
        
        def dfs(node_path: str) -> bool:
            """
            Depth-first search to detect cycles.
            
            Returns True if cycle detected.
            """
            visited.add(node_path)
            rec_stack.add(node_path)
            path.append(node_path)
            
            # Check all dependencies
            node = graph.nodes.get(node_path)
            if node:
                for imported_file in node.imports:
                    if imported_file not in visited:
                        if dfs(imported_file):
                            return True
                    elif imported_file in rec_stack:
                        # Cycle detected!
                        cycle_start = path.index(imported_file)
                        cycle = path[cycle_start:] + [imported_file]
                        
                        circular_deps.append(CircularDependency(
                            cycle=cycle,
                            severity='warning'
                        ))
                        
                        logger.warning(f"Circular dependency detected: {' -> '.join(cycle)}")
                        return True
            
            path.pop()
            rec_stack.remove(node_path)
            return False
        
        # Run DFS from each unvisited node
        for node_path in graph.nodes.keys():
            if node_path not in visited:
                dfs(node_path)
        
        logger.debug(f"Found {len(circular_deps)} circular dependencies")
        
        return circular_deps
    
    def get_dependency_metrics(self, graph: DependencyGraph) -> Dict[str, Any]:
        """
        Calculate dependency metrics for the graph.
        
        Args:
            graph: Dependency graph
        
        Returns:
            Dictionary of metrics
        """
        total_files = len(graph.nodes)
        total_edges = len(graph.edges)
        total_external = len(graph.external_dependencies)
        total_circular = len(graph.circular_dependencies)
        
        # Calculate average dependencies per file
        if total_files > 0:
            avg_imports = sum(len(node.imports) for node in graph.nodes.values()) / total_files
            avg_imported_by = sum(len(node.imported_by) for node in graph.nodes.values()) / total_files
        else:
            avg_imports = 0
            avg_imported_by = 0
        
        # Find most imported files
        most_imported = sorted(
            [(path, len(node.imported_by)) for path, node in graph.nodes.items()],
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # Find files with most imports
        most_imports = sorted(
            [(path, len(node.imports)) for path, node in graph.nodes.items()],
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return {
            'total_files': total_files,
            'total_edges': total_edges,
            'total_external_packages': total_external,
            'total_circular_dependencies': total_circular,
            'avg_imports_per_file': round(avg_imports, 2),
            'avg_imported_by_per_file': round(avg_imported_by, 2),
            'most_imported_files': most_imported,
            'most_imports_files': most_imports,
            'external_dependencies': graph.external_dependencies
        }
