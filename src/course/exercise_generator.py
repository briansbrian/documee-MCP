"""Exercise Generator - Creates coding exercises from patterns."""

import re
import uuid
from typing import List, Tuple
from src.models import DetectedPattern, FileAnalysis
from .models import Exercise, TestCase
from .config import CourseConfig


class ExerciseGenerator:
    """Generates coding exercises from detected patterns."""
    
    def __init__(self, config: CourseConfig):
        """Initialize the exercise generator.
        
        Args:
            config: Course generation configuration
        """
        self.config = config
    
    def generate_exercise(self, pattern: DetectedPattern, file_analysis: FileAnalysis) -> Exercise:
        """Generate a coding exercise from a detected pattern.
        
        Args:
            pattern: Detected pattern to create exercise from
            file_analysis: File analysis containing the pattern
            
        Returns:
            Exercise with starter code, solution, hints, and test cases
        """
        # Extract solution code from the pattern
        solution_code = self._extract_pattern_code(pattern, file_analysis)
        
        # Create starter code with TODOs
        starter_code = self._create_starter_code(solution_code, pattern.pattern_type)
        
        # Generate step-by-step instructions
        instructions = self._generate_instructions(pattern, file_analysis)
        
        # Generate hints
        hints = self._generate_hints(solution_code, pattern.pattern_type)
        
        # Generate test cases
        test_cases = self._generate_test_cases(pattern, solution_code)
        
        # Determine difficulty based on complexity
        difficulty = self._determine_difficulty(file_analysis)
        
        # Estimate time based on complexity
        estimated_minutes = self._estimate_time(difficulty, len(instructions))
        
        # Generate learning objectives
        learning_objectives = self._generate_learning_objectives(pattern)
        
        return Exercise(
            exercise_id=str(uuid.uuid4()),
            title=f"Practice: {self._format_pattern_name(pattern.pattern_type)}",
            description=f"Implement a {pattern.pattern_type} based on the example from {file_analysis.file_path}",
            difficulty=difficulty,
            estimated_minutes=estimated_minutes,
            instructions=instructions,
            starter_code=starter_code,
            solution_code=solution_code,
            hints=hints,
            test_cases=test_cases,
            learning_objectives=learning_objectives
        )
    
    def _extract_pattern_code(self, pattern: DetectedPattern, file_analysis: FileAnalysis) -> str:
        """Extract relevant code demonstrating the pattern.
        
        Args:
            pattern: Detected pattern
            file_analysis: File analysis containing the pattern
            
        Returns:
            Code snippet demonstrating the pattern
        """
        # Read the source file
        try:
            with open(file_analysis.file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # If pattern has line numbers, extract those lines
            if pattern.line_numbers:
                start_line = min(pattern.line_numbers) - 1  # 0-indexed
                end_line = max(pattern.line_numbers)
                
                # Expand to include context (up to 10 lines before/after)
                start_line = max(0, start_line - 2)
                end_line = min(len(lines), end_line + 2)
                
                code_lines = lines[start_line:end_line]
                return ''.join(code_lines).strip()
            
            # Otherwise, try to find relevant function or class
            for func in file_analysis.symbol_info.functions:
                if any(evidence in func.name.lower() for evidence in pattern.evidence):
                    func_lines = lines[func.start_line - 1:func.end_line]
                    return ''.join(func_lines).strip()
            
            for cls in file_analysis.symbol_info.classes:
                if any(evidence in cls.name.lower() for evidence in pattern.evidence):
                    cls_lines = lines[cls.start_line - 1:cls.end_line]
                    # Limit to 50 lines
                    if len(cls_lines) > 50:
                        cls_lines = cls_lines[:50]
                        cls_lines.append("    # ... (truncated for brevity)\n")
                    return ''.join(cls_lines).strip()
            
            # Fallback: return first 30 lines
            return ''.join(lines[:30]).strip()
            
        except Exception as e:
            # Fallback to a simple template
            return f"# Code example for {pattern.pattern_type}\n# (Unable to extract: {str(e)})"
    
    def _create_starter_code(self, solution_code: str, pattern_type: str) -> str:
        """Create starter code with TODO comments.
        
        Args:
            solution_code: Complete solution code
            pattern_type: Type of pattern
            
        Returns:
            Starter code with TODOs replacing implementation
        """
        lines = solution_code.split('\n')
        starter_lines = []
        in_function = False
        indent_level = 0
        
        for line in lines:
            stripped = line.lstrip()
            
            # Keep imports, class definitions, function signatures
            if (stripped.startswith('import ') or 
                stripped.startswith('from ') or
                stripped.startswith('class ') or
                stripped.startswith('def ') or
                stripped.startswith('async def ')):
                starter_lines.append(line)
                
                if stripped.startswith('def ') or stripped.startswith('async def '):
                    in_function = True
                    indent_level = len(line) - len(stripped) + 4
                continue
            
            # Keep docstrings
            if '"""' in stripped or "'''" in stripped:
                starter_lines.append(line)
                continue
            
            # Keep decorators
            if stripped.startswith('@'):
                starter_lines.append(line)
                continue
            
            # Replace function body with TODO
            if in_function and stripped and not stripped.startswith('#'):
                # Add TODO on first line of implementation
                todo_line = ' ' * indent_level + f"# TODO: Implement {pattern_type} logic here"
                starter_lines.append(todo_line)
                starter_lines.append(' ' * indent_level + "pass")
                in_function = False
            elif not stripped or stripped.startswith('#'):
                # Keep empty lines and comments
                starter_lines.append(line)
        
        return '\n'.join(starter_lines)
    
    def _generate_instructions(self, pattern: DetectedPattern, file_analysis: FileAnalysis) -> List[str]:
        """Generate step-by-step instructions for the exercise.
        
        Args:
            pattern: Detected pattern
            file_analysis: File analysis
            
        Returns:
            List of instruction steps
        """
        instructions = []
        pattern_type = pattern.pattern_type
        
        # Generic instructions based on pattern type
        if 'component' in pattern_type.lower():
            instructions.extend([
                "Create the component structure with proper imports",
                "Define the component's props and state",
                "Implement the component's render logic",
                "Add any necessary event handlers"
            ])
        elif 'api' in pattern_type.lower() or 'route' in pattern_type.lower():
            instructions.extend([
                "Define the API endpoint with proper HTTP method",
                "Implement request validation",
                "Add the main business logic",
                "Return appropriate response with status codes"
            ])
        elif 'class' in pattern_type.lower():
            instructions.extend([
                "Define the class with appropriate attributes",
                "Implement the constructor/initializer",
                "Add the required methods",
                "Ensure proper encapsulation"
            ])
        elif 'function' in pattern_type.lower():
            instructions.extend([
                "Define the function signature with parameters",
                "Add input validation if needed",
                "Implement the core logic",
                "Return the expected result"
            ])
        else:
            # Generic instructions
            instructions.extend([
                f"Implement the {pattern_type} following the pattern shown",
                "Ensure all required functionality is included",
                "Test your implementation with the provided test cases"
            ])
        
        # Add pattern-specific evidence as hints
        if pattern.evidence:
            instructions.append(f"Key concepts to include: {', '.join(pattern.evidence[:3])}")
        
        return instructions
    
    def _generate_hints(self, solution_code: str, pattern_type: str) -> List[str]:
        """Generate progressive hints for the exercise.
        
        Args:
            solution_code: Complete solution code
            pattern_type: Type of pattern
            
        Returns:
            List of hints with progressive revelation
        """
        hints = []
        
        # Hint 1: High-level approach
        hints.append(
            f"Start by understanding the structure of a {pattern_type}. "
            "Look at the imports and main components needed."
        )
        
        # Hint 2: Key implementation details
        lines = solution_code.split('\n')
        key_lines = [line for line in lines if 'def ' in line or 'class ' in line or 'return ' in line]
        if key_lines:
            hints.append(
                f"Key elements to implement: {len(key_lines)} main components. "
                "Focus on the function signatures and return values first."
            )
        
        # Hint 3: Specific guidance
        if 'import' in solution_code:
            imports = [line for line in lines if line.strip().startswith('import') or line.strip().startswith('from')]
            if imports:
                hints.append(f"You'll need these imports: {imports[0].strip()}")
        
        return hints
    
    def _generate_test_cases(self, pattern: DetectedPattern, solution_code: str) -> List[TestCase]:
        """Generate test cases for validating the exercise solution.
        
        Args:
            pattern: Detected pattern
            solution_code: Complete solution code
            
        Returns:
            List of test cases
        """
        test_cases = []
        pattern_type = pattern.pattern_type
        
        # Generate basic test cases based on pattern type
        if 'function' in pattern_type.lower():
            test_cases.append(TestCase(
                input="Basic input",
                expected_output="Expected output based on function logic",
                description="Test basic functionality"
            ))
            test_cases.append(TestCase(
                input="Edge case input",
                expected_output="Expected edge case output",
                description="Test edge case handling"
            ))
        elif 'class' in pattern_type.lower():
            test_cases.append(TestCase(
                input="Create instance with valid parameters",
                expected_output="Instance created successfully",
                description="Test class instantiation"
            ))
            test_cases.append(TestCase(
                input="Call main method",
                expected_output="Method returns expected result",
                description="Test main method functionality"
            ))
        elif 'api' in pattern_type.lower():
            test_cases.append(TestCase(
                input="Valid request payload",
                expected_output="200 OK with expected response",
                description="Test successful API call"
            ))
            test_cases.append(TestCase(
                input="Invalid request payload",
                expected_output="400 Bad Request",
                description="Test error handling"
            ))
        else:
            # Generic test case
            test_cases.append(TestCase(
                input="Sample input",
                expected_output="Expected output",
                description=f"Test {pattern_type} implementation"
            ))
        
        return test_cases
    
    def _determine_difficulty(self, file_analysis: FileAnalysis) -> str:
        """Determine exercise difficulty based on file complexity.
        
        Args:
            file_analysis: File analysis with complexity metrics
            
        Returns:
            Difficulty level: 'beginner', 'intermediate', or 'advanced'
        """
        avg_complexity = file_analysis.complexity_metrics.avg_complexity
        
        if avg_complexity < 5:
            return 'beginner'
        elif avg_complexity < 10:
            return 'intermediate'
        else:
            return 'advanced'
    
    def _estimate_time(self, difficulty: str, instruction_count: int) -> int:
        """Estimate time to complete exercise in minutes.
        
        Args:
            difficulty: Exercise difficulty level
            instruction_count: Number of instruction steps
            
        Returns:
            Estimated minutes to complete
        """
        base_time = {
            'beginner': 15,
            'intermediate': 25,
            'advanced': 40
        }
        
        time = base_time.get(difficulty, 20)
        # Add 5 minutes per instruction step
        time += instruction_count * 5
        
        return min(time, 60)  # Cap at 60 minutes
    
    def _generate_learning_objectives(self, pattern: DetectedPattern) -> List[str]:
        """Generate learning objectives for the exercise.
        
        Args:
            pattern: Detected pattern
            
        Returns:
            List of learning objectives
        """
        objectives = []
        pattern_type = pattern.pattern_type
        
        # Format pattern name for readability
        formatted_name = self._format_pattern_name(pattern_type)
        
        objectives.append(f"Understand how to implement a {formatted_name}")
        objectives.append(f"Practice writing clean, maintainable code for {formatted_name}")
        
        # Add objectives based on evidence
        if pattern.evidence:
            for evidence in pattern.evidence[:2]:
                objectives.append(f"Apply {evidence} in your implementation")
        
        return objectives
    
    def _format_pattern_name(self, pattern_type: str) -> str:
        """Format pattern type name for display.
        
        Args:
            pattern_type: Raw pattern type string
            
        Returns:
            Formatted, human-readable pattern name
        """
        # Convert snake_case or camelCase to Title Case
        formatted = re.sub(r'[_-]', ' ', pattern_type)
        formatted = re.sub(r'([a-z])([A-Z])', r'\1 \2', formatted)
        return formatted.title()
    
    def generate_exercises_for_lesson(
        self, 
        file_analysis: FileAnalysis, 
        max_exercises: int = 3
    ) -> List[Exercise]:
        """Generate 1-3 exercises for a lesson based on complexity.
        
        Args:
            file_analysis: File analysis to generate exercises from
            max_exercises: Maximum number of exercises to generate
            
        Returns:
            List of exercises (1-3 based on complexity)
        """
        exercises = []
        
        # Determine number of exercises based on complexity
        avg_complexity = file_analysis.complexity_metrics.avg_complexity
        if avg_complexity < 5:
            num_exercises = 1
        elif avg_complexity < 10:
            num_exercises = 2
        else:
            num_exercises = min(3, max_exercises)
        
        # Generate exercises from detected patterns
        patterns = file_analysis.patterns[:num_exercises]
        
        for pattern in patterns:
            try:
                exercise = self.generate_exercise(pattern, file_analysis)
                exercises.append(exercise)
            except Exception as e:
                # Log error but continue with other exercises
                print(f"Warning: Failed to generate exercise for pattern {pattern.pattern_type}: {e}")
                continue
        
        # If no patterns, create a generic exercise
        if not exercises and file_analysis.symbol_info.functions:
            # Create a generic pattern from the first function
            func = file_analysis.symbol_info.functions[0]
            generic_pattern = DetectedPattern(
                pattern_type="function_implementation",
                file_path=file_analysis.file_path,
                confidence=0.8,
                evidence=[func.name],
                line_numbers=list(range(func.start_line, func.end_line + 1)),
                metadata={"function_name": func.name}
            )
            try:
                exercise = self.generate_exercise(generic_pattern, file_analysis)
                exercises.append(exercise)
            except Exception as e:
                print(f"Warning: Failed to generate generic exercise: {e}")
        
        return exercises
