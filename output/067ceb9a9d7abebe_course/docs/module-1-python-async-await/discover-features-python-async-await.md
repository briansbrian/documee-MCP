# Discover Features: Python Async Await

**Difficulty**: intermediate | **Duration**: 45 minutes

## Learning Objectives

- Understand python async await pattern
- Understand python comprehensions pattern
- Analyze complex code structure
- Learn documentation best practices


## Introduction

Excellent teaching value (score: 0.76). Well-documented (100% coverage). Slightly complex (avg complexity: 8.7). Contains useful patterns. Well-structured code.

You'll learn about Python Async Await, Python Comprehensions through hands-on code analysis.

By the end of this lesson, you'll be able to:
- Apply python async await pattern- Understand python comprehensions pattern- Analyze discover_features function implementation- Apply techniques for managing code complexity- Understand documentation best practices

## Explanation

## What This Code Does

This file contains several functions:

- **discover_features**: Discover features in a codebase such as routes, components, API endpoints, utilities, and hooks.
- **_find_directories**: Find all directories matching a pattern in the codebase.
- **_filter_by_categories**: Filter features by specified categories.

## Key Patterns

### Python Async Await

This code demonstrates the python async await pattern. Evidence includes: Async functions: 1, Await statements: 6. This shows characteristics of this pattern.

### Python Comprehensions

This code demonstrates the python comprehensions pattern. Evidence includes: Uses comprehensions (4 occurrences). This has some elements of this pattern.

## Complexity Considerations

This code has an average complexity of 8.7. The most complex functions are: discover_features. Pay special attention to how the code manages this complexity through clear structure and organization.



## Code Example

```python
"""
Feature Discovery Tool for MCP Server.

This module implements the discover_features tool that identifies features in a codebase
such as routes, components, API endpoints, utilities, and hooks. Achieves God Mode
performance through intelligent caching (<0.1s cached, <5s first run).
"""

import logging
import os
from typing import Dict, Any, List, Optional

from src.cache.unified_cache import UnifiedCacheManager
from src.models.schemas import Feature, FeatureDiscoveryResult
from src.utils.file_utils import generate_feature_id


logger = logging.getLogger(__name__)


# Feature directory patterns by category
FEATURE_PATTERNS = {
    "routes": ["routes", "pages", "app"],
    "components": ["components", "widgets"],
    "api": ["api", "endpoints", "controllers"],
    "utils": ["utils", "helpers", "lib"],
    "hooks": ["hooks", "composables"]
}


async def discover_features(
    codebase_id: str,
    categories: Optional[List[str]] = None,
    use_cache: bool = True,
    cache_manager: Optional[UnifiedCacheManager] = None
) -> Dict[str, Any]:
    """
    Discover features in a codebase such as routes, components, API endpoints, utilities, and hooks.
    
    This function searches for feature directories based on common patterns, generates unique
    feature IDs, assigns priorities, and filters by categories. Results are cached for 1 hour
    to achieve God Mode performance (<0.1s on subsequent calls).
    
    Args:
        codebase_id: Unique identifier from scan_codebase
        categories: List of categories to discover (default: ["all"])
                   Options: routes, components, api, utils, hooks, or all
        use_cache: Whether to use cached results if available (default: True)
        cache_manager: UnifiedCacheManager instance for caching
        

# ... (175 more lines)
```

### Code Annotations

**Line 31**: Python Async Await pattern starts here
**Line 169**: Complex function (complexity 6): Pay attention to control flow
**Line 89**: Python Comprehensions pattern starts here

## Walkthrough

## Code Walkthrough

Let's walk through the code step by step:

### Functions

**discover_features**

Discover features in a codebase such as routes, components, API endpoints, utilities, and hooks.
    
    This function searches for feature directories based on common patterns, generates unique
    feature IDs, assigns priorities, and filters by categories. Results are cached for 1 hour
    to achieve God Mode performance (<0.1s on subsequent calls).
    
    Args:
        codebase_id: Unique identifier from scan_codebase
        categories: List of categories to discover (default: ["all"])
                   Options: routes, components, api, utils, hooks, or all
        use_cache: Whether to use cached results if available (default: True)
        cache_manager: UnifiedCacheManager instance for caching
        
    Returns:
        Dictionary containing:
            - features: List of Feature objects with id, name, category, path, priority
            - total_features: Total number of features discovered
            - categories: List of unique categories found
            - from_cache: Whether result was from cache
            
    Raises:
        ValueError: If codebase has not been scanned first
        
    Examples:
        >>> result = await discover_features("a1b2c3d4e5f6g7h8")
        >>> print(result["total_features"])
        5
        >>> print(result["features"][0]["category"])
        "routes"

Parameters:
- `codebase_id`
- `categories`
- `use_cache`
- `cache_manager`

*Note: This function has complexity 18, so pay attention to its control flow.*

**_find_directories**

Find all directories matching a pattern in the codebase.
    
    This function searches for directories whose name matches the pattern,
    looking at all levels of the directory tree.
    
    Args:
        root_path: Root directory to search
        pattern: Directory name pattern to match (e.g., "routes", "components")
        
    Returns:
        List of absolute paths to matching directories

Parameters:
- `root_path`
- `pattern`

*Note: This function has complexity 6, so pay attention to its control flow.*

**_filter_by_categories**

Filter features by specified categories.
    
    Args:
        features: List of feature dictionaries
        categories: List of categories to include
        
    Returns:
        Filtered list of feature dictionaries

Parameters:
- `features`
- `categories`

### Important Code Sections

**Line 31**: Python Async Await pattern starts here

**Line 89**: Python Comprehensions pattern starts here

**Line 169**: Complex function (complexity 6): Pay attention to control flow



## Summary

## Summary

In this lesson, you learned:

- Apply python async await pattern
- Understand python comprehensions pattern
- Analyze discover_features function implementation
- Apply techniques for managing code complexity
- Understand documentation best practices

### Key Takeaways

- Understanding python async await and python comprehensions will help you write better code
- Managing complexity through clear structure is essential for maintainable code
- Good documentation makes code easier to understand and maintain
- Practice implementing these concepts in your own projects

### Next Steps

Try modifying the code to experiment with different approaches. Complete the exercises to reinforce your understanding.


## Further Reading

- Code Complexity and Refactoring
- Documentation Best Practices

## Exercises

### Practice: Python Async Await

Implement a python_async_await based on the example from C:\Users\brian\OneDrive\Documents\Apps\Documee_mcp\src\tools\discover_features.py

**Difficulty**: intermediate | **Estimated Time**: 45 minutes

#### Instructions

1. Implement the python_async_await following the pattern shown
2. Ensure all required functionality is included
3. Test your implementation with the provided test cases
4. Key concepts to include: Async functions: 1, Await statements: 6

#### Starter Code

```python
async def discover_features(
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

Key elements to implement: 1 main components. Focus on the function signatures and return values first.

</details>

#### Test Cases

**Test 1**: Test python_async_await implementation
- Input: `Sample input`
- Expected: `Expected output`

---


## Tags

`python_async_await` `python_comprehensions`