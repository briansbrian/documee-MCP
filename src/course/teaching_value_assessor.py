"""
Teaching value assessment for AI content enrichment.

This module implements a comprehensive scoring system (0-14 scale) to evaluate
whether code sections are worth teaching based on multiple criteria:
- Reusability (0-3): Is the pattern reusable across projects?
- Best Practice (0-3): Does it follow industry best practices?
- Fundamentality (0-3): Is it a fundamental concept?
- Uniqueness (0-2): Is it interesting or novel?
- Junior Dev Value (0-3): Is it valuable for junior developers?

Code with a total score > 7 is recommended for teaching.
"""

import logging
from typing import Dict, List, Any
from dataclasses import dataclass

from ..models.analysis_models import DetectedPattern, FileAnalysis
from .enrichment_models import (
    TeachingValueAssessment,
    FeatureMapping,
    EvidenceBundle
)

logger = logging.getLogger(__name__)


class TeachingValueAssessor:
    """
    Assesses teaching value of code sections for educational content.
    
    Implements a multi-criteria scoring system to determine if code
    is worth including in educational materials.
    """
    
    # Pattern types that indicate high reusability
    REUSABLE_PATTERNS = {
        'react_component', 'api_route', 'database_operation',
        'authentication', 'validation', 'error_handling',
        'caching', 'middleware', 'decorator', 'factory',
        'singleton', 'observer', 'strategy', 'adapter'
    }
    
    # Pattern types that represent best practices
    BEST_PRACTICE_PATTERNS = {
        'error_handling', 'validation', 'authentication',
        'authorization', 'logging', 'testing', 'documentation',
        'dependency_injection', 'separation_of_concerns'
    }
    
    # Fundamental concepts for learning
    FUNDAMENTAL_CONCEPTS = {
        'function', 'class', 'module', 'import', 'export',
        'async', 'promise', 'callback', 'event_handler',
        'data_structure', 'algorithm', 'api_route',
        'database_operation', 'file_io'
    }
    
    def __init__(self):
        """Initialize the teaching value assessor."""
        pass
    
    def assess_teaching_value(
        self,
        feature: FeatureMapping,
        evidence: EvidenceBundle,
        file_analysis: FileAnalysis
    ) -> TeachingValueAssessment:
        """
        Assess overall teaching value with comprehensive scoring.
        
        Args:
            feature: Feature mapping with user-facing context
            evidence: Evidence bundle with code, tests, docs
            file_analysis: File analysis with patterns and metrics
            
        Returns:
            TeachingValueAssessment with scores and reasoning
        """
        logger.info(f"Assessing teaching value for feature: {feature.feature_name}")
        
        # Calculate individual scores
        reusability = self.score_reusability(file_analysis.patterns)
        best_practice = self.score_best_practice(evidence)
        fundamentality = self.score_fundamentality(feature)
        uniqueness = self.score_uniqueness(file_analysis)
        junior_dev = self.score_junior_dev_value(feature, file_analysis)
        
        # Build scores dictionary
        scores = {
            'reusability': reusability,
            'best_practice': best_practice,
            'fundamentality': fundamentality,
            'uniqueness': uniqueness,
            'junior_dev': junior_dev
        }
        
        # Calculate total and recommendation
        total_score = sum(scores.values())
        should_teach = total_score > 7
        
        # Generate reasoning
        reasoning = self._generate_reasoning(scores, feature, file_analysis)
        
        logger.info(
            f"Teaching value assessment complete: "
            f"total={total_score}/14, should_teach={should_teach}"
        )
        
        return TeachingValueAssessment(
            scores=scores,
            total_score=total_score,
            should_teach=should_teach,
            reasoning=reasoning
        )
    
    def score_reusability(self, patterns: List[DetectedPattern]) -> int:
        """
        Score reusability based on detected patterns (0-3 points).
        
        Scoring criteria:
        - 3 points: Multiple highly reusable patterns (3+)
        - 2 points: Some reusable patterns (2)
        - 1 point: One reusable pattern
        - 0 points: No reusable patterns
        
        Args:
            patterns: List of detected patterns in the code
            
        Returns:
            Score from 0-3
        """
        if not patterns:
            return 0
        
        # Count reusable patterns
        reusable_count = sum(
            1 for p in patterns
            if p.pattern_type in self.REUSABLE_PATTERNS
        )
        
        if reusable_count >= 3:
            return 3
        elif reusable_count == 2:
            return 2
        elif reusable_count == 1:
            return 1
        else:
            return 0
    
    def score_best_practice(self, evidence: EvidenceBundle) -> int:
        """
        Score best practice adherence (0-3 points).
        
        Scoring criteria:
        - 3 points: Strong evidence of best practices (tests + docs + patterns)
        - 2 points: Good evidence (2 of 3: tests, docs, patterns)
        - 1 point: Some evidence (1 of 3)
        - 0 points: No evidence of best practices
        
        Args:
            evidence: Evidence bundle with tests, docs, and code
            
        Returns:
            Score from 0-3
        """
        evidence_count = 0
        
        # Check for test coverage
        if evidence.test_files and len(evidence.test_files) > 0:
            evidence_count += 1
        
        # Check for documentation
        if evidence.documentation and len(evidence.documentation) > 0:
            evidence_count += 1
        
        # Check for best practice patterns in source files
        has_best_practice_patterns = False
        for source_file in evidence.source_files:
            # Look for error handling, validation, etc. in code
            code = source_file.get('code', '')
            if any(keyword in code.lower() for keyword in [
                'try', 'except', 'catch', 'validate', 'assert',
                'raise', 'throw', 'error', 'logger', 'log'
            ]):
                has_best_practice_patterns = True
                break
        
        if has_best_practice_patterns:
            evidence_count += 1
        
        return min(evidence_count, 3)
    
    def score_fundamentality(self, feature: FeatureMapping) -> int:
        """
        Score fundamentality based on concept importance (0-3 points).
        
        Scoring criteria:
        - 3 points: Core fundamental concept (essential for all developers)
        - 2 points: Important concept (valuable for most developers)
        - 1 point: Useful concept (helpful but not essential)
        - 0 points: Niche or advanced concept
        
        Args:
            feature: Feature mapping with business context
            
        Returns:
            Score from 0-3
        """
        feature_name_lower = feature.feature_name.lower()
        purpose_lower = feature.user_facing_purpose.lower()
        
        # Check for fundamental keywords
        fundamental_keywords = [
            'crud', 'create', 'read', 'update', 'delete',
            'authentication', 'authorization', 'login', 'signup',
            'api', 'endpoint', 'route', 'handler',
            'database', 'query', 'model', 'schema',
            'validation', 'error handling', 'logging',
            'configuration', 'setup', 'initialization'
        ]
        
        important_keywords = [
            'search', 'filter', 'sort', 'pagination',
            'upload', 'download', 'export', 'import',
            'notification', 'email', 'cache', 'session'
        ]
        
        useful_keywords = [
            'analytics', 'reporting', 'dashboard',
            'integration', 'webhook', 'scheduler'
        ]
        
        # Check feature name and purpose
        text_to_check = f"{feature_name_lower} {purpose_lower}"
        
        if any(keyword in text_to_check for keyword in fundamental_keywords):
            return 3
        elif any(keyword in text_to_check for keyword in important_keywords):
            return 2
        elif any(keyword in text_to_check for keyword in useful_keywords):
            return 1
        else:
            return 0
    
    def score_uniqueness(self, file_analysis: FileAnalysis) -> int:
        """
        Score uniqueness based on interesting or novel aspects (0-2 points).
        
        Scoring criteria:
        - 2 points: Highly unique/interesting (novel patterns, creative solutions)
        - 1 point: Somewhat unique (interesting implementation details)
        - 0 points: Standard/common implementation
        
        Args:
            file_analysis: File analysis with patterns and complexity
            
        Returns:
            Score from 0-2
        """
        uniqueness_score = 0
        
        # Check for high complexity (might indicate interesting algorithms)
        if file_analysis.complexity_metrics.max_complexity > 10:
            uniqueness_score += 1
        
        # Check for multiple different pattern types (indicates versatility)
        unique_pattern_types = set(p.pattern_type for p in file_analysis.patterns)
        if len(unique_pattern_types) >= 3:
            uniqueness_score += 1
        
        # Check for high-confidence patterns (well-implemented)
        high_confidence_patterns = [
            p for p in file_analysis.patterns
            if p.confidence >= 0.8
        ]
        if len(high_confidence_patterns) >= 2:
            uniqueness_score = min(uniqueness_score + 1, 2)
        
        return min(uniqueness_score, 2)
    
    def score_junior_dev_value(
        self,
        feature: FeatureMapping,
        file_analysis: FileAnalysis
    ) -> int:
        """
        Score value for junior developers (0-3 points).
        
        Scoring criteria:
        - 3 points: Extremely valuable (common tasks, clear patterns, good docs)
        - 2 points: Very valuable (useful patterns, decent complexity)
        - 1 point: Somewhat valuable (might be too simple or too complex)
        - 0 points: Not suitable for juniors (too advanced or too trivial)
        
        Args:
            feature: Feature mapping with user context
            file_analysis: File analysis with complexity and patterns
            
        Returns:
            Score from 0-3
        """
        score = 0
        
        # Check complexity - moderate complexity is best for learning
        avg_complexity = file_analysis.complexity_metrics.avg_complexity
        if 2 <= avg_complexity <= 8:
            # Sweet spot for learning
            score += 2
        elif 1 <= avg_complexity < 2 or 8 < avg_complexity <= 12:
            # Still valuable but not ideal
            score += 1
        # Too simple (<1) or too complex (>12) gets 0 points
        
        # Check documentation coverage - well-documented code is better for learning
        if file_analysis.documentation_coverage >= 0.7:
            score += 1
        elif file_analysis.documentation_coverage >= 0.4:
            score += 0.5  # Will be rounded in total
        
        # Check for practical, real-world features
        practical_keywords = [
            'user', 'data', 'form', 'input', 'output',
            'save', 'load', 'process', 'handle', 'manage'
        ]
        
        feature_text = f"{feature.feature_name} {feature.user_facing_purpose}".lower()
        if any(keyword in feature_text for keyword in practical_keywords):
            score += 1
        
        return min(int(score), 3)
    
    def _generate_reasoning(
        self,
        scores: Dict[str, int],
        feature: FeatureMapping,
        file_analysis: FileAnalysis
    ) -> str:
        """
        Generate human-readable reasoning for the scores.
        
        Args:
            scores: Dictionary of individual scores
            feature: Feature mapping
            file_analysis: File analysis
            
        Returns:
            Explanation string
        """
        reasons = []
        
        # Reusability reasoning
        if scores['reusability'] >= 2:
            reasons.append(
                f"High reusability ({scores['reusability']}/3): "
                f"Contains {len(file_analysis.patterns)} reusable patterns"
            )
        elif scores['reusability'] == 1:
            reasons.append("Moderate reusability (1/3): Contains some reusable patterns")
        else:
            reasons.append("Low reusability (0/3): Few reusable patterns detected")
        
        # Best practice reasoning
        if scores['best_practice'] >= 2:
            reasons.append(
                f"Strong best practices ({scores['best_practice']}/3): "
                "Well-tested and documented"
            )
        elif scores['best_practice'] == 1:
            reasons.append("Some best practices (1/3): Partial coverage")
        else:
            reasons.append("Limited best practices (0/3): Needs improvement")
        
        # Fundamentality reasoning
        if scores['fundamentality'] >= 2:
            reasons.append(
                f"Fundamental concept ({scores['fundamentality']}/3): "
                f"'{feature.feature_name}' is important for developers"
            )
        elif scores['fundamentality'] == 1:
            reasons.append("Useful concept (1/3): Helpful but not essential")
        else:
            reasons.append("Niche concept (0/3): Advanced or specialized")
        
        # Uniqueness reasoning
        if scores['uniqueness'] >= 1:
            reasons.append(
                f"Interesting implementation ({scores['uniqueness']}/2): "
                "Contains unique or novel aspects"
            )
        else:
            reasons.append("Standard implementation (0/2): Common patterns")
        
        # Junior dev value reasoning
        if scores['junior_dev'] >= 2:
            reasons.append(
                f"High junior dev value ({scores['junior_dev']}/3): "
                f"Good complexity and documentation"
            )
        elif scores['junior_dev'] == 1:
            reasons.append("Moderate junior dev value (1/3): Some learning potential")
        else:
            reasons.append("Low junior dev value (0/3): Too simple or too complex")
        
        return "; ".join(reasons)
