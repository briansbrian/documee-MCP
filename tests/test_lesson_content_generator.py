"""Unit tests for Lesson Content Generator."""

import pytest
import tempfile
import os
from datetime import datetime
from src.course.content_generator import LessonContentGenerator
from src.course.config import CourseConfig
from src.models import (
    FileAnalysis,
    SymbolInfo,
    DetectedPattern,
    ComplexityMetrics,
    TeachingValueScore,
    FunctionInfo,
    ClassInfo,
    ImportInfo,
)


# ========== Test Fixtures ==========

@pytest.fixture
def course_config():
    """Create a default course configuration."""
    return CourseConfig(
        target_audience="mixed",
        max_code_lines=50,
        include_annotations=True,
        use_simple_language=True
    )


@pytest.fixture
def temp_python_file():
    """Create a temporary Python file for testing."""
    content = '''"""Example module for testing."""

def simple_function(x, y):
    """Add two numbers.
    
    Args:
        x: First number
        y: Second number
        
    Returns:
        Sum of x and y
    """
    return x + y


class ExampleClass:
    """An example class."""
    
    def __init__(self, value):
        """Initialize with a value."""
        self.value = value
    
    def get_value(self):
        """Get the stored value."""
        return self.value
'''
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(content)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def simple_file_analysis(temp_python_file):
    """Create a simple file analysis for testing."""
    return FileAnalysis(
        file_path=temp_python_file,
        language="python",
        symbol_info=SymbolInfo(
            functions=[
                FunctionInfo(
                    name="simple_function",
                    parameters=["x", "y"],
                    return_type="int",
                    docstring="Add two numbers.",
                    start_line=3,
                    end_line=14,
                    complexity=1,
                    is_async=False
                )
            ],
            classes=[
                ClassInfo(
                    name="ExampleClass",
                    methods=[
                        FunctionInfo(
                            name="__init__",
                            parameters=["self", "value"],
                            return_type=None,
                            docstring="Initialize with a value.",
                            start_line=19,
                            end_line=21,
                            complexity=1,
                            is_async=False
                        ),
                        FunctionInfo(
                            name="get_value",
                            parameters=["self"],
                            return_type=None,
                            docstring="Get the stored value.",
                            start_line=23,
                            end_line=25,
                            complexity=1,
                            is_async=False
                        )
                    ],
                    base_classes=[],
                    docstring="An example class.",
                    start_line=17,
                    end_line=25
                )
            ],
            imports=[]
        ),
        patterns=[
            DetectedPattern(
                pattern_type="class_definition",
                file_path=temp_python_file,
                confidence=0.9,
                evidence=["class ExampleClass"],
                line_numbers=[17]
            ),
            DetectedPattern(
                pattern_type="function_definition",
                file_path=temp_python_file,
                confidence=0.85,
                evidence=["def simple_function"],
                line_numbers=[3]
            )
        ],
        complexity_metrics=ComplexityMetrics(
            avg_complexity=1.0,
            max_complexity=1,
            min_complexity=1,
            high_complexity_functions=[],
            trivial_functions=["simple_function"],
            avg_nesting_depth=1.0
        ),
        teaching_value=TeachingValueScore(
            total_score=0.75,
            documentation_score=0.9,
            complexity_score=0.6,
            pattern_score=0.8,
            structure_score=0.7,
            explanation="Good example of basic class and function",
            factors={}
        ),
        documentation_coverage=0.9,
        linter_issues=[],
        has_errors=False,
        errors=[],
        analyzed_at=datetime.now().isoformat(),
        cache_hit=False
    )


@pytest.fixture
def complex_file_analysis(temp_python_file):
    """Create a complex file analysis for testing."""
    return FileAnalysis(
        file_path=temp_python_file,
        language="python",
        symbol_info=SymbolInfo(
            functions=[
                FunctionInfo(
                    name="complex_function",
                    parameters=["x", "y", "z"],
                    return_type="dict",
                    docstring="A complex function with high complexity.",
                    start_line=1,
                    end_line=20,
                    complexity=12,
                    is_async=True
                )
            ],
            classes=[],
            imports=[
                ImportInfo(
                    module="typing",
                    imported_symbols=["Dict", "List"],
                    is_relative=False,
                    import_type="from_import",
                    line_number=1
                )
            ]
        ),
        patterns=[
            DetectedPattern(
                pattern_type="async_pattern",
                file_path=temp_python_file,
                confidence=0.95,
                evidence=["async def", "await"],
                line_numbers=[1, 5, 10]
            ),
            DetectedPattern(
                pattern_type="error_handling",
                file_path=temp_python_file,
                confidence=0.8,
                evidence=["try", "except"],
                line_numbers=[7, 15]
            )
        ],
        complexity_metrics=ComplexityMetrics(
            avg_complexity=12.0,
            max_complexity=12,
            min_complexity=12,
            high_complexity_functions=["complex_function"],
            trivial_functions=[],
            avg_nesting_depth=3.5
        ),
        teaching_value=TeachingValueScore(
            total_score=0.85,
            documentation_score=0.9,
            complexity_score=0.8,
            pattern_score=0.9,
            structure_score=0.8,
            explanation="Advanced async pattern with error handling",
            factors={}
        ),
        documentation_coverage=0.9,
        linter_issues=[],
        has_errors=False,
        errors=[],
        analyzed_at=datetime.now().isoformat(),
        cache_hit=False
    )


# ========== Test Code Example Extraction ==========

def test_extract_code_example_basic(course_config, simple_file_analysis):
    """Test basic code example extraction."""
    generator = LessonContentGenerator(course_config)
    code_example = generator.extract_code_example(simple_file_analysis)
    
    # Verify code example structure
    assert code_example.code is not None
    assert len(code_example.code) > 0
    assert code_example.language == "python"
    assert code_example.filename.endswith(".py")


def test_extract_code_example_language_detection(course_config, simple_file_analysis):
    """Test language detection from file extension."""
    generator = LessonContentGenerator(course_config)
    
    # Test Python
    code_example = generator.extract_code_example(simple_file_analysis)
    assert code_example.language == "python"


def test_extract_code_example_highlights(course_config, simple_file_analysis):
    """Test that code highlights are created."""
    generator = LessonContentGenerator(course_config)
    code_example = generator.extract_code_example(simple_file_analysis)
    
    # Should have highlights for patterns
    assert isinstance(code_example.highlights, list)


def test_extract_code_example_annotations(course_config, simple_file_analysis):
    """Test that annotations are generated."""
    generator = LessonContentGenerator(course_config)
    code_example = generator.extract_code_example(simple_file_analysis)
    
    # Should have annotations dictionary
    assert isinstance(code_example.annotations, dict)


def test_extract_code_example_max_lines(simple_file_analysis):
    """Test that code is limited to max_code_lines."""
    config = CourseConfig(max_code_lines=10)
    generator = LessonContentGenerator(config)
    
    code_example = generator.extract_code_example(simple_file_analysis)
    
    # Code should be limited
    lines = code_example.code.split('\n')
    # Allow some flexibility for truncation message
    assert len(lines) <= 15  # 10 lines + truncation message


# ========== Test Learning Objectives Generation ==========

def test_generate_objectives_count(course_config, simple_file_analysis):
    """Test that 3-5 objectives are generated."""
    generator = LessonContentGenerator(course_config)
    objectives = generator.generate_objectives(simple_file_analysis)
    
    # Should have 3-5 objectives (Req 2.2)
    assert 3 <= len(objectives) <= 5


def test_generate_objectives_from_patterns(course_config, simple_file_analysis):
    """Test that objectives are generated from patterns."""
    generator = LessonContentGenerator(course_config)
    objectives = generator.generate_objectives(simple_file_analysis)
    
    # Should include objectives based on patterns
    assert len(objectives) > 0
    # Objectives should be strings
    for obj in objectives:
        assert isinstance(obj, str)
        assert len(obj) > 0


def test_generate_objectives_action_verbs(course_config, simple_file_analysis):
    """Test that objectives use action verbs."""
    generator = LessonContentGenerator(course_config)
    objectives = generator.generate_objectives(simple_file_analysis)
    
    # Check for action verbs (Req 7.3)
    action_verbs = ["understand", "implement", "apply", "analyze", "master"]
    
    has_action_verb = False
    for obj in objectives:
        obj_lower = obj.lower()
        if any(verb in obj_lower for verb in action_verbs):
            has_action_verb = True
            break
    
    assert has_action_verb, "Objectives should use action verbs"


def test_generate_objectives_complex_code(course_config, complex_file_analysis):
    """Test objectives for complex code."""
    generator = LessonContentGenerator(course_config)
    objectives = generator.generate_objectives(complex_file_analysis)
    
    # Should have objectives
    assert len(objectives) >= 3
    
    # Should mention complexity or advanced concepts
    objectives_text = " ".join(objectives).lower()
    assert "complexity" in objectives_text or "advanced" in objectives_text or "async" in objectives_text


# ========== Test Introduction Generation ==========

def test_generate_introduction_basic(course_config, simple_file_analysis):
    """Test basic introduction generation."""
    generator = LessonContentGenerator(course_config)
    objectives = generator.generate_objectives(simple_file_analysis)
    introduction = generator.generate_introduction(simple_file_analysis, objectives)
    
    # Should have content
    assert len(introduction) > 0
    
    # Should mention objectives
    assert "learn" in introduction.lower() or "understand" in introduction.lower()


def test_generate_introduction_includes_patterns(course_config, simple_file_analysis):
    """Test that introduction mentions patterns."""
    generator = LessonContentGenerator(course_config)
    objectives = generator.generate_objectives(simple_file_analysis)
    introduction = generator.generate_introduction(simple_file_analysis, objectives)
    
    # Should mention patterns
    intro_lower = introduction.lower()
    assert "class" in intro_lower or "function" in intro_lower


def test_generate_introduction_includes_objectives(course_config, simple_file_analysis):
    """Test that introduction lists objectives."""
    generator = LessonContentGenerator(course_config)
    objectives = generator.generate_objectives(simple_file_analysis)
    introduction = generator.generate_introduction(simple_file_analysis, objectives)
    
    # Should include at least one objective
    for obj in objectives:
        if obj in introduction:
            return
    
    # Or should mention "able to"
    assert "able to" in introduction.lower()


# ========== Test Explanation Generation ==========

def test_generate_explanation_basic(course_config, simple_file_analysis):
    """Test basic explanation generation."""
    generator = LessonContentGenerator(course_config)
    explanation = generator.generate_explanation(simple_file_analysis)
    
    # Should have content
    assert len(explanation) > 0
    
    # Should use markdown headers
    assert "##" in explanation


def test_generate_explanation_describes_code(course_config, simple_file_analysis):
    """Test that explanation describes the code."""
    generator = LessonContentGenerator(course_config)
    explanation = generator.generate_explanation(simple_file_analysis)
    
    # Should mention class or function
    explanation_lower = explanation.lower()
    assert "class" in explanation_lower or "function" in explanation_lower


def test_generate_explanation_simple_language(course_config, simple_file_analysis):
    """Test that explanation uses simple language."""
    generator = LessonContentGenerator(course_config)
    explanation = generator.generate_explanation(simple_file_analysis)
    
    # Should not be overly technical (basic check)
    assert len(explanation) > 0
    # Should have readable sentences
    assert "." in explanation


def test_generate_explanation_complexity_note(course_config, complex_file_analysis):
    """Test that explanation notes high complexity."""
    generator = LessonContentGenerator(course_config)
    explanation = generator.generate_explanation(complex_file_analysis)
    
    # Should mention complexity
    explanation_lower = explanation.lower()
    assert "complexity" in explanation_lower


# ========== Test Walkthrough Generation ==========

def test_generate_walkthrough_basic(course_config, simple_file_analysis):
    """Test basic walkthrough generation."""
    generator = LessonContentGenerator(course_config)
    code_example = generator.extract_code_example(simple_file_analysis)
    walkthrough = generator.generate_walkthrough(code_example, simple_file_analysis)
    
    # Should have content
    assert len(walkthrough) > 0
    
    # Should use markdown headers
    assert "##" in walkthrough


def test_generate_walkthrough_describes_classes(course_config, simple_file_analysis):
    """Test that walkthrough describes classes."""
    generator = LessonContentGenerator(course_config)
    code_example = generator.extract_code_example(simple_file_analysis)
    walkthrough = generator.generate_walkthrough(code_example, simple_file_analysis)
    
    # Should mention the class
    assert "ExampleClass" in walkthrough or "class" in walkthrough.lower()


def test_generate_walkthrough_describes_functions(course_config, simple_file_analysis):
    """Test that walkthrough describes functions."""
    generator = LessonContentGenerator(course_config)
    code_example = generator.extract_code_example(simple_file_analysis)
    walkthrough = generator.generate_walkthrough(code_example, simple_file_analysis)
    
    # Should mention functions
    walkthrough_lower = walkthrough.lower()
    assert "function" in walkthrough_lower or "method" in walkthrough_lower


def test_generate_walkthrough_includes_annotations(course_config, simple_file_analysis):
    """Test that walkthrough includes code annotations."""
    generator = LessonContentGenerator(course_config)
    code_example = generator.extract_code_example(simple_file_analysis)
    
    # Add some annotations
    code_example.annotations[10] = "Test annotation"
    
    walkthrough = generator.generate_walkthrough(code_example, simple_file_analysis)
    
    # Should include annotation section if annotations exist
    if code_example.annotations:
        assert "Line" in walkthrough or "annotation" in walkthrough.lower()


# ========== Test Summary Generation ==========

def test_generate_summary_basic(course_config, simple_file_analysis):
    """Test basic summary generation."""
    generator = LessonContentGenerator(course_config)
    objectives = generator.generate_objectives(simple_file_analysis)
    summary = generator.generate_summary(objectives, simple_file_analysis)
    
    # Should have content
    assert len(summary) > 0
    
    # Should use markdown headers
    assert "##" in summary


def test_generate_summary_recaps_objectives(course_config, simple_file_analysis):
    """Test that summary recaps objectives."""
    generator = LessonContentGenerator(course_config)
    objectives = generator.generate_objectives(simple_file_analysis)
    summary = generator.generate_summary(objectives, simple_file_analysis)
    
    # Should mention learning
    summary_lower = summary.lower()
    assert "learned" in summary_lower or "learn" in summary_lower


def test_generate_summary_includes_takeaways(course_config, simple_file_analysis):
    """Test that summary includes key takeaways."""
    generator = LessonContentGenerator(course_config)
    objectives = generator.generate_objectives(simple_file_analysis)
    summary = generator.generate_summary(objectives, simple_file_analysis)
    
    # Should have takeaways section
    assert "takeaway" in summary.lower() or "key" in summary.lower()


def test_generate_summary_includes_next_steps(course_config, simple_file_analysis):
    """Test that summary includes next steps."""
    generator = LessonContentGenerator(course_config)
    objectives = generator.generate_objectives(simple_file_analysis)
    summary = generator.generate_summary(objectives, simple_file_analysis)
    
    # Should have next steps
    summary_lower = summary.lower()
    assert "next" in summary_lower or "practice" in summary_lower


# ========== Integration Test ==========

def test_generate_lesson_content_complete(course_config, simple_file_analysis):
    """Test complete lesson content generation."""
    generator = LessonContentGenerator(course_config)
    lesson_content = generator.generate_lesson_content(simple_file_analysis)
    
    # Verify all sections are present
    assert lesson_content.introduction is not None
    assert len(lesson_content.introduction) > 0
    
    assert lesson_content.explanation is not None
    assert len(lesson_content.explanation) > 0
    
    assert lesson_content.code_example is not None
    assert lesson_content.code_example.code is not None
    
    assert lesson_content.walkthrough is not None
    assert len(lesson_content.walkthrough) > 0
    
    assert lesson_content.summary is not None
    assert len(lesson_content.summary) > 0
    
    assert isinstance(lesson_content.further_reading, list)


def test_generate_lesson_content_structure(course_config, simple_file_analysis):
    """Test that lesson content has proper structure."""
    generator = LessonContentGenerator(course_config)
    lesson_content = generator.generate_lesson_content(simple_file_analysis)
    
    # Verify structure (Req 2.4)
    # Should have introduction, explanation, code walkthrough, summary
    assert "##" in lesson_content.explanation  # Has sections
    assert "##" in lesson_content.walkthrough  # Has sections
    assert "##" in lesson_content.summary  # Has sections


def test_generate_lesson_content_markdown_format(course_config, simple_file_analysis):
    """Test that content is in Markdown format."""
    generator = LessonContentGenerator(course_config)
    lesson_content = generator.generate_lesson_content(simple_file_analysis)
    
    # Check for markdown elements (Req 2.5)
    all_content = (
        lesson_content.introduction +
        lesson_content.explanation +
        lesson_content.walkthrough +
        lesson_content.summary
    )
    
    # Should have markdown headers
    assert "#" in all_content
    
    # Should have lists
    assert "-" in all_content or "*" in all_content
