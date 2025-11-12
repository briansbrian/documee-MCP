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
]
