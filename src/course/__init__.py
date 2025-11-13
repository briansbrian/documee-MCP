"""Course Generator - Transform analysis results into educational courses."""

from .models import (
    CourseOutline,
    Module,
    Lesson,
    LessonContent,
    CodeExample,
    CodeHighlight,
    Exercise,
    TestCase,
)

from .config import CourseConfig
from .structure_generator import CourseStructureGenerator
from .content_generator import LessonContentGenerator
from .exercise_generator import ExerciseGenerator
from .content_validator import ContentValidator, ValidationReport, ValidationIssue
from .metadata_generator import MetadataGenerator
from .incremental_updater import (
    IncrementalUpdateManager,
    FileChange,
    LessonUpdate,
    CourseVersion,
)

__all__ = [
    "CourseOutline",
    "Module",
    "Lesson",
    "LessonContent",
    "CodeExample",
    "CodeHighlight",
    "Exercise",
    "TestCase",
    "CourseConfig",
    "CourseStructureGenerator",
    "LessonContentGenerator",
    "ExerciseGenerator",
    "ContentValidator",
    "ValidationReport",
    "ValidationIssue",
    "MetadataGenerator",
    "IncrementalUpdateManager",
    "FileChange",
    "LessonUpdate",
    "CourseVersion",
]
