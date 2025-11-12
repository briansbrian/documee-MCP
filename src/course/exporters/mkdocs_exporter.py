"""MkDocs Exporter - Exports courses to MkDocs format."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, List
from ..models import CourseOutline, Module, Lesson
from ..config import CourseConfig
from ..template_engine import TemplateEngine


class MkDocsExporter:
    """Exports courses to MkDocs static site format.
    
    This class implements Requirements 4.1, 4.2, 4.3, 4.4, 4.5:
    - Generates valid mkdocs.yml configuration
    - Creates hierarchical navigation structure
    - Configures Material theme with code highlighting
    - Enables search and table of contents
    - Generates lesson markdown files in docs/
    """
    
    def __init__(self, config: CourseConfig):
        """Initialize the MkDocs exporter.
        
        Args:
            config: Course generation configuration
        """
        self.config = config
        self.template_engine = TemplateEngine(config)
    
    def export_to_mkdocs(self, course: CourseOutline, output_dir: str) -> str:
        """Export course to MkDocs format.
        
        This method implements Requirements 4.1, 4.2:
        - Generates valid mkdocs.yml configuration file
        - Creates directory structure (docs/, mkdocs.yml)
        
        Args:
            course: Course outline to export
            output_dir: Output directory path
            
        Returns:
            Path to mkdocs.yml file
            
        Raises:
            OSError: If directory creation or file writing fails
        """
        # Create directory structure (Req 4.1)
        self._create_directory_structure(output_dir)
        
        # Generate mkdocs.yml configuration (Req 4.1, 4.2, 4.3, 4.4, 4.5)
        mkdocs_config = self._generate_mkdocs_config(course)
        mkdocs_path = os.path.join(output_dir, "mkdocs.yml")
        self._write_yaml_file(mkdocs_path, mkdocs_config)
        
        # Generate lesson markdown files in docs/ (Req 4.2)
        self._generate_lesson_files(course, output_dir)
        
        # Generate index.md (Req 4.2)
        self._generate_index_file(course, output_dir)
        
        return mkdocs_path
    
    def _create_directory_structure(self, output_dir: str) -> None:
        """Create the MkDocs directory structure.
        
        Creates:
        - output_dir/
        - output_dir/docs/
        - output_dir/docs/{module_slug}/ for each module
        
        Args:
            output_dir: Base output directory
        """
        # Create base directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Create docs directory
        docs_dir = os.path.join(output_dir, "docs")
        os.makedirs(docs_dir, exist_ok=True)
    
    def _generate_mkdocs_config(self, course: CourseOutline) -> Dict[str, Any]:
        """Generate mkdocs.yml configuration.
        
        This method implements Requirements 4.2, 4.3, 4.4, 4.5:
        - Creates hierarchical navigation structure
        - Configures Material theme with code highlighting
        - Enables search and table of contents
        - Configures markdown extensions
        
        Args:
            course: Course outline
            
        Returns:
            Dictionary representing mkdocs.yml configuration
        """
        config = {
            # Basic site information (Req 4.1)
            "site_name": course.title,
            "site_description": course.description,
            "site_author": course.author,
            
            # Theme configuration with Material theme (Req 4.3)
            "theme": {
                "name": "material",
                "palette": {
                    "primary": "indigo",
                    "accent": "indigo"
                },
                "features": [
                    "navigation.tabs",  # Top-level navigation tabs
                    "navigation.sections",  # Expandable sections
                    "navigation.expand",  # Expand all sections by default
                    "search.suggest",  # Search suggestions (Req 4.5)
                    "search.highlight",  # Highlight search terms
                    "content.code.copy"  # Copy button for code blocks
                ],
                "font": {
                    "text": "Roboto",
                    "code": "Roboto Mono"
                }
            },
            
            # Plugins (Req 4.5)
            "plugins": [
                "search",  # Enable search functionality
                "tags"  # Enable tags for lessons
            ],
            
            # Markdown extensions (Req 4.3)
            "markdown_extensions": [
                "pymdownx.highlight",  # Code highlighting with line numbers
                "pymdownx.superfences",  # Enhanced code blocks
                "pymdownx.details",  # Collapsible sections
                "admonition",  # Callout boxes
                "toc"  # Table of contents (Req 4.5)
            ],
            
            # Navigation structure (Req 4.2)
            "nav": self._generate_navigation(course)
        }
        
        return config
    
    def _generate_navigation(self, course: CourseOutline) -> List[Dict[str, Any]]:
        """Generate hierarchical navigation structure.
        
        This method implements Requirement 4.2:
        - Creates navigation structure hierarchically with modules as top-level sections
        
        Args:
            course: Course outline
            
        Returns:
            List of navigation items for mkdocs.yml
        """
        nav = []
        
        # Add home page
        nav.append({"Home": "index.md"})
        
        # Add each module as a top-level section (Req 4.2)
        for module in course.modules:
            module_slug = self._slugify(module.title)
            module_nav = {
                module.title: []
            }
            
            # Add each lesson under the module
            for lesson in module.lessons:
                lesson_slug = self._slugify(lesson.title)
                lesson_path = f"{module_slug}/{lesson_slug}.md"
                module_nav[module.title].append({
                    lesson.title: lesson_path
                })
            
            nav.append(module_nav)
        
        return nav
    
    def _generate_lesson_files(self, course: CourseOutline, output_dir: str) -> None:
        """Generate lesson markdown files in docs/ directory.
        
        This method implements Requirement 4.2:
        - Generates lesson markdown files in docs/
        
        Args:
            course: Course outline
            output_dir: Base output directory
        """
        docs_dir = os.path.join(output_dir, "docs")
        
        for module in course.modules:
            # Create module directory
            module_slug = self._slugify(module.title)
            module_dir = os.path.join(docs_dir, module_slug)
            os.makedirs(module_dir, exist_ok=True)
            
            # Generate lesson files
            for lesson in module.lessons:
                lesson_slug = self._slugify(lesson.title)
                lesson_path = os.path.join(module_dir, f"{lesson_slug}.md")
                
                # Render lesson content using template
                lesson_content = self._render_lesson(lesson)
                
                # Write lesson file
                self._write_file(lesson_path, lesson_content)
    
    def _generate_index_file(self, course: CourseOutline, output_dir: str) -> None:
        """Generate index.md file for the course homepage.
        
        Args:
            course: Course outline
            output_dir: Base output directory
        """
        docs_dir = os.path.join(output_dir, "docs")
        index_path = os.path.join(docs_dir, "index.md")
        
        # Render index content using template
        try:
            index_content = self.template_engine.render_index(course)
        except Exception:
            # Fallback to manual generation if template fails
            index_content = self._generate_index_content(course)
        
        # Write index file
        self._write_file(index_path, index_content)
    
    def _render_lesson(self, lesson: Lesson) -> str:
        """Render a lesson to markdown format.
        
        Args:
            lesson: Lesson to render
            
        Returns:
            Rendered lesson content
        """
        try:
            # Try to use template engine
            return self.template_engine.render_lesson(lesson)
        except Exception:
            # Fallback to manual generation if template fails
            return self._generate_lesson_content(lesson)
    
    def _generate_lesson_content(self, lesson: Lesson) -> str:
        """Generate lesson content manually (fallback).
        
        Args:
            lesson: Lesson to generate content for
            
        Returns:
            Markdown content for the lesson
        """
        lines = []
        
        # Title
        lines.append(f"# {lesson.title}\n")
        
        # Metadata
        lines.append(f"**Difficulty**: {lesson.difficulty} | **Duration**: {lesson.duration_minutes} minutes\n")
        
        # Description
        if lesson.description:
            lines.append(f"{lesson.description}\n")
        
        # Learning Objectives
        if lesson.learning_objectives:
            lines.append("## Learning Objectives\n")
            for obj in lesson.learning_objectives:
                lines.append(f"- {obj}")
            lines.append("")
        
        # Prerequisites
        if lesson.prerequisites:
            lines.append("## Prerequisites\n")
            lines.append("This lesson requires understanding of:\n")
            for prereq in lesson.prerequisites:
                lines.append(f"- {prereq}")
            lines.append("")
        
        # Content
        if lesson.content:
            # Introduction
            if lesson.content.introduction:
                lines.append("## Introduction\n")
                lines.append(f"{lesson.content.introduction}\n")
            
            # Explanation
            if lesson.content.explanation:
                lines.append("## Explanation\n")
                lines.append(f"{lesson.content.explanation}\n")
            
            # Code Example
            if lesson.content.code_example:
                lines.append("## Code Example\n")
                lines.append(f"```{lesson.content.code_example.language}")
                lines.append(lesson.content.code_example.code)
                lines.append("```\n")
            
            # Walkthrough
            if lesson.content.walkthrough:
                lines.append("## Walkthrough\n")
                lines.append(f"{lesson.content.walkthrough}\n")
            
            # Summary
            if lesson.content.summary:
                lines.append("## Summary\n")
                lines.append(f"{lesson.content.summary}\n")
        
        # Exercises
        if lesson.exercises:
            lines.append("## Exercises\n")
            for idx, exercise in enumerate(lesson.exercises, 1):
                lines.append(f"### Exercise {idx}: {exercise.title}\n")
                lines.append(f"{exercise.description}\n")
                lines.append(f"**Difficulty**: {exercise.difficulty} | **Time**: {exercise.estimated_minutes} minutes\n")
                
                # Instructions
                if exercise.instructions:
                    lines.append("#### Instructions\n")
                    for i, instruction in enumerate(exercise.instructions, 1):
                        lines.append(f"{i}. {instruction}")
                    lines.append("")
                
                # Starter Code
                if exercise.starter_code:
                    lines.append("#### Starter Code\n")
                    lines.append("```python")
                    lines.append(exercise.starter_code)
                    lines.append("```\n")
        
        # Tags
        if lesson.tags:
            lines.append(f"\n---\n**Tags**: {', '.join(lesson.tags)}")
        
        return "\n".join(lines)
    
    def _generate_index_content(self, course: CourseOutline) -> str:
        """Generate index page content manually (fallback).
        
        Args:
            course: Course outline
            
        Returns:
            Markdown content for the index page
        """
        lines = []
        
        # Title
        lines.append(f"# {course.title}\n")
        
        # Description
        lines.append(f"{course.description}\n")
        
        # Course Info
        lines.append("## Course Information\n")
        lines.append(f"- **Author**: {course.author}")
        lines.append(f"- **Version**: {course.version}")
        lines.append(f"- **Total Duration**: {course.total_duration_hours:.1f} hours")
        lines.append(f"- **Modules**: {len(course.modules)}")
        
        # Count total lessons
        total_lessons = sum(len(m.lessons) for m in course.modules)
        lines.append(f"- **Lessons**: {total_lessons}\n")
        
        # Difficulty Distribution
        if course.difficulty_distribution:
            lines.append("## Difficulty Distribution\n")
            for difficulty, count in course.difficulty_distribution.items():
                lines.append(f"- **{difficulty.title()}**: {count} lessons")
            lines.append("")
        
        # Prerequisites
        if course.prerequisites:
            lines.append("## Prerequisites\n")
            for prereq in course.prerequisites:
                lines.append(f"- {prereq}")
            lines.append("")
        
        # Modules Overview
        lines.append("## Course Modules\n")
        for module in course.modules:
            lines.append(f"### {module.title}\n")
            lines.append(f"{module.description}\n")
            lines.append(f"- **Difficulty**: {module.difficulty}")
            lines.append(f"- **Duration**: {module.duration_hours:.1f} hours")
            lines.append(f"- **Lessons**: {len(module.lessons)}\n")
        
        # Tags
        if course.tags:
            lines.append(f"\n---\n**Topics Covered**: {', '.join(course.tags)}")
        
        return "\n".join(lines)
    
    def _slugify(self, text: str) -> str:
        """Convert text to URL-friendly slug.
        
        Args:
            text: Text to slugify
            
        Returns:
            Slugified text
        """
        import re
        # Remove invalid characters for file paths (especially Windows)
        text = re.sub(r'[<>:"/\\|?*]', '', text)
        # Replace spaces and underscores with hyphens
        text = text.replace(' ', '-').replace('_', '-')
        # Remove multiple consecutive hyphens
        text = re.sub(r'-+', '-', text)
        # Remove leading/trailing hyphens
        text = text.strip('-')
        return text.lower()
    
    def _write_yaml_file(self, path: str, data: Dict[str, Any]) -> None:
        """Write data to a YAML file.
        
        Args:
            path: File path
            data: Data to write
        """
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    def _write_file(self, path: str, content: str) -> None:
        """Write content to a file.
        
        Args:
            path: File path
            content: Content to write
        """
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
