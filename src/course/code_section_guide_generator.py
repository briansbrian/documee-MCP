"""
Code Section Guide Generator - Creates evidence-based guides for code sections.

This module generates comprehensive guides for individual code sections with full
citations to tests, git commits, and related code. It implements progressive
disclosure strategies for explaining code from simple to complex concepts.
"""

import logging
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from .models import CodeExample
from .enrichment_models import CodeSectionGuide, EvidenceBundle


logger = logging.getLogger(__name__)


class CodeSectionGuideGenerator:
    """
    Generates evidence-based guides for code sections.
    
    This generator creates comprehensive guides that include:
    - Purpose with test evidence
    - Key concepts extracted from patterns
    - Progressive explanation approach
    - Related code with context
    - Common mistakes from test failures
    """
    
    def __init__(self):
        """Initialize the code section guide generator."""
        pass
    
    def generate_section_guide(
        self,
        code_example: CodeExample,
        evidence: EvidenceBundle
    ) -> CodeSectionGuide:
        """
        Generate a comprehensive guide for a code section with full citations.
        
        Args:
            code_example: The code example to generate a guide for
            evidence: Evidence bundle with tests, commits, and related code
            
        Returns:
            CodeSectionGuide with all evidence and guidance
        """
        logger.info(f"Generating section guide for {code_example.filename}")
        
        # Extract line range from code example (default to full file if not specified)
        line_range = self._extract_line_range(code_example)
        
        # Find related tests for this code
        test_evidence = self._find_tests_for_code(code_example, evidence.test_files)
        
        # Describe purpose with test evidence
        purpose = self.describe_purpose_with_evidence(code_example, test_evidence)
        
        # Extract key concepts from code patterns
        key_concepts = self.extract_key_concepts(code_example)
        
        # Suggest explanation approach for progressive disclosure
        explanation_approach = self.suggest_explanation_approach(code_example)
        
        # Find related code with context
        related_code = self.find_related_code(code_example, evidence)
        
        # Find git evidence for this code
        git_evidence = self._find_git_evidence(code_example, evidence.git_commits)
        
        # Identify common mistakes from tests
        common_mistakes = self.identify_common_mistakes(code_example, test_evidence)
        
        return CodeSectionGuide(
            file_path=code_example.filename,
            line_range=line_range,
            code_snippet=code_example.code,
            purpose=purpose,
            key_concepts=key_concepts,
            explanation_approach=explanation_approach,
            related_code=related_code,
            test_evidence=test_evidence,
            git_evidence=git_evidence,
            common_mistakes=common_mistakes
        )
    
    def describe_purpose_with_evidence(
        self,
        code: CodeExample,
        tests: List[Dict[str, str]]
    ) -> str:
        """
        Describe the purpose of code with citations to test results.
        
        Args:
            code: The code example
            tests: List of related tests with descriptions
            
        Returns:
            Purpose description with test citations
        """
        # Start with basic purpose from code structure
        purpose_parts = []
        
        # Analyze code structure for purpose
        code_lower = code.code.lower()
        
        # Detect common patterns
        if 'class ' in code.code:
            class_name = self._extract_class_name(code.code)
            purpose_parts.append(f"Defines the {class_name} class")
        elif 'def ' in code.code or 'function ' in code.code:
            func_name = self._extract_function_name(code.code)
            purpose_parts.append(f"Implements the {func_name} function")
        elif 'route' in code_lower or '@app.' in code_lower or '@router.' in code_lower:
            purpose_parts.append("Defines an API endpoint")
        elif 'component' in code_lower or 'export default' in code.code:
            purpose_parts.append("Implements a UI component")
        else:
            purpose_parts.append("Provides functionality")
        
        # Add test evidence if available
        if tests:
            test_descriptions = [t.get('description', '') for t in tests if t.get('description')]
            if test_descriptions:
                purpose_parts.append(f"(validated by {len(tests)} test(s): {', '.join(test_descriptions[:2])})")
        
        return " ".join(purpose_parts)
    
    def extract_key_concepts(self, code: CodeExample) -> List[str]:
        """
        Extract key programming concepts from code patterns and structure.
        
        Args:
            code: The code example
            
        Returns:
            List of key concepts demonstrated in the code
        """
        concepts = []
        code_text = code.code
        code_lower = code_text.lower()
        
        # Language-specific concepts
        if code.language in ['python', 'py']:
            concepts.extend(self._extract_python_concepts(code_text))
        elif code.language in ['javascript', 'typescript', 'js', 'ts']:
            concepts.extend(self._extract_javascript_concepts(code_text))
        
        # Common patterns across languages
        if 'class ' in code_text:
            concepts.append("Object-Oriented Programming")
            if '__init__' in code_text or 'constructor' in code_text:
                concepts.append("Class Initialization")
        
        if 'async ' in code_text or 'await ' in code_text:
            concepts.append("Asynchronous Programming")
        
        if 'try:' in code_text or 'try {' in code_text or 'catch' in code_text:
            concepts.append("Error Handling")
        
        if 'import ' in code_text or 'from ' in code_text or 'require(' in code_text:
            concepts.append("Module Imports")
        
        if '@' in code_text and ('def ' in code_text or 'function' in code_text):
            concepts.append("Decorators" if code.language == 'python' else "Annotations")
        
        if 'if ' in code_text or 'else' in code_text:
            concepts.append("Conditional Logic")
        
        if 'for ' in code_text or 'while ' in code_text:
            concepts.append("Iteration")
        
        if 'lambda' in code_text or '=>' in code_text:
            concepts.append("Lambda Functions")
        
        # Data structure concepts
        if '[' in code_text and ']' in code_text:
            concepts.append("Lists/Arrays")
        
        if '{' in code_text and ':' in code_text and code.language == 'python':
            concepts.append("Dictionaries")
        elif '{' in code_text and code.language in ['javascript', 'typescript']:
            concepts.append("Objects")
        
        # API and web concepts
        if any(method in code_lower for method in ['get', 'post', 'put', 'delete', 'patch']):
            if 'route' in code_lower or '@app.' in code_lower:
                concepts.append("RESTful API")
        
        if 'request' in code_lower or 'response' in code_lower:
            concepts.append("HTTP Request/Response")
        
        # Database concepts
        if any(db in code_lower for db in ['query', 'select', 'insert', 'update', 'delete', 'database', 'db.']):
            concepts.append("Database Operations")
        
        # Return unique concepts
        return list(dict.fromkeys(concepts))  # Preserve order while removing duplicates
    
    def suggest_explanation_approach(self, code: CodeExample) -> List[str]:
        """
        Suggest a progressive disclosure approach for explaining code.
        
        This method provides a step-by-step approach to explain code from
        simple to complex concepts, following pedagogical best practices.
        
        Args:
            code: The code example
            
        Returns:
            List of explanation steps ordered from simple to complex
        """
        approach = []
        code_text = code.code
        
        # Step 1: Start with the big picture
        if 'class ' in code_text:
            approach.append("Start by explaining what the class represents and its role in the system")
        elif 'def ' in code_text or 'function ' in code_text:
            approach.append("Begin with what the function does at a high level (inputs and outputs)")
        else:
            approach.append("Start with the overall purpose of this code section")
        
        # Step 2: Explain the structure
        if 'class ' in code_text:
            approach.append("Describe the class attributes and their purposes")
            approach.append("Walk through the main methods in order of typical usage")
        elif 'def ' in code_text or 'function ' in code_text:
            approach.append("Explain the function signature (parameters and return type)")
            approach.append("Walk through the function logic step by step")
        
        # Step 3: Dive into specific patterns
        if 'async ' in code_text or 'await ' in code_text:
            approach.append("Explain the asynchronous nature and why it's needed")
        
        if 'try:' in code_text or 'try {' in code_text:
            approach.append("Discuss error handling strategy and what errors are caught")
        
        if '@' in code_text and ('def ' in code_text or 'function' in code_text):
            approach.append("Explain the decorator/annotation and what it adds to the function")
        
        # Step 4: Highlight important details
        if 'if ' in code_text or 'else' in code_text:
            approach.append("Walk through the conditional logic and different code paths")
        
        if 'for ' in code_text or 'while ' in code_text:
            approach.append("Explain the iteration logic and what's being processed")
        
        # Step 5: Connect to broader context
        approach.append("Show how this code fits into the larger application")
        approach.append("Mention common use cases and when this code is called")
        
        # Step 6: Discuss edge cases and best practices
        approach.append("Point out edge cases and how they're handled")
        approach.append("Highlight best practices demonstrated in the code")
        
        return approach
    
    def find_related_code(
        self,
        code: CodeExample,
        evidence: EvidenceBundle
    ) -> List[Dict[str, str]]:
        """
        Find related code sections with context and relationships.
        
        Args:
            code: The code example
            evidence: Evidence bundle with dependencies and source files
            
        Returns:
            List of related code with path, context, and relationship
        """
        related = []
        
        # Extract imports/dependencies from the code
        imports = self._extract_imports(code.code, code.language)
        
        # Find related files from dependencies
        for dep in evidence.dependencies:
            dep_name = dep.get('name', '')
            # Check if this dependency is imported in the code
            if any(imp in dep_name or dep_name in imp for imp in imports):
                related.append({
                    'path': dep_name,
                    'context': dep.get('reason', 'Dependency'),
                    'relationship': 'imports'
                })
        
        # Find files that depend on this code
        for dependent in evidence.dependents:
            dep_name = dependent.get('name', '')
            related.append({
                'path': dep_name,
                'context': dependent.get('usage', 'Used by this file'),
                'relationship': 'imported_by'
            })
        
        # Look for related files in source_files
        current_file = code.filename
        for source_file in evidence.source_files:
            file_path = source_file.get('path', '')
            if file_path != current_file:
                # Check if files are in the same directory (likely related)
                if self._are_files_related(current_file, file_path):
                    related.append({
                        'path': file_path,
                        'context': 'Related file in same module',
                        'relationship': 'sibling'
                    })
        
        return related[:10]  # Limit to top 10 related files
    
    def identify_common_mistakes(
        self,
        code: CodeExample,
        tests: List[Dict[str, str]]
    ) -> List[str]:
        """
        Identify common mistakes from test failures and code patterns.
        
        Args:
            code: The code example
            tests: List of related tests
            
        Returns:
            List of common mistakes to highlight
        """
        mistakes = []
        code_text = code.code
        code_lower = code_text.lower()
        
        # Analyze test descriptions for common pitfalls
        for test in tests:
            test_name = test.get('test_name', '').lower()
            test_desc = test.get('description', '').lower()
            
            # Look for negative test cases
            if any(word in test_name or word in test_desc for word in ['error', 'fail', 'invalid', 'exception', 'edge']):
                mistakes.append(f"Watch out for: {test.get('description', test.get('test_name', 'edge case'))}")
        
        # Common Python mistakes
        if code.language in ['python', 'py']:
            if '==' in code_text and 'is' not in code_text:
                mistakes.append("Using == for comparison (consider 'is' for None/True/False)")
            
            if 'except:' in code_text:
                mistakes.append("Catching all exceptions with bare 'except:' (be more specific)")
            
            if 'global ' in code_text:
                mistakes.append("Using global variables (consider passing as parameters)")
        
        # Common JavaScript/TypeScript mistakes
        if code.language in ['javascript', 'typescript', 'js', 'ts']:
            if '==' in code_text and '===' not in code_text:
                mistakes.append("Using == instead of === (loose vs strict equality)")
            
            if 'var ' in code_text:
                mistakes.append("Using 'var' instead of 'let' or 'const'")
        
        # Async/await mistakes
        if 'async ' in code_text:
            if 'await ' not in code_text:
                mistakes.append("Async function without await (might not need to be async)")
            
            if 'try' not in code_text:
                mistakes.append("Async code without error handling (use try/catch)")
        
        # Error handling mistakes
        if 'try:' in code_text or 'try {' in code_text:
            if 'finally' not in code_text and ('open(' in code_text or 'file' in code_lower):
                mistakes.append("Opening files without 'finally' block for cleanup")
        
        # Security-related mistakes
        if 'password' in code_lower:
            if 'hash' not in code_lower and 'bcrypt' not in code_lower:
                mistakes.append("Handling passwords without hashing (always hash passwords)")
        
        if 'sql' in code_lower or 'query' in code_lower:
            if 'format' in code_text or '+' in code_text:
                mistakes.append("Potential SQL injection risk (use parameterized queries)")
        
        return mistakes[:8]  # Limit to top 8 most relevant mistakes
    
    # Helper methods
    
    def _extract_line_range(self, code: CodeExample) -> Tuple[int, int]:
        """Extract line range from code example."""
        # Count lines in code
        lines = code.code.split('\n')
        return (1, len(lines))
    
    def _find_tests_for_code(
        self,
        code: CodeExample,
        test_files: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """Find tests related to this code."""
        related_tests = []
        
        # Extract function/class names from code
        names = self._extract_names(code.code)
        
        for test_file in test_files:
            test_path = test_file.get('path', '')
            tests = test_file.get('tests', [])
            
            for test in tests:
                test_name = test.get('name', '')
                test_desc = test.get('description', '')
                
                # Check if test name mentions any of the code names
                if any(name.lower() in test_name.lower() for name in names):
                    related_tests.append({
                        'test_name': test_name,
                        'description': test_desc,
                        'file': test_path
                    })
        
        return related_tests
    
    def _find_git_evidence(
        self,
        code: CodeExample,
        git_commits: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """Find git commits related to this code file."""
        related_commits = []
        
        for commit in git_commits:
            # Check if commit affected this file
            files_changed = commit.get('files_changed', [])
            if code.filename in files_changed or any(code.filename in f for f in files_changed):
                related_commits.append({
                    'commit': commit.get('hash', '')[:8],  # Short hash
                    'message': commit.get('message', ''),
                    'date': commit.get('date', '')
                })
        
        return related_commits[:5]  # Limit to 5 most recent commits
    
    def _extract_class_name(self, code: str) -> str:
        """Extract class name from code."""
        match = re.search(r'class\s+(\w+)', code)
        return match.group(1) if match else "class"
    
    def _extract_function_name(self, code: str) -> str:
        """Extract function name from code."""
        # Try Python function
        match = re.search(r'def\s+(\w+)', code)
        if match:
            return match.group(1)
        
        # Try JavaScript function
        match = re.search(r'function\s+(\w+)', code)
        if match:
            return match.group(1)
        
        # Try arrow function with const
        match = re.search(r'const\s+(\w+)\s*=', code)
        if match:
            return match.group(1)
        
        return "function"
    
    def _extract_names(self, code: str) -> List[str]:
        """Extract function and class names from code."""
        names = []
        
        # Extract class names
        for match in re.finditer(r'class\s+(\w+)', code):
            names.append(match.group(1))
        
        # Extract function names
        for match in re.finditer(r'def\s+(\w+)', code):
            names.append(match.group(1))
        
        for match in re.finditer(r'function\s+(\w+)', code):
            names.append(match.group(1))
        
        for match in re.finditer(r'const\s+(\w+)\s*=.*=>', code):
            names.append(match.group(1))
        
        return names
    
    def _extract_python_concepts(self, code: str) -> List[str]:
        """Extract Python-specific concepts."""
        concepts = []
        
        if 'with ' in code:
            concepts.append("Context Managers")
        
        if '__' in code:
            concepts.append("Dunder Methods")
        
        if 'yield' in code:
            concepts.append("Generators")
        
        if '@property' in code:
            concepts.append("Properties")
        
        if 'isinstance' in code or 'type(' in code:
            concepts.append("Type Checking")
        
        if 'list comprehension' in code or '[' in code and 'for' in code and ']' in code:
            concepts.append("List Comprehensions")
        
        return concepts
    
    def _extract_javascript_concepts(self, code: str) -> List[str]:
        """Extract JavaScript/TypeScript-specific concepts."""
        concepts = []
        
        if 'Promise' in code or '.then(' in code:
            concepts.append("Promises")
        
        if 'useState' in code or 'useEffect' in code:
            concepts.append("React Hooks")
        
        if 'export default' in code or 'export {' in code:
            concepts.append("ES6 Modules")
        
        if '=>' in code:
            concepts.append("Arrow Functions")
        
        if 'const {' in code or 'const [' in code:
            concepts.append("Destructuring")
        
        if '...' in code:
            concepts.append("Spread Operator")
        
        return concepts
    
    def _extract_imports(self, code: str, language: str) -> List[str]:
        """Extract import statements from code."""
        imports = []
        
        if language in ['python', 'py']:
            # Python imports
            for match in re.finditer(r'from\s+([\w.]+)\s+import', code):
                imports.append(match.group(1))
            for match in re.finditer(r'import\s+([\w.]+)', code):
                imports.append(match.group(1))
        
        elif language in ['javascript', 'typescript', 'js', 'ts']:
            # JavaScript/TypeScript imports
            for match in re.finditer(r'from\s+[\'"]([^\'"]+)[\'"]', code):
                imports.append(match.group(1))
            for match in re.finditer(r'require\([\'"]([^\'"]+)[\'"]\)', code):
                imports.append(match.group(1))
        
        return imports
    
    def _are_files_related(self, file1: str, file2: str) -> bool:
        """Check if two files are related (same directory or similar names)."""
        # Normalize paths
        file1 = file1.replace('\\', '/')
        file2 = file2.replace('\\', '/')
        
        # Check if in same directory
        dir1 = '/'.join(file1.split('/')[:-1])
        dir2 = '/'.join(file2.split('/')[:-1])
        
        if dir1 == dir2:
            return True
        
        # Check if similar names (e.g., user.py and user_test.py)
        name1 = file1.split('/')[-1].replace('_test', '').replace('.test', '').split('.')[0]
        name2 = file2.split('/')[-1].replace('_test', '').replace('.test', '').split('.')[0]
        
        return name1 == name2
