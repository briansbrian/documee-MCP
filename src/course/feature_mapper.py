"""
Feature Mapping Analyzer for AI Content Enrichment.

This module implements the Feature-to-Lesson Mapping framework, connecting
code implementation to user-facing features and business value. It identifies
features from code, traces user flows, extracts business value, and finds
entry points for comprehensive feature understanding.
"""

import logging
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

from src.course.models import Lesson
from src.models.analysis_models import FileAnalysis
from src.course.enrichment_models import FeatureMapping

logger = logging.getLogger(__name__)


class FeatureMapper:
    """
    Maps code to user-facing features following FEATURE-TO-LESSON-MAPPING framework.
    
    Investigates:
    - What feature does this code implement?
    - What do users do with this feature?
    - Why does this feature exist?
    - Where do users interact with it?
    - How does the feature flow work?
    """
    
    def __init__(self, repo_path: str):
        """
        Initialize feature mapper.
        
        Args:
            repo_path: Path to the repository root
        """
        self.repo_path = Path(repo_path).resolve()
        logger.info(f"Initialized FeatureMapper for: {self.repo_path}")
    
    def identify_feature_from_code(
        self,
        lesson: Lesson,
        file_analysis: FileAnalysis
    ) -> FeatureMapping:
        """
        Detect features from code analysis and lesson context.
        
        Analyzes the code structure, patterns, and lesson information to
        identify the user-facing feature being implemented.
        
        Args:
            lesson: Lesson object containing file path and metadata
            file_analysis: FileAnalysis with symbols, patterns, and metrics
            
        Returns:
            FeatureMapping object with feature details
        """
        logger.info(
            f"Identifying feature for lesson '{lesson.lesson_id}' "
            f"from file: {lesson.file_path}"
        )
        
        # Identify feature name from multiple sources
        feature_name = self._identify_feature_name(lesson, file_analysis)
        
        # Extract user-facing purpose
        user_facing_purpose = self._extract_user_facing_purpose(
            lesson,
            file_analysis
        )
        
        # Extract business value (will be enriched with git/docs later)
        business_value = self._extract_business_value_from_code(
            lesson,
            file_analysis
        )
        
        # Find entry points
        entry_points = self.find_entry_points(file_analysis)
        
        # Extract feature flow
        feature_flow = self.extract_user_flow(file_analysis)
        
        feature_mapping = FeatureMapping(
            feature_name=feature_name,
            user_facing_purpose=user_facing_purpose,
            business_value=business_value,
            entry_points=entry_points,
            feature_flow=feature_flow
        )
        
        logger.info(
            f"Identified feature: '{feature_name}' with "
            f"{len(entry_points)} entry point(s)"
        )
        
        return feature_mapping
    
    def _identify_feature_name(
        self,
        lesson: Lesson,
        file_analysis: FileAnalysis
    ) -> str:
        """
        Identify feature name from lesson and code analysis.
        
        Args:
            lesson: Lesson object
            file_analysis: FileAnalysis object
            
        Returns:
            Feature name string
        """
        # Priority 1: Use lesson title if descriptive
        if lesson.title and not lesson.title.startswith("Lesson"):
            return lesson.title
        
        # Priority 2: Extract from file path patterns
        file_path = Path(lesson.file_path)
        
        # Check for common feature patterns in path
        path_parts = file_path.parts
        
        # Look for feature indicators in path
        feature_indicators = [
            'routes', 'api', 'controllers', 'views', 'components',
            'services', 'handlers', 'endpoints', 'features'
        ]
        
        for i, part in enumerate(path_parts):
            if part.lower() in feature_indicators and i + 1 < len(path_parts):
                # Next part is likely the feature name
                feature_part = path_parts[i + 1]
                # Remove file extension and clean up
                feature_name = file_path.stem if i + 1 == len(path_parts) - 1 else feature_part
                return self._humanize_name(feature_name)
        
        # Priority 3: Extract from detected patterns
        for pattern in file_analysis.patterns:
            if pattern.pattern_type in ['api_endpoint', 'route', 'component']:
                # Use pattern type as feature
                return self._humanize_name(pattern.pattern_type)
        
        # Priority 4: Use main class or function name
        if file_analysis.symbol_info.classes:
            main_class = file_analysis.symbol_info.classes[0]
            return self._humanize_name(main_class.name)
        
        if file_analysis.symbol_info.functions:
            main_func = file_analysis.symbol_info.functions[0]
            return self._humanize_name(main_func.name)
        
        # Fallback: Use file name
        return self._humanize_name(file_path.stem)
    
    def _humanize_name(self, name: str) -> str:
        """
        Convert code name to human-readable feature name.
        
        Args:
            name: Code name (e.g., 'user_authentication', 'UserAuth')
            
        Returns:
            Human-readable name (e.g., 'User Authentication')
        """
        # Remove common suffixes
        name = re.sub(r'(Controller|Service|Handler|Component|View|Route|API)$', '', name)
        
        # Convert camelCase to spaces
        name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
        
        # Convert snake_case to spaces
        name = name.replace('_', ' ')
        
        # Convert kebab-case to spaces
        name = name.replace('-', ' ')
        
        # Capitalize words
        name = ' '.join(word.capitalize() for word in name.split())
        
        return name.strip()
    
    def _extract_user_facing_purpose(
        self,
        lesson: Lesson,
        file_analysis: FileAnalysis
    ) -> str:
        """
        Extract what users do with this feature.
        
        Args:
            lesson: Lesson object
            file_analysis: FileAnalysis object
            
        Returns:
            User-facing purpose description
        """
        # Check lesson description first
        if lesson.description and len(lesson.description) > 20:
            return lesson.description
        
        # Analyze patterns to infer purpose
        purposes = []
        
        for pattern in file_analysis.patterns:
            if pattern.pattern_type == 'api_endpoint':
                # Extract HTTP method and path to infer purpose
                method = pattern.metadata.get('method', 'GET')
                path = pattern.metadata.get('path', pattern.file_path)
                
                if method == 'POST':
                    purposes.append(f"Create or submit {self._extract_resource_from_path(path)}")
                elif method == 'GET':
                    purposes.append(f"Retrieve or view {self._extract_resource_from_path(path)}")
                elif method == 'PUT' or method == 'PATCH':
                    purposes.append(f"Update {self._extract_resource_from_path(path)}")
                elif method == 'DELETE':
                    purposes.append(f"Delete {self._extract_resource_from_path(path)}")
            
            elif pattern.pattern_type == 'database_operation':
                operation = pattern.metadata.get('operation', '')
                if 'create' in operation.lower() or 'insert' in operation.lower():
                    purposes.append("Store data in the system")
                elif 'read' in operation.lower() or 'select' in operation.lower():
                    purposes.append("Retrieve data from the system")
                elif 'update' in operation.lower():
                    purposes.append("Modify existing data")
                elif 'delete' in operation.lower():
                    purposes.append("Remove data from the system")
            
            elif pattern.pattern_type == 'authentication':
                purposes.append("Authenticate users and manage access")
            
            elif pattern.pattern_type == 'validation':
                purposes.append("Validate user input and ensure data quality")
        
        if purposes:
            # Combine unique purposes
            unique_purposes = list(dict.fromkeys(purposes))
            if len(unique_purposes) == 1:
                return f"Users can {unique_purposes[0].lower()}"
            else:
                return f"Users can {', '.join(unique_purposes).lower()}"
        
        # Fallback: Generic purpose based on file type
        if 'api' in lesson.file_path.lower() or 'route' in lesson.file_path.lower():
            return "Users interact with this feature through API endpoints"
        elif 'component' in lesson.file_path.lower() or 'view' in lesson.file_path.lower():
            return "Users interact with this feature through the user interface"
        elif 'service' in lesson.file_path.lower():
            return "Users benefit from this feature's business logic and data processing"
        else:
            return "Users interact with this feature to accomplish specific tasks"
    
    def _extract_resource_from_path(self, path: str) -> str:
        """
        Extract resource name from API path.
        
        Args:
            path: API path (e.g., '/api/users/:id')
            
        Returns:
            Resource name (e.g., 'user information')
        """
        # Remove path parameters
        path = re.sub(r':[^/]+', '', path)
        path = re.sub(r'\{[^}]+\}', '', path)
        
        # Extract last meaningful segment
        segments = [s for s in path.split('/') if s and s != 'api']
        
        if segments:
            resource = segments[-1]
            # Singularize if plural
            if resource.endswith('s') and len(resource) > 1:
                resource = resource[:-1]
            return f"{resource} information"
        
        return "data"
    
    def _extract_business_value_from_code(
        self,
        lesson: Lesson,
        file_analysis: FileAnalysis
    ) -> str:
        """
        Extract business value from code structure and patterns.
        
        Note: This provides initial business value from code analysis.
        Should be enriched with git commits and documentation.
        
        Args:
            lesson: Lesson object
            file_analysis: FileAnalysis object
            
        Returns:
            Business value description
        """
        # Check for docstrings that explain "why"
        for func in file_analysis.symbol_info.functions:
            if func.docstring and len(func.docstring) > 50:
                # Look for business value keywords
                if any(keyword in func.docstring.lower() for keyword in 
                       ['enable', 'allow', 'provide', 'ensure', 'support', 'improve']):
                    return func.docstring.split('\n')[0]
        
        for cls in file_analysis.symbol_info.classes:
            if cls.docstring and len(cls.docstring) > 50:
                if any(keyword in cls.docstring.lower() for keyword in 
                       ['enable', 'allow', 'provide', 'ensure', 'support', 'improve']):
                    return cls.docstring.split('\n')[0]
        
        # Infer from patterns
        value_statements = []
        
        for pattern in file_analysis.patterns:
            if pattern.pattern_type == 'authentication':
                value_statements.append("Ensures secure access and protects user data")
            elif pattern.pattern_type == 'validation':
                value_statements.append("Maintains data quality and prevents errors")
            elif pattern.pattern_type == 'caching':
                value_statements.append("Improves performance and user experience")
            elif pattern.pattern_type == 'error_handling':
                value_statements.append("Provides reliability and graceful failure handling")
            elif pattern.pattern_type == 'logging':
                value_statements.append("Enables monitoring and troubleshooting")
        
        if value_statements:
            return value_statements[0]
        
        # Generic business value
        return "Provides essential functionality for the application"
    
    def extract_business_value(
        self,
        feature_mapping: FeatureMapping,
        evidence: Dict[str, Any]
    ) -> str:
        """
        Extract business value from documentation and git commits.
        
        Enriches the initial business value with evidence from git history
        and documentation to explain why the feature exists.
        
        Args:
            feature_mapping: Initial feature mapping
            evidence: Evidence bundle with git commits and documentation
            
        Returns:
            Enhanced business value description
        """
        business_value_parts = []
        
        # Start with code-derived value
        if feature_mapping.business_value:
            business_value_parts.append(feature_mapping.business_value)
        
        # Extract from git commits
        git_commits = evidence.get('git_commits', [])
        for commit in git_commits[:3]:  # Check first 3 commits
            message = commit.get('message', '')
            
            # Look for business value keywords in commit messages
            value_keywords = [
                'enable', 'allow', 'provide', 'support', 'improve',
                'fix', 'resolve', 'address', 'implement', 'add'
            ]
            
            for keyword in value_keywords:
                if keyword in message.lower():
                    # Extract sentence containing keyword
                    sentences = message.split('.')
                    for sentence in sentences:
                        if keyword in sentence.lower():
                            business_value_parts.append(sentence.strip())
                            break
                    break
        
        # Extract from documentation
        documentation = evidence.get('documentation', [])
        for doc in documentation:
            content = doc.get('content', '')
            
            # Look for purpose/value statements
            if any(keyword in content.lower() for keyword in 
                   ['purpose:', 'why:', 'enables', 'allows', 'provides']):
                # Extract relevant portion
                lines = content.split('\n')
                for line in lines:
                    if any(keyword in line.lower() for keyword in 
                           ['purpose:', 'why:', 'enables', 'allows', 'provides']):
                        business_value_parts.append(line.strip())
                        break
        
        # Combine and deduplicate
        if business_value_parts:
            # Remove duplicates while preserving order
            seen = set()
            unique_parts = []
            for part in business_value_parts:
                if part.lower() not in seen:
                    seen.add(part.lower())
                    unique_parts.append(part)
            
            # Return first 2-3 most relevant statements
            return '. '.join(unique_parts[:3])
        
        return feature_mapping.business_value
    
    def find_entry_points(
        self,
        file_analysis: FileAnalysis
    ) -> List[str]:
        """
        Find entry points for UI/API/CLI interactions.
        
        Identifies where users or other code can interact with this feature,
        including API endpoints, UI components, CLI commands, and public functions.
        
        Args:
            file_analysis: FileAnalysis with patterns and symbols
            
        Returns:
            List of entry point descriptions
        """
        entry_points = []
        
        # Check for API endpoints
        for pattern in file_analysis.patterns:
            if pattern.pattern_type == 'api_endpoint':
                method = pattern.metadata.get('method', 'GET')
                path = pattern.metadata.get('path', pattern.file_path)
                entry_points.append(f"API: {method} {path}")
            
            elif pattern.pattern_type == 'route':
                path = pattern.metadata.get('path', pattern.file_path)
                entry_points.append(f"Route: {path}")
            
            elif pattern.pattern_type == 'component':
                component_name = pattern.metadata.get('name', pattern.pattern_type)
                entry_points.append(f"UI Component: {component_name}")
            
            elif pattern.pattern_type == 'cli_command':
                command = pattern.metadata.get('command', pattern.pattern_type)
                entry_points.append(f"CLI: {command}")
        
        # Check for public functions (potential programmatic entry points)
        for func in file_analysis.symbol_info.functions:
            # Public functions (not starting with _ in Python)
            if not func.name.startswith('_'):
                # Check if it's exported or has decorators
                if func.decorators or func.is_async:
                    entry_points.append(f"Function: {func.name}()")
        
        # Check for public classes
        for cls in file_analysis.symbol_info.classes:
            if not cls.name.startswith('_'):
                # Check for public methods
                public_methods = [m for m in cls.methods if not m.name.startswith('_')]
                if public_methods:
                    entry_points.append(
                        f"Class: {cls.name} with {len(public_methods)} public method(s)"
                    )
        
        # If no specific entry points found, infer from file type
        if not entry_points:
            file_path = file_analysis.file_path.lower()
            
            if 'api' in file_path or 'route' in file_path:
                entry_points.append("API endpoints (see code for details)")
            elif 'component' in file_path or 'view' in file_path:
                entry_points.append("UI components (see code for details)")
            elif 'cli' in file_path or 'command' in file_path:
                entry_points.append("Command-line interface")
            elif 'service' in file_path:
                entry_points.append("Service methods (programmatic access)")
            else:
                entry_points.append("Public functions and classes")
        
        logger.debug(f"Found {len(entry_points)} entry point(s) in {file_analysis.file_path}")
        
        return entry_points
    
    def extract_user_flow(
        self,
        file_analysis: FileAnalysis
    ) -> List[str]:
        """
        Trace user interactions through the code.
        
        Analyzes the code structure to create a step-by-step flow of how
        users interact with the feature or how data flows through the system.
        
        Args:
            file_analysis: FileAnalysis with symbols and patterns
            
        Returns:
            List of flow steps in order
        """
        flow_steps = []
        
        # Analyze patterns to build flow
        patterns_by_type = {}
        for pattern in file_analysis.patterns:
            pattern_type = pattern.pattern_type
            if pattern_type not in patterns_by_type:
                patterns_by_type[pattern_type] = []
            patterns_by_type[pattern_type].append(pattern)
        
        # Build flow based on common patterns
        
        # Step 1: Entry point (API/UI/CLI)
        if 'api_endpoint' in patterns_by_type:
            endpoint = patterns_by_type['api_endpoint'][0]
            method = endpoint.metadata.get('method', 'GET')
            path = endpoint.metadata.get('path', endpoint.file_path)
            flow_steps.append(f"User sends {method} request to {path}")
        elif 'route' in patterns_by_type:
            route = patterns_by_type['route'][0]
            path = route.metadata.get('path', route.file_path)
            flow_steps.append(f"User navigates to {path}")
        elif 'component' in patterns_by_type:
            component = patterns_by_type['component'][0]
            component_name = component.metadata.get('name', component.pattern_type)
            flow_steps.append(f"User interacts with {component_name} component")
        else:
            flow_steps.append("User initiates the feature")
        
        # Step 2: Validation
        if 'validation' in patterns_by_type:
            flow_steps.append("System validates input data")
        
        # Step 3: Authentication/Authorization
        if 'authentication' in patterns_by_type:
            flow_steps.append("System verifies user authentication and permissions")
        
        # Step 4: Business logic
        # Infer from function calls
        main_functions = [f for f in file_analysis.symbol_info.functions 
                         if not f.name.startswith('_') and f.name not in ['main', 'init']]
        
        if main_functions:
            # Use first significant function as business logic
            func = main_functions[0]
            flow_steps.append(f"System processes request using {func.name}()")
        else:
            flow_steps.append("System processes the request")
        
        # Step 5: Database operations
        if 'database_operation' in patterns_by_type:
            db_ops = patterns_by_type['database_operation']
            operations = [op.metadata.get('operation', 'query') for op in db_ops]
            
            if any('create' in op.lower() or 'insert' in op.lower() for op in operations):
                flow_steps.append("System stores data in database")
            elif any('update' in op.lower() for op in operations):
                flow_steps.append("System updates database records")
            elif any('delete' in op.lower() for op in operations):
                flow_steps.append("System removes data from database")
            else:
                flow_steps.append("System queries database for data")
        
        # Step 6: Caching (if present)
        if 'caching' in patterns_by_type:
            flow_steps.append("System caches result for improved performance")
        
        # Step 7: Error handling
        if 'error_handling' in patterns_by_type:
            flow_steps.append("System handles any errors gracefully")
        
        # Step 8: Response
        if 'api_endpoint' in patterns_by_type:
            flow_steps.append("System returns JSON response to client")
        elif 'route' in patterns_by_type:
            flow_steps.append("System renders page with results")
        else:
            flow_steps.append("System returns result to caller")
        
        # If no patterns detected, create generic flow from functions
        if len(flow_steps) <= 1:
            flow_steps = self._create_generic_flow(file_analysis)
        
        logger.debug(f"Extracted {len(flow_steps)}-step user flow from {file_analysis.file_path}")
        
        return flow_steps
    
    def _create_generic_flow(self, file_analysis: FileAnalysis) -> List[str]:
        """
        Create a generic flow when specific patterns aren't detected.
        
        Args:
            file_analysis: FileAnalysis object
            
        Returns:
            List of generic flow steps
        """
        flow = []
        
        # Analyze function order and calls
        functions = file_analysis.symbol_info.functions
        
        if functions:
            # Find entry point (main, run, execute, or first public function)
            entry_func = None
            for func in functions:
                if func.name in ['main', 'run', 'execute', 'handler', 'process']:
                    entry_func = func
                    break
            
            if not entry_func:
                # Use first public function
                public_funcs = [f for f in functions if not f.name.startswith('_')]
                if public_funcs:
                    entry_func = public_funcs[0]
            
            if entry_func:
                flow.append(f"Execution starts with {entry_func.name}()")
                
                # Add steps for other significant functions
                other_funcs = [f for f in functions 
                              if f != entry_func and not f.name.startswith('_')]
                
                for func in other_funcs[:3]:  # Limit to 3 additional steps
                    flow.append(f"Calls {func.name}() to process data")
                
                flow.append("Returns result to caller")
        
        # Fallback if no functions
        if not flow:
            flow = [
                "Code is executed",
                "Data is processed",
                "Result is returned"
            ]
        
        return flow


def create_feature_mapper(repo_path: str) -> FeatureMapper:
    """
    Factory function to create a FeatureMapper instance.
    
    Args:
        repo_path: Path to repository root
        
    Returns:
        FeatureMapper instance
    """
    return FeatureMapper(repo_path)
