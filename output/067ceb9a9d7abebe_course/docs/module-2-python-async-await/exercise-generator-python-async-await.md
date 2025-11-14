# Exercise Generator: Python Async Await

**Difficulty**: beginner | **Duration**: 48 minutes

## Learning Objectives

- Understand python context managers pattern
- Understand python async await pattern
- Understand python comprehensions pattern
- Learn documentation best practices


## Introduction

Excellent teaching value (score: 0.84). Well-documented (100% coverage). Ideal complexity (avg: 4.8) for teaching. Contains useful patterns. Well-structured code.

You'll learn about Python Context Managers, Python Async Await, Python Comprehensions through hands-on code analysis.

By the end of this lesson, you'll be able to:
- Apply python async await pattern- Understand python comprehensions pattern- Understand python context managers pattern- Implement ExerciseGenerator class structure- Understand documentation best practices

## Explanation

## Understanding the Code

Let's break down this code step by step.

### Purpose

The `ExerciseGenerator` class generates coding exercises from detected patterns.


## Key Patterns

### Python Context Managers

This code demonstrates the python context managers pattern. Evidence includes: Uses context managers (2 with statements), File handling with context managers. This has some elements of this pattern.

### Python Async Await

This code demonstrates the python async await pattern. Evidence includes: Async functions: 2, Await statements: 4. This shows characteristics of this pattern.

### Python Comprehensions

This code demonstrates the python comprehensions pattern. Evidence includes: Uses comprehensions (4 occurrences). This has some elements of this pattern.



## Code Example

```python
"""Exercise Generator - Creates coding exercises from patterns."""

import re
import uuid
from typing import List, Tuple
from src.models import DetectedPattern, FileAnalysis
from .models import Exercise, TestCase
from .config import CourseConfig
from .performance_monitor import get_monitor


class ExerciseGenerator:
    """Generates coding exercises from detected patterns."""
    
    def __init__(self, config: CourseConfig, course_cache=None):
        """Initialize the exercise generator.
        
        Args:
            config: Course generation configuration
            course_cache: Optional CourseCacheManager for caching
        """
        self.config = config
        self.course_cache = course_cache
    
    async def generate_exercise(self, pattern: DetectedPattern, file_analysis: FileAnalysis) -> Exercise:
        """Generate a coding exercise from a detected pattern.
        
        Args:
            pattern: Detected pattern to create exercise from
            file_analysis: File analysis containing the pattern
            
        Returns:
            Exercise with starter code, solution, hints, and test cases
        """
        monitor = get_monitor()
        
        with monitor.measure("exercise_generation", pattern_type=pattern.pattern_type):
            # Check cache first
            if self.course_cache:
                cached = await self.course_cache.get_exercise(
                    file_analysis.file_path,
                    pattern.pattern_type
                )
                if cached and "data" in cached:
                    import logging
                    logging.getLogger(__name__).info(
                        f"Using cached exercise for {file_analysis.file_path}:{pattern.pattern_type}"
                    )
                    return self._deserialize_exercise(cached["data"])
            

# ... (498 more lines)
```

### Code Annotations

**Line 12**: Class definition: Generates coding exercises from detected patterns.
**Line 37**: Python Context Managers pattern starts here
**Line 25**: Python Async Await pattern starts here
**Line 279**: Python Comprehensions pattern starts here

## Walkthrough

## Code Walkthrough

Let's walk through the code step by step:

### ExerciseGenerator Class

Generates coding exercises from detected patterns.

**Key Methods:**

- `__init__(self, config, course_cache)`: Initialize the exercise generator.
- `generate_exercise(self, pattern, file_analysis)`: Generate a coding exercise from a detected pattern.
- `_extract_pattern_code(self, pattern, file_analysis)`: Extract relevant code demonstrating the pattern.
- `_create_starter_code(self, solution_code, pattern_type)`: Create starter code with TODO comments.
- `_generate_instructions(self, pattern, file_analysis)`: Generate step-by-step instructions for the exercise.

### Important Code Sections

**Line 12**: Class definition: Generates coding exercises from detected patterns.

**Line 25**: Python Async Await pattern starts here

**Line 37**: Python Context Managers pattern starts here

**Line 279**: Python Comprehensions pattern starts here



## Summary

## Summary

In this lesson, you learned:

- Apply python async await pattern
- Understand python comprehensions pattern
- Understand python context managers pattern
- Implement ExerciseGenerator class structure
- Understand documentation best practices

### Key Takeaways

- Understanding python context managers and python async await will help you write better code
- Good documentation makes code easier to understand and maintain
- Practice implementing these concepts in your own projects

### Next Steps

Try modifying the code to experiment with different approaches. Complete the exercises to reinforce your understanding.


## Further Reading

- Documentation Best Practices

## Exercises

### Practice: Python Async Await

Implement a python_async_await based on the example from C:\Users\brian\OneDrive\Documents\Apps\Documee_mcp\src\course\exercise_generator.py

**Difficulty**: beginner | **Estimated Time**: 35 minutes

#### Instructions

1. Implement the python_async_await following the pattern shown
2. Ensure all required functionality is included
3. Test your implementation with the provided test cases
4. Key concepts to include: Async functions: 2, Await statements: 4

#### Starter Code

```python
    
    async def generate_exercise(self, pattern: DetectedPattern, file_analysis: FileAnalysis) -> Exercise:
        """Generate a coding exercise from a detected pattern.
        
        # TODO: Implement python_async_await logic here
        pass
            
        """
        
            # Check cache first
                    import logging
            
            # Extract solution code from the pattern
        
        # Create starter code with TODOs
        
        # Generate step-by-step instructions
        
        # Generate hints
        
        # Generate test cases
        
        # Determine difficulty based on complexity
        
        # Estimate time based on complexity
        
        # Generate learning objectives
        
        
        # Cache the result
        
    
    def _extract_pattern_code(self, pattern: DetectedPattern, file_analysis: FileAnalysis) -> str:
        """Extract relevant code demonstrating the pattern.
        
        # TODO: Implement python_async_await logic here
        pass
            
        """
        # Read the source file
            
            # If pattern has line numbers, extract those lines
                
                # Expand to include context (up to 10 lines before/after)
                
            
            # Otherwise, try to find relevant function or class
            
                    # Limit to 50 lines
            
            # Fallback: return first 30 lines
            
            # Fallback to a simple template
    
    def _create_starter_code(self, solution_code: str, pattern_type: str) -> str:
        """Create starter code with TODO comments.
        
        # TODO: Implement python_async_await logic here
        pass
            
        """
        
            
            # Keep imports, class definitions, function signatures
                
            
            # Keep docstrings
            if '"""' in stripped or "'''" in stripped:
            
            # Keep decorators
            
            # Replace function body with TODO
                # Add TODO on first line of implementation
                # Keep empty lines and comments
        
    
    def _generate_instructions(self, pattern: DetectedPattern, file_analysis: FileAnalysis) -> List[str]:
        """Generate step-by-step instructions for the exercise.
        
        # TODO: Implement python_async_await logic here
        pass
            
        """
        
        # Generic instructions based on pattern type
            # Generic instructions
        
        # Add pattern-specific evidence as hints
        
    
    def _generate_hints(self, solution_code: str, pattern_type: str) -> List[str]:
        """Generate progressive hints for the exercise.
        
        # TODO: Implement python_async_await logic here
        pass
            
        """
        
        # Hint 1: High-level approach
        
        # Hint 2: Key implementation details
        
        # Hint 3: Specific guidance
        
    
    def _generate_test_cases(self, pattern: DetectedPattern, solution_code: str) -> List[TestCase]:
        """Generate test cases for validating the exercise solution.
        
        # TODO: Implement python_async_await logic here
        pass
            
        """
        
        # Generate basic test cases based on pattern type
            # Generic test case
        
    
    def _determine_difficulty(self, file_analysis: FileAnalysis) -> str:
        """Determine exercise difficulty based on file complexity.
        
        # TODO: Implement python_async_await logic here
        pass
            
        """
        
    
    def _estimate_time(self, difficulty: str, instruction_count: int) -> int:
        """Estimate time to complete exercise in minutes.
        
        # TODO: Implement python_async_await logic here
        pass
            
        """
        
        # Add 5 minutes per instruction step
        
    
    def _generate_learning_objectives(self, pattern: DetectedPattern) -> List[str]:
        """Generate learning objectives for the exercise.
        
        # TODO: Implement python_async_await logic here
        pass
            
        """
        
        # Format pattern name for readability
        
        
        # Add objectives based on evidence
        
    
    def _format_pattern_name(self, pattern_type: str) -> str:
        """Format pattern type name for display.
        
        # TODO: Implement python_async_await logic here
        pass
            
        """
        # Convert snake_case or camelCase to Title Case
    
    async def generate_exercises_for_lesson(
        # TODO: Implement python_async_await logic here
        pass
```

#### Hints

<details>
<summary>Hint 1</summary>

Start by understanding the structure of a python_async_await. Look at the imports and main components needed.

</details>
<details>
<summary>Hint 2</summary>

Key elements to implement: 38 main components. Focus on the function signatures and return values first.

</details>
<details>
<summary>Hint 3</summary>

You'll need these imports: import logging

</details>

#### Test Cases

**Test 1**: Test python_async_await implementation
- Input: `Sample input`
- Expected: `Expected output`

---


## Tags

`python_context_managers` `python_async_await` `python_comprehensions`