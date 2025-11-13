# Course Generator Configuration Guide

This guide documents all configuration options available for the Course Generator, including course settings, export formats, and template customization.

## Table of Contents

- [CourseConfig Settings](#courseconfig-settings)
- [Export Formats](#export-formats)
- [Template Customization](#template-customization)
- [Configuration Examples](#configuration-examples)

---

## CourseConfig Settings

The `CourseConfig` class provides comprehensive configuration options for course generation. All settings have sensible defaults but can be customized to fit your needs.

### Basic Settings

#### `target_audience: str`
**Default:** `"mixed"`  
**Options:** `"beginner"`, `"intermediate"`, `"advanced"`, `"mixed"`

Defines the target audience for the course. This affects:
- Content complexity and language
- Lesson filtering and difficulty
- Explanation depth and detail

```python
from src.course.config import CourseConfig

# Beginner-focused course
config = CourseConfig(target_audience="beginner")

# Advanced course
config = CourseConfig(target_audience="advanced")
```

#### `course_focus: str`
**Default:** `"full-stack"`  
**Options:** `"patterns"`, `"architecture"`, `"best-practices"`, `"full-stack"`

Determines which aspects of the codebase to prioritize:
- **patterns**: Focus on design patterns and code patterns
- **architecture**: Emphasize system architecture and structure
- **best-practices**: Highlight coding best practices and conventions
- **full-stack**: Balanced coverage of all aspects

```python
# Focus on design patterns
config = CourseConfig(course_focus="patterns")

# Focus on architecture
config = CourseConfig(course_focus="architecture")
```

#### `author: str`
**Default:** `"Documee Course Generator"`

The author name to include in course metadata.

```python
config = CourseConfig(author="Jane Doe")
```

#### `version: str`
**Default:** `"1.0.0"`

Course version number for tracking updates.

```python
config = CourseConfig(version="2.1.0")
```

### Duration Settings

#### `max_duration_hours: Optional[float]`
**Default:** `None` (no limit)

Maximum total course duration in hours. When set, the generator will limit the number of lessons to fit within this duration.

```python
# Create a 10-hour course
config = CourseConfig(max_duration_hours=10.0)

# Create a 40-hour comprehensive course
config = CourseConfig(max_duration_hours=40.0)
```

#### `min_lesson_duration: int`
**Default:** `15`

Minimum lesson duration in minutes.

#### `max_lesson_duration: int`
**Default:** `60`

Maximum lesson duration in minutes.

```python
# Short, focused lessons (15-30 minutes)
config = CourseConfig(
    min_lesson_duration=15,
    max_lesson_duration=30
)

# Longer, in-depth lessons (30-90 minutes)
config = CourseConfig(
    min_lesson_duration=30,
    max_lesson_duration=90
)
```

### Module Settings

#### `min_modules: int`
**Default:** `3`

Minimum number of modules to create.

#### `max_modules: int`
**Default:** `8`

Maximum number of modules to create.

```python
# Create a compact course with 3-5 modules
config = CourseConfig(
    min_modules=3,
    max_modules=5
)

# Create a comprehensive course with 5-10 modules
config = CourseConfig(
    min_modules=5,
    max_modules=10
)
```

### Exercise Settings

#### `min_exercises_per_lesson: int`
**Default:** `1`

Minimum number of exercises per lesson.

#### `max_exercises_per_lesson: int`
**Default:** `3`

Maximum number of exercises per lesson.

```python
# Minimal exercises (1 per lesson)
config = CourseConfig(
    min_exercises_per_lesson=1,
    max_exercises_per_lesson=1
)

# Comprehensive exercises (2-5 per lesson)
config = CourseConfig(
    min_exercises_per_lesson=2,
    max_exercises_per_lesson=5
)
```

### Code Example Settings

#### `max_code_lines: int`
**Default:** `50`

Maximum number of lines to include in code examples. Longer code will be truncated.

#### `include_annotations: bool`
**Default:** `True`

Whether to include inline annotations in code examples.

```python
# Shorter code examples without annotations
config = CourseConfig(
    max_code_lines=30,
    include_annotations=False
)

# Longer code examples with detailed annotations
config = CourseConfig(
    max_code_lines=100,
    include_annotations=True
)
```

### Content Generation Settings

#### `use_simple_language: bool`
**Default:** `True`

Whether to use simple, accessible language in explanations.

#### `include_glossary: bool`
**Default:** `True`

Whether to include a glossary of terms.

```python
# Technical, advanced language
config = CourseConfig(
    use_simple_language=False,
    include_glossary=False
)

# Beginner-friendly language with glossary
config = CourseConfig(
    use_simple_language=True,
    include_glossary=True
)
```

### Export Settings

#### `default_export_format: str`
**Default:** `"mkdocs"`  
**Options:** `"mkdocs"`, `"nextjs"`, `"json"`, `"markdown"`, `"pdf"`

Default format for course export.

```python
# Export to JSON by default
config = CourseConfig(default_export_format="json")

# Export to Markdown by default
config = CourseConfig(default_export_format="markdown")
```

#### `template_dir: Optional[str]`
**Default:** `None` (use built-in templates)

Path to custom template directory. See [Template Customization](#template-customization) for details.

```python
# Use custom templates
config = CourseConfig(template_dir="./my_templates")
```

### Filtering Settings

#### `min_teaching_value: float`
**Default:** `0.5`

Minimum teaching value score (0.0-1.0) for files to be included in the course.

```python
# Include only high-value content
config = CourseConfig(min_teaching_value=0.7)

# Include more content with lower threshold
config = CourseConfig(min_teaching_value=0.3)
```

#### `priority_tags: List[str]`
**Default:** `[]` (empty list)

List of tags to prioritize when selecting content.

#### `exclude_tags: List[str]`
**Default:** `[]` (empty list)

List of tags to exclude from the course.

```python
# Prioritize React and API content
config = CourseConfig(
    priority_tags=["react", "api", "authentication"]
)

# Exclude test and configuration files
config = CourseConfig(
    exclude_tags=["test", "config", "setup"]
)
```

### Configuration Validation

The `CourseConfig` class includes a `validate()` method that checks all settings for validity:

```python
config = CourseConfig(
    target_audience="intermediate",
    min_modules=3,
    max_modules=8
)

# Validate configuration
try:
    config.validate()
    print("Configuration is valid!")
except ValueError as e:
    print(f"Invalid configuration: {e}")
```

---

## Export Formats

The Course Generator supports multiple export formats, each optimized for different use cases.

### MkDocs (Recommended)

**Format:** `"mkdocs"`  
**Output:** Static website with Material theme

MkDocs is the recommended format for creating professional course websites.

**Features:**
- Material for MkDocs theme with code highlighting
- Hierarchical navigation
- Search functionality
- Table of contents
- Mobile-responsive design
- Markdown extensions (admonitions, code blocks, etc.)

**Usage:**
```python
from src.course.exporters.mkdocs_exporter import MkDocsExporter

exporter = MkDocsExporter(config)
await exporter.export(course_outline, "output/mkdocs_course")

# Preview the course
# cd output/mkdocs_course
# mkdocs serve
```

**Output Structure:**
```
output/mkdocs_course/
├── mkdocs.yml          # MkDocs configuration
├── docs/
│   ├── index.md        # Course homepage
│   ├── module-1/
│   │   ├── lesson-1.md
│   │   └── lesson-2.md
│   └── module-2/
│       └── lesson-1.md
```

### JSON

**Format:** `"json"`  
**Output:** Structured JSON data

JSON export provides a machine-readable format for integration with other systems.

**Features:**
- Complete course data structure
- Schema validation
- Easy to parse and process
- Suitable for APIs and databases

**Usage:**
```python
from src.course.exporters.json_exporter import JSONExporter

exporter = JSONExporter(config)
await exporter.export(course_outline, "output/course.json")
```

**Output Structure:**
```json
{
  "course_id": "uuid",
  "title": "Course Title",
  "modules": [
    {
      "module_id": "uuid",
      "title": "Module 1",
      "lessons": [
        {
          "lesson_id": "uuid",
          "title": "Lesson 1",
          "content": {...},
          "exercises": [...]
        }
      ]
    }
  ]
}
```

### Markdown

**Format:** `"markdown"`  
**Output:** Standalone Markdown files

Markdown export creates standalone files that can be used with any Markdown viewer or editor.

**Features:**
- Portable and universal format
- Relative links between files
- README with course overview
- Compatible with GitHub, GitLab, etc.

**Usage:**
```python
from src.course.exporters.markdown_exporter import MarkdownExporter

exporter = MarkdownExporter(config)
await exporter.export(course_outline, "output/markdown_course")
```

**Output Structure:**
```
output/markdown_course/
├── README.md           # Course overview
├── module-1/
│   ├── lesson-1.md
│   └── lesson-2.md
└── module-2/
    └── lesson-1.md
```

### Next.js

**Format:** `"nextjs"`  
**Output:** Next.js project with React components

Next.js export creates a complete web application with interactive features.

**Features:**
- React components for lessons and exercises
- Client-side navigation
- Interactive code examples
- Progress tracking
- Modern web app experience

**Usage:**
```python
from src.course.exporters.nextjs_exporter import NextJSExporter

exporter = NextJSExporter(config)
await exporter.export(course_outline, "output/nextjs_course")

# Run the app
# cd output/nextjs_course
# npm install
# npm run dev
```

**Output Structure:**
```
output/nextjs_course/
├── package.json
├── pages/
│   ├── index.js
│   ├── modules/
│   │   └── [moduleId]/
│   │       └── [lessonId].js
├── components/
│   ├── Lesson.js
│   └── Exercise.js
└── data/
    └── course.json
```

### PDF (Optional)

**Format:** `"pdf"`  
**Output:** Single PDF document

PDF export creates a printable document with all course content.

**Features:**
- Single file for offline use
- Proper formatting and page breaks
- Table of contents
- Printable format

**Requirements:**
```bash
pip install weasyprint
```

**Usage:**
```python
from src.course.exporters.pdf_exporter import PDFExporter

exporter = PDFExporter(config)
await exporter.export(course_outline, "output/course.pdf")
```

### Export Manager

Use the `ExportManager` to easily export to any format:

```python
from src.course.exporters.export_manager import ExportManager

manager = ExportManager(config)

# Export to MkDocs
await manager.export(course_outline, "output/mkdocs", "mkdocs")

# Export to JSON
await manager.export(course_outline, "output/course.json", "json")

# Export to multiple formats
for format_type in ["mkdocs", "json", "markdown"]:
    await manager.export(course_outline, f"output/{format_type}", format_type)
```

---

## Template Customization

The Course Generator uses Jinja2 templates for content generation. You can customize these templates to match your branding and style preferences.

### Built-in Templates

The generator includes default templates for:
- `lesson.md.j2` - Lesson content
- `exercise.md.j2` - Exercise content
- `module.md.j2` - Module overview
- `index.md.j2` - Course homepage

### Custom Template Directory

To use custom templates:

1. Create a template directory:
```bash
mkdir my_templates
```

2. Copy and modify the default templates:
```bash
cp src/course/templates/*.j2 my_templates/
```

3. Configure the generator to use your templates:
```python
config = CourseConfig(template_dir="my_templates")
```

### Template Variables

Templates have access to the following variables:

#### Lesson Template (`lesson.md.j2`)

```jinja2
{{ lesson.title }}                    # Lesson title
{{ lesson.description }}              # Lesson description
{{ lesson.difficulty }}               # beginner/intermediate/advanced
{{ lesson.duration_minutes }}         # Duration in minutes
{{ lesson.learning_objectives }}      # List of objectives
{{ lesson.prerequisites }}            # List of prerequisite lesson IDs
{{ lesson.concepts }}                 # List of concepts covered
{{ lesson.tags }}                     # List of tags

{{ lesson.content.introduction }}     # Introduction text
{{ lesson.content.explanation }}      # Explanation text
{{ lesson.content.walkthrough }}      # Code walkthrough
{{ lesson.content.summary }}          # Summary text
{{ lesson.content.further_reading }}  # List of reading suggestions

{{ lesson.content.code_example.code }}        # Code content
{{ lesson.content.code_example.language }}    # Programming language
{{ lesson.content.code_example.filename }}    # Source filename
{{ lesson.content.code_example.highlights }}  # List of CodeHighlight
{{ lesson.content.code_example.annotations }} # Dict of line -> annotation

{{ lesson.exercises }}                # List of Exercise objects
```

#### Exercise Template (`exercise.md.j2`)

```jinja2
{{ exercise.title }}                  # Exercise title
{{ exercise.description }}            # Exercise description
{{ exercise.difficulty }}             # Difficulty level
{{ exercise.estimated_minutes }}      # Estimated time
{{ exercise.instructions }}           # List of instruction steps
{{ exercise.starter_code }}           # Starter code with TODOs
{{ exercise.solution_code }}          # Complete solution
{{ exercise.hints }}                  # List of hints
{{ exercise.test_cases }}             # List of TestCase objects
{{ exercise.learning_objectives }}    # List of objectives
```

#### Module Template (`module.md.j2`)

```jinja2
{{ module.title }}                    # Module title
{{ module.description }}              # Module description
{{ module.order }}                    # Module order number
{{ module.difficulty }}               # Difficulty level
{{ module.duration_hours }}           # Duration in hours
{{ module.learning_objectives }}      # List of objectives
{{ module.lessons }}                  # List of Lesson objects
```

### Template Filters

Jinja2 provides built-in filters, and you can add custom ones:

```jinja2
{# Built-in filters #}
{{ lesson.title | upper }}            # UPPERCASE
{{ lesson.title | lower }}            # lowercase
{{ lesson.title | title }}            # Title Case
{{ lesson.duration_minutes | round }} # Round number

{# List filters #}
{{ lesson.concepts | join(', ') }}    # Join list with commas
{{ lesson.exercises | length }}       # Get list length
{{ lesson.objectives | first }}       # Get first item
{{ lesson.objectives | last }}        # Get last item
```

### Example Custom Template

Here's an example of a custom lesson template with enhanced styling:

```jinja2
# {{ lesson.title }}

<div class="lesson-header">
  <span class="badge badge-{{ lesson.difficulty }}">{{ lesson.difficulty | upper }}</span>
  <span class="duration">⏱️ {{ lesson.duration_minutes }} minutes</span>
</div>

---

## 🎯 Learning Objectives

{% for objective in lesson.learning_objectives %}
- [ ] {{ objective }}
{% endfor %}

---

## 📚 Introduction

{{ lesson.content.introduction }}

---

## 💡 Explanation

{{ lesson.content.explanation }}

---

## 👨‍💻 Code Example

**File:** `{{ lesson.content.code_example.filename }}`

```{{ lesson.content.code_example.language }}
{{ lesson.content.code_example.code }}
```

{% if lesson.content.code_example.highlights %}
### 🔍 Key Sections

{% for highlight in lesson.content.code_example.highlights %}
- **Lines {{ highlight.start_line }}-{{ highlight.end_line }}**: {{ highlight.description }}
{% endfor %}
{% endif %}

---

## 🚶 Walkthrough

{{ lesson.content.walkthrough }}

---

## ✅ Summary

{{ lesson.content.summary }}

---

{% if lesson.exercises %}
## 🏋️ Practice Exercises

{% for exercise in lesson.exercises %}
### Exercise {{ loop.index }}: {{ exercise.title }}

**Difficulty:** {{ exercise.difficulty }} | **Time:** {{ exercise.estimated_minutes }} min

{{ exercise.description }}

<details>
<summary>📋 Instructions</summary>

{% for instruction in exercise.instructions %}
{{ loop.index }}. {{ instruction }}
{% endfor %}

</details>

<details>
<summary>💡 Hints</summary>

{% for hint in exercise.hints %}
**Hint {{ loop.index }}:** {{ hint }}

{% endfor %}
</details>

{% endfor %}
{% endif %}

---

{% if lesson.content.further_reading %}
## 📖 Further Reading

{% for reading in lesson.content.further_reading %}
- {{ reading }}
{% endfor %}
{% endif %}
```

### Template Best Practices

1. **Keep templates readable**: Use clear variable names and comments
2. **Handle missing data**: Use `{% if variable %}` checks for optional fields
3. **Use filters**: Apply filters for formatting (upper, lower, round, etc.)
4. **Add visual hierarchy**: Use headings, separators, and whitespace
5. **Include metadata**: Show difficulty, duration, and prerequisites
6. **Make it scannable**: Use lists, tables, and code blocks effectively
7. **Test thoroughly**: Verify templates with various course configurations

---

## Configuration Examples

### Example 1: Beginner-Friendly Course

```python
config = CourseConfig(
    target_audience="beginner",
    course_focus="full-stack",
    author="Your Name",
    version="1.0.0",
    
    # Short, focused lessons
    min_lesson_duration=15,
    max_lesson_duration=30,
    
    # Fewer modules for simplicity
    min_modules=3,
    max_modules=5,
    
    # Minimal exercises
    min_exercises_per_lesson=1,
    max_exercises_per_lesson=2,
    
    # Simple code examples
    max_code_lines=30,
    include_annotations=True,
    
    # Beginner-friendly content
    use_simple_language=True,
    include_glossary=True,
    
    # Only high-quality content
    min_teaching_value=0.7
)
```

### Example 2: Advanced Technical Course

```python
config = CourseConfig(
    target_audience="advanced",
    course_focus="architecture",
    author="Senior Engineer",
    version="2.0.0",
    
    # Longer, in-depth lessons
    min_lesson_duration=45,
    max_lesson_duration=90,
    
    # More modules for comprehensive coverage
    min_modules=6,
    max_modules=10,
    
    # More exercises for practice
    min_exercises_per_lesson=2,
    max_exercises_per_lesson=5,
    
    # Longer code examples
    max_code_lines=100,
    include_annotations=True,
    
    # Technical language
    use_simple_language=False,
    include_glossary=False,
    
    # Include more content
    min_teaching_value=0.4,
    
    # Focus on architecture patterns
    priority_tags=["architecture", "design_patterns", "scalability"]
)
```

### Example 3: Pattern-Focused Course

```python
config = CourseConfig(
    target_audience="intermediate",
    course_focus="patterns",
    author="Pattern Expert",
    
    # Standard lesson length
    min_lesson_duration=30,
    max_lesson_duration=60,
    
    # Moderate number of modules
    min_modules=4,
    max_modules=6,
    
    # Balanced exercises
    min_exercises_per_lesson=2,
    max_exercises_per_lesson=3,
    
    # Focus on pattern examples
    max_code_lines=50,
    include_annotations=True,
    
    # Clear explanations
    use_simple_language=True,
    
    # Prioritize pattern content
    priority_tags=[
        "factory_pattern",
        "singleton_pattern",
        "observer_pattern",
        "strategy_pattern"
    ],
    
    # Exclude non-pattern content
    exclude_tags=["config", "test", "setup"]
)
```

### Example 4: Quick Start Course

```python
config = CourseConfig(
    target_audience="mixed",
    course_focus="best-practices",
    
    # Limit total duration
    max_duration_hours=10.0,
    
    # Short lessons
    min_lesson_duration=15,
    max_lesson_duration=30,
    
    # Compact structure
    min_modules=3,
    max_modules=4,
    
    # Minimal exercises
    min_exercises_per_lesson=1,
    max_exercises_per_lesson=1,
    
    # Concise code examples
    max_code_lines=30,
    
    # Only the best content
    min_teaching_value=0.8
)
```

---

## See Also

- [Course Generator Examples](../examples/course_generator_example.py) - Practical usage examples
- [API Documentation](./COURSE_API.md) - Complete API reference
- [MCP Tools Guide](./COURSE_MCP_TOOLS.md) - Using course generation via MCP
