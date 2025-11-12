"""Unit tests for Template Engine."""

import pytest
import tempfile
import os
from datetime import datetime
from pathlib import Path
from jinja2 import TemplateError

from src.course.template_engine import TemplateEngine
from src.course.config import CourseConfig
from src.course.models import (
    CourseOutline,
    Module,
    Lesson,
    LessonContent,
    CodeExample,
    CodeHighlight,
    Exercise,
    TestCase,
)


# ========== Test Fixtures ==========

@pytest.fixture
def course_config():
    """Create a default course configuration."""
    return CourseConfig(
        target_audience="mixed",
        author="Test Author",
        version="1.0.0",
    )


@pytest.fixture
def custom_template_dir():
    """Create a temporary directory with custom templates."""
    temp_dir = tempfile.mkdtemp()
    
    # Create a simple custom template
    custom_template = """# Custom {{ lesson.title }}
This is a custom template.
"""
    template_path = Path(temp_dir) / "custom_lesson.md.j2"
    template_path.write_text(custom_template)
    
    yield temp_dir
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def code_example():
    """Create a sample code example."""
    return CodeExample(
        code="def hello():\n    print('Hello, World!')",
        language="python",
        filename="hello.py",
        highlights=[
            CodeHighlight(
                start_line=1,
                end_line=1,
                description="Function definition"
            )
        ],
        annotations={
            1: "Function definition",
            2: "Print statement"
        }
    )


@pytest.fixture
def lesson_content(code_example):
    """Create sample lesson content."""
    return LessonContent(
        introduction="This lesson teaches you about functions.",
        explanation="Functions are reusable blocks of code.",
        code_example=code_example,
        walkthrough="Let's walk through this code step by step.",
        summary="You learned about functions!",
        further_reading=["Python Documentation", "Real Python"]
    )


@pytest.fixture
def exercise():
    """Create a sample exercise."""
    return Exercise(
        exercise_id="ex1",
        title="Create a Function",
        description="Practice creating functions",
        difficulty="beginner",
        estimated_minutes=15,
        instructions=["Create a function", "Add a print statement"],
        starter_code="# TODO: Implement function",
        solution_code="def hello():\n    print('Hello!')",
        hints=["Start with def", "Use print()"],
        test_cases=[
            TestCase(
                input="hello()",
                expected_output="Hello!",
                description="Function should print greeting"
            )
        ],
        learning_objectives=["Understand function syntax"]
    )


@pytest.fixture
def lesson(lesson_content, exercise):
    """Create a sample lesson."""
    return Lesson(
        lesson_id="lesson1",
        title="Introduction to Functions",
        description="Learn about Python functions",
        order=1,
        difficulty="beginner",
        duration_minutes=30,
        file_path="hello.py",
        teaching_value=0.85,
        learning_objectives=["Understand functions", "Write basic functions"],
        prerequisites=["Python basics"],
        concepts=["functions", "syntax"],
        content=lesson_content,
        exercises=[exercise],
        tags=["python", "functions"]
    )


@pytest.fixture
def module(lesson):
    """Create a sample module."""
    return Module(
        module_id="mod1",
        title="Python Basics",
        description="Learn Python fundamentals",
        order=1,
        lessons=[lesson],
        difficulty="beginner",
        duration_hours=0.5,
        learning_objectives=["Master Python basics"]
    )


@pytest.fixture
def course(module):
    """Create a sample course."""
    return CourseOutline(
        course_id="course1",
        title="Python Programming Course",
        description="Learn Python from scratch",
        author="Test Author",
        version="1.0.0",
        created_at=datetime(2024, 1, 1, 12, 0, 0),
        modules=[module],
        total_duration_hours=0.5,
        difficulty_distribution={"beginner": 1},
        tags=["python", "programming"],
        prerequisites=["Basic computer skills"]
    )


# ========== Test Template Engine Initialization ==========

def test_template_engine_init(course_config):
    """Test template engine initialization."""
    engine = TemplateEngine(course_config)
    
    assert engine.config == course_config
    assert engine.env is not None


def test_template_engine_default_templates(course_config):
    """Test that default templates are loaded."""
    engine = TemplateEngine(course_config)
    
    templates = engine.list_templates()
    assert "lesson.md.j2" in templates
    assert "exercise.md.j2" in templates
    assert "module.md.j2" in templates
    assert "index.md.j2" in templates


def test_template_engine_custom_template_dir(custom_template_dir):
    """Test loading custom template directory."""
    config = CourseConfig(template_dir=custom_template_dir)
    engine = TemplateEngine(config)
    
    templates = engine.list_templates()
    assert "custom_lesson.md.j2" in templates


# ========== Test Template Validation ==========

def test_validate_template_exists(course_config):
    """Test validating an existing template."""
    engine = TemplateEngine(course_config)
    
    # Should not raise
    assert engine.validate_template("lesson.md.j2") is True


def test_validate_template_not_exists(course_config):
    """Test validating a non-existent template."""
    engine = TemplateEngine(course_config)
    
    with pytest.raises(TemplateError):
        engine.validate_template("nonexistent.md.j2")


def test_validate_all_default_templates(course_config):
    """Test that all default templates are valid."""
    engine = TemplateEngine(course_config)
    
    templates = ["lesson.md.j2", "exercise.md.j2", "module.md.j2", "index.md.j2"]
    for template in templates:
        assert engine.validate_template(template) is True


# ========== Test Custom Filters ==========

def test_slugify_filter(course_config):
    """Test the slugify custom filter."""
    engine = TemplateEngine(course_config)
    
    assert engine._slugify("Hello World") == "hello-world"
    assert engine._slugify("Test_Example") == "test-example"
    assert engine._slugify("Multiple   Spaces") == "multiple---spaces"


def test_format_duration_filter_minutes(course_config):
    """Test format_duration filter for minutes."""
    engine = TemplateEngine(course_config)
    
    assert engine._format_duration(30) == "30 minutes"
    assert engine._format_duration(45) == "45 minutes"


def test_format_duration_filter_hours(course_config):
    """Test format_duration filter for hours."""
    engine = TemplateEngine(course_config)
    
    assert engine._format_duration(60) == "1 hour"
    assert engine._format_duration(120) == "2 hours"


def test_format_duration_filter_mixed(course_config):
    """Test format_duration filter for hours and minutes."""
    engine = TemplateEngine(course_config)
    
    assert engine._format_duration(90) == "1 hour 30 minutes"
    assert engine._format_duration(150) == "2 hours 30 minutes"


# ========== Test Lesson Template Rendering ==========

def test_render_lesson_basic(course_config, lesson):
    """Test basic lesson rendering."""
    engine = TemplateEngine(course_config)
    output = engine.render_lesson(lesson)
    
    assert len(output) > 0
    assert "Introduction to Functions" in output
    assert "Learning Objectives" in output


def test_render_lesson_includes_metadata(course_config, lesson):
    """Test that lesson includes metadata."""
    engine = TemplateEngine(course_config)
    output = engine.render_lesson(lesson)
    
    assert "beginner" in output
    assert "30 minutes" in output


def test_render_lesson_includes_prerequisites(course_config, lesson):
    """Test that lesson includes prerequisites."""
    engine = TemplateEngine(course_config)
    output = engine.render_lesson(lesson)
    
    assert "Prerequisites" in output
    assert "Python basics" in output


def test_render_lesson_includes_code_example(course_config, lesson):
    """Test that lesson includes code example."""
    engine = TemplateEngine(course_config)
    output = engine.render_lesson(lesson)
    
    assert "```python" in output
    assert "def hello():" in output


def test_render_lesson_includes_annotations(course_config, lesson):
    """Test that lesson includes code annotations."""
    engine = TemplateEngine(course_config)
    output = engine.render_lesson(lesson)
    
    assert "Code Annotations" in output
    assert "Line 1" in output
    assert "Function definition" in output


def test_render_lesson_includes_exercises(course_config, lesson):
    """Test that lesson includes exercises."""
    engine = TemplateEngine(course_config)
    output = engine.render_lesson(lesson)
    
    assert "Exercises" in output
    assert "Create a Function" in output
    assert "Starter Code" in output


def test_render_lesson_includes_tags(course_config, lesson):
    """Test that lesson includes tags."""
    engine = TemplateEngine(course_config)
    output = engine.render_lesson(lesson)
    
    assert "Tags" in output
    assert "`python`" in output
    assert "`functions`" in output


# ========== Test Exercise Template Rendering ==========

def test_render_exercise_basic(course_config, exercise):
    """Test basic exercise rendering."""
    engine = TemplateEngine(course_config)
    output = engine.render_exercise(exercise)
    
    assert len(output) > 0
    assert "Create a Function" in output


def test_render_exercise_includes_metadata(course_config, exercise):
    """Test that exercise includes metadata."""
    engine = TemplateEngine(course_config)
    output = engine.render_exercise(exercise)
    
    assert "beginner" in output
    assert "15 minutes" in output


def test_render_exercise_includes_instructions(course_config, exercise):
    """Test that exercise includes instructions."""
    engine = TemplateEngine(course_config)
    output = engine.render_exercise(exercise)
    
    assert "Instructions" in output
    assert "1. Create a function" in output


def test_render_exercise_includes_starter_code(course_config, exercise):
    """Test that exercise includes starter code."""
    engine = TemplateEngine(course_config)
    output = engine.render_exercise(exercise)
    
    assert "Starter Code" in output
    assert "# TODO: Implement function" in output


def test_render_exercise_includes_hints(course_config, exercise):
    """Test that exercise includes hints."""
    engine = TemplateEngine(course_config)
    output = engine.render_exercise(exercise)
    
    assert "Hints" in output
    assert "Hint 1" in output
    assert "Start with def" in output


def test_render_exercise_includes_test_cases(course_config, exercise):
    """Test that exercise includes test cases."""
    engine = TemplateEngine(course_config)
    output = engine.render_exercise(exercise)
    
    assert "Test Cases" in output
    assert "hello()" in output
    assert "Hello!" in output


def test_render_exercise_includes_solution(course_config, exercise):
    """Test that exercise includes solution."""
    engine = TemplateEngine(course_config)
    output = engine.render_exercise(exercise)
    
    assert "Solution" in output
    assert "def hello():" in output


# ========== Test Module Template Rendering ==========

def test_render_module_basic(course_config, module):
    """Test basic module rendering."""
    engine = TemplateEngine(course_config)
    output = engine.render_module(module)
    
    assert len(output) > 0
    assert "Python Basics" in output


def test_render_module_includes_metadata(course_config, module):
    """Test that module includes metadata."""
    engine = TemplateEngine(course_config)
    output = engine.render_module(module)
    
    assert "beginner" in output
    assert "0.5 hours" in output


def test_render_module_includes_objectives(course_config, module):
    """Test that module includes learning objectives."""
    engine = TemplateEngine(course_config)
    output = engine.render_module(module)
    
    assert "Learning Objectives" in output
    assert "Master Python basics" in output


def test_render_module_includes_lessons(course_config, module):
    """Test that module includes lessons."""
    engine = TemplateEngine(course_config)
    output = engine.render_module(module)
    
    assert "Lessons" in output
    assert "Introduction to Functions" in output


def test_render_module_includes_teaching_value(course_config, module):
    """Test that module includes teaching value."""
    engine = TemplateEngine(course_config)
    output = engine.render_module(module)
    
    assert "Teaching Value" in output
    assert "0.85" in output


# ========== Test Index Template Rendering ==========

def test_render_index_basic(course_config, course):
    """Test basic index rendering."""
    engine = TemplateEngine(course_config)
    output = engine.render_index(course)
    
    assert len(output) > 0
    assert "Python Programming Course" in output


def test_render_index_includes_metadata(course_config, course):
    """Test that index includes metadata."""
    engine = TemplateEngine(course_config)
    output = engine.render_index(course)
    
    assert "Test Author" in output
    assert "1.0.0" in output
    assert "2024-01-01" in output


def test_render_index_includes_overview(course_config, course):
    """Test that index includes course overview."""
    engine = TemplateEngine(course_config)
    output = engine.render_index(course)
    
    assert "Course Overview" in output
    assert "Learn Python from scratch" in output


def test_render_index_includes_prerequisites(course_config, course):
    """Test that index includes prerequisites."""
    engine = TemplateEngine(course_config)
    output = engine.render_index(course)
    
    assert "Prerequisites" in output
    assert "Basic computer skills" in output


def test_render_index_includes_difficulty_distribution(course_config, course):
    """Test that index includes difficulty distribution."""
    engine = TemplateEngine(course_config)
    output = engine.render_index(course)
    
    assert "Difficulty Distribution" in output
    assert "Beginner" in output


def test_render_index_includes_modules(course_config, course):
    """Test that index includes modules."""
    engine = TemplateEngine(course_config)
    output = engine.render_index(course)
    
    assert "Course Modules" in output
    assert "Python Basics" in output


def test_render_index_includes_learning_path(course_config, course):
    """Test that index includes learning path."""
    engine = TemplateEngine(course_config)
    output = engine.render_index(course)
    
    assert "Learning Path" in output


def test_render_index_includes_tags(course_config, course):
    """Test that index includes tags."""
    engine = TemplateEngine(course_config)
    output = engine.render_index(course)
    
    assert "Topics Covered" in output
    assert "`python`" in output


# ========== Test Template Rendering Methods ==========

def test_render_template_with_context(course_config):
    """Test rendering template with context."""
    engine = TemplateEngine(course_config)
    
    context = {"lesson": {"title": "Test Lesson"}}
    output = engine.render_string("# {{ lesson.title }}", context)
    
    assert output == "# Test Lesson"


def test_render_string_basic(course_config):
    """Test rendering string template."""
    engine = TemplateEngine(course_config)
    
    output = engine.render_string("Hello {{ name }}!", {"name": "World"})
    assert output == "Hello World!"


def test_render_string_with_filter(course_config):
    """Test rendering string with custom filter."""
    engine = TemplateEngine(course_config)
    
    output = engine.render_string("{{ text|slugify }}", {"text": "Hello World"})
    assert output == "hello-world"


def test_render_template_error_handling(course_config):
    """Test error handling for invalid template."""
    engine = TemplateEngine(course_config)
    
    with pytest.raises(TemplateError):
        engine.render_template("nonexistent.md.j2", {})


def test_render_string_error_handling(course_config):
    """Test error handling for invalid template string."""
    engine = TemplateEngine(course_config)
    
    with pytest.raises(TemplateError):
        engine.render_string("{{ invalid syntax", {})


# ========== Test List Templates ==========

def test_list_templates(course_config):
    """Test listing available templates."""
    engine = TemplateEngine(course_config)
    
    templates = engine.list_templates()
    assert isinstance(templates, list)
    assert len(templates) > 0


# ========== Integration Tests ==========

def test_render_complete_course(course_config, course):
    """Test rendering a complete course with all components."""
    engine = TemplateEngine(course_config)
    
    # Render index
    index_output = engine.render_index(course)
    assert "Python Programming Course" in index_output
    
    # Render module
    module_output = engine.render_module(course.modules[0])
    assert "Python Basics" in module_output
    
    # Render lesson
    lesson_output = engine.render_lesson(course.modules[0].lessons[0])
    assert "Introduction to Functions" in lesson_output
    
    # Render exercise
    exercise_output = engine.render_exercise(course.modules[0].lessons[0].exercises[0])
    assert "Create a Function" in exercise_output


def test_template_consistency(course_config, lesson):
    """Test that templates produce consistent output."""
    engine = TemplateEngine(course_config)
    
    # Render twice
    output1 = engine.render_lesson(lesson)
    output2 = engine.render_lesson(lesson)
    
    # Should be identical
    assert output1 == output2


def test_template_markdown_validity(course_config, lesson):
    """Test that templates produce valid markdown."""
    engine = TemplateEngine(course_config)
    output = engine.render_lesson(lesson)
    
    # Check for markdown elements
    assert "#" in output  # Headers
    assert "**" in output  # Bold
    assert "```" in output  # Code blocks
    assert "-" in output  # Lists
