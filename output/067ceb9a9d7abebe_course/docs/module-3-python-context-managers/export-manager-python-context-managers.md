# Export Manager: Python Context Managers

**Difficulty**: beginner | **Duration**: 35 minutes

## Learning Objectives

- Understand python context managers pattern
- Understand python comprehensions pattern
- Learn documentation best practices


## Introduction

Excellent teaching value (score: 0.77). Well-documented (100% coverage). Ideal complexity (avg: 3.5) for teaching. Contains useful patterns. Reasonable structure.

You'll learn about Python Context Managers, Python Comprehensions through hands-on code analysis.

By the end of this lesson, you'll be able to:
- Apply python context managers pattern- Understand python comprehensions pattern- Implement ExportManager class structure- Understand documentation best practices

## Explanation

## What This Code Does

The `ExportManager` class manages export of courses to multiple formats.


## Key Patterns

### Python Context Managers

This code demonstrates the python context managers pattern. Evidence includes: Uses context managers (4 with statements), File handling with context managers. This shows characteristics of this pattern.

### Python Comprehensions

This code demonstrates the python comprehensions pattern. Evidence includes: Uses comprehensions (1 occurrences). This has some elements of this pattern.



## Code Example

```python
"""Export Manager - Handles export to multiple formats."""

import os
import json
from typing import Optional, Dict, Any
from pathlib import Path
from ..models import CourseOutline
from ..config import CourseConfig
from .mkdocs_exporter import MkDocsExporter


class ExportManager:
    """Manages export of courses to multiple formats.
    
    This class implements Requirements 5.1, 5.2, 5.3, 5.4, 5.5:
    - Supports MkDocs, Next.js, JSON, Markdown, and PDF formats
    - Routes export requests to appropriate exporters
    - Validates output directory permissions
    """
    
    SUPPORTED_FORMATS = ['mkdocs', 'nextjs', 'json', 'markdown', 'pdf']
    
    def __init__(self, config: CourseConfig):
        """Initialize the export manager.
        
        Args:
            config: Course generation configuration
        """
        self.config = config
        self.mkdocs_exporter = MkDocsExporter(config)
    
    def export(self, course: CourseOutline, output_dir: str, format: Optional[str] = None) -> str:
        """Export course to the specified format.
        
        This method implements Requirement 5.1:
        - Routes export to appropriate format handler
        - Validates output directory permissions
        
        Args:
            course: Course outline to export
            output_dir: Output directory path
            format: Export format (mkdocs, nextjs, json, markdown, pdf)
                   If None, uses config.default_export_format
            
        Returns:
            Path to exported content
            
        Raises:
            ValueError: If format is not supported
            OSError: If output directory is not writable

# ... (823 more lines)
```

### Code Annotations

**Line 12**: Class definition: Manages export of courses to multiple formats.
**Line 135**: Python Context Managers pattern starts here
**Line 321**: Python Comprehensions pattern starts here

## Walkthrough

## Code Walkthrough

Let's walk through the code step by step:

### ExportManager Class

Manages export of courses to multiple formats.
    
    This class implements Requirements 5.1, 5.2, 5.3, 5.4, 5.5:
    - Supports MkDocs, Next.js, JSON, Markdown, and PDF formats
    - Routes export requests to appropriate exporters
    - Validates output directory permissions

**Key Methods:**

- `__init__(self, config)`: Initialize the export manager.
- `export(self, course, output_dir, format)`: Export course to the specified format.
- `_validate_output_directory(self, output_dir)`: Validate that output directory is writable.
- `_export_mkdocs(self, course, output_dir)`: Export to MkDocs format.
- `_export_json(self, course, output_dir)`: Export to JSON format.

### Important Code Sections

**Line 12**: Class definition: Manages export of courses to multiple formats.

**Line 135**: Python Context Managers pattern starts here

**Line 321**: Python Comprehensions pattern starts here



## Summary

## Summary

In this lesson, you learned:

- Apply python context managers pattern
- Understand python comprehensions pattern
- Implement ExportManager class structure
- Understand documentation best practices

### Key Takeaways

- Understanding python context managers and python comprehensions will help you write better code
- Good documentation makes code easier to understand and maintain
- Practice implementing these concepts in your own projects

### Next Steps

Try modifying the code to experiment with different approaches. Complete the exercises to reinforce your understanding.


## Further Reading

- Documentation Best Practices

## Exercises

### Practice: Python Context Managers

Implement a python_context_managers based on the example from C:\Users\brian\OneDrive\Documents\Apps\Documee_mcp\src\course\exporters\export_manager.py

**Difficulty**: beginner | **Estimated Time**: 35 minutes

#### Instructions

1. Implement the python_context_managers following the pattern shown
2. Ensure all required functionality is included
3. Test your implementation with the provided test cases
4. Key concepts to include: Uses context managers (4 with statements), File handling with context managers

#### Starter Code

```python
# Write formatted JSON (Req 5.2)
        
    
    def _export_markdown(self, course: CourseOutline, output_dir: str) -> str:
        """Export to standalone Markdown format.
        
        # TODO: Implement python_context_managers logic here
        pass
        
            
        """
        # Create README with course overview (Req 5.4)
        
        # Create standalone markdown files for each lesson (Req 5.4)
            
        
    
    def _export_nextjs(self, course: CourseOutline, output_dir: str) -> str:
        """Export to Next.js format.
        
        # TODO: Implement python_context_managers logic here
        pass
        
            
        """
        # Create Next.js project structure (Req 5.3)
        
        # Generate course data as JSON (Req 5.3)
        
        # Create React components (Req 5.3)
        
        # Create navigation component (Req 5.3)
        
        # Create package.json
        
    
    def _export_pdf(self, course: CourseOutline, output_dir: str) -> str:
        """Export to PDF format (optional).
        
        # TODO: Implement python_context_managers logic here
        pass
        
            
            
        """
            import markdown
            from weasyprint import HTML, CSS
        
        # Generate combined markdown content (Req 5.5)
        
        # Convert markdown to HTML
        
        # Add CSS for proper formatting (Req 5.5)
        
        # Generate PDF (Req 5.5)
        
    
    def _course_to_dict(self, course: CourseOutline) -> Dict[str, Any]:
        """Convert CourseOutline to dictionary.
        
        # TODO: Implement python_context_managers logic here
        pass
        
            
        """

    
    def _generate_markdown_readme(self, course: CourseOutline) -> str:
        """Generate README.md content for markdown export.
        
        # TODO: Implement python_context_managers logic here
        pass
            
        """
        
        # Title
        
        # Description
        
        # Course Info
        
        # Count total lessons
        
        # Prerequisites
        
        # Modules Overview with relative links (Req 5.4)
            
            # List lessons with relative links (Req 5.4)
        
    
    def _generate_markdown_lesson(self, lesson, module, course) -> str:
        """Generate markdown content for a lesson.
        
        # TODO: Implement python_context_managers logic here
        pass
            
        """
        
        # Navigation breadcrumb with relative links (Req 5.4)
        
        # Title
        
        # Metadata
        
        # Description
        
        # Learning Objectives
        
        # Prerequisites
        
        # Content
            
            
            
            
        
        # Exercises
                
                
        
    
    def _create_nextjs_structure(self, output_dir: str) -> None:
        """Create Next.js project directory structure.
        
        # TODO: Implement python_context_managers logic here
        pass
        """
        # Create standard Next.js directories
        
    
    def _generate_nextjs_components(self, course: CourseOutline, output_dir: str) -> None:
        """Generate React components for lessons.
        
        # TODO: Implement python_context_managers logic here
        pass
        """
        
        # Generate LessonCard component
        lesson_card = '''import React from 'react';


'''
        
        # Generate LessonContent component
        lesson_content = '''import React from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/cjs/styles/prism';


      
      
      
          
          
          
          
      
'''
    
    def _generate_nextjs_navigation(self, course: CourseOutline, output_dir: str) -> None:
        """Generate navigation component.
        
        # TODO: Implement python_context_managers logic here
        pass
        """
        
        navigation = '''import React from 'react';
import Link from 'next/link';


      
'''
    
    def _generate_nextjs_package_json(self, course: CourseOutline, output_dir: str) -> None:
        """Generate package.json for Next.js project.
        
        # TODO: Implement python_context_managers logic here
        pass
        """
        
    
    def _generate_combined_markdown(self, course: CourseOutline) -> str:
        """Generate combined markdown for PDF export.
        
        # TODO: Implement python_context_managers logic here
        pass
            
        """
        
        # Title page
        
        # Table of contents
        
        # Lessons
            
                
                    
                    
                    
                
        
    
    def _generate_pdf_css(self) -> str:
        """Generate CSS for PDF formatting.
        
        # TODO: Implement python_context_managers logic here
        pass
        """
        return '''
        @page {
        
        
        
        
        
        
        
        '''
    
    def _slugify(self, text: str) -> str:
        """Convert text to URL-friendly slug.
        
        # TODO: Implement python_context_managers logic here
        pass
            
        """
        import re
        # Remove invalid characters for file paths (especially Windows)
        # Replace spaces and underscores with hyphens
        # Remove multiple consecutive hyphens
        # Remove leading/trailing hyphens
    
    def _write_file(self, path: str, content: str) -> None:
        """Write content to a file.
        
        # TODO: Implement python_context_managers logic here
        pass
        """
```

#### Hints

<details>
<summary>Hint 1</summary>

Start by understanding the structure of a python_context_managers. Look at the imports and main components needed.

</details>
<details>
<summary>Hint 2</summary>

Key elements to implement: 27 main components. Focus on the function signatures and return values first.

</details>
<details>
<summary>Hint 3</summary>

You'll need these imports: import markdown

</details>

#### Test Cases

**Test 1**: Test python_context_managers implementation
- Input: `Sample input`
- Expected: `Expected output`

---


## Tags

`python_context_managers` `python_comprehensions`