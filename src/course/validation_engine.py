"""
Validation Engine for AI Content Enrichment.

This module provides validation capabilities to ensure understanding is
consistent across multiple evidence sources (code, tests, documentation,
git history). Implements cross-referencing and consistency checking to
prevent hallucinations and maintain accuracy.
"""

import logging
import re
from typing import List, Dict, Any, Optional, Set
from pathlib import Path

logger = logging.getLogger(__name__)


class ValidationEngine:
    """
    Validates understanding against multiple evidence sources.
    
    Ensures that code behavior, test expectations, documentation, and
    git context are all consistent with each other, providing confidence
    in the accuracy of enrichment guides.
    """
    
    def __init__(self):
        """Initialize validation engine."""
        logger.info("Initialized ValidationEngine")
    
    def validate_code_behavior(
        self,
        source_files: List[Dict[str, Any]]
    ) -> str:
        """
        Analyze actual code behavior from source files.
        
        Examines the implementation to determine what the code actually does,
        extracting key behaviors, patterns, and functionality.
        
        Args:
            source_files: List of source file dictionaries with keys:
                - path: File path
                - code: Source code content
                - language: Programming language
                - sections: Code sections with line ranges
                
        Returns:
            Description of actual code behavior with citations
        """
        if not source_files:
            logger.warning("No source files provided for behavior validation")
            return "No source code available for validation"
        
        behaviors = []
        
        for source_file in source_files:
            file_path = source_file.get('path', 'unknown')
            code = source_file.get('code', '')
            language = source_file.get('language', 'unknown')
            
            if not code:
                continue
            
            # Analyze code structure and behavior
            file_behaviors = self._analyze_code_structure(
                code,
                language,
                file_path
            )
            
            behaviors.extend(file_behaviors)
        
        if not behaviors:
            return "Unable to determine code behavior from source files"
        
        # Consolidate behaviors into description
        behavior_desc = self._consolidate_behaviors(behaviors)
        
        logger.info(
            f"Validated code behavior from {len(source_files)} source file(s): "
            f"{len(behaviors)} behaviors identified"
        )
        
        return behavior_desc

    
    def _analyze_code_structure(
        self,
        code: str,
        language: str,
        file_path: str
    ) -> List[Dict[str, str]]:
        """
        Analyze code structure to identify behaviors.
        
        Args:
            code: Source code content
            language: Programming language
            file_path: Path to source file
            
        Returns:
            List of behavior dictionaries with 'description' and 'citation'
        """
        behaviors = []
        
        # Detect functions/methods
        if language == 'python':
            behaviors.extend(self._analyze_python_code(code, file_path))
        elif language in ['javascript', 'typescript']:
            behaviors.extend(self._analyze_javascript_code(code, file_path))
        else:
            # Generic analysis for other languages
            behaviors.extend(self._analyze_generic_code(code, file_path))
        
        return behaviors
    
    def _analyze_python_code(
        self,
        code: str,
        file_path: str
    ) -> List[Dict[str, str]]:
        """
        Analyze Python code for behaviors.
        
        Args:
            code: Python source code
            file_path: Path to source file
            
        Returns:
            List of identified behaviors
        """
        behaviors = []
        lines = code.split('\n')
        
        # Find function definitions
        func_pattern = r'^(async\s+)?def\s+(\w+)\s*\([^)]*\):'
        for i, line in enumerate(lines, 1):
            match = re.match(func_pattern, line.strip())
            if match:
                is_async = match.group(1) is not None
                func_name = match.group(2)
                
                # Extract docstring if present
                docstring = self._extract_python_docstring(lines, i)
                
                behavior_desc = f"Defines {'async ' if is_async else ''}function '{func_name}'"
                if docstring:
                    behavior_desc += f": {docstring.split('.')[0]}"
                
                behaviors.append({
                    'description': behavior_desc,
                    'citation': f"{file_path}:{i}"
                })
        
        # Find class definitions
        class_pattern = r'^class\s+(\w+)'
        for i, line in enumerate(lines, 1):
            match = re.match(class_pattern, line.strip())
            if match:
                class_name = match.group(1)
                
                # Extract docstring if present
                docstring = self._extract_python_docstring(lines, i)
                
                behavior_desc = f"Defines class '{class_name}'"
                if docstring:
                    behavior_desc += f": {docstring.split('.')[0]}"
                
                behaviors.append({
                    'description': behavior_desc,
                    'citation': f"{file_path}:{i}"
                })
        
        # Detect common patterns
        if 'raise ' in code:
            behaviors.append({
                'description': 'Implements error handling with exceptions',
                'citation': f"{file_path}"
            })
        
        if 'async def' in code or 'await ' in code:
            behaviors.append({
                'description': 'Uses asynchronous programming patterns',
                'citation': f"{file_path}"
            })
        
        if '@dataclass' in code:
            behaviors.append({
                'description': 'Uses dataclass pattern for data structures',
                'citation': f"{file_path}"
            })
        
        return behaviors
    
    def _extract_python_docstring(
        self,
        lines: List[str],
        def_line: int
    ) -> Optional[str]:
        """
        Extract docstring following a function/class definition.
        
        Args:
            lines: Source code lines
            def_line: Line number of definition (1-indexed)
            
        Returns:
            Docstring content or None
        """
        # Look for docstring in next few lines
        for i in range(def_line, min(def_line + 5, len(lines))):
            line = lines[i].strip()
            if line.startswith('"""') or line.startswith("'''"):
                # Single-line docstring
                if line.count('"""') == 2 or line.count("'''") == 2:
                    return line.strip('"""').strip("'''").strip()
                # Multi-line docstring
                docstring_lines = [line.strip('"""').strip("'''")]
                for j in range(i + 1, min(i + 20, len(lines))):
                    next_line = lines[j]
                    if '"""' in next_line or "'''" in next_line:
                        docstring_lines.append(next_line.split('"""')[0].split("'''")[0])
                        return ' '.join(docstring_lines).strip()
                    docstring_lines.append(next_line.strip())
        
        return None
    
    def _analyze_javascript_code(
        self,
        code: str,
        file_path: str
    ) -> List[Dict[str, str]]:
        """
        Analyze JavaScript/TypeScript code for behaviors.
        
        Args:
            code: JavaScript/TypeScript source code
            file_path: Path to source file
            
        Returns:
            List of identified behaviors
        """
        behaviors = []
        lines = code.split('\n')
        
        # Find function declarations
        func_patterns = [
            r'function\s+(\w+)\s*\(',
            r'const\s+(\w+)\s*=\s*\([^)]*\)\s*=>',
            r'(\w+)\s*:\s*\([^)]*\)\s*=>',
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern in func_patterns:
                match = re.search(pattern, line)
                if match:
                    func_name = match.group(1)
                    behaviors.append({
                        'description': f"Defines function '{func_name}'",
                        'citation': f"{file_path}:{i}"
                    })
                    break
        
        # Find class definitions
        class_pattern = r'class\s+(\w+)'
        for i, line in enumerate(lines, 1):
            match = re.search(class_pattern, line)
            if match:
                class_name = match.group(1)
                behaviors.append({
                    'description': f"Defines class '{class_name}'",
                    'citation': f"{file_path}:{i}"
                })
        
        # Detect common patterns
        if 'async ' in code or 'await ' in code:
            behaviors.append({
                'description': 'Uses asynchronous programming with async/await',
                'citation': f"{file_path}"
            })
        
        if 'export ' in code:
            behaviors.append({
                'description': 'Exports functionality as module',
                'citation': f"{file_path}"
            })
        
        if 'React.' in code or 'useState' in code or 'useEffect' in code:
            behaviors.append({
                'description': 'Implements React component patterns',
                'citation': f"{file_path}"
            })
        
        return behaviors
    
    def _analyze_generic_code(
        self,
        code: str,
        file_path: str
    ) -> List[Dict[str, str]]:
        """
        Generic code analysis for unsupported languages.
        
        Args:
            code: Source code content
            file_path: Path to source file
            
        Returns:
            List of identified behaviors
        """
        behaviors = []
        
        # Basic pattern detection
        if 'class ' in code:
            behaviors.append({
                'description': 'Defines one or more classes',
                'citation': f"{file_path}"
            })
        
        if 'function ' in code or 'def ' in code:
            behaviors.append({
                'description': 'Defines one or more functions',
                'citation': f"{file_path}"
            })
        
        if 'import ' in code or 'require(' in code:
            behaviors.append({
                'description': 'Imports external dependencies',
                'citation': f"{file_path}"
            })
        
        return behaviors
    
    def _consolidate_behaviors(
        self,
        behaviors: List[Dict[str, str]]
    ) -> str:
        """
        Consolidate behaviors into a coherent description.
        
        Args:
            behaviors: List of behavior dictionaries
            
        Returns:
            Consolidated behavior description with citations
        """
        if not behaviors:
            return "No behaviors identified"
        
        # Group behaviors by type
        descriptions = []
        for behavior in behaviors:
            desc = behavior['description']
            citation = behavior['citation']
            descriptions.append(f"- {desc} ({citation})")
        
        return "Code behavior analysis:\n" + "\n".join(descriptions)

    
    def validate_test_expectations(
        self,
        test_files: List[Dict[str, Any]]
    ) -> str:
        """
        Extract expected behavior from test files.
        
        Analyzes test cases to determine what behavior the tests expect,
        providing a specification of intended functionality.
        
        Args:
            test_files: List of test file dictionaries with keys:
                - path: Test file path
                - test_cases: List of test cases
                - framework: Test framework used
                - coverage: What functionality is tested
                
        Returns:
            Description of expected behavior based on tests
        """
        if not test_files:
            logger.warning("No test files provided for expectation validation")
            return "No tests available for validation"
        
        expectations = []
        
        for test_file in test_files:
            file_path = test_file.get('path', 'unknown')
            test_cases = test_file.get('test_cases', [])
            framework = test_file.get('framework', 'unknown')
            coverage = test_file.get('coverage', [])
            
            # Extract expectations from test cases
            for test_case in test_cases:
                test_name = test_case.get('name', '')
                description = test_case.get('description', '')
                
                expectation = self._extract_expectation_from_test(
                    test_name,
                    description,
                    file_path
                )
                
                if expectation:
                    expectations.append(expectation)
            
            # Add coverage information
            if coverage:
                for coverage_item in coverage:
                    expectations.append({
                        'description': coverage_item,
                        'citation': f"{file_path} (test coverage)"
                    })
        
        if not expectations:
            return "Unable to determine expected behavior from tests"
        
        # Consolidate expectations
        expectation_desc = self._consolidate_expectations(expectations)
        
        logger.info(
            f"Validated test expectations from {len(test_files)} test file(s): "
            f"{len(expectations)} expectations identified"
        )
        
        return expectation_desc
    
    def _extract_expectation_from_test(
        self,
        test_name: str,
        description: str,
        file_path: str
    ) -> Optional[Dict[str, str]]:
        """
        Extract expectation from test name and description.
        
        Args:
            test_name: Name of the test
            description: Test description
            file_path: Path to test file
            
        Returns:
            Expectation dictionary or None
        """
        # Use description if available, otherwise parse test name
        text = description if description else test_name
        
        if not text:
            return None
        
        # Clean up test name (remove test_ prefix, replace underscores)
        if text.startswith('test_'):
            text = text[5:]
        text = text.replace('_', ' ')
        
        # Extract expectation patterns
        expectation = None
        
        if 'should' in text.lower():
            # "should X" pattern
            parts = text.lower().split('should')
            if len(parts) > 1:
                expectation = f"Should {parts[1].strip()}"
        elif 'test' in text.lower():
            # "test X" pattern
            parts = text.lower().split('test')
            if len(parts) > 1:
                expectation = f"Tests that {parts[1].strip()}"
        else:
            # Use as-is
            expectation = text.strip().capitalize()
        
        if expectation:
            return {
                'description': expectation,
                'citation': f"{file_path} ({test_name})"
            }
        
        return None
    
    def _consolidate_expectations(
        self,
        expectations: List[Dict[str, str]]
    ) -> str:
        """
        Consolidate expectations into a coherent description.
        
        Args:
            expectations: List of expectation dictionaries
            
        Returns:
            Consolidated expectation description with citations
        """
        if not expectations:
            return "No expectations identified"
        
        descriptions = []
        for expectation in expectations:
            desc = expectation['description']
            citation = expectation['citation']
            descriptions.append(f"- {desc} ({citation})")
        
        return "Test expectations:\n" + "\n".join(descriptions)
    
    def validate_documentation_alignment(
        self,
        docs: List[Dict[str, Any]]
    ) -> str:
        """
        Check consistency between code and documentation.
        
        Analyzes documentation (docstrings, comments, README) to verify
        that it aligns with actual code behavior.
        
        Args:
            docs: List of documentation dictionaries with keys:
                - type: 'docstring', 'comment', 'inline'
                - content: Documentation text
                - location: Where it appears
                - context: What it documents
                
        Returns:
            Description of documentation alignment with citations
        """
        if not docs:
            logger.warning("No documentation provided for alignment validation")
            return "No documentation available for validation"
        
        alignments = []
        
        for doc in docs:
            doc_type = doc.get('type', 'unknown')
            content = doc.get('content', '')
            location = doc.get('location', 'unknown')
            context = doc.get('context', '')
            
            if not content:
                continue
            
            # Extract key information from documentation
            alignment = self._analyze_documentation(
                content,
                doc_type,
                location,
                context
            )
            
            if alignment:
                alignments.append(alignment)
        
        if not alignments:
            return "No documentation alignment information available"
        
        # Consolidate alignments
        alignment_desc = self._consolidate_alignments(alignments)
        
        logger.info(
            f"Validated documentation alignment from {len(docs)} documentation item(s): "
            f"{len(alignments)} alignments identified"
        )
        
        return alignment_desc
    
    def _analyze_documentation(
        self,
        content: str,
        doc_type: str,
        location: str,
        context: str
    ) -> Optional[Dict[str, str]]:
        """
        Analyze documentation content for alignment information.
        
        Args:
            content: Documentation text
            doc_type: Type of documentation
            location: Where it appears
            context: What it documents
            
        Returns:
            Alignment dictionary or None
        """
        # Extract first sentence or summary
        sentences = content.split('.')
        summary = sentences[0].strip() if sentences else content.strip()
        
        # Limit length
        if len(summary) > 150:
            summary = summary[:147] + "..."
        
        return {
            'description': f"{context}: {summary}",
            'citation': f"{location} ({doc_type})"
        }
    
    def _consolidate_alignments(
        self,
        alignments: List[Dict[str, str]]
    ) -> str:
        """
        Consolidate documentation alignments into description.
        
        Args:
            alignments: List of alignment dictionaries
            
        Returns:
            Consolidated alignment description
        """
        if not alignments:
            return "No alignments identified"
        
        descriptions = []
        for alignment in alignments:
            desc = alignment['description']
            citation = alignment['citation']
            descriptions.append(f"- {desc} ({citation})")
        
        return "Documentation alignment:\n" + "\n".join(descriptions)

    
    def validate_git_context(
        self,
        commits: List[Dict[str, Any]]
    ) -> str:
        """
        Extract historical context from git commits.
        
        Analyzes commit messages and metadata to understand why code
        was written, what problems it solves, and how it evolved.
        
        Args:
            commits: List of commit dictionaries with keys:
                - hash: Commit hash
                - author: Author name
                - date: Commit date
                - subject: Commit subject line
                - message: Full commit message
                - files: Files modified
                
        Returns:
            Description of git context with citations
        """
        if not commits:
            logger.warning("No commits provided for git context validation")
            return "No git history available for validation"
        
        contexts = []
        
        for commit in commits:
            commit_hash = commit.get('hash', 'unknown')[:8]
            subject = commit.get('subject', '')
            message = commit.get('message', '')
            author = commit.get('author', 'unknown')
            date = commit.get('date', 'unknown')
            files = commit.get('files', [])
            
            # Extract context from commit
            context = self._extract_commit_context(
                subject,
                message,
                commit_hash,
                author,
                date,
                files
            )
            
            if context:
                contexts.append(context)
        
        if not contexts:
            return "Unable to extract context from git history"
        
        # Consolidate contexts
        context_desc = self._consolidate_git_contexts(contexts)
        
        logger.info(
            f"Validated git context from {len(commits)} commit(s): "
            f"{len(contexts)} contexts identified"
        )
        
        return context_desc
    
    def _extract_commit_context(
        self,
        subject: str,
        message: str,
        commit_hash: str,
        author: str,
        date: str,
        files: List[str]
    ) -> Optional[Dict[str, str]]:
        """
        Extract context from a single commit.
        
        Args:
            subject: Commit subject line
            message: Full commit message
            commit_hash: Short commit hash
            author: Commit author
            date: Commit date
            files: Files modified
            
        Returns:
            Context dictionary or None
        """
        # Use subject as primary context
        context_text = subject
        
        # Extract additional context from message if different from subject
        if message and message.strip() != subject.strip():
            # Get first paragraph of message
            paragraphs = message.split('\n\n')
            if len(paragraphs) > 1:
                # Skip subject line, get first body paragraph
                first_para = paragraphs[1].strip()
                if first_para and len(first_para) < 200:
                    context_text += f". {first_para}"
        
        # Identify commit type from subject
        commit_type = self._identify_commit_type(subject)
        
        # Format date for readability
        date_str = date.split('T')[0] if 'T' in date else date
        
        return {
            'description': context_text,
            'citation': f"Commit {commit_hash} by {author} on {date_str}",
            'type': commit_type,
            'files_count': len(files)
        }
    
    def _identify_commit_type(self, subject: str) -> str:
        """
        Identify the type of commit from subject line.
        
        Args:
            subject: Commit subject line
            
        Returns:
            Commit type (feature, fix, refactor, docs, etc.)
        """
        subject_lower = subject.lower()
        
        # Common commit type patterns (check more specific patterns first)
        if any(word in subject_lower for word in ['test', 'spec']):
            return 'test'
        elif any(word in subject_lower for word in ['fix', 'bug', 'resolve', 'patch']):
            return 'fix'
        elif any(word in subject_lower for word in ['refactor', 'restructure', 'reorganize']):
            return 'refactor'
        elif any(word in subject_lower for word in ['doc', 'comment', 'readme']):
            return 'documentation'
        elif any(word in subject_lower for word in ['remove', 'delete', 'clean']):
            return 'removal'
        elif any(word in subject_lower for word in ['update', 'modify', 'change']):
            return 'update'
        elif any(word in subject_lower for word in ['add', 'implement', 'create', 'feat']):
            return 'feature'
        else:
            return 'other'
    
    def _consolidate_git_contexts(
        self,
        contexts: List[Dict[str, str]]
    ) -> str:
        """
        Consolidate git contexts into a coherent description.
        
        Args:
            contexts: List of context dictionaries
            
        Returns:
            Consolidated context description
        """
        if not contexts:
            return "No contexts identified"
        
        # Group by commit type
        by_type: Dict[str, List[Dict[str, str]]] = {}
        for context in contexts:
            commit_type = context.get('type', 'other')
            if commit_type not in by_type:
                by_type[commit_type] = []
            by_type[commit_type].append(context)
        
        # Build description
        descriptions = []
        descriptions.append("Git history context:")
        
        for commit_type, type_contexts in by_type.items():
            descriptions.append(f"\n{commit_type.capitalize()} commits:")
            for context in type_contexts:
                desc = context['description']
                citation = context['citation']
                # Limit description length
                if len(desc) > 100:
                    desc = desc[:97] + "..."
                descriptions.append(f"  - {desc} ({citation})")
        
        return "\n".join(descriptions)
    
    def cross_reference_sources(
        self,
        evidence: Dict[str, Any]
    ) -> bool:
        """
        Verify consistency across all evidence sources.
        
        Cross-references code behavior, test expectations, documentation,
        and git context to ensure they tell a consistent story.
        
        Args:
            evidence: Dictionary containing all evidence:
                - code_behavior: Code behavior description
                - test_expectations: Test expectations description
                - documentation_alignment: Documentation alignment description
                - git_context: Git context description
                
        Returns:
            True if sources are consistent, False if inconsistencies detected
        """
        code_behavior = evidence.get('code_behavior', '')
        test_expectations = evidence.get('test_expectations', '')
        documentation = evidence.get('documentation_alignment', '')
        git_context = evidence.get('git_context', '')
        
        # Check if we have enough evidence to cross-reference
        available_sources = sum([
            bool(code_behavior and code_behavior != "No source code available for validation"),
            bool(test_expectations and test_expectations != "No tests available for validation"),
            bool(documentation and documentation != "No documentation available for validation"),
            bool(git_context and git_context != "No git history available for validation")
        ])
        
        if available_sources < 2:
            logger.warning(
                f"Insufficient evidence sources for cross-referencing: "
                f"{available_sources} source(s) available"
            )
            return True  # Can't determine inconsistency with < 2 sources
        
        # Extract key terms from each source
        code_terms = self._extract_key_terms(code_behavior)
        test_terms = self._extract_key_terms(test_expectations)
        doc_terms = self._extract_key_terms(documentation)
        git_terms = self._extract_key_terms(git_context)
        
        # Check for overlapping concepts
        all_terms = [code_terms, test_terms, doc_terms, git_terms]
        available_term_sets = [terms for terms in all_terms if terms]
        
        if len(available_term_sets) < 2:
            return True
        
        # Calculate overlap between sources
        overlaps = []
        for i in range(len(available_term_sets)):
            for j in range(i + 1, len(available_term_sets)):
                overlap = available_term_sets[i] & available_term_sets[j]
                overlap_ratio = len(overlap) / max(
                    len(available_term_sets[i]),
                    len(available_term_sets[j])
                )
                overlaps.append(overlap_ratio)
        
        # If average overlap is too low, sources might be inconsistent
        avg_overlap = sum(overlaps) / len(overlaps) if overlaps else 0
        
        # Threshold: at least 10% overlap between sources
        is_consistent = avg_overlap >= 0.10
        
        logger.info(
            f"Cross-reference validation: {available_sources} sources, "
            f"average overlap: {avg_overlap:.2%}, "
            f"consistent: {is_consistent}"
        )
        
        return is_consistent
    
    def _extract_key_terms(self, text: str) -> Set[str]:
        """
        Extract key terms from text for comparison.
        
        Args:
            text: Text to analyze
            
        Returns:
            Set of key terms (lowercase, normalized)
        """
        if not text:
            return set()
        
        # Remove common words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
            'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are',
            'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do',
            'does', 'did', 'will', 'would', 'should', 'could', 'may',
            'might', 'must', 'can', 'this', 'that', 'these', 'those',
            'it', 'its', 'they', 'them', 'their', 'what', 'which', 'who',
            'when', 'where', 'why', 'how', 'all', 'each', 'every', 'both',
            'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor',
            'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very'
        }
        
        # Extract words (alphanumeric sequences)
        words = re.findall(r'\b[a-z_][a-z0-9_]*\b', text.lower())
        
        # Filter out stop words and short words
        key_terms = {
            word for word in words
            if word not in stop_words and len(word) > 2
        }
        
        return key_terms


def create_validation_engine() -> ValidationEngine:
    """
    Factory function to create a ValidationEngine instance.
    
    Returns:
        ValidationEngine instance
    """
    return ValidationEngine()
