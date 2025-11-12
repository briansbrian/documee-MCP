"""Tests for MkDocs configuration generation."""

import os
import tempfile
import shutil
import yaml
from datetime import datetime
from src.course.exporters.mkdocs_exporter import MkDocsExporter
from src.course.config import CourseConfig
from src.course.models import (
    CourseOutline, Module, Lesson, LessonContent, CodeExample
)


def test_mkdocs_config_structure():
    """Test that mkdocs.yml has correct structure and all required fields."""
    config = CourseConfig()
    
    # Create minimal course
    code_example = CodeExample(code="print('test')", language="python", filename="test.py")
    lesson_content = LessonContent(
        introduction="Intro",
        explanation="Explanation",
        code_example=code_example,
        walkthrough="Walk",
        summary="Summary"
    )
    
    lesson = Lesson(
        lesson_id="l1",
        title="Test Lesson",
        description="Test",
        order=0,
        difficulty="beginner",
        duration_minutes=30,
        file_path="test.py",
        teaching_value=0.8,
        learning_objectives=["Learn"],
        content=lesson_content
    )
    
    module = Module(
        module_id="m1",
        title="Test Module",
        description="Test",
        order=0,
        lessons=[lesson],
        difficulty="beginner",
        duration_hours=0.5
    )
    
    course = CourseOutline(
        course_id="c1",
        title="Test Course",
        description="A test course",
        author="Test Author",
        version="1.0.0",
        created_at=datetime.now(),
        modules=[module],
        total_duration_hours=0.5
    )
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        exporter = MkDocsExporter(config)
        mkdocs_path = exporter.export_to_mkdocs(course, temp_dir)
        
        # Load and verify mkdocs.yml
        with open(mkdocs_path, 'r', encoding='utf-8') as f:
            mkdocs_config = yaml.safe_load(f)
        
        # Verify basic site information (Req 4.1)
        assert mkdocs_config['site_name'] == "Test Course"
        assert mkdocs_config['site_description'] == "A test course"
        assert mkdocs_config['site_author'] == "Test Author"
        
        # Verify theme configuration (Req 4.3)
        assert mkdocs_config['theme']['name'] == "material"
        assert 'palette' in mkdocs_config['theme']
        assert 'features' in mkdocs_config['theme']
        
        # Verify theme features (Req 4.4, 4.5)
        features = mkdocs_config['theme']['features']
        assert "navigation.tabs" in features
        assert "navigation.sections" in features
        assert "search.suggest" in features
        assert "content.code.copy" in features
        
        # Verify plugins (Req 4.5)
        assert "search" in mkdocs_config['plugins']
        assert "tags" in mkdocs_config['plugins']
        
        # Verify markdown extensions (Req 4.3)
        extensions = mkdocs_config['markdown_extensions']
        assert "pymdownx.highlight" in extensions
        assert "pymdownx.superfences" in extensions
        assert "admonition" in extensions
        assert "toc" in extensions
        
        # Verify navigation structure (Req 4.2)
        nav = mkdocs_config['nav']
        assert len(nav) >= 2  # Home + at least one module
        assert nav[0] == {"Home": "index.md"}
        
        # Verify module in navigation
        module_nav = nav[1]
        assert "Test Module" in module_nav
        assert isinstance(module_nav["Test Module"], list)
        assert len(module_nav["Test Module"]) == 1
        
        print("✓ MkDocs configuration structure test passed")
        
    finally:
        shutil.rmtree(temp_dir)


def test_mkdocs_navigation_hierarchy():
    """Test that navigation is properly hierarchical with modules and lessons."""
    config = CourseConfig()
    
    # Create course with multiple modules and lessons
    lessons_m1 = []
    for i in range(3):
        code_example = CodeExample(code=f"# Lesson {i}", language="python", filename=f"l{i}.py")
        content = LessonContent(
            introduction=f"Intro {i}",
            explanation=f"Explanation {i}",
            code_example=code_example,
            walkthrough=f"Walk {i}",
            summary=f"Summary {i}"
        )
        lesson = Lesson(
            lesson_id=f"l{i}",
            title=f"Lesson {i}",
            description=f"Test lesson {i}",
            order=i,
            difficulty="beginner",
            duration_minutes=30,
            file_path=f"test{i}.py",
            teaching_value=0.8,
            learning_objectives=[f"Learn {i}"],
            content=content
        )
        lessons_m1.append(lesson)
    
    module1 = Module(
        module_id="m1",
        title="Module One",
        description="First module",
        order=0,
        lessons=lessons_m1,
        difficulty="beginner",
        duration_hours=1.5
    )
    
    lessons_m2 = []
    for i in range(2):
        code_example = CodeExample(code=f"# Lesson {i}", language="python", filename=f"l{i}.py")
        content = LessonContent(
            introduction=f"Intro {i}",
            explanation=f"Explanation {i}",
            code_example=code_example,
            walkthrough=f"Walk {i}",
            summary=f"Summary {i}"
        )
        lesson = Lesson(
            lesson_id=f"l{i+3}",
            title=f"Advanced Lesson {i}",
            description=f"Advanced lesson {i}",
            order=i,
            difficulty="advanced",
            duration_minutes=45,
            file_path=f"adv{i}.py",
            teaching_value=0.9,
            learning_objectives=[f"Master {i}"],
            content=content
        )
        lessons_m2.append(lesson)
    
    module2 = Module(
        module_id="m2",
        title="Module Two",
        description="Second module",
        order=1,
        lessons=lessons_m2,
        difficulty="advanced",
        duration_hours=1.5
    )
    
    course = CourseOutline(
        course_id="c1",
        title="Multi-Module Course",
        description="Course with multiple modules",
        author="Test Author",
        version="1.0.0",
        created_at=datetime.now(),
        modules=[module1, module2],
        total_duration_hours=3.0
    )
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        exporter = MkDocsExporter(config)
        mkdocs_path = exporter.export_to_mkdocs(course, temp_dir)
        
        # Load mkdocs.yml
        with open(mkdocs_path, 'r', encoding='utf-8') as f:
            mkdocs_config = yaml.safe_load(f)
        
        nav = mkdocs_config['nav']
        
        # Verify structure: Home + 2 modules
        assert len(nav) == 3
        assert nav[0] == {"Home": "index.md"}
        
        # Verify Module One
        module1_nav = nav[1]
        assert "Module One" in module1_nav
        assert len(module1_nav["Module One"]) == 3  # 3 lessons
        
        # Verify Module Two
        module2_nav = nav[2]
        assert "Module Two" in module2_nav
        assert len(module2_nav["Module Two"]) == 2  # 2 lessons
        
        # Verify lesson files exist
        docs_dir = os.path.join(temp_dir, "docs")
        
        # Check Module One lessons
        module1_dir = os.path.join(docs_dir, "module-one")
        assert os.path.exists(module1_dir)
        assert os.path.exists(os.path.join(module1_dir, "lesson-0.md"))
        assert os.path.exists(os.path.join(module1_dir, "lesson-1.md"))
        assert os.path.exists(os.path.join(module1_dir, "lesson-2.md"))
        
        # Check Module Two lessons
        module2_dir = os.path.join(docs_dir, "module-two")
        assert os.path.exists(module2_dir)
        assert os.path.exists(os.path.join(module2_dir, "advanced-lesson-0.md"))
        assert os.path.exists(os.path.join(module2_dir, "advanced-lesson-1.md"))
        
        print("✓ MkDocs navigation hierarchy test passed")
        
    finally:
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    test_mkdocs_config_structure()
    test_mkdocs_navigation_hierarchy()
    print("\nAll MkDocs configuration tests passed!")
