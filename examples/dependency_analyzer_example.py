"""
Example usage of the Dependency Analyzer.

This script demonstrates how to use the DependencyAnalyzer to:
1. Extract import statements from files
2. Build dependency graphs
3. Detect circular dependencies
4. Categorize internal vs external dependencies
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analysis.dependency_analyzer import DependencyAnalyzer
from src.analysis.symbol_extractor import SymbolInfo, ImportInfo
from dataclasses import dataclass, field


@dataclass
class MockFileAnalysis:
    """Mock FileAnalysis for demonstration."""
    symbol_info: SymbolInfo = field(default_factory=SymbolInfo)


def example_simple_dependency_graph():
    """Example: Build a simple dependency graph."""
    print("=" * 60)
    print("Example 1: Simple Dependency Graph")
    print("=" * 60)
    
    analyzer = DependencyAnalyzer(project_root=".")
    
    # Create mock file analyses
    file_analyses = {
        "src/main.py": MockFileAnalysis(
            symbol_info=SymbolInfo(imports=[
                ImportInfo(module="numpy", imported_symbols=["array"], 
                          is_relative=False, import_type="from_import", line_number=1),
                ImportInfo(module="pandas", imported_symbols=["DataFrame"], 
                          is_relative=False, import_type="from_import", line_number=2),
            ])
        ),
        "src/utils.py": MockFileAnalysis(
            symbol_info=SymbolInfo(imports=[
                ImportInfo(module="os", imported_symbols=[], 
                          is_relative=False, import_type="import", line_number=1),
            ])
        ),
    }
    
    # Analyze dependencies
    graph = analyzer.analyze_dependencies("example_project", file_analyses)
    
    print(f"\nTotal files: {len(graph.nodes)}")
    print(f"Total edges: {len(graph.edges)}")
    print(f"External packages: {len(graph.external_dependencies)}")
    print(f"\nExternal dependencies:")
    for package, count in graph.external_dependencies.items():
        print(f"  - {package}: {count} import(s)")
    
    # Get metrics
    metrics = analyzer.get_dependency_metrics(graph)
    print(f"\nMetrics:")
    print(f"  - Average imports per file: {metrics['avg_imports_per_file']}")
    print(f"  - Average imported by per file: {metrics['avg_imported_by_per_file']}")


def example_circular_dependency_detection():
    """Example: Detect circular dependencies."""
    print("\n" + "=" * 60)
    print("Example 2: Circular Dependency Detection")
    print("=" * 60)
    
    analyzer = DependencyAnalyzer(project_root=".")
    
    # Create mock file analyses with circular dependency
    # File A imports File B, File B imports File A
    file_analyses = {
        "module_a.py": MockFileAnalysis(
            symbol_info=SymbolInfo(imports=[
                ImportInfo(module="module_b", imported_symbols=["function_b"], 
                          is_relative=False, import_type="from_import", line_number=1),
            ])
        ),
        "module_b.py": MockFileAnalysis(
            symbol_info=SymbolInfo(imports=[
                ImportInfo(module="module_a", imported_symbols=["function_a"], 
                          is_relative=False, import_type="from_import", line_number=1),
            ])
        ),
    }
    
    # Manually create graph with circular dependency for demonstration
    from src.analysis.dependency_analyzer import DependencyGraph, FileNode, DependencyEdge
    
    graph = DependencyGraph()
    graph.nodes["module_a.py"] = FileNode(file_path="module_a.py", imports=["module_b.py"])
    graph.nodes["module_b.py"] = FileNode(file_path="module_b.py", imports=["module_a.py"])
    graph.edges = [
        DependencyEdge(from_file="module_a.py", to_file="module_b.py"),
        DependencyEdge(from_file="module_b.py", to_file="module_a.py")
    ]
    
    # Detect circular dependencies
    circular_deps = analyzer._detect_circular_dependencies(graph)
    
    print(f"\nCircular dependencies found: {len(circular_deps)}")
    for i, circular_dep in enumerate(circular_deps, 1):
        print(f"\nCircular dependency #{i}:")
        print(f"  Cycle: {' -> '.join(circular_dep.cycle)}")
        print(f"  Severity: {circular_dep.severity}")


def example_internal_vs_external():
    """Example: Categorize internal vs external dependencies."""
    print("\n" + "=" * 60)
    print("Example 3: Internal vs External Dependencies")
    print("=" * 60)
    
    analyzer = DependencyAnalyzer(project_root=".")
    
    # Create mock file analyses
    file_analyses = {
        "src/api/routes.py": MockFileAnalysis(
            symbol_info=SymbolInfo(imports=[
                # External dependencies
                ImportInfo(module="fastapi", imported_symbols=["FastAPI"], 
                          is_relative=False, import_type="from_import", line_number=1),
                ImportInfo(module="pydantic", imported_symbols=["BaseModel"], 
                          is_relative=False, import_type="from_import", line_number=2),
                # Internal dependency (relative import)
                ImportInfo(module=".models", imported_symbols=["User"], 
                          is_relative=True, import_type="from_import", line_number=3),
            ])
        ),
        "src/api/models.py": MockFileAnalysis(
            symbol_info=SymbolInfo(imports=[
                ImportInfo(module="sqlalchemy", imported_symbols=["Column", "String"], 
                          is_relative=False, import_type="from_import", line_number=1),
            ])
        ),
    }
    
    # Analyze dependencies
    graph = analyzer.analyze_dependencies("api_project", file_analyses)
    
    print(f"\nFile dependency breakdown:")
    for file_path, node in graph.nodes.items():
        print(f"\n{file_path}:")
        print(f"  Internal imports: {len(node.imports)}")
        if node.imports:
            for imp in node.imports:
                print(f"    - {imp}")
        print(f"  External imports: {len(node.external_imports)}")
        if node.external_imports:
            for imp in node.external_imports:
                print(f"    - {imp}")
    
    print(f"\n\nExternal packages used:")
    for package, count in sorted(graph.external_dependencies.items()):
        print(f"  - {package}: {count} import(s)")


def example_scoped_packages():
    """Example: Handle scoped packages (@org/package)."""
    print("\n" + "=" * 60)
    print("Example 4: Scoped Package Names")
    print("=" * 60)
    
    analyzer = DependencyAnalyzer(project_root=".")
    
    # Create mock file analyses with scoped packages
    file_analyses = {
        "src/index.ts": MockFileAnalysis(
            symbol_info=SymbolInfo(imports=[
                ImportInfo(module="@types/node", imported_symbols=[], 
                          is_relative=False, import_type="es6_import", line_number=1),
                ImportInfo(module="@angular/core", imported_symbols=["Component"], 
                          is_relative=False, import_type="es6_import", line_number=2),
                ImportInfo(module="react", imported_symbols=["useState"], 
                          is_relative=False, import_type="es6_import", line_number=3),
            ])
        ),
    }
    
    # Analyze dependencies
    graph = analyzer.analyze_dependencies("typescript_project", file_analyses)
    
    print(f"\nScoped packages detected:")
    for package, count in graph.external_dependencies.items():
        if package.startswith('@'):
            print(f"  - {package}: {count} import(s)")
    
    print(f"\nRegular packages detected:")
    for package, count in graph.external_dependencies.items():
        if not package.startswith('@'):
            print(f"  - {package}: {count} import(s)")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("DEPENDENCY ANALYZER EXAMPLES")
    print("=" * 60)
    
    example_simple_dependency_graph()
    example_circular_dependency_detection()
    example_internal_vs_external()
    example_scoped_packages()
    
    print("\n" + "=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
