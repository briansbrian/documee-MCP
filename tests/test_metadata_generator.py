"""Unit tests for Metadata Generator."""

import pytest
from datetime import datetime
from src.course.metadata_generator import MetadataGenerator
from src.course.models import (
    CourseOutline,
    Module,
    Lesson,
    Exercise,
    LessonContent,
    CodeExample,
    TestCase,
)


# ========== Test Fixtures ==========

@pytest.fixture
def metadata_generator():
    """Create a metadata generator instance."""
    return MetadataGenerator()


@pytest.fixture
def sample_exercise():
    """Create a sample exercise for testing."""
    return Exercise(
        exercise_id="ex-001",
        title="Practice Function Implementation",
        description="Implement a simple function",
        difficulty="beginner",
        estimated_minutes=20,
        instructions=["Step 1", "Step 2", "Step 3"],
        starter_code="def example():\n    pass",
        solution_code="def example():\n    return 42",
        hints=["Hint 1", "Hint 2"],
        test_cases=[
            TestCase(
                input="example()",
                expected_output="42",
                description="Test basic functionality"
            )
        ],
        learning_objectives=["Understand function implementation"]
    )


@pytest.fixture
def sample_lesson(sample_exercise):
    """Create a sample lesson for testing."""
    return Lesson(
        lesson_id="lesson-001",
        title="Introduction to Functions",
        description="Learn about functions",
        order=0,
        difficulty="beginner",
        duration_minutes=30,
        file_path="src/example.py",
        teaching_value=0.8,
        learning_objectives=["Understand functions", "Write clean code"],
        prerequisites=["lesson-000"],
        concepts=["functions", "parameters"],
        exercises=[sample_exercise],
        tags=["python", "functions", "basics"]
    )


@pytest.fixture
def sample_module(sample_lesson):
    """Create a sample module for testing."""
    return Module(
        module_id="module-001",
        title="Python Basics",
        description="Learn Python fundamentals",
        order=0,
        lessons=[sample_lesson],
        difficulty="beginner",
        duration_hours=0.5,
        learning_objectives=["Master Python basics"]
    )


@pytest.fixture
def sample_course(sample_module):
    """Create a sample course for testing."""
    return CourseOutline(
        course_id="course-001",
        title="Learn Python",
        description="A comprehensive Python course",
        author="Test Author",
        version="1.0.0",
        created_at=datetime(2024, 1, 1, 12, 0, 0),
        modules=[sample_module],
        total_duration_hours=0.5,
        difficulty_distribution={"beginner": 1, "intermediate": 0, "advanced": 0},
        tags=["python", "programming"],
        prerequisites=[]
    )


# ========== Test Course Metadata Generation ==========

def test_generate_course_metadata_includes_core_fields(metadata_generator, sample_course):
    """Test that course metadata includes all core fields (Req 14.1)."""
    metadata = metadata_generator.generate_course_metadata(sample_course)
    
    # Verify core identification fields
    assert metadata["course_id"] == "course-001"
    assert metadata["title"] == "Learn Python"
    assert metadata["description"] == "A comprehensive Python course"
    assert metadata["author"] == "Test Author"
    assert metadata["version"] == "1.0.0"


def test_generate_course_metadata_includes_timestamps(metadata_generator, sample_course):
    """Test that course metadata includes creation date (Req 14.1)."""
    metadata = metadata_generator.generate_course_metadata(sample_course)
    
    assert "created_at" in metadata
    assert "updated_at" in metadata
    assert metadata["created_at"] == "2024-01-01T12:00:00"


def test_generate_course_metadata_includes_tags(metadata_generator, sample_course):
    """Test that course metadata includes tags (Req 14.1)."""
    metadata = metadata_generator.generate_course_metadata(sample_course)
    
    assert "tags" in metadata
    assert isinstance(metadata["tags"], list)
    assert "python" in metadata["tags"]


def test_generate_course_metadata_includes_structure_info(metadata_generator, sample_course):
    """Test that course metadata includes structure information (Req 14.5)."""
    metadata = metadata_generator.generate_course_metadata(sample_course)
    
    assert "structure" in metadata
    assert metadata["structure"]["total_modules"] == 1
    assert metadata["structure"]["total_lessons"] == 1
    assert metadata["structure"]["total_exercises"] == 1
    assert metadata["structure"]["total_duration_hours"] == 0.5


def test_generate_course_metadata_includes_difficulty_distribution(metadata_generator, sample_course):
    """Test that course metadata includes difficulty distribution (Req 14.5)."""
    metadata = metadata_generator.generate_course_metadata(sample_course)
    
    assert "difficulty_distribution" in metadata
    assert metadata["difficulty_distribution"]["beginner"] == 1
    assert metadata["difficulty_distribution"]["intermediate"] == 0
    assert metadata["difficulty_distribution"]["advanced"] == 0


# ========== Test Lesson Metadata Generation ==========

def test_generate_lesson_metadata_includes_core_fields(metadata_generator, sample_lesson, sample_module):
    """Test that lesson metadata includes core fields (Req 14.2)."""
    metadata = metadata_generator.generate_lesson_metadata(sample_lesson, sample_module)
    
    assert metadata["lesson_id"] == "lesson-001"
    assert metadata["title"] == "Introduction to Functions"
    assert metadata["description"] == "Learn about functions"


def test_generate_lesson_metadata_includes_difficulty_and_duration(metadata_generator, sample_lesson, sample_module):
    """Test that lesson metadata includes difficulty and duration (Req 14.2)."""
    metadata = metadata_generator.generate_lesson_metadata(sample_lesson, sample_module)
    
    assert metadata["difficulty"] == "beginner"
    assert metadata["duration_minutes"] == 30
    assert "estimated_completion_time" in metadata


def test_generate_lesson_metadata_includes_prerequisites(metadata_generator, sample_lesson, sample_module):
    """Test that lesson metadata includes prerequisites (Req 14.2)."""
    metadata = metadata_generator.generate_lesson_metadata(sample_lesson, sample_module)
    
    assert "prerequisites" in metadata
    assert metadata["prerequisites"] == ["lesson-000"]


def test_generate_lesson_metadata_includes_learning_objectives(metadata_generator, sample_lesson, sample_module):
    """Test that lesson metadata includes learning objectives (Req 14.2)."""
    metadata = metadata_generator.generate_lesson_metadata(sample_lesson, sample_module)
    
    assert "learning_objectives" in metadata
    assert len(metadata["learning_objectives"]) == 2
    assert "Understand functions" in metadata["learning_objectives"]


def test_generate_lesson_metadata_includes_tags_from_patterns(metadata_generator, sample_lesson, sample_module):
    """Test that lesson metadata includes tags generated from patterns (Req 14.4)."""
    metadata = metadata_generator.generate_lesson_metadata(sample_lesson, sample_module)
    
    assert "tags" in metadata
    assert "python" in metadata["tags"]
    assert "functions" in metadata["tags"]


# ========== Test Exercise Metadata Generation ==========

def test_generate_exercise_metadata_includes_core_fields(metadata_generator, sample_exercise, sample_lesson):
    """Test that exercise metadata includes core fields (Req 14.3)."""
    metadata = metadata_generator.generate_exercise_metadata(sample_exercise, sample_lesson)
    
    assert metadata["exercise_id"] == "ex-001"
    assert metadata["title"] == "Practice Function Implementation"
    assert metadata["description"] == "Implement a simple function"


def test_generate_exercise_metadata_includes_difficulty_and_time(metadata_generator, sample_exercise, sample_lesson):
    """Test that exercise metadata includes difficulty and estimated time (Req 14.3)."""
    metadata = metadata_generator.generate_exercise_metadata(sample_exercise, sample_lesson)
    
    assert metadata["difficulty"] == "beginner"
    assert metadata["estimated_minutes"] == 20
    assert "estimated_completion_time" in metadata


def test_generate_exercise_metadata_includes_solution_availability(metadata_generator, sample_exercise, sample_lesson):
    """Test that exercise metadata includes solution availability flag (Req 14.3)."""
    metadata = metadata_generator.generate_exercise_metadata(sample_exercise, sample_lesson)
    
    assert "solution_available" in metadata
    assert metadata["solution_available"] is True
    assert metadata["has_solution"] is True


def test_generate_exercise_metadata_with_no_solution(metadata_generator, sample_lesson):
    """Test exercise metadata when solution is not available."""
    exercise_no_solution = Exercise(
        exercise_id="ex-002",
        title="Challenge Exercise",
        description="Advanced challenge",
        difficulty="advanced",
        estimated_minutes=45,
        instructions=["Step 1"],
        starter_code="# TODO",
        solution_code="",  # No solution
        hints=[],
        test_cases=[]
    )
    
    metadata = metadata_generator.generate_exercise_metadata(exercise_no_solution, sample_lesson)
    
    assert metadata["solution_available"] is False
    assert metadata["has_solution"] is False


# ========== Test Course Manifest Generation ==========

def test_generate_course_manifest_includes_course_metadata(metadata_generator, sample_course):
    """Test that course manifest includes course metadata (Req 14.1, 14.5)."""
    manifest = metadata_generator.generate_course_manifest(sample_course)
    
    assert "course" in manifest
    assert manifest["course"]["course_id"] == "course-001"
    assert manifest["course"]["title"] == "Learn Python"


def test_generate_course_manifest_includes_modules(metadata_generator, sample_course):
    """Test that course manifest includes module details (Req 14.5)."""
    manifest = metadata_generator.generate_course_manifest(sample_course)
    
    assert "modules" in manifest
    assert len(manifest["modules"]) == 1
    assert manifest["modules"][0]["module_id"] == "module-001"


def test_generate_course_manifest_includes_lessons(metadata_generator, sample_course):
    """Test that course manifest includes lesson details (Req 14.5)."""
    manifest = metadata_generator.generate_course_manifest(sample_course)
    
    assert len(manifest["modules"][0]["lessons"]) == 1
    lesson = manifest["modules"][0]["lessons"][0]
    assert lesson["lesson_id"] == "lesson-001"


def test_generate_course_manifest_includes_exercises(metadata_generator, sample_course):
    """Test that course manifest includes exercise details (Req 14.5)."""
    manifest = metadata_generator.generate_course_manifest(sample_course)
    
    lesson = manifest["modules"][0]["lessons"][0]
    assert "exercises" in lesson
    assert len(lesson["exercises"]) == 1
    assert lesson["exercises"][0]["exercise_id"] == "ex-001"


def test_generate_course_manifest_includes_indices(metadata_generator, sample_course):
    """Test that course manifest includes quick reference indices (Req 14.5)."""
    manifest = metadata_generator.generate_course_manifest(sample_course)
    
    assert "indices" in manifest
    assert "lessons_by_difficulty" in manifest["indices"]
    assert "lessons_by_tag" in manifest["indices"]
    assert "lessons_by_duration" in manifest["indices"]


def test_generate_course_manifest_has_version_info(metadata_generator, sample_course):
    """Test that course manifest includes version information."""
    manifest = metadata_generator.generate_course_manifest(sample_course)
    
    assert "manifest_version" in manifest
    assert "generated_at" in manifest


# ========== Test Helper Methods ==========

def test_format_duration_minutes_only(metadata_generator):
    """Test duration formatting for minutes only."""
    assert metadata_generator._format_duration(45) == "45m"


def test_format_duration_hours_only(metadata_generator):
    """Test duration formatting for exact hours."""
    assert metadata_generator._format_duration(120) == "2h"


def test_format_duration_hours_and_minutes(metadata_generator):
    """Test duration formatting for hours and minutes."""
    assert metadata_generator._format_duration(90) == "1h 30m"


def test_map_difficulty_to_complexity(metadata_generator):
    """Test difficulty to complexity mapping."""
    assert metadata_generator._map_difficulty_to_complexity("beginner") == 3
    assert metadata_generator._map_difficulty_to_complexity("intermediate") == 6
    assert metadata_generator._map_difficulty_to_complexity("advanced") == 9


def test_get_recommended_audience(metadata_generator):
    """Test recommended audience descriptions."""
    beginner_audience = metadata_generator._get_recommended_audience("beginner")
    assert "New programmers" in beginner_audience
    
    intermediate_audience = metadata_generator._get_recommended_audience("intermediate")
    assert "basic programming experience" in intermediate_audience
    
    advanced_audience = metadata_generator._get_recommended_audience("advanced")
    assert "Experienced developers" in advanced_audience


def test_index_lessons_by_difficulty(metadata_generator, sample_course):
    """Test indexing lessons by difficulty."""
    index = metadata_generator._index_lessons_by_difficulty(sample_course)
    
    assert "beginner" in index
    assert "intermediate" in index
    assert "advanced" in index
    assert len(index["beginner"]) == 1
    assert "lesson-001" in index["beginner"]


def test_index_lessons_by_tag(metadata_generator, sample_course):
    """Test indexing lessons by tags."""
    index = metadata_generator._index_lessons_by_tag(sample_course)
    
    assert "python" in index
    assert "functions" in index
    assert "lesson-001" in index["python"]


def test_index_lessons_by_duration(metadata_generator, sample_course):
    """Test indexing lessons by duration ranges."""
    index = metadata_generator._index_lessons_by_duration(sample_course)
    
    assert "short" in index
    assert "medium" in index
    assert "long" in index
    # 30 minutes should be in "medium" category
    assert "lesson-001" in index["medium"]
