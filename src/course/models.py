"""Data models for Course Generator."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional


@dataclass
class CodeHighlight:
    """A highlighted section of code."""
    start_line: int
    end_line: int
    description: str


@dataclass
class CodeExample:
    """A code example with annotations."""
    code: str
    language: str
    filename: str
    highlights: List[CodeHighlight] = field(default_factory=list)
    annotations: Dict[int, str] = field(default_factory=dict)  # Line number -> explanation


@dataclass
class TestCase:
    """A test case for validating exercise solutions."""
    input: str
    expected_output: str
    description: str


@dataclass
class Exercise:
    """A coding exercise for students."""
    exercise_id: str
    title: str
    description: str
    difficulty: str
    estimated_minutes: int
    instructions: List[str]
    starter_code: str
    solution_code: str
    hints: List[str] = field(default_factory=list)
    test_cases: List[TestCase] = field(default_factory=list)
    learning_objectives: List[str] = field(default_factory=list)


@dataclass
class LessonContent:
    """The actual lesson content."""
    introduction: str
    explanation: str
    code_example: CodeExample
    walkthrough: str
    summary: str
    further_reading: List[str] = field(default_factory=list)


@dataclass
class Lesson:
    """A single educational unit."""
    lesson_id: str
    title: str
    description: str
    order: int
    difficulty: str
    duration_minutes: int
    file_path: str  # Source file this lesson is based on
    teaching_value: float
    learning_objectives: List[str]
    prerequisites: List[str] = field(default_factory=list)
    concepts: List[str] = field(default_factory=list)
    content: Optional[LessonContent] = None
    exercises: List[Exercise] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


@dataclass
class Module:
    """A collection of related lessons."""
    module_id: str
    title: str
    description: str
    order: int
    lessons: List[Lesson]
    difficulty: str  # beginner, intermediate, advanced
    duration_hours: float
    learning_objectives: List[str] = field(default_factory=list)


@dataclass
class CourseOutline:
    """Complete course structure with modules and lessons."""
    course_id: str
    title: str
    description: str
    author: str
    version: str
    created_at: datetime
    modules: List[Module]
    total_duration_hours: float
    difficulty_distribution: Dict[str, int] = field(default_factory=dict)  # beginner: 5, intermediate: 10, advanced: 3
    tags: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
