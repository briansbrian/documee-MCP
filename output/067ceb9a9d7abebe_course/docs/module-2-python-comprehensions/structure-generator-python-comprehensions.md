# Structure Generator: Python Comprehensions

**Difficulty**: beginner | **Duration**: 40 minutes

## Learning Objectives

- Understand python context managers pattern
- Understand python async await pattern
- Understand python comprehensions pattern
- Learn documentation best practices


## Introduction

Excellent teaching value (score: 0.82). Well-documented (100% coverage). Ideal complexity (avg: 3.7) for teaching. Contains useful patterns. Reasonable structure.

You'll learn about Python Context Managers, Python Async Await, Python Comprehensions through hands-on code analysis.

By the end of this lesson, you'll be able to:
- Implement python comprehensions pattern- Understand python async await pattern- Understand python context managers pattern- Implement CourseStructureGenerator class structure- Understand documentation best practices

## Explanation

## What This Code Does

The `CourseStructureGenerator` class generates course structure from codebase analysis.


## Key Patterns

### Python Context Managers

This code demonstrates the python context managers pattern. Evidence includes: Uses context managers (1 with statements). This has some elements of this pattern.

### Python Async Await

This code demonstrates the python async await pattern. Evidence includes: Async functions: 1, Await statements: 2. This has some elements of this pattern.

### Python Comprehensions

This code demonstrates the python comprehensions pattern. Evidence includes: Uses comprehensions (17 occurrences). This is a clear example of this pattern.



## Code Example

```python
"""Course Structure Generator - Organizes analysis results into modules and lessons."""

from typing import List, Tuple, Dict, Optional
from datetime import datetime
import uuid
from collections import defaultdict
from src.models import CodebaseAnalysis, FileAnalysis, DetectedPattern
from .models import CourseOutline, Module, Lesson
from .config import CourseConfig
from .performance_monitor import get_monitor


class CourseStructureGenerator:
    """Generates course structure from codebase analysis."""
    
    def __init__(self, config: CourseConfig, course_cache=None):
        """Initialize the course structure generator.
        
        Args:
            config: Course generation configuration
            course_cache: Optional CourseCacheManager for caching
        """
        self.config = config
        self.course_cache = course_cache
    
    async def generate_course_structure(self, analysis: CodebaseAnalysis) -> CourseOutline:
        """Generate a complete course structure from analysis results.
        
        This method implements Requirements 1.1, 1.2, 1.3, 1.4, 1.5:
        - Creates CourseOutline with modules organized by difficulty
        - Sorts lessons by teaching value score
        - Creates 3-8 modules based on teachable files
        - Groups lessons by related patterns
        - Estimates total course duration
        
        Args:
            analysis: Codebase analysis results
            
        Returns:
            CourseOutline with modules and lessons
        """
        monitor = get_monitor()
        
        with monitor.measure("course_structure", file_count=len(analysis.file_analyses)):
            # Check cache first
            if self.course_cache:
                cached = await self.course_cache.get_course_structure(analysis.codebase_id)
                if cached and "data" in cached:
                    import logging
                    logging.getLogger(__name__).info(f"Using cached course structure for {analysis.codebase_id}")

# ... (1117 more lines)
```

### Code Annotations

**Line 13**: Class definition: Generates course structure from codebase analysis.
**Line 44**: Python Context Managers pattern starts here
**Line 26**: Python Async Await pattern starts here
**Line 106**: Python Comprehensions pattern starts here

## Walkthrough

## Code Walkthrough

Let's walk through the code step by step:

### CourseStructureGenerator Class

Generates course structure from codebase analysis.

**Key Methods:**

- `__init__(self, config, course_cache)`: Initialize the course structure generator.
- `generate_course_structure(self, analysis)`: Generate a complete course structure from analysis results.
- `group_by_patterns(self, teachable_files, analysis)`: Group files by detected patterns and concepts.
- `calculate_module_count(self, num_teachable_files)`: Calculate optimal number of modules based on file count.
- `sort_by_difficulty(self, modules)`: Sort modules by difficulty level (beginner → intermediate → advanced).

### Important Code Sections

**Line 13**: Class definition: Generates course structure from codebase analysis.

**Line 26**: Python Async Await pattern starts here

**Line 44**: Python Context Managers pattern starts here

**Line 106**: Python Comprehensions pattern starts here



## Summary

## Summary

In this lesson, you learned:

- Implement python comprehensions pattern
- Understand python async await pattern
- Understand python context managers pattern
- Implement CourseStructureGenerator class structure
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

### Practice: Python Comprehensions

Implement a python_comprehensions based on the example from C:\Users\brian\OneDrive\Documents\Apps\Documee_mcp\src\course\structure_generator.py

**Difficulty**: beginner | **Estimated Time**: 35 minutes

#### Instructions

1. Implement the python_comprehensions following the pattern shown
2. Ensure all required functionality is included
3. Test your implementation with the provided test cases
4. Key concepts to include: Uses comprehensions (17 occurrences)

#### Starter Code

```python
# Cache the result
        
    
    def group_by_patterns(
        # TODO: Implement python_comprehensions logic here
        pass
        """Group files by detected patterns and concepts.
        
        
            
        """
        # Create pattern-based groups
        
            
            # Find primary pattern for this file
            
        
        # Convert to list of groups, sorted by group size (largest first)
        
        # Add ungrouped files as individual groups
        
    
    def calculate_module_count(self, num_teachable_files: int) -> int:
        """Calculate optimal number of modules based on file count.
        
        # TODO: Implement python_comprehensions logic here
        pass
        
            
        """
        
        # Aim for 3-5 lessons per module
        
    
    def sort_by_difficulty(self, modules: List[Module]) -> List[Module]:
        """Sort modules by difficulty level (beginner → intermediate → advanced).
        
        # TODO: Implement python_comprehensions logic here
        pass
        
            
        """
        
    
    def _filter_teachable_files(self, analysis: CodebaseAnalysis) -> List[Tuple[str, float]]:
        """Filter files by teaching value threshold and sort by score.
        
        # TODO: Implement python_comprehensions logic here
        pass
        """
        
        # Already sorted by teaching value in descending order
    
    def _get_primary_pattern(self, file_analysis: FileAnalysis) -> str:
        """Get the primary pattern type for a file."""
        # TODO: Implement python_comprehensions logic here
        pass
        
        # Return the pattern with highest confidence
    
    def _create_modules(
        # TODO: Implement python_comprehensions logic here
        pass
        """Create modules from grouped files."""
        
        # Distribute groups across modules
        
            
            
        
    
    def _create_single_module(
        # TODO: Implement python_comprehensions logic here
        pass
        """Create a single module from file groups.
        
        """
        # Flatten groups into single list
        
        # Create lessons with pattern grouping (Req 1.4)
        
        # Calculate module difficulty (Req 1.1)
        
        # Calculate module duration (Req 1.3)
        
        # Generate module title and description
        
        # Generate module learning objectives (Req 1.4)
        
    
    def _generate_module_objectives(
        # TODO: Implement python_comprehensions logic here
        pass
        """Generate learning objectives for a module.
        
        """
        
        # Collect all patterns from the module
        
        # Create objectives for top patterns
        
        # Add objective based on module difficulty
        
        # Add objective based on lesson count
        
    
    def _create_basic_lesson(
        # TODO: Implement python_comprehensions logic here
        pass
        """Create a basic lesson structure (full implementation in Task 2.2)."""
        # Calculate difficulty from complexity
        
        # Estimate duration based on complexity
        
        # Generate title from file path
        
        # Generate description
        
        # Extract concepts from patterns
        
        # Generate basic learning objectives
        
        
        # Apply audience-based adjustments (Task 13.2)
        
    
    def _calculate_module_difficulty(self, lessons: List[Lesson]) -> str:
        """Calculate overall module difficulty from lessons."""
        # TODO: Implement python_comprehensions logic here
        pass
        
        
        # Return the most common difficulty
    
    def _calculate_lesson_difficulty(self, file_analysis: FileAnalysis) -> str:
        """Calculate lesson difficulty from complexity metrics."""
        # TODO: Implement python_comprehensions logic here
        pass
        
    
    def _estimate_lesson_duration(self, file_analysis: FileAnalysis) -> int:
        """Estimate lesson duration in minutes based on complexity."""
        # Base duration
        # TODO: Implement python_comprehensions logic here
        pass
        
        # Add time based on number of functions/classes
        
        # Add time based on patterns
        
        
        # Clamp to config range
    
    def _generate_lesson_title(self, file_path: str, file_analysis: FileAnalysis) -> str:
        """Generate a lesson title from file path and analysis."""
        # Get filename without extension
        import os
        # TODO: Implement python_comprehensions logic here
        pass
        
        # Convert snake_case or kebab-case to Title Case
        
        # Add pattern context if available
        
    
    def _generate_lesson_description(self, file_analysis: FileAnalysis) -> str:
        """Generate a lesson description from analysis."""
        # TODO: Implement python_comprehensions logic here
        pass
        
        # Add teaching value explanation
        
        # Add pattern information
        
    
    def _generate_basic_objectives(self, file_analysis: FileAnalysis) -> List[str]:
        """Generate basic learning objectives from file analysis."""
        # TODO: Implement python_comprehensions logic here
        pass
        
        # Add objectives based on patterns
        
        # Add objective based on complexity
        
        # Add objective based on documentation
        
    
    def _generate_module_title(
        # TODO: Implement python_comprehensions logic here
        pass
        """Generate a module title from file groups."""
        # Get most common pattern across all files
        
        
        
    
    def _generate_module_description(self, lessons: List[Lesson]) -> str:
        """Generate a module description from lessons."""
        # TODO: Implement python_comprehensions logic here
        pass
        
        # Collect unique concepts
        
        
    
    def _calculate_difficulty_distribution(self, modules: List[Module]) -> Dict[str, int]:
        """Calculate distribution of difficulty levels across all lessons."""
        # TODO: Implement python_comprehensions logic here
        pass
        
        
    
    def _generate_course_title(self, analysis: CodebaseAnalysis) -> str:
        """Generate a course title from codebase analysis."""
        # Use codebase_id as base
        # TODO: Implement python_comprehensions logic here
        pass
    
    def _generate_course_description(
        # TODO: Implement python_comprehensions logic here
        pass
        """Generate a course description."""
    
    def _generate_course_tags(self, analysis: CodebaseAnalysis) -> List[str]:
        """Generate course tags from analysis."""
        # TODO: Implement python_comprehensions logic here
        pass
        
        # Add pattern types as tags
        
    
    # ========== Task 2.3: Learning Progression Logic ==========
    
    def _apply_learning_progression(
        # TODO: Implement python_comprehensions logic here
        pass
        """Apply learning progression logic to modules and lessons.
        
        
            
        """
        # Build a map of file_path -> lesson for quick lookup
        
        
        # Detect prerequisites for each lesson (Req 6.2, 6.3)
        
        # Sort lessons within each module by prerequisites (Req 6.4)
            # Update lesson order after sorting
        
    
    def _detect_prerequisites(
        # TODO: Implement python_comprehensions logic here
        pass
        """Detect prerequisite lessons based on imports and dependencies.
        
        
            
        """
        
        # Get file analysis for this lesson
        
        # Check imports to find dependencies
            # Skip external imports
                # Try to find the imported file in our lessons
                
                    # Only add if it's a different lesson and simpler
        
        # Also check dependency graph
        
    
    def _is_internal_import(self, module: str, analysis: CodebaseAnalysis) -> bool:
        """Check if an import is internal to the codebase."""
        # Check if any file path contains the module name
        # TODO: Implement python_comprehensions logic here
        pass
    
    def _resolve_import_to_file(
        # TODO: Implement python_comprehensions logic here
        pass
        """Resolve an import statement to an actual file path."""
        # Try to find matching file in analysis
        
            # Check if file path ends with module path
        
    
    def _is_simpler_lesson(self, lesson1: Lesson, lesson2: Lesson) -> bool:
        """Check if lesson1 is simpler than lesson2.
        
        # TODO: Implement python_comprehensions logic here
        pass
        """
        
        
            # If same difficulty, use teaching value (higher = simpler/better starting point)
        
    
    def _sort_lessons_by_prerequisites(self, lessons: List[Lesson]) -> List[Lesson]:
        """Sort lessons so prerequisites appear before dependent lessons.
        
        # TODO: Implement python_comprehensions logic here
        pass
        
        """
        # Build dependency graph
        
```

#### Hints

<details>
<summary>Hint 1</summary>

Start by understanding the structure of a python_comprehensions. Look at the imports and main components needed.

</details>
<details>
<summary>Hint 2</summary>

Key elements to implement: 67 main components. Focus on the function signatures and return values first.

</details>
<details>
<summary>Hint 3</summary>

You'll need these imports: import os

</details>

#### Test Cases

**Test 1**: Test python_comprehensions implementation
- Input: `Sample input`
- Expected: `Expected output`

---


## Tags

`python_context_managers` `python_async_await` `python_comprehensions`