"""Tests for export formats.

Tests Requirements 5.1, 5.2, 5.3, 5.4:
- JSON export structure
- Markdown export
- Next.js export
- Export error handling
"""

import os
import json
import tempfile
import shutil
from datetime import datetime
from src.course.exporters.export_manager import ExportManager
from src.course.config import CourseConfig
from src.course.models import (
    CourseOutline, Module, Lesson, LessonContent,
    CodeExample, Exercise, TestCase, CodeHighlight
)


def create_test_course():
    """Create a test course for export testing."""
    # Create code example
    code_example = CodeExample(
        code="def hello():\n    print('Hello, World!')",
        language="python",
        filename="hello.py",
        highlights=[
            CodeHighlight(start_line=1, end_line=2, description="Function definition")
        ],
        annotations={1: "Define the function", 2: "Print greeting"}
    )
    
    # Create lesson content
    lesson_content = LessonContent(
        introduction="Learn about functions in Python",
        explanation="Functions are reusable blocks of code that perform specific tasks",
        code_example=code_example,
        walkthrough="This function prints a greeting message to the console",
        summary="You learned how to define and call basic functions",
        further_reading=["Python Functions Documentation"]
    )
    
    # Create exercise
    exercise = Exercise(
        exercise_id="ex-1",
        title="Write a greeting function",
        description="Create a function that greets a user by name",
        difficulty="beginner",
        estimated_minutes=10,
        instructions=[
            "Define a function called greet",
            "Accept a name parameter",
            "Print a personalized greeting"
        ],
        starter_code="def greet(name):\n    # Your code here\n    pass",
        solution_code="def greet(name):\n    print(f'Hello, {name}!')",
        hints=["Use an f-string for formatting", "Don't forget the exclamation mark"],
        test_cases=[
            TestCase(
                input="Alice",
                expected_output="Hello, Alice!",
                description="Test greeting Alice"
            )
        ],
        learning_objectives=["Define functions", "Use parameters"]
    )
    
    # Create lesson
    lesson = Lesson(
        lesson_id="lesson-1",
        title="Introduction to Functions",
        description="Learn the basics of functions",
        order=0,
        difficulty="beginner",
        duration_minutes=30,
        file_path="src/hello.py",
        teaching_value=0.8,
        learning_objectives=["Understand function syntax", "Write basic functions"],
        prerequisites=["Basic Python syntax"],
        concepts=["functions", "syntax"],
        content=lesson_content,
        exercises=[exercise],
        tags=["functions", "basics"]
    )
    
    # Create module
    module = Module(
        module_id="module-1",
        title="Python Basics",
        description="Learn the fundamentals of Python programming",
        order=0,
        lessons=[lesson],
        difficulty="beginner",
        duration_hours=0.5,
        learning_objectives=["Master basic Python concepts"]
    )
    
    # Create course
    course = CourseOutline(
        course_id="course-1",
        title="Python Programming Course",
        description="A comprehensive course on Python programming",
        author="Test Author",
        version="1.0.0",
        created_at=datetime(2024, 1, 1, 12, 0, 0),
        modules=[module],
        total_duration_hours=0.5,
        difficulty_distribution={"beginner": 1},
        tags=["python", "programming"],
        prerequisites=["Basic computer skills"]
    )
    
    return course


def test_json_export_structure():
    """Test JSON export structure.
    
    Tests Requirement 5.2:
    - Converts CourseOutline to dict
    - Includes all course data with schema
    - Writes formatted JSON with proper indentation
    """
    print("\n🧪 Testing JSON export structure...")
    
    # Create test course and config
    course = create_test_course()
    config = CourseConfig()
    export_manager = ExportManager(config)
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Export to JSON
        json_path = export_manager.export(course, temp_dir, format='json')
        
        # Verify file was created
        assert os.path.exists(json_path), "JSON file should be created"
        assert json_path.endswith('course.json'), "JSON file should be named course.json"
        
        # Read and parse JSON
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Verify schema version (Req 5.2)
        assert 'schema_version' in data, "JSON should include schema version"
        assert data['schema_version'] == '1.0', "Schema version should be 1.0"
        
        # Verify course metadata (Req 5.2)
        assert data['course_id'] == 'course-1', "Course ID should match"
        assert data['title'] == 'Python Programming Course', "Title should match"
        assert data['description'] == 'A comprehensive course on Python programming', "Description should match"
        assert data['author'] == 'Test Author', "Author should match"
        assert data['version'] == '1.0.0', "Version should match"
        assert data['total_duration_hours'] == 0.5, "Duration should match"
        
        # Verify difficulty distribution (Req 5.2)
        assert 'difficulty_distribution' in data, "Should include difficulty distribution"
        assert data['difficulty_distribution']['beginner'] == 1, "Should have 1 beginner lesson"
        
        # Verify tags and prerequisites (Req 5.2)
        assert 'tags' in data, "Should include tags"
        assert 'python' in data['tags'], "Should include python tag"
        assert 'prerequisites' in data, "Should include prerequisites"
        assert 'Basic computer skills' in data['prerequisites'], "Should include prerequisite"
        
        # Verify modules structure (Req 5.2)
        assert 'modules' in data, "Should include modules"
        assert len(data['modules']) == 1, "Should have 1 module"
        
        module = data['modules'][0]
        assert module['module_id'] == 'module-1', "Module ID should match"
        assert module['title'] == 'Python Basics', "Module title should match"
        assert module['difficulty'] == 'beginner', "Module difficulty should match"
        
        # Verify lessons structure (Req 5.2)
        assert 'lessons' in module, "Module should include lessons"
        assert len(module['lessons']) == 1, "Module should have 1 lesson"
        
        lesson = module['lessons'][0]
        assert lesson['lesson_id'] == 'lesson-1', "Lesson ID should match"
        assert lesson['title'] == 'Introduction to Functions', "Lesson title should match"
        assert lesson['difficulty'] == 'beginner', "Lesson difficulty should match"
        assert lesson['duration_minutes'] == 30, "Lesson duration should match"
        assert lesson['teaching_value'] == 0.8, "Teaching value should match"
        
        # Verify lesson content (Req 5.2)
        assert 'content' in lesson, "Lesson should include content"
        content = lesson['content']
        assert content['introduction'] == 'Learn about functions in Python', "Introduction should match"
        assert content['explanation'] == 'Functions are reusable blocks of code that perform specific tasks', "Explanation should match"
        
        # Verify code example (Req 5.2)
        assert 'code_example' in content, "Content should include code example"
        code_ex = content['code_example']
        assert code_ex['code'] == "def hello():\n    print('Hello, World!')", "Code should match"
        assert code_ex['language'] == 'python', "Language should match"
        assert code_ex['filename'] == 'hello.py', "Filename should match"
        
        # Verify code highlights (Req 5.2)
        assert 'highlights' in code_ex, "Code example should include highlights"
        assert len(code_ex['highlights']) == 1, "Should have 1 highlight"
        highlight = code_ex['highlights'][0]
        assert highlight['start_line'] == 1, "Highlight start line should match"
        assert highlight['end_line'] == 2, "Highlight end line should match"
        
        # Verify annotations (Req 5.2)
        assert 'annotations' in code_ex, "Code example should include annotations"
        assert '1' in code_ex['annotations'], "Should have annotation for line 1"
        
        # Verify exercises (Req 5.2)
        assert 'exercises' in lesson, "Lesson should include exercises"
        assert len(lesson['exercises']) == 1, "Should have 1 exercise"
        
        exercise = lesson['exercises'][0]
        assert exercise['exercise_id'] == 'ex-1', "Exercise ID should match"
        assert exercise['title'] == 'Write a greeting function', "Exercise title should match"
        assert exercise['difficulty'] == 'beginner', "Exercise difficulty should match"
        assert len(exercise['instructions']) == 3, "Should have 3 instructions"
        assert len(exercise['hints']) == 2, "Should have 2 hints"
        assert len(exercise['test_cases']) == 1, "Should have 1 test case"
        
        # Verify test case structure (Req 5.2)
        test_case = exercise['test_cases'][0]
        assert test_case['input'] == 'Alice', "Test case input should match"
        assert test_case['expected_output'] == 'Hello, Alice!', "Test case output should match"
        assert test_case['description'] == 'Test greeting Alice', "Test case description should match"
        
        # Verify JSON formatting (Req 5.2)
        with open(json_path, 'r', encoding='utf-8') as f:
            json_content = f.read()
        assert '  ' in json_content, "JSON should be indented"
        assert '\n' in json_content, "JSON should have line breaks"
    
    print("✅ JSON export structure test passed")


def test_markdown_export():
    """Test Markdown export.
    
    Tests Requirement 5.4:
    - Creates standalone markdown files
    - Generates README with course overview
    - Uses relative links between files
    """
    print("\n🧪 Testing Markdown export...")
    
    # Create test course and config
    course = create_test_course()
    config = CourseConfig()
    export_manager = ExportManager(config)
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Export to Markdown
        readme_path = export_manager.export(course, temp_dir, format='markdown')
        
        # Verify README was created (Req 5.4)
        assert os.path.exists(readme_path), "README.md should be created"
        assert readme_path.endswith('README.md'), "Should return path to README.md"
        
        # Read README content
        with open(readme_path, 'r', encoding='utf-8') as f:
            readme_content = f.read()
        
        # Verify README contains course overview (Req 5.4)
        assert '# Python Programming Course' in readme_content, "README should have course title"
        assert 'A comprehensive course on Python programming' in readme_content, "README should have description"
        assert '**Author**: Test Author' in readme_content, "README should have author"
        assert '**Version**: 1.0.0' in readme_content, "README should have version"
        assert '**Total Duration**: 0.5 hours' in readme_content, "README should have duration"
        assert '**Modules**: 1' in readme_content, "README should have module count"
        assert '**Lessons**: 1' in readme_content, "README should have lesson count"
        
        # Verify module overview in README (Req 5.4)
        assert '### Python Basics' in readme_content, "README should list module"
        assert 'Learn the fundamentals of Python programming' in readme_content, "README should have module description"
        
        # Verify relative links in README (Req 5.4)
        assert 'python-basics/introduction-to-functions.md' in readme_content, "README should have relative link to lesson"
        assert '[Introduction to Functions]' in readme_content, "README should have lesson link text"
        
        # Verify module directory was created (Req 5.4)
        module_dir = os.path.join(temp_dir, 'python-basics')
        assert os.path.exists(module_dir), "Module directory should be created"
        assert os.path.isdir(module_dir), "Module path should be a directory"
        
        # Verify lesson file was created (Req 5.4)
        lesson_path = os.path.join(module_dir, 'introduction-to-functions.md')
        assert os.path.exists(lesson_path), "Lesson markdown file should be created"
        
        # Read lesson content
        with open(lesson_path, 'r', encoding='utf-8') as f:
            lesson_content = f.read()
        
        # Verify lesson has navigation breadcrumb with relative link (Req 5.4)
        assert '[← Back to Course](./../README.md)' in lesson_content, "Lesson should have back link to README"
        
        # Verify lesson structure (Req 5.4)
        assert '# Introduction to Functions' in lesson_content, "Lesson should have title"
        assert '**Module**: Python Basics' in lesson_content, "Lesson should show module"
        assert '**Difficulty**: beginner' in lesson_content, "Lesson should show difficulty"
        assert '**Duration**: 30 minutes' in lesson_content, "Lesson should show duration"
        
        # Verify lesson sections (Req 5.4)
        assert '## Learning Objectives' in lesson_content, "Lesson should have learning objectives section"
        assert 'Understand function syntax' in lesson_content, "Should include learning objective"
        assert '## Prerequisites' in lesson_content, "Lesson should have prerequisites section"
        assert 'Basic Python syntax' in lesson_content, "Should include prerequisite"
        assert '## Introduction' in lesson_content, "Lesson should have introduction section"
        assert '## Explanation' in lesson_content, "Lesson should have explanation section"
        assert '## Code Example' in lesson_content, "Lesson should have code example section"
        assert '## Walkthrough' in lesson_content, "Lesson should have walkthrough section"
        assert '## Summary' in lesson_content, "Lesson should have summary section"
        
        # Verify code block formatting (Req 5.4)
        assert '```python' in lesson_content, "Should have Python code block"
        assert "def hello():" in lesson_content, "Should include code example"
        
        # Verify exercises section (Req 5.4)
        assert '## Exercises' in lesson_content, "Lesson should have exercises section"
        assert '### Exercise 1: Write a greeting function' in lesson_content, "Should include exercise title"
        assert '#### Instructions' in lesson_content, "Exercise should have instructions"
        assert '#### Starter Code' in lesson_content, "Exercise should have starter code"
    
    print("✅ Markdown export test passed")


def test_nextjs_export():
    """Test Next.js export.
    
    Tests Requirement 5.3:
    - Generates Next.js project structure
    - Creates React components for lessons
    - Generates course data as JSON
    - Creates navigation component
    """
    print("\n🧪 Testing Next.js export...")
    
    # Create test course and config
    course = create_test_course()
    config = CourseConfig()
    export_manager = ExportManager(config)
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Export to Next.js
        nextjs_path = export_manager.export(course, temp_dir, format='nextjs')
        
        # Verify Next.js project structure was created (Req 5.3)
        assert os.path.exists(nextjs_path), "Next.js project directory should be created"
        
        # Verify standard Next.js directories (Req 5.3)
        app_dir = os.path.join(nextjs_path, 'app')
        components_dir = os.path.join(nextjs_path, 'components')
        data_dir = os.path.join(nextjs_path, 'data')
        public_dir = os.path.join(nextjs_path, 'public')
        styles_dir = os.path.join(nextjs_path, 'styles')
        
        assert os.path.exists(app_dir), "app/ directory should be created"
        assert os.path.exists(components_dir), "components/ directory should be created"
        assert os.path.exists(data_dir), "data/ directory should be created"
        assert os.path.exists(public_dir), "public/ directory should be created"
        assert os.path.exists(styles_dir), "styles/ directory should be created"
        
        # Verify course data JSON was generated (Req 5.3)
        course_data_path = os.path.join(data_dir, 'course.json')
        assert os.path.exists(course_data_path), "course.json should be created in data/"
        
        # Verify course data structure
        with open(course_data_path, 'r', encoding='utf-8') as f:
            course_data = json.load(f)
        assert course_data['course_id'] == 'course-1', "Course data should match"
        assert course_data['title'] == 'Python Programming Course', "Course title should match"
        
        # Verify React components were created (Req 5.3)
        lesson_card_path = os.path.join(components_dir, 'LessonCard.tsx')
        lesson_content_path = os.path.join(components_dir, 'LessonContent.tsx')
        navigation_path = os.path.join(components_dir, 'Navigation.tsx')
        
        assert os.path.exists(lesson_card_path), "LessonCard component should be created"
        assert os.path.exists(lesson_content_path), "LessonContent component should be created"
        assert os.path.exists(navigation_path), "Navigation component should be created (Req 5.3)"
        
        # Verify LessonCard component structure (Req 5.3)
        with open(lesson_card_path, 'r', encoding='utf-8') as f:
            lesson_card_content = f.read()
        assert 'interface LessonCardProps' in lesson_card_content, "Should define props interface"
        assert 'export default function LessonCard' in lesson_card_content, "Should export component"
        assert 'title: string' in lesson_card_content, "Should accept title prop"
        assert 'difficulty: string' in lesson_card_content, "Should accept difficulty prop"
        assert 'duration: number' in lesson_card_content, "Should accept duration prop"
        
        # Verify LessonContent component structure (Req 5.3)
        with open(lesson_content_path, 'r', encoding='utf-8') as f:
            lesson_content_content = f.read()
        assert 'interface LessonContentProps' in lesson_content_content, "Should define props interface"
        assert 'export default function LessonContent' in lesson_content_content, "Should export component"
        assert 'SyntaxHighlighter' in lesson_content_content, "Should use syntax highlighter for code"
        assert 'learning_objectives' in lesson_content_content, "Should render learning objectives"
        assert 'code_example' in lesson_content_content, "Should render code examples"
        assert 'exercises' in lesson_content_content, "Should render exercises"
        
        # Verify Navigation component structure (Req 5.3)
        with open(navigation_path, 'r', encoding='utf-8') as f:
            navigation_content = f.read()
        assert 'interface NavigationProps' in navigation_content, "Should define props interface"
        assert 'export default function Navigation' in navigation_content, "Should export component"
        assert 'course: any' in navigation_content, "Should accept course prop"
        assert 'course.modules' in navigation_content, "Should iterate over modules"
        assert 'module.lessons' in navigation_content, "Should iterate over lessons"
        assert 'Link href' in navigation_content, "Should use Next.js Link component"
        
        # Verify package.json was created (Req 5.3)
        package_json_path = os.path.join(nextjs_path, 'package.json')
        assert os.path.exists(package_json_path), "package.json should be created"
        
        # Verify package.json structure
        with open(package_json_path, 'r', encoding='utf-8') as f:
            package_data = json.load(f)
        assert package_data['name'] == 'python-programming-course', "Package name should be slugified course title"
        assert package_data['version'] == '1.0.0', "Package version should match course version"
        assert 'scripts' in package_data, "Should include scripts"
        assert 'dev' in package_data['scripts'], "Should include dev script"
        assert 'build' in package_data['scripts'], "Should include build script"
        assert 'dependencies' in package_data, "Should include dependencies"
        assert 'next' in package_data['dependencies'], "Should include Next.js dependency"
        assert 'react' in package_data['dependencies'], "Should include React dependency"
        assert 'react-syntax-highlighter' in package_data['dependencies'], "Should include syntax highlighter"
    
    print("✅ Next.js export test passed")


def test_export_error_handling():
    """Test export error handling.
    
    Tests Requirement 5.1:
    - Validates format is supported
    - Validates output directory permissions
    - Returns clear error messages
    """
    print("\n🧪 Testing export error handling...")
    
    # Create test course and config
    course = create_test_course()
    config = CourseConfig()
    export_manager = ExportManager(config)
    
    # Test 1: Unsupported format (Req 5.1)
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            export_manager.export(course, temp_dir, format='invalid_format')
            assert False, "Should raise ValueError for unsupported format"
        except ValueError as e:
            assert 'Unsupported export format' in str(e), "Error message should mention unsupported format"
            assert 'invalid_format' in str(e), "Error message should include the invalid format"
            assert 'Supported formats' in str(e), "Error message should list supported formats"
    
    # Test 2: Invalid output directory (Req 5.1)
    # Use a path that cannot be created (e.g., under a file instead of directory)
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a file
        file_path = os.path.join(temp_dir, 'test_file.txt')
        with open(file_path, 'w') as f:
            f.write('test')
        
        # Try to create a directory under the file (should fail)
        invalid_dir = os.path.join(file_path, 'subdir')
        try:
            export_manager.export(course, invalid_dir, format='json')
            assert False, "Should raise OSError for invalid directory"
        except OSError as e:
            assert 'Cannot create output directory' in str(e) or 'not a directory' in str(e).lower(), \
                "Error message should mention directory creation failure"
    
    # Test 3: Format validation is case-insensitive (Req 5.1)
    with tempfile.TemporaryDirectory() as temp_dir:
        # Should work with uppercase format
        json_path = export_manager.export(course, temp_dir, format='JSON')
        assert os.path.exists(json_path), "Should handle uppercase format"
        
        # Should work with mixed case
        temp_dir2 = os.path.join(temp_dir, 'test2')
        os.makedirs(temp_dir2)
        json_path2 = export_manager.export(course, temp_dir2, format='Json')
        assert os.path.exists(json_path2), "Should handle mixed case format"
    
    # Test 4: Supported formats list (Req 5.1)
    assert 'mkdocs' in ExportManager.SUPPORTED_FORMATS, "Should support mkdocs"
    assert 'json' in ExportManager.SUPPORTED_FORMATS, "Should support json"
    assert 'markdown' in ExportManager.SUPPORTED_FORMATS, "Should support markdown"
    assert 'nextjs' in ExportManager.SUPPORTED_FORMATS, "Should support nextjs"
    assert 'pdf' in ExportManager.SUPPORTED_FORMATS, "Should support pdf"
    
    print("✅ Export error handling test passed")


def test_default_export_format():
    """Test that default export format is used when format is not specified."""
    print("\n🧪 Testing default export format...")
    
    # Create test course and config
    course = create_test_course()
    config = CourseConfig()
    export_manager = ExportManager(config)
    
    # Export without specifying format (should use default)
    with tempfile.TemporaryDirectory() as temp_dir:
        result_path = export_manager.export(course, temp_dir)
        
        # Default format should be mkdocs
        assert result_path.endswith('mkdocs.yml'), "Default export should be mkdocs"
        assert os.path.exists(result_path), "Default export should create files"
    
    print("✅ Default export format test passed")


if __name__ == '__main__':
    print("=" * 60)
    print("Running Export Formats Tests")
    print("=" * 60)
    
    test_json_export_structure()
    test_markdown_export()
    test_nextjs_export()
    test_export_error_handling()
    test_default_export_format()
    
    print("\n" + "=" * 60)
    print("✅ All export format tests passed!")
    print("=" * 60)
