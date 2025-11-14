"""
Architecture Context Extractor for AI Content Enrichment.

This module extracts architectural context from code analysis, including
component roles, data flow, interaction diagrams, dependencies, and design patterns.
Provides evidence-based architectural understanding for enrichment guides.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from src.models.analysis_models import FileAnalysis, DetectedPattern
from src.analysis.dependency_analyzer import DependencyGraph
from src.course.enrichment_models import ArchitectureContext

logger = logging.getLogger(__name__)


class ArchitectureExtractor:
    """
    Extracts architectural context with evidence from code analysis.
    
    Provides methods to:
    - Extract component role in the system
    - Trace data flow through components
    - Generate interaction diagrams (Mermaid)
    - Extract dependencies with evidence
    - Identify design patterns with evidence
    """
    
    def __init__(self, repo_path: str):
        """
        Initialize architecture extractor.
        
        Args:
            repo_path: Path to the repository root
        """
        self.repo_path = Path(repo_path).resolve()
        logger.info(f"Initialized ArchitectureExtractor for: {self.repo_path}")
    
    def extract_architecture_context(
        self,
        file_analysis: FileAnalysis,
        dependency_graph: DependencyGraph
    ) -> ArchitectureContext:
        """
        Extract complete architecture context for a file.
        
        Args:
            file_analysis: FileAnalysis object with symbols and patterns
            dependency_graph: DependencyGraph with all dependencies
            
        Returns:
            ArchitectureContext with all architectural information
        """
        logger.info(f"Extracting architecture context for: {file_analysis.file_path}")
        
        # Extract component role
        component_role = self.extract_component_role(
            file_analysis,
            dependency_graph
        )
        
        # Extract data flow
        data_flow = self.extract_data_flow(
            file_analysis,
            dependency_graph
        )
        
        # Generate interaction diagram
        interaction_diagram = self.generate_interaction_diagram(
            file_analysis,
            dependency_graph
        )
        
        # Extract dependencies with evidence
        dependencies = self.extract_dependencies_with_evidence(file_analysis)
        
        # Extract dependents (what depends on this file)
        dependents = self._extract_dependents_with_evidence(
            file_analysis,
            dependency_graph
        )
        
        # Identify design patterns
        design_patterns = self.extract_design_patterns(
            file_analysis,
            file_analysis.patterns
        )
        
        architecture_context = ArchitectureContext(
            component_role=component_role,
            data_flow=data_flow,
            interaction_diagram=interaction_diagram,
            dependencies=dependencies,
            dependents=dependents,
            design_patterns=design_patterns
        )
        
        logger.info(
            f"Extracted architecture context: "
            f"{len(dependencies)} dependencies, "
            f"{len(dependents)} dependents, "
            f"{len(design_patterns)} design patterns"
        )
        
        return architecture_context

    
    def extract_component_role(
        self,
        file_analysis: FileAnalysis,
        dependency_graph: DependencyGraph
    ) -> str:
        """
        Extract component role in system with evidence from dependency graph.
        
        Analyzes the file's position in the dependency graph, its patterns,
        and its relationships to determine its architectural role.
        
        Args:
            file_analysis: FileAnalysis object
            dependency_graph: DependencyGraph with all dependencies
            
        Returns:
            Description of component's role with evidence citations
        """
        file_path = file_analysis.file_path
        role_parts = []
        
        # Get node from dependency graph
        node = dependency_graph.nodes.get(file_path)
        
        if not node:
            logger.warning(f"File {file_path} not found in dependency graph")
            return "Component role could not be determined (file not in dependency graph)"
        
        # Analyze based on dependency patterns
        num_imports = len(node.imports)
        num_imported_by = len(node.imported_by)
        
        # Determine layer based on dependencies
        if num_imported_by > num_imports * 2:
            # Many files depend on this, few dependencies
            role_parts.append(
                f"Core utility component (imported by {num_imported_by} files, "
                f"imports {num_imports} files)"
            )
        elif num_imports > num_imported_by * 2:
            # Many dependencies, few dependents
            role_parts.append(
                f"High-level orchestrator (imports {num_imports} files, "
                f"imported by {num_imported_by} files)"
            )
        elif num_imported_by == 0:
            # Nothing depends on this
            role_parts.append(
                f"Entry point or standalone component (no files import this)"
            )
        elif num_imports == 0:
            # No dependencies
            role_parts.append(
                f"Leaf component with no dependencies (imported by {num_imported_by} files)"
            )
        else:
            # Balanced
            role_parts.append(
                f"Intermediate component (imports {num_imports} files, "
                f"imported by {num_imported_by} files)"
            )
        
        # Analyze based on detected patterns
        pattern_roles = self._infer_role_from_patterns(file_analysis.patterns)
        if pattern_roles:
            role_parts.extend(pattern_roles)
        
        # Analyze based on file path
        path_role = self._infer_role_from_path(file_path)
        if path_role:
            role_parts.append(path_role)
        
        # Combine role descriptions
        if len(role_parts) == 1:
            return role_parts[0]
        else:
            return f"{role_parts[0]}. {' '.join(role_parts[1:])}"
    
    def _infer_role_from_patterns(
        self,
        patterns: List[DetectedPattern]
    ) -> List[str]:
        """
        Infer architectural role from detected patterns.
        
        Args:
            patterns: List of detected patterns
            
        Returns:
            List of role descriptions
        """
        roles = []
        
        pattern_types = {p.pattern_type for p in patterns}
        
        if 'api_endpoint' in pattern_types or 'route' in pattern_types:
            roles.append("Serves as API/route handler for external requests")
        
        if 'database_operation' in pattern_types:
            roles.append("Manages data persistence and database interactions")
        
        if 'authentication' in pattern_types:
            roles.append("Handles authentication and security concerns")
        
        if 'validation' in pattern_types:
            roles.append("Validates data integrity and business rules")
        
        if 'caching' in pattern_types:
            roles.append("Implements caching for performance optimization")
        
        if 'error_handling' in pattern_types:
            roles.append("Provides error handling and recovery mechanisms")
        
        if 'logging' in pattern_types:
            roles.append("Implements logging and observability")
        
        if 'component' in pattern_types:
            roles.append("Provides UI component for user interface")
        
        return roles
    
    def _infer_role_from_path(self, file_path: str) -> Optional[str]:
        """
        Infer architectural role from file path.
        
        Args:
            file_path: Path to file
            
        Returns:
            Role description or None
        """
        path_lower = file_path.lower()
        
        # Common architectural patterns in paths
        if '/models/' in path_lower or '/schemas/' in path_lower:
            return "Defines data models and schemas"
        
        if '/controllers/' in path_lower or '/handlers/' in path_lower:
            return "Acts as controller/handler in MVC architecture"
        
        if '/services/' in path_lower:
            return "Implements business logic as a service"
        
        if '/repositories/' in path_lower or '/dao/' in path_lower:
            return "Provides data access layer (repository pattern)"
        
        if '/utils/' in path_lower or '/helpers/' in path_lower:
            return "Provides utility functions and helpers"
        
        if '/middleware/' in path_lower:
            return "Acts as middleware in request processing pipeline"
        
        if '/views/' in path_lower or '/templates/' in path_lower:
            return "Provides view/template for presentation layer"
        
        if '/components/' in path_lower:
            return "Provides reusable UI component"
        
        if '/api/' in path_lower or '/routes/' in path_lower:
            return "Defines API routes and endpoints"
        
        if '/config/' in path_lower or '/settings/' in path_lower:
            return "Manages configuration and settings"
        
        if '/tests/' in path_lower or 'test_' in path_lower:
            return "Provides test coverage for functionality"
        
        return None

    
    def extract_data_flow(
        self,
        file_analysis: FileAnalysis,
        dependency_graph: DependencyGraph
    ) -> str:
        """
        Trace data movement through the component with code citations.
        
        Analyzes function calls, data transformations, and dependencies
        to describe how data flows through this component.
        
        Args:
            file_analysis: FileAnalysis object
            dependency_graph: DependencyGraph with dependencies
            
        Returns:
            Description of data flow with code citations
        """
        flow_steps = []
        
        # Analyze imports to understand data sources
        if file_analysis.symbol_info.imports:
            import_sources = []
            for imp in file_analysis.symbol_info.imports[:5]:  # Limit to first 5
                if imp.imported_symbols:
                    symbols = ', '.join(imp.imported_symbols[:3])
                    import_sources.append(f"{symbols} from {imp.module}")
                else:
                    import_sources.append(imp.module)
            
            if import_sources:
                flow_steps.append(
                    f"Data enters from imported modules: {', '.join(import_sources)}"
                )
        
        # Analyze function parameters and returns
        functions = file_analysis.symbol_info.functions
        if functions:
            # Find main processing functions (not private, not __init__)
            main_funcs = [
                f for f in functions 
                if not f.name.startswith('_') and f.name not in ['__init__', '__str__', '__repr__']
            ]
            
            if main_funcs:
                func = main_funcs[0]
                
                # Describe input
                if func.parameters:
                    params = ', '.join(func.parameters[:3])
                    flow_steps.append(
                        f"Function {func.name}() receives data via parameters: {params} "
                        f"(line {func.start_line})"
                    )
                
                # Describe processing
                flow_steps.append(
                    f"Data is processed in {func.name}() "
                    f"(lines {func.start_line}-{func.end_line})"
                )
                
                # Describe output
                if func.return_type:
                    flow_steps.append(
                        f"Returns {func.return_type} to caller"
                    )
                else:
                    flow_steps.append("Returns processed result to caller")
        
        # Analyze classes and their methods
        classes = file_analysis.symbol_info.classes
        if classes:
            cls = classes[0]
            
            # Check for data storage (attributes)
            # Note: ClassInfo doesn't track attributes, so we skip this check
            # If needed in the future, add attributes field to ClassInfo model
            if hasattr(cls, 'attributes') and cls.attributes:
                attrs = ', '.join(cls.attributes[:3])
                flow_steps.append(
                    f"Class {cls.name} stores data in attributes: {attrs} "
                    f"(line {cls.start_line})"
                )
            
            # Check for data transformation methods
            transform_methods = [
                m for m in cls.methods 
                if any(keyword in m.name.lower() for keyword in 
                       ['process', 'transform', 'convert', 'parse', 'format', 'build'])
            ]
            
            if transform_methods:
                method = transform_methods[0]
                flow_steps.append(
                    f"Data is transformed by {cls.name}.{method.name}() "
                    f"(line {method.start_line})"
                )
        
        # Analyze patterns for data flow
        for pattern in file_analysis.patterns:
            if pattern.pattern_type == 'database_operation':
                operation = pattern.metadata.get('operation', 'query')
                flow_steps.append(
                    f"Data flows to/from database via {operation} operation "
                    f"(line {pattern.line_number})"
                )
            
            elif pattern.pattern_type == 'api_endpoint':
                method = pattern.metadata.get('method', 'GET')
                flow_steps.append(
                    f"Data is received/sent via {method} HTTP request "
                    f"(line {pattern.line_number})"
                )
            
            elif pattern.pattern_type == 'caching':
                flow_steps.append(
                    f"Data may be cached for performance "
                    f"(line {pattern.line_number})"
                )
        
        # Analyze exports to understand data destinations
        if file_analysis.symbol_info.exports:
            export_names = ', '.join(file_analysis.symbol_info.exports[:5])
            flow_steps.append(
                f"Data/functionality is exported for use by other modules: {export_names}"
            )
        
        # Combine flow steps
        if flow_steps:
            return ' → '.join(flow_steps)
        else:
            return "Data flow could not be determined from available analysis"

    
    def generate_interaction_diagram(
        self,
        file_analysis: FileAnalysis,
        dependency_graph: DependencyGraph
    ) -> str:
        """
        Generate Mermaid interaction diagram showing dependencies.
        
        Creates a visual representation of how this component interacts
        with its dependencies and dependents.
        
        Args:
            file_analysis: FileAnalysis object
            dependency_graph: DependencyGraph with all dependencies
            
        Returns:
            Mermaid diagram as string
        """
        file_path = file_analysis.file_path
        node = dependency_graph.nodes.get(file_path)
        
        if not node:
            return "```mermaid\\ngraph TD\\n    A[Component not in dependency graph]\\n```"
        
        # Get file name for cleaner diagram
        file_name = Path(file_path).stem
        
        # Start Mermaid diagram
        lines = ["```mermaid", "graph TD"]
        
        # Add central node
        central_id = "CURRENT"
        lines.append(f"    {central_id}[{file_name}]")
        lines.append(f"    style {central_id} fill:#f9f,stroke:#333,stroke-width:4px")
        
        # Add dependencies (what this file imports)
        if node.imports:
            lines.append("")
            lines.append("    %% Dependencies (imports)")
            
            for i, dep_path in enumerate(node.imports[:5]):  # Limit to 5
                dep_name = Path(dep_path).stem
                dep_id = f"DEP{i}"
                lines.append(f"    {dep_id}[{dep_name}]")
                lines.append(f"    {dep_id} --> {central_id}")
            
            if len(node.imports) > 5:
                lines.append(f"    DEPMORE[... {len(node.imports) - 5} more dependencies]")
                lines.append(f"    DEPMORE -.-> {central_id}")
        
        # Add dependents (what imports this file)
        if node.imported_by:
            lines.append("")
            lines.append("    %% Dependents (imported by)")
            
            for i, dependent_path in enumerate(node.imported_by[:5]):  # Limit to 5
                dependent_name = Path(dependent_path).stem
                dependent_id = f"DEPENDENT{i}"
                lines.append(f"    {dependent_id}[{dependent_name}]")
                lines.append(f"    {central_id} --> {dependent_id}")
            
            if len(node.imported_by) > 5:
                lines.append(f"    DEPNDMORE[... {len(node.imported_by) - 5} more dependents]")
                lines.append(f"    {central_id} -.-> DEPNDMORE")
        
        # Add external dependencies if any
        if node.external_imports:
            lines.append("")
            lines.append("    %% External dependencies")
            
            for i, ext_dep in enumerate(node.external_imports[:3]):  # Limit to 3
                ext_id = f"EXT{i}"
                # Shorten long package names
                ext_name = ext_dep.split('.')[0] if '.' in ext_dep else ext_dep
                lines.append(f"    {ext_id}[{ext_name}]")
                lines.append(f"    style {ext_id} fill:#bbf,stroke:#333,stroke-width:2px")
                lines.append(f"    {ext_id} --> {central_id}")
            
            if len(node.external_imports) > 3:
                lines.append(f"    EXTMORE[... {len(node.external_imports) - 3} more external]")
                lines.append(f"    style EXTMORE fill:#bbf,stroke:#333,stroke-width:2px")
                lines.append(f"    EXTMORE -.-> {central_id}")
        
        lines.append("```")
        
        return '\\n'.join(lines)

    
    def extract_dependencies_with_evidence(
        self,
        file_analysis: FileAnalysis
    ) -> List[Dict[str, str]]:
        """
        Extract dependencies with evidence citing imports.
        
        Analyzes import statements to document what this component
        depends on and why.
        
        Args:
            file_analysis: FileAnalysis object with import information
            
        Returns:
            List of dependency dictionaries with keys:
                - name: Module/package name
                - reason: Why it's imported
                - evidence: Import statement citation
        """
        dependencies = []
        
        for import_info in file_analysis.symbol_info.imports:
            # Determine reason for import
            reason = self._infer_dependency_reason(
                import_info.module,
                import_info.imported_symbols
            )
            
            # Build evidence citation
            if import_info.imported_symbols:
                symbols = ', '.join(import_info.imported_symbols[:3])
                if len(import_info.imported_symbols) > 3:
                    symbols += f", ... ({len(import_info.imported_symbols)} total)"
                evidence = f"Line {import_info.line_number}: imports {symbols} from {import_info.module}"
            else:
                evidence = f"Line {import_info.line_number}: imports {import_info.module}"
            
            dependencies.append({
                'name': import_info.module,
                'reason': reason,
                'evidence': evidence
            })
        
        logger.debug(
            f"Extracted {len(dependencies)} dependencies from {file_analysis.file_path}"
        )
        
        return dependencies
    
    def _infer_dependency_reason(
        self,
        module_name: str,
        symbols: List[str]
    ) -> str:
        """
        Infer why a module is imported.
        
        Args:
            module_name: Name of imported module
            symbols: List of imported symbols
            
        Returns:
            Human-readable reason
        """
        # Check module name for common patterns
        module_lower = module_name.lower()
        
        if 'test' in module_lower:
            return "Testing utilities and fixtures"
        if 'logging' in module_lower or 'logger' in module_lower:
            return "Logging and diagnostics"
        if 'config' in module_lower or 'settings' in module_lower:
            return "Configuration management"
        if 'util' in module_lower or 'helper' in module_lower:
            return "Utility functions and helpers"
        if 'model' in module_lower or 'schema' in module_lower:
            return "Data models and schemas"
        if 'api' in module_lower or 'client' in module_lower:
            return "API client or interface"
        if 'db' in module_lower or 'database' in module_lower:
            return "Database operations"
        if 'auth' in module_lower:
            return "Authentication and authorization"
        if 'validation' in module_lower or 'validator' in module_lower:
            return "Data validation"
        if 'cache' in module_lower:
            return "Caching functionality"
        if 'error' in module_lower or 'exception' in module_lower:
            return "Error handling"
        
        # Check symbols for patterns
        if symbols:
            symbol_str = ' '.join(symbols).lower()
            
            if 'dataclass' in symbol_str or 'field' in symbol_str:
                return "Dataclass definitions"
            if 'async' in symbol_str or 'await' in symbol_str:
                return "Asynchronous operations"
            if 'type' in symbol_str or 'optional' in symbol_str or 'list' in symbol_str:
                return "Type hints and annotations"
            if 'path' in symbol_str:
                return "File path operations"
            if 'json' in symbol_str:
                return "JSON serialization/deserialization"
            if 'datetime' in symbol_str or 'time' in symbol_str:
                return "Date and time operations"
            
            # Generic description based on symbols
            if len(symbols) == 1:
                return f"Uses {symbols[0]} functionality"
            elif len(symbols) <= 3:
                return f"Uses {', '.join(symbols)}"
            else:
                return f"Uses multiple utilities from {module_name}"
        
        # Fallback
        return f"Provides functionality from {module_name}"
    
    def _extract_dependents_with_evidence(
        self,
        file_analysis: FileAnalysis,
        dependency_graph: DependencyGraph
    ) -> List[Dict[str, str]]:
        """
        Extract what depends on this file (reverse dependencies).
        
        Args:
            file_analysis: FileAnalysis object
            dependency_graph: DependencyGraph with all dependencies
            
        Returns:
            List of dependent dictionaries with keys:
                - name: File that imports this
                - usage: How it's used
                - evidence: Citation
        """
        dependents = []
        
        node = dependency_graph.nodes.get(file_analysis.file_path)
        if not node:
            return dependents
        
        for dependent_path in node.imported_by:
            # Get file name
            dependent_name = Path(dependent_path).name
            
            # Infer usage from path
            usage = self._infer_usage_from_path(dependent_path)
            
            # Build evidence
            evidence = f"Imported by {dependent_path}"
            
            dependents.append({
                'name': dependent_name,
                'usage': usage,
                'evidence': evidence
            })
        
        logger.debug(
            f"Extracted {len(dependents)} dependents for {file_analysis.file_path}"
        )
        
        return dependents
    
    def _infer_usage_from_path(self, file_path: str) -> str:
        """
        Infer how a file uses this component based on its path.
        
        Args:
            file_path: Path to dependent file
            
        Returns:
            Usage description
        """
        path_lower = file_path.lower()
        
        if '/test' in path_lower or 'test_' in path_lower:
            return "Used in tests"
        if '/api/' in path_lower or '/routes/' in path_lower:
            return "Used in API/route handlers"
        if '/controllers/' in path_lower:
            return "Used in controllers"
        if '/services/' in path_lower:
            return "Used in service layer"
        if '/views/' in path_lower or '/components/' in path_lower:
            return "Used in UI components"
        if '/utils/' in path_lower or '/helpers/' in path_lower:
            return "Used by utility functions"
        
        return "Used by this module"

    
    def extract_design_patterns(
        self,
        file_analysis: FileAnalysis,
        patterns: List[DetectedPattern]
    ) -> List[Dict[str, str]]:
        """
        Identify design patterns with evidence from code.
        
        Analyzes detected patterns and code structure to identify
        common design patterns being used.
        
        Args:
            file_analysis: FileAnalysis object
            patterns: List of detected patterns
            
        Returns:
            List of design pattern dictionaries with keys:
                - pattern: Pattern name
                - evidence: Code citation
                - explanation: How it's implemented
        """
        design_patterns = []
        
        # Analyze detected patterns
        pattern_types = {p.pattern_type for p in patterns}
        
        # Repository pattern
        if 'database_operation' in pattern_types:
            db_patterns = [p for p in patterns if p.pattern_type == 'database_operation']
            if len(db_patterns) >= 2:
                design_patterns.append({
                    'pattern': 'Repository Pattern',
                    'evidence': f"Multiple database operations (lines {', '.join(str(p.line_number) for p in db_patterns[:3])})",
                    'explanation': 'Encapsulates data access logic in a repository-like structure'
                })
        
        # Singleton pattern (check for class with getInstance or similar)
        for cls in file_analysis.symbol_info.classes:
            singleton_methods = [
                m for m in cls.methods 
                if m.name.lower() in ['getinstance', 'get_instance', 'instance']
            ]
            if singleton_methods:
                design_patterns.append({
                    'pattern': 'Singleton Pattern',
                    'evidence': f"Class {cls.name} with {singleton_methods[0].name}() method (line {singleton_methods[0].start_line})",
                    'explanation': 'Ensures only one instance of the class exists'
                })
        
        # Factory pattern (check for create/build methods)
        for func in file_analysis.symbol_info.functions:
            if any(keyword in func.name.lower() for keyword in ['create', 'build', 'make', 'factory']):
                design_patterns.append({
                    'pattern': 'Factory Pattern',
                    'evidence': f"Function {func.name}() (line {func.start_line})",
                    'explanation': 'Creates objects without specifying exact class'
                })
                break
        
        # Decorator pattern (check for decorators)
        decorated_functions = [f for f in file_analysis.symbol_info.functions if f.decorators]
        if decorated_functions:
            func = decorated_functions[0]
            decorators = ', '.join(func.decorators[:3])
            design_patterns.append({
                'pattern': 'Decorator Pattern',
                'evidence': f"Function {func.name}() with decorators: {decorators} (line {func.start_line})",
                'explanation': 'Adds behavior to functions using decorators'
            })
        
        # Strategy pattern (check for multiple similar methods)
        for cls in file_analysis.symbol_info.classes:
            # Look for methods with similar names (e.g., process_x, process_y)
            method_prefixes = {}
            for method in cls.methods:
                if '_' in method.name:
                    prefix = method.name.split('_')[0]
                    if prefix not in method_prefixes:
                        method_prefixes[prefix] = []
                    method_prefixes[prefix].append(method)
            
            # If we have multiple methods with same prefix, might be strategy pattern
            for prefix, methods in method_prefixes.items():
                if len(methods) >= 3:
                    method_names = ', '.join(m.name for m in methods[:3])
                    design_patterns.append({
                        'pattern': 'Strategy Pattern',
                        'evidence': f"Class {cls.name} with multiple {prefix}_* methods: {method_names}",
                        'explanation': 'Defines family of algorithms with interchangeable implementations'
                    })
                    break
        
        # Observer pattern (check for event/listener patterns)
        for pattern in patterns:
            if 'event' in pattern.pattern_type.lower() or 'listener' in pattern.pattern_type.lower():
                design_patterns.append({
                    'pattern': 'Observer Pattern',
                    'evidence': f"{pattern.pattern_type} detected (line {pattern.line_number})",
                    'explanation': 'Implements event-driven communication between objects'
                })
                break
        
        # Middleware pattern
        if 'middleware' in file_analysis.file_path.lower():
            design_patterns.append({
                'pattern': 'Middleware Pattern',
                'evidence': f"File path indicates middleware: {file_analysis.file_path}",
                'explanation': 'Processes requests in a pipeline before reaching handlers'
            })
        
        # MVC pattern indicators
        if any(keyword in file_analysis.file_path.lower() for keyword in ['controller', 'view', 'model']):
            component_type = None
            if 'controller' in file_analysis.file_path.lower():
                component_type = 'Controller'
            elif 'view' in file_analysis.file_path.lower():
                component_type = 'View'
            elif 'model' in file_analysis.file_path.lower():
                component_type = 'Model'
            
            if component_type:
                design_patterns.append({
                    'pattern': 'MVC Pattern',
                    'evidence': f"File path indicates {component_type} component: {file_analysis.file_path}",
                    'explanation': f'Part of Model-View-Controller architecture ({component_type} layer)'
                })
        
        # Dependency Injection (check for constructor parameters)
        for cls in file_analysis.symbol_info.classes:
            init_methods = [m for m in cls.methods if m.name == '__init__']
            if init_methods:
                init_method = init_methods[0]
                if len(init_method.parameters) >= 2:  # self + at least one dependency
                    params = ', '.join(init_method.parameters[1:4])  # Skip 'self'
                    design_patterns.append({
                        'pattern': 'Dependency Injection',
                        'evidence': f"Class {cls.name}.__init__() accepts dependencies: {params} (line {init_method.start_line})",
                        'explanation': 'Dependencies are injected through constructor'
                    })
                    break
        
        logger.debug(
            f"Identified {len(design_patterns)} design patterns in {file_analysis.file_path}"
        )
        
        return design_patterns


def create_architecture_extractor(repo_path: str) -> ArchitectureExtractor:
    """
    Factory function to create an ArchitectureExtractor instance.
    
    Args:
        repo_path: Path to repository root
        
    Returns:
        ArchitectureExtractor instance
    """
    return ArchitectureExtractor(repo_path)
