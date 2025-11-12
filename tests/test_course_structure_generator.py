"""Unit tests for Course Structure Generator."""

import pytest
from datetime import datetime
from src.course.structure_generator import CourseStructureGenerator
from src.course.config import CourseConfig
from src.models import (
    CodebaseAnalysis,
    FileAnalysis,
    SymbolInfo,
    DetectedPattern,
    ComplexityMetrics,
    TeachingValueScore,
    DependencyGraph,
    FileNode,
    CodebaseMetrics,
    FunctionInfo,
    ImportInfo,
)


# ========== Test Fixtures ==========

@pytest.fixture
def course_config():
    """Create a default course configuration."""
    return CourseConfig(
        target_audience="mixed",
        course_focus="full-stack",
        author="Test Author",
        version="1.0.0",
        min_modules=3,
        max_modules=8,
        min_teaching_value=0.5
    )


@pytest.fixture
def simple_file_analysis():
    """Create a simple file analysis for testing."""
    return FileAnalysis(
        file_path="src/example.py",
        language="python",
        symbol_info=SymbolInfo(
            functions=[
                FunctionInfo(
                    name="simple_func",
                    parameters=["x"],
                    return_type="int",
                    docstring="A simple function",
                    start_line=1,
                    end_line=3,
                    complexity=2,
                    is_async=False
                )
            ],
            classes=[],
            imports=[]
        ),
        patterns=[
            DetectedPattern(
                pattern_type="function_definition",
                file_path="src/example.py",
                confidence=0.9,
                evidence=["def simple_func"],
                line_numbers=[1]
            )
        ],
        complexity_metrics=ComplexityMetrics(
            avg_complexity=2.0,
            max_complexity=2,
            min_complexity=2,
            high_complexity_functions=[],
            trivial_functions=[],
            avg_nesting_depth=1.0
        ),
        teaching_value=TeachingValueScore(
            total_score=0.7,
            documentation_score=0.8,
            complexity_score=0.6,
            pattern_score=0.7,
            structure_score=0.7,
            explanation="Good example of basic function",
            factors={}
        ),
        documentation_coverage=0.8,
        linter_issues=[],
        has_errors=False,
        errors=[],
        analyzed_at=datetime.now().isoformat(),
        cache_hit=False
    )


@pytest.fixture
def complex_file_analysis():
    """Create a complex file analysis for testing."""
    return FileAnalysis(
        file_path="src/advanced.py",
        language="python",
        symbol_info=SymbolInfo(
            functions=[
                FunctionInfo(
                    name="complex_func",
                    parameters=["x", "y", "z"],
                    return_type="dict",
                    docstring="A complex function",
                    start_line=1,
                    end_line=20,
                    complexity=12,
                    is_async=True
                )
            ],
            classes=[],
            imports=[
                ImportInfo(
                    module="src.example",
                    imported_symbols=["simple_func"],
                    is_relative=True,
                    import_type="from_import",
                    line_number=1
                )
            ]
        ),
        patterns=[
            DetectedPattern(
                pattern_type="async_pattern",
                file_path="src/advanced.py",
                confidence=0.95,
                evidence=["async def"],
                line_numbers=[1]
            )
        ],
        complexity_metrics=ComplexityMetrics(
            avg_complexity=12.0,
            max_complexity=12,
            min_complexity=12,
            high_complexity_functions=["complex_func"],
            trivial_functions=[],
            avg_nesting_depth=3.5
        ),
        teaching_value=TeachingValueScore(
            total_score=0.85,
            documentation_score=0.9,
            complexity_score=0.8,
            pattern_score=0.9,
            structure_score=0.8,
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


@pytest.fixture
def sample_codebase_analysis(simple_file_analysis, complex_file_analysis):
    """Create a sample codebase analysis with multiple files."""
    # Create additional file analyses with different patterns
    file_analyses = {
        "src/example.py": simple_file_analysis,
        "src/advanced.py": complex_file_analysis,
    }
    
    # Add more files with different patterns
    for i in range(3, 10):
        pattern_type = ["api_route", "database_model", "utility_function"][i % 3]
        complexity = 3 + (i % 3) * 3  # 3, 6, 9
        
        file_analyses[f"src/file{i}.py"] = FileAnalysis(
            file_path=f"src/file{i}.py",
            language="python",
            symbol_info=SymbolInfo(functions=[], classes=[], imports=[]),
            patterns=[
                DetectedPattern(
                    pattern_type=pattern_type,
                    file_path=f"src/file{i}.py",
                    confidence=0.8,
                    evidence=[pattern_type],
                    line_numbers=[1]
                )
            ],
            complexity_metrics=ComplexityMetrics(
                avg_complexity=float(complexity),
                max_complexity=complexity,
                min_complexity=complexity,
                high_complexity_functions=[],
                trivial_functions=[],
                avg_nesting_depth=1.5
            ),
            teaching_value=TeachingValueScore(
                total_score=0.6 + (i * 0.02),
                documentation_score=0.7,
                complexity_score=0.6,
                pattern_score=0.6,
                structure_score=0.6,
                explanation=f"Example {i}",
                factors={}
            ),
            documentation_coverage=0.7,
            linter_issues=[],
            has_errors=False,
            errors=[],
            analyzed_at=datetime.now().isoformat(),
            cache_hit=False
        )
    
    # Create dependency graph
    dep_graph = DependencyGraph(
        nodes={
            "src/example.py": FileNode(
                file_path="src/example.py",
                imports=[],
                imported_by=["src/advanced.py"],
                external_imports=[]
            ),
            "src/advanced.py": FileNode(
                file_path="src/advanced.py",
                imports=["src/example.py"],
                imported_by=[],
                external_imports=[]
            )
        },
        edges=[],
        circular_dependencies=[],
        external_dependencies={}
    )
    
    # Create top teaching files list
    top_teaching_files = sorted(
        [(path, fa.teaching_value.total_score) for path, fa in file_analyses.items()],
        key=lambda x: x[1],
        reverse=True
    )
    
    return CodebaseAnalysis(
        codebase_id="test_codebase",
        file_analyses=file_analyses,
        dependency_graph=dep_graph,
        global_patterns=[
            DetectedPattern(
                pattern_type="function_definition",
                file_path="",
                confidence=0.9,
                evidence=[],
                line_numbers=[]
            )
        ],
        top_teaching_files=top_teaching_files,
        metrics=CodebaseMetrics(
            total_files=len(file_analyses),
            total_functions=10,
            total_classes=2,
            avg_complexity=5.0,
            avg_documentation_coverage=0.75,
            total_patterns_detected=len(file_analyses),
            analysis_time_ms=100.0,
            cache_hit_rate=0.0
        ),
        analyzed_at=datetime.now().isoformat()
    )


# ========== Test Module Count Calculation ==========

def test_calculate_module_count_minimum(course_config):
    """Test that module count respects minimum."""
    generator = CourseStructureGenerator(course_config)
    
    # With 0 files, should return min_modules
    assert generator.calculate_module_count(0) == course_config.min_modules
    
    # With 1 file, should return min_modules
    assert generator.calculate_module_count(1) == course_config.min_modules


def test_calculate_module_count_maximum(course_config):
    """Test that module count respects maximum."""
    generator = CourseStructureGenerator(course_config)
    
    # With many files, should not exceed max_modules
    assert generator.calculate_module_count(100) <= course_config.max_modules


def test_calculate_module_count_ideal_range(course_config):
    """Test module count calculation for typical file counts."""
    generator = CourseStructureGenerator(course_config)
    
    # 12 files should create 3 modules (4 lessons each)
    assert generator.calculate_module_count(12) == 3
    
    # 20 files should create 5 modules (4 lessons each)
    assert generator.calculate_module_count(20) == 5
    
    # 32 files should create 8 modules (4 lessons each)
    assert generator.calculate_module_count(32) == 8


# ========== Test Lesson Grouping by Patterns ==========

def test_group_by_patterns_empty(course_config, sample_codebase_analysis):
    """Test grouping with no teachable files."""
    generator = CourseStructureGenerator(course_config)
    
    grouped = generator.group_by_patterns([], sample_codebase_analysis)
    assert grouped == []


def test_group_by_patterns_single_pattern(course_config, sample_codebase_analysis):
    """Test grouping files with same pattern."""
    generator = CourseStructureGenerator(course_config)
    
    # Get files with same pattern type
    teachable_files = [
        ("src/file3.py", 0.66),
        ("src/file6.py", 0.72),
    ]
    
    grouped = generator.group_by_patterns(teachable_files, sample_codebase_analysis)
    
    # Should group files with same pattern together
    assert len(grouped) > 0
    # Each group should have file analysis
    for group in grouped:
        for item in group:
            assert len(item) == 3  # (file_path, teaching_value, file_analysis)


def test_group_by_patterns_multiple_patterns(course_config, sample_codebase_analysis):
    """Test grouping files with different patterns."""
    generator = CourseStructureGenerator(course_config)
    
    teachable_files = [
        (path, score) for path, score in sample_codebase_analysis.top_teaching_files
        if score >= 0.6
    ]
    
    grouped = generator.group_by_patterns(teachable_files, sample_codebase_analysis)
    
    # Should create multiple groups for different patterns
    assert len(grouped) >= 2
    
    # Groups should be sorted by size (largest first)
    if len(grouped) > 1:
        assert len(grouped[0]) >= len(grouped[-1])


def test_group_by_patterns_preserves_file_analysis(course_config, sample_codebase_analysis):
    """Test that grouping preserves file analysis data."""
    generator = CourseStructureGenerator(course_config)
    
    teachable_files = sample_codebase_analysis.top_teaching_files[:5]
    grouped = generator.group_by_patterns(teachable_files, sample_codebase_analysis)
    
    # Verify each grouped item has correct structure
    for group in grouped:
        for file_path, teaching_value, file_analysis in group:
            assert file_path in sample_codebase_analysis.file_analyses
            assert file_analysis == sample_codebase_analysis.file_analyses[file_path]
            assert teaching_value > 0


# ========== Test Difficulty Ordering ==========

def test_sort_by_difficulty_empty(course_config):
    """Test sorting empty module list."""
    generator = CourseStructureGenerator(course_config)
    
    sorted_modules = generator.sort_by_difficulty([])
    assert sorted_modules == []


def test_sort_by_difficulty_single_module(course_config, sample_codebase_analysis):
    """Test sorting with single module."""
    generator = CourseStructureGenerator(course_config)
    course = generator.generate_course_structure(sample_codebase_analysis)
    
    if len(course.modules) > 0:
        single = [course.modules[0]]
        sorted_modules = generator.sort_by_difficulty(single)
        assert len(sorted_modules) == 1
        assert sorted_modules[0] == single[0]


def test_sort_by_difficulty_order(course_config, sample_codebase_analysis):
    """Test that modules are sorted beginner -> intermediate -> advanced."""
    generator = CourseStructureGenerator(course_config)
    course = generator.generate_course_structure(sample_codebase_analysis)
    
    sorted_modules = generator.sort_by_difficulty(course.modules)
    
    # Verify order: beginner first, advanced last
    difficulty_order = {"beginner": 0, "intermediate": 1, "advanced": 2}
    
    for i in range(len(sorted_modules) - 1):
        current_diff = difficulty_order.get(sorted_modules[i].difficulty, 1)
        next_diff = difficulty_order.get(sorted_modules[i + 1].difficulty, 1)
        assert current_diff <= next_diff


# ========== Test Prerequisite Detection ==========

def test_detect_prerequisites_no_imports(course_config, simple_file_analysis, sample_codebase_analysis):
    """Test prerequisite detection with no imports."""
    generator = CourseStructureGenerator(course_config)
    
    # Create lesson from simple file (no imports)
    lesson = generator._create_basic_lesson(
        "src/example.py", 0.7, simple_file_analysis, 0
    )
    
    file_to_lesson = {"src/example.py": lesson}
    
    prerequisites = generator._detect_prerequisites(
        lesson, file_to_lesson, sample_codebase_analysis
    )
    
    # Should have no prerequisites
    assert prerequisites == []


def test_detect_prerequisites_with_imports(course_config, simple_file_analysis, complex_file_analysis, sample_codebase_analysis):
    """Test prerequisite detection with imports."""
    generator = CourseStructureGenerator(course_config)
    
    # Create lessons
    simple_lesson = generator._create_basic_lesson(
        "src/example.py", 0.7, simple_file_analysis, 0
    )
    complex_lesson = generator._create_basic_lesson(
        "src/advanced.py", 0.85, complex_file_analysis, 1
    )
    
    file_to_lesson = {
        "src/example.py": simple_lesson,
        "src/advanced.py": complex_lesson
    }
    
    # Complex file imports simple file
    prerequisites = generator._detect_prerequisites(
        complex_lesson, file_to_lesson, sample_codebase_analysis
    )
    
    # Should detect simple_lesson as prerequisite
    assert simple_lesson.lesson_id in prerequisites


def test_detect_prerequisites_difficulty_check(course_config, sample_codebase_analysis):
    """Test that prerequisites are only simpler lessons."""
    generator = CourseStructureGenerator(course_config)
    course = generator.generate_course_structure(sample_codebase_analysis)
    
    # Check all lessons
    for module in course.modules:
        for lesson in module.lessons:
            if lesson.prerequisites:
                # Find prerequisite lessons
                all_lessons = [l for m in course.modules for l in m.lessons]
                lesson_map = {l.lesson_id: l for l in all_lessons}
                
                for prereq_id in lesson.prerequisites:
                    if prereq_id in lesson_map:
                        prereq_lesson = lesson_map[prereq_id]
                        # Prerequisite should be simpler or equal difficulty
                        assert generator._is_simpler_lesson(prereq_lesson, lesson)


def test_sort_lessons_by_prerequisites_no_dependencies(course_config, sample_codebase_analysis):
    """Test sorting lessons with no dependencies."""
    generator = CourseStructureGenerator(course_config)
    
    # Create lessons with no prerequisites
    lessons = []
    for i in range(3):
        file_analysis = sample_codebase_analysis.file_analyses[f"src/file{i+3}.py"]
        lesson = generator._create_basic_lesson(
            f"src/file{i+3}.py",
            0.6 + i * 0.02,
            file_analysis,
            i
        )
        lessons.append(lesson)
    
    sorted_lessons = generator._sort_lessons_by_prerequisites(lessons)
    
    # Should maintain some order (by difficulty)
    assert len(sorted_lessons) == len(lessons)


def test_sort_lessons_by_prerequisites_with_dependencies(course_config, simple_file_analysis, complex_file_analysis):
    """Test sorting lessons with dependencies."""
    generator = CourseStructureGenerator(course_config)
    
    # Create lessons with prerequisites
    simple_lesson = generator._create_basic_lesson(
        "src/example.py", 0.7, simple_file_analysis, 0
    )
    complex_lesson = generator._create_basic_lesson(
        "src/advanced.py", 0.85, complex_file_analysis, 1
    )
    
    # Set prerequisite
    complex_lesson.prerequisites = [simple_lesson.lesson_id]
    
    # Sort in wrong order initially
    lessons = [complex_lesson, simple_lesson]
    sorted_lessons = generator._sort_lessons_by_prerequisites(lessons)
    
    # Simple lesson should come before complex lesson
    simple_idx = sorted_lessons.index(simple_lesson)
    complex_idx = sorted_lessons.index(complex_lesson)
    assert simple_idx < complex_idx


# ========== Integration Tests ==========

def test_generate_course_structure_complete(course_config, sample_codebase_analysis):
    """Test complete course structure generation."""
    generator = CourseStructureGenerator(course_config)
    course = generator.generate_course_structure(sample_codebase_analysis)
    
    # Verify course structure
    assert course.course_id is not None
    assert course.title is not None
    assert course.description is not None
    assert course.author == course_config.author
    assert course.version == course_config.version
    
    # Verify modules
    assert len(course.modules) >= course_config.min_modules
    assert len(course.modules) <= course_config.max_modules
    
    # Verify each module has lessons
    for module in course.modules:
        assert len(module.lessons) > 0
        assert module.difficulty in ["beginner", "intermediate", "advanced"]
        assert module.duration_hours > 0
    
    # Verify total duration
    assert course.total_duration_hours > 0
    
    # Verify difficulty distribution
    assert "beginner" in course.difficulty_distribution
    assert "intermediate" in course.difficulty_distribution
    assert "advanced" in course.difficulty_distribution


def test_generate_course_structure_lesson_ordering(course_config, sample_codebase_analysis):
    """Test that lessons are properly ordered within modules."""
    generator = CourseStructureGenerator(course_config)
    course = generator.generate_course_structure(sample_codebase_analysis)
    
    # Check lesson ordering within each module
    for module in course.modules:
        # Verify order field is sequential
        for idx, lesson in enumerate(module.lessons):
            assert lesson.order == idx
        
        # Verify prerequisites come before dependent lessons
        lesson_ids = [l.lesson_id for l in module.lessons]
        for idx, lesson in enumerate(module.lessons):
            for prereq_id in lesson.prerequisites:
                if prereq_id in lesson_ids:
                    prereq_idx = lesson_ids.index(prereq_id)
                    assert prereq_idx < idx, "Prerequisite should come before dependent lesson"


def test_generate_course_structure_module_ordering(course_config, sample_codebase_analysis):
    """Test that modules are ordered by difficulty."""
    generator = CourseStructureGenerator(course_config)
    course = generator.generate_course_structure(sample_codebase_analysis)
    
    # Verify modules are sorted by difficulty
    difficulty_order = {"beginner": 0, "intermediate": 1, "advanced": 2}
    
    for i in range(len(course.modules) - 1):
        current_diff = difficulty_order.get(course.modules[i].difficulty, 1)
        next_diff = difficulty_order.get(course.modules[i + 1].difficulty, 1)
        assert current_diff <= next_diff, "Modules should be ordered by difficulty"
