"""
Narrative Structure Builder for AI Content Enrichment.

This module builds structured narratives for lessons by organizing content
into introduction, learning progression, code walkthrough order, conclusion,
and next steps - all designed to create coherent, beginner-friendly learning flows.
"""

import logging
from typing import List, Dict, Any, Optional

from src.course.enrichment_models import (
    NarrativeStructure,
    SystematicInvestigation,
    TeachingValueAssessment,
    CodeSectionGuide
)

logger = logging.getLogger(__name__)


class NarrativeBuilder:
    """
    Builds narrative structures for lessons to guide content creation.
    
    Creates learning flows that progress from simple to complex concepts,
    with clear introductions, structured walkthroughs, and actionable next steps.
    """
    
    def __init__(self):
        """Initialize the narrative builder."""
        logger.info("Initialized NarrativeBuilder")
    
    def build_narrative(
        self,
        investigation: SystematicInvestigation,
        teaching_value: TeachingValueAssessment,
        code_sections: List[CodeSectionGuide],
        lesson_context: Optional[Dict[str, Any]] = None,
        course_outline: Optional[Dict[str, Any]] = None
    ) -> NarrativeStructure:
        """
        Build complete narrative structure for a lesson.
        
        Args:
            investigation: Systematic investigation results
            teaching_value: Teaching value assessment
            code_sections: List of code section guides
            lesson_context: Optional lesson metadata (title, topic, etc.)
            course_outline: Optional course outline for progression context
            
        Returns:
            NarrativeStructure with all narrative components
        """
        logger.info("Building narrative structure")
        
        # Build introduction points
        introduction_points = self.build_introduction_points(
            investigation,
            teaching_value,
            lesson_context
        )
        
        # Build learning progression
        concepts = self._extract_concepts_from_sections(code_sections)
        learning_progression = self.build_learning_progression(concepts)
        
        # Build code walkthrough order
        code_walkthrough_order = self.build_code_walkthrough_order(code_sections)
        
        # Build conclusion points
        conclusion_points = self.build_conclusion_points(
            investigation,
            teaching_value
        )
        
        # Suggest next steps
        next_steps = self.suggest_next_steps(
            lesson_context,
            course_outline,
            teaching_value
        )
        
        narrative = NarrativeStructure(
            introduction_points=introduction_points,
            learning_progression=learning_progression,
            code_walkthrough_order=code_walkthrough_order,
            conclusion_points=conclusion_points,
            next_steps=next_steps
        )
        
        logger.info("Completed narrative structure building")
        
        return narrative

    
    def build_introduction_points(
        self,
        investigation: SystematicInvestigation,
        teaching_value: TeachingValueAssessment,
        lesson_context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Build introduction points that provide context and motivation.
        
        Creates 3-5 introduction points that:
        - Set the context for what will be learned
        - Explain why this topic matters
        - Motivate the learner with practical value
        - Preview key concepts
        
        Args:
            investigation: Systematic investigation with what/why/how
            teaching_value: Teaching value assessment with reasoning
            lesson_context: Optional lesson metadata
            
        Returns:
            List of introduction points (3-5 items)
        """
        logger.debug("Building introduction points")
        
        intro_points = []
        
        # Point 1: What this lesson covers (from investigation)
        what_summary = self._summarize_what_it_does(investigation.what_it_does)
        if what_summary:
            intro_points.append(f"This lesson covers {what_summary}")
        
        # Point 2: Why it matters (from investigation and teaching value)
        why_summary = self._summarize_why_it_exists(investigation.why_it_exists)
        if why_summary:
            intro_points.append(f"Understanding this is important because {why_summary}")
        
        # Point 3: Practical value (from teaching value reasoning)
        if teaching_value.should_teach and teaching_value.reasoning:
            practical_value = self._extract_practical_value(teaching_value.reasoning)
            if practical_value:
                intro_points.append(practical_value)
        
        # Point 4: Key concepts preview (from investigation)
        if investigation.how_it_works:
            concepts_preview = self._preview_key_concepts(investigation.how_it_works)
            if concepts_preview:
                intro_points.append(f"You'll learn {concepts_preview}")
        
        # Point 5: Prerequisites or context (if available)
        if lesson_context and lesson_context.get('prerequisites'):
            prereqs = lesson_context['prerequisites']
            if prereqs:
                prereq_str = ", ".join(prereqs[:3])
                intro_points.append(f"This builds on your knowledge of {prereq_str}")
        
        # Ensure we have at least 3 points
        if len(intro_points) < 3:
            # Add generic motivational point
            intro_points.append("This is a fundamental concept that you'll use frequently in real-world development")
        
        logger.debug(f"Generated {len(intro_points)} introduction points")
        
        return intro_points[:5]  # Return max 5 points
    
    def build_learning_progression(self, concepts: List[str]) -> List[str]:
        """
        Build learning progression ordered from simple to complex.
        
        Organizes concepts in a logical learning order:
        1. Foundational concepts first
        2. Building blocks before compositions
        3. Simple patterns before advanced techniques
        4. Concrete examples before abstractions
        
        Args:
            concepts: List of concepts to order
            
        Returns:
            Ordered list of concepts (simple → complex)
        """
        logger.debug(f"Building learning progression from {len(concepts)} concepts")
        
        if not concepts:
            return ["Understanding the basic functionality", "Exploring the implementation", "Applying the concepts"]
        
        # Categorize concepts by complexity
        foundational = []
        intermediate = []
        advanced = []
        
        for concept in concepts:
            complexity = self._assess_concept_complexity(concept)
            
            if complexity == 'foundational':
                foundational.append(concept)
            elif complexity == 'advanced':
                advanced.append(concept)
            else:
                intermediate.append(concept)
        
        # Build progression: foundational → intermediate → advanced
        progression = []
        
        # Add foundational concepts
        progression.extend(foundational)
        
        # Add intermediate concepts
        progression.extend(intermediate)
        
        # Add advanced concepts
        progression.extend(advanced)
        
        logger.debug(f"Created progression with {len(progression)} ordered concepts")
        
        return progression
    
    def build_code_walkthrough_order(
        self,
        code_sections: List[CodeSectionGuide]
    ) -> List[str]:
        """
        Build code walkthrough order for explanation flow.
        
        Determines the optimal order to explain code sections:
        1. Entry points first (where execution starts)
        2. Dependencies before dependents
        3. Simple sections before complex ones
        4. Core logic before edge cases
        
        Args:
            code_sections: List of code section guides
            
        Returns:
            Ordered list of code section references
        """
        logger.debug(f"Building code walkthrough order for {len(code_sections)} sections")
        
        if not code_sections:
            return []
        
        # Score each section for walkthrough priority
        scored_sections = []
        
        for section in code_sections:
            score = self._calculate_walkthrough_priority(section)
            scored_sections.append((score, section))
        
        # Sort by priority (higher score = explain first)
        scored_sections.sort(key=lambda x: x[0], reverse=True)
        
        # Build walkthrough order with descriptions
        walkthrough_order = []
        
        for score, section in scored_sections:
            # Create reference with context
            file_name = section.file_path.split('/')[-1]
            line_ref = f"{section.line_range[0]}-{section.line_range[1]}"
            
            # Add purpose for context
            purpose_summary = self._summarize_purpose(section.purpose)
            
            reference = f"{file_name}:{line_ref} - {purpose_summary}"
            walkthrough_order.append(reference)
        
        logger.debug(f"Created walkthrough order with {len(walkthrough_order)} sections")
        
        return walkthrough_order
    
    def build_conclusion_points(
        self,
        investigation: SystematicInvestigation,
        teaching_value: TeachingValueAssessment
    ) -> List[str]:
        """
        Build conclusion points for key takeaways.
        
        Creates 3-5 conclusion points that:
        - Reinforce the most important concepts
        - Highlight best practices
        - Warn about common pitfalls
        - Connect to broader patterns
        
        Args:
            investigation: Systematic investigation results
            teaching_value: Teaching value assessment
            
        Returns:
            List of conclusion points (3-5 items)
        """
        logger.debug("Building conclusion points")
        
        conclusion_points = []
        
        # Point 1: Core takeaway (what was learned)
        core_takeaway = self._extract_core_takeaway(investigation.what_it_does)
        if core_takeaway:
            conclusion_points.append(core_takeaway)
        
        # Point 2: Best practice (from teaching value)
        if teaching_value.scores.get('best_practice', 0) >= 2:
            best_practice = self._extract_best_practice(investigation.how_it_works)
            if best_practice:
                conclusion_points.append(best_practice)
        
        # Point 3: Common pitfall warning (from investigation)
        if investigation.common_pitfalls:
            # Get the most important pitfall
            top_pitfall = investigation.common_pitfalls[0]
            pitfall_warning = self._format_pitfall_warning(top_pitfall)
            conclusion_points.append(pitfall_warning)
        
        # Point 4: Reusability insight (if highly reusable)
        if teaching_value.scores.get('reusability', 0) >= 2:
            reusability_insight = self._extract_reusability_insight(teaching_value.reasoning)
            if reusability_insight:
                conclusion_points.append(reusability_insight)
        
        # Point 5: Connection to broader patterns
        broader_connection = self._connect_to_broader_patterns(investigation.how_it_works)
        if broader_connection:
            conclusion_points.append(broader_connection)
        
        # Ensure we have at least 3 points
        if len(conclusion_points) < 3:
            conclusion_points.append("This pattern is widely used in professional development")
        
        logger.debug(f"Generated {len(conclusion_points)} conclusion points")
        
        return conclusion_points[:5]  # Return max 5 points
    
    def suggest_next_steps(
        self,
        lesson_context: Optional[Dict[str, Any]],
        course_outline: Optional[Dict[str, Any]],
        teaching_value: TeachingValueAssessment
    ) -> List[str]:
        """
        Suggest next steps for lesson progression.
        
        Provides 3-5 suggestions for what to learn next:
        - Next lesson in the course (if available)
        - Related advanced topics
        - Practical exercises to try
        - Real-world applications to explore
        
        Args:
            lesson_context: Optional lesson metadata
            course_outline: Optional course outline
            teaching_value: Teaching value assessment
            
        Returns:
            List of next step suggestions (3-5 items)
        """
        logger.debug("Suggesting next steps")
        
        next_steps = []
        
        # Step 1: Next lesson in course (if available)
        if course_outline and lesson_context:
            next_lesson = self._find_next_lesson(lesson_context, course_outline)
            if next_lesson:
                next_steps.append(f"Continue to the next lesson: {next_lesson}")
        
        # Step 2: Practice suggestion
        next_steps.append("Practice by implementing this pattern in your own project")
        
        # Step 3: Advanced topic (if fundamentality is high)
        if teaching_value.scores.get('fundamentality', 0) >= 2:
            advanced_topic = self._suggest_advanced_topic(lesson_context)
            if advanced_topic:
                next_steps.append(f"Explore advanced concepts: {advanced_topic}")
        
        # Step 4: Real-world application
        next_steps.append("Look for examples of this pattern in open-source projects")
        
        # Step 5: Related concepts
        if lesson_context and lesson_context.get('related_topics'):
            related = lesson_context['related_topics']
            if related:
                related_str = ", ".join(related[:2])
                next_steps.append(f"Study related concepts: {related_str}")
        
        # Ensure we have at least 3 steps
        if len(next_steps) < 3:
            next_steps.append("Review the code examples and experiment with variations")
        
        logger.debug(f"Generated {len(next_steps)} next steps")
        
        return next_steps[:5]  # Return max 5 steps
    
    # Helper methods
    
    def _extract_concepts_from_sections(
        self,
        code_sections: List[CodeSectionGuide]
    ) -> List[str]:
        """
        Extract all concepts from code sections.
        
        Args:
            code_sections: List of code section guides
            
        Returns:
            List of unique concepts
        """
        concepts = []
        
        for section in code_sections:
            concepts.extend(section.key_concepts)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_concepts = []
        for concept in concepts:
            if concept.lower() not in seen:
                seen.add(concept.lower())
                unique_concepts.append(concept)
        
        return unique_concepts
    
    def _summarize_what_it_does(self, what_it_does: str) -> str:
        """
        Summarize what the code does for introduction.
        
        Args:
            what_it_does: Full description from investigation
            
        Returns:
            Concise summary
        """
        if not what_it_does:
            return "the core functionality"
        
        # Take first sentence or first 100 chars
        sentences = what_it_does.split('.')
        if sentences:
            summary = sentences[0].strip()
            # Remove citation markers
            summary = summary.split('[')[0].strip()
            return summary.lower()
        
        return what_it_does[:100].lower()
    
    def _summarize_why_it_exists(self, why_it_exists: str) -> str:
        """
        Summarize why the code exists for introduction.
        
        Args:
            why_it_exists: Full explanation from investigation
            
        Returns:
            Concise summary
        """
        if not why_it_exists:
            return "it solves a common development challenge"
        
        # Extract the core reason
        if "exists to:" in why_it_exists.lower():
            reason = why_it_exists.split("exists to:")[-1].strip()
            # Take first part before semicolon
            reason = reason.split(';')[0].strip()
            # Remove citation markers
            reason = reason.split('[')[0].strip()
            return reason.lower()
        
        # Take first sentence
        sentences = why_it_exists.split('.')
        if sentences:
            summary = sentences[0].strip()
            summary = summary.split('[')[0].strip()
            return summary.lower()
        
        return why_it_exists[:100].lower()
    
    def _extract_practical_value(self, reasoning: str) -> Optional[str]:
        """
        Extract practical value from teaching value reasoning.
        
        Args:
            reasoning: Teaching value reasoning
            
        Returns:
            Practical value statement or None
        """
        if not reasoning:
            return None
        
        # Look for value-related keywords
        value_keywords = ['useful', 'important', 'valuable', 'helps', 'enables', 'allows']
        
        sentences = reasoning.split('.')
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in value_keywords):
                return sentence.strip()
        
        # Default practical value
        return "This pattern will help you write more maintainable and professional code"
    
    def _preview_key_concepts(self, how_it_works: str) -> Optional[str]:
        """
        Preview key concepts from implementation description.
        
        Args:
            how_it_works: Implementation description
            
        Returns:
            Concepts preview or None
        """
        if not how_it_works:
            return None
        
        # Extract key phrases
        if "uses" in how_it_works.lower():
            # Extract what it uses
            parts = how_it_works.lower().split("uses")
            if len(parts) > 1:
                concepts = parts[1].split(',')[0].strip()
                concepts = concepts.split('[')[0].strip()
                return f"how to use {concepts}"
        
        # Default preview
        return "the implementation patterns and best practices"
    
    def _assess_concept_complexity(self, concept: str) -> str:
        """
        Assess the complexity level of a concept.
        
        Args:
            concept: Concept description
            
        Returns:
            Complexity level: 'foundational', 'intermediate', or 'advanced'
        """
        concept_lower = concept.lower()
        
        # Foundational indicators
        foundational_keywords = [
            'basic', 'simple', 'introduction', 'fundamental',
            'definition', 'syntax', 'structure', 'variable',
            'function', 'class', 'import', 'export'
        ]
        
        # Advanced indicators
        advanced_keywords = [
            'advanced', 'complex', 'optimization', 'performance',
            'async', 'concurrent', 'distributed', 'architecture',
            'pattern', 'design', 'algorithm', 'security'
        ]
        
        # Check for foundational
        if any(keyword in concept_lower for keyword in foundational_keywords):
            return 'foundational'
        
        # Check for advanced
        if any(keyword in concept_lower for keyword in advanced_keywords):
            return 'advanced'
        
        # Default to intermediate
        return 'intermediate'
    
    def _calculate_walkthrough_priority(self, section: CodeSectionGuide) -> int:
        """
        Calculate priority score for code walkthrough order.
        
        Higher score = explain first
        
        Args:
            section: Code section guide
            
        Returns:
            Priority score (0-100)
        """
        score = 50  # Base score
        
        # Entry points get higher priority
        if 'entry' in section.purpose.lower() or 'main' in section.purpose.lower():
            score += 30
        
        # Simple concepts first
        if any(keyword in section.purpose.lower() for keyword in ['basic', 'simple', 'define']):
            score += 20
        
        # Core functionality before edge cases
        if 'edge' in section.purpose.lower() or 'special' in section.purpose.lower():
            score -= 20
        
        # Fewer dependencies = explain first
        if len(section.related_code) == 0:
            score += 15
        elif len(section.related_code) > 3:
            score -= 10
        
        # Well-tested code is more important
        if len(section.test_evidence) > 2:
            score += 10
        
        return score
    
    def _summarize_purpose(self, purpose: str) -> str:
        """
        Summarize section purpose for walkthrough reference.
        
        Args:
            purpose: Full purpose description
            
        Returns:
            Concise summary
        """
        if not purpose:
            return "code section"
        
        # Remove citations
        summary = purpose.split('[')[0].strip()
        
        # Take first 50 chars
        if len(summary) > 50:
            summary = summary[:47] + "..."
        
        return summary
    
    def _extract_core_takeaway(self, what_it_does: str) -> str:
        """
        Extract core takeaway for conclusion.
        
        Args:
            what_it_does: What the code does
            
        Returns:
            Core takeaway statement
        """
        if not what_it_does:
            return "You've learned a fundamental programming pattern"
        
        # Extract main functionality
        summary = self._summarize_what_it_does(what_it_does)
        
        return f"You now understand how to {summary}"
    
    def _extract_best_practice(self, how_it_works: str) -> Optional[str]:
        """
        Extract best practice from implementation.
        
        Args:
            how_it_works: Implementation description
            
        Returns:
            Best practice statement or None
        """
        if not how_it_works:
            return None
        
        # Look for best practice indicators
        best_practice_keywords = ['error handling', 'validation', 'async', 'cache', 'security']
        
        for keyword in best_practice_keywords:
            if keyword in how_it_works.lower():
                return f"Always implement {keyword} in production code"
        
        return "Follow the patterns demonstrated here in your own implementations"
    
    def _format_pitfall_warning(self, pitfall: str) -> str:
        """
        Format pitfall as a warning for conclusion.
        
        Args:
            pitfall: Pitfall description
            
        Returns:
            Formatted warning
        """
        # Remove citations
        warning = pitfall.split('[')[0].strip()
        
        # Ensure it starts with a warning phrase
        if not any(warning.lower().startswith(phrase) for phrase in ['avoid', 'don\'t', 'never', 'be careful']):
            warning = f"Avoid: {warning}"
        
        return warning
    
    def _extract_reusability_insight(self, reasoning: str) -> Optional[str]:
        """
        Extract reusability insight from teaching value reasoning.
        
        Args:
            reasoning: Teaching value reasoning
            
        Returns:
            Reusability insight or None
        """
        if not reasoning:
            return None
        
        # Look for reusability mentions
        if 'reusab' in reasoning.lower():
            sentences = reasoning.split('.')
            for sentence in sentences:
                if 'reusab' in sentence.lower():
                    return sentence.strip()
        
        return "This pattern is reusable across many different scenarios"
    
    def _connect_to_broader_patterns(self, how_it_works: str) -> Optional[str]:
        """
        Connect to broader programming patterns.
        
        Args:
            how_it_works: Implementation description
            
        Returns:
            Connection statement or None
        """
        if not how_it_works:
            return None
        
        # Identify patterns
        pattern_keywords = {
            'async': 'asynchronous programming patterns',
            'class': 'object-oriented design principles',
            'functional': 'functional programming concepts',
            'decorator': 'decorator pattern and metaprogramming',
            'cache': 'caching strategies and optimization',
            'validate': 'input validation and data integrity'
        }
        
        for keyword, pattern in pattern_keywords.items():
            if keyword in how_it_works.lower():
                return f"This demonstrates {pattern} used throughout professional development"
        
        return None
    
    def _find_next_lesson(
        self,
        lesson_context: Dict[str, Any],
        course_outline: Dict[str, Any]
    ) -> Optional[str]:
        """
        Find the next lesson in the course.
        
        Args:
            lesson_context: Current lesson metadata
            course_outline: Course outline structure
            
        Returns:
            Next lesson title or None
        """
        # This is a placeholder - actual implementation would depend on course structure
        # For now, return None to indicate no next lesson found
        return None
    
    def _suggest_advanced_topic(
        self,
        lesson_context: Optional[Dict[str, Any]]
    ) -> Optional[str]:
        """
        Suggest an advanced topic related to the lesson.
        
        Args:
            lesson_context: Lesson metadata
            
        Returns:
            Advanced topic suggestion or None
        """
        if not lesson_context:
            return None
        
        # Generic advanced topics based on common patterns
        advanced_topics = {
            'async': 'concurrent programming and parallelism',
            'class': 'design patterns and SOLID principles',
            'api': 'API design and RESTful architecture',
            'database': 'database optimization and indexing strategies',
            'test': 'test-driven development and testing strategies',
            'security': 'security best practices and threat modeling'
        }
        
        # Check lesson title or topic for keywords
        title = lesson_context.get('title', '').lower()
        topic = lesson_context.get('topic', '').lower()
        
        for keyword, advanced_topic in advanced_topics.items():
            if keyword in title or keyword in topic:
                return advanced_topic
        
        return None


def create_narrative_builder() -> NarrativeBuilder:
    """
    Factory function to create a NarrativeBuilder instance.
    
    Returns:
        NarrativeBuilder instance
    """
    return NarrativeBuilder()
