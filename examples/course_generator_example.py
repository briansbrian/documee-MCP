"""
Course Generator Usage Examples

This file demonstrates how to use the Course Generator to create educational
courses from codebase analysis results.

Examples:
1. Export course to MkDocs
2. Generate lesson outline
3. Create exercise
4. Custom templates
"""

import asyncio
from pathlib import Path
from src.models import CodebaseAnalysis
from src.course.config import CourseConfig
from src.course.structure_generator import CourseStructureGenerator
from src.course.content_generator import LessonContentGenerator
from src.course.exercise_generator import ExerciseGenerator
from src.course.exporters.mkdocs_exporter import MkDocsExporter
from src.course.exporters.export_manager import ExportManager


# ============================================================================
# Example 1: Export Course to MkDocs
# ============================================================================

async def example_export_to_mkdocs():
    """Example: Export a complete course to MkDocs format."""
    print("=" * 70)
    print("Example 1: Export Course to MkDocs")
    print("=" * 70)
    
    # Step 1: Load analysis results (assuming you have a cached analysis)
    from src.cache.cache_manager import CacheManager
    
    cache_manager = CacheManager()
    codebase_id = "my_project"
    
    # Get analysis from cache
    analysis = await cache_manager.get_analysis(codebase_id)
    if not analysis:
        print(f"No analysis found for {codebase_id}. Run analysis first.")
        return
    
    # Step 2: Configure course generation
    config = CourseConfig(
        target_audience="intermediate",
        course_focus="full-stack",
        author="Your Name",
        version="1.0.0",
        max_duration_hours=20.0,
        min_teaching_value=0.6
    )
    
    # Step 3: Generate course structure
    structure_generator = CourseStructureGenerator(config)
    course_outline = await structure_generator.generate_course_structure(analysis)
    
    print(f"\nGenerated course: {course_outline.title}")
    print(f"Modules: {len(course_outline.modules)}")
    print(f"Total duration: {course_outline.total_duration_hours:.1f} hours")
    
    # Step 4: Generate content for each lesson
    content_generator = LessonContentGenerator(config)
    exercise_generator = ExerciseGenerator(config)
    
    for module in course_outline.modules:
        print(f"\nModule {module.order + 1}: {module.title}")
        for lesson in module.lessons:
            # Generate lesson content
            file_analysis = analysis.file_analyses.get(lesson.file_path)
            if file_analysis:
                lesson.content = await content_generator.generate_lesson_content(file_analysis)
                lesson.exercises = await exercise_generator.generate_exercises_for_lesson(
                    file_analysis,
                    max_exercises=config.max_exercises_per_lesson
                )
                print(f"  - {lesson.title} ({lesson.duration_minutes} min, {len(lesson.exercises)} exercises)")
    
    # Step 5: Export to MkDocs
    output_dir = Path("output/mkdocs_course")
    exporter = MkDocsExporter(config)
    await exporter.export(course_outline, str(output_dir))
    
    print(f"\n✓ Course exported to: {output_dir}")
    print(f"  Run 'mkdocs serve' in {output_dir} to preview the course")


# ============================================================================
# Example 2: Generate Lesson Outline
# ============================================================================

async def example_generate_lesson_outline():
    """Example: Generate a lesson outline for a specific file."""
    print("\n" + "=" * 70)
    print("Example 2: Generate Lesson Outline")
    print("=" * 70)
    
    # Step 1: Analyze a specific file
    from src.analysis.analysis_engine import AnalysisEngine
    
    file_path = "src/course/structure_generator.py"
    
    engine = AnalysisEngine()
    file_analysis = await engine.analyze_file(file_path)
    
    if not file_analysis:
        print(f"Could not analyze {file_path}")
        return
    
    # Step 2: Configure for lesson generation
    config = CourseConfig(
        target_audience="intermediate",
        use_simple_language=True,
        include_annotations=True
    )
    
    # Step 3: Generate lesson content
    content_generator = LessonContentGenerator(config)
    lesson_content = await content_generator.generate_lesson_content(file_analysis)
    
    # Step 4: Display lesson outline
    print(f"\nLesson: {Path(file_path).stem.replace('_', ' ').title()}")
    print(f"File: {file_path}")
    print(f"Language: {lesson_content.code_example.language}")
    
    print("\n## Learning Objectives:")
    objectives = content_generator.generate_objectives(file_analysis)
    for i, obj in enumerate(objectives, 1):
        print(f"{i}. {obj}")
    
    print("\n## Introduction:")
    print(lesson_content.introduction[:200] + "...")
    
    print("\n## Code Highlights:")
    for highlight in lesson_content.code_example.highlights[:3]:
        print(f"  Lines {highlight.start_line}-{highlight.end_line}: {highlight.description}")
    
    print("\n## Annotations:")
    for line_num, annotation in list(lesson_content.code_example.annotations.items())[:3]:
        print(f"  Line {line_num}: {annotation}")


# ============================================================================
# Example 3: Create Exercise
# ============================================================================

async def example_create_exercise():
    """Example: Create a coding exercise from a pattern."""
    print("\n" + "=" * 70)
    print("Example 3: Create Exercise")
    print("=" * 70)
    
    # Step 1: Analyze a file to find patterns
    from src.analysis.analysis_engine import AnalysisEngine
    
    file_path = "src/course/exercise_generator.py"
    
    engine = AnalysisEngine()
    file_analysis = await engine.analyze_file(file_path)
    
    if not file_analysis or not file_analysis.patterns:
        print(f"No patterns found in {file_path}")
        return
    
    # Step 2: Select a pattern
    pattern = file_analysis.patterns[0]
    print(f"\nPattern: {pattern.pattern_type}")
    print(f"Confidence: {pattern.confidence:.2f}")
    print(f"Evidence: {', '.join(pattern.evidence[:3])}")
    
    # Step 3: Generate exercise
    config = CourseConfig(
        target_audience="intermediate",
        max_exercises_per_lesson=3
    )
    
    exercise_generator = ExerciseGenerator(config)
    exercise = await exercise_generator.generate_exercise(pattern, file_analysis)
    
    # Step 4: Display exercise details
    print(f"\n## Exercise: {exercise.title}")
    print(f"Difficulty: {exercise.difficulty}")
    print(f"Estimated time: {exercise.estimated_minutes} minutes")
    
    print("\n## Instructions:")
    for i, instruction in enumerate(exercise.instructions, 1):
        print(f"{i}. {instruction}")
    
    print("\n## Starter Code Preview:")
    starter_lines = exercise.starter_code.split('\n')[:15]
    print('\n'.join(starter_lines))
    if len(exercise.starter_code.split('\n')) > 15:
        print("... (truncated)")
    
    print(f"\n## Hints: {len(exercise.hints)} available")
    print(f"## Test Cases: {len(exercise.test_cases)} provided")


# ============================================================================
# Example 4: Custom Templates
# ============================================================================

async def example_custom_templates():
    """Example: Use custom templates for course generation."""
    print("\n" + "=" * 70)
    print("Example 4: Custom Templates")
    print("=" * 70)
    
    # Step 1: Create custom template directory
    template_dir = Path("custom_templates")
    template_dir.mkdir(exist_ok=True)
    
    # Step 2: Create a custom lesson template
    custom_lesson_template = """# {{ lesson.title }}

> **Level:** {{ lesson.difficulty | upper }} | **Duration:** {{ lesson.duration_minutes }} minutes

---

## 🎯 What You'll Learn

{% for objective in lesson.learning_objectives %}
{{ loop.index }}. {{ objective }}
{% endfor %}

---

## 📖 Introduction

{{ lesson.content.introduction }}

---

## 💡 Key Concepts

{{ lesson.content.explanation }}

---

## 🔍 Code Deep Dive

```{{ lesson.content.code_example.language }}
{{ lesson.content.code_example.code }}
```

{{ lesson.content.walkthrough }}

---

## ✅ Summary

{{ lesson.content.summary }}

---

## 🏋️ Practice Exercises

{% for exercise in lesson.exercises %}
### Exercise {{ loop.index }}: {{ exercise.title }}

**Difficulty:** {{ exercise.difficulty }} | **Time:** {{ exercise.estimated_minutes }} min

{{ exercise.description }}

<details>
<summary>View Instructions</summary>

{% for instruction in exercise.instructions %}
{{ loop.index }}. {{ instruction }}
{% endfor %}

</details>

{% endfor %}

---

**Next:** Continue to the next lesson to build on these concepts!
"""
    
    # Save custom template
    lesson_template_path = template_dir / "lesson.md.j2"
    lesson_template_path.write_text(custom_lesson_template)
    
    print(f"\n✓ Created custom lesson template: {lesson_template_path}")
    
    # Step 3: Configure course generation with custom templates
    config = CourseConfig(
        target_audience="beginner",
        template_dir=str(template_dir),
        author="Custom Course Creator",
        use_simple_language=True
    )
    
    print(f"\n✓ Configured to use custom templates from: {template_dir}")
    print("\nCustom template features:")
    print("  - Emoji icons for visual appeal")
    print("  - Collapsible exercise instructions")
    print("  - Enhanced formatting with separators")
    print("  - Beginner-friendly language")
    
    # Step 4: Generate a sample lesson with custom template
    from src.analysis.analysis_engine import AnalysisEngine
    
    file_path = "src/course/models.py"
    engine = AnalysisEngine()
    file_analysis = await engine.analyze_file(file_path)
    
    if file_analysis:
        content_generator = LessonContentGenerator(config)
        lesson_content = await content_generator.generate_lesson_content(file_analysis)
        
        # Use template engine to render with custom template
        from src.course.template_engine import TemplateEngine
        
        template_engine = TemplateEngine(config)
        
        # Create a sample lesson object
        from src.course.models import Lesson
        lesson = Lesson(
            lesson_id="sample",
            title="Understanding Data Models",
            description="Learn about course data structures",
            order=0,
            difficulty="beginner",
            duration_minutes=30,
            file_path=file_path,
            teaching_value=0.8,
            learning_objectives=content_generator.generate_objectives(file_analysis),
            content=lesson_content,
            exercises=[]
        )
        
        # Render with custom template
        rendered = template_engine.render_template("lesson.md.j2", lesson=lesson)
        
        # Save sample output
        output_path = Path("output/custom_template_sample.md")
        output_path.parent.mkdir(exist_ok=True)
        output_path.write_text(rendered)
        
        print(f"\n✓ Generated sample lesson with custom template: {output_path}")


# ============================================================================
# Example 5: Export to Multiple Formats
# ============================================================================

async def example_export_multiple_formats():
    """Example: Export course to multiple formats."""
    print("\n" + "=" * 70)
    print("Example 5: Export to Multiple Formats")
    print("=" * 70)
    
    # Step 1: Load or generate course outline
    from src.cache.cache_manager import CacheManager
    
    cache_manager = CacheManager()
    codebase_id = "my_project"
    analysis = await cache_manager.get_analysis(codebase_id)
    
    if not analysis:
        print(f"No analysis found for {codebase_id}")
        return
    
    config = CourseConfig(
        target_audience="mixed",
        course_focus="full-stack"
    )
    
    structure_generator = CourseStructureGenerator(config)
    course_outline = await structure_generator.generate_course_structure(analysis)
    
    # Step 2: Export to multiple formats
    export_manager = ExportManager(config)
    output_base = Path("output/multi_format")
    
    formats = ["mkdocs", "json", "markdown"]
    
    for format_type in formats:
        output_dir = output_base / format_type
        print(f"\nExporting to {format_type}...")
        
        try:
            await export_manager.export(course_outline, str(output_dir), format_type)
            print(f"  ✓ Exported to: {output_dir}")
        except Exception as e:
            print(f"  ✗ Failed: {e}")
    
    print(f"\n✓ All exports complete in: {output_base}")


# ============================================================================
# Main: Run All Examples
# ============================================================================

async def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("COURSE GENERATOR USAGE EXAMPLES")
    print("=" * 70)
    
    # Run examples
    try:
        # Example 1: Export to MkDocs (requires existing analysis)
        # await example_export_to_mkdocs()
        
        # Example 2: Generate lesson outline
        await example_generate_lesson_outline()
        
        # Example 3: Create exercise
        await example_create_exercise()
        
        # Example 4: Custom templates
        await example_custom_templates()
        
        # Example 5: Multiple formats (requires existing analysis)
        # await example_export_multiple_formats()
        
    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("Examples complete!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
