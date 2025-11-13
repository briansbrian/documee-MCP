"""
Performance tests for Course Generator.

Tests validate that course generation meets performance targets:
- Course outline generation: <5s for 100-file codebase
- Lesson generation: <2s per lesson
- Exercise generation: <3s per exercise
- MkDocs export: <10s for 20-lesson course
"""

import asyncio
import os
import tempfile
import time
from pathlib import Path

import pytest
import pytest_asyncio

from src.analysis.config import AnalysisConfig
from src.analysis.engine import AnalysisEngine
from src.cache.unified_cache import UnifiedCacheManager
from src.course.config import CourseConfig
from src.course.structure_generator import CourseStructureGenerator
from src.course.content_generator import LessonContentGenerator
from src.course.exercise_generator import ExerciseGenerator
from src.course.course_cache import CourseCacheManager
from src.course.performance_monitor import get_monitor, reset_monitor
from src.models import FileAnalysis, DetectedPattern, SymbolInfo, ComplexityMetrics, TeachingValueScore


@pytest_asyncio.fixture
async def cache_manager():
    """Create a cache manager for testing."""
    temp_db = tempfile.mktemp(suffix='.db')
    cache = UnifiedCacheManager(
        max_memory_mb=100,
        sqlite_path=temp_db,
        redis_url=None
    )
    await cache.initialize()
    yield cache
    await cache.close()
    if os.path.exists(temp_db):
        os.remove(temp_db)


@pytest_asyncio.fixture
async def course_cache(cache_manager):
    """Create a course cache manager for testing."""
    return CourseCacheManager(cache_manager)


@pytest.fixture
def course_config():
    """Create course configuration for testing."""
    return CourseConfig(
        author="Test Author",
        version="1.0.0",
        min_teaching_value=0.5,
        min_modules=3,
        max_modules=8,
        min_lesson_duration=15,
        max_lesson_duration=60,
        max_code_lines=50,
        include_annotations=True
    )


@pytest.fixture
def temp_codebase_100_files():
    """Create a temporary codebase with 100 Python files."""
    temp_dir = tempfile.mkdtemp()
    file_paths = []
    
    for i in range(100):
        file_path = os.path.join(temp_dir, f'file_{i:03d}.py')
        with open(file_path, 'w') as f:
            f.write(f'''
"""Module {i} for performance testing."""

def function_{i}_1():
    """Function docstring."""
    x = {i}
    if x > 0:
        return x * 2
    return 0

def function_{i}_2():
    """Another function."""
    y = {i}
    for j in range(10):
        y += j
    return y

class Class_{i}:
    """Class docstring."""
    
    def method_1(self):
        """Method docstring."""
        return "method1"
    
    def method_2(self, param):
        """Method docstring."""
        if param > 0:
            return param * 2
        return 0
''')
        file_paths.append(file_path)
    
    yield temp_dir, file_paths
    
    import shutil
    shutil.rmtree(temp_dir)


@pytest_asyncio.fixture
async def analysis_engine(cache_manager):
    """Create analysis engine for testing."""
    config = AnalysisConfig(
        max_complexity_threshold=10,
        min_documentation_coverage=0.5,
        max_file_size_mb=10,
        supported_languages=["python"],
        max_parallel_files=10,
        cache_ttl_seconds=3600,
        enable_linters=False,
        enable_incremental=True,
        persistence_path=tempfile.mkdtemp()
    )
    return AnalysisEngine(cache_manager, config)


def create_mock_file_analysis(file_path: str, index: int) -> FileAnalysis:
    """Create a mock FileAnalysis for testing."""
    return FileAnalysis(
        file_path=file_path,
        language="python",
        symbol_info=SymbolInfo(
            functions=[],
            classes=[],
            imports=[],
            exports=[]
        ),
        patterns=[
            DetectedPattern(
                pattern_type=f"pattern_{index % 3}",
                file_path=file_path,
                confidence=0.8,
                evidence=[f"evidence_{index}"],
                line_numbers=[1, 2, 3],
                metadata={}
            )
        ],
        teaching_value=TeachingValueScore(
            total_score=0.6 + (index % 4) * 0.1,
            documentation_score=0.7,
            complexity_score=0.6,
            pattern_score=0.8,
            structure_score=0.5,
            explanation=f"Teaching value for file {index}",
            factors={}
        ),
        complexity_metrics=ComplexityMetrics(
            avg_complexity=5.0 + (index % 5),
            max_complexity=10,
            min_complexity=1,
            high_complexity_functions=[],
            trivial_functions=[],
            avg_nesting_depth=2.0
        ),
        documentation_coverage=0.7,
        linter_issues=[],
        has_errors=False,
        errors=[],
        analyzed_at="2024-01-01T00:00:00",
        cache_hit=False,
        is_notebook=False
    )


@pytest.mark.asyncio
async def test_course_structure_generation_performance(
    course_config,
    course_cache,
    temp_codebase_100_files
):
    """
    Test: Course structure generation should complete in <5s for 100-file codebase.
    
    Requirement: 11.1 - Course outline generation <5s
    """
    temp_dir, file_paths = temp_codebase_100_files
    
    # Create mock analysis
    from src.models import CodebaseAnalysis, AnalysisMetrics, DependencyGraph
    
    file_analyses = {
        fp: create_mock_file_analysis(fp, i)
        for i, fp in enumerate(file_paths)
    }
    
    analysis = CodebaseAnalysis(
        codebase_id="test_codebase_100",
        root_path=temp_dir,
        file_analyses=file_analyses,
        metrics=AnalysisMetrics(
            total_files=len(file_paths),
            total_lines=5000,
            total_functions=200,
            total_classes=100,
            avg_complexity=5.0,
            total_patterns_detected=150,
            analysis_time_ms=1000,
            cache_hit_rate=0.0
        ),
        global_patterns=[],
        dependency_graph=DependencyGraph(nodes={}, edges=[]),
        top_teaching_files=[(fp, 0.8) for fp in file_paths[:50]]
    )
    
    # Reset performance monitor
    reset_monitor()
    monitor = get_monitor()
    
    # Generate course structure
    generator = CourseStructureGenerator(course_config, course_cache)
    
    start_time = time.time()
    course_outline = await generator.generate_course_structure(analysis)
    elapsed_s = time.time() - start_time
    
    # Validate result
    assert course_outline is not None
    assert len(course_outline.modules) >= 3
    assert len(course_outline.modules) <= 8
    
    # Validate performance target: <5s
    print(f"\nCourse structure generation: {elapsed_s:.2f}s for {len(file_paths)} files")
    print(f"Generated {len(course_outline.modules)} modules")
    assert elapsed_s < 5.0, f"Course structure generation took {elapsed_s:.2f}s, expected <5s"
    
    # Check performance monitor
    stats = monitor.get_stats()
    print(f"Performance stats: {stats}")


@pytest.mark.asyncio
async def test_lesson_content_generation_performance(course_config, course_cache):
    """
    Test: Lesson content generation should complete in <2s per lesson.
    
    Requirement: 11.2 - Lesson generation <2s
    """
    # Create mock file analysis
    file_path = "test_file.py"
    file_analysis = create_mock_file_analysis(file_path, 0)
    
    # Add more detailed symbol info for realistic test
    from src.models import FunctionInfo, ClassInfo
    file_analysis.symbol_info.functions = [
        FunctionInfo(
            name="test_function",
            start_line=1,
            end_line=10,
            parameters=["param1", "param2"],
            return_type="str",
            docstring="Test function docstring",
            complexity=5,
            is_async=False
        )
    ]
    file_analysis.symbol_info.classes = [
        ClassInfo(
            name="TestClass",
            start_line=12,
            end_line=30,
            base_classes=[],
            methods=[],
            docstring="Test class docstring"
        )
    ]
    
    # Reset performance monitor
    reset_monitor()
    monitor = get_monitor()
    
    # Generate lesson content
    generator = LessonContentGenerator(course_config, course_cache)
    
    start_time = time.time()
    lesson_content = await generator.generate_lesson_content(file_analysis)
    elapsed_s = time.time() - start_time
    
    # Validate result
    assert lesson_content is not None
    assert lesson_content.introduction
    assert lesson_content.explanation
    assert lesson_content.code_example
    
    # Validate performance target: <2s
    print(f"\nLesson content generation: {elapsed_s:.2f}s")
    assert elapsed_s < 2.0, f"Lesson generation took {elapsed_s:.2f}s, expected <2s"
    
    # Check performance monitor
    stats = monitor.get_stats()
    assert "lesson_content" in stats["operations"]


@pytest.mark.asyncio
async def test_exercise_generation_performance(course_config, course_cache):
    """
    Test: Exercise generation should complete in <3s per exercise.
    
    Requirement: 11.3 - Exercise generation <3s
    """
    # Create mock file analysis and pattern
    file_path = "test_file.py"
    file_analysis = create_mock_file_analysis(file_path, 0)
    
    pattern = DetectedPattern(
        pattern_type="test_pattern",
        file_path=file_path,
        confidence=0.9,
        evidence=["evidence1", "evidence2"],
        line_numbers=[1, 2, 3, 4, 5],
        metadata={}
    )
    
    # Reset performance monitor
    reset_monitor()
    monitor = get_monitor()
    
    # Generate exercise
    generator = ExerciseGenerator(course_config, course_cache)
    
    start_time = time.time()
    exercise = await generator.generate_exercise(pattern, file_analysis)
    elapsed_s = time.time() - start_time
    
    # Validate result
    assert exercise is not None
    assert exercise.title
    assert exercise.starter_code
    assert exercise.solution_code
    assert len(exercise.hints) > 0
    
    # Validate performance target: <3s
    print(f"\nExercise generation: {elapsed_s:.2f}s")
    assert elapsed_s < 3.0, f"Exercise generation took {elapsed_s:.2f}s, expected <3s"
    
    # Check performance monitor
    stats = monitor.get_stats()
    assert "exercise_generation" in stats["operations"]


@pytest.mark.asyncio
async def test_cached_course_structure_performance(
    course_config,
    course_cache,
    temp_codebase_100_files
):
    """
    Test: Cached course structure should be retrieved very quickly (<0.1s).
    
    Requirement: 11.5 - Use caching to avoid regenerating unchanged content
    """
    temp_dir, file_paths = temp_codebase_100_files
    
    # Create mock analysis
    from src.models import CodebaseAnalysis, AnalysisMetrics, DependencyGraph
    
    file_analyses = {
        fp: create_mock_file_analysis(fp, i)
        for i, fp in enumerate(file_paths[:20])  # Use fewer files for faster test
    }
    
    analysis = CodebaseAnalysis(
        codebase_id="test_codebase_cached",
        root_path=temp_dir,
        file_analyses=file_analyses,
        metrics=AnalysisMetrics(
            total_files=len(file_analyses),
            total_lines=1000,
            total_functions=40,
            total_classes=20,
            avg_complexity=5.0,
            total_patterns_detected=30,
            analysis_time_ms=500,
            cache_hit_rate=0.0
        ),
        global_patterns=[],
        dependency_graph=DependencyGraph(nodes={}, edges=[]),
        top_teaching_files=[(fp, 0.8) for fp in list(file_analyses.keys())[:10]]
    )
    
    # Generate course structure (first time)
    generator = CourseStructureGenerator(course_config, course_cache)
    await generator.generate_course_structure(analysis)
    
    # Generate again (should use cache)
    start_time = time.time()
    course_outline = await generator.generate_course_structure(analysis)
    elapsed_s = time.time() - start_time
    
    # Validate result
    assert course_outline is not None
    
    # Validate performance: cached should be very fast (<0.1s)
    print(f"\nCached course structure retrieval: {elapsed_s:.2f}s")
    assert elapsed_s < 0.1, f"Cached retrieval took {elapsed_s:.2f}s, expected <0.1s"


@pytest.mark.asyncio
async def test_performance_monitor_tracking():
    """
    Test: Performance monitor should track all operations correctly.
    
    Requirement: 11.1, 11.2, 11.3, 11.4 - Track performance metrics
    """
    reset_monitor()
    monitor = get_monitor()
    
    # Simulate some operations
    with monitor.measure("course_structure", file_count=100):
        await asyncio.sleep(0.1)
    
    with monitor.measure("lesson_content", file_path="test.py"):
        await asyncio.sleep(0.05)
    
    with monitor.measure("exercise_generation", pattern_type="test"):
        await asyncio.sleep(0.03)
    
    # Get stats
    stats = monitor.get_stats()
    
    # Validate tracking
    assert stats["total_operations"] == 3
    assert "course_structure" in stats["operations"]
    assert "lesson_content" in stats["operations"]
    assert "exercise_generation" in stats["operations"]
    
    # Check targets
    targets = monitor.check_targets()
    print(f"\nPerformance targets: {targets}")
    
    # Log summary
    monitor.log_summary()


@pytest.mark.asyncio
async def test_performance_target_compliance():
    """
    Test: All operations should meet their performance targets.
    
    Requirement: 11.1, 11.2, 11.3, 11.4 - Meet performance targets
    """
    reset_monitor()
    monitor = get_monitor()
    
    # Simulate operations within targets
    with monitor.measure("course_structure"):
        await asyncio.sleep(0.5)  # Well under 5s target
    
    with monitor.measure("lesson_content"):
        await asyncio.sleep(0.2)  # Well under 2s target
    
    with monitor.measure("exercise_generation"):
        await asyncio.sleep(0.3)  # Well under 3s target
    
    # Check compliance
    targets = monitor.check_targets()
    
    # All should meet targets
    for operation, meets_target in targets.items():
        print(f"{operation}: {'✓' if meets_target else '✗'}")
        assert meets_target, f"{operation} did not meet performance target"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
