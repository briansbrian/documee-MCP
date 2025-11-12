"""
Documentation Coverage Analyzer for measuring documentation quality.

This module analyzes code documentation coverage by counting functions and classes
with docstrings/JSDoc comments and detecting inline comments explaining complex logic.
"""

import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass

from .symbol_extractor import SymbolInfo, FunctionInfo, ClassInfo

logger = logging.getLogger(__name__)


@dataclass
class DocumentationCoverage:
    """Documentation coverage metrics for a file.
    
    Attributes:
        total_score: Overall documentation coverage score (0.0-1.0)
        function_coverage: Percentage of functions with docstrings (0.0-1.0)
        class_coverage: Percentage of classes with docstrings (0.0-1.0)
        method_coverage: Percentage of methods with docstrings (0.0-1.0)
        total_functions: Total number of functions analyzed
        documented_functions: Number of functions with documentation
        total_classes: Total number of classes analyzed
        documented_classes: Number of classes with documentation
        total_methods: Total number of methods analyzed
        documented_methods: Number of methods with documentation
        has_inline_comments: Whether inline comments were detected
        inline_comment_bonus: Bonus score for inline comments (0.0-0.1)
    """
    total_score: float = 0.0
    function_coverage: float = 0.0
    class_coverage: float = 0.0
    method_coverage: float = 0.0
    total_functions: int = 0
    documented_functions: int = 0
    total_classes: int = 0
    documented_classes: int = 0
    total_methods: int = 0
    documented_methods: int = 0
    has_inline_comments: bool = False
    inline_comment_bonus: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        from dataclasses import asdict
        return asdict(self)


class DocumentationCoverageAnalyzer:
    """
    Analyzes documentation coverage for code files.
    
    Measures documentation quality by:
    - Counting functions with docstrings (Python) or JSDoc (JavaScript/TypeScript)
    - Counting classes with documentation
    - Calculating method-level coverage separately
    - Detecting inline comments explaining complex logic
    """
    
    def __init__(self):
        """Initialize the Documentation Coverage Analyzer."""
        logger.debug("DocumentationCoverageAnalyzer initialized")
    
    def calculate_coverage(
        self,
        symbol_info: SymbolInfo,
        file_content: Optional[str] = None,
        language: str = "python"
    ) -> DocumentationCoverage:
        """
        Calculate documentation coverage for a file.
        
        Args:
            symbol_info: Extracted symbols from the file
            file_content: Optional file content for inline comment detection
            language: Programming language (python, javascript, typescript)
        
        Returns:
            DocumentationCoverage with detailed metrics
        
        Example:
            >>> coverage = analyzer.calculate_coverage(symbols, content, "python")
            >>> print(f"Coverage: {coverage.total_score:.2%}")
        """
        coverage = DocumentationCoverage()
        
        # Count documented functions (top-level only)
        coverage.total_functions = len(symbol_info.functions)
        coverage.documented_functions = sum(
            1 for func in symbol_info.functions
            if self._has_documentation(func, language)
        )
        
        # Calculate function coverage
        if coverage.total_functions > 0:
            coverage.function_coverage = (
                coverage.documented_functions / coverage.total_functions
            )
        
        # Count documented classes
        coverage.total_classes = len(symbol_info.classes)
        coverage.documented_classes = sum(
            1 for cls in symbol_info.classes
            if self._has_documentation(cls, language)
        )
        
        # Calculate class coverage
        if coverage.total_classes > 0:
            coverage.class_coverage = (
                coverage.documented_classes / coverage.total_classes
            )
        
        # Count documented methods (within classes)
        for cls in symbol_info.classes:
            coverage.total_methods += len(cls.methods)
            coverage.documented_methods += sum(
                1 for method in cls.methods
                if self._has_documentation(method, language)
            )
        
        # Calculate method coverage
        if coverage.total_methods > 0:
            coverage.method_coverage = (
                coverage.documented_methods / coverage.total_methods
            )
        
        # Detect inline comments if file content provided
        if file_content:
            coverage.has_inline_comments = self._detect_inline_comments(
                file_content, language
            )
            if coverage.has_inline_comments:
                coverage.inline_comment_bonus = 0.1
        
        # Calculate total score
        coverage.total_score = self._calculate_total_score(coverage)
        
        logger.debug(
            f"Documentation coverage: {coverage.total_score:.2%} "
            f"(functions: {coverage.function_coverage:.2%}, "
            f"classes: {coverage.class_coverage:.2%}, "
            f"methods: {coverage.method_coverage:.2%})"
        )
        
        return coverage
    
    def _has_documentation(
        self,
        symbol: FunctionInfo | ClassInfo,
        language: str
    ) -> bool:
        """
        Check if a symbol has documentation.
        
        Args:
            symbol: Function or class to check
            language: Programming language
        
        Returns:
            True if symbol has docstring/JSDoc, False otherwise
        """
        if not symbol.docstring:
            return False
        
        # Check for meaningful documentation (not just empty or placeholder)
        doc = symbol.docstring.strip()
        
        if not doc:
            return False
        
        # Require minimum length for meaningful documentation
        if len(doc) < 10:
            return False
        
        # Filter out placeholder docstrings
        placeholders = [
            "todo",
            "fixme",
            "...",
            "tbd",
            "to be determined",
            "to be implemented"
        ]
        
        doc_lower = doc.lower()
        
        # Check if the docstring is primarily placeholder text
        # If it starts with a placeholder or is mostly placeholder, reject it
        for placeholder in placeholders:
            if doc_lower.startswith(placeholder):
                return False
            # If placeholder is significant portion of short docstring
            if placeholder in doc_lower and len(doc) < 30:
                return False
        
        return True
    
    def _detect_inline_comments(self, file_content: str, language: str) -> bool:
        """
        Detect inline comments explaining complex logic.
        
        Looks for comments within function bodies that explain what the code does,
        not just structural comments like section headers.
        
        Args:
            file_content: Source code content
            language: Programming language
        
        Returns:
            True if meaningful inline comments detected, False otherwise
        """
        if not file_content:
            return False
        
        lines = file_content.split('\n')
        inline_comment_count = 0
        
        # Define comment patterns by language
        if language == 'python':
            comment_marker = '#'
        elif language in ['javascript', 'typescript', 'java', 'go', 'rust', 'cpp', 'c', 'c_sharp', 'php']:
            comment_marker = '//'
        elif language == 'ruby':
            comment_marker = '#'
        else:
            comment_marker = '#'
        
        for line in lines:
            stripped = line.strip()
            
            # Skip empty lines
            if not stripped:
                continue
            
            # Check for inline comments (not at start of line)
            if comment_marker in line:
                # Get the part before the comment
                before_comment = line.split(comment_marker)[0]
                
                # If there's code before the comment, it's an inline comment
                if before_comment.strip():
                    inline_comment_count += 1
                    continue
                
                # Check for standalone comments that explain logic
                # (indented, not section headers)
                if stripped.startswith(comment_marker):
                    comment_text = stripped[len(comment_marker):].strip()
                    
                    # Filter out section headers and decorative comments
                    if self._is_explanatory_comment(comment_text, line):
                        inline_comment_count += 1
        
        # Require at least 3 inline comments to consider it well-commented
        return inline_comment_count >= 3
    
    def _is_explanatory_comment(self, comment_text: str, full_line: str) -> bool:
        """
        Check if a comment is explanatory (not a section header or decorator).
        
        Args:
            comment_text: The comment text without the comment marker
            full_line: The full line including indentation
        
        Returns:
            True if comment explains logic, False if it's structural
        """
        # Must be indented (inside a function/method)
        if not full_line.startswith((' ', '\t')):
            return False
        
        # Filter out section headers
        section_markers = [
            '===', '---', '***', '###',
            'section', 'region', 'endregion'
        ]
        
        comment_lower = comment_text.lower()
        if any(marker in comment_lower for marker in section_markers):
            return False
        
        # Filter out very short comments (likely not explanatory)
        if len(comment_text) < 15:
            return False
        
        # Filter out TODO/FIXME/NOTE markers (not explanatory)
        if comment_lower.startswith(('todo', 'fixme', 'note:', 'hack', 'xxx')):
            return False
        
        # Likely an explanatory comment
        return True
    
    def _calculate_total_score(self, coverage: DocumentationCoverage) -> float:
        """
        Calculate total documentation coverage score.
        
        Weights:
        - Function coverage: 40%
        - Class coverage: 30%
        - Method coverage: 30%
        - Inline comment bonus: +0.1 (capped at 1.0)
        
        Args:
            coverage: Documentation coverage metrics
        
        Returns:
            Total score from 0.0 to 1.0
        """
        # If no symbols, return 0
        if (coverage.total_functions == 0 and 
            coverage.total_classes == 0 and 
            coverage.total_methods == 0):
            return 0.0
        
        # Calculate weighted score based on what's present
        total_weight = 0.0
        weighted_score = 0.0
        
        # Function coverage (40% weight)
        if coverage.total_functions > 0:
            weighted_score += coverage.function_coverage * 0.4
            total_weight += 0.4
        
        # Class coverage (30% weight)
        if coverage.total_classes > 0:
            weighted_score += coverage.class_coverage * 0.3
            total_weight += 0.3
        
        # Method coverage (30% weight)
        if coverage.total_methods > 0:
            weighted_score += coverage.method_coverage * 0.3
            total_weight += 0.3
        
        # Normalize by actual weight used
        if total_weight > 0:
            base_score = weighted_score / total_weight
        else:
            base_score = 0.0
        
        # Add inline comment bonus
        total_score = min(1.0, base_score + coverage.inline_comment_bonus)
        
        return total_score
