"""
Teaching Value Scorer for scoring files by educational value.

This module scores code files based on their teaching value by analyzing
documentation coverage, code complexity, pattern usage, and code structure.
"""

import logging
from typing import List, Dict, Any
from dataclasses import dataclass, field

from .symbol_extractor import SymbolInfo, FunctionInfo, ClassInfo
from .complexity_analyzer import ComplexityMetrics
from .documentation_coverage import DocumentationCoverage
from .config import AnalysisConfig

logger = logging.getLogger(__name__)


@dataclass
class TeachingValueScore:
    """
    Teaching value score for a code file.
    
    Attributes:
        total_score: Overall teaching value score (0.0-1.0)
        documentation_score: Score based on documentation coverage (0.0-1.0)
        complexity_score: Score based on code complexity (0.0-1.0)
        pattern_score: Score based on pattern usage (0.0-1.0)
        structure_score: Score based on code structure (0.0-1.0)
        explanation: Human-readable explanation of the score
        factors: Detailed breakdown of scoring factors
    """
    total_score: float = 0.0
    documentation_score: float = 0.0
    complexity_score: float = 0.0
    pattern_score: float = 0.0
    structure_score: float = 0.0
    explanation: str = ""
    factors: Dict[str, Any] = field(default_factory=dict)


class TeachingValueScorer:
    """
    Scores files by teaching value.
    
    Evaluates code based on:
    - Documentation coverage (higher is better)
    - Code complexity (moderate is best)
    - Pattern usage (more patterns = more teaching value)
    - Code structure (clear organization is better)
    """
    
    def __init__(self, config: AnalysisConfig):
        """
        Initialize the Teaching Value Scorer.
        
        Args:
            config: Analysis configuration with weights
        """
        self.weights = config.teaching_value_weights
        logger.debug(f"TeachingValueScorer initialized with weights: {self.weights}")
    
    def score_file(
        self,
        symbol_info: SymbolInfo,
        patterns: List[Any],
        complexity_metrics: ComplexityMetrics,
        documentation_coverage: DocumentationCoverage
    ) -> TeachingValueScore:
        """
        Calculate teaching value score for a file.
        
        Args:
            symbol_info: Extracted symbols from the file
            patterns: Detected patterns in the file
            complexity_metrics: Complexity metrics for the file
            documentation_coverage: Documentation coverage metrics
        
        Returns:
            TeachingValueScore with detailed breakdown
        
        Example:
            >>> score = scorer.score_file(symbols, patterns, complexity, docs)
            >>> print(f"Teaching value: {score.total_score:.2f}")
        """
        # Calculate individual scores
        doc_score = self._score_documentation(documentation_coverage)
        complexity_score = self._score_complexity(complexity_metrics)
        pattern_score = self._score_patterns(patterns)
        structure_score = self._score_structure(symbol_info)
        
        # Calculate weighted total
        total_score = (
            self.weights['documentation'] * doc_score +
            self.weights['complexity'] * complexity_score +
            self.weights['pattern'] * pattern_score +
            self.weights['structure'] * structure_score
        )
        
        # Ensure score is in valid range
        total_score = max(0.0, min(1.0, total_score))
        
        # Generate explanation
        explanation = self._generate_explanation(
            total_score,
            doc_score,
            complexity_score,
            pattern_score,
            structure_score,
            complexity_metrics,
            documentation_coverage
        )
        
        # Build detailed factors
        factors = {
            'documentation': {
                'score': doc_score,
                'weight': self.weights['documentation'],
                'coverage': documentation_coverage.total_score,
                'function_coverage': documentation_coverage.function_coverage,
                'class_coverage': documentation_coverage.class_coverage
            },
            'complexity': {
                'score': complexity_score,
                'weight': self.weights['complexity'],
                'avg_complexity': complexity_metrics.avg_complexity,
                'max_complexity': complexity_metrics.max_complexity,
                'high_complexity_count': complexity_metrics.high_complexity_count,
                'trivial_count': complexity_metrics.trivial_count
            },
            'patterns': {
                'score': pattern_score,
                'weight': self.weights['pattern'],
                'pattern_count': len(patterns),
                'patterns': [p.pattern_type for p in patterns] if patterns else []
            },
            'structure': {
                'score': structure_score,
                'weight': self.weights['structure'],
                'total_functions': len(symbol_info.functions),
                'total_classes': len(symbol_info.classes)
            }
        }
        
        score = TeachingValueScore(
            total_score=round(total_score, 3),
            documentation_score=round(doc_score, 3),
            complexity_score=round(complexity_score, 3),
            pattern_score=round(pattern_score, 3),
            structure_score=round(structure_score, 3),
            explanation=explanation,
            factors=factors
        )
        
        logger.debug(
            f"Teaching value score: {score.total_score:.3f} "
            f"(doc={doc_score:.2f}, complexity={complexity_score:.2f}, "
            f"pattern={pattern_score:.2f}, structure={structure_score:.2f})"
        )
        
        return score
    
    def _score_documentation(self, coverage: DocumentationCoverage) -> float:
        """
        Score based on documentation coverage.
        
        Higher documentation coverage = higher score.
        
        Args:
            coverage: Documentation coverage metrics
        
        Returns:
            Score from 0.0 to 1.0
        """
        # Use the total coverage score directly
        return coverage.total_score
    
    def _score_complexity(self, metrics: ComplexityMetrics) -> float:
        """
        Score based on code complexity (prefer moderate complexity).
        
        Scoring:
        - 1.0 if 3 <= avg_complexity <= 7 (sweet spot for teaching)
        - 0.7 if 2 <= avg_complexity < 3 or 7 < avg_complexity <= 10
        - 0.3 if avg_complexity > 10 or avg_complexity < 2
        
        Args:
            metrics: Complexity metrics
        
        Returns:
            Score from 0.0 to 1.0
        """
        avg_complexity = metrics.avg_complexity
        
        # No functions = no complexity score
        if avg_complexity == 0:
            return 0.0
        
        # Sweet spot: moderate complexity (3-7)
        if 3 <= avg_complexity <= 7:
            return 1.0
        
        # Acceptable: slightly simple or slightly complex (2-3 or 7-10)
        elif 2 <= avg_complexity < 3 or 7 < avg_complexity <= 10:
            return 0.7
        
        # Poor: too simple or too complex (<2 or >10)
        else:
            return 0.3
    
    def _score_patterns(self, patterns: List[Any]) -> float:
        """
        Score based on pattern usage.
        
        More patterns = more teaching value (capped at 1.0).
        Each pattern adds 0.2 to the score.
        
        Args:
            patterns: List of detected patterns
        
        Returns:
            Score from 0.0 to 1.0
        """
        if not patterns:
            return 0.0
        
        # Each pattern adds 0.2, capped at 1.0
        score = len(patterns) * 0.2
        return min(1.0, score)
    
    def _score_structure(self, symbol_info: SymbolInfo) -> float:
        """
        Score based on code structure clarity.
        
        Evaluates:
        - Presence of both functions and classes (good organization)
        - Reasonable number of functions per class
        - Consistent naming (all functions have names)
        
        Args:
            symbol_info: Symbol information
        
        Returns:
            Score from 0.0 to 1.0
        """
        score = 0.0
        
        total_functions = len(symbol_info.functions)
        total_classes = len(symbol_info.classes)
        
        # No code = no structure score
        if total_functions == 0 and total_classes == 0:
            return 0.0
        
        # Bonus for having both functions and classes (good organization)
        if total_functions > 0 and total_classes > 0:
            score += 0.3
        elif total_functions > 0 or total_classes > 0:
            score += 0.2
        
        # Check class structure
        if total_classes > 0:
            methods_per_class = []
            for cls in symbol_info.classes:
                methods_per_class.append(len(cls.methods))
            
            avg_methods = sum(methods_per_class) / len(methods_per_class)
            
            # Good: 2-10 methods per class
            if 2 <= avg_methods <= 10:
                score += 0.4
            # Acceptable: 1 or 11-15 methods
            elif avg_methods == 1 or 11 <= avg_methods <= 15:
                score += 0.2
            # Poor: 0 or >15 methods
            else:
                score += 0.1
        else:
            # If no classes, check function count
            # Good: 3-15 functions
            if 3 <= total_functions <= 15:
                score += 0.4
            # Acceptable: 1-2 or 16-25 functions
            elif total_functions <= 2 or 16 <= total_functions <= 25:
                score += 0.2
            # Poor: >25 functions (too many)
            else:
                score += 0.1
        
        # Check naming consistency (all symbols have names)
        all_named = True
        for func in symbol_info.functions:
            if not func.name or func.name.strip() == '':
                all_named = False
                break
        
        if all_named:
            for cls in symbol_info.classes:
                if not cls.name or cls.name.strip() == '':
                    all_named = False
                    break
        
        if all_named:
            score += 0.3
        else:
            score += 0.1
        
        return min(1.0, score)
    
    def _generate_explanation(
        self,
        total_score: float,
        doc_score: float,
        complexity_score: float,
        pattern_score: float,
        structure_score: float,
        complexity_metrics: ComplexityMetrics,
        documentation_coverage: DocumentationCoverage
    ) -> str:
        """
        Generate human-readable explanation of the score.
        
        Args:
            total_score: Total teaching value score
            doc_score: Documentation score
            complexity_score: Complexity score
            pattern_score: Pattern score
            structure_score: Structure score
            complexity_metrics: Complexity metrics
            documentation_coverage: Documentation coverage
        
        Returns:
            Human-readable explanation string
        """
        # Determine overall rating
        if total_score >= 0.7:
            rating = "Excellent"
        elif total_score >= 0.5:
            rating = "Good"
        elif total_score >= 0.3:
            rating = "Fair"
        else:
            rating = "Poor"
        
        explanation_parts = [
            f"{rating} teaching value (score: {total_score:.2f})."
        ]
        
        # Documentation feedback
        if doc_score >= 0.7:
            explanation_parts.append(
                f"Well-documented ({documentation_coverage.total_score:.0%} coverage)."
            )
        elif doc_score >= 0.4:
            explanation_parts.append(
                f"Moderate documentation ({documentation_coverage.total_score:.0%} coverage)."
            )
        else:
            explanation_parts.append(
                f"Poor documentation ({documentation_coverage.total_score:.0%} coverage)."
            )
        
        # Complexity feedback
        avg_complexity = complexity_metrics.avg_complexity
        if complexity_score >= 0.9:
            explanation_parts.append(
                f"Ideal complexity (avg: {avg_complexity:.1f}) for teaching."
            )
        elif complexity_score >= 0.6:
            if avg_complexity < 3:
                explanation_parts.append(
                    f"Slightly simple (avg complexity: {avg_complexity:.1f})."
                )
            else:
                explanation_parts.append(
                    f"Slightly complex (avg complexity: {avg_complexity:.1f})."
                )
        else:
            if avg_complexity < 2:
                explanation_parts.append(
                    f"Too simple (avg complexity: {avg_complexity:.1f}) for teaching."
                )
            else:
                explanation_parts.append(
                    f"Too complex (avg complexity: {avg_complexity:.1f}) for teaching."
                )
        
        # Pattern feedback
        if pattern_score >= 0.4:
            explanation_parts.append("Contains useful patterns.")
        elif pattern_score > 0:
            explanation_parts.append("Contains some patterns.")
        
        # Structure feedback
        if structure_score >= 0.7:
            explanation_parts.append("Well-structured code.")
        elif structure_score >= 0.4:
            explanation_parts.append("Reasonable structure.")
        else:
            explanation_parts.append("Could improve structure.")
        
        return " ".join(explanation_parts)
