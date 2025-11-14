"""
Exercise Generator from Codebase.

This module generates exercises directly from actual codebase code,
creating starter code, solutions, hints, and test cases based on
real implementation and tests.
"""

import logging
import re
from typing import List, Dict, Any, Optional
from pathlib import Path

from src.course.enrichment_models import (
    FeatureMapping,
    EvidenceBundle,
    ExerciseGeneration
)

logger = logging.getLogger(__name__)


class ExerciseFromCodeGenerator:
    """
    Generates exercises from actual codebase code.
    
    Creates progressive exercises by extracting solution code from the
    codebase, simplifying it to starter code, extracting requirements
    from tests, and generating progressive hints.
    """
    
    def __init__(self):
        """Initialize the exercise generator."""
        logger.info("Initialized ExerciseFromCodeGenerator")
    
    def generate_exercises(
        self,
        feature: FeatureMapping,
        evidence: EvidenceBundle
    ) -> ExerciseGeneration:
        """
        Generate complete exercise from codebase evidence.
        
        Args:
            feature: Feature mapping with context
            evidence: Evidence bundle with source and test files
            
        Returns:
            ExerciseGeneration with all exercise components
        """
        logger.info(f"Generating exercises for feature: {feature.feature_name}")
        
        # Extract solution code from actual codebase
        solution_code = self.extract_solution_code(evidence)
        
        # Create starter code by removing implementation
        starter_code = self.create_starter_code(solution_code)
        
        # Extract requirements from tests
        requirements = self.extract_requirements_from_tests(evidence.test_files)
        
        # Generate progressive hints
        hints = self.generate_progressive_hints(solution_code, requirements)
        
        # Create assessment questions
        assessment = self.create_assessment_questions(feature, evidence)
        
        # Create hands-on tasks
        hands_on_tasks = self._create_hands_on_tasks(feature, requirements)
        
        # Format test cases
        test_cases = self._format_test_cases(evidence.test_files)
        
        return ExerciseGeneration(
            hands_on_tasks=hands_on_tasks,
            starter_code=starter_code,
            solution_code=solution_code,
            test_cases=test_cases,
            progressive_hints=hints,
            self_assessment=assessment
        )
    
    def extract_solution_code(self, evidence: EvidenceBundle) -> str:
        """
        Extract solution code from actual codebase.
        
        Identifies the core implementation from source files that
        represents the complete solution to the exercise.
        
        Args:
            evidence: Evidence bundle with source files
            
        Returns:
            Complete solution code as string
        """
        logger.info("Extracting solution code from evidence")
        
        if not evidence.source_files:
            logger.warning("No source files in evidence bundle")
            return "# No solution code available"
        
        # Use the first source file as primary solution
        primary_source = evidence.source_files[0]
        
        # Extract the most relevant section
        if primary_source.get('sections'):
            # Find the section with the most substantial code
            best_section = max(
                primary_source['sections'],
                key=lambda s: len(s.get('code', ''))
            )
            solution = best_section.get('code', '')
        else:
            solution = primary_source.get('code', '')
        
        # Clean up the solution code
        solution = self._clean_code(solution)
        
        logger.info(f"Extracted solution code: {len(solution)} characters")
        return solution
    
    def create_starter_code(self, solution: str) -> str:
        """
        Create starter code by removing implementation details.
        
        Transforms complete solution into a template that students
        can fill in, preserving structure but removing implementation.
        
        Args:
            solution: Complete solution code
            
        Returns:
            Starter code template as string
        """
        logger.info("Creating starter code from solution")
        
        if not solution or solution.strip() == "# No solution code available":
            return "# TODO: Implement the solution\npass"
        
        lines = solution.split('\n')
        starter_lines = []
        
        # Track indentation and structure
        in_function = False
        in_class = False
        function_indent = 0
        
        for line in lines:
            stripped = line.strip()
            indent = len(line) - len(line.lstrip())
            
            # Keep imports
            if stripped.startswith(('import ', 'from ')):
                starter_lines.append(line)
                continue
            
            # Keep class definitions
            if stripped.startswith('class '):
                starter_lines.append(line)
                in_class = True
                continue
            
            # Keep function/method definitions
            if stripped.startswith('def '):
                starter_lines.append(line)
                in_function = True
                function_indent = indent
                
                # Add docstring if present in next lines
                continue
            
            # Keep docstrings
            if stripped.startswith(('"""', "'''")):
                starter_lines.append(line)
                # Handle multi-line docstrings
                if not (stripped.endswith('"""') or stripped.endswith("'''")):
                    # Continue until closing quotes
                    continue
                continue
            
            # If we're in a function, replace implementation with TODO
            if in_function and indent > function_indent:
                # Skip implementation lines
                if stripped and not stripped.startswith('#'):
                    # Only add TODO once per function
                    if not any('TODO' in l for l in starter_lines[-3:]):
                        starter_lines.append(' ' * (function_indent + 4) + '# TODO: Implement this')
                        starter_lines.append(' ' * (function_indent + 4) + 'pass')
                continue
            
            # Reset function tracking when we exit
            if in_function and indent <= function_indent and stripped:
                in_function = False
            
            # Keep comments and blank lines for structure
            if not stripped or stripped.startswith('#'):
                starter_lines.append(line)
        
        starter_code = '\n'.join(starter_lines)
        
        # Clean up multiple consecutive blank lines
        starter_code = re.sub(r'\n\n\n+', '\n\n', starter_code)
        
        logger.info(f"Created starter code: {len(starter_code)} characters")
        return starter_code
    
    def extract_requirements_from_tests(
        self,
        tests: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Extract requirements from test files for exercise specifications.
        
        Analyzes test cases to determine what functionality needs to
        be implemented, creating clear requirements for students.
        
        Args:
            tests: List of test file dictionaries from evidence
            
        Returns:
            List of requirement strings
        """
        logger.info(f"Extracting requirements from {len(tests)} test file(s)")
        
        requirements = []
        
        for test_file in tests:
            test_cases = test_file.get('test_cases', [])
            
            for test_case in test_cases:
                description = test_case.get('description', '')
                name = test_case.get('name', '')
                
                # Convert test description to requirement
                requirement = self._test_to_requirement(description or name)
                
                if requirement and requirement not in requirements:
                    requirements.append(requirement)
        
        # If no test-based requirements, create generic ones
        if not requirements:
            requirements = [
                "Implement the core functionality",
                "Handle edge cases appropriately",
                "Return expected output format"
            ]
        
        logger.info(f"Extracted {len(requirements)} requirements")
        return requirements
    
    def _test_to_requirement(self, test_description: str) -> str:
        """
        Convert a test description to a requirement statement.
        
        Args:
            test_description: Test case description
            
        Returns:
            Requirement statement
        """
        # Clean up test name formatting
        desc = test_description.replace('_', ' ').strip()
        
        # Remove common test prefixes
        desc = re.sub(r'^test\s+', '', desc, flags=re.IGNORECASE)
        
        # Convert "should X" to "Must X"
        if 'should' in desc.lower():
            desc = desc.lower().replace('should', 'Must')
        
        # Capitalize first letter
        if desc:
            desc = desc[0].upper() + desc[1:]
        
        # Ensure it ends with proper punctuation
        if desc and not desc.endswith(('.', '!', '?')):
            desc += '.'
        
        return desc
    
    def generate_progressive_hints(
        self,
        solution: str,
        requirements: List[str]
    ) -> List[str]:
        """
        Generate 3-5 progressive hints (general → specific).
        
        Creates hints that guide students from high-level approach
        to specific implementation details without giving away
        the complete solution.
        
        Args:
            solution: Complete solution code
            requirements: List of requirements to fulfill
            
        Returns:
            List of 3-5 progressive hints
        """
        logger.info("Generating progressive hints")
        
        hints = []
        
        # Hint 1: High-level approach (most general)
        hints.append(self._generate_approach_hint(solution, requirements))
        
        # Hint 2: Key concepts or patterns
        hints.append(self._generate_concept_hint(solution))
        
        # Hint 3: Structure hint
        hints.append(self._generate_structure_hint(solution))
        
        # Hint 4: Implementation detail (if complex enough)
        if len(solution) > 200:  # Only for non-trivial solutions
            hints.append(self._generate_detail_hint(solution))
        
        # Hint 5: Edge case reminder (if applicable)
        if len(requirements) > 2:
            hints.append(self._generate_edge_case_hint(requirements))
        
        logger.info(f"Generated {len(hints)} progressive hints")
        return hints
    
    def _generate_approach_hint(
        self,
        solution: str,
        requirements: List[str]
    ) -> str:
        """Generate high-level approach hint."""
        # Analyze solution for key patterns
        has_loop = any(keyword in solution for keyword in ['for ', 'while '])
        has_condition = 'if ' in solution
        has_return = 'return ' in solution
        
        if has_loop and has_condition:
            return "Think about iterating through the data and checking conditions for each item."
        elif has_loop:
            return "Consider using a loop to process the data systematically."
        elif has_condition:
            return "Start by identifying the conditions that determine different behaviors."
        elif has_return:
            return "Focus on what the function needs to return and work backwards."
        else:
            return "Break down the problem into smaller steps and tackle each one."
    
    def _generate_concept_hint(self, solution: str) -> str:
        """Generate hint about key concepts or patterns."""
        # Detect common patterns
        if 'dict' in solution.lower() or '{' in solution and ':' in solution:
            return "A dictionary/object might be useful for storing key-value relationships."
        elif 'list' in solution.lower() or '[' in solution:
            return "Consider using a list/array to collect and organize your results."
        elif 'class ' in solution:
            return "Think about what data and methods belong together in a class."
        elif 'lambda' in solution or '=>' in solution:
            return "A simple function or lambda expression could make this more concise."
        elif 'try:' in solution or 'catch' in solution:
            return "Don't forget to handle potential errors that might occur."
        else:
            return "Look for patterns in the solution structure that repeat."
    
    def _generate_structure_hint(self, solution: str) -> str:
        """Generate hint about code structure."""
        # Count functions/methods
        func_count = solution.count('def ') + solution.count('function ')
        
        if func_count > 1:
            return f"You'll need about {func_count} functions to organize the logic properly."
        elif 'class ' in solution:
            methods = solution.count('def ') - 1  # Exclude __init__
            return f"Create a class with approximately {methods} methods to encapsulate the behavior."
        else:
            # Analyze complexity
            lines = [l for l in solution.split('\n') if l.strip() and not l.strip().startswith('#')]
            if len(lines) > 10:
                return "Break the implementation into logical sections with clear responsibilities."
            else:
                return "Keep the implementation simple and focused on the core logic."
    
    def _generate_detail_hint(self, solution: str) -> str:
        """Generate hint about specific implementation detail."""
        # Look for specific patterns
        if 're.' in solution or 'regex' in solution.lower():
            return "Regular expressions can help with pattern matching in strings."
        elif '.join(' in solution:
            return "String joining methods can efficiently combine multiple pieces."
        elif '.split(' in solution:
            return "Splitting strings into parts can make processing easier."
        elif '.append(' in solution or '.push(' in solution:
            return "Build up your result incrementally by adding items one at a time."
        elif 'enumerate' in solution:
            return "You might need both the index and value when iterating."
        elif '.get(' in solution:
            return "Safe dictionary access with .get() can prevent key errors."
        else:
            return "Pay attention to the order of operations in your implementation."
    
    def _generate_edge_case_hint(self, requirements: List[str]) -> str:
        """Generate hint about edge cases."""
        # Look for edge case keywords in requirements
        edge_keywords = ['empty', 'null', 'none', 'zero', 'negative', 'invalid']
        
        has_edge_cases = any(
            any(keyword in req.lower() for keyword in edge_keywords)
            for req in requirements
        )
        
        if has_edge_cases:
            return "Make sure to handle edge cases like empty inputs, null values, or boundary conditions."
        else:
            return "Test your solution with edge cases: empty inputs, single items, and large datasets."
    
    def create_assessment_questions(
        self,
        feature: FeatureMapping,
        evidence: EvidenceBundle
    ) -> List[str]:
        """
        Create self-assessment questions for checking understanding.
        
        Generates questions that help students verify they understand
        the concepts, not just the implementation.
        
        Args:
            feature: Feature mapping with context
            evidence: Evidence bundle with documentation
            
        Returns:
            List of self-assessment questions
        """
        logger.info(f"Creating assessment questions for {feature.feature_name}")
        
        questions = []
        
        # Question about purpose
        questions.append(
            f"What is the main purpose of {feature.feature_name} and "
            f"why is it important?"
        )
        
        # Question about implementation approach
        if evidence.source_files:
            primary_source = evidence.source_files[0]
            language = primary_source.get('language', 'this code')
            questions.append(
                f"What approach does this {language} implementation use "
                f"and why is it effective?"
            )
        
        # Question about edge cases
        if evidence.test_files:
            questions.append(
                "What edge cases does the implementation handle and why "
                "are they important?"
            )
        
        # Question about dependencies
        if evidence.dependencies:
            dep_names = [d.get('name', '') for d in evidence.dependencies[:3]]
            if dep_names:
                deps_str = ', '.join(dep_names)
                questions.append(
                    f"Why does this code depend on {deps_str} and what "
                    f"do they provide?"
                )
        
        # Question about real-world application
        questions.append(
            f"How would you apply the concepts from {feature.feature_name} "
            f"to a different problem?"
        )
        
        # Question about improvements
        questions.append(
            "What improvements or optimizations could be made to this "
            "implementation?"
        )
        
        logger.info(f"Created {len(questions)} assessment questions")
        return questions
    
    def _create_hands_on_tasks(
        self,
        feature: FeatureMapping,
        requirements: List[str]
    ) -> List[Dict[str, str]]:
        """
        Create hands-on task descriptions.
        
        Args:
            feature: Feature mapping
            requirements: List of requirements
            
        Returns:
            List of task dictionaries
        """
        tasks = []
        
        # Main implementation task
        tasks.append({
            'title': f"Implement {feature.feature_name}",
            'description': f"Complete the implementation of {feature.feature_name} "
                          f"following the requirements and passing all tests.",
            'difficulty': 'medium'
        })
        
        # Extension tasks based on requirements
        if len(requirements) > 3:
            tasks.append({
                'title': "Add Error Handling",
                'description': "Enhance the implementation with comprehensive error "
                              "handling for edge cases.",
                'difficulty': 'medium'
            })
        
        # Optimization task
        tasks.append({
            'title': "Optimize Performance",
            'description': "Analyze and improve the performance of your implementation "
                          "for large inputs.",
            'difficulty': 'hard'
        })
        
        return tasks
    
    def _format_test_cases(
        self,
        test_files: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Format test cases for exercise.
        
        Args:
            test_files: List of test file dictionaries
            
        Returns:
            Formatted test cases
        """
        formatted_tests = []
        
        for test_file in test_files:
            for test_case in test_file.get('test_cases', []):
                formatted_tests.append({
                    'name': test_case.get('name', ''),
                    'description': test_case.get('description', ''),
                    'file': test_file.get('path', ''),
                    'framework': test_file.get('framework', 'unknown')
                })
        
        return formatted_tests
    
    def _clean_code(self, code: str) -> str:
        """
        Clean up code by removing excessive whitespace.
        
        Args:
            code: Raw code string
            
        Returns:
            Cleaned code string
        """
        if not code:
            return ""
        
        # Remove trailing whitespace from each line
        lines = [line.rstrip() for line in code.split('\n')]
        
        # Remove excessive blank lines (max 2 consecutive)
        cleaned_lines = []
        blank_count = 0
        
        for line in lines:
            if not line.strip():
                blank_count += 1
                if blank_count <= 2:
                    cleaned_lines.append(line)
            else:
                blank_count = 0
                cleaned_lines.append(line)
        
        # Remove leading/trailing blank lines
        while cleaned_lines and not cleaned_lines[0].strip():
            cleaned_lines.pop(0)
        while cleaned_lines and not cleaned_lines[-1].strip():
            cleaned_lines.pop()
        
        return '\n'.join(cleaned_lines)


def create_exercise_generator() -> ExerciseFromCodeGenerator:
    """
    Factory function to create an ExerciseFromCodeGenerator instance.
    
    Returns:
        ExerciseFromCodeGenerator instance
    """
    return ExerciseFromCodeGenerator()
