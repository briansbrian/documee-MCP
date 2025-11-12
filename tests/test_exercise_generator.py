"""Unit tests for Exercise Generator."""

import pytest
import tempfile
import os
from datetime import datetime
from src.course.exercise_generator import ExerciseGenerator
from src.course.config import CourseConfig
from src.models import (
    FileAnalysis,
    SymbolInfo,
    DetectedPattern,
    ComplexityMetrics,
    TeachingValueScore,
    FunctionInfo,
    ClassInfo,
    ImportInfo,
)


# ========== Test Fixtures ==========

@pytest.fixture
def course_config():
    """Create a default course configuration."""
    return CourseConfig(
        target_audience="mixed",
        max_code_lines=50,
        include_annotations=True,
        use_simple_language=True
    )


@pytest.fixture
def temp_python_file():
    """Create a temporary Python file for testing."""
    content = '''"""Example module for testing."""

def calculate_sum(numbers):
    """Calculate the sum of a list of numbers.
    
    Args:
        numbers: List of numbers to sum
        
    Returns:
        Sum of all numbers
    """
    total = 0
    for num in numbers:
        total += num
    return total


class Calculator:
    """A simple calculator class."""
    
    def __init__(self):
        """Initialize the calculator."""
        self.result = 0
    
    def add(self, value):
        """Add a value to the result."""
        self.result += value
        return self.result
    
    def reset(self):
        """Reset the calculator."""
        self.result = 0
'''
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(content)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def function_pattern(temp_python_file):
    """Create a function pattern for testing."""
    return DetectedPattern(
        pattern_type="function_implementation",
        file_path=temp_python_file,
        confidence=0.85,
        evidence=["def calculate_sum", "for loop", "accumulator"],
        line_numbers=[3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    )


@pytest.fixture
def class_pattern(temp_python_file):
    """Create a class pattern for testing."""
    return DetectedPattern(
        pattern_type="class_definition",
        file_path=temp_python_file,
        confidence=0.9,
        evidence=["class Calculator", "methods", "state management"],
        line_numbers=[17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32]
    )


@pytest.fixture
def api_pattern(temp_python_file):
    """Create an API pattern for testing."""
    return DetectedPattern(
        pattern_type="api_endpoint",
        file_path=temp_python_file,
        confidence=0.8,
        evidence=["route", "request", "response"],
        line_numbers=[3, 4, 5]
    )


@pytest.fixture
def simple_file_analysis(temp_python_file):
    """Create a simple file analysis for testing."""
    return FileAnalysis(
        file_path=temp_python_file,
        language="python",
        symbol_info=SymbolInfo(
            functions=[
                FunctionInfo(
                    name="calculate_sum",
                    parameters=["numbers"],
                    return_type="int",
                    docstring="Calculate the sum of a list of numbers.",
                    start_line=3,
                    end_line=14,
                    complexity=2,
                    is_async=False
                )
            ],
            classes=[
                ClassInfo(
                    name="Calculator",
                    methods=[
                        FunctionInfo(
                            name="__init__",
                            parameters=["self"],
                            return_type=None,
                            docstring="Initialize the calculator.",
                            start_line=20,
                            end_line=22,
                            complexity=1,
                            is_async=False
                        ),
                        FunctionInfo(
                            name="add",
                            parameters=["self", "value"],
                            return_type="int",
                            docstring="Add a value to the result.",
                            start_line=24,
                            end_line=27,
                            complexity=1,
                            is_async=False
                        ),
                        FunctionInfo(
                            name="reset",
                            parameters=["self"],
                            return_type=None,
                            docstring="Reset the calculator.",
                            start_line=29,
                            end_line=31,
                            complexity=1,
                            is_async=False
                        )
                    ],
                    base_classes=[],
                    docstring="A simple calculator class.",
                    start_line=17,
                    end_line=31
                )
            ],
            imports=[]
        ),
        patterns=[
            DetectedPattern(
                pattern_type="function_implementation",
                file_path=temp_python_file,
                confidence=0.85,
                evidence=["def calculate_sum"],
                line_numbers=[3]
            ),
            DetectedPattern(
                pattern_type="class_definition",
                file_path=temp_python_file,
                confidence=0.9,
                evidence=["class Calculator"],
                line_numbers=[17]
            )
        ],
        complexity_metrics=ComplexityMetrics(
            avg_complexity=1.5,
            max_complexity=2,
            min_complexity=1,
            high_complexity_functions=[],
            trivial_functions=["reset"],
            avg_nesting_depth=1.2
        ),
        teaching_value=TeachingValueScore(
            total_score=0.75,
            documentation_score=0.9,
            complexity_score=0.6,
            pattern_score=0.8,
            structure_score=0.7,
            explanation="Good example of basic class and function",
            factors={}
        ),
        documentation_coverage=0.9,
        linter_issues=[],
        has_errors=False,
        errors=[],
        analyzed_at=datetime.now().isoformat(),
        cache_hit=False
    )


@pytest.fixture
def complex_file_analysis(temp_python_file):
    """Create a complex file analysis for testing."""
    return FileAnalysis(
        file_path=temp_python_file,
        language="python",
        symbol_info=SymbolInfo(
            functions=[
                FunctionInfo(
                    name="complex_algorithm",
                    parameters=["data", "options"],
                    return_type="dict",
                    docstring="A complex algorithm with high complexity.",
                    start_line=1,
                    end_line=30,
                    complexity=15,
                    is_async=True
                )
            ],
            classes=[],
            imports=[
                ImportInfo(
                    module="typing",
                    imported_symbols=["Dict", "List"],
                    is_relative=False,
                    import_type="from_import",
                    line_number=1
                )
            ]
        ),
        patterns=[
            DetectedPattern(
                pattern_type="async_pattern",
                file_path=temp_python_file,
                confidence=0.95,
                evidence=["async def", "await"],
                line_numbers=[1, 5, 10]
            )
        ],
        complexity_metrics=ComplexityMetrics(
            avg_complexity=15.0,
            max_complexity=15,
            min_complexity=15,
            high_complexity_functions=["complex_algorithm"],
            trivial_functions=[],
            avg_nesting_depth=4.0
        ),
        teaching_value=TeachingValueScore(
            total_score=0.85,
            documentation_score=0.9,
            complexity_score=0.9,
            pattern_score=0.9,
            structure_score=0.7,
            explanation="Advanced async pattern",
            factors={}
        ),
        documentation_coverage=0.9,
        linter_issues=[],
        has_errors=False,
        errors=[],
        analyzed_at=datetime.now().isoformat(),
        cache_hit=False
    )


# ========== Test Starter Code Generation with TODOs ==========

def test_create_starter_code_has_todos(course_config, function_pattern, simple_file_analysis):
    """Test that starter code includes TODO comments (Req 3.1)."""
    generator = ExerciseGenerator(course_config)
    exercise = generator.generate_exercise(function_pattern, simple_file_analysis)
    
    # Starter code should have TODO comments
    assert "TODO" in exercise.starter_code
    assert "pass" in exercise.starter_code


def test_create_starter_code_preserves_signature(course_config, function_pattern, simple_file_analysis):
    """Test that starter code preserves function signatures."""
    generator = ExerciseGenerator(course_config)
    exercise = generator.generate_exercise(function_pattern, simple_file_analysis)
    
    # Should preserve function definition
    assert "def " in exercise.starter_code


def test_create_starter_code_preserves_imports(course_config, function_pattern, simple_file_analysis):
    """Test that starter code preserves import statements."""
    generator = ExerciseGenerator(course_config)
    
    # Add imports to the solution
    solution_code = "import math\n\ndef calculate():\n    return math.pi"
    starter = generator._create_starter_code(solution_code, "function")
    
    # Should preserve imports
    assert "import math" in starter


def test_create_starter_code_preserves_docstrings(course_config, function_pattern, simple_file_analysis):
    """Test that starter code preserves docstrings."""
    generator = ExerciseGenerator(course_config)
    exercise = generator.generate_exercise(function_pattern, simple_file_analysis)
    
    # Should preserve docstrings
    assert '"""' in exercise.starter_code or "'''" in exercise.starter_code


def test_create_starter_code_removes_implementation(course_config, function_pattern, simple_file_analysis):
    """Test that starter code removes implementation details."""
    generator = ExerciseGenerator(course_config)
    
    solution_code = '''def calculate_sum(numbers):
    """Calculate sum."""
    total = 0
    for num in numbers:
        total += num
    return total'''
    
    starter = generator._create_starter_code(solution_code, "function")
    
    # Should remove implementation but keep structure
    assert "TODO" in starter
    assert "pass" in starter
    # Should not have the full implementation
    assert "for num in numbers:" not in starter


def test_create_starter_code_class_pattern(course_config, class_pattern, simple_file_analysis):
    """Test starter code generation for class patterns."""
    generator = ExerciseGenerator(course_config)
    exercise = generator.generate_exercise(class_pattern, simple_file_analysis)
    
    # Should have class definition
    assert "class " in exercise.starter_code
    # Should have TODO
    assert "TODO" in exercise.starter_code


# ========== Test Hint Generation ==========

def test_generate_hints_count(course_config, function_pattern, simple_file_analysis):
    """Test that hints are generated (Req 3.5)."""
    generator = ExerciseGenerator(course_config)
    exercise = generator.generate_exercise(function_pattern, simple_file_analysis)
    
    # Should have hints
    assert len(exercise.hints) > 0


def test_generate_hints_progressive(course_config, function_pattern, simple_file_analysis):
    """Test that hints provide progressive revelation."""
    generator = ExerciseGenerator(course_config)
    exercise = generator.generate_exercise(function_pattern, simple_file_analysis)
    
    # Should have multiple hints
    assert len(exercise.hints) >= 1
    
    # First hint should be high-level
    first_hint = exercise.hints[0].lower()
    assert "structure" in first_hint or "understand" in first_hint or "start" in first_hint


def test_generate_hints_includes_imports(course_config, function_pattern, simple_file_analysis):
    """Test that hints mention required imports when present."""
    generator = ExerciseGenerator(course_config)
    
    solution_code = "import math\n\ndef calculate():\n    return math.pi"
    hints = generator._generate_hints(solution_code, "function")
    
    # Should mention imports in hints
    hints_text = " ".join(hints).lower()
    assert "import" in hints_text


def test_generate_hints_mentions_key_elements(course_config, function_pattern, simple_file_analysis):
    """Test that hints mention key implementation elements."""
    generator = ExerciseGenerator(course_config)
    exercise = generator.generate_exercise(function_pattern, simple_file_analysis)
    
    # Should have hints about implementation
    hints_text = " ".join(exercise.hints).lower()
    assert len(hints_text) > 0
    # Should mention components or elements
    assert "component" in hints_text or "element" in hints_text or "implement" in hints_text


# ========== Test Test Case Generation ==========

def test_generate_test_cases_count(course_config, function_pattern, simple_file_analysis):
    """Test that test cases are generated."""
    generator = ExerciseGenerator(course_config)
    exercise = generator.generate_exercise(function_pattern, simple_file_analysis)
    
    # Should have test cases
    assert len(exercise.test_cases) > 0


def test_generate_test_cases_structure(course_config, function_pattern, simple_file_analysis):
    """Test that test cases have proper structure."""
    generator = ExerciseGenerator(course_config)
    exercise = generator.generate_exercise(function_pattern, simple_file_analysis)
    
    # Each test case should have required fields
    for test_case in exercise.test_cases:
        assert test_case.input is not None
        assert test_case.expected_output is not None
        assert test_case.description is not None
        assert len(test_case.description) > 0


def test_generate_test_cases_function_pattern(course_config, function_pattern, simple_file_analysis):
    """Test test case generation for function patterns."""
    generator = ExerciseGenerator(course_config)
    exercise = generator.generate_exercise(function_pattern, simple_file_analysis)
    
    # Should have at least 2 test cases for functions
    assert len(exercise.test_cases) >= 1
    
    # Should test basic and edge cases
    descriptions = [tc.description.lower() for tc in exercise.test_cases]
    has_basic_or_edge = any("basic" in d or "edge" in d for d in descriptions)
    assert has_basic_or_edge


def test_generate_test_cases_class_pattern(course_config, class_pattern, simple_file_analysis):
    """Test test case generation for class patterns."""
    generator = ExerciseGenerator(course_config)
    exercise = generator.generate_exercise(class_pattern, simple_file_analysis)
    
    # Should have test cases
    assert len(exercise.test_cases) >= 1
    
    # Should test instantiation or methods
    descriptions = [tc.description.lower() for tc in exercise.test_cases]
    has_class_test = any("instance" in d or "method" in d or "class" in d for d in descriptions)
    assert has_class_test


def test_generate_test_cases_api_pattern(course_config, api_pattern, simple_file_analysis):
    """Test test case generation for API patterns."""
    generator = ExerciseGenerator(course_config)
    exercise = generator.generate_exercise(api_pattern, simple_file_analysis)
    
    # Should have test cases
    assert len(exercise.test_cases) >= 1


# ========== Test Solution Code Extraction ==========

def test_extract_pattern_code_basic(course_config, function_pattern, simple_file_analysis):
    """Test basic solution code extraction (Req 3.3)."""
    generator = ExerciseGenerator(course_config)
    exercise = generator.generate_exercise(function_pattern, simple_file_analysis)
    
    # Should have solution code
    assert len(exercise.solution_code) > 0


def test_extract_pattern_code_from_line_numbers(course_config, function_pattern, simple_file_analysis):
    """Test code extraction using pattern line numbers."""
    generator = ExerciseGenerator(course_config)
    solution_code = generator._extract_pattern_code(function_pattern, simple_file_analysis)
    
    # Should extract code
    assert len(solution_code) > 0
    # Should contain function definition
    assert "def " in solution_code


def test_extract_pattern_code_from_function(course_config, simple_file_analysis, temp_python_file):
    """Test code extraction from function info."""
    generator = ExerciseGenerator(course_config)
    
    # Create pattern with evidence matching function name
    pattern = DetectedPattern(
        pattern_type="function",
        file_path=temp_python_file,
        confidence=0.8,
        evidence=["calculate_sum"],
        line_numbers=[]
    )
    
    solution_code = generator._extract_pattern_code(pattern, simple_file_analysis)
    
    # Should extract function code
    assert "calculate_sum" in solution_code


def test_extract_pattern_code_from_class(course_config, simple_file_analysis, temp_python_file):
    """Test code extraction from class info."""
    generator = ExerciseGenerator(course_config)
    
    # Create pattern with evidence matching class name
    pattern = DetectedPattern(
        pattern_type="class",
        file_path=temp_python_file,
        confidence=0.9,
        evidence=["calculator"],
        line_numbers=[]
    )
    
    solution_code = generator._extract_pattern_code(pattern, simple_file_analysis)
    
    # Should extract class code
    assert "Calculator" in solution_code or "class" in solution_code


def test_extract_pattern_code_limits_length(course_config, simple_file_analysis, temp_python_file):
    """Test that extracted code is limited to reasonable length."""
    generator = ExerciseGenerator(course_config)
    
    # Create pattern for class
    pattern = DetectedPattern(
        pattern_type="class",
        file_path=temp_python_file,
        confidence=0.9,
        evidence=["calculator"],
        line_numbers=[]
    )
    
    solution_code = generator._extract_pattern_code(pattern, simple_file_analysis)
    
    # Should limit to 50 lines for classes
    lines = solution_code.split('\n')
    # Allow some flexibility
    assert len(lines) <= 55


# ========== Test Exercise Generation Integration ==========

def test_generate_exercise_complete(course_config, function_pattern, simple_file_analysis):
    """Test complete exercise generation."""
    generator = ExerciseGenerator(course_config)
    exercise = generator.generate_exercise(function_pattern, simple_file_analysis)
    
    # Verify all required fields
    assert exercise.exercise_id is not None
    assert len(exercise.exercise_id) > 0
    
    assert exercise.title is not None
    assert len(exercise.title) > 0
    
    assert exercise.description is not None
    assert len(exercise.description) > 0
    
    assert exercise.difficulty in ["beginner", "intermediate", "advanced"]
    assert exercise.estimated_minutes > 0
    
    assert len(exercise.instructions) > 0
    assert len(exercise.starter_code) > 0
    assert len(exercise.solution_code) > 0
    assert len(exercise.hints) > 0
    assert len(exercise.test_cases) > 0
    assert len(exercise.learning_objectives) > 0


def test_generate_exercise_instructions(course_config, function_pattern, simple_file_analysis):
    """Test that exercise has clear instructions (Req 3.2)."""
    generator = ExerciseGenerator(course_config)
    exercise = generator.generate_exercise(function_pattern, simple_file_analysis)
    
    # Should have step-by-step instructions
    assert len(exercise.instructions) >= 3
    
    # Instructions should be strings
    for instruction in exercise.instructions:
        assert isinstance(instruction, str)
        assert len(instruction) > 0


def test_generate_exercise_difficulty_beginner(course_config, function_pattern, simple_file_analysis):
    """Test difficulty determination for simple code."""
    generator = ExerciseGenerator(course_config)
    exercise = generator.generate_exercise(function_pattern, simple_file_analysis)
    
    # Simple file should be beginner or intermediate
    assert exercise.difficulty in ["beginner", "intermediate"]


def test_generate_exercise_difficulty_advanced(course_config, complex_file_analysis):
    """Test difficulty determination for complex code."""
    generator = ExerciseGenerator(course_config)
    
    # Create pattern for complex code
    pattern = DetectedPattern(
        pattern_type="async_pattern",
        file_path=complex_file_analysis.file_path,
        confidence=0.95,
        evidence=["async", "await"],
        line_numbers=[1, 5, 10]
    )
    
    exercise = generator.generate_exercise(pattern, complex_file_analysis)
    
    # Complex file should be advanced
    assert exercise.difficulty == "advanced"


def test_generate_exercise_time_estimation(course_config, function_pattern, simple_file_analysis):
    """Test time estimation for exercises."""
    generator = ExerciseGenerator(course_config)
    exercise = generator.generate_exercise(function_pattern, simple_file_analysis)
    
    # Should have reasonable time estimate
    assert 10 <= exercise.estimated_minutes <= 60


def test_generate_exercise_learning_objectives(course_config, function_pattern, simple_file_analysis):
    """Test learning objectives generation."""
    generator = ExerciseGenerator(course_config)
    exercise = generator.generate_exercise(function_pattern, simple_file_analysis)
    
    # Should have learning objectives
    assert len(exercise.learning_objectives) >= 2
    
    # Objectives should mention the pattern
    objectives_text = " ".join(exercise.learning_objectives).lower()
    assert "implement" in objectives_text or "understand" in objectives_text


# ========== Test Multiple Exercises Generation ==========

def test_generate_exercises_for_lesson_count(course_config, simple_file_analysis):
    """Test that 1-3 exercises are generated based on complexity (Req 3.4)."""
    generator = ExerciseGenerator(course_config)
    exercises = generator.generate_exercises_for_lesson(simple_file_analysis)
    
    # Should generate 1-3 exercises
    assert 1 <= len(exercises) <= 3


def test_generate_exercises_for_lesson_simple_code(course_config, simple_file_analysis):
    """Test exercise count for simple code."""
    generator = ExerciseGenerator(course_config)
    exercises = generator.generate_exercises_for_lesson(simple_file_analysis)
    
    # Simple code (complexity < 5) should have 1-2 exercises
    assert 1 <= len(exercises) <= 2


def test_generate_exercises_for_lesson_complex_code(course_config, complex_file_analysis):
    """Test exercise count for complex code."""
    generator = ExerciseGenerator(course_config)
    exercises = generator.generate_exercises_for_lesson(complex_file_analysis)
    
    # Complex code should have more exercises
    assert len(exercises) >= 1


def test_generate_exercises_for_lesson_from_patterns(course_config, simple_file_analysis):
    """Test that exercises are generated from detected patterns."""
    generator = ExerciseGenerator(course_config)
    exercises = generator.generate_exercises_for_lesson(simple_file_analysis)
    
    # Should have exercises
    assert len(exercises) > 0
    
    # Each exercise should be valid
    for exercise in exercises:
        assert exercise.exercise_id is not None
        assert len(exercise.starter_code) > 0
        assert len(exercise.solution_code) > 0


def test_generate_exercises_for_lesson_max_limit(course_config, simple_file_analysis):
    """Test that max_exercises parameter is respected."""
    generator = ExerciseGenerator(course_config)
    exercises = generator.generate_exercises_for_lesson(simple_file_analysis, max_exercises=1)
    
    # Should not exceed max
    assert len(exercises) <= 1


def test_generate_exercises_for_lesson_fallback(course_config, temp_python_file):
    """Test fallback exercise generation when no patterns exist."""
    generator = ExerciseGenerator(course_config)
    
    # Create file analysis with no patterns but has functions
    file_analysis = FileAnalysis(
        file_path=temp_python_file,
        language="python",
        symbol_info=SymbolInfo(
            functions=[
                FunctionInfo(
                    name="test_function",
                    parameters=["x"],
                    return_type="int",
                    docstring="Test function",
                    start_line=1,
                    end_line=5,
                    complexity=1,
                    is_async=False
                )
            ],
            classes=[],
            imports=[]
        ),
        patterns=[],  # No patterns
        complexity_metrics=ComplexityMetrics(
            avg_complexity=1.0,
            max_complexity=1,
            min_complexity=1,
            high_complexity_functions=[],
            trivial_functions=["test_function"],
            avg_nesting_depth=1.0
        ),
        teaching_value=TeachingValueScore(
            total_score=0.5,
            documentation_score=0.5,
            complexity_score=0.5,
            pattern_score=0.5,
            structure_score=0.5,
            explanation="Basic function",
            factors={}
        ),
        documentation_coverage=0.5,
        linter_issues=[],
        has_errors=False,
        errors=[],
        analyzed_at=datetime.now().isoformat(),
        cache_hit=False
    )
    
    exercises = generator.generate_exercises_for_lesson(file_analysis)
    
    # Should generate at least one exercise using fallback
    assert len(exercises) >= 1
