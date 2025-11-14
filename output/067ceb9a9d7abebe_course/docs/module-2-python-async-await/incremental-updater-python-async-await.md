# Incremental Updater: Python Async Await

**Difficulty**: beginner | **Duration**: 1 hour

## Learning Objectives

- Understand python context managers pattern
- Understand python async await pattern
- Understand python comprehensions pattern
- Learn documentation best practices


## Introduction

Excellent teaching value (score: 0.88). Well-documented (100% coverage). Ideal complexity (avg: 3.3) for teaching. Contains useful patterns. Well-structured code.

You'll learn about Python Context Managers, Python Async Await, Python Comprehensions through hands-on code analysis.

By the end of this lesson, you'll be able to:
- Implement python async await pattern- Implement python comprehensions pattern- Apply python context managers pattern- Implement FileChange class structure- Understand documentation best practices

## Explanation

## Understanding the Code

Let's break down this code step by step.

### Purpose

The `FileChange` class represents a change to a source file.

The `LessonUpdate` class represents an update to a lesson.


## Key Patterns

### Python Context Managers

This code demonstrates the python context managers pattern. Evidence includes: Uses context managers (3 with statements), File handling with context managers. This shows characteristics of this pattern.

### Python Async Await

This code demonstrates the python async await pattern. Evidence includes: Async functions: 4, Await statements: 5. This is a clear example of this pattern.

### Python Comprehensions

This code demonstrates the python comprehensions pattern. Evidence includes: Uses comprehensions (10 occurrences). This is a clear example of this pattern.



## Code Example

```python
"""Incremental Course Update Manager.

This module provides incremental update functionality for courses.
Implements Requirements 15.1, 15.2, 15.3, 15.4, 15.5:
- Detects which lessons need updates based on file changes
- Tracks course version history
- Preserves manual edits to lesson content
- Archives deleted lessons
- Completes updates in <3s for <5 changes
"""

import hashlib
import json
import logging
import os
import time
from typing import Dict, List, Optional, Set, Tuple, Any
from datetime import datetime
from dataclasses import dataclass, field

from .models import CourseOutline, Module, Lesson, LessonContent
from .course_cache import CourseCacheManager
from src.models import CodebaseAnalysis


logger = logging.getLogger(__name__)


@dataclass
class FileChange:
    """Represents a change to a source file."""
    file_path: str
    change_type: str  # 'added', 'modified', 'deleted'
    old_hash: Optional[str] = None
    new_hash: Optional[str] = None
    detected_at: datetime = field(default_factory=datetime.now)


@dataclass
class LessonUpdate:
    """Represents an update to a lesson."""
    lesson_id: str
    file_path: str
    update_type: str  # 'content', 'structure', 'archived'
    changes: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class CourseVersion:

# ... (924 more lines)
```

### Code Annotations

**Line 30**: Class definition: Represents a change to a source file.
**Line 40**: Class definition: Represents an update to a lesson.
**Line 50**: Class definition: Represents a version of the course.
**Line 63**: Class definition: Manages incremental updates to course content.
**Line 106**: Python Context Managers pattern starts here
**Line 127**: Python Async Await pattern starts here
**Line 208**: Python Comprehensions pattern starts here

## Walkthrough

## Code Walkthrough

Let's walk through the code step by step:

### FileChange Class

Represents a change to a source file.

### LessonUpdate Class

Represents an update to a lesson.

### CourseVersion Class

Represents a version of the course.

### IncrementalUpdateManager Class

Manages incremental updates to course content.
    
    Provides functionality for:
    - Detecting file changes
    - Identifying lessons that need updates
    - Preserving manual edits
    - Tracking version history
    - Archiving deleted lessons

**Key Methods:**

- `__init__(self, cache_manager, output_dir)`: Initialize the incremental update manager.
- `_compute_file_hash(self, file_path)`: Compute SHA256 hash of file content.
- `_get_file_mtime(self, file_path)`: Get file modification time.
- `detect_file_changes(self, codebase_id, current_files, analysis)`: Detect changes to source files since last course generation.
- `identify_lessons_to_update(self, course, file_changes)`: Identify which lessons need updates based on file changes.

### Important Code Sections

**Line 30**: Class definition: Represents a change to a source file.

**Line 40**: Class definition: Represents an update to a lesson.

**Line 50**: Class definition: Represents a version of the course.

**Line 63**: Class definition: Manages incremental updates to course content.

**Line 106**: Python Context Managers pattern starts here



## Summary

## Summary

In this lesson, you learned:

- Implement python async await pattern
- Implement python comprehensions pattern
- Apply python context managers pattern
- Implement FileChange class structure
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

Implement a python_async_await based on the example from C:\Users\brian\OneDrive\Documents\Apps\Documee_mcp\src\course\incremental_updater.py

**Difficulty**: beginner | **Estimated Time**: 35 minutes

#### Instructions

1. Implement the python_async_await following the pattern shown
2. Ensure all required functionality is included
3. Test your implementation with the provided test cases
4. Key concepts to include: Async functions: 4, Await statements: 5

#### Starter Code

```python
    
    async def detect_file_changes(
        # TODO: Implement python_async_await logic here
        pass
        """Detect changes to source files since last course generation.
        
        
            
        """
        
        # Get cached course structure to find previous files
        
            # No previous course, all files are new
        
        
        # Detect added files
        
        # Detect deleted files
        
        # Detect modified files
            
            # Check if file has changed using cache
            
            # Update hash tracking
        
        
    
    def identify_lessons_to_update(
        # TODO: Implement python_async_await logic here
        pass
        """Identify which lessons need updates based on file changes.
        
        
            
        """
        
        # Build map of file_path -> lesson
        
        # Match file changes to lessons
                
                # Check if lesson has manual edits that should be preserved
                
        
    
    def _has_manual_edits(self, lesson_id: str) -> bool:
        """Check if a lesson has manual edits.
        
        # TODO: Implement python_async_await logic here
        pass
        
            
        """
    
    def mark_manual_edit(self, lesson_id: str, section: str):
        """Mark a section of a lesson as manually edited.
        
        # TODO: Implement python_async_await logic here
        pass
        
        """
        
    
    def preserve_manual_edits(
        # TODO: Implement python_async_await logic here
        pass
        """Preserve manually edited sections when updating lesson content.
        
        
            
        """
        
        
        # Create a copy of new content
        
        # Preserve manually edited sections
        
        
        
        
        
        # Note: code_example is always regenerated from source
        
    
    def archive_lesson(self, course_id: str, lesson: Lesson, reason: str = "file_deleted"):
        """Archive a lesson instead of deleting it.
        
        # TODO: Implement python_async_await logic here
        pass
        
        """
        
        # Add archive metadata
        
        
    
    def get_archived_lessons(self, course_id: str) -> List[Lesson]:
        """Get archived lessons for a course.
        
        # TODO: Implement python_async_await logic here
        pass
            
        """
    
    def create_version(
        # TODO: Implement python_async_await logic here
        pass
        """Create a new course version entry.
        
        
            
        """
        
        
        # Add to version history
        
        
        
    
    def get_version_history(self, course_id: str) -> List[CourseVersion]:
        """Get version history for a course.
        
        # TODO: Implement python_async_await logic here
        pass
        
            
        """
        # Return in reverse order (newest first) since versions are appended chronologically
    
    def get_latest_version(self, course_id: str) -> Optional[CourseVersion]:
        """Get the latest version for a course.
        
        # TODO: Implement python_async_await logic here
        pass
            
        """
    
    def increment_version(self, current_version: str, change_type: str = "minor") -> str:
        """Increment version number based on change type.
        
        # TODO: Implement python_async_await logic here
        pass
            
        """
            
            
    
    def save_version_history(self, course_id: str, output_path: Optional[str] = None):
        """Save version history to disk.
        
        # TODO: Implement python_async_await logic here
        pass
        """
        
        
        
        # Serialize to JSON
        
        
    
    def load_version_history(self, course_id: str, input_path: Optional[str] = None):
        """Load version history from disk.
        
        # TODO: Implement python_async_await logic here
        pass
        """
        
        
            
            # Deserialize from JSON
            
            


    async def update_course_incrementally(
        # TODO: Implement python_async_await logic here
        pass
        """Update course incrementally based on file changes.
        
        
            
        """
        
        
        # Identify lessons to update
        
        # Track updates
        
        # Process each lesson update
                # Archive the lesson
            
                # Update lesson content
        
        # Remove archived lessons from course
        
        # Update course metadata
        
        # Create version entry
        
        # Save version history
        
        
        # Verify performance requirement (Req 15.5)
        
    
    async def _update_lesson_content(
        # TODO: Implement python_async_await logic here
        pass
        """Update content for a single lesson.
        
        
            
        """
        
        # Get file analysis
        
        # Store old content if it exists
        
        # Generate new content
        
        # Preserve manual edits if any
        
        # Update lesson metadata
        
        # Update learning objectives if patterns changed
        
        
        # Update complexity-based difficulty
        
    
    def _calculate_difficulty(self, file_analysis) -> str:
        """Calculate lesson difficulty from file analysis.
        
        # TODO: Implement python_async_await logic here
        pass
            
        """
        
    
    def _remove_archived_lessons(
        # TODO: Implement python_async_await logic here
        pass
        """Remove archived lessons from course structure.
        
            
        """
        
        
        # Remove archived lessons from modules
            
            # Update lesson order after removal
            
            # Update module duration
        
        # Remove empty modules
        
        # Update module order
        
        # Update course duration
        
        # Update difficulty distribution
        
        
    
    def _calculate_difficulty_distribution(self, course: CourseOutline) -> Dict[str, int]:
        """Calculate difficulty distribution across all lessons.
        
        # TODO: Implement python_async_await logic here
        pass
            
        """
        
        
    
    def _count_total_lessons(self, course: CourseOutline) -> int:
        """Count total lessons in course.
        
        # TODO: Implement python_async_await logic here
        pass
            
        """
    
    def _generate_change_summary(
        # TODO: Implement python_async_await logic here
        pass
        """Generate a human-readable summary of changes.
        
            
        """
        
        # Count change types
        
        
        # Count update types
        
        
    
    async def check_for_updates(
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

Key elements to implement: 45 main components. Focus on the function signatures and return values first.

</details>

#### Test Cases

**Test 1**: Test python_async_await implementation
- Input: `Sample input`
- Expected: `Expected output`

---

### Practice: Python Comprehensions

Implement a python_comprehensions based on the example from C:\Users\brian\OneDrive\Documents\Apps\Documee_mcp\src\course\incremental_updater.py

**Difficulty**: beginner | **Estimated Time**: 35 minutes

#### Instructions

1. Implement the python_comprehensions following the pattern shown
2. Ensure all required functionality is included
3. Test your implementation with the provided test cases
4. Key concepts to include: Uses comprehensions (10 occurrences)

#### Starter Code

```python
        
    
    def identify_lessons_to_update(
        # TODO: Implement python_comprehensions logic here
        pass
        """Identify which lessons need updates based on file changes.
        
        
            
        """
        
        # Build map of file_path -> lesson
        
        # Match file changes to lessons
                
                # Check if lesson has manual edits that should be preserved
                
        
    
    def _has_manual_edits(self, lesson_id: str) -> bool:
        """Check if a lesson has manual edits.
        
        # TODO: Implement python_comprehensions logic here
        pass
        
            
        """
    
    def mark_manual_edit(self, lesson_id: str, section: str):
        """Mark a section of a lesson as manually edited.
        
        # TODO: Implement python_comprehensions logic here
        pass
        
        """
        
    
    def preserve_manual_edits(
        # TODO: Implement python_comprehensions logic here
        pass
        """Preserve manually edited sections when updating lesson content.
        
        
            
        """
        
        
        # Create a copy of new content
        
        # Preserve manually edited sections
        
        
        
        
        
        # Note: code_example is always regenerated from source
        
    
    def archive_lesson(self, course_id: str, lesson: Lesson, reason: str = "file_deleted"):
        """Archive a lesson instead of deleting it.
        
        # TODO: Implement python_comprehensions logic here
        pass
        
        """
        
        # Add archive metadata
        
        
    
    def get_archived_lessons(self, course_id: str) -> List[Lesson]:
        """Get archived lessons for a course.
        
        # TODO: Implement python_comprehensions logic here
        pass
            
        """
    
    def create_version(
        # TODO: Implement python_comprehensions logic here
        pass
        """Create a new course version entry.
        
        
            
        """
        
        
        # Add to version history
        
        
        
    
    def get_version_history(self, course_id: str) -> List[CourseVersion]:
        """Get version history for a course.
        
        # TODO: Implement python_comprehensions logic here
        pass
        
            
        """
        # Return in reverse order (newest first) since versions are appended chronologically
    
    def get_latest_version(self, course_id: str) -> Optional[CourseVersion]:
        """Get the latest version for a course.
        
        # TODO: Implement python_comprehensions logic here
        pass
            
        """
    
    def increment_version(self, current_version: str, change_type: str = "minor") -> str:
        """Increment version number based on change type.
        
        # TODO: Implement python_comprehensions logic here
        pass
            
        """
            
            
    
    def save_version_history(self, course_id: str, output_path: Optional[str] = None):
        """Save version history to disk.
        
        # TODO: Implement python_comprehensions logic here
        pass
        """
        
        
        
        # Serialize to JSON
        
        
    
    def load_version_history(self, course_id: str, input_path: Optional[str] = None):
        """Load version history from disk.
        
        # TODO: Implement python_comprehensions logic here
        pass
        """
        
        
            
            # Deserialize from JSON
            
            


    async def update_course_incrementally(
        # TODO: Implement python_comprehensions logic here
        pass
        """Update course incrementally based on file changes.
        
        
            
        """
        
        
        # Identify lessons to update
        
        # Track updates
        
        # Process each lesson update
                # Archive the lesson
            
                # Update lesson content
        
        # Remove archived lessons from course
        
        # Update course metadata
        
        # Create version entry
        
        # Save version history
        
        
        # Verify performance requirement (Req 15.5)
        
    
    async def _update_lesson_content(
        # TODO: Implement python_comprehensions logic here
        pass
        """Update content for a single lesson.
        
        
            
        """
        
        # Get file analysis
        
        # Store old content if it exists
        
        # Generate new content
        
        # Preserve manual edits if any
        
        # Update lesson metadata
        
        # Update learning objectives if patterns changed
        
        
        # Update complexity-based difficulty
        
    
    def _calculate_difficulty(self, file_analysis) -> str:
        """Calculate lesson difficulty from file analysis.
        
        # TODO: Implement python_comprehensions logic here
        pass
            
        """
        
    
    def _remove_archived_lessons(
        # TODO: Implement python_comprehensions logic here
        pass
        """Remove archived lessons from course structure.
        
            
        """
        
        
        # Remove archived lessons from modules
            
            # Update lesson order after removal
            
            # Update module duration
        
        # Remove empty modules
        
        # Update module order
        
        # Update course duration
        
        # Update difficulty distribution
        
        
    
    def _calculate_difficulty_distribution(self, course: CourseOutline) -> Dict[str, int]:
        """Calculate difficulty distribution across all lessons.
        
        # TODO: Implement python_comprehensions logic here
        pass
            
        """
        
        
    
    def _count_total_lessons(self, course: CourseOutline) -> int:
        """Count total lessons in course.
        
        # TODO: Implement python_comprehensions logic here
        pass
            
        """
    
    def _generate_change_summary(
        # TODO: Implement python_comprehensions logic here
        pass
        """Generate a human-readable summary of changes.
        
            
        """
        
        # Count change types
        
        
        # Count update types
        
```

#### Hints

<details>
<summary>Hint 1</summary>

Start by understanding the structure of a python_comprehensions. Look at the imports and main components needed.

</details>
<details>
<summary>Hint 2</summary>

Key elements to implement: 40 main components. Focus on the function signatures and return values first.

</details>

#### Test Cases

**Test 1**: Test python_comprehensions implementation
- Input: `Sample input`
- Expected: `Expected output`

---


## Tags

`python_context_managers` `python_async_await` `python_comprehensions`