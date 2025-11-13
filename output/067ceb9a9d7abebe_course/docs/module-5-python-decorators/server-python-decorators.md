# Server: Python Decorators

**Difficulty**: intermediate | **Duration**: 1 hour

## Learning Objectives

- Understand python decorators pattern
- Understand python generators pattern
- Understand python async await pattern
- Analyze complex code structure
- Learn documentation best practices


## Introduction

Excellent teaching value (score: 0.82). Well-documented (100% coverage). Slightly complex (avg complexity: 7.9). Contains useful patterns. Well-structured code.

You'll learn about Python Decorators, Python Generators, Python Async Await through hands-on code analysis.

By the end of this lesson, you'll be able to:
- Implement python decorators pattern- Implement python async await pattern- Implement python comprehensions pattern- Implement AppContext class structure- Apply techniques for managing code complexity

## Explanation

## What This Code Does

The `AppContext` class application context shared across all tools.


## Key Patterns

### Python Decorators

This code demonstrates the python decorators pattern. Evidence includes: Uses custom decorators (5 types), Total decorators: 15. This is a clear example of this pattern.

### Python Generators

This code demonstrates the python generators pattern. Evidence includes: Uses generators (1 yield statements), Uses generator expressions. This has some elements of this pattern.

### Python Async Await

This code demonstrates the python async await pattern. Evidence includes: Async functions: 15, Await statements: 23. This is a clear example of this pattern.

## Complexity Considerations

This code has an average complexity of 7.9. The most complex functions are: analyze_codebase_tool, export_course, generate_lesson_outline. Pay special attention to how the code manages this complexity through clear structure and organization.



## Code Example

```python
"""
MCP Server Core Implementation using FastMCP.

This module implements the main MCP server entry point with FastMCP framework.
It registers 3 discovery tools (scan_codebase, detect_frameworks, discover_features),
2 resources (codebase://structure, codebase://features), and 1 prompt (analyze_codebase).

The server uses lifespan management for proper cache initialization and cleanup,
achieving God Mode performance through the 3-tier caching system.
"""

import logging
import time
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Optional

from fastmcp import FastMCP, Context

from src.cache.unified_cache import UnifiedCacheManager
from src.config.settings import Settings
from src.tools.scan_codebase import scan_codebase as scan_codebase_impl
from src.tools.detect_frameworks import detect_frameworks as detect_frameworks_impl
from src.tools.discover_features import discover_features as discover_features_impl
from src.analysis.engine import AnalysisEngine
from src.analysis.config import AnalysisConfig


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("server.log")
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class AppContext:
    """Application context shared across all tools."""
    cache_manager: UnifiedCacheManager
    config: Settings
    analysis_engine: AnalysisEngine


# Module-level variable to store app context

# ... (1545 more lines)
```

### Code Annotations

**Line 43**: Class definition: Application context shared across all tools.
**Line 506**: Complex function (complexity 9): Pay attention to control flow
**Line 606**: Complex function (complexity 10): Pay attention to control flow
**Line 711**: Complex function (complexity 7): Pay attention to control flow
**Line 808**: Complex function (complexity 9): Pay attention to control flow
**Line 898**: Complex function (complexity 11): Pay attention to control flow
**Line 1021**: Complex function (complexity 16): Pay attention to control flow
**Line 1193**: Complex function (complexity 14): Pay attention to control flow
**Line 1359**: Complex function (complexity 21): Pay attention to control flow
**Line 55**: Python Async Await pattern starts here
**Line 110**: Python Generators pattern starts here

## Walkthrough

## Code Walkthrough

Let's walk through the code step by step:

### AppContext Class

Application context shared across all tools.

### Functions

**app_lifespan**

Manage server startup and shutdown lifecycle.
    
    Startup:
        - Load configuration from config.yaml
        - Create UnifiedCacheManager
        - Initialize cache connections and tables
        - Log server startup
    
    Shutdown:
        - Close cache connections
        - Cleanup resources
        - Log server shutdown
    
    Args:
        server: FastMCP server instance
        
    Yields:
        AppContext with cache_manager and config

Parameters:
- `server`

**scan_codebase**

Scan codebase structure, languages, and frameworks.
    
    Traverses the directory tree up to max_depth, counts files by language,
    detects project type, and generates a unique codebase ID. Results are
    cached for 1 hour to achieve God Mode performance (<0.1s on subsequent calls).
    
    Args:
        path: Directory path to scan (required)
              Examples:
              - Current directory: "."
              - Relative path: "./src"
              - Absolute path (Windows): "C:\\Users\\username\\project"
              - Absolute path (Unix): "/home/username/project"
        max_depth: Maximum directory depth to traverse (default: 10)
                  Lower values = faster scan, higher values = more thorough
        use_cache: Use cached results if available (default: true)
        ctx: FastMCP context (injected automatically)
    
    Returns:
        Dictionary with codebase_id (save this for other tools!), structure, summary, scan_time_ms, from_cache
    
    Raises:
        ValueError: If path is invalid or contains directory traversal attempts (..)
        PermissionError: If access to path is denied
    
    Examples:
        Scan current directory:
        {"path": "."}
        
        Scan with custom depth:
        {"path": ".", "max_depth": 5}
        
        Scan absolute path:
        {"path": "C:\\Users\\brian\\project"}

Parameters:
- `path`
- `max_depth`
- `use_cache`
- `ctx`

**detect_frameworks**

Detect frameworks and libraries with confidence scores.
    
    Analyzes package.json for JavaScript/TypeScript projects and requirements.txt
    for Python projects, assigning confidence scores (0.99 for package.json, 0.95
    for requirements.txt) and evidence for each detected framework.
    
    Args:
        codebase_id: Unique identifier from scan_codebase (required)
                    You must run scan_codebase first to get this ID
        confidence_threshold: Minimum confidence score to include (0.0-1.0, default: 0.7)
                            Lower = more results, higher = only high-confidence detections
                            Examples: 0.5 (permissive), 0.7 (balanced), 0.9 (strict)
        use_cache: Use cached results if available (default: true)
        ctx: FastMCP context (injected automatically)
    
    Returns:
        Dictionary with frameworks array (name, version, confidence, evidence), 
        total_detected count, confidence_threshold used, from_cache status
    
    Raises:
        ValueError: If codebase has not been scanned first (run scan_codebase first!)
    
    Examples:
        Detect with default threshold:
        {"codebase_id": "a1b2c3d4e5f6g7h8"}
        
        Detect with strict threshold:
        {"codebase_id": "a1b2c3d4e5f6g7h8", "confidence_threshold": 0.9}
        
        Detect with permissive threshold:
        {"codebase_id": "a1b2c3d4e5f6g7h8", "confidence_threshold": 0.5}

Parameters:
- `codebase_id`
- `confidence_threshold`
- `use_cache`
- `ctx`

**discover_features**

Discover features like routes, components, API endpoints, utilities, and hooks.
    
    Searches for feature directories based on common patterns (routes/, components/,
    api/, utils/, hooks/), generates unique feature IDs, and assigns priorities
    (high for routes/api, medium for others).
    
    Args:
        codebase_id: Unique identifier from scan_codebase (required)
        categories: Optional list of categories to discover. 
                   To discover all categories, either:
                   - Don't include "categories" in your JSON at all, OR
                   - Use empty array: []
                   
                   Available category options:
                   - ["routes"] - only routes
                   - ["components"] - only components  
                   - ["api"] - only API endpoints
                   - ["utils"] - only utilities
                   - ["hooks"] - only hooks
                   - ["routes", "api"] - multiple categories
        use_cache: Use cached results if available (default: true)
        ctx: FastMCP context (injected automatically)
    
    Returns:
        Dictionary with features array, total_features, categories, from_cache
    
    Raises:
        ValueError: If codebase has not been scanned first or if codebase_id is empty
    
    Examples:
        Discover all features (omit categories):
        {"codebase_id": "a1b2c3d4e5f6g7h8"}
        
        Discover all features (empty array):
        {"codebase_id": "a1b2c3d4e5f6g7h8", "categories": []}
        
        Discover only routes and API:
        {"codebase_id": "a1b2c3d4e5f6g7h8", "categories": ["routes", "api"]}
        
        Discover only components:
        {"codebase_id": "a1b2c3d4e5f6g7h8", "categories": ["components"]}

Parameters:
- `codebase_id`
- `categories`
- `use_cache`
- `ctx`

**get_structure**

Get cached codebase structure.
    
    Returns the structure data from the most recent scan_codebase call.
    This resource provides access to the codebase's file organization,
    language distribution, and summary information.
    
    Args:
        ctx: FastMCP context (injected automatically)
    
    Returns:
        Dictionary with codebase structure data
    
    Raises:
        ValueError: If resource not available (scan_codebase not called yet)
    
    Examples:
        >>> structure = await get_structure()
        >>> print(structure["structure"]["total_files"])
        150

Parameters:
- `ctx`

### Important Code Sections

**Line 43**: Class definition: Application context shared across all tools.

**Line 55**: Python Async Await pattern starts here

**Line 110**: Python Generators pattern starts here

**Line 506**: Complex function (complexity 9): Pay attention to control flow

**Line 606**: Complex function (complexity 10): Pay attention to control flow



## Summary

## Summary

In this lesson, you learned:

- Implement python decorators pattern
- Implement python async await pattern
- Implement python comprehensions pattern
- Implement AppContext class structure
- Apply techniques for managing code complexity

### Key Takeaways

- Understanding python decorators and python generators will help you write better code
- Managing complexity through clear structure is essential for maintainable code
- Good documentation makes code easier to understand and maintain
- Practice implementing these concepts in your own projects

### Next Steps

Try modifying the code to experiment with different approaches. Complete the exercises to reinforce your understanding.


## Further Reading

- Code Complexity and Refactoring
- Documentation Best Practices

## Exercises

### Practice: Python Decorators

Implement a python_decorators based on the example from C:\Users\brian\OneDrive\Documents\Apps\Documee_mcp\src\server.py

**Difficulty**: intermediate | **Estimated Time**: 45 minutes

#### Instructions

1. Implement the python_decorators following the pattern shown
2. Ensure all required functionality is included
3. Test your implementation with the provided test cases
4. Key concepts to include: Uses custom decorators (5 types), Total decorators: 15

#### Starter Code

```python
@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """
    # TODO: Implement python_decorators logic here
    pass
    
    
    
        
    """
    
    # Startup: initialize resources
    
        # Load configuration
        
        # Create cache manager
        
        # Initialize cache
        
        # Create analysis engine
        
        # Create app context
        
        # Yield context to server
        
        # Shutdown: cleanup resources
        
        


# Create FastMCP server with lifespan management


@mcp.tool
async def scan_codebase(
    # TODO: Implement python_decorators logic here
    pass
    """
    
    
    
    
    
        
        
    """
    
    # Access app context
    
    
    # Log tool invocation
    
    # Call implementation
    
    # Log completion
    
    # Log slow operations
    


@mcp.tool
async def detect_frameworks(
    # TODO: Implement python_decorators logic here
    pass
    """
    
    
    
    
    
        
        
    """
    
    # Access app context
    
    
    # Log tool invocation
    
    # Call implementation
    
    # Log completion
    
    # Log slow operations
    


@mcp.tool
async def discover_features(
    # TODO: Implement python_decorators logic here
    pass
    """
    
    
                   
    
    
    
        
        
        
    """
    
    # Access app context
    
    
    # Log tool invocation
    
    # Call implementation
    
    # Log completion
    
    # Log slow operations
    


@mcp.resource("codebase://structure")
async def get_structure(ctx: Context = None) -> dict:
    """
    # TODO: Implement python_decorators logic here
    pass
    
    
    
    
    
    """
    # Access app context
    
    
    # Log resource access
    
    # Retrieve cached structure
    
    


@mcp.resource("codebase://features")
async def get_features(ctx: Context = None) -> dict:
    """
    # TODO: Implement python_decorators logic here
    pass
    
    
    
    
    
    """
    # Access app context
    
    
    # Log resource access
    
    # Retrieve cached features
    
    


@mcp.prompt
async def analyze_codebase(codebase_path: str) -> str:
    """
    # TODO: Implement python_decorators logic here
    pass
    
    
    
    
    """
    # Log prompt access
    
    # Return template with 4-step workflow
    return f"""Please analyze the codebase at: {codebase_path}







Start with Step 1 and proceed sequentially for best results."""


@mcp.tool
async def analyze_file(
    # TODO: Implement python_decorators logic here
    pass
    """
    
    
    
    
    
        
        
    """
    
    # Access app context
    
    
    # Validate input
    
    # Check if file exists
    from pathlib import Path
    
    # Log tool invocation
    
        # Call analysis engine
        
        # Convert to dict for JSON serialization
        
        # Log completion
        
        # Log slow operations
        
        


@mcp.tool
async def detect_patterns(
    # TODO: Implement python_decorators logic here
    pass
    """
    
    
    
    
    
        
    """
    
    # Access app context
    
    
    # Validate input
    
    # Log tool invocation
    
    # Check cache first
    
            
            # Extract patterns from cached analysis
            
            # Build response
            
            # Convert patterns to dict format if needed
            
            
            
    
    # Not in cache - need to analyze codebase first


@mcp.tool
async def analyze_dependencies(
    # TODO: Implement python_decorators logic here
    pass
```

#### Hints

<details>
<summary>Hint 1</summary>

Start by understanding the structure of a python_decorators. Look at the imports and main components needed.

</details>
<details>
<summary>Hint 2</summary>

Key elements to implement: 18 main components. Focus on the function signatures and return values first.

</details>
<details>
<summary>Hint 3</summary>

You'll need these imports: from pathlib import Path

</details>

#### Test Cases

**Test 1**: Test python_decorators implementation
- Input: `Sample input`
- Expected: `Expected output`

---

### Practice: Python Async Await

Implement a python_async_await based on the example from C:\Users\brian\OneDrive\Documents\Apps\Documee_mcp\src\server.py

**Difficulty**: intermediate | **Estimated Time**: 45 minutes

#### Instructions

1. Implement the python_async_await following the pattern shown
2. Ensure all required functionality is included
3. Test your implementation with the provided test cases
4. Key concepts to include: Async functions: 15, Await statements: 23

#### Starter Code

```python
@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """
    # TODO: Implement python_async_await logic here
    pass
    
    
    
        
    """
    
    # Startup: initialize resources
    
        # Load configuration
        
        # Create cache manager
        
        # Initialize cache
        
        # Create analysis engine
        
        # Create app context
        
        # Yield context to server
        
        # Shutdown: cleanup resources
        
        


# Create FastMCP server with lifespan management


@mcp.tool
async def scan_codebase(
    # TODO: Implement python_async_await logic here
    pass
    """
    
    
    
    
    
        
        
    """
    
    # Access app context
    
    
    # Log tool invocation
    
    # Call implementation
    
    # Log completion
    
    # Log slow operations
    


@mcp.tool
async def detect_frameworks(
    # TODO: Implement python_async_await logic here
    pass
    """
    
    
    
    
    
        
        
    """
    
    # Access app context
    
    
    # Log tool invocation
    
    # Call implementation
    
    # Log completion
    
    # Log slow operations
    


@mcp.tool
async def discover_features(
    # TODO: Implement python_async_await logic here
    pass
    """
    
    
                   
    
    
    
        
        
        
    """
    
    # Access app context
    
    
    # Log tool invocation
    
    # Call implementation
    
    # Log completion
    
    # Log slow operations
    


@mcp.resource("codebase://structure")
async def get_structure(ctx: Context = None) -> dict:
    """
    # TODO: Implement python_async_await logic here
    pass
    
    
    
    
    
    """
    # Access app context
    
    
    # Log resource access
    
    # Retrieve cached structure
    
    


@mcp.resource("codebase://features")
async def get_features(ctx: Context = None) -> dict:
    """
    # TODO: Implement python_async_await logic here
    pass
    
    
    
    
    
    """
    # Access app context
    
    
    # Log resource access
    
    # Retrieve cached features
    
    


@mcp.prompt
async def analyze_codebase(codebase_path: str) -> str:
    """
    # TODO: Implement python_async_await logic here
    pass
    
    
    
    
    """
    # Log prompt access
    
    # Return template with 4-step workflow
    return f"""Please analyze the codebase at: {codebase_path}







Start with Step 1 and proceed sequentially for best results."""


@mcp.tool
async def analyze_file(
    # TODO: Implement python_async_await logic here
    pass
    """
    
    
    
    
    
        
        
    """
    
    # Access app context
    
    
    # Validate input
    
    # Check if file exists
    from pathlib import Path
    
    # Log tool invocation
    
        # Call analysis engine
        
        # Convert to dict for JSON serialization
        
        # Log completion
        
        # Log slow operations
        
        


@mcp.tool
async def detect_patterns(
    # TODO: Implement python_async_await logic here
    pass
    """
    
    
    
    
    
        
    """
    
    # Access app context
    
    
    # Validate input
    
    # Log tool invocation
    
    # Check cache first
    
            
            # Extract patterns from cached analysis
            
            # Build response
            
            # Convert patterns to dict format if needed
            
            
            
    
    # Not in cache - need to analyze codebase first


@mcp.tool
async def analyze_dependencies(
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

Key elements to implement: 18 main components. Focus on the function signatures and return values first.

</details>
<details>
<summary>Hint 3</summary>

You'll need these imports: from pathlib import Path

</details>

#### Test Cases

**Test 1**: Test python_async_await implementation
- Input: `Sample input`
- Expected: `Expected output`

---

### Practice: Python Comprehensions

Implement a python_comprehensions based on the example from C:\Users\brian\OneDrive\Documents\Apps\Documee_mcp\src\server.py

**Difficulty**: intermediate | **Estimated Time**: 45 minutes

#### Instructions

1. Implement the python_comprehensions following the pattern shown
2. Ensure all required functionality is included
3. Test your implementation with the provided test cases
4. Key concepts to include: Uses comprehensions (6 occurrences)

#### Starter Code

```python
            
            
            
    
    # Not in cache - need to analyze codebase first


@mcp.tool
async def analyze_dependencies(
    # TODO: Implement python_comprehensions logic here
    pass
    """
    
    
    
    
    
        
    """
    
    # Access app context
    
    
    # Validate input
    
    # Log tool invocation
    
    # Check cache first
    
            
            # Extract dependency graph from cached analysis
            
            # Calculate metrics
            
            
            
    
    # Not in cache - need to analyze codebase first


@mcp.tool
async def score_teaching_value(
    # TODO: Implement python_comprehensions logic here
    pass
    """
    
    
    
    
    
        
    """
    
    # Access app context
    
    
    # Validate input
    
    # Check if file exists
    from pathlib import Path
    
    # Log tool invocation
    
        # Analyze file to get teaching value
        
        # Extract teaching value score
        
        # Log completion
        
        # Log slow operations
        
        


@mcp.tool
async def analyze_codebase_tool(
    # TODO: Implement python_comprehensions logic here
    pass
    """
    
    
    
    
    
        
        
    """
    
    # Access app context
    
    
    # Validate input
    
    # Log tool invocation
    
    # Check cache first
    
            
            # Add from_cache flag
            
            
    
        # Perform analysis
        
        # Convert to dict for JSON serialization
        
        # Log completion
        
        # Log slow operations
        
        
        # Re-raise ValueError with clear message


@mcp.tool
async def export_course(
    # TODO: Implement python_comprehensions logic here
    pass
    """
    
    
    
    
    
        
        
        
    """
    
    # Access app context
    
    
    # Validate input
    
    # Validate format
    from src.course.exporters.export_manager import ExportManager
    
    # Log tool invocation
    
        # Get analysis from cache
        
        
        # Convert to CodebaseAnalysis if needed
        from src.models import CodebaseAnalysis
        
        # Generate course structure
        from src.course.structure_generator import CourseStructureGenerator
        from src.course.content_generator import LessonContentGenerator
        from src.course.exercise_generator import ExerciseGenerator
        from src.course.config import CourseConfig
        from src.course.exporters.export_manager import ExportManager
        
        # Create course config with user-specified parameters
        
        
        # Generate lesson content for each lesson
        
                # Get file analysis for this lesson
                    # Generate lesson content
                    
                    # Generate exercises (1-3 per lesson based on complexity)
                    
        
        # Set output directory
        
        # Export course
        
        # Calculate statistics
        
        
        # Log completion
        
        # Log slow operations
        
        


@mcp.tool
async def generate_lesson_outline(
    # TODO: Implement python_comprehensions logic here
    pass
    """
    
    
    
    
    
        
    """
    
    # Access app context
    
    
    # Validate input
    
    # Check if file exists
    from pathlib import Path
    
    # Log tool invocation
    
        # Analyze file
        
        # Generate lesson content
        from src.course.content_generator import LessonContentGenerator
        from src.course.config import CourseConfig
        
        
        # Generate learning objectives
        
        # Extract key concepts from patterns
```

#### Hints

<details>
<summary>Hint 1</summary>

Start by understanding the structure of a python_comprehensions. Look at the imports and main components needed.

</details>
<details>
<summary>Hint 2</summary>

Key elements to implement: 11 main components. Focus on the function signatures and return values first.

</details>
<details>
<summary>Hint 3</summary>

You'll need these imports: from_cache = False

</details>

#### Test Cases

**Test 1**: Test python_comprehensions implementation
- Input: `Sample input`
- Expected: `Expected output`

---


## Tags

`python_decorators` `python_generators` `python_async_await` `python_comprehensions`