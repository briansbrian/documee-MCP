"""Example usage of MetadataGenerator.

This example demonstrates how to generate comprehensive metadata for courses,
lessons, and exercises using the MetadataGenerator class.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime
from src.course import (
    MetadataGenerator,
    CourseOutline,
    Module,
    Lesson,
    Exercise,
    TestCase,
)
import json


def main():
    """Demonstrate metadata generation functionality."""
    
    # Create a metadata generator
    generator = MetadataGenerator()
    
    # Create sample exercise
    exercise = Exercise(
        exercise_id="ex-001",
        title="Implement a Calculator",
        description="Create a simple calculator with basic operations",
        difficulty="beginner",
        estimated_minutes=25,
        instructions=[
            "Define a Calculator class",
            "Implement add, subtract, multiply, divide methods",
            "Add error handling for division by zero",
            "Test your implementation"
        ],
        starter_code="class Calculator:\n    # TODO: Implement methods\n    pass",
        solution_code="class Calculator:\n    def add(self, a, b):\n        return a + b\n    # ...",
        hints=["Start with the add method", "Remember to handle edge cases"],
        test_cases=[
            TestCase(
                input="calc.add(2, 3)",
                expected_output="5",
                description="Test addition"
            )
        ],
        learning_objectives=["Understand class structure", "Implement basic methods"]
    )
    
    # Create sample lesson
    lesson = Lesson(
        lesson_id="lesson-001",
        title="Object-Oriented Programming Basics",
        description="Learn the fundamentals of OOP",
        order=0,
        difficulty="beginner",
        duration_minutes=45,
        file_path="src/calculator.py",
        teaching_value=0.85,
        learning_objectives=[
            "Understand classes and objects",
            "Implement methods",
            "Apply encapsulation"
        ],
        prerequisites=[],
        concepts=["classes", "methods", "objects"],
        exercises=[exercise],
        tags=["python", "oop", "classes"]
    )
    
    # Create sample module
    module = Module(
        module_id="module-001",
        title="Python Fundamentals",
        description="Master the basics of Python programming",
        order=0,
        lessons=[lesson],
        difficulty="beginner",
        duration_hours=0.75,
        learning_objectives=["Master Python basics", "Write clean code"]
    )
    
    # Create sample course
    course = CourseOutline(
        course_id="course-001",
        title="Python Programming Masterclass",
        description="A comprehensive course for learning Python from scratch",
        author="Jane Developer",
        version="1.0.0",
        created_at=datetime.now(),
        modules=[module],
        total_duration_hours=0.75,
        difficulty_distribution={"beginner": 1, "intermediate": 0, "advanced": 0},
        tags=["python", "programming", "beginner-friendly"],
        prerequisites=[]
    )
    
    print("=" * 70)
    print("METADATA GENERATOR EXAMPLE")
    print("=" * 70)
    
    # Generate course metadata
    print("\n1. COURSE METADATA")
    print("-" * 70)
    course_metadata = generator.generate_course_metadata(course)
    print(f"Course ID: {course_metadata['course_id']}")
    print(f"Title: {course_metadata['title']}")
    print(f"Author: {course_metadata['author']}")
    print(f"Version: {course_metadata['version']}")
    print(f"Total Modules: {course_metadata['structure']['total_modules']}")
    print(f"Total Lessons: {course_metadata['structure']['total_lessons']}")
    print(f"Total Exercises: {course_metadata['structure']['total_exercises']}")
    print(f"Duration: {course_metadata['structure']['total_duration_hours']} hours")
    print(f"Tags: {', '.join(course_metadata['tags'])}")
    
    # Generate lesson metadata
    print("\n2. LESSON METADATA")
    print("-" * 70)
    lesson_metadata = generator.generate_lesson_metadata(lesson, module)
    print(f"Lesson ID: {lesson_metadata['lesson_id']}")
    print(f"Title: {lesson_metadata['title']}")
    print(f"Difficulty: {lesson_metadata['difficulty']}")
    print(f"Duration: {lesson_metadata['estimated_completion_time']}")
    print(f"Learning Objectives: {len(lesson_metadata['learning_objectives'])}")
    print(f"Exercise Count: {lesson_metadata['exercise_count']}")
    print(f"Tags: {', '.join(lesson_metadata['tags'])}")
    
    # Generate exercise metadata
    print("\n3. EXERCISE METADATA")
    print("-" * 70)
    exercise_metadata = generator.generate_exercise_metadata(exercise, lesson)
    print(f"Exercise ID: {exercise_metadata['exercise_id']}")
    print(f"Title: {exercise_metadata['title']}")
    print(f"Difficulty: {exercise_metadata['difficulty']}")
    print(f"Estimated Time: {exercise_metadata['estimated_completion_time']}")
    print(f"Solution Available: {exercise_metadata['solution_available']}")
    print(f"Hint Count: {exercise_metadata['hint_count']}")
    print(f"Test Cases: {exercise_metadata['test_case_count']}")
    
    # Generate complete course manifest
    print("\n4. COURSE MANIFEST")
    print("-" * 70)
    manifest = generator.generate_course_manifest(course)
    print(f"Manifest Version: {manifest['manifest_version']}")
    print(f"Generated At: {manifest['generated_at']}")
    print(f"Total Modules: {len(manifest['modules'])}")
    print(f"Indices Available:")
    print(f"  - Lessons by Difficulty: {list(manifest['indices']['lessons_by_difficulty'].keys())}")
    print(f"  - Lessons by Tag: {len(manifest['indices']['lessons_by_tag'])} tags")
    print(f"  - Lessons by Duration: {list(manifest['indices']['lessons_by_duration'].keys())}")
    
    # Save manifest to file
    output_file = "output/course_manifest_example.json"
    print(f"\n5. SAVING MANIFEST")
    print("-" * 70)
    print(f"Saving complete manifest to: {output_file}")
    
    import os
    os.makedirs("output", exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Manifest saved successfully!")
    print(f"✓ File size: {os.path.getsize(output_file)} bytes")
    
    print("\n" + "=" * 70)
    print("EXAMPLE COMPLETE")
    print("=" * 70)
    print("\nKey Features Demonstrated:")
    print("  ✓ Course metadata generation (Req 14.1)")
    print("  ✓ Lesson metadata with prerequisites (Req 14.2)")
    print("  ✓ Exercise metadata with solution availability (Req 14.3)")
    print("  ✓ Tags from patterns (Req 14.4)")
    print("  ✓ Complete course manifest (Req 14.5)")


if __name__ == "__main__":
    main()
