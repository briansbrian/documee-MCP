"""
Evidence Collection Utilities for AI Content Enrichment.

This module provides utilities to collect evidence from multiple sources
(code, tests, documentation, dependencies) to support evidence-based
content enrichment and prevent hallucinations.
"""

import logging
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import aiofiles

from src.models.analysis_models import FileAnalysis
from src.course.models import Lesson

logger = logging.getLogger(__name__)


class EvidenceCollector:
    """
    Collects evidence from multiple sources for content enrichment.
    
    Provides methods to gather source code, tests, documentation, and
    dependency information to create comprehensive evidence bundles.
    """
    
    def __init__(self, repo_path: str):
        """
        Initialize evidence collector.
        
        Args:
            repo_path: Path to the repository root
        """
        self.repo_path = Path(repo_path).resolve()
        logger.info(f"Initialized EvidenceCollector for: {self.repo_path}")
    
    async def collect_source_evidence(
        self,
        lesson: Lesson
    ) -> List[Dict[str, Any]]:
        """
        Gather source code with line numbers for a lesson.
        
        Collects the actual source code files referenced in the lesson,
        including line number references for precise citations.
        
        Args:
            lesson: Lesson object containing file_path and content
            
        Returns:
            List of source file dictionaries with keys:
                - path: File path relative to repo
                - code: Full source code content
                - lines: Total number of lines
                - language: Programming language
                - sections: List of relevant code sections with line ranges
        """
        source_files = []
        
        # Primary source file from lesson
        if lesson.file_path:
            file_evidence = await self._collect_file_evidence(
                lesson.file_path,
                lesson.content
            )
            if file_evidence:
                source_files.append(file_evidence)
        
        # Additional files from code examples
        if lesson.content and lesson.content.code_example:
            code_example = lesson.content.code_example
            if code_example.filename and code_example.filename != lesson.file_path:
                file_evidence = await self._collect_file_evidence(
                    code_example.filename,
                    lesson.content
                )
                if file_evidence:
                    source_files.append(file_evidence)
        
        logger.info(
            f"Collected source evidence for lesson '{lesson.lesson_id}': "
            f"{len(source_files)} file(s)"
        )
        
        return source_files
    
    async def _collect_file_evidence(
        self,
        file_path: str,
        lesson_content: Optional[Any] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Collect evidence from a single source file.
        
        Args:
            file_path: Path to source file
            lesson_content: Optional lesson content to extract relevant sections
            
        Returns:
            Dictionary with file evidence or None if file not found
        """
        try:
            # Resolve file path
            full_path = self.repo_path / file_path
            
            if not full_path.exists():
                logger.warning(f"Source file not found: {file_path}")
                return None
            
            # Read file content
            async with aiofiles.open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                code = await f.read()
            
            lines = code.split('\n')
            
            # Detect language from extension
            language = self._detect_language(file_path)
            
            # Extract relevant sections if lesson content provided
            sections = []
            if lesson_content and hasattr(lesson_content, 'code_example'):
                code_example = lesson_content.code_example
                if hasattr(code_example, 'highlights'):
                    for highlight in code_example.highlights:
                        sections.append({
                            'start_line': highlight.start_line,
                            'end_line': highlight.end_line,
                            'description': highlight.description,
                            'code': '\n'.join(lines[highlight.start_line-1:highlight.end_line])
                        })
            
            # If no sections specified, treat entire file as one section
            if not sections:
                sections.append({
                    'start_line': 1,
                    'end_line': len(lines),
                    'description': 'Complete file',
                    'code': code
                })
            
            return {
                'path': file_path,
                'code': code,
                'lines': len(lines),
                'language': language,
                'sections': sections
            }
            
        except Exception as e:
            logger.error(f"Error collecting file evidence for {file_path}: {e}")
            return None
    
    def _detect_language(self, file_path: str) -> str:
        """
        Detect programming language from file extension.
        
        Args:
            file_path: Path to file
            
        Returns:
            Language name (e.g., 'python', 'javascript', 'typescript')
        """
        extension_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.cpp': 'cpp',
            '.cc': 'cpp',
            '.cxx': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.rb': 'ruby',
            '.php': 'php',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala'
        }
        
        ext = Path(file_path).suffix.lower()
        return extension_map.get(ext, 'unknown')
    
    async def collect_test_evidence(
        self,
        lesson: Lesson
    ) -> List[Dict[str, Any]]:
        """
        Find and parse related test files for a lesson.
        
        Searches for test files that validate the behavior of code
        in the lesson, extracting test descriptions and assertions.
        
        Args:
            lesson: Lesson object containing file_path
            
        Returns:
            List of test file dictionaries with keys:
                - path: Test file path
                - test_cases: List of test cases found
                - framework: Test framework detected (pytest, jest, etc.)
                - coverage: What functionality is tested
        """
        test_files = []
        
        if not lesson.file_path:
            logger.warning(f"No file_path in lesson {lesson.lesson_id}")
            return test_files
        
        # Find potential test files
        test_file_paths = await self._find_test_files(lesson.file_path)
        
        for test_path in test_file_paths:
            test_evidence = await self._parse_test_file(test_path)
            if test_evidence:
                test_files.append(test_evidence)
        
        logger.info(
            f"Collected test evidence for lesson '{lesson.lesson_id}': "
            f"{len(test_files)} test file(s)"
        )
        
        return test_files
    
    async def _find_test_files(self, source_file: str) -> List[str]:
        """
        Find test files related to a source file.
        
        Args:
            source_file: Path to source file
            
        Returns:
            List of potential test file paths
        """
        test_files = []
        source_path = Path(source_file)
        
        # Common test file patterns
        patterns = [
            # Python patterns
            f"test_{source_path.stem}.py",
            f"{source_path.stem}_test.py",
            f"tests/test_{source_path.stem}.py",
            f"tests/{source_path.stem}_test.py",
            # JavaScript/TypeScript patterns
            f"{source_path.stem}.test.js",
            f"{source_path.stem}.spec.js",
            f"{source_path.stem}.test.ts",
            f"{source_path.stem}.spec.ts",
            f"__tests__/{source_path.stem}.test.js",
            f"__tests__/{source_path.stem}.test.ts",
        ]
        
        # Search for test files
        for pattern in patterns:
            # Try in same directory
            test_path = source_path.parent / pattern
            if (self.repo_path / test_path).exists():
                test_files.append(str(test_path))
            
            # Try in tests directory at repo root
            test_path = Path("tests") / pattern
            if (self.repo_path / test_path).exists():
                test_files.append(str(test_path))
        
        return test_files
    
    async def _parse_test_file(self, test_path: str) -> Optional[Dict[str, Any]]:
        """
        Parse a test file to extract test cases and assertions.
        
        Args:
            test_path: Path to test file
            
        Returns:
            Dictionary with test evidence or None if parsing fails
        """
        try:
            full_path = self.repo_path / test_path
            
            if not full_path.exists():
                return None
            
            async with aiofiles.open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = await f.read()
            
            # Detect test framework
            framework = self._detect_test_framework(content, test_path)
            
            # Extract test cases
            test_cases = self._extract_test_cases(content, framework)
            
            # Determine what's being tested
            coverage = self._analyze_test_coverage(content, test_cases)
            
            return {
                'path': test_path,
                'test_cases': test_cases,
                'framework': framework,
                'coverage': coverage,
                'total_tests': len(test_cases)
            }
            
        except Exception as e:
            logger.error(f"Error parsing test file {test_path}: {e}")
            return None
    
    def _detect_test_framework(self, content: str, file_path: str) -> str:
        """
        Detect the test framework used in a test file.
        
        Args:
            content: Test file content
            file_path: Path to test file
            
        Returns:
            Framework name (pytest, jest, mocha, unittest, etc.)
        """
        # Python frameworks
        if 'import pytest' in content or '@pytest' in content:
            return 'pytest'
        if 'import unittest' in content or 'unittest.TestCase' in content:
            return 'unittest'
        
        # JavaScript frameworks
        if 'describe(' in content or 'it(' in content:
            if 'jest' in content.lower() or '.test.' in file_path or '.spec.' in file_path:
                return 'jest'
            return 'mocha'
        
        if 'test(' in content and ('.test.' in file_path or '.spec.' in file_path):
            return 'jest'
        
        return 'unknown'
    
    def _extract_test_cases(
        self,
        content: str,
        framework: str
    ) -> List[Dict[str, Any]]:
        """
        Extract test cases from test file content.
        
        Args:
            content: Test file content
            framework: Detected test framework
            
        Returns:
            List of test case dictionaries
        """
        test_cases = []
        
        if framework == 'pytest':
            # Match pytest test functions: def test_something():
            pattern = r'def\s+(test_\w+)\s*\([^)]*\):\s*(?:"""([^"]+)"""|\'\'\'([^\']+)\'\'\')?'
            matches = re.finditer(pattern, content, re.MULTILINE)
            
            for match in matches:
                test_name = match.group(1)
                docstring = match.group(2) or match.group(3) or ""
                
                test_cases.append({
                    'name': test_name,
                    'description': docstring.strip() if docstring else test_name.replace('_', ' '),
                    'type': 'function'
                })
        
        elif framework == 'unittest':
            # Match unittest test methods: def test_something(self):
            pattern = r'def\s+(test_\w+)\s*\(self[^)]*\):\s*(?:"""([^"]+)"""|\'\'\'([^\']+)\'\'\')?'
            matches = re.finditer(pattern, content, re.MULTILINE)
            
            for match in matches:
                test_name = match.group(1)
                docstring = match.group(2) or match.group(3) or ""
                
                test_cases.append({
                    'name': test_name,
                    'description': docstring.strip() if docstring else test_name.replace('_', ' '),
                    'type': 'method'
                })
        
        elif framework in ['jest', 'mocha']:
            # Match describe/it blocks
            # it('should do something', ...)
            it_pattern = r'it\s*\(\s*[\'"]([^\'"]+)[\'"]'
            it_matches = re.finditer(it_pattern, content)
            
            for match in it_matches:
                description = match.group(1)
                test_cases.append({
                    'name': description,
                    'description': description,
                    'type': 'it'
                })
            
            # test('should do something', ...)
            test_pattern = r'test\s*\(\s*[\'"]([^\'"]+)[\'"]'
            test_matches = re.finditer(test_pattern, content)
            
            for match in test_matches:
                description = match.group(1)
                test_cases.append({
                    'name': description,
                    'description': description,
                    'type': 'test'
                })
        
        return test_cases
    
    def _analyze_test_coverage(
        self,
        content: str,
        test_cases: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Analyze what functionality is covered by tests.
        
        Args:
            content: Test file content
            test_cases: Extracted test cases
            
        Returns:
            List of functionality descriptions being tested
        """
        coverage = []
        
        # Extract common patterns from test descriptions
        for test_case in test_cases:
            desc = test_case['description'].lower()
            
            # Look for common test patterns
            if 'should' in desc:
                # Extract the "should X" part
                parts = desc.split('should')
                if len(parts) > 1:
                    coverage.append(f"Should {parts[1].strip()}")
            elif 'test' in desc:
                # Extract what's being tested
                parts = desc.split('test')
                if len(parts) > 1:
                    coverage.append(parts[1].strip().capitalize())
            else:
                coverage.append(desc.capitalize())
        
        # Remove duplicates while preserving order
        seen = set()
        unique_coverage = []
        for item in coverage:
            if item not in seen:
                seen.add(item)
                unique_coverage.append(item)
        
        return unique_coverage
    
    def collect_documentation_evidence(
        self,
        file_analysis: FileAnalysis
    ) -> List[Dict[str, Any]]:
        """
        Extract documentation from file analysis.
        
        Collects inline comments, docstrings, and other documentation
        from the analyzed file to provide context.
        
        Args:
            file_analysis: FileAnalysis object with symbol information
            
        Returns:
            List of documentation dictionaries with keys:
                - type: 'docstring', 'comment', 'inline'
                - content: Documentation text
                - location: Where it appears (function name, line number)
                - context: What it documents
        """
        documentation = []
        
        # Extract function docstrings
        for func in file_analysis.symbol_info.functions:
            if func.docstring:
                documentation.append({
                    'type': 'docstring',
                    'content': func.docstring,
                    'location': f"Function: {func.name} (lines {func.start_line}-{func.end_line})",
                    'context': f"Documents function '{func.name}'"
                })
        
        # Extract class docstrings
        for cls in file_analysis.symbol_info.classes:
            if cls.docstring:
                documentation.append({
                    'type': 'docstring',
                    'content': cls.docstring,
                    'location': f"Class: {cls.name} (lines {cls.start_line}-{cls.end_line})",
                    'context': f"Documents class '{cls.name}'"
                })
            
            # Extract method docstrings
            for method in cls.methods:
                if method.docstring:
                    documentation.append({
                        'type': 'docstring',
                        'content': method.docstring,
                        'location': f"Method: {cls.name}.{method.name} (lines {method.start_line}-{method.end_line})",
                        'context': f"Documents method '{cls.name}.{method.name}'"
                    })
        
        logger.info(
            f"Collected documentation evidence for {file_analysis.file_path}: "
            f"{len(documentation)} item(s)"
        )
        
        return documentation
    
    def collect_dependency_evidence(
        self,
        file_analysis: FileAnalysis
    ) -> List[Dict[str, Any]]:
        """
        Map dependencies with evidence from file analysis.
        
        Extracts import statements and dependency relationships,
        providing evidence for what the code depends on.
        
        Args:
            file_analysis: FileAnalysis object with import information
            
        Returns:
            List of dependency dictionaries with keys:
                - name: Module/package name
                - symbols: Imported symbols
                - reason: Why it's imported (inferred from usage)
                - evidence: Import statement location
                - type: 'standard_library', 'third_party', 'local'
        """
        dependencies = []
        
        for import_info in file_analysis.symbol_info.imports:
            # Determine dependency type
            dep_type = self._classify_dependency(import_info.module)
            
            # Create dependency evidence
            dependency = {
                'name': import_info.module,
                'symbols': import_info.imported_symbols,
                'reason': self._infer_import_reason(
                    import_info.module,
                    import_info.imported_symbols
                ),
                'evidence': f"Line {import_info.line_number}: {import_info.import_type}",
                'type': dep_type,
                'is_relative': import_info.is_relative
            }
            
            dependencies.append(dependency)
        
        logger.info(
            f"Collected dependency evidence for {file_analysis.file_path}: "
            f"{len(dependencies)} dependencies"
        )
        
        return dependencies
    
    def _classify_dependency(self, module_name: str) -> str:
        """
        Classify a dependency as standard library, third-party, or local.
        
        Args:
            module_name: Name of the imported module
            
        Returns:
            Dependency type: 'standard_library', 'third_party', or 'local'
        """
        # Python standard library modules (common ones)
        python_stdlib = {
            'os', 'sys', 'json', 'datetime', 'time', 'math', 'random',
            're', 'collections', 'itertools', 'functools', 'pathlib',
            'typing', 'dataclasses', 'asyncio', 'logging', 'unittest',
            'subprocess', 'threading', 'multiprocessing', 'io', 'csv',
            'xml', 'html', 'http', 'urllib', 'email', 'hashlib', 'hmac'
        }
        
        # JavaScript/Node.js built-in modules
        js_builtin = {
            'fs', 'path', 'http', 'https', 'url', 'util', 'events',
            'stream', 'crypto', 'os', 'process', 'buffer', 'child_process'
        }
        
        base_module = module_name.split('.')[0]
        
        if base_module in python_stdlib or base_module in js_builtin:
            return 'standard_library'
        elif module_name.startswith('.') or module_name.startswith('src'):
            return 'local'
        else:
            return 'third_party'
    
    def _infer_import_reason(
        self,
        module_name: str,
        symbols: List[str]
    ) -> str:
        """
        Infer why a module is imported based on its name and symbols.
        
        Args:
            module_name: Name of the imported module
            symbols: List of imported symbols
            
        Returns:
            Human-readable reason for the import
        """
        # Common patterns
        if 'test' in module_name.lower():
            return "Testing utilities"
        if 'logging' in module_name.lower():
            return "Logging functionality"
        if 'config' in module_name.lower():
            return "Configuration management"
        if 'util' in module_name.lower() or 'helper' in module_name.lower():
            return "Utility functions"
        if 'model' in module_name.lower():
            return "Data models"
        if 'api' in module_name.lower():
            return "API functionality"
        if 'db' in module_name.lower() or 'database' in module_name.lower():
            return "Database operations"
        
        # Infer from symbols
        if symbols:
            if len(symbols) == 1:
                return f"Uses {symbols[0]}"
            elif len(symbols) <= 3:
                return f"Uses {', '.join(symbols)}"
            else:
                return f"Uses multiple utilities from {module_name}"
        
        return f"Provides functionality from {module_name}"


def create_evidence_collector(repo_path: str) -> EvidenceCollector:
    """
    Factory function to create an EvidenceCollector instance.
    
    Args:
        repo_path: Path to repository root
        
    Returns:
        EvidenceCollector instance
    """
    return EvidenceCollector(repo_path)
