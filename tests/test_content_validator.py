"""Unit tests for Content Validator.

Tests Requirements 13.1, 13.2, 13.3, 13.4, 13.5:
- Validates each lesson has learning objectives
- Validates each lesson has code examples
- Validates exercise starter code syntax
- Validates internal links
- Generates validation report with issues
"""

import pytest
from datetime import datetime
from src.course.content_validator import ContentValidator, ValidationIssue, ValidationReport
from src.course.models import (
    CourseOutline,
    Module,
    Lesson,
    LessonContent,
    CodeExample,
    Exercise,
    TestCase
)


# ========== Test Fixtures ==========

@pytest.fixture
def validator():
    """Create a content validator instance."""
    return ContentValidator()


@pytest.fixture
def valid_code_example():
    """Create a valid code example."""
    return CodeExample(
        code="""def hello_world():
    \"\"\"Print hello world.\"\"\"
    print("Hello, World!")
    return True""",
        language="python",
        filename="example.py",
        highlights=[],
        annotations={}
    )


@pytest.fixture
def valid_lesson_content(valid_code_example):
    """Create valid lesson content."""
    return LessonContent(
        introduction="This lesson teaches basic functions.",
        explanation="Functions are reusable blocks of code.",
        code_example=valid_code_example,
        walkthrough="Let's walk through this function step by step.",
        summary="You learned how to create basic functions.",
        further_reading=[]
    )


@pytest.fixture
def valid_lesson(valid_lesson_content):
    """Create a valid lesson."""
    return Lesson(
        lesson_id="lesson_001",
        title="Introduction to Functions",
        description="Learn how to create functions",
        order=0,
        difficulty="beginner",
        duration_minutes=30,
        file_path="src/example.py",
        teaching_value=0.8,
        learning_objectives=[
            "Understand function syntax",
            "Implement basic functions",
            "Apply functions to solve problems"
        ],
        prerequisites=[],
        concepts=["functions", "parameters", "return values"],
        content=valid_lesson_content,
        exercises=[],
        tags=["python", "functions"]
    )


@pytest.fixture
def valid_exercise():
    """Create a valid exercise."""
    return Exercise(
        exercise_id="ex_001",
        title="Create a Function",
        description="Practice creating functions",
        difficulty="beginner",
        estimated_minutes=15,
        instructions=[
            "Define a function named greet",
            "Add a parameter for name",
            "Return a greeting message"
        ],
        starter_code="""def greet(name):
    # TODO: Return greeting message
    pass""",
        solution_code="""def greet(name):
    return f"Hello, {name}!"
""",
        hints=["Use f-string formatting", "Return the string"],
        test_cases=[
            TestCase(
                input="greet('Alice')",
                expected_output="Hello, Alice!",
                description="Test with name Alice"
            )
        ],
        learning_objectives=["Implement functions with parameters"]
    )


@pytest.fixture
def valid_module(valid_lesson):
    """Create a valid module."""
    return Module(
        module_id="mod_001",
        title="Python Basics",
        description="Learn Python fundamentals",
        order=0,
        lessons=[valid_lesson],
        difficulty="beginner",
        duration_hours=2.0,
        learning_objectives=["Master Python basics"]
    )


@pytest.fixture
def valid_course(valid_module):
    """Create a valid course."""
    return CourseOutline(
        course_id="course_001",
        title="Python Programming",
        description="Complete Python course",
        author="Test Author",
        version="1.0.0",
        created_at=datetime.now(),
        modules=[valid_module],
        total_duration_hours=2.0,
        difficulty_distribution={"beginner": 1, "intermediate": 0, "advanced": 0},
        tags=["python"],
        prerequisites=[]
    )


# ========== Requirement 13.1: Test Learning Objectives Validation ==========

def test_validate_lesson_with_no_objectives(validator, valid_lesson):
    """Test validation fails when lesson has no learning objectives."""
    valid_lesson.learning_objectives = []
    
    report = validator.validate_lesson(valid_lesson)
    
    assert not report.passed
    assert report.errors > 0
    assert any(
        issue.category == 'learning_objectives' and issue.severity == 'error'
        for issue in report.issues
    )


def test_validate_lesson_with_one_objective(validator, valid_lesson):
    """Test validation warns when lesson has only one objective."""
    valid_lesson.learning_objectives = ["Understand functions"]
    
    report = validator.validate_lesson(valid_lesson)
    
    assert report.warnings > 0
    assert any(
        issue.category == 'learning_objectives' and 'only 1' in issue.message
        for issue in report.issues
    )


def test_validate_lesson_with_too_many_objectives(validator, valid_lesson):
    """Test validation warns when lesson has too many objectives."""
    valid_lesson.learning_objectives = [
        f"Objective {i}" for i in range(10)
    ]
    
    report = validator.validate_lesson(valid_lesson)
    
    assert report.warnings > 0
    assert any(
        issue.category == 'learning_objectives' and 'recommended: 3-5' in issue.message
        for issue in report.issues
    )


def test_validate_objective_without_action_verb(validator, valid_lesson):
    """Test validation provides info when objective doesn't start with action verb."""
    valid_lesson.learning_objectives = [
        "Functions are important",
        "The basics of Python"
    ]
    
    report = validator.validate_lesson(valid_lesson)
    
    assert report.info > 0
    assert any(
        issue.category == 'learning_objectives' and "doesn't start with action verb" in issue.message
        for issue in report.issues
    )


def test_validate_objectives_with_action_verbs(validator, valid_lesson):
    """Test validation passes with proper action verbs."""
    valid_lesson.learning_objectives = [
        "Understand function syntax",
        "Implement basic functions",
        "Apply functions to problems"
    ]
    
    report = validator.validate_lesson(valid_lesson)
    
    # Should not have errors about action verbs
    action_verb_issues = [
        issue for issue in report.issues
        if issue.category == 'learning_objectives' and 'action verb' in issue.message
    ]
    assert len(action_verb_issues) == 0


# ========== Requirement 13.2: Test Code Examples Validation ==========

def test_validate_lesson_with_no_content(validator, valid_lesson):
    """Test validation fails when lesson has no content."""
    valid_lesson.content = None
    
    report = validator.validate_lesson(valid_lesson)
    
    assert not report.passed
    assert report.errors > 0
    assert any(
        issue.category == 'code_examples' and 'no content' in issue.message
        for issue in report.issues
    )


def test_validate_lesson_with_no_code_example(validator, valid_lesson):
    """Test validation fails when lesson has no code example."""
    valid_lesson.content.code_example = None
    
    report = validator.validate_lesson(valid_lesson)
    
    assert not report.passed
    assert report.errors > 0
    assert any(
        issue.category == 'code_examples' and 'no code example' in issue.message
        for issue in report.issues
    )


def test_validate_lesson_with_empty_code_example(validator, valid_lesson):
    """Test validation fails when code example is empty."""
    valid_lesson.content.code_example.code = ""
    
    report = validator.validate_lesson(valid_lesson)
    
    assert not report.passed
    assert report.errors > 0
    assert any(
        issue.category == 'code_examples' and 'empty code example' in issue.message
        for issue in report.issues
    )


def test_validate_code_example_too_short(validator, valid_lesson):
    """Test validation warns when code example is very short."""
    valid_lesson.content.code_example.code = "x = 1\ny = 2"
    
    report = validator.validate_lesson(valid_lesson)
    
    assert report.warnings > 0
    assert any(
        issue.category == 'code_examples' and 'very short' in issue.message
        for issue in report.issues
    )


def test_validate_code_example_too_long(validator, valid_lesson):
    """Test validation warns when code example exceeds 50 lines."""
    # Create code with 60 lines
    long_code = "\n".join([f"line_{i} = {i}" for i in range(60)])
    valid_lesson.content.code_example.code = long_code
    
    report = validator.validate_lesson(valid_lesson)
    
    assert report.warnings > 0
    assert any(
        issue.category == 'code_examples' and 'very long' in issue.message and '≤50' in issue.message
        for issue in report.issues
    )


def test_validate_code_example_no_language(validator, valid_lesson):
    """Test validation warns when language is not specified."""
    valid_lesson.content.code_example.language = None
    
    report = validator.validate_lesson(valid_lesson)
    
    assert report.warnings > 0
    assert any(
        issue.category == 'code_examples' and 'no language specified' in issue.message
        for issue in report.issues
    )


# ========== Requirement 13.3: Test Exercise Syntax Validation ==========

def test_validate_exercise_with_no_starter_code(validator, valid_lesson, valid_exercise):
    """Test validation fails when exercise has no starter code."""
    valid_exercise.starter_code = None
    valid_lesson.exercises = [valid_exercise]
    
    report = validator.validate_lesson(valid_lesson)
    
    assert not report.passed
    assert report.errors > 0
    assert any(
        issue.category == 'syntax' and 'no starter code' in issue.message
        for issue in report.issues
    )


def test_validate_exercise_with_valid_python_syntax(validator, valid_lesson, valid_exercise):
    """Test validation passes with valid Python syntax."""
    valid_exercise.starter_code = """def add(a, b):
    # TODO: Implement addition
    pass"""
    valid_lesson.exercises = [valid_exercise]
    
    report = validator.validate_lesson(valid_lesson)
    
    # Should not have syntax errors
    syntax_errors = [
        issue for issue in report.issues
        if issue.category == 'syntax' and issue.severity == 'error'
    ]
    assert len(syntax_errors) == 0


def test_validate_exercise_with_invalid_python_syntax(validator, valid_lesson, valid_exercise):
    """Test validation fails with invalid Python syntax."""
    valid_exercise.starter_code = """def broken_func(
    # Missing closing parenthesis
    pass"""
    valid_lesson.exercises = [valid_exercise]
    
    report = validator.validate_lesson(valid_lesson)
    
    assert not report.passed
    assert report.errors > 0
    assert any(
        issue.category == 'syntax' and 'syntax error' in issue.message
        for issue in report.issues
    )


def test_validate_exercise_solution_syntax(validator, valid_lesson, valid_exercise):
    """Test validation checks solution code syntax."""
    valid_exercise.solution_code = """def broken():
    return "missing quote"""
    valid_lesson.exercises = [valid_exercise]
    
    report = validator.validate_lesson(valid_lesson)
    
    # Should validate solution code
    syntax_issues = [
        issue for issue in report.issues
        if issue.category == 'syntax' and 'solution code' in issue.message
    ]
    assert len(syntax_issues) > 0


def test_validate_javascript_syntax_unmatched_braces(validator, valid_lesson, valid_exercise):
    """Test validation detects unmatched braces in JavaScript."""
    valid_lesson.content.code_example.language = "javascript"
    valid_exercise.starter_code = """function test() {
    console.log("missing closing brace");
"""
    valid_lesson.exercises = [valid_exercise]
    
    report = validator.validate_lesson(valid_lesson)
    
    assert not report.passed
    assert any(
        issue.category == 'syntax' and 'unmatched braces' in issue.message
        for issue in report.issues
    )


def test_validate_javascript_syntax_unmatched_parentheses(validator, valid_lesson, valid_exercise):
    """Test validation detects unmatched parentheses in JavaScript."""
    valid_lesson.content.code_example.language = "javascript"
    valid_exercise.starter_code = """function test( {
    console.log("missing paren");
}"""
    valid_lesson.exercises = [valid_exercise]
    
    report = validator.validate_lesson(valid_lesson)
    
    assert not report.passed
    assert any(
        issue.category == 'syntax' and 'unmatched parentheses' in issue.message
        for issue in report.issues
    )


# ========== Requirement 13.4: Test Internal Links Validation ==========

def test_validate_invalid_prerequisite_link(validator, valid_course):
    """Test validation fails when prerequisite references non-existent lesson."""
    lesson = valid_course.modules[0].lessons[0]
    lesson.prerequisites = ["non_existent_lesson_id"]
    
    report = validator.validate_course(valid_course)
    
    assert not report.passed
    assert report.errors > 0
    assert any(
        issue.category == 'links' and 'invalid prerequisite' in issue.message
        for issue in report.issues
    )


def test_validate_circular_prerequisites(validator, valid_course, valid_lesson):
    """Test validation detects circular prerequisite dependencies."""
    # Create two lessons with circular dependencies
    lesson1 = valid_lesson
    lesson1.lesson_id = "lesson_001"
    lesson1.prerequisites = ["lesson_002"]
    
    lesson2 = Lesson(
        lesson_id="lesson_002",
        title="Advanced Functions",
        description="Advanced topics",
        order=1,
        difficulty="intermediate",
        duration_minutes=45,
        file_path="src/advanced.py",
        teaching_value=0.85,
        learning_objectives=["Master advanced functions"],
        prerequisites=["lesson_001"],  # Circular!
        concepts=["advanced"],
        content=valid_lesson.content,
        exercises=[],
        tags=["python"]
    )
    
    valid_course.modules[0].lessons = [lesson1, lesson2]
    
    report = validator.validate_course(valid_course)
    
    assert not report.passed
    assert any(
        issue.category == 'links' and 'circular' in issue.message
        for issue in report.issues
    )


def test_validate_markdown_links_in_content(validator, valid_course):
    """Test validation checks markdown links in lesson content."""
    lesson = valid_course.modules[0].lessons[0]
    lesson.content.introduction = "See [this lesson](non-existent-lesson) for more."
    
    report = validator.validate_course(valid_course)
    
    # Should warn about potentially broken link
    link_warnings = [
        issue for issue in report.issues
        if issue.category == 'links' and 'broken internal link' in issue.message
    ]
    assert len(link_warnings) > 0


def test_validate_external_links_ignored(validator, valid_course):
    """Test validation ignores external HTTP links."""
    lesson = valid_course.modules[0].lessons[0]
    lesson.content.introduction = "Visit [Python docs](https://python.org) for more."
    
    report = validator.validate_course(valid_course)
    
    # Should not flag external links
    link_issues = [
        issue for issue in report.issues
        if issue.category == 'links' and 'python.org' in issue.message
    ]
    assert len(link_issues) == 0


# ========== Requirement 13.5: Test Validation Reporting ==========

def test_validation_report_structure(validator, valid_course):
    """Test validation report has correct structure."""
    report = validator.validate_course(valid_course)
    
    assert hasattr(report, 'total_issues')
    assert hasattr(report, 'errors')
    assert hasattr(report, 'warnings')
    assert hasattr(report, 'info')
    assert hasattr(report, 'issues')
    assert hasattr(report, 'passed')


def test_validation_report_to_dict(validator, valid_course):
    """Test validation report converts to dictionary."""
    report = validator.validate_course(valid_course)
    report_dict = report.to_dict()
    
    assert 'total_issues' in report_dict
    assert 'errors' in report_dict
    assert 'warnings' in report_dict
    assert 'info' in report_dict
    assert 'passed' in report_dict
    assert 'issues' in report_dict
    assert isinstance(report_dict['issues'], list)


def test_validation_issue_includes_file_path(validator, valid_lesson):
    """Test validation issues include file path."""
    valid_lesson.learning_objectives = []
    
    report = validator.validate_lesson(valid_lesson)
    
    assert len(report.issues) > 0
    issue = report.issues[0]
    assert issue.file_path == valid_lesson.file_path


def test_validation_issue_includes_suggestion(validator, valid_lesson):
    """Test validation issues include suggestions."""
    valid_lesson.learning_objectives = []
    
    report = validator.validate_lesson(valid_lesson)
    
    assert len(report.issues) > 0
    issue = report.issues[0]
    assert issue.suggestion is not None
    assert len(issue.suggestion) > 0


def test_validation_report_text_format(validator, valid_course):
    """Test validation report generates readable text."""
    # Create course with some issues
    lesson = valid_course.modules[0].lessons[0]
    lesson.learning_objectives = []  # Create an error
    
    report = validator.validate_course(valid_course)
    report_text = validator.generate_report_text()
    
    assert "CONTENT VALIDATION REPORT" in report_text
    assert "FAILED" in report_text
    assert "ERRORS" in report_text
    assert len(report_text) > 100


def test_validation_report_passed_message(validator, valid_course):
    """Test validation report shows passed message when no issues."""
    report = validator.validate_course(valid_course)
    
    if report.passed:
        report_text = validator.generate_report_text()
        assert "PASSED" in report_text or "No issues found" in report_text


def test_validation_report_counts_severity_correctly(validator, valid_lesson):
    """Test validation report counts errors, warnings, and info correctly."""
    # Create multiple types of issues
    valid_lesson.learning_objectives = []  # Error
    valid_lesson.content.code_example.language = None  # Warning
    valid_lesson.exercises = []  # Info
    
    report = validator.validate_lesson(valid_lesson)
    
    assert report.errors >= 1
    assert report.warnings >= 1
    assert report.info >= 1
    assert report.total_issues == report.errors + report.warnings + report.info


# ========== Test Course Structure Validation ==========

def test_validate_course_with_no_modules(validator):
    """Test validation fails when course has no modules."""
    course = CourseOutline(
        course_id="course_001",
        title="Empty Course",
        description="Test",
        author="Test",
        version="1.0.0",
        created_at=datetime.now(),
        modules=[],
        total_duration_hours=0,
        difficulty_distribution={},
        tags=[],
        prerequisites=[]
    )
    
    report = validator.validate_course(course)
    
    assert not report.passed
    assert report.errors > 0
    assert any(
        'no modules' in issue.message
        for issue in report.issues
    )


def test_validate_course_with_few_modules(validator, valid_module):
    """Test validation warns when course has too few modules."""
    course = CourseOutline(
        course_id="course_001",
        title="Small Course",
        description="Test",
        author="Test",
        version="1.0.0",
        created_at=datetime.now(),
        modules=[valid_module],
        total_duration_hours=2.0,
        difficulty_distribution={"beginner": 1},
        tags=[],
        prerequisites=[]
    )
    
    report = validator.validate_course(course)
    
    assert report.warnings > 0
    assert any(
        'recommended: 3-8' in issue.message
        for issue in report.issues
    )


def test_validate_course_with_no_title(validator, valid_module):
    """Test validation fails when course has no title."""
    course = CourseOutline(
        course_id="course_001",
        title="",
        description="Test",
        author="Test",
        version="1.0.0",
        created_at=datetime.now(),
        modules=[valid_module],
        total_duration_hours=2.0,
        difficulty_distribution={"beginner": 1},
        tags=[],
        prerequisites=[]
    )
    
    report = validator.validate_course(course)
    
    assert not report.passed
    assert any(
        'no title' in issue.message
        for issue in report.issues
    )


def test_validate_module_with_no_lessons(validator, valid_course):
    """Test validation fails when module has no lessons."""
    valid_course.modules[0].lessons = []
    
    report = validator.validate_course(valid_course)
    
    assert not report.passed
    assert any(
        'no lessons' in issue.message
        for issue in report.issues
    )


def test_validate_lesson_with_invalid_duration(validator, valid_lesson):
    """Test validation warns when lesson has invalid duration."""
    valid_lesson.duration_minutes = 0
    
    report = validator.validate_lesson(valid_lesson)
    
    assert report.warnings > 0
    assert any(
        'invalid duration' in issue.message
        for issue in report.issues
    )


# ========== Integration Tests ==========

def test_validate_complete_valid_course(validator, valid_course):
    """Test validation passes for a complete valid course."""
    report = validator.validate_course(valid_course)
    
    # Should pass or have only minor warnings/info
    assert report.errors == 0


def test_validate_course_with_multiple_issues(validator, valid_course):
    """Test validation reports multiple issues correctly."""
    # Create multiple issues
    lesson = valid_course.modules[0].lessons[0]
    lesson.learning_objectives = []  # Error
    lesson.content.code_example.language = None  # Warning
    lesson.prerequisites = ["non_existent"]  # Error
    
    report = validator.validate_course(valid_course)
    
    assert not report.passed
    assert report.total_issues >= 3
    assert report.errors >= 2
    assert report.warnings >= 1


def test_validation_report_add_issue(validator):
    """Test adding issues to validation report."""
    report = ValidationReport(total_issues=0, errors=0, warnings=0, info=0)
    
    # Add error
    report.add_issue(ValidationIssue(
        severity='error',
        category='test',
        message='Test error'
    ))
    
    assert report.total_issues == 1
    assert report.errors == 1
    assert not report.passed
    
    # Add warning
    report.add_issue(ValidationIssue(
        severity='warning',
        category='test',
        message='Test warning'
    ))
    
    assert report.total_issues == 2
    assert report.warnings == 1
    
    # Add info
    report.add_issue(ValidationIssue(
        severity='info',
        category='test',
        message='Test info'
    ))
    
    assert report.total_issues == 3
    assert report.info == 1
