"""Example: Export a course to MkDocs format.

This example demonstrates how to use the MkDocsExporter to export
a course outline to MkDocs static site format.
"""

import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.course.exporters import MkDocsExporter
from src.course.config import CourseConfig
from src.course.models import (
    CourseOutline, Module, Lesson, LessonContent, 
    CodeExample, Exercise, TestCase
)


def create_sample_course() -> CourseOutline:
    """Create a sample course for demonstration."""
    
    # Create code examples
    hello_code = CodeExample(
        code="""def greet(name):
    \"\"\"Greet someone by name.\"\"\"
    return f"Hello, {name}!"

# Usage
message = greet("World")
print(message)""",
        language="python",
        filename="hello.py",
        highlights=[],
        annotations={
            1: "Define a function that takes a name parameter",
            2: "Use an f-string to format the greeting",
            5: "Call the function with an argument"
        }
    )
    
    class_code = CodeExample(
        code="""class Person:
    \"\"\"Represents a person with a name and age.\"\"\"
    
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def introduce(self):
        return f"Hi, I'm {self.name} and I'm {self.age} years old."

# Create an instance
person = Person("Alice", 30)
print(person.introduce())""",
        language="python",
        filename="person.py"
    )
    
    # Create lesson content
    lesson1_content = LessonContent(
        introduction="Functions are reusable blocks of code that perform specific tasks.",
        explanation="In Python, functions are defined using the `def` keyword followed by the function name and parameters.",
        code_example=hello_code,
        walkthrough="This example shows a simple greeting function that takes a name and returns a formatted message.",
        summary="You learned how to define and call functions in Python.",
        further_reading=["Python Functions Documentation", "Best Practices for Function Design"]
    )
    
    lesson2_content = LessonContent(
        introduction="Classes are blueprints for creating objects with attributes and methods.",
        explanation="Object-oriented programming allows you to organize code into reusable, modular structures.",
        code_example=class_code,
        walkthrough="This Person class demonstrates how to define attributes in __init__ and create methods.",
        summary="You learned the basics of classes and object-oriented programming.",
        further_reading=["Python Classes Tutorial", "OOP Principles"]
    )
    
    # Create exercises
    exercise1 = Exercise(
        exercise_id="ex1",
        title="Create a Calculator Function",
        description="Write a function that performs basic arithmetic operations.",
        difficulty="beginner",
        estimated_minutes=15,
        instructions=[
            "Define a function called 'calculate' that takes three parameters: num1, num2, and operation",
            "Support operations: 'add', 'subtract', 'multiply', 'divide'",
            "Return the result of the operation",
            "Handle division by zero"
        ],
        starter_code="""def calculate(num1, num2, operation):
    # TODO: Implement the calculator logic
    pass""",
        solution_code="""def calculate(num1, num2, operation):
    if operation == 'add':
        return num1 + num2
    elif operation == 'subtract':
        return num1 - num2
    elif operation == 'multiply':
        return num1 * num2
    elif operation == 'divide':
        if num2 == 0:
            return "Error: Division by zero"
        return num1 / num2
    else:
        return "Error: Invalid operation\"""",
        hints=[
            "Use if-elif statements to check the operation type",
            "Remember to check for division by zero before dividing"
        ],
        test_cases=[
            TestCase("calculate(5, 3, 'add')", "8", "Test addition"),
            TestCase("calculate(10, 2, 'divide')", "5.0", "Test division"),
            TestCase("calculate(5, 0, 'divide')", "Error: Division by zero", "Test division by zero")
        ],
        learning_objectives=["Implement conditional logic", "Handle edge cases"]
    )
    
    # Create lessons
    lesson1 = Lesson(
        lesson_id="lesson-1",
        title="Introduction to Functions",
        description="Learn how to define and use functions in Python",
        order=0,
        difficulty="beginner",
        duration_minutes=30,
        file_path="examples/hello.py",
        teaching_value=0.85,
        learning_objectives=[
            "Understand function syntax",
            "Define functions with parameters",
            "Return values from functions"
        ],
        prerequisites=[],
        concepts=["functions", "parameters", "return values"],
        content=lesson1_content,
        exercises=[exercise1],
        tags=["python", "functions", "basics"]
    )
    
    lesson2 = Lesson(
        lesson_id="lesson-2",
        title="Object-Oriented Programming Basics",
        description="Learn about classes and objects in Python",
        order=1,
        difficulty="intermediate",
        duration_minutes=45,
        file_path="examples/person.py",
        teaching_value=0.90,
        learning_objectives=[
            "Understand class structure",
            "Create class instances",
            "Define methods"
        ],
        prerequisites=["lesson-1"],
        concepts=["classes", "objects", "methods", "OOP"],
        content=lesson2_content,
        exercises=[],
        tags=["python", "OOP", "classes"]
    )
    
    # Create module
    module = Module(
        module_id="module-1",
        title="Python Fundamentals",
        description="Master the core concepts of Python programming",
        order=0,
        lessons=[lesson1, lesson2],
        difficulty="beginner",
        duration_hours=1.25,
        learning_objectives=[
            "Write reusable functions",
            "Create and use classes",
            "Apply OOP principles"
        ]
    )
    
    # Create course
    course = CourseOutline(
        course_id="python-course-1",
        title="Python Programming Essentials",
        description="A comprehensive introduction to Python programming covering functions, classes, and more.",
        author="Documee Course Generator",
        version="1.0.0",
        created_at=datetime.now(),
        modules=[module],
        total_duration_hours=1.25,
        difficulty_distribution={"beginner": 1, "intermediate": 1},
        tags=["python", "programming", "fundamentals"],
        prerequisites=["Basic computer literacy"]
    )
    
    return course


def main():
    """Main example function."""
    print("Creating sample course...")
    course = create_sample_course()
    
    print(f"Course: {course.title}")
    print(f"Modules: {len(course.modules)}")
    print(f"Total lessons: {sum(len(m.lessons) for m in course.modules)}")
    print(f"Duration: {course.total_duration_hours} hours\n")
    
    # Configure exporter
    config = CourseConfig(
        author="Documee",
        version="1.0.0"
    )
    
    # Create exporter
    exporter = MkDocsExporter(config)
    
    # Export to MkDocs
    output_dir = "output/mkdocs_example"
    print(f"Exporting to MkDocs format at: {output_dir}")
    
    try:
        mkdocs_path = exporter.export_to_mkdocs(course, output_dir)
        print(f"✓ Export successful!")
        print(f"✓ MkDocs config: {mkdocs_path}")
        print(f"✓ Docs directory: {os.path.join(output_dir, 'docs')}")
        print(f"\nTo preview the site:")
        print(f"  1. cd {output_dir}")
        print(f"  2. pip install mkdocs-material")
        print(f"  3. mkdocs serve")
        print(f"  4. Open http://127.0.0.1:8000 in your browser")
    except Exception as e:
        print(f"✗ Export failed: {e}")
        raise


if __name__ == "__main__":
    main()
