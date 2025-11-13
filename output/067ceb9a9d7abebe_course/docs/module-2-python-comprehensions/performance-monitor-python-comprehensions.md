# Performance Monitor: Python Comprehensions

**Difficulty**: beginner | **Duration**: 55 minutes

## Learning Objectives

- Understand python context managers pattern
- Understand python generators pattern
- Understand python comprehensions pattern
- Learn documentation best practices


## Introduction

Excellent teaching value (score: 0.82). Well-documented (100% coverage). Slightly simple (avg complexity: 2.1). Contains useful patterns. Well-structured code.

You'll learn about Python Context Managers, Python Generators, Python Comprehensions through hands-on code analysis.

By the end of this lesson, you'll be able to:
- Understand python comprehensions pattern- Understand python generators pattern- Understand python context managers pattern- Implement PerformanceMetric class structure- Understand documentation best practices

## Explanation

## What This Code Does

The `PerformanceMetric` class performance metric for a single operation.

The `PerformanceMonitor` class monitors and tracks performance of course generation operations.


## Key Patterns

### Python Context Managers

This code demonstrates the python context managers pattern. Evidence includes: Uses context managers (1 with statements). This has some elements of this pattern.

### Python Generators

This code demonstrates the python generators pattern. Evidence includes: Uses generators (1 yield statements), Uses generator expressions. This has some elements of this pattern.

### Python Comprehensions

This code demonstrates the python comprehensions pattern. Evidence includes: Uses comprehensions (3 occurrences). This has some elements of this pattern.



## Code Example

```python
"""Performance Monitoring for Course Generation.

This module provides performance monitoring and timing utilities to ensure
course generation meets speed requirements:
- Course outline generation <5s
- Lesson generation <2s
- Exercise generation <3s
- MkDocs export <10s
"""

import time
import logging
from typing import Dict, List, Optional
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime


logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Performance metric for a single operation."""
    operation: str
    duration_seconds: float
    timestamp: datetime
    success: bool
    metadata: Dict = field(default_factory=dict)


class PerformanceMonitor:
    """Monitors and tracks performance of course generation operations.
    
    Implements Requirements 11.1, 11.2, 11.3, 11.4:
    - Tracks course outline generation time (<5s target)
    - Tracks lesson generation time (<2s target)
    - Tracks exercise generation time (<3s target)
    - Tracks MkDocs export time (<10s target)
    """
    
    # Performance targets (in seconds)
    TARGETS = {
        "course_outline": 5.0,
        "lesson_generation": 2.0,
        "exercise_generation": 3.0,
        "mkdocs_export": 10.0,
        "lesson_content": 2.0,
        "course_structure": 5.0
    }

# ... (182 more lines)
```

### Code Annotations

**Line 23**: Class definition: Performance metric for a single operation.
**Line 32**: Class definition: Monitors and tracks performance of course generation operations.
**Line 70**: Python Context Managers pattern starts here
**Line 78**: Python Generators pattern starts here
**Line 118**: Python Comprehensions pattern starts here

## Walkthrough

## Code Walkthrough

Let's walk through the code step by step:

### PerformanceMetric Class

Performance metric for a single operation.

### PerformanceMonitor Class

Monitors and tracks performance of course generation operations.
    
    Implements Requirements 11.1, 11.2, 11.3, 11.4:
    - Tracks course outline generation time (<5s target)
    - Tracks lesson generation time (<2s target)
    - Tracks exercise generation time (<3s target)
    - Tracks MkDocs export time (<10s target)

**Key Methods:**

- `__init__(self)`: Initialize the performance monitor.
- `get_metrics(self, operation)`: Get performance metrics.
- `get_average_duration(self, operation)`: Get average duration for an operation.
- `get_stats(self)`: Get performance statistics.
- `check_targets(self)`: Check if all operations meet their performance targets.

### Functions

**get_monitor**

Get the global performance monitor instance.
    
    Returns:
        Global PerformanceMonitor instance

**reset_monitor**

Reset the global performance monitor.

### Important Code Sections

**Line 23**: Class definition: Performance metric for a single operation.

**Line 32**: Class definition: Monitors and tracks performance of course generation operations.

**Line 70**: Python Context Managers pattern starts here

**Line 78**: Python Generators pattern starts here

**Line 118**: Python Comprehensions pattern starts here



## Summary

## Summary

In this lesson, you learned:

- Understand python comprehensions pattern
- Understand python generators pattern
- Understand python context managers pattern
- Implement PerformanceMetric class structure
- Understand documentation best practices

### Key Takeaways

- Understanding python context managers and python generators will help you write better code
- Good documentation makes code easier to understand and maintain
- Practice implementing these concepts in your own projects

### Next Steps

Try modifying the code to experiment with different approaches. Complete the exercises to reinforce your understanding.


## Further Reading

- Documentation Best Practices


## Tags

`python_context_managers` `python_generators` `python_comprehensions`