"""Tests for Course Configuration and Filtering."""

import pytest
from src.course.config import CourseConfig
from src.course.structure_generator import CourseStructureGenerator
from src.models import (
    FileAnalysis, ComplexityMetrics, SymbolInfo, 
    TeachingValueScore, DetectedPattern
)


def create_teaching_value(score=0.7):
    """Helper to create TeachingValueScore."""
    return TeachingValueScore(
        total_score=score,
        documentation_score=0.5,
        complexity_score=0.6,
        pattern_score=0.8,
        structure_score=0.7,
        explanation="Good example"
    )


def create_complexity_metrics():
    """Helper to create ComplexityMetrics."""
    return ComplexityMetrics(
        avg_complexity=3.0,
        max_complexity=5,
        min_complexity=1,
        high_complexity_functions=[],
        trivial_functions=[],
        avg_nesting_depth=2.0
    )


@pytest.fixture
def basic_config():
    """Create a basic course configuration."""
    return CourseConfig(
        target_audience="mixed",
        course_focus="full-stack",
        author="Test Author"
    )


@pytest.fixture
def beginner_config():
    """Create a beginner-focused configuration."""
    return CourseConfig(
        target_audience="beginner",
        course_focus="best-practices",
        author="Test Author"
    )


@pytest.fixture
def advanced_config():
    """Create an advanced-focused configuration."""
    return CourseConfig(
        target_audience="advanced",
        course_focus="patterns",
        author="Test Author"
    )


@pytest.fixture
def sample_file_analysis():
    """Create a sample file analysis."""
    from datetime import datetime
    return FileAnalysis(
        file_path="test.py",
        language="python",
        complexity_metrics=create_complexity_metrics(),
        symbol_info=SymbolInfo(
            functions=[],
            classes=[],
            imports=[]
        ),
        patterns=[
            DetectedPattern(
                pattern_type="factory_pattern",
                file_path="test.py",
                confidence=0.8,
                evidence=["Factory method"],
                line_numbers=[10, 20]
            )
        ],
        teaching_value=create_teaching_value(),
        documentation_coverage=0.5,
        linter_issues=[],
        has_errors=False,
        errors=[],
        analyzed_at=datetime.now().isoformat(),
        cache_hit=False
    )


# ========== Test CourseConfig Validation ==========

def test_config_validation_valid(basic_config):
    """Test that valid configuration passes validation."""
    assert basic_config.validate() is True


def test_config_validation_invalid_audience():
    """Test that invalid audience raises error."""
    config = CourseConfig(target_audience="invalid")
    with pytest.raises(ValueError, match="target_audience must be one of"):
        config.validate()


def test_config_validation_invalid_focus():
    """Test that invalid focus raises error."""
    config = CourseConfig(course_focus="invalid")
    with pytest.raises(ValueError, match="course_focus must be one of"):
        config.validate()


def test_config_validation_invalid_modules():
    """Test that invalid module range raises error."""
    config = CourseConfig(min_modules=10, max_modules=5)
    with pytest.raises(ValueError, match="min_modules cannot be greater than max_modules"):
        config.validate()


# ========== Test Audience Filtering ==========

def test_should_include_for_beginner_audience():
    """Test lesson inclusion for beginner audience."""
    config = CourseConfig(target_audience="beginner")
    generator = CourseStructureGenerator(config)
    
    # Beginners should see beginner and intermediate
    assert generator._should_include_for_audience("beginner") is True
    assert generator._should_include_for_audience("intermediate") is True
    assert generator._should_include_for_audience("advanced") is False


def test_should_include_for_advanced_audience():
    """Test lesson inclusion for advanced audience."""
    config = CourseConfig(target_audience="advanced")
    generator = CourseStructureGenerator(config)
    
    # Advanced should see intermediate and advanced
    assert generator._should_include_for_audience("beginner") is False
    assert generator._should_include_for_audience("intermediate") is True
    assert generator._should_include_for_audience("advanced") is True


def test_should_include_for_mixed_audience():
    """Test lesson inclusion for mixed audience."""
    config = CourseConfig(target_audience="mixed")
    generator = CourseStructureGenerator(config)
    
    # Mixed should see all levels
    assert generator._should_include_for_audience("beginner") is True
    assert generator._should_include_for_audience("intermediate") is True
    assert generator._should_include_for_audience("advanced") is True


def test_adjust_content_complexity_for_beginners(beginner_config, sample_file_analysis):
    """Test content complexity adjustment for beginners."""
    generator = CourseStructureGenerator(beginner_config)
    
    # Create a basic lesson
    lesson = generator._create_basic_lesson(
        "test.py", 0.7, sample_file_analysis, 0
    )
    
    # Beginners should have longer duration
    assert lesson.duration_minutes >= beginner_config.min_lesson_duration
    # Should have foundational objectives
    assert any("understand" in obj.lower() for obj in lesson.learning_objectives)


def test_adjust_content_complexity_for_advanced(advanced_config, sample_file_analysis):
    """Test content complexity adjustment for advanced learners."""
    generator = CourseStructureGenerator(advanced_config)
    
    # Create a basic lesson
    lesson = generator._create_basic_lesson(
        "test.py", 0.7, sample_file_analysis, 0
    )
    
    # Advanced should have shorter duration
    assert lesson.duration_minutes >= advanced_config.min_lesson_duration
    # Should have implementation objectives
    assert any("implement" in obj.lower() for obj in lesson.learning_objectives)


# ========== Test Focus Filtering ==========

def test_calculate_focus_relevance_patterns():
    """Test focus relevance calculation for patterns focus."""
    from datetime import datetime
    config = CourseConfig(course_focus="patterns")
    generator = CourseStructureGenerator(config)
    
    # Create file analysis with pattern-focused content
    file_analysis = FileAnalysis(
        file_path="test.py",
        language="python",
        complexity_metrics=create_complexity_metrics(),
        symbol_info=SymbolInfo(functions=[], classes=[], imports=[]),
        patterns=[
            DetectedPattern(
                pattern_type="factory_pattern",
                file_path="test.py",
                confidence=0.9,
                evidence=["Factory method"],
                line_numbers=[10]
            )
        ],
        teaching_value=create_teaching_value(),
        documentation_coverage=0.5,
        linter_issues=[],
        has_errors=False,
        errors=[],
        analyzed_at=datetime.now().isoformat(),
        cache_hit=False
    )
    
    relevance = generator._calculate_focus_relevance(file_analysis)
    assert relevance > 0.5  # Should be highly relevant


def test_calculate_focus_relevance_exclude_tags():
    """Test that exclude tags filter out files."""
    from datetime import datetime
    config = CourseConfig(
        course_focus="patterns",
        exclude_tags=["factory_pattern"]
    )
    generator = CourseStructureGenerator(config)
    
    # Create file analysis with excluded pattern
    file_analysis = FileAnalysis(
        file_path="test.py",
        language="python",
        complexity_metrics=create_complexity_metrics(),
        symbol_info=SymbolInfo(functions=[], classes=[], imports=[]),
        patterns=[
            DetectedPattern(
                pattern_type="factory_pattern",
                file_path="test.py",
                confidence=0.9,
                evidence=["Factory method"],
                line_numbers=[10]
            )
        ],
        teaching_value=create_teaching_value(),
        documentation_coverage=0.5,
        linter_issues=[],
        has_errors=False,
        errors=[],
        analyzed_at=datetime.now().isoformat(),
        cache_hit=False
    )
    
    relevance = generator._calculate_focus_relevance(file_analysis)
    assert relevance == 0.0  # Should be excluded


def test_prioritize_patterns_by_focus():
    """Test pattern prioritization by focus."""
    config = CourseConfig(course_focus="patterns")
    generator = CourseStructureGenerator(config)
    
    patterns = [
        DetectedPattern(
            pattern_type="factory_pattern",
            file_path="test.py",
            confidence=0.7,
            evidence=["Factory"],
            line_numbers=[10]
        ),
        DetectedPattern(
            pattern_type="random_pattern",
            file_path="test.py",
            confidence=0.9,
            evidence=["Random"],
            line_numbers=[20]
        )
    ]
    
    prioritized = generator.prioritize_patterns_by_focus(patterns)
    
    # Factory pattern should be prioritized for "patterns" focus
    assert prioritized[0].pattern_type == "factory_pattern"


# ========== Test Configuration Settings ==========

def test_config_default_values():
    """Test that configuration has sensible defaults."""
    config = CourseConfig()
    
    assert config.target_audience == "mixed"
    assert config.course_focus == "full-stack"
    assert config.min_modules == 3
    assert config.max_modules == 8
    assert config.max_code_lines == 50
    assert config.include_annotations is True


def test_config_custom_values():
    """Test that configuration accepts custom values."""
    config = CourseConfig(
        target_audience="beginner",
        course_focus="patterns",
        max_duration_hours=10.0,
        template_dir="/custom/templates",
        min_modules=5,
        max_modules=10
    )
    
    assert config.target_audience == "beginner"
    assert config.course_focus == "patterns"
    assert config.max_duration_hours == 10.0
    assert config.template_dir == "/custom/templates"
    assert config.min_modules == 5
    assert config.max_modules == 10
