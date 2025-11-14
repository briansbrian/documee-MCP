"""
Real-world context suggester for AI content enrichment.

This module generates practical use cases, beginner-friendly analogies,
industry patterns, best practices, and anti-patterns based on feature
analysis and code evidence.
"""

import logging
from typing import List, Dict, Any
from src.course.enrichment_models import FeatureMapping, EvidenceBundle, RealWorldContext
from src.models.analysis_models import DetectedPattern

logger = logging.getLogger(__name__)


class RealWorldContextSuggester:
    """
    Suggests real-world context for features to make learning relatable.
    
    Generates:
    - Practical use cases for features
    - Beginner-friendly analogies
    - Industry-standard patterns
    - Best practices from code quality
    - Anti-patterns from issues/comments
    """
    
    def __init__(self):
        """Initialize the real-world context suggester."""
        # Common analogies for programming concepts
        self._concept_analogies = {
            'authentication': [
                "Like showing your ID at a building entrance - you prove who you are once, then get a visitor badge",
                "Similar to a movie ticket - you pay once (login) and can enter multiple times during the showing"
            ],
            'caching': [
                "Like keeping frequently used items on your desk instead of in a filing cabinet",
                "Similar to bookmarking websites - faster than searching every time"
            ],
            'database': [
                "Like a filing cabinet with organized folders and labels",
                "Similar to a library catalog system - organized storage with quick lookup"
            ],
            'api': [
                "Like a restaurant menu - you order (request) and get food (response) without knowing how it's cooked",
                "Similar to a vending machine - you press buttons (API calls) and get products (data)"
            ],
            'validation': [
                "Like a bouncer at a club checking IDs - only valid entries get through",
                "Similar to spell-check - catches mistakes before they cause problems"
            ],
            'encryption': [
                "Like a locked safe - only people with the combination can access the contents",
                "Similar to speaking in code - the message is scrambled unless you know how to decode it"
            ],
            'async': [
                "Like ordering food delivery - you place the order and do other things while waiting",
                "Similar to washing machine - you start it and do other tasks while it runs"
            ],
            'middleware': [
                "Like security checkpoints at an airport - everyone passes through before boarding",
                "Similar to a receptionist - handles initial requests before passing to the right person"
            ]
        }
        
        # Industry patterns mapped to pattern types
        self._industry_patterns = {
            'react_component': [
                "Component-based architecture",
                "Unidirectional data flow",
                "Props for component communication",
                "State management patterns"
            ],
            'api_route': [
                "RESTful API design",
                "HTTP method conventions (GET, POST, PUT, DELETE)",
                "Status code standards (200, 404, 500)",
                "Request/response patterns"
            ],
            'database_operation': [
                "CRUD operations (Create, Read, Update, Delete)",
                "Repository pattern for data access",
                "Connection pooling",
                "Transaction management"
            ],
            'authentication': [
                "Token-based authentication (JWT)",
                "Password hashing (bcrypt, argon2)",
                "Session management",
                "OAuth2 for third-party login"
            ],
            'error_handling': [
                "Try-catch-finally pattern",
                "Error propagation",
                "Graceful degradation",
                "Logging and monitoring"
            ],
            'validation': [
                "Input sanitization",
                "Schema validation",
                "Type checking",
                "Boundary validation"
            ]
        }
    
    def suggest_use_cases(self, feature: FeatureMapping) -> List[str]:
        """
        Suggest practical use cases for a feature.
        
        Args:
            feature: Feature mapping with business context
            
        Returns:
            List of practical scenarios where this feature is used
        """
        use_cases = []
        
        # Extract use cases from feature name and purpose
        feature_lower = feature.feature_name.lower()
        purpose_lower = feature.user_facing_purpose.lower()
        
        # Authentication/Authorization use cases
        if any(term in feature_lower for term in ['auth', 'login', 'user', 'session']):
            use_cases.extend([
                "Web application user login systems",
                "Mobile app authentication",
                "API authentication for third-party integrations",
                "Single sign-on (SSO) systems"
            ])
        
        # Data management use cases
        if any(term in feature_lower for term in ['database', 'data', 'storage', 'crud']):
            use_cases.extend([
                "User profile management",
                "Content management systems",
                "E-commerce product catalogs",
                "Data analytics dashboards"
            ])
        
        # API/Service use cases
        if any(term in feature_lower for term in ['api', 'endpoint', 'service', 'route']):
            use_cases.extend([
                "Mobile app backend services",
                "Third-party integrations",
                "Microservices communication",
                "Public API for developers"
            ])
        
        # File/Upload use cases
        if any(term in feature_lower for term in ['file', 'upload', 'download', 'storage']):
            use_cases.extend([
                "User profile picture uploads",
                "Document management systems",
                "Media sharing platforms",
                "Backup and restore functionality"
            ])
        
        # Search use cases
        if any(term in feature_lower for term in ['search', 'filter', 'query']):
            use_cases.extend([
                "E-commerce product search",
                "Content discovery systems",
                "User directory lookups",
                "Log analysis and debugging"
            ])
        
        # Notification use cases
        if any(term in feature_lower for term in ['notification', 'alert', 'email', 'message']):
            use_cases.extend([
                "User notification systems",
                "Email marketing campaigns",
                "Real-time alerts and monitoring",
                "Chat and messaging applications"
            ])
        
        # Payment use cases
        if any(term in feature_lower for term in ['payment', 'checkout', 'billing', 'subscription']):
            use_cases.extend([
                "E-commerce checkout flows",
                "Subscription management",
                "Invoice generation",
                "Payment gateway integration"
            ])
        
        # If no specific use cases found, provide generic ones based on purpose
        if not use_cases:
            if 'create' in purpose_lower or 'add' in purpose_lower:
                use_cases.append(f"Creating new {feature.feature_name.lower()} entries")
            if 'read' in purpose_lower or 'view' in purpose_lower or 'get' in purpose_lower:
                use_cases.append(f"Viewing and retrieving {feature.feature_name.lower()} data")
            if 'update' in purpose_lower or 'edit' in purpose_lower:
                use_cases.append(f"Modifying existing {feature.feature_name.lower()} records")
            if 'delete' in purpose_lower or 'remove' in purpose_lower:
                use_cases.append(f"Removing {feature.feature_name.lower()} entries")
        
        # Add business value as a use case if meaningful
        if feature.business_value and len(feature.business_value) > 20:
            use_cases.append(feature.business_value)
        
        logger.debug(f"Generated {len(use_cases)} use cases for feature: {feature.feature_name}")
        return use_cases[:5]  # Limit to top 5 most relevant
    
    def suggest_analogies(self, feature: FeatureMapping, skill_level: str = "beginner") -> List[str]:
        """
        Suggest beginner-friendly analogies for a feature.
        
        Args:
            feature: Feature mapping with context
            skill_level: Target skill level (beginner, intermediate, advanced)
            
        Returns:
            List of analogies that explain the feature in relatable terms
        """
        analogies = []
        feature_lower = feature.feature_name.lower()
        
        # Check for known concepts and add their analogies
        for concept, concept_analogies in self._concept_analogies.items():
            if concept in feature_lower:
                analogies.extend(concept_analogies)
        
        # Generate custom analogies based on feature characteristics
        purpose_lower = feature.user_facing_purpose.lower()
        
        # CRUD operation analogies
        if 'create' in purpose_lower:
            analogies.append("Like filling out a form - you provide information and it gets saved")
        if 'read' in purpose_lower or 'view' in purpose_lower:
            analogies.append("Like looking up a contact in your phone - quick access to stored information")
        if 'update' in purpose_lower or 'edit' in purpose_lower:
            analogies.append("Like editing a document - you change existing content and save the updates")
        if 'delete' in purpose_lower or 'remove' in purpose_lower:
            analogies.append("Like throwing away a file - it's removed from storage permanently")
        
        # Flow-based analogies
        if len(feature.feature_flow) > 2:
            analogies.append(
                f"Like an assembly line - data moves through {len(feature.feature_flow)} steps, "
                "each adding or transforming something"
            )
        
        # Entry point analogies
        if feature.entry_points:
            if len(feature.entry_points) == 1:
                analogies.append("Like a single door to a building - one way in, controlled access")
            elif len(feature.entry_points) > 1:
                analogies.append(
                    f"Like a building with {len(feature.entry_points)} entrances - "
                    "multiple ways to access the same functionality"
                )
        
        # For advanced users, skip overly simple analogies
        if skill_level == "advanced":
            analogies = [a for a in analogies if "like" not in a.lower()[:10]]
        
        logger.debug(f"Generated {len(analogies)} analogies for feature: {feature.feature_name}")
        return analogies[:4]  # Limit to top 4 most relevant
    
    def identify_industry_patterns(self, patterns: List[DetectedPattern]) -> List[str]:
        """
        Identify industry-standard patterns from detected code patterns.
        
        Args:
            patterns: List of detected code patterns
            
        Returns:
            List of industry-standard approaches and patterns
        """
        industry_patterns = set()
        
        for pattern in patterns:
            pattern_type = pattern.pattern_type.lower()
            
            # Add known industry patterns for this pattern type
            if pattern_type in self._industry_patterns:
                industry_patterns.update(self._industry_patterns[pattern_type])
            
            # Extract patterns from evidence
            for evidence in pattern.evidence:
                evidence_lower = evidence.lower()
                
                # Design patterns
                if 'singleton' in evidence_lower:
                    industry_patterns.add("Singleton pattern for single instance management")
                if 'factory' in evidence_lower:
                    industry_patterns.add("Factory pattern for object creation")
                if 'observer' in evidence_lower:
                    industry_patterns.add("Observer pattern for event handling")
                if 'decorator' in evidence_lower:
                    industry_patterns.add("Decorator pattern for extending functionality")
                if 'strategy' in evidence_lower:
                    industry_patterns.add("Strategy pattern for algorithm selection")
                
                # Architectural patterns
                if 'mvc' in evidence_lower or 'model-view-controller' in evidence_lower:
                    industry_patterns.add("MVC (Model-View-Controller) architecture")
                if 'repository' in evidence_lower:
                    industry_patterns.add("Repository pattern for data access abstraction")
                if 'service' in evidence_lower and 'layer' in evidence_lower:
                    industry_patterns.add("Service layer pattern for business logic")
                if 'middleware' in evidence_lower:
                    industry_patterns.add("Middleware pattern for request processing")
                
                # Async patterns
                if 'async' in evidence_lower or 'await' in evidence_lower:
                    industry_patterns.add("Async/await pattern for non-blocking operations")
                if 'promise' in evidence_lower:
                    industry_patterns.add("Promise-based asynchronous programming")
                if 'callback' in evidence_lower:
                    industry_patterns.add("Callback pattern for asynchronous operations")
                
                # Error handling patterns
                if 'try' in evidence_lower and 'catch' in evidence_lower:
                    industry_patterns.add("Try-catch error handling")
                if 'error boundary' in evidence_lower:
                    industry_patterns.add("Error boundary pattern for fault isolation")
        
        # Add general patterns based on pattern count
        if len(patterns) > 10:
            industry_patterns.add("Modular architecture with separation of concerns")
        
        logger.debug(f"Identified {len(industry_patterns)} industry patterns from {len(patterns)} detected patterns")
        return sorted(list(industry_patterns))[:8]  # Limit to top 8
    
    def extract_best_practices(self, evidence: EvidenceBundle) -> List[str]:
        """
        Extract best practices from code quality indicators.
        
        Args:
            evidence: Evidence bundle with code, tests, docs, and git history
            
        Returns:
            List of best practices demonstrated in the code
        """
        best_practices = []
        
        # Test coverage indicates good practices
        if evidence.test_files:
            best_practices.append("Write comprehensive tests to validate behavior")
            
            # Check for different test types
            test_types = set()
            for test_file in evidence.test_files:
                test_path = test_file.get('path', '').lower()
                if 'unit' in test_path:
                    test_types.add('unit')
                if 'integration' in test_path:
                    test_types.add('integration')
                if 'e2e' in test_path or 'end-to-end' in test_path:
                    test_types.add('e2e')
            
            if len(test_types) > 1:
                best_practices.append("Use multiple test types (unit, integration, e2e) for thorough coverage")
        
        # Documentation indicates good practices
        if evidence.documentation:
            doc_count = len(evidence.documentation)
            if doc_count > 3:
                best_practices.append("Document code with clear comments and docstrings")
            
            # Check for specific documentation types
            for doc in evidence.documentation:
                doc_type = doc.get('type', '').lower()
                content = doc.get('content', '').lower()
                
                if doc_type == 'docstring' or '"""' in content:
                    best_practices.append("Use docstrings to explain function purpose and parameters")
                    break
        
        # Git commit patterns indicate good practices
        if evidence.git_commits:
            commit_count = len(evidence.git_commits)
            if commit_count > 5:
                best_practices.append("Make frequent, focused commits with clear messages")
            
            # Check commit message quality
            descriptive_commits = sum(
                1 for commit in evidence.git_commits
                if len(commit.get('message', '')) > 20
            )
            if descriptive_commits / max(commit_count, 1) > 0.7:
                best_practices.append("Write descriptive commit messages explaining the 'why'")
        
        # Dependency management
        if evidence.dependencies:
            best_practices.append("Manage dependencies explicitly and keep them up to date")
            
            # Check for dependency injection patterns
            for dep in evidence.dependencies:
                if 'inject' in dep.get('reason', '').lower():
                    best_practices.append("Use dependency injection for loose coupling")
                    break
        
        # Source file organization
        if evidence.source_files:
            # Check for modular structure
            unique_paths = set(f.get('path', '') for f in evidence.source_files)
            if len(unique_paths) > 3:
                best_practices.append("Organize code into focused, single-responsibility modules")
            
            # Check for code reuse
            for source_file in evidence.source_files:
                code = source_file.get('code', '')
                if 'import' in code or 'require' in code:
                    best_practices.append("Reuse code through imports rather than duplication")
                    break
        
        # Error handling
        for source_file in evidence.source_files:
            code = source_file.get('code', '').lower()
            if 'try' in code and 'except' in code:
                best_practices.append("Handle errors gracefully with try-except blocks")
                break
            if 'raise' in code or 'throw' in code:
                best_practices.append("Raise meaningful exceptions with clear error messages")
                break
        
        # Validation
        for source_file in evidence.source_files:
            code = source_file.get('code', '').lower()
            if 'validate' in code or 'check' in code or 'assert' in code:
                best_practices.append("Validate inputs before processing to prevent errors")
                break
        
        logger.debug(f"Extracted {len(best_practices)} best practices from evidence")
        return best_practices[:6]  # Limit to top 6
    
    def identify_anti_patterns(self, evidence: EvidenceBundle) -> List[str]:
        """
        Identify anti-patterns from code issues and comments.
        
        Args:
            evidence: Evidence bundle with code and documentation
            
        Returns:
            List of anti-patterns to avoid
        """
        anti_patterns = []
        
        # Check documentation for warnings and TODOs
        for doc in evidence.documentation:
            content = doc.get('content', '').lower()
            
            if 'todo' in content or 'fixme' in content:
                anti_patterns.append("Avoid leaving TODO comments in production code - fix issues promptly")
            
            if 'hack' in content or 'workaround' in content:
                anti_patterns.append("Avoid hacky workarounds - refactor for proper solutions")
            
            if 'deprecated' in content:
                anti_patterns.append("Don't use deprecated APIs - migrate to current alternatives")
            
            if 'warning' in content or 'caution' in content:
                # Extract the warning context
                if 'security' in content:
                    anti_patterns.append("Avoid security vulnerabilities - follow security best practices")
                elif 'performance' in content:
                    anti_patterns.append("Avoid performance bottlenecks - profile and optimize critical paths")
        
        # Check source code for common anti-patterns
        for source_file in evidence.source_files:
            code = source_file.get('code', '').lower()
            
            # Magic numbers
            if any(char.isdigit() for char in code):
                # Simple heuristic: if there are numbers not in variable names
                if '= 100' in code or '= 1000' in code or '= 3600' in code:
                    anti_patterns.append("Avoid magic numbers - use named constants for clarity")
            
            # Long functions (heuristic: many lines)
            lines = source_file.get('lines', [])
            if isinstance(lines, list) and len(lines) > 50:
                anti_patterns.append("Avoid overly long functions - break into smaller, focused functions")
            
            # Deep nesting
            if '        ' in code:  # 8+ spaces indicates deep nesting
                anti_patterns.append("Avoid deep nesting - use early returns or extract functions")
            
            # Global state
            if 'global ' in code:
                anti_patterns.append("Avoid global variables - use parameters and return values")
            
            # Hardcoded values
            if 'localhost' in code or '127.0.0.1' in code:
                anti_patterns.append("Avoid hardcoded URLs - use configuration files or environment variables")
            
            # Poor error handling
            if 'except:' in code or 'catch()' in code:  # Bare except/catch
                anti_patterns.append("Avoid catching all exceptions - handle specific errors appropriately")
            
            # Code duplication indicators
            if code.count('def ') > 5 or code.count('function ') > 5:
                # Check for similar function names (simple heuristic)
                if 'copy' in code or 'duplicate' in code:
                    anti_patterns.append("Avoid code duplication - extract common logic into reusable functions")
        
        # Check git commits for problem indicators
        for commit in evidence.git_commits:
            message = commit.get('message', '').lower()
            
            if 'fix' in message and 'bug' in message:
                anti_patterns.append("Avoid introducing bugs - write tests before implementing features")
            
            if 'revert' in message:
                anti_patterns.append("Avoid hasty commits - review and test changes before committing")
            
            if 'hotfix' in message or 'emergency' in message:
                anti_patterns.append("Avoid emergency fixes - implement proper testing and staging processes")
        
        # Check test files for testing anti-patterns
        for test_file in evidence.test_files:
            test_code = str(test_file).lower()
            
            if 'skip' in test_code or 'ignore' in test_code:
                anti_patterns.append("Avoid skipping tests - fix or remove broken tests")
            
            if 'sleep' in test_code or 'wait' in test_code:
                anti_patterns.append("Avoid sleep/wait in tests - use proper async handling or mocks")
        
        # Remove duplicates and limit
        anti_patterns = list(dict.fromkeys(anti_patterns))  # Preserve order while removing dupes
        
        logger.debug(f"Identified {len(anti_patterns)} anti-patterns from evidence")
        return anti_patterns[:6]  # Limit to top 6
    
    def generate_context(
        self,
        feature: FeatureMapping,
        patterns: List[DetectedPattern],
        evidence: EvidenceBundle,
        skill_level: str = "beginner"
    ) -> RealWorldContext:
        """
        Generate complete real-world context for a feature.
        
        Args:
            feature: Feature mapping with business context
            patterns: Detected code patterns
            evidence: Evidence bundle with code and documentation
            skill_level: Target skill level for analogies
            
        Returns:
            Complete RealWorldContext with all suggestions
        """
        logger.info(f"Generating real-world context for feature: {feature.feature_name}")
        
        context = RealWorldContext(
            practical_use_cases=self.suggest_use_cases(feature),
            analogies=self.suggest_analogies(feature, skill_level),
            industry_patterns=self.identify_industry_patterns(patterns),
            best_practices=self.extract_best_practices(evidence),
            anti_patterns=self.identify_anti_patterns(evidence)
        )
        
        logger.info(
            f"Generated real-world context: {len(context.practical_use_cases)} use cases, "
            f"{len(context.analogies)} analogies, {len(context.industry_patterns)} patterns, "
            f"{len(context.best_practices)} best practices, {len(context.anti_patterns)} anti-patterns"
        )
        
        return context
