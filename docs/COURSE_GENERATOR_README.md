# Course Generator Documentation

Welcome to the Course Generator documentation! This guide will help you get started with creating educational courses from your codebase.

## Quick Links

- **[Usage Examples](../examples/course_generator_example.py)** - Practical code examples
- **[Configuration Guide](./COURSE_CONFIGURATION.md)** - Complete configuration reference
- **[API Documentation](./COURSE_API.md)** - Full API reference

## What is the Course Generator?

The Course Generator transforms codebase analysis results into structured educational courses. It automatically:

- Creates course outlines with modules and lessons
- Generates lesson content with code examples and explanations
- Creates coding exercises with starter code and solutions
- Exports to multiple formats (MkDocs, JSON, Markdown, Next.js)

## Quick Start

### 1. Basic Course Generation

```python
import asyncio
from src.course.config import CourseConfig
from src.course.structure_generator import CourseStructureGenerator
from src.cache.cache_manager import CacheManager

async def generate_course():
    # Load analysis from cache
    cache_manager = CacheManager()
    analysis = await cache_manager.get_analysis("my_project")
    
    # Configure course generation
    config = CourseConfig(
        target_audience="intermediate",
        course_focus="full-stack",
        author="Your Name"
    )
    
    # Generate course structure
    generator = CourseStructureGenerator(config)
    course = await generator.generate_course_structure(analysis)
    
    print(f"Generated: {course.title}")
    print(f"Modules: {len(course.modules)}")
    print(f"Duration: {course.total_duration_hours:.1f} hours")

asyncio.run(generate_course())
```

### 2. Export to MkDocs

```python
from src.course.exporters.mkdocs_exporter import MkDocsExporter

# Export course
exporter = MkDocsExporter(config)
await exporter.export(course, "output/my_course")

# Preview the course
# cd output/my_course
# mkdocs serve
```

### 3. Generate Lesson Content

```python
from src.course.content_generator import LessonContentGenerator

# Generate content for a lesson
content_generator = LessonContentGenerator(config)

for module in course.modules:
    for lesson in module.lessons:
        file_analysis = analysis.file_analyses.get(lesson.file_path)
        if file_analysis:
            lesson.content = await content_generator.generate_lesson_content(file_analysis)
```

## Key Features

### 🎯 Intelligent Course Structure

- Automatically organizes content into 3-8 modules
- Groups lessons by related patterns and concepts
- Orders lessons by difficulty and prerequisites
- Estimates duration based on complexity

### 📚 Rich Lesson Content

- Introduction with learning objectives
- Detailed explanations in simple language
- Code examples with syntax highlighting
- Step-by-step walkthroughs
- Summary and further reading

### 🏋️ Hands-On Exercises

- Starter code with TODO comments
- Step-by-step instructions
- Progressive hints
- Test cases for validation
- Complete solutions

### 📤 Multiple Export Formats

- **MkDocs**: Professional course websites
- **JSON**: Machine-readable data
- **Markdown**: Portable documentation
- **Next.js**: Interactive web apps
- **PDF**: Printable documents

## Configuration Options

The Course Generator is highly configurable. Here are the most common settings:

```python
config = CourseConfig(
    # Audience
    target_audience="intermediate",  # beginner, intermediate, advanced, mixed
    
    # Focus
    course_focus="full-stack",  # patterns, architecture, best-practices, full-stack
    
    # Duration
    max_duration_hours=20.0,
    min_lesson_duration=15,
    max_lesson_duration=60,
    
    # Exercises
    min_exercises_per_lesson=1,
    max_exercises_per_lesson=3,
    
    # Content
    use_simple_language=True,
    include_annotations=True,
    max_code_lines=50,
    
    # Filtering
    min_teaching_value=0.6,
    priority_tags=["react", "api"],
    exclude_tags=["test", "config"]
)
```

See [Configuration Guide](./COURSE_CONFIGURATION.md) for all options.

## Common Use Cases

### Use Case 1: Onboarding New Developers

Create a beginner-friendly course to help new team members learn your codebase:

```python
config = CourseConfig(
    target_audience="beginner",
    course_focus="full-stack",
    max_duration_hours=10.0,
    use_simple_language=True,
    min_teaching_value=0.7
)
```

### Use Case 2: Architecture Documentation

Generate a course focused on system architecture:

```python
config = CourseConfig(
    target_audience="intermediate",
    course_focus="architecture",
    priority_tags=["architecture", "design_patterns", "scalability"],
    exclude_tags=["test", "config"]
)
```

### Use Case 3: Best Practices Training

Create a course highlighting coding best practices:

```python
config = CourseConfig(
    target_audience="mixed",
    course_focus="best-practices",
    priority_tags=["error_handling", "security", "testing"],
    max_exercises_per_lesson=3
)
```

### Use Case 4: Pattern Library

Build a comprehensive pattern reference:

```python
config = CourseConfig(
    target_audience="advanced",
    course_focus="patterns",
    priority_tags=[
        "factory_pattern",
        "singleton_pattern",
        "observer_pattern"
    ]
)
```

## Examples

The [examples directory](../examples/course_generator_example.py) contains complete working examples:

1. **Export Course to MkDocs** - Generate and export a complete course
2. **Generate Lesson Outline** - Create a lesson from a single file
3. **Create Exercise** - Generate a coding exercise from a pattern
4. **Custom Templates** - Use custom Jinja2 templates
5. **Multiple Formats** - Export to multiple formats at once

Run the examples:

```bash
.\venv\Scripts\python.exe examples\course_generator_example.py
```

## Documentation Structure

```
docs/
├── COURSE_GENERATOR_README.md     # This file - overview and quick start
├── COURSE_CONFIGURATION.md        # Complete configuration reference
└── COURSE_API.md                  # Full API documentation

examples/
└── course_generator_example.py    # Working code examples
```

## Workflow

Here's the typical workflow for generating a course:

```
1. Analyze Codebase
   ↓
2. Configure Course Generation
   ↓
3. Generate Course Structure
   ↓
4. Generate Lesson Content
   ↓
5. Generate Exercises
   ↓
6. Export to Format(s)
   ↓
7. Review and Customize
```

## Performance

The Course Generator is optimized for speed:

- **Course outline**: < 5 seconds for 100 files
- **Single lesson**: < 2 seconds
- **Exercises**: < 3 seconds per lesson
- **MkDocs export**: < 10 seconds for 20 lessons

Caching is used to avoid regenerating unchanged content.

## Customization

### Custom Templates

Create custom Jinja2 templates for complete control over output:

```python
config = CourseConfig(template_dir="my_templates")
```

See [Configuration Guide](./COURSE_CONFIGURATION.md#template-customization) for details.

### Content Filtering

Filter content by teaching value, tags, and patterns:

```python
config = CourseConfig(
    min_teaching_value=0.7,
    priority_tags=["important", "core"],
    exclude_tags=["deprecated", "experimental"]
)
```

### Audience Targeting

Adjust content complexity for different audiences:

```python
# Beginner course
config = CourseConfig(
    target_audience="beginner",
    use_simple_language=True,
    max_code_lines=30
)

# Advanced course
config = CourseConfig(
    target_audience="advanced",
    use_simple_language=False,
    max_code_lines=100
)
```

## Troubleshooting

### Issue: No lessons generated

**Solution**: Lower the `min_teaching_value` threshold:

```python
config = CourseConfig(min_teaching_value=0.3)
```

### Issue: Course too long

**Solution**: Set `max_duration_hours`:

```python
config = CourseConfig(max_duration_hours=10.0)
```

### Issue: Template not found

**Solution**: Check `template_dir` path:

```python
from pathlib import Path

template_dir = Path("my_templates")
if not template_dir.exists():
    template_dir.mkdir()

config = CourseConfig(template_dir=str(template_dir))
```

### Issue: Export fails

**Solution**: Ensure output directory is writable:

```python
from pathlib import Path

output_dir = Path("output/course")
output_dir.mkdir(parents=True, exist_ok=True)
```

## Best Practices

1. **Start with defaults**: Use default configuration first, then customize
2. **Filter content**: Use `min_teaching_value` to focus on quality content
3. **Target audience**: Set `target_audience` to match your users
4. **Test exports**: Try different export formats to find what works best
5. **Customize templates**: Create custom templates for branding
6. **Cache results**: Use caching to speed up regeneration
7. **Review output**: Always review generated content before publishing

## Next Steps

1. **Read the examples**: Check out [course_generator_example.py](../examples/course_generator_example.py)
2. **Explore configuration**: See [COURSE_CONFIGURATION.md](./COURSE_CONFIGURATION.md)
3. **Learn the API**: Read [COURSE_API.md](./COURSE_API.md)
4. **Generate your first course**: Follow the Quick Start above
5. **Customize**: Adjust configuration and templates to your needs

## Support

For issues or questions:

1. Check the [API Documentation](./COURSE_API.md)
2. Review the [examples](../examples/course_generator_example.py)
3. Read the [Configuration Guide](./COURSE_CONFIGURATION.md)

## Version

Course Generator v1.0.0

Last updated: November 13, 2025
