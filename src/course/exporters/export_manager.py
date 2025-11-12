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
        """
        # Use default format if not specified
        if format is None:
            format = self.config.default_export_format
        
        # Validate format (Req 5.1)
        format = format.lower()
        if format not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported export format: {format}. "
                f"Supported formats: {', '.join(self.SUPPORTED_FORMATS)}"
            )
        
        # Validate output directory permissions (Req 5.1)
        self._validate_output_directory(output_dir)
        
        # Route to appropriate exporter (Req 5.1)
        if format == 'mkdocs':
            return self._export_mkdocs(course, output_dir)
        elif format == 'json':
            return self._export_json(course, output_dir)
        elif format == 'markdown':
            return self._export_markdown(course, output_dir)
        elif format == 'nextjs':
            return self._export_nextjs(course, output_dir)
        elif format == 'pdf':
            return self._export_pdf(course, output_dir)
        else:
            raise ValueError(f"Format {format} not yet implemented")
    
    def _validate_output_directory(self, output_dir: str) -> None:
        """Validate that output directory is writable.
        
        This method implements Requirement 5.1:
        - Validates output directory permissions
        
        Args:
            output_dir: Output directory path
            
        Raises:
            OSError: If directory is not writable
        """
        # Create directory if it doesn't exist
        try:
            os.makedirs(output_dir, exist_ok=True)
        except OSError as e:
            raise OSError(f"Cannot create output directory {output_dir}: {e}")
        
        # Check if directory is writable
        if not os.access(output_dir, os.W_OK):
            raise OSError(f"Output directory is not writable: {output_dir}")
    
    def _export_mkdocs(self, course: CourseOutline, output_dir: str) -> str:
        """Export to MkDocs format.
        
        Args:
            course: Course outline to export
            output_dir: Output directory path
            
        Returns:
            Path to mkdocs.yml file
        """
        return self.mkdocs_exporter.export_to_mkdocs(course, output_dir)
    
    def _export_json(self, course: CourseOutline, output_dir: str) -> str:
        """Export to JSON format.
        
        This method implements Requirement 5.2:
        - Converts CourseOutline to dict
        - Includes all course data with schema
        - Writes formatted JSON with proper indentation
        
        Args:
            course: Course outline to export
            output_dir: Output directory path
            
        Returns:
            Path to JSON file
        """
        # Convert course to dictionary (Req 5.2)
        course_dict = self._course_to_dict(course)
        
        # Write formatted JSON (Req 5.2)
        json_path = os.path.join(output_dir, "course.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(course_dict, f, indent=2, ensure_ascii=False, default=str)
        
        return json_path
    
    def _export_markdown(self, course: CourseOutline, output_dir: str) -> str:
        """Export to standalone Markdown format.
        
        This method implements Requirement 5.4:
        - Creates standalone markdown files
        - Generates README with course overview
        - Uses relative links between files
        
        Args:
            course: Course outline to export
            output_dir: Output directory path
            
        Returns:
            Path to README.md file
        """
        # Create README with course overview (Req 5.4)
        readme_path = os.path.join(output_dir, "README.md")
        readme_content = self._generate_markdown_readme(course)
        self._write_file(readme_path, readme_content)
        
        # Create standalone markdown files for each lesson (Req 5.4)
        for module in course.modules:
            module_slug = self._slugify(module.title)
            module_dir = os.path.join(output_dir, module_slug)
            os.makedirs(module_dir, exist_ok=True)
            
            for lesson in module.lessons:
                lesson_slug = self._slugify(lesson.title)
                lesson_path = os.path.join(module_dir, f"{lesson_slug}.md")
                lesson_content = self._generate_markdown_lesson(lesson, module, course)
                self._write_file(lesson_path, lesson_content)
        
        return readme_path
    
    def _export_nextjs(self, course: CourseOutline, output_dir: str) -> str:
        """Export to Next.js format.
        
        This method implements Requirement 5.3:
        - Generates Next.js project structure
        - Creates React components for lessons
        - Generates course data as JSON
        - Creates navigation component
        
        Args:
            course: Course outline to export
            output_dir: Output directory path
            
        Returns:
            Path to Next.js project directory
        """
        # Create Next.js project structure (Req 5.3)
        self._create_nextjs_structure(output_dir)
        
        # Generate course data as JSON (Req 5.3)
        data_dir = os.path.join(output_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        course_data_path = os.path.join(data_dir, "course.json")
        course_dict = self._course_to_dict(course)
        with open(course_data_path, 'w', encoding='utf-8') as f:
            json.dump(course_dict, f, indent=2, ensure_ascii=False, default=str)
        
        # Create React components (Req 5.3)
        self._generate_nextjs_components(course, output_dir)
        
        # Create navigation component (Req 5.3)
        self._generate_nextjs_navigation(course, output_dir)
        
        # Create package.json
        self._generate_nextjs_package_json(course, output_dir)
        
        return output_dir
    
    def _export_pdf(self, course: CourseOutline, output_dir: str) -> str:
        """Export to PDF format (optional).
        
        This method implements Requirement 5.5:
        - Uses markdown-to-pdf library
        - Generates single PDF with all lessons
        - Adds proper formatting and page breaks
        
        Args:
            course: Course outline to export
            output_dir: Output directory path
            
        Returns:
            Path to PDF file
            
        Note:
            This is an optional feature that requires additional dependencies.
            If dependencies are not available, raises NotImplementedError.
        """
        try:
            import markdown
            from weasyprint import HTML, CSS
        except ImportError:
            raise NotImplementedError(
                "PDF export requires 'markdown' and 'weasyprint' packages. "
                "Install with: pip install markdown weasyprint"
            )
        
        # Generate combined markdown content (Req 5.5)
        combined_md = self._generate_combined_markdown(course)
        
        # Convert markdown to HTML
        html_content = markdown.markdown(
            combined_md,
            extensions=['fenced_code', 'tables', 'toc']
        )
        
        # Add CSS for proper formatting (Req 5.5)
        css_content = self._generate_pdf_css()
        
        # Generate PDF (Req 5.5)
        pdf_path = os.path.join(output_dir, f"{self._slugify(course.title)}.pdf")
        HTML(string=html_content).write_pdf(
            pdf_path,
            stylesheets=[CSS(string=css_content)]
        )
        
        return pdf_path
    
    def _course_to_dict(self, course: CourseOutline) -> Dict[str, Any]:
        """Convert CourseOutline to dictionary.
        
        This method implements Requirement 5.2:
        - Includes all course data with schema
        
        Args:
            course: Course outline to convert
            
        Returns:
            Dictionary representation of course
        """
        return {
            "schema_version": "1.0",
            "course_id": course.course_id,
            "title": course.title,
            "description": course.description,
            "author": course.author,
            "version": course.version,
            "created_at": course.created_at.isoformat(),
            "total_duration_hours": course.total_duration_hours,
            "difficulty_distribution": course.difficulty_distribution,
            "tags": course.tags,
            "prerequisites": course.prerequisites,
            "modules": [
                {
                    "module_id": m.module_id,
                    "title": m.title,
                    "description": m.description,
                    "order": m.order,
                    "difficulty": m.difficulty,
                    "duration_hours": m.duration_hours,
                    "learning_objectives": m.learning_objectives,
                    "lessons": [
                        {
                            "lesson_id": l.lesson_id,
                            "title": l.title,
                            "description": l.description,
                            "order": l.order,
                            "difficulty": l.difficulty,
                            "duration_minutes": l.duration_minutes,
                            "file_path": l.file_path,
                            "teaching_value": l.teaching_value,
                            "learning_objectives": l.learning_objectives,
                            "prerequisites": l.prerequisites,
                            "concepts": l.concepts,
                            "tags": l.tags,
                            "content": {
                                "introduction": l.content.introduction if l.content else "",
                                "explanation": l.content.explanation if l.content else "",
                                "code_example": {
                                    "code": l.content.code_example.code if l.content and l.content.code_example else "",
                                    "language": l.content.code_example.language if l.content and l.content.code_example else "",
                                    "filename": l.content.code_example.filename if l.content and l.content.code_example else "",
                                    "highlights": [
                                        {
                                            "start_line": h.start_line,
                                            "end_line": h.end_line,
                                            "description": h.description
                                        }
                                        for h in (l.content.code_example.highlights if l.content and l.content.code_example else [])
                                    ],
                                    "annotations": l.content.code_example.annotations if l.content and l.content.code_example else {}
                                } if l.content else None,
                                "walkthrough": l.content.walkthrough if l.content else "",
                                "summary": l.content.summary if l.content else "",
                                "further_reading": l.content.further_reading if l.content else []
                            } if l.content else None,
                            "exercises": [
                                {
                                    "exercise_id": e.exercise_id,
                                    "title": e.title,
                                    "description": e.description,
                                    "difficulty": e.difficulty,
                                    "estimated_minutes": e.estimated_minutes,
                                    "instructions": e.instructions,
                                    "starter_code": e.starter_code,
                                    "solution_code": e.solution_code,
                                    "hints": e.hints,
                                    "test_cases": [
                                        {
                                            "input": tc.input,
                                            "expected_output": tc.expected_output,
                                            "description": tc.description
                                        }
                                        for tc in e.test_cases
                                    ],
                                    "learning_objectives": e.learning_objectives
                                }
                                for e in l.exercises
                            ]
                        }
                        for l in m.lessons
                    ]
                }
                for m in course.modules
            ]
        }

    
    def _generate_markdown_readme(self, course: CourseOutline) -> str:
        """Generate README.md content for markdown export.
        
        Args:
            course: Course outline
            
        Returns:
            Markdown content for README
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
        
        # Prerequisites
        if course.prerequisites:
            lines.append("## Prerequisites\n")
            for prereq in course.prerequisites:
                lines.append(f"- {prereq}")
            lines.append("")
        
        # Modules Overview with relative links (Req 5.4)
        lines.append("## Course Modules\n")
        for module in course.modules:
            module_slug = self._slugify(module.title)
            lines.append(f"### {module.title}\n")
            lines.append(f"{module.description}\n")
            lines.append(f"- **Difficulty**: {module.difficulty}")
            lines.append(f"- **Duration**: {module.duration_hours:.1f} hours")
            lines.append(f"- **Lessons**: {len(module.lessons)}\n")
            
            # List lessons with relative links (Req 5.4)
            lines.append("**Lessons:**\n")
            for lesson in module.lessons:
                lesson_slug = self._slugify(lesson.title)
                lesson_path = f"{module_slug}/{lesson_slug}.md"
                lines.append(f"- [{lesson.title}]({lesson_path})")
            lines.append("")
        
        return "\n".join(lines)
    
    def _generate_markdown_lesson(self, lesson, module, course) -> str:
        """Generate markdown content for a lesson.
        
        Args:
            lesson: Lesson to generate content for
            module: Module containing the lesson
            course: Course outline
            
        Returns:
            Markdown content for the lesson
        """
        lines = []
        
        # Navigation breadcrumb with relative links (Req 5.4)
        lines.append(f"[← Back to Course](./../README.md)\n")
        
        # Title
        lines.append(f"# {lesson.title}\n")
        
        # Metadata
        lines.append(f"**Module**: {module.title}")
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
            for prereq in lesson.prerequisites:
                lines.append(f"- {prereq}")
            lines.append("")
        
        # Content
        if lesson.content:
            if lesson.content.introduction:
                lines.append("## Introduction\n")
                lines.append(f"{lesson.content.introduction}\n")
            
            if lesson.content.explanation:
                lines.append("## Explanation\n")
                lines.append(f"{lesson.content.explanation}\n")
            
            if lesson.content.code_example:
                lines.append("## Code Example\n")
                lines.append(f"```{lesson.content.code_example.language}")
                lines.append(lesson.content.code_example.code)
                lines.append("```\n")
            
            if lesson.content.walkthrough:
                lines.append("## Walkthrough\n")
                lines.append(f"{lesson.content.walkthrough}\n")
            
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
                
                if exercise.instructions:
                    lines.append("#### Instructions\n")
                    for i, instruction in enumerate(exercise.instructions, 1):
                        lines.append(f"{i}. {instruction}")
                    lines.append("")
                
                if exercise.starter_code:
                    lines.append("#### Starter Code\n")
                    lines.append("```python")
                    lines.append(exercise.starter_code)
                    lines.append("```\n")
        
        return "\n".join(lines)
    
    def _create_nextjs_structure(self, output_dir: str) -> None:
        """Create Next.js project directory structure.
        
        Args:
            output_dir: Output directory path
        """
        # Create standard Next.js directories
        directories = [
            "app",
            "components",
            "data",
            "public",
            "styles"
        ]
        
        for dir_name in directories:
            os.makedirs(os.path.join(output_dir, dir_name), exist_ok=True)
    
    def _generate_nextjs_components(self, course: CourseOutline, output_dir: str) -> None:
        """Generate React components for lessons.
        
        Args:
            course: Course outline
            output_dir: Output directory path
        """
        components_dir = os.path.join(output_dir, "components")
        
        # Generate LessonCard component
        lesson_card = '''import React from 'react';

interface LessonCardProps {
  title: string;
  description: string;
  difficulty: string;
  duration: number;
  onClick: () => void;
}

export default function LessonCard({ title, description, difficulty, duration, onClick }: LessonCardProps) {
  return (
    <div className="lesson-card" onClick={onClick}>
      <h3>{title}</h3>
      <p>{description}</p>
      <div className="lesson-meta">
        <span className={`difficulty ${difficulty}`}>{difficulty}</span>
        <span className="duration">{duration} min</span>
      </div>
    </div>
  );
}
'''
        self._write_file(os.path.join(components_dir, "LessonCard.tsx"), lesson_card)
        
        # Generate LessonContent component
        lesson_content = '''import React from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/cjs/styles/prism';

interface LessonContentProps {
  lesson: any;
}

export default function LessonContent({ lesson }: LessonContentProps) {
  return (
    <div className="lesson-content">
      <h1>{lesson.title}</h1>
      
      <div className="lesson-meta">
        <span>Difficulty: {lesson.difficulty}</span>
        <span>Duration: {lesson.duration_minutes} minutes</span>
      </div>
      
      {lesson.learning_objectives && (
        <section className="learning-objectives">
          <h2>Learning Objectives</h2>
          <ul>
            {lesson.learning_objectives.map((obj: string, idx: number) => (
              <li key={idx}>{obj}</li>
            ))}
          </ul>
        </section>
      )}
      
      {lesson.content && (
        <>
          {lesson.content.introduction && (
            <section className="introduction">
              <h2>Introduction</h2>
              <p>{lesson.content.introduction}</p>
            </section>
          )}
          
          {lesson.content.explanation && (
            <section className="explanation">
              <h2>Explanation</h2>
              <p>{lesson.content.explanation}</p>
            </section>
          )}
          
          {lesson.content.code_example && (
            <section className="code-example">
              <h2>Code Example</h2>
              <SyntaxHighlighter language={lesson.content.code_example.language} style={vscDarkPlus}>
                {lesson.content.code_example.code}
              </SyntaxHighlighter>
            </section>
          )}
          
          {lesson.content.walkthrough && (
            <section className="walkthrough">
              <h2>Walkthrough</h2>
              <p>{lesson.content.walkthrough}</p>
            </section>
          )}
          
          {lesson.content.summary && (
            <section className="summary">
              <h2>Summary</h2>
              <p>{lesson.content.summary}</p>
            </section>
          )}
        </>
      )}
      
      {lesson.exercises && lesson.exercises.length > 0 && (
        <section className="exercises">
          <h2>Exercises</h2>
          {lesson.exercises.map((exercise: any, idx: number) => (
            <div key={idx} className="exercise">
              <h3>{exercise.title}</h3>
              <p>{exercise.description}</p>
              <div className="exercise-meta">
                <span>Difficulty: {exercise.difficulty}</span>
                <span>Time: {exercise.estimated_minutes} min</span>
              </div>
            </div>
          ))}
        </section>
      )}
    </div>
  );
}
'''
        self._write_file(os.path.join(components_dir, "LessonContent.tsx"), lesson_content)
    
    def _generate_nextjs_navigation(self, course: CourseOutline, output_dir: str) -> None:
        """Generate navigation component.
        
        Args:
            course: Course outline
            output_dir: Output directory path
        """
        components_dir = os.path.join(output_dir, "components")
        
        navigation = '''import React from 'react';
import Link from 'next/link';

interface NavigationProps {
  course: any;
}

export default function Navigation({ course }: NavigationProps) {
  return (
    <nav className="course-navigation">
      <div className="nav-header">
        <h2>{course.title}</h2>
      </div>
      
      <div className="nav-modules">
        {course.modules.map((module: any, moduleIdx: number) => (
          <div key={moduleIdx} className="nav-module">
            <h3>{module.title}</h3>
            <ul>
              {module.lessons.map((lesson: any, lessonIdx: number) => (
                <li key={lessonIdx}>
                  <Link href={`/lesson/${lesson.lesson_id}`}>
                    {lesson.title}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </nav>
  );
}
'''
        self._write_file(os.path.join(components_dir, "Navigation.tsx"), navigation)
    
    def _generate_nextjs_package_json(self, course: CourseOutline, output_dir: str) -> None:
        """Generate package.json for Next.js project.
        
        Args:
            course: Course outline
            output_dir: Output directory path
        """
        package_json = {
            "name": self._slugify(course.title),
            "version": course.version,
            "description": course.description,
            "scripts": {
                "dev": "next dev",
                "build": "next build",
                "start": "next start",
                "lint": "next lint"
            },
            "dependencies": {
                "next": "^14.0.0",
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-syntax-highlighter": "^15.5.0"
            },
            "devDependencies": {
                "@types/node": "^20.0.0",
                "@types/react": "^18.2.0",
                "@types/react-syntax-highlighter": "^15.5.0",
                "typescript": "^5.0.0"
            }
        }
        
        package_path = os.path.join(output_dir, "package.json")
        with open(package_path, 'w', encoding='utf-8') as f:
            json.dump(package_json, f, indent=2)
    
    def _generate_combined_markdown(self, course: CourseOutline) -> str:
        """Generate combined markdown for PDF export.
        
        Args:
            course: Course outline
            
        Returns:
            Combined markdown content
        """
        lines = []
        
        # Title page
        lines.append(f"# {course.title}\n")
        lines.append(f"**Author**: {course.author}\n")
        lines.append(f"**Version**: {course.version}\n")
        lines.append(f"{course.description}\n")
        lines.append("\\pagebreak\n")
        
        # Table of contents
        lines.append("# Table of Contents\n")
        for module in course.modules:
            lines.append(f"- {module.title}")
            for lesson in module.lessons:
                lines.append(f"  - {lesson.title}")
        lines.append("\n\\pagebreak\n")
        
        # Lessons
        for module in course.modules:
            lines.append(f"# {module.title}\n")
            lines.append(f"{module.description}\n")
            lines.append("\\pagebreak\n")
            
            for lesson in module.lessons:
                lines.append(f"## {lesson.title}\n")
                lines.append(f"**Difficulty**: {lesson.difficulty} | **Duration**: {lesson.duration_minutes} minutes\n")
                
                if lesson.content:
                    if lesson.content.introduction:
                        lines.append(f"{lesson.content.introduction}\n")
                    
                    if lesson.content.explanation:
                        lines.append(f"### Explanation\n")
                        lines.append(f"{lesson.content.explanation}\n")
                    
                    if lesson.content.code_example:
                        lines.append(f"### Code Example\n")
                        lines.append(f"```{lesson.content.code_example.language}")
                        lines.append(lesson.content.code_example.code)
                        lines.append("```\n")
                    
                    if lesson.content.summary:
                        lines.append(f"### Summary\n")
                        lines.append(f"{lesson.content.summary}\n")
                
                lines.append("\\pagebreak\n")
        
        return "\n".join(lines)
    
    def _generate_pdf_css(self) -> str:
        """Generate CSS for PDF formatting.
        
        Returns:
            CSS content for PDF styling
        """
        return '''
        @page {
            size: A4;
            margin: 2cm;
        }
        
        body {
            font-family: 'Arial', sans-serif;
            font-size: 11pt;
            line-height: 1.6;
        }
        
        h1 {
            font-size: 24pt;
            margin-top: 1em;
            margin-bottom: 0.5em;
            page-break-before: always;
        }
        
        h2 {
            font-size: 18pt;
            margin-top: 1em;
            margin-bottom: 0.5em;
        }
        
        h3 {
            font-size: 14pt;
            margin-top: 0.8em;
            margin-bottom: 0.4em;
        }
        
        code {
            font-family: 'Courier New', monospace;
            font-size: 9pt;
            background-color: #f5f5f5;
            padding: 2px 4px;
        }
        
        pre {
            background-color: #f5f5f5;
            padding: 10px;
            border-left: 3px solid #333;
            overflow-x: auto;
            page-break-inside: avoid;
        }
        
        pre code {
            background-color: transparent;
            padding: 0;
        }
        '''
    
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
    
    def _write_file(self, path: str, content: str) -> None:
        """Write content to a file.
        
        Args:
            path: File path
            content: Content to write
        """
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
