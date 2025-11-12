"""Integration tests for MkDocs Exporter.

Tests Requirements 4.1, 4.2, 4.3, 4.4, 4.5:
- Directory structure creation
- mkdocs.yml generation
- Lesson file generation
- Navigation structure
"""

import os
import tempfile
import shutil
import yaml
from datetime import datetime
from src.course.exporters.mkdocs_exporter import MkDocsExporter
from src.course.config import CourseConfig
from src.course.models import (
    CourseOutline, Module, Lesson, LessonContent, 
    CodeExample, Exercise, TestCase
)


def create_test_course():
    """Create a test course with multiple modules and lessons."""
    # Create code examples
    code_example1 = CodeExample(
        code="def hello():\n    print('Hello, World!')",
        language="python",
        filename="hello.py"
    )
    
    code_example2 = CodeExample(
        code="def add(a, b):\n    return a + b",
        language="python",
        filename="math_ops.py"
    )
    
    # Create lesson content
    lesson_content1 = LessonContent(
        introduction="Learn about functions",
        explanation="Functions are reusable blocks of code",
        code_example=code_example1,
        walkthrough="This function prints a greeting",
        summary="You learned about basic functions"
    )
    
    lesson_content2 = LessonContent(
        introduction="Learn about parameters",
        explanation="Functions can accept parameters",
        code_example=code_example2,
        walkthrough="This function adds two numbers",
        summary="You learned about function parameters"
    )
    
    # Create exercises
    exercise1 = Exercise(
        exercise_id="ex-1",
        title="Write a greeting function",
        description="Create a function that greets a user by name",
        difficulty="beginner",
        estimated_minutes=10,
        instructions=["Define a function called greet", "Accept a name parameter", "Print a greeting"],
        starter_code="def greet(name):\n    # Your code here\n    pass",
        solution_code="def greet(name):\n    print(f'Hello, {name}!')",
        test_cases=[
            TestCase(
                input="Alice",
                expected_output="Hello, Alice!",
                description="Test greeting Alice"
            )
        ]
    )
    
    # Create lessons
    lesson1 = Lesson(
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
        content=lesson_content1,
        exercises=[exercise1],
        tags=["functions", "basics"]
    )
    
    lesson2 = Lesson(
        lesson_id="lesson-2",
        title="Function Parameters",
        description="Learn about function parameters",
        order=1,
        difficulty="beginner",
        duration_minutes=45,
        file_path="src/math_ops.py",
        teaching_value=0.9,
        learning_objectives=["Use function parameters", "Return values"],
        content=lesson_content2,
        tags=["functions", "parameters"]
    )
    
    lesson3 = Lesson(
        lesson_id="lesson-3",
        title="Advanced Functions",
        description="Learn advanced function concepts",
        order=0,
        difficulty="intermediate",
        duration_minutes=60,
        file_path="src/advanced.py",
        teaching_value=0.85,
        learning_objectives=["Use decorators", "Understand closures"],
        tags=["functions", "advanced"]
    )
    
    # Create modules
    module1 = Module(
        module_id="module-1",
        title="Python Basics",
        description="Learn Python fundamentals",
        order=0,
        lessons=[lesson1, lesson2],
        difficulty="beginner",
        duration_hours=1.25
    )
    
    module2 = Module(
        module_id="module-2",
        title="Advanced Python",
        description="Advanced Python concepts",
        order=1,
        lessons=[lesson3],
        difficulty="intermediate",
        duration_hours=1.0
    )
    
    # Create course outline
    course = CourseOutline(
        course_id="course-1",
        title="Learn Python Programming",
        description="A comprehensive Python course for beginners and intermediate learners",
        author="Test Author",
        version="1.0.0",
        created_at=datetime.now(),
        modules=[module1, module2],
        total_duration_hours=2.25,
        difficulty_distribution={"beginner": 2, "intermediate": 1},
        prerequisites=["Basic computer skills"],
        tags=["python", "programming"]
    )
    
    return course


def test_directory_structure_creation():
    """Test that MkDocs export creates correct directory structure.
    
    Tests Requirement 4.1: Directory structure creation
    """
    config = CourseConfig()
    course = create_test_course()
    temp_dir = tempfile.mkdtemp()
    
    try:
        exporter = MkDocsExporter(config)
        exporter.export_to_mkdocs(course, temp_dir)
        
        # Verify base directory exists
        assert os.path.exists(temp_dir), "Output directory should exist"
        
        # Verify docs directory exists
        docs_dir = os.path.join(temp_dir, "docs")
        assert os.path.exists(docs_dir), "docs/ directory should exist"
        
        # Verify module directories exist
        module1_dir = os.path.join(docs_dir, "python-basics")
        assert os.path.exists(module1_dir), "Module 1 directory should exist"
        
        module2_dir = os.path.join(docs_dir, "advanced-python")
        assert os.path.exists(module2_dir), "Module 2 directory should exist"
        
        print("✓ Directory structure creation test passed")
        
    finally:
        shutil.rmtree(temp_dir)


def test_mkdocs_yml_generation():
    """Test that mkdocs.yml is generated with correct configuration.
    
    Tests Requirements 4.1, 4.2, 4.3, 4.4, 4.5:
    - Valid mkdocs.yml generation
    - Theme configuration
    - Plugin configuration
    - Markdown extensions
    """
    config = CourseConfig()
    course = create_test_course()
    temp_dir = tempfile.mkdtemp()
    
    try:
        exporter = MkDocsExporter(config)
        mkdocs_path = exporter.export_to_mkdocs(course, temp_dir)
        
        # Verify mkdocs.yml exists
        assert os.path.exists(mkdocs_path), "mkdocs.yml should exist"
        assert mkdocs_path.endswith("mkdocs.yml"), "Path should end with mkdocs.yml"
        
        # Load and verify configuration
        with open(mkdocs_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        # Verify basic site information (Req 4.1)
        assert config_data['site_name'] == "Learn Python Programming", "Site name should match course title"
        assert config_data['site_author'] == "Test Author", "Site author should match course author"
        assert "comprehensive Python course" in config_data['site_description'], "Site description should match"
        
        # Verify theme configuration (Req 4.3)
        assert config_data['theme']['name'] == "material", "Should use Material theme"
        assert 'palette' in config_data['theme'], "Theme should have palette configuration"
        assert 'features' in config_data['theme'], "Theme should have features"
        assert 'search.suggest' in config_data['theme']['features'], "Should enable search suggestions (Req 4.5)"
        assert 'content.code.copy' in config_data['theme']['features'], "Should enable code copy button"
        
        # Verify plugins (Req 4.5)
        assert 'plugins' in config_data, "Should have plugins configured"
        assert 'search' in config_data['plugins'], "Should have search plugin (Req 4.5)"
        
        # Verify markdown extensions (Req 4.3)
        assert 'markdown_extensions' in config_data, "Should have markdown extensions"
        assert 'pymdownx.highlight' in config_data['markdown_extensions'], "Should have code highlighting"
        assert 'pymdownx.superfences' in config_data['markdown_extensions'], "Should have enhanced code blocks"
        assert 'toc' in config_data['markdown_extensions'], "Should have table of contents (Req 4.5)"
        
        # Verify navigation exists
        assert 'nav' in config_data, "Should have navigation structure"
        
        print("✓ mkdocs.yml generation test passed")
        
    finally:
        shutil.rmtree(temp_dir)


def test_lesson_file_generation():
    """Test that lesson markdown files are generated correctly.
    
    Tests Requirement 4.2: Lesson file generation in docs/
    """
    config = CourseConfig()
    course = create_test_course()
    temp_dir = tempfile.mkdtemp()
    
    try:
        exporter = MkDocsExporter(config)
        exporter.export_to_mkdocs(course, temp_dir)
        
        docs_dir = os.path.join(temp_dir, "docs")
        
        # Verify index.md exists
        index_path = os.path.join(docs_dir, "index.md")
        assert os.path.exists(index_path), "index.md should exist"
        
        # Verify index content
        with open(index_path, 'r', encoding='utf-8') as f:
            index_content = f.read()
        assert "Learn Python Programming" in index_content, "Index should contain course title"
        assert "Test Author" in index_content, "Index should contain author"
        assert "2.2" in index_content or "2.3" in index_content, "Index should contain total duration"
        
        # Verify lesson files in module 1
        lesson1_path = os.path.join(docs_dir, "python-basics", "introduction-to-functions.md")
        assert os.path.exists(lesson1_path), "Lesson 1 file should exist"
        
        lesson2_path = os.path.join(docs_dir, "python-basics", "function-parameters.md")
        assert os.path.exists(lesson2_path), "Lesson 2 file should exist"
        
        # Verify lesson files in module 2
        lesson3_path = os.path.join(docs_dir, "advanced-python", "advanced-functions.md")
        assert os.path.exists(lesson3_path), "Lesson 3 file should exist"
        
        # Verify lesson 1 content
        with open(lesson1_path, 'r', encoding='utf-8') as f:
            lesson1_content = f.read()
        assert "Introduction to Functions" in lesson1_content, "Lesson should contain title"
        assert "beginner" in lesson1_content, "Lesson should contain difficulty"
        assert "30 minutes" in lesson1_content, "Lesson should contain duration"
        assert "def hello()" in lesson1_content, "Lesson should contain code example"
        assert "Learning Objectives" in lesson1_content, "Lesson should contain learning objectives"
        assert "Prerequisites" in lesson1_content, "Lesson should contain prerequisites"
        assert "## Exercises" in lesson1_content, "Lesson should contain exercises section"
        assert "Write a greeting function" in lesson1_content, "Lesson should contain exercise title"
        
        # Verify lesson 2 content
        with open(lesson2_path, 'r', encoding='utf-8') as f:
            lesson2_content = f.read()
        assert "Function Parameters" in lesson2_content, "Lesson should contain title"
        assert "def add(a, b)" in lesson2_content, "Lesson should contain code example"
        
        print("✓ Lesson file generation test passed")
        
    finally:
        shutil.rmtree(temp_dir)


def test_navigation_structure():
    """Test that navigation structure is hierarchical and correct.
    
    Tests Requirement 4.2: Hierarchical navigation structure
    """
    config = CourseConfig()
    course = create_test_course()
    temp_dir = tempfile.mkdtemp()
    
    try:
        exporter = MkDocsExporter(config)
        mkdocs_path = exporter.export_to_mkdocs(course, temp_dir)
        
        # Load configuration
        with open(mkdocs_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        nav = config_data['nav']
        
        # Verify navigation structure
        assert len(nav) >= 3, "Navigation should have at least 3 items (Home + 2 modules)"
        
        # Verify Home page
        assert nav[0] == {'Home': 'index.md'}, "First nav item should be Home"
        
        # Verify module 1 structure
        module1_nav = None
        for item in nav:
            if 'Python Basics' in item:
                module1_nav = item
                break
        
        assert module1_nav is not None, "Module 1 should be in navigation"
        assert 'Python Basics' in module1_nav, "Module 1 title should be correct"
        module1_lessons = module1_nav['Python Basics']
        assert len(module1_lessons) == 2, "Module 1 should have 2 lessons"
        
        # Verify lesson paths in module 1
        lesson1_item = module1_lessons[0]
        assert 'Introduction to Functions' in lesson1_item, "Lesson 1 should be in navigation"
        assert lesson1_item['Introduction to Functions'] == 'python-basics/introduction-to-functions.md', \
            "Lesson 1 path should be correct"
        
        lesson2_item = module1_lessons[1]
        assert 'Function Parameters' in lesson2_item, "Lesson 2 should be in navigation"
        assert lesson2_item['Function Parameters'] == 'python-basics/function-parameters.md', \
            "Lesson 2 path should be correct"
        
        # Verify module 2 structure
        module2_nav = None
        for item in nav:
            if 'Advanced Python' in item:
                module2_nav = item
                break
        
        assert module2_nav is not None, "Module 2 should be in navigation"
        assert 'Advanced Python' in module2_nav, "Module 2 title should be correct"
        module2_lessons = module2_nav['Advanced Python']
        assert len(module2_lessons) == 1, "Module 2 should have 1 lesson"
        
        # Verify lesson path in module 2
        lesson3_item = module2_lessons[0]
        assert 'Advanced Functions' in lesson3_item, "Lesson 3 should be in navigation"
        assert lesson3_item['Advanced Functions'] == 'advanced-python/advanced-functions.md', \
            "Lesson 3 path should be correct"
        
        print("✓ Navigation structure test passed")
        
    finally:
        shutil.rmtree(temp_dir)


def test_mkdocs_exporter_basic():
    """Test basic MkDocs export functionality (legacy test)."""
    config = CourseConfig()
    
    # Create a simple course outline
    code_example = CodeExample(
        code="def hello():\n    print('Hello, World!')",
        language="python",
        filename="hello.py"
    )
    
    lesson_content = LessonContent(
        introduction="Learn about functions",
        explanation="Functions are reusable blocks of code",
        code_example=code_example,
        walkthrough="This function prints a greeting",
        summary="You learned about basic functions"
    )
    
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
        content=lesson_content
    )
    
    module = Module(
        module_id="module-1",
        title="Python Basics",
        description="Learn Python fundamentals",
        order=0,
        lessons=[lesson],
        difficulty="beginner",
        duration_hours=0.5
    )
    
    course = CourseOutline(
        course_id="course-1",
        title="Learn Python",
        description="A comprehensive Python course",
        author="Test Author",
        version="1.0.0",
        created_at=datetime.now(),
        modules=[module],
        total_duration_hours=0.5,
        difficulty_distribution={"beginner": 1}
    )
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        exporter = MkDocsExporter(config)
        mkdocs_path = exporter.export_to_mkdocs(course, temp_dir)
        
        # Verify mkdocs.yml was created
        assert os.path.exists(mkdocs_path)
        assert mkdocs_path.endswith("mkdocs.yml")
        
        # Verify docs directory was created
        docs_dir = os.path.join(temp_dir, "docs")
        assert os.path.exists(docs_dir)
        
        # Verify index.md was created
        index_path = os.path.join(docs_dir, "index.md")
        assert os.path.exists(index_path)
        
        # Verify module directory was created
        module_dir = os.path.join(docs_dir, "python-basics")
        assert os.path.exists(module_dir)
        
        # Verify lesson file was created
        lesson_path = os.path.join(module_dir, "introduction-to-functions.md")
        assert os.path.exists(lesson_path)
        
        # Verify lesson content
        with open(lesson_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "Introduction to Functions" in content
            assert "beginner" in content
            assert "def hello()" in content
        
        print("✓ MkDocs export basic test passed")
        
    finally:
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    test_directory_structure_creation()
    test_mkdocs_yml_generation()
    test_lesson_file_generation()
    test_navigation_structure()
    test_mkdocs_exporter_basic()
    print("\n✅ All MkDocs exporter integration tests passed!")
