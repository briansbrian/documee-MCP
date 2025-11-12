"""
Pattern Detector for identifying common coding patterns and architectural decisions.

This module provides a plugin architecture for detecting patterns like React components,
API routes, database models, authentication patterns, and more.
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from .symbol_extractor import SymbolInfo

logger = logging.getLogger(__name__)


@dataclass
class DetectedPattern:
    """Information about a detected coding pattern.
    
    Attributes:
        pattern_type: Type of pattern (e.g., 'react_component', 'api_route')
        file_path: Path to the file where pattern was detected
        confidence: Confidence score (0.0-1.0) indicating detection certainty
        evidence: List of evidence strings that triggered detection
        line_numbers: Line numbers where pattern evidence was found
        metadata: Pattern-specific additional data
    """
    pattern_type: str
    file_path: str
    confidence: float
    evidence: List[str] = field(default_factory=list)
    line_numbers: List[int] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class BasePatternDetector(ABC):
    """
    Abstract base class for pattern detectors.
    
    All pattern detectors must inherit from this class and implement
    the detect() method. This enables a plugin architecture where
    custom pattern detectors can be easily added.
    """
    
    @abstractmethod
    def detect(self, symbol_info: SymbolInfo, file_content: str, file_path: str) -> List[DetectedPattern]:
        """
        Detect patterns in the given file.
        
        Args:
            symbol_info: Extracted symbols from the file
            file_content: Raw file content as string
            file_path: Path to the file being analyzed
        
        Returns:
            List of detected patterns with confidence scores
        
        Example:
            >>> detector = ReactPatternDetector()
            >>> patterns = detector.detect(symbol_info, file_content, "src/App.tsx")
            >>> for pattern in patterns:
            ...     print(f"{pattern.pattern_type}: {pattern.confidence}")
        """
        pass
    
    def _calculate_confidence(self, evidence_count: int, max_evidence: int = 5) -> float:
        """
        Calculate confidence score based on evidence count.
        
        Args:
            evidence_count: Number of evidence items found
            max_evidence: Maximum evidence count for 1.0 confidence
        
        Returns:
            Confidence score between 0.0 and 1.0
        """
        if evidence_count == 0:
            return 0.0
        return min(evidence_count / max_evidence, 1.0)


class PatternDetector:
    """
    Main pattern detector that orchestrates multiple pattern detectors.
    
    Uses a plugin architecture to support custom pattern detectors.
    """
    
    def __init__(self, detectors: Optional[List[BasePatternDetector]] = None):
        """
        Initialize the Pattern Detector with a list of detectors.
        
        Args:
            detectors: List of pattern detector instances. If None, uses default detectors.
        """
        if detectors is None:
            # Default detectors will be added in subsequent tasks
            self.detectors: List[BasePatternDetector] = []
        else:
            self.detectors = detectors
        
        logger.debug(f"PatternDetector initialized with {len(self.detectors)} detectors")
    
    def register_detector(self, detector: BasePatternDetector):
        """
        Register a new pattern detector.
        
        Args:
            detector: Pattern detector instance to register
        
        Example:
            >>> pattern_detector = PatternDetector()
            >>> pattern_detector.register_detector(CustomPatternDetector())
        """
        self.detectors.append(detector)
        logger.debug(f"Registered detector: {detector.__class__.__name__}")
    
    def detect_patterns_in_file(self, symbol_info: SymbolInfo, file_content: str, file_path: str) -> List[DetectedPattern]:
        """
        Detect all patterns in a single file using all registered detectors.
        
        Args:
            symbol_info: Extracted symbols from the file
            file_content: Raw file content as string
            file_path: Path to the file being analyzed
        
        Returns:
            List of all detected patterns from all detectors
        """
        all_patterns = []
        
        for detector in self.detectors:
            try:
                patterns = detector.detect(symbol_info, file_content, file_path)
                all_patterns.extend(patterns)
                logger.debug(
                    f"{detector.__class__.__name__} found {len(patterns)} patterns in {file_path}"
                )
            except Exception as e:
                logger.error(
                    f"Error in {detector.__class__.__name__} for {file_path}: {e}",
                    exc_info=True
                )
        
        return all_patterns
    
    def detect_global_patterns(self, file_analyses: Dict[str, Any]) -> List[DetectedPattern]:
        """
        Detect patterns across the entire codebase.
        
        This aggregates patterns from individual files and identifies
        codebase-wide architectural patterns.
        
        Args:
            file_analyses: Dictionary mapping file paths to FileAnalysis objects
        
        Returns:
            List of global patterns detected across the codebase
        """
        # Aggregate all patterns from individual files
        all_patterns = []
        pattern_counts = {}
        
        for file_path, analysis in file_analyses.items():
            if hasattr(analysis, 'patterns'):
                for pattern in analysis.patterns:
                    all_patterns.append(pattern)
                    pattern_type = pattern.pattern_type
                    pattern_counts[pattern_type] = pattern_counts.get(pattern_type, 0) + 1
        
        # Create global pattern summaries
        global_patterns = []
        for pattern_type, count in pattern_counts.items():
            global_patterns.append(DetectedPattern(
                pattern_type=f"global_{pattern_type}",
                file_path="<codebase>",
                confidence=1.0,
                evidence=[f"Found {count} instances across codebase"],
                line_numbers=[],
                metadata={
                    "count": count,
                    "pattern_type": pattern_type
                }
            ))
        
        logger.info(f"Detected {len(global_patterns)} global patterns across codebase")
        return global_patterns



class ReactPatternDetector(BasePatternDetector):
    """
    Detects React component patterns in JavaScript/TypeScript files.
    
    Looks for:
    - Functional components (functions returning JSX)
    - Hooks usage (useState, useEffect, etc.)
    - Props destructuring
    - Component exports
    """
    
    # Common React hooks
    REACT_HOOKS = {
        'useState', 'useEffect', 'useContext', 'useReducer',
        'useCallback', 'useMemo', 'useRef', 'useImperativeHandle',
        'useLayoutEffect', 'useDebugValue', 'useDeferredValue',
        'useTransition', 'useId', 'useSyncExternalStore'
    }
    
    def detect(self, symbol_info: SymbolInfo, file_content: str, file_path: str) -> List[DetectedPattern]:
        """
        Detect React patterns in the file.
        
        Args:
            symbol_info: Extracted symbols from the file
            file_content: Raw file content as string
            file_path: Path to the file being analyzed
        
        Returns:
            List of detected React patterns
        """
        patterns = []
        
        # Check if file imports React
        has_react_import = self._has_react_import(symbol_info)
        if not has_react_import:
            return patterns
        
        # Detect functional components
        for func in symbol_info.functions:
            component_pattern = self._detect_functional_component(
                func, file_content, file_path
            )
            if component_pattern:
                patterns.append(component_pattern)
        
        # Detect hooks usage
        hooks_pattern = self._detect_hooks_usage(symbol_info, file_content, file_path)
        if hooks_pattern:
            patterns.append(hooks_pattern)
        
        return patterns
    
    def _has_react_import(self, symbol_info: SymbolInfo) -> bool:
        """Check if file imports React."""
        for imp in symbol_info.imports:
            if imp.module in ['react', 'React']:
                return True
            # Check for React imports from other sources
            if 'react' in imp.module.lower():
                return True
        return False
    
    def _detect_functional_component(
        self, 
        func: Any, 
        file_content: str, 
        file_path: str
    ) -> Optional[DetectedPattern]:
        """
        Detect if a function is a React functional component.
        
        Evidence:
        - Function name starts with uppercase (PascalCase)
        - Returns JSX (contains 'return' with '<' or 'React.createElement')
        - Has props parameter
        - Uses hooks
        """
        evidence = []
        line_numbers = [func.start_line]
        metadata = {
            "component_name": func.name,
            "is_async": func.is_async
        }
        
        # Check 1: PascalCase name (component convention)
        if func.name and func.name[0].isupper():
            evidence.append(f"PascalCase function name: {func.name}")
        else:
            # Not a component if not PascalCase
            return None
        
        # Check 2: Has props parameter
        if func.parameters and len(func.parameters) > 0:
            # Check for props destructuring
            first_param = func.parameters[0]
            if '{' in first_param or first_param == 'props':
                evidence.append(f"Props parameter: {first_param}")
                metadata["has_props"] = True
        
        # Check 3: Returns JSX (look for JSX syntax in function body)
        # Extract function body from file content
        func_lines = self._get_function_lines(file_content, func.start_line, func.end_line)
        func_body = '\n'.join(func_lines)
        
        if self._contains_jsx(func_body):
            evidence.append("Returns JSX elements")
            metadata["returns_jsx"] = True
        else:
            # Not a component if doesn't return JSX
            return None
        
        # Check 4: Uses React hooks
        hooks_used = self._find_hooks_in_code(func_body)
        if hooks_used:
            evidence.append(f"Uses hooks: {', '.join(hooks_used)}")
            metadata["hooks"] = hooks_used
        
        # Calculate confidence based on evidence
        confidence = self._calculate_confidence(len(evidence), max_evidence=4)
        
        return DetectedPattern(
            pattern_type="react_component",
            file_path=file_path,
            confidence=confidence,
            evidence=evidence,
            line_numbers=line_numbers,
            metadata=metadata
        )
    
    def _detect_hooks_usage(
        self, 
        symbol_info: SymbolInfo, 
        file_content: str, 
        file_path: str
    ) -> Optional[DetectedPattern]:
        """
        Detect React hooks usage in the file.
        
        Returns a pattern if hooks are used, with details about which hooks.
        """
        hooks_used = self._find_hooks_in_code(file_content)
        
        if not hooks_used:
            return None
        
        evidence = [f"Uses {len(hooks_used)} different hooks"]
        for hook in hooks_used:
            evidence.append(f"Hook: {hook}")
        
        # Find line numbers where hooks are used
        line_numbers = []
        lines = file_content.split('\n')
        for i, line in enumerate(lines, 1):
            for hook in hooks_used:
                if hook in line:
                    line_numbers.append(i)
                    break
        
        confidence = min(len(hooks_used) / 3, 1.0)  # 3+ hooks = high confidence
        
        return DetectedPattern(
            pattern_type="react_hooks",
            file_path=file_path,
            confidence=confidence,
            evidence=evidence,
            line_numbers=line_numbers,
            metadata={
                "hooks": list(hooks_used),
                "hook_count": len(hooks_used)
            }
        )
    
    def _contains_jsx(self, code: str) -> bool:
        """
        Check if code contains JSX syntax.
        
        Looks for:
        - return <Element>
        - return (<Element>
        - React.createElement
        """
        # Simple heuristic: look for return statements with JSX
        lines = code.split('\n')
        for line in lines:
            line = line.strip()
            # Check for JSX return
            if 'return' in line and '<' in line:
                # Make sure it's not a comparison
                if 'return <' in line or 'return (' in line:
                    return True
            # Check for React.createElement
            if 'React.createElement' in line:
                return True
        return False
    
    def _find_hooks_in_code(self, code: str) -> set:
        """Find all React hooks used in the code."""
        hooks_found = set()
        for hook in self.REACT_HOOKS:
            if hook in code:
                hooks_found.add(hook)
        return hooks_found
    
    def _get_function_lines(self, file_content: str, start_line: int, end_line: int) -> List[str]:
        """Extract lines of a function from file content."""
        lines = file_content.split('\n')
        # Convert to 0-indexed
        start_idx = start_line - 1
        end_idx = end_line
        return lines[start_idx:end_idx]



class APIPatternDetector(BasePatternDetector):
    """
    Detects API route patterns in various frameworks.
    
    Supports:
    - Express.js routes (app.get, router.post, etc.)
    - FastAPI endpoints (@app.get, @router.post, etc.)
    - Next.js API routes (export default function handler)
    """
    
    # Express HTTP methods
    EXPRESS_METHODS = {'get', 'post', 'put', 'delete', 'patch', 'options', 'head'}
    
    # FastAPI decorators
    FASTAPI_DECORATORS = {
        '@app.get', '@app.post', '@app.put', '@app.delete', '@app.patch',
        '@router.get', '@router.post', '@router.put', '@router.delete', '@router.patch'
    }
    
    def detect(self, symbol_info: SymbolInfo, file_content: str, file_path: str) -> List[DetectedPattern]:
        """
        Detect API route patterns in the file.
        
        Args:
            symbol_info: Extracted symbols from the file
            file_content: Raw file content as string
            file_path: Path to the file being analyzed
        
        Returns:
            List of detected API patterns
        """
        patterns = []
        
        # Detect Express routes
        express_pattern = self._detect_express_routes(symbol_info, file_content, file_path)
        if express_pattern:
            patterns.append(express_pattern)
        
        # Detect FastAPI endpoints
        fastapi_pattern = self._detect_fastapi_endpoints(symbol_info, file_content, file_path)
        if fastapi_pattern:
            patterns.append(fastapi_pattern)
        
        # Detect Next.js API routes
        nextjs_pattern = self._detect_nextjs_api_routes(symbol_info, file_content, file_path)
        if nextjs_pattern:
            patterns.append(nextjs_pattern)
        
        return patterns
    
    def _detect_express_routes(
        self, 
        symbol_info: SymbolInfo, 
        file_content: str, 
        file_path: str
    ) -> Optional[DetectedPattern]:
        """
        Detect Express.js route patterns.
        
        Evidence:
        - Imports express
        - Uses app.get, app.post, router.get, etc.
        - Route handler functions
        """
        evidence = []
        line_numbers = []
        routes = []
        
        # Check for express import
        has_express = False
        for imp in symbol_info.imports:
            if imp.module == 'express':
                has_express = True
                evidence.append("Imports express")
                line_numbers.append(imp.line_number)
                break
        
        if not has_express:
            return None
        
        # Find route definitions in code
        lines = file_content.split('\n')
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Check for app.METHOD or router.METHOD patterns
            for method in self.EXPRESS_METHODS:
                patterns_to_check = [
                    f'app.{method}(',
                    f'router.{method}(',
                    f'app.{method} (',
                    f'router.{method} ('
                ]
                
                for pattern in patterns_to_check:
                    if pattern in line_stripped:
                        # Extract route path if possible
                        route_path = self._extract_route_path(line_stripped)
                        routes.append({
                            "method": method.upper(),
                            "path": route_path,
                            "line": i
                        })
                        evidence.append(f"Route: {method.upper()} {route_path}")
                        line_numbers.append(i)
                        break
        
        if not routes:
            return None
        
        confidence = self._calculate_confidence(len(routes), max_evidence=5)
        
        return DetectedPattern(
            pattern_type="express_api",
            file_path=file_path,
            confidence=confidence,
            evidence=evidence,
            line_numbers=line_numbers,
            metadata={
                "framework": "express",
                "routes": routes,
                "route_count": len(routes)
            }
        )
    
    def _detect_fastapi_endpoints(
        self, 
        symbol_info: SymbolInfo, 
        file_content: str, 
        file_path: str
    ) -> Optional[DetectedPattern]:
        """
        Detect FastAPI endpoint patterns.
        
        Evidence:
        - Imports fastapi
        - Uses @app.get, @app.post decorators
        - Async route handlers
        """
        evidence = []
        line_numbers = []
        endpoints = []
        
        # Check for fastapi import
        has_fastapi = False
        for imp in symbol_info.imports:
            if 'fastapi' in imp.module.lower():
                has_fastapi = True
                evidence.append(f"Imports {imp.module}")
                line_numbers.append(imp.line_number)
                break
        
        if not has_fastapi:
            return None
        
        # Find endpoint decorators
        for func in symbol_info.functions:
            for decorator in func.decorators:
                # Check if decorator is a FastAPI route decorator
                for fastapi_dec in self.FASTAPI_DECORATORS:
                    if fastapi_dec in decorator:
                        # Extract route path
                        route_path = self._extract_route_path(decorator)
                        method = self._extract_http_method(decorator)
                        
                        endpoints.append({
                            "method": method,
                            "path": route_path,
                            "function": func.name,
                            "line": func.start_line,
                            "is_async": func.is_async
                        })
                        evidence.append(f"Endpoint: {method} {route_path} ({func.name})")
                        line_numbers.append(func.start_line)
                        break
        
        if not endpoints:
            return None
        
        confidence = self._calculate_confidence(len(endpoints), max_evidence=5)
        
        return DetectedPattern(
            pattern_type="fastapi_endpoint",
            file_path=file_path,
            confidence=confidence,
            evidence=evidence,
            line_numbers=line_numbers,
            metadata={
                "framework": "fastapi",
                "endpoints": endpoints,
                "endpoint_count": len(endpoints)
            }
        )
    
    def _detect_nextjs_api_routes(
        self, 
        symbol_info: SymbolInfo, 
        file_content: str, 
        file_path: str
    ) -> Optional[DetectedPattern]:
        """
        Detect Next.js API route patterns.
        
        Evidence:
        - File in pages/api/ or app/api/ directory
        - Exports default handler function
        - Handler has req, res parameters
        """
        evidence = []
        line_numbers = []
        
        # Check if file is in API routes directory
        is_api_route = '/api/' in file_path or '\\api\\' in file_path
        if not is_api_route:
            return None
        
        evidence.append("File in API routes directory")
        
        # Look for default export handler
        has_handler = False
        handler_name = None
        
        # Check for "export default" in file content
        lines = file_content.split('\n')
        for i, line in enumerate(lines, 1):
            if 'export default' in line:
                # Check if it's a function
                if 'function' in line or '=>' in line:
                    has_handler = True
                    line_numbers.append(i)
                    evidence.append("Exports default handler function")
                    
                    # Try to extract handler name
                    if 'function' in line:
                        parts = line.split('function')
                        if len(parts) > 1:
                            name_part = parts[1].strip().split('(')[0].strip()
                            if name_part:
                                handler_name = name_part
                    break
        
        if not has_handler:
            return None
        
        # Check for req, res parameters in functions
        for func in symbol_info.functions:
            if len(func.parameters) >= 2:
                param_names = [p.lower() for p in func.parameters[:2]]
                if 'req' in param_names or 'request' in param_names:
                    if 'res' in param_names or 'response' in param_names:
                        evidence.append(f"Handler with req/res parameters: {func.name}")
                        line_numbers.append(func.start_line)
                        handler_name = func.name
                        break
        
        confidence = self._calculate_confidence(len(evidence), max_evidence=3)
        
        return DetectedPattern(
            pattern_type="nextjs_api_route",
            file_path=file_path,
            confidence=confidence,
            evidence=evidence,
            line_numbers=line_numbers,
            metadata={
                "framework": "nextjs",
                "handler_name": handler_name
            }
        )
    
    def _extract_route_path(self, code: str) -> str:
        """
        Extract route path from code line.
        
        Examples:
            app.get('/users', ...) -> '/users'
            @app.get("/items/{item_id}") -> '/items/{item_id}'
        """
        # Look for strings in quotes
        import re
        
        # Match single or double quoted strings
        matches = re.findall(r'["\']([^"\']+)["\']', code)
        if matches:
            # Return first match that looks like a path
            for match in matches:
                if match.startswith('/') or match.startswith('\\'):
                    return match
            # If no path-like string, return first match
            return matches[0]
        
        return "<unknown>"
    
    def _extract_http_method(self, decorator: str) -> str:
        """Extract HTTP method from decorator string."""
        decorator_lower = decorator.lower()
        for method in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']:
            if f'.{method}' in decorator_lower:
                return method.upper()
        return "UNKNOWN"



class DatabasePatternDetector(BasePatternDetector):
    """
    Detects database-related patterns in code.
    
    Supports:
    - ORM models (SQLAlchemy, Prisma, Sequelize, Django ORM, etc.)
    - Query builders (Knex, TypeORM, etc.)
    - Database migrations
    """
    
    # ORM frameworks and their indicators
    ORM_INDICATORS = {
        'sqlalchemy': ['declarative_base', 'Column', 'relationship', 'Base'],
        'django': ['models.Model', 'models.CharField', 'models.ForeignKey'],
        'sequelize': ['Sequelize', 'DataTypes', 'sequelize.define'],
        'typeorm': ['Entity', 'Column', 'PrimaryGeneratedColumn', 'ManyToOne'],
        'prisma': ['PrismaClient', '@prisma/client'],
        'mongoose': ['mongoose.Schema', 'mongoose.model', 'Schema'],
        'peewee': ['Model', 'CharField', 'ForeignKeyField']
    }
    
    # Query builder indicators
    QUERY_BUILDER_INDICATORS = {
        'knex': ['knex(', '.select(', '.where(', '.insert('],
        'query-builder': ['.createQueryBuilder', '.select(', '.where(']
    }
    
    # Migration indicators
    MIGRATION_INDICATORS = [
        'def upgrade(', 'def downgrade(',  # Alembic
        'exports.up', 'exports.down',  # Knex migrations
        'class Migration',  # Django migrations
        'async up(', 'async down('  # TypeORM migrations
    ]
    
    def detect(self, symbol_info: SymbolInfo, file_content: str, file_path: str) -> List[DetectedPattern]:
        """
        Detect database patterns in the file.
        
        Args:
            symbol_info: Extracted symbols from the file
            file_content: Raw file content as string
            file_path: Path to the file being analyzed
        
        Returns:
            List of detected database patterns
        """
        patterns = []
        
        # Detect ORM models
        orm_pattern = self._detect_orm_models(symbol_info, file_content, file_path)
        if orm_pattern:
            patterns.append(orm_pattern)
        
        # Detect query builders
        query_pattern = self._detect_query_builders(symbol_info, file_content, file_path)
        if query_pattern:
            patterns.append(query_pattern)
        
        # Detect migrations
        migration_pattern = self._detect_migrations(symbol_info, file_content, file_path)
        if migration_pattern:
            patterns.append(migration_pattern)
        
        return patterns
    
    def _detect_orm_models(
        self, 
        symbol_info: SymbolInfo, 
        file_content: str, 
        file_path: str
    ) -> Optional[DetectedPattern]:
        """
        Detect ORM model definitions.
        
        Evidence:
        - Imports ORM framework
        - Classes inherit from Model/Base
        - Uses Column definitions
        """
        evidence = []
        line_numbers = []
        models = []
        detected_orm = None
        
        # Check imports for ORM frameworks
        for imp in symbol_info.imports:
            for orm_name, indicators in self.ORM_INDICATORS.items():
                if orm_name in imp.module.lower():
                    detected_orm = orm_name
                    evidence.append(f"Imports {orm_name}")
                    line_numbers.append(imp.line_number)
                    break
                # Check imported symbols
                for symbol in imp.imported_symbols:
                    if symbol in indicators:
                        detected_orm = orm_name
                        evidence.append(f"Imports {symbol} from {orm_name}")
                        line_numbers.append(imp.line_number)
                        break
        
        if not detected_orm:
            return None
        
        # Check classes for model patterns
        for cls in symbol_info.classes:
            is_model = False
            
            # Check base classes
            for base in cls.base_classes:
                if any(indicator in base for indicator in ['Model', 'Base', 'Document']):
                    is_model = True
                    break
            
            # Check for Column/Field definitions in class
            if not is_model:
                # Get class body from file content
                class_lines = self._get_lines(file_content, cls.start_line, cls.end_line)
                class_body = '\n'.join(class_lines)
                
                # Look for ORM field definitions
                if any(indicator in class_body for indicator in ['Column(', 'Field(', 'CharField', 'IntegerField']):
                    is_model = True
            
            if is_model:
                models.append({
                    "name": cls.name,
                    "line": cls.start_line,
                    "base_classes": cls.base_classes
                })
                evidence.append(f"Model class: {cls.name}")
                line_numbers.append(cls.start_line)
        
        if not models:
            return None
        
        confidence = self._calculate_confidence(len(models), max_evidence=5)
        
        return DetectedPattern(
            pattern_type="orm_model",
            file_path=file_path,
            confidence=confidence,
            evidence=evidence,
            line_numbers=line_numbers,
            metadata={
                "orm_framework": detected_orm,
                "models": models,
                "model_count": len(models)
            }
        )
    
    def _detect_query_builders(
        self, 
        symbol_info: SymbolInfo, 
        file_content: str, 
        file_path: str
    ) -> Optional[DetectedPattern]:
        """
        Detect query builder usage.
        
        Evidence:
        - Imports query builder library
        - Uses query builder methods (.select, .where, etc.)
        """
        evidence = []
        line_numbers = []
        detected_builder = None
        query_count = 0
        
        # Check imports
        for imp in symbol_info.imports:
            for builder_name in self.QUERY_BUILDER_INDICATORS.keys():
                if builder_name in imp.module.lower():
                    detected_builder = builder_name
                    evidence.append(f"Imports {builder_name}")
                    line_numbers.append(imp.line_number)
                    break
        
        if not detected_builder:
            return None
        
        # Count query builder method calls
        lines = file_content.split('\n')
        for i, line in enumerate(lines, 1):
            for indicator in self.QUERY_BUILDER_INDICATORS.get(detected_builder, []):
                if indicator in line:
                    query_count += 1
                    if len(line_numbers) < 10:  # Limit line numbers
                        line_numbers.append(i)
                    break
        
        if query_count > 0:
            evidence.append(f"Uses query builder methods ({query_count} occurrences)")
        
        confidence = self._calculate_confidence(query_count, max_evidence=10)
        
        return DetectedPattern(
            pattern_type="query_builder",
            file_path=file_path,
            confidence=confidence,
            evidence=evidence,
            line_numbers=line_numbers,
            metadata={
                "builder": detected_builder,
                "query_count": query_count
            }
        )
    
    def _detect_migrations(
        self, 
        symbol_info: SymbolInfo, 
        file_content: str, 
        file_path: str
    ) -> Optional[DetectedPattern]:
        """
        Detect database migration files.
        
        Evidence:
        - File in migrations directory
        - Contains upgrade/downgrade functions
        - Contains migration class
        """
        evidence = []
        line_numbers = []
        
        # Check if file is in migrations directory
        is_migration_file = 'migration' in file_path.lower() or 'migrate' in file_path.lower()
        if is_migration_file:
            evidence.append("File in migrations directory")
        
        # Look for migration indicators
        migration_type = None
        for indicator in self.MIGRATION_INDICATORS:
            if indicator in file_content:
                evidence.append(f"Contains migration function: {indicator}")
                
                # Find line number
                lines = file_content.split('\n')
                for i, line in enumerate(lines, 1):
                    if indicator in line:
                        line_numbers.append(i)
                        break
                
                # Determine migration type
                if 'upgrade' in indicator or 'downgrade' in indicator:
                    migration_type = 'alembic'
                elif 'exports.' in indicator:
                    migration_type = 'knex'
                elif 'Migration' in indicator:
                    migration_type = 'django'
                elif 'async' in indicator:
                    migration_type = 'typeorm'
        
        if not evidence:
            return None
        
        confidence = self._calculate_confidence(len(evidence), max_evidence=3)
        
        return DetectedPattern(
            pattern_type="database_migration",
            file_path=file_path,
            confidence=confidence,
            evidence=evidence,
            line_numbers=line_numbers,
            metadata={
                "migration_type": migration_type
            }
        )
    
    def _get_lines(self, file_content: str, start_line: int, end_line: int) -> List[str]:
        """Extract lines from file content."""
        lines = file_content.split('\n')
        start_idx = start_line - 1
        end_idx = end_line
        return lines[start_idx:end_idx]



class AuthPatternDetector(BasePatternDetector):
    """
    Detects authentication and authorization patterns in code.
    
    Supports:
    - JWT (JSON Web Tokens)
    - OAuth (OAuth2, OpenID Connect)
    - Session-based authentication
    - API key authentication
    """
    
    # JWT indicators
    JWT_INDICATORS = [
        'jwt.encode', 'jwt.decode', 'jsonwebtoken',
        'JWT', 'JWTBearer', 'create_access_token',
        'verify_token', 'decode_token'
    ]
    
    # OAuth indicators
    OAUTH_INDICATORS = [
        'OAuth', 'oauth2', 'OpenID', 'OIDC',
        'authorize_url', 'token_url', 'client_id',
        'client_secret', 'authorization_code',
        'OAuthProvider', 'GoogleOAuth', 'FacebookOAuth'
    ]
    
    # Session indicators
    SESSION_INDICATORS = [
        'session', 'Session', 'SessionMiddleware',
        'set_session', 'get_session', 'session_id',
        'cookie-session', 'express-session'
    ]
    
    # API key indicators
    API_KEY_INDICATORS = [
        'api_key', 'apiKey', 'API_KEY',
        'x-api-key', 'Authorization: Bearer',
        'authenticate_api_key'
    ]
    
    # Password hashing indicators
    PASSWORD_INDICATORS = [
        'bcrypt', 'hashpw', 'checkpw',
        'pbkdf2', 'scrypt', 'argon2',
        'hash_password', 'verify_password',
        'PasswordHasher'
    ]
    
    def detect(self, symbol_info: SymbolInfo, file_content: str, file_path: str) -> List[DetectedPattern]:
        """
        Detect authentication patterns in the file.
        
        Args:
            symbol_info: Extracted symbols from the file
            file_content: Raw file content as string
            file_path: Path to the file being analyzed
        
        Returns:
            List of detected authentication patterns
        """
        patterns = []
        
        # Detect JWT patterns
        jwt_pattern = self._detect_jwt_pattern(symbol_info, file_content, file_path)
        if jwt_pattern:
            patterns.append(jwt_pattern)
        
        # Detect OAuth patterns
        oauth_pattern = self._detect_oauth_pattern(symbol_info, file_content, file_path)
        if oauth_pattern:
            patterns.append(oauth_pattern)
        
        # Detect session-based auth
        session_pattern = self._detect_session_pattern(symbol_info, file_content, file_path)
        if session_pattern:
            patterns.append(session_pattern)
        
        # Detect API key auth
        api_key_pattern = self._detect_api_key_pattern(symbol_info, file_content, file_path)
        if api_key_pattern:
            patterns.append(api_key_pattern)
        
        # Detect password hashing
        password_pattern = self._detect_password_hashing(symbol_info, file_content, file_path)
        if password_pattern:
            patterns.append(password_pattern)
        
        return patterns
    
    def _detect_jwt_pattern(
        self, 
        symbol_info: SymbolInfo, 
        file_content: str, 
        file_path: str
    ) -> Optional[DetectedPattern]:
        """
        Detect JWT authentication patterns.
        
        Evidence:
        - Imports JWT library
        - Uses jwt.encode/decode
        - Token creation/verification functions
        """
        evidence = []
        line_numbers = []
        jwt_operations = []
        
        # Check imports
        for imp in symbol_info.imports:
            if any(jwt_lib in imp.module.lower() for jwt_lib in ['jwt', 'pyjwt', 'jsonwebtoken']):
                evidence.append(f"Imports JWT library: {imp.module}")
                line_numbers.append(imp.line_number)
        
        # Check for JWT operations in code
        lines = file_content.split('\n')
        for i, line in enumerate(lines, 1):
            for indicator in self.JWT_INDICATORS:
                if indicator in line:
                    jwt_operations.append(indicator)
                    if len(line_numbers) < 10:
                        line_numbers.append(i)
                    evidence.append(f"JWT operation: {indicator}")
                    break
        
        if not evidence:
            return None
        
        # Check for token-related functions
        for func in symbol_info.functions:
            func_name_lower = func.name.lower()
            if any(keyword in func_name_lower for keyword in ['token', 'jwt', 'auth', 'verify']):
                if func.name not in [op for op in jwt_operations]:
                    evidence.append(f"Auth function: {func.name}")
                    line_numbers.append(func.start_line)
        
        confidence = self._calculate_confidence(len(evidence), max_evidence=5)
        
        return DetectedPattern(
            pattern_type="jwt_authentication",
            file_path=file_path,
            confidence=confidence,
            evidence=evidence,
            line_numbers=line_numbers,
            metadata={
                "auth_type": "jwt",
                "operations": list(set(jwt_operations))
            }
        )
    
    def _detect_oauth_pattern(
        self, 
        symbol_info: SymbolInfo, 
        file_content: str, 
        file_path: str
    ) -> Optional[DetectedPattern]:
        """
        Detect OAuth authentication patterns.
        
        Evidence:
        - Imports OAuth library
        - Uses OAuth flow (authorize, token exchange)
        - OAuth provider configuration
        """
        evidence = []
        line_numbers = []
        oauth_features = []
        
        # Check imports
        for imp in symbol_info.imports:
            if any(oauth_lib in imp.module.lower() for oauth_lib in ['oauth', 'authlib', 'oauthlib']):
                evidence.append(f"Imports OAuth library: {imp.module}")
                line_numbers.append(imp.line_number)
        
        # Check for OAuth indicators in code
        for indicator in self.OAUTH_INDICATORS:
            if indicator in file_content:
                oauth_features.append(indicator)
                evidence.append(f"OAuth feature: {indicator}")
                
                # Find line number
                lines = file_content.split('\n')
                for i, line in enumerate(lines, 1):
                    if indicator in line and len(line_numbers) < 10:
                        line_numbers.append(i)
                        break
        
        if not evidence:
            return None
        
        confidence = self._calculate_confidence(len(evidence), max_evidence=5)
        
        return DetectedPattern(
            pattern_type="oauth_authentication",
            file_path=file_path,
            confidence=confidence,
            evidence=evidence,
            line_numbers=line_numbers,
            metadata={
                "auth_type": "oauth",
                "features": list(set(oauth_features))
            }
        )
    
    def _detect_session_pattern(
        self, 
        symbol_info: SymbolInfo, 
        file_content: str, 
        file_path: str
    ) -> Optional[DetectedPattern]:
        """
        Detect session-based authentication patterns.
        
        Evidence:
        - Imports session library
        - Uses session management
        - Session middleware
        """
        evidence = []
        line_numbers = []
        session_features = []
        
        # Check imports
        for imp in symbol_info.imports:
            module_lower = imp.module.lower()
            if 'session' in module_lower:
                evidence.append(f"Imports session library: {imp.module}")
                line_numbers.append(imp.line_number)
        
        # Check for session indicators
        for indicator in self.SESSION_INDICATORS:
            if indicator in file_content:
                session_features.append(indicator)
                if len(evidence) < 10:
                    evidence.append(f"Session feature: {indicator}")
                
                # Find line number
                lines = file_content.split('\n')
                for i, line in enumerate(lines, 1):
                    if indicator in line and len(line_numbers) < 10:
                        line_numbers.append(i)
                        break
        
        if not evidence:
            return None
        
        confidence = self._calculate_confidence(len(evidence), max_evidence=5)
        
        return DetectedPattern(
            pattern_type="session_authentication",
            file_path=file_path,
            confidence=confidence,
            evidence=evidence,
            line_numbers=line_numbers,
            metadata={
                "auth_type": "session",
                "features": list(set(session_features))
            }
        )
    
    def _detect_api_key_pattern(
        self, 
        symbol_info: SymbolInfo, 
        file_content: str, 
        file_path: str
    ) -> Optional[DetectedPattern]:
        """
        Detect API key authentication patterns.
        
        Evidence:
        - API key validation
        - API key headers
        - API key middleware
        """
        evidence = []
        line_numbers = []
        
        # Check for API key indicators
        lines = file_content.split('\n')
        for i, line in enumerate(lines, 1):
            for indicator in self.API_KEY_INDICATORS:
                if indicator in line:
                    evidence.append(f"API key usage: {indicator}")
                    line_numbers.append(i)
                    break
        
        if not evidence:
            return None
        
        # Check for API key validation functions
        for func in symbol_info.functions:
            func_name_lower = func.name.lower()
            if 'api' in func_name_lower and 'key' in func_name_lower:
                evidence.append(f"API key function: {func.name}")
                line_numbers.append(func.start_line)
        
        confidence = self._calculate_confidence(len(evidence), max_evidence=4)
        
        return DetectedPattern(
            pattern_type="api_key_authentication",
            file_path=file_path,
            confidence=confidence,
            evidence=evidence,
            line_numbers=line_numbers,
            metadata={
                "auth_type": "api_key"
            }
        )
    
    def _detect_password_hashing(
        self, 
        symbol_info: SymbolInfo, 
        file_content: str, 
        file_path: str
    ) -> Optional[DetectedPattern]:
        """
        Detect password hashing patterns.
        
        Evidence:
        - Imports password hashing library
        - Uses password hashing functions
        - Password verification
        """
        evidence = []
        line_numbers = []
        hash_algorithms = []
        
        # Check imports
        for imp in symbol_info.imports:
            module_lower = imp.module.lower()
            for algo in ['bcrypt', 'pbkdf2', 'scrypt', 'argon2', 'passlib']:
                if algo in module_lower:
                    evidence.append(f"Imports password hashing: {imp.module}")
                    line_numbers.append(imp.line_number)
                    hash_algorithms.append(algo)
        
        # Check for password hashing indicators
        for indicator in self.PASSWORD_INDICATORS:
            if indicator in file_content:
                if indicator not in hash_algorithms:
                    hash_algorithms.append(indicator)
                
                # Find line number
                lines = file_content.split('\n')
                for i, line in enumerate(lines, 1):
                    if indicator in line and len(line_numbers) < 10:
                        evidence.append(f"Password hashing: {indicator}")
                        line_numbers.append(i)
                        break
        
        if not evidence:
            return None
        
        # Check for password-related functions
        for func in symbol_info.functions:
            func_name_lower = func.name.lower()
            if 'password' in func_name_lower or 'hash' in func_name_lower:
                evidence.append(f"Password function: {func.name}")
                line_numbers.append(func.start_line)
        
        confidence = self._calculate_confidence(len(evidence), max_evidence=5)
        
        return DetectedPattern(
            pattern_type="password_hashing",
            file_path=file_path,
            confidence=confidence,
            evidence=evidence,
            line_numbers=line_numbers,
            metadata={
                "auth_type": "password",
                "algorithms": list(set(hash_algorithms))
            }
        )
