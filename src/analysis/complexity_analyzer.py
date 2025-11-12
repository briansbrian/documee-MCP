"""
Complexity Analyzer for calculating code complexity metrics.

This module analyzes code complexity including cyclomatic complexity,
nesting depth, and decision point counting across multiple languages.
"""

import logging
from typing import Any, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ComplexityMetrics:
    """
    Complexity metrics for a code file.
    
    Attributes:
        avg_complexity: Average cyclomatic complexity across all functions
        max_complexity: Maximum complexity found in any function
        min_complexity: Minimum complexity found in any function
        high_complexity_count: Number of functions with complexity > 10
        trivial_count: Number of functions with complexity < 2
        avg_nesting_depth: Average nesting depth across all functions
        max_nesting_depth: Maximum nesting depth found
        total_decision_points: Total decision points in the file
    """
    avg_complexity: float = 0.0
    max_complexity: int = 0
    min_complexity: int = 0
    high_complexity_count: int = 0
    trivial_count: int = 0
    avg_nesting_depth: float = 0.0
    max_nesting_depth: int = 0
    total_decision_points: int = 0


class ComplexityAnalyzer:
    """
    Analyzes code complexity metrics.
    
    Calculates cyclomatic complexity, nesting depth, and identifies
    high complexity and trivial functions.
    """
    
    def __init__(self):
        """Initialize the Complexity Analyzer."""
        logger.debug("ComplexityAnalyzer initialized")
        
        # Language-specific decision node types
        self.decision_nodes = {
            'python': {
                'if_statement', 'elif_clause',
                'for_statement', 'while_statement',
                'except_clause',
                'case_clause',  # Python 3.10+ match statements
                'boolean_operator'  # and, or
            },
            'javascript': {
                'if_statement',
                'for_statement', 'for_in_statement',
                'while_statement', 'do_statement',
                'switch_case', 'case',
                'catch_clause',
                'ternary_expression',
                'binary_expression'  # && and ||
            },
            'typescript': {
                'if_statement',
                'for_statement', 'for_in_statement',
                'while_statement', 'do_statement',
                'switch_case', 'case',
                'catch_clause',
                'ternary_expression',
                'binary_expression'
            },
            'java': {
                'if_statement',
                'for_statement', 'enhanced_for_statement',
                'while_statement', 'do_statement',
                'switch_block_statement_group', 'switch_label',
                'catch_clause',
                'ternary_expression',
                'binary_expression'
            },
            'go': {
                'if_statement',
                'for_statement',
                'switch_statement', 'case_clause',
                'select_statement',
                'binary_expression'
            },
            'rust': {
                'if_expression',
                'for_expression', 'while_expression', 'loop_expression',
                'match_expression', 'match_arm',
                'binary_expression'
            },
            'cpp': {
                'if_statement',
                'for_statement', 'for_range_loop',
                'while_statement', 'do_statement',
                'switch_statement', 'case_statement',
                'catch_clause',
                'conditional_expression',
                'binary_expression'
            },
            'c_sharp': {
                'if_statement',
                'for_statement', 'foreach_statement',
                'while_statement', 'do_statement',
                'switch_statement', 'switch_section',
                'catch_clause',
                'conditional_expression',
                'binary_expression'
            },
            'ruby': {
                'if', 'unless', 'elsif',
                'for', 'while', 'until',
                'case', 'when',
                'rescue',
                'binary'
            },
            'php': {
                'if_statement',
                'for_statement', 'foreach_statement',
                'while_statement', 'do_statement',
                'switch_statement', 'case_statement',
                'catch_clause',
                'ternary_expression',
                'binary_expression'
            }
        }
        
        # Logical operators that count as decision points
        self.logical_operators = {'&&', '||', 'and', 'or', 'AND', 'OR'}
    
    def calculate_complexity(self, node: Any, language: str) -> int:
        """
        Calculate cyclomatic complexity for a function.
        
        Complexity starts at 1 and increases by 1 for each:
        - if, elif, else if
        - for, while, do-while
        - case in switch/match statements
        - catch/except clauses
        - and, or, &&, || operators
        
        Args:
            node: Function node to analyze
            language: Programming language
        
        Returns:
            Cyclomatic complexity score
        
        Example:
            >>> complexity = analyzer.calculate_complexity(func_node, 'python')
            >>> print(f"Complexity: {complexity}")
        """
        complexity = 1
        
        # Get decision nodes for this language
        decision_node_types = self.decision_nodes.get(language, set())
        
        # Recursively count decision points
        complexity += self._count_decision_points(node, decision_node_types)
        
        return complexity
    
    def calculate_nesting_depth(self, node: Any) -> int:
        """
        Calculate maximum nesting depth for a function.
        
        Measures the maximum level of nested control structures
        (if, for, while, etc.).
        
        Args:
            node: Function node to analyze
        
        Returns:
            Maximum nesting depth
        
        Example:
            >>> depth = analyzer.calculate_nesting_depth(func_node)
            >>> print(f"Max nesting depth: {depth}")
        """
        return self._calculate_depth_recursive(node, 0)
    
    def analyze_file(self, symbol_info: Any) -> ComplexityMetrics:
        """
        Analyze complexity metrics for an entire file.
        
        Args:
            symbol_info: SymbolInfo containing functions and classes
        
        Returns:
            ComplexityMetrics with aggregated statistics
        
        Example:
            >>> metrics = analyzer.analyze_file(symbol_info)
            >>> print(f"Average complexity: {metrics.avg_complexity}")
        """
        complexities = []
        nesting_depths = []
        high_complexity_count = 0
        trivial_count = 0
        total_decision_points = 0
        
        # Analyze all functions
        for func in symbol_info.functions:
            complexity = func.complexity
            complexities.append(complexity)
            
            # Count high complexity functions (>10)
            if complexity > 10:
                high_complexity_count += 1
            
            # Count trivial functions (<2)
            if complexity < 2:
                trivial_count += 1
            
            # Decision points = complexity - 1
            total_decision_points += (complexity - 1)
        
        # Analyze methods in classes
        for cls in symbol_info.classes:
            for method in cls.methods:
                complexity = method.complexity
                complexities.append(complexity)
                
                if complexity > 10:
                    high_complexity_count += 1
                
                if complexity < 2:
                    trivial_count += 1
                
                total_decision_points += (complexity - 1)
        
        # Calculate statistics
        if complexities:
            avg_complexity = sum(complexities) / len(complexities)
            max_complexity = max(complexities)
            min_complexity = min(complexities)
        else:
            avg_complexity = 0.0
            max_complexity = 0
            min_complexity = 0
        
        metrics = ComplexityMetrics(
            avg_complexity=round(avg_complexity, 2),
            max_complexity=max_complexity,
            min_complexity=min_complexity,
            high_complexity_count=high_complexity_count,
            trivial_count=trivial_count,
            avg_nesting_depth=0.0,  # Would need AST nodes to calculate
            max_nesting_depth=0,
            total_decision_points=total_decision_points
        )
        
        logger.debug(
            f"Complexity analysis: avg={metrics.avg_complexity}, "
            f"max={metrics.max_complexity}, "
            f"high_complexity={high_complexity_count}, "
            f"trivial={trivial_count}"
        )
        
        return metrics
    
    def _count_decision_points(self, node: Any, decision_node_types: set) -> int:
        """
        Recursively count decision points in a node tree.
        
        Args:
            node: Node to analyze
            decision_node_types: Set of node types that count as decisions
        
        Returns:
            Number of decision points
        """
        count = 0
        
        # Check if this node is a decision point
        if node.type in decision_node_types:
            # For binary expressions, only count logical operators
            if node.type in ['binary_expression', 'boolean_operator', 'binary']:
                operator = self._get_operator(node)
                if operator in self.logical_operators:
                    count += 1
            else:
                count += 1
        
        # Recursively count in children
        for child in node.children:
            count += self._count_decision_points(child, decision_node_types)
        
        return count
    
    def _get_operator(self, node: Any) -> str:
        """
        Extract operator from a binary expression node.
        
        Args:
            node: Binary expression node
        
        Returns:
            Operator as string
        """
        for child in node.children:
            operator_text = child.text.decode('utf-8') if hasattr(child.text, 'decode') else str(child.text)
            if operator_text in self.logical_operators:
                return operator_text
        return ""
    
    def _calculate_depth_recursive(self, node: Any, current_depth: int) -> int:
        """
        Recursively calculate maximum nesting depth.
        
        Args:
            node: Current node
            current_depth: Current depth level
        
        Returns:
            Maximum depth found
        """
        max_depth = current_depth
        
        # Node types that increase nesting depth
        nesting_nodes = {
            'if_statement', 'elif_clause', 'else_clause',
            'for_statement', 'while_statement', 'do_statement',
            'switch_statement', 'case', 'case_clause',
            'try_statement', 'catch_clause', 'except_clause',
            'with_statement',
            'if_expression', 'for_expression', 'while_expression',
            'match_expression', 'match_arm'
        }
        
        # Increase depth if this is a nesting node
        if node.type in nesting_nodes:
            current_depth += 1
            max_depth = current_depth
        
        # Recursively check children
        for child in node.children:
            child_depth = self._calculate_depth_recursive(child, current_depth)
            max_depth = max(max_depth, child_depth)
        
        return max_depth
    
    def flag_high_complexity(self, complexity: int) -> bool:
        """
        Check if complexity is high (>10).
        
        Args:
            complexity: Complexity score
        
        Returns:
            True if high complexity
        """
        return complexity > 10
    
    def flag_trivial(self, complexity: int) -> bool:
        """
        Check if complexity is trivial (<2).
        
        Args:
            complexity: Complexity score
        
        Returns:
            True if trivial
        """
        return complexity < 2
