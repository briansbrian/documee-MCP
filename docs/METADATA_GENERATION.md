# Metadata Generation

## Overview

The Metadata Generator creates comprehensive metadata for courses, lessons, and exercises. It implements Requirements 14.1, 14.2, 14.3, 14.4, and 14.5 from the Course Generator specification.

## Features

### Course Metadata (Req 14.1, 14.5)
- Core identification (course_id, title, description, author, version)
- Timestamps (created_at, updated_at)
- Structure information (total modules, lessons, exercises, duration)
- Difficulty distribution across all lessons
- Tags and prerequisites
- Module summaries
- Learning path information
- Schema versioning

### Lesson Metadata (Req 14.2, 14.4)
- Core identification (lesson_id, title, description)
- Position in course (module_id, order)
- Difficulty and duration with formatted completion time
- Learning objectives and prerequisites
- Concepts covered
- Tags generated from patterns
- Source file information
- Content and exercise availability
- Complexity level and recommended audience

### Exercise Metadata (Req 14.3)
- Core identification (exercise_id, title, description)
- Parent lesson information
- Difficulty and estimated time
- Learning objectives
- Content availability flags:
  - has_starter_code
  - has_solution
  - solution_available
  - hint_count
  - test_case_count
- Complexity level and recommended audience
- Validation availability

### Course Manifest (Req 14.5)
- Complete course metadata
- Detailed module and lesson structure
- Exercise metadata for all exercises
- Quick reference indices:
  - Lessons by difficulty
  - Lessons by tag
  - Lessons by duration
- Manifest versioning and generation timestamp

## Usage

### Basic Usage

```python
from src.course import MetadataGenerator, CourseOutline

# Create generator
generator = MetadataGenerator()

# Generate course metadata
course_metadata = generator.generate_course_metadata(course)

# Generate lesson metadata
lesson_metadata = generator.generate_lesson_metadata(lesson, module)

# Generate exercise metadata
exercise_metadata = generator.generate_exercise_metadata(exercise, lesson)

# Generate complete manifest
manifest = generator.generate_course_manifest(course)
```

### Example Output

#### Course Metadata
```json
{
  "course_id": "course-001",
  "title": "Python Programming Masterclass",
  "author": "Jane Developer",
  "version": "1.0.0",
  "created_at": "2025-11-13T02:54:51.107555",
  "structure": {
    "total_modules": 1,
    "total_lessons": 1,
    "total_exercises": 1,
    "total_duration_hours": 0.75
  },
  "difficulty_distribution": {
    "beginner": 1,
    "intermediate": 0,
    "advanced": 0
  },
  "tags": ["python", "programming", "beginner-friendly"]
}
```

#### Lesson Metadata
```json
{
  "lesson_id": "lesson-001",
  "title": "Object-Oriented Programming Basics",
  "difficulty": "beginner",
  "duration_minutes": 45,
  "estimated_completion_time": "45m",
  "learning_objectives": [
    "Understand classes and objects",
    "Implement methods"
  ],
  "prerequisites": [],
  "tags": ["python", "oop", "classes"]
}
```

#### Exercise Metadata
```json
{
  "exercise_id": "ex-001",
  "title": "Implement a Calculator",
  "difficulty": "beginner",
  "estimated_minutes": 25,
  "estimated_completion_time": "25m",
  "solution_available": true,
  "hint_count": 2,
  "test_case_count": 1
}
```

## Helper Methods

### Duration Formatting
- `_format_duration(minutes)`: Converts minutes to human-readable format
  - 45 minutes → "45m"
  - 120 minutes → "2h"
  - 90 minutes → "1h 30m"

### Difficulty Mapping
- `_map_difficulty_to_complexity(difficulty)`: Maps difficulty to numeric score
  - beginner → 3
  - intermediate → 6
  - advanced → 9

### Audience Recommendations
- `_get_recommended_audience(difficulty)`: Returns audience description
  - beginner → "New programmers and those learning fundamentals"
  - intermediate → "Developers with basic programming experience"
  - advanced → "Experienced developers looking to master advanced concepts"

### Indexing
- `_index_lessons_by_difficulty(course)`: Groups lessons by difficulty level
- `_index_lessons_by_tag(course)`: Groups lessons by tags
- `_index_lessons_by_duration(course)`: Groups lessons by duration ranges
  - short: < 30 minutes
  - medium: 30-60 minutes
  - long: > 60 minutes

## Testing

Comprehensive test suite in `tests/test_metadata_generator.py`:
- 28 tests covering all functionality
- Tests for course, lesson, and exercise metadata
- Tests for manifest generation
- Tests for helper methods
- All tests passing ✓

## Integration

The MetadataGenerator is exported from `src/course/__init__.py` and can be used alongside other course generation components:

```python
from src.course import (
    CourseStructureGenerator,
    LessonContentGenerator,
    ExerciseGenerator,
    MetadataGenerator
)
```

## Example

See `examples/metadata_generator_example.py` for a complete working example that demonstrates:
- Course metadata generation
- Lesson metadata generation
- Exercise metadata generation
- Complete manifest generation
- Saving manifest to JSON file

Run the example:
```bash
.\venv\Scripts\python.exe examples/metadata_generator_example.py
```

## Requirements Satisfied

✓ **Requirement 14.1**: Generate course metadata with title, description, author, version, creation date, and tags  
✓ **Requirement 14.2**: Generate lesson metadata with title, difficulty, duration, prerequisites, and learning objectives  
✓ **Requirement 14.3**: Generate exercise metadata with title, difficulty, estimated time, and solution availability  
✓ **Requirement 14.4**: Generate tags from patterns for lessons  
✓ **Requirement 14.5**: Create course manifest file listing all lessons, modules, and resources  

## Files Created

- `src/course/metadata_generator.py` - Main implementation
- `tests/test_metadata_generator.py` - Comprehensive test suite
- `examples/metadata_generator_example.py` - Usage example
- `docs/METADATA_GENERATION.md` - This documentation
