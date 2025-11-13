# Symbol Extractor: Python Comprehensions

**Difficulty**: intermediate | **Duration**: 50 minutes

## Learning Objectives

- Understand python comprehensions pattern
- Analyze complex code structure
- Learn documentation best practices


## Introduction

Excellent teaching value (score: 0.74). Well-documented (100% coverage). Ideal complexity (avg: 6.5) for teaching. Contains some patterns. Well-structured code.

You'll learn about Python Comprehensions through hands-on code analysis.

By the end of this lesson, you'll be able to:
- Understand python comprehensions pattern- Implement FunctionInfo class structure- Apply techniques for managing code complexity- Understand documentation best practices

## Explanation

## What This Code Does

The `FunctionInfo` class information about a function or method.

The `ClassInfo` class information about a class.


## Key Patterns

### Python Comprehensions

This code demonstrates the python comprehensions pattern. Evidence includes: Uses comprehensions (1 occurrences). This has some elements of this pattern.

## Complexity Considerations

This code has an average complexity of 6.5. The most complex functions are: SymbolExtractor._extract_python_symbols, SymbolExtractor._extract_python_imports, SymbolExtractor._traverse_javascript_node. Pay special attention to how the code manages this complexity through clear structure and organization.



## Code Example

```python
"""
Symbol Extractor for extracting functions, classes, and other symbols from AST.

This module extracts structured information about code symbols (functions, classes,
imports, etc.) from parsed Abstract Syntax Trees across multiple languages.
"""

import logging
from typing import List, Optional, Any, Dict
from dataclasses import dataclass, field

from .ast_parser import ParseResult

logger = logging.getLogger(__name__)


@dataclass
class FunctionInfo:
    """Information about a function or method.
    
    Attributes:
        name: Function name
        parameters: List of parameter names
        return_type: Return type annotation (if available)
        docstring: Function docstring/documentation
        start_line: Starting line number (1-indexed)
        end_line: Ending line number (1-indexed)
        complexity: Cyclomatic complexity score
        is_async: Whether function is async
        decorators: List of decorator names
    """
    name: str
    parameters: List[str] = field(default_factory=list)
    return_type: Optional[str] = None
    docstring: Optional[str] = None
    start_line: int = 0
    end_line: int = 0
    complexity: int = 1
    is_async: bool = False
    decorators: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        from dataclasses import asdict
        return asdict(self)


@dataclass
class ClassInfo:
    """Information about a class.

# ... (1612 more lines)
```

### Code Annotations

**Line 18**: Class definition: Information about a function or method.
**Line 49**: Class definition: Information about a class.
**Line 76**: Class definition: Information about an import statement.
**Line 99**: Class definition: Complete symbol information for a file.
**Line 119**: Class definition: Extracts functions, classes, and other symbols from AST.
**Line 316**: Python Comprehensions pattern starts here

## Walkthrough

## Code Walkthrough

Let's walk through the code step by step:

### FunctionInfo Class

Information about a function or method.
    
    Attributes:
        name: Function name
        parameters: List of parameter names
        return_type: Return type annotation (if available)
        docstring: Function docstring/documentation
        start_line: Starting line number (1-indexed)
        end_line: Ending line number (1-indexed)
        complexity: Cyclomatic complexity score
        is_async: Whether function is async
        decorators: List of decorator names

**Key Methods:**

- `to_dict(self)`: Convert to dictionary for JSON serialization.

### ClassInfo Class

Information about a class.
    
    Attributes:
        name: Class name
        methods: List of methods in the class
        base_classes: List of parent class names
        docstring: Class docstring/documentation
        start_line: Starting line number (1-indexed)
        end_line: Ending line number (1-indexed)
        decorators: List of decorator names

**Key Methods:**

- `to_dict(self)`: Convert to dictionary for JSON serialization.

### ImportInfo Class

Information about an import statement.
    
    Attributes:
        module: Module name being imported
        imported_symbols: List of specific symbols imported (empty for 'import x')
        is_relative: Whether this is a relative import
        import_type: Type of import ('import', 'from_import', 'require', 'es6_import')
        line_number: Line number of the import

**Key Methods:**

- `to_dict(self)`: Convert to dictionary for JSON serialization.

### SymbolInfo Class

Complete symbol information for a file.
    
    Attributes:
        functions: List of functions found in the file
        classes: List of classes found in the file
        imports: List of import statements
        exports: List of exported symbols (for JS/TS)

**Key Methods:**

- `to_dict(self)`: Convert to dictionary for JSON serialization.

### SymbolExtractor Class

Extracts functions, classes, and other symbols from AST.
    
    Supports multiple languages with language-specific extraction logic.

**Key Methods:**

- `__init__(self)`: Initialize the Symbol Extractor.
- `extract_symbols(self, parse_result)`: Extract all symbols from parsed file.
- `_extract_python_symbols(self, parse_result)`: Extract symbols from Python AST.
- `_extract_python_function(self, node)`: Extract function information from Python function_definition node.
- `_extract_python_parameters(self, params_node)`: Extract parameter names from Python parameters node.

### Important Code Sections

**Line 18**: Class definition: Information about a function or method.

**Line 49**: Class definition: Information about a class.

**Line 76**: Class definition: Information about an import statement.

**Line 99**: Class definition: Complete symbol information for a file.

**Line 119**: Class definition: Extracts functions, classes, and other symbols from AST.



## Summary

## Summary

In this lesson, you learned:

- Understand python comprehensions pattern
- Implement FunctionInfo class structure
- Apply techniques for managing code complexity
- Understand documentation best practices

### Key Takeaways

- Understanding python comprehensions will help you write better code
- Managing complexity through clear structure is essential for maintainable code
- Good documentation makes code easier to understand and maintain
- Practice implementing these concepts in your own projects

### Next Steps

Try modifying the code to experiment with different approaches. Complete the exercises to reinforce your understanding.


## Further Reading

- Code Complexity and Refactoring
- Documentation Best Practices


## Tags

`python_comprehensions`