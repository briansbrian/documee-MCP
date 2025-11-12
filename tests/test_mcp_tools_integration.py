"""Integration tests for MCP tools.

Tests Requirements 10.1, 10.2, 10.3, 10.4, 10.5:
- export_course with various formats
- generate_lesson_outline
- create_exercise
- Error handling
"""

import pytest
import pytest_asyncio
import os
import json
import tempfile
import shutil
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

# Import server module and app context
import src.server
from src.server import AppContext

# Import models
from src.models import (
    CodebaseAnalysis,
    FileAnalysis,
    SymbolInfo,
    DetectedPattern,
    ComplexityMetrics,
    TeachingValueScore,
    DependencyGraph,
    CodebaseMetrics,
    FunctionInfo,
    ClassInfo,
    ImportInfo
)

from src.cache.unified_cache import UnifiedCacheManager
from src.config.settings import Settings
from src.analysis.engine import AnalysisEngine
from src.analysis.config import AnalysisConfig


# ========== Helper Functions ==========

def get_mcp_tool(tool_name: str):
    """Get the actual function from an MCP tool."""
    return src.server.mcp._tool_manager._tools[tool_name].fn


# ========== Test Fixtures ==========

@pytest_asyncio.fixture
async def mock_app_context():
    """Create a mock app context for testing."""
    # Create temporary cache database
    temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    temp_db.close()
    
    # Create cache manager
    cache_manager = UnifiedCacheManager(
        max_memory_mb=100,
        sqlite_path=temp_db.name,
        redis_url=None
    )
    await cache_manager.initialize()
    
    # Create config
    config = Settings()
    
    # Create analysis engine
    analysis_config = AnalysisConfig()
    analysis_engine = AnalysisEngine(cache_manager, analysis_config)
    
    # Create app context
    context = AppContext(
        cache_manager=cache_manager,
        config=config,
        analysis_engine=analysis_engine
    )
    
    # Patch global app_context
    import src.server
    original_context = src.server.app_context
    src.server.app_context = context
    
    yield context
    
    # Cleanup
    src.server.app_context = original_context
    await cache_manager.close()
    if os.path.exists(temp_db.name):
        os.unlink(temp_db.name)


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
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(content)
        temp_path = f.name
    
    yield temp_path
    
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def sample_file_analysis(temp_python_file):
    """Create a sample file analysis."""
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
                    methods=[],
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
            trivial_functions=[],
            avg_nesting_depth=1.2
        ),
        teaching_value=TeachingValueScore(
            total_score=0.75,
            documentation_score=0.9,
            complexity_score=0.6,
            pattern_score=0.8,
            structure_score=0.7,
            explanation="Good example of basic function and class",
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
def sample_codebase_analysis(sample_file_analysis, temp_python_file):
    """Create a sample codebase analysis."""
    file_analyses = {temp_python_file: sample_file_analysis}
    
    # Add more files for variety
    for i in range(2, 6):
        file_path = f"src/file{i}.py"
        file_analyses[file_path] = FileAnalysis(
            file_path=file_path,
            language="python",
            symbol_info=SymbolInfo(functions=[], classes=[], imports=[]),
            patterns=[
                DetectedPattern(
                    pattern_type="utility_function",
                    file_path=file_path,
                    confidence=0.8,
                    evidence=["utility"],
                    line_numbers=[1]
                )
            ],
            complexity_metrics=ComplexityMetrics(
                avg_complexity=3.0,
                max_complexity=3,
                min_complexity=3,
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
    
    dep_graph = DependencyGraph(
        nodes={},
        edges=[],
        circular_dependencies=[],
        external_dependencies={}
    )
    
    top_teaching_files = sorted(
        [(path, fa.teaching_value.total_score) for path, fa in file_analyses.items()],
        key=lambda x: x[1],
        reverse=True
    )
    
    return CodebaseAnalysis(
        codebase_id="test_codebase_123",
        file_analyses=file_analyses,
        dependency_graph=dep_graph,
        global_patterns=[],
        top_teaching_files=top_teaching_files,
        metrics=CodebaseMetrics(
            total_files=len(file_analyses),
            total_functions=5,
            total_classes=1,
            avg_complexity=2.0,
            avg_documentation_coverage=0.75,
            total_patterns_detected=len(file_analyses),
            analysis_time_ms=100.0,
            cache_hit_rate=0.0
        ),
        analyzed_at=datetime.now().isoformat()
    )


# ========== Test export_course Tool ==========

@pytest.mark.asyncio
async def test_export_course_mkdocs_format(mock_app_context, sample_codebase_analysis):
    """Test export_course with MkDocs format (Req 10.1, 10.4)."""
    print("\n🧪 Testing export_course with MkDocs format...")
    
    # Store analysis in cache
    cache_key = f"codebase:{sample_codebase_analysis.codebase_id}"
    await mock_app_context.cache_manager.set_analysis(cache_key, sample_codebase_analysis.to_dict())
    
    # Create temporary output directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Call export_course tool
        result = await get_mcp_tool('export_course')(
            codebase_id=sample_codebase_analysis.codebase_id,
            format="mkdocs",
            output_dir=temp_dir
        )
        
        # Verify result structure (Req 10.4)
        assert "export_path" in result
        assert "format" in result
        assert "statistics" in result
        assert "codebase_id" in result
        
        # Verify format
        assert result["format"] == "mkdocs"
        assert result["codebase_id"] == sample_codebase_analysis.codebase_id
        
        # Verify statistics
        stats = result["statistics"]
        assert "modules" in stats
        assert "lessons" in stats
        assert "exercises" in stats
        assert stats["modules"] > 0
        assert stats["lessons"] > 0
        
        # Verify export path exists
        assert os.path.exists(result["export_path"])
        
        # Verify MkDocs structure (export_path is the output directory)
        mkdocs_yml = os.path.join(temp_dir, "mkdocs.yml")
        assert os.path.exists(mkdocs_yml), f"mkdocs.yml should exist at {mkdocs_yml}"
        
        docs_dir = os.path.join(temp_dir, "docs")
        assert os.path.exists(docs_dir), f"docs/ directory should exist at {docs_dir}"
        
        print(f"✅ MkDocs export successful: {result['export_path']}")
        print(f"   Modules: {stats['modules']}, Lessons: {stats['lessons']}, Exercises: {stats['exercises']}")


@pytest.mark.asyncio
async def test_export_course_json_format(mock_app_context, sample_codebase_analysis):
    """Test export_course with JSON format (Req 10.1, 10.4)."""
    print("\n🧪 Testing export_course with JSON format...")
    
    # Store analysis in cache
    cache_key = f"codebase:{sample_codebase_analysis.codebase_id}"
    await mock_app_context.cache_manager.set_analysis(cache_key, sample_codebase_analysis.to_dict())
    
    # Create temporary output directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Call export_course tool
        result = await get_mcp_tool('export_course')(
            codebase_id=sample_codebase_analysis.codebase_id,
            format="json",
            output_dir=temp_dir
        )
        
        # Verify result structure
        assert result["format"] == "json"
        assert os.path.exists(result["export_path"])
        
        # Verify JSON file exists
        json_file = os.path.join(temp_dir, "course.json")
        assert os.path.exists(json_file), f"course.json should exist at {json_file}"
        
        # Verify JSON is valid
        with open(json_file, 'r') as f:
            course_data = json.load(f)
            assert "course_id" in course_data
            assert "modules" in course_data
            assert len(course_data["modules"]) > 0
        
        print(f"✅ JSON export successful: {json_file}")


@pytest.mark.asyncio
async def test_export_course_markdown_format(mock_app_context, sample_codebase_analysis):
    """Test export_course with Markdown format (Req 10.1, 10.4)."""
    print("\n🧪 Testing export_course with Markdown format...")
    
    # Store analysis in cache
    cache_key = f"codebase:{sample_codebase_analysis.codebase_id}"
    await mock_app_context.cache_manager.set_analysis(cache_key, sample_codebase_analysis.to_dict())
    
    # Create temporary output directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Call export_course tool
        result = await get_mcp_tool('export_course')(
            codebase_id=sample_codebase_analysis.codebase_id,
            format="markdown",
            output_dir=temp_dir
        )
        
        # Verify result structure
        assert result["format"] == "markdown"
        assert os.path.exists(result["export_path"])
        
        # Verify markdown files exist
        readme = os.path.join(temp_dir, "README.md")
        assert os.path.exists(readme), f"README.md should exist at {readme}"
        
        print(f"✅ Markdown export successful: {result['export_path']}")


@pytest.mark.asyncio
async def test_export_course_invalid_format(mock_app_context, sample_codebase_analysis):
    """Test export_course with invalid format (Req 10.5 - error handling)."""
    print("\n🧪 Testing export_course with invalid format...")
    
    # Store analysis in cache
    cache_key = f"codebase:{sample_codebase_analysis.codebase_id}"
    await mock_app_context.cache_manager.set_analysis(cache_key, sample_codebase_analysis.to_dict())
    
    # Call export_course with invalid format
    with pytest.raises(ValueError) as exc_info:
        await get_mcp_tool('export_course')(
            codebase_id=sample_codebase_analysis.codebase_id,
            format="invalid_format"
        )
    
    # Verify error message
    assert "Invalid format" in str(exc_info.value)
    assert "Supported formats" in str(exc_info.value)
    
    print(f"✅ Invalid format error handled correctly: {exc_info.value}")


@pytest.mark.asyncio
async def test_export_course_missing_analysis(mock_app_context):
    """Test export_course with missing analysis (Req 10.5 - error handling)."""
    print("\n🧪 Testing export_course with missing analysis...")
    
    # Call export_course without storing analysis first
    with pytest.raises(ValueError) as exc_info:
        await get_mcp_tool('export_course')(
            codebase_id="nonexistent_codebase",
            format="mkdocs"
        )
    
    # Verify error message
    assert "not analyzed" in str(exc_info.value).lower()
    assert "analyze_codebase_tool" in str(exc_info.value)
    
    print(f"✅ Missing analysis error handled correctly: {exc_info.value}")


@pytest.mark.asyncio
async def test_export_course_empty_codebase_id(mock_app_context):
    """Test export_course with empty codebase_id (Req 10.5 - error handling)."""
    print("\n🧪 Testing export_course with empty codebase_id...")
    
    # Call export_course with empty codebase_id
    with pytest.raises(ValueError) as exc_info:
        await get_mcp_tool('export_course')(
            codebase_id="",
            format="mkdocs"
        )
    
    # Verify error message
    assert "required" in str(exc_info.value).lower()
    assert "cannot be empty" in str(exc_info.value).lower()
    
    print(f"✅ Empty codebase_id error handled correctly: {exc_info.value}")


# ========== Test generate_lesson_outline Tool ==========

@pytest.mark.asyncio
async def test_generate_lesson_outline_success(mock_app_context, temp_python_file):
    """Test generate_lesson_outline with valid file (Req 10.2, 10.4)."""
    print("\n🧪 Testing generate_lesson_outline with valid file...")
    
    # Call generate_lesson_outline tool
    result = await get_mcp_tool('generate_lesson_outline')(file_path=temp_python_file)
    
    # Verify result structure (Req 10.4)
    assert "title" in result
    assert "file_path" in result
    assert "learning_objectives" in result
    assert "key_concepts" in result
    assert "difficulty" in result
    assert "estimated_duration_minutes" in result
    assert "code_examples" in result
    assert "suggested_exercises" in result
    assert "patterns" in result
    assert "teaching_value_score" in result
    
    # Verify file path
    assert result["file_path"] == temp_python_file
    
    # Verify learning objectives
    assert isinstance(result["learning_objectives"], list)
    assert len(result["learning_objectives"]) >= 1
    
    # Verify difficulty
    assert result["difficulty"] in ["beginner", "intermediate", "advanced"]
    
    # Verify duration
    assert result["estimated_duration_minutes"] > 0
    assert result["estimated_duration_minutes"] <= 15
    
    # Verify teaching value score
    assert 0.0 <= result["teaching_value_score"] <= 1.0
    
    print(f"✅ Lesson outline generated successfully")
    print(f"   Title: {result['title']}")
    print(f"   Difficulty: {result['difficulty']}")
    print(f"   Duration: {result['estimated_duration_minutes']} minutes")
    print(f"   Objectives: {len(result['learning_objectives'])}")


@pytest.mark.asyncio
async def test_generate_lesson_outline_file_not_found(mock_app_context):
    """Test generate_lesson_outline with non-existent file (Req 10.5 - error handling)."""
    print("\n🧪 Testing generate_lesson_outline with non-existent file...")
    
    # Call generate_lesson_outline with non-existent file
    with pytest.raises(ValueError) as exc_info:
        await get_mcp_tool('generate_lesson_outline')(file_path="nonexistent_file.py")
    
    # Verify error message
    assert "not found" in str(exc_info.value).lower()
    
    print(f"✅ File not found error handled correctly: {exc_info.value}")


@pytest.mark.asyncio
async def test_generate_lesson_outline_empty_path(mock_app_context):
    """Test generate_lesson_outline with empty path (Req 10.5 - error handling)."""
    print("\n🧪 Testing generate_lesson_outline with empty path...")
    
    # Call generate_lesson_outline with empty path
    with pytest.raises(ValueError) as exc_info:
        await get_mcp_tool('generate_lesson_outline')(file_path="")
    
    # Verify error message
    assert "required" in str(exc_info.value).lower()
    assert "cannot be empty" in str(exc_info.value).lower()
    
    print(f"✅ Empty path error handled correctly: {exc_info.value}")


# ========== Test create_exercise Tool ==========

@pytest.mark.asyncio
async def test_create_exercise_generic(mock_app_context):
    """Test create_exercise without codebase (Req 10.3, 10.4)."""
    print("\n🧪 Testing create_exercise with generic pattern...")
    
    # Call create_exercise tool
    result = await get_mcp_tool('create_exercise')(
        pattern_type="function_implementation",
        difficulty="intermediate"
    )
    
    # Verify result structure (Req 10.4)
    assert "exercise_id" in result
    assert "title" in result
    assert "description" in result
    assert "difficulty" in result
    assert "estimated_minutes" in result
    assert "instructions" in result
    assert "starter_code" in result
    assert "solution_code" in result
    assert "hints" in result
    assert "test_cases" in result
    assert "learning_objectives" in result
    assert "pattern_type" in result
    
    # Verify pattern type
    assert result["pattern_type"] == "function_implementation"
    
    # Verify difficulty
    assert result["difficulty"] == "intermediate"
    
    # Verify instructions
    assert isinstance(result["instructions"], list)
    assert len(result["instructions"]) > 0
    
    # Verify hints
    assert isinstance(result["hints"], list)
    assert len(result["hints"]) > 0
    
    # Verify test cases
    assert isinstance(result["test_cases"], list)
    
    # Verify learning objectives
    assert isinstance(result["learning_objectives"], list)
    assert len(result["learning_objectives"]) > 0
    
    print(f"✅ Exercise created successfully")
    print(f"   Title: {result['title']}")
    print(f"   Difficulty: {result['difficulty']}")
    print(f"   Duration: {result['estimated_minutes']} minutes")
    print(f"   Instructions: {len(result['instructions'])}")
    print(f"   Hints: {len(result['hints'])}")


@pytest.mark.asyncio
async def test_create_exercise_with_codebase(mock_app_context, sample_codebase_analysis):
    """Test create_exercise with codebase context (Req 10.3, 10.4)."""
    print("\n🧪 Testing create_exercise with codebase context...")
    
    # Store analysis in cache
    cache_key = f"codebase:{sample_codebase_analysis.codebase_id}"
    await mock_app_context.cache_manager.set_analysis(cache_key, sample_codebase_analysis.to_dict())
    
    # Call create_exercise tool with codebase_id
    result = await get_mcp_tool('create_exercise')(
        pattern_type="function_implementation",
        difficulty="beginner",
        codebase_id=sample_codebase_analysis.codebase_id
    )
    
    # Verify result structure
    assert "exercise_id" in result
    assert "pattern_type" in result
    assert result["pattern_type"] == "function_implementation"
    assert result["difficulty"] == "beginner"
    
    # Verify beginner difficulty adjustments
    assert result["estimated_minutes"] <= 15
    
    print(f"✅ Exercise created from codebase successfully")
    print(f"   Pattern: {result['pattern_type']}")
    print(f"   Difficulty: {result['difficulty']}")


@pytest.mark.asyncio
async def test_create_exercise_advanced_difficulty(mock_app_context):
    """Test create_exercise with advanced difficulty (Req 10.3, 10.4)."""
    print("\n🧪 Testing create_exercise with advanced difficulty...")
    
    # Call create_exercise tool with advanced difficulty
    result = await get_mcp_tool('create_exercise')(
        pattern_type="api_route",
        difficulty="advanced"
    )
    
    # Verify difficulty
    assert result["difficulty"] == "advanced"
    
    # Verify advanced difficulty adjustments
    assert result["estimated_minutes"] >= 30
    
    print(f"✅ Advanced exercise created successfully")
    print(f"   Duration: {result['estimated_minutes']} minutes")


@pytest.mark.asyncio
async def test_create_exercise_empty_pattern(mock_app_context):
    """Test create_exercise with empty pattern_type (Req 10.5 - error handling)."""
    print("\n🧪 Testing create_exercise with empty pattern_type...")
    
    # Call create_exercise with empty pattern_type
    with pytest.raises(ValueError) as exc_info:
        await get_mcp_tool('create_exercise')(pattern_type="")
    
    # Verify error message
    assert "required" in str(exc_info.value).lower()
    assert "cannot be empty" in str(exc_info.value).lower()
    
    print(f"✅ Empty pattern error handled correctly: {exc_info.value}")


@pytest.mark.asyncio
async def test_create_exercise_invalid_difficulty(mock_app_context):
    """Test create_exercise with invalid difficulty (Req 10.5 - error handling)."""
    print("\n🧪 Testing create_exercise with invalid difficulty...")
    
    # Call create_exercise with invalid difficulty
    with pytest.raises(ValueError) as exc_info:
        await get_mcp_tool('create_exercise')(
            pattern_type="function_implementation",
            difficulty="invalid"
        )
    
    # Verify error message
    assert "Invalid difficulty" in str(exc_info.value)
    assert "beginner" in str(exc_info.value)
    assert "intermediate" in str(exc_info.value)
    assert "advanced" in str(exc_info.value)
    
    print(f"✅ Invalid difficulty error handled correctly: {exc_info.value}")


# ========== Test Error Handling ==========

@pytest.mark.asyncio
async def test_export_course_server_not_initialized():
    """Test export_course when server not initialized (Req 10.5)."""
    print("\n🧪 Testing export_course with uninitialized server...")
    
    # Temporarily set app_context to None
    import src.server
    original_context = src.server.app_context
    src.server.app_context = None
    
    try:
        # Call export_course
        with pytest.raises(RuntimeError) as exc_info:
            await get_mcp_tool('export_course')(
                codebase_id="test_id",
                format="mkdocs"
            )
        
        # Verify error message
        assert "not initialized" in str(exc_info.value).lower()
        
        print(f"✅ Server not initialized error handled correctly: {exc_info.value}")
    finally:
        # Restore app_context
        src.server.app_context = original_context


@pytest.mark.asyncio
async def test_generate_lesson_outline_server_not_initialized(temp_python_file):
    """Test generate_lesson_outline when server not initialized (Req 10.5)."""
    print("\n🧪 Testing generate_lesson_outline with uninitialized server...")
    
    # Temporarily set app_context to None
    import src.server
    original_context = src.server.app_context
    src.server.app_context = None
    
    try:
        # Call generate_lesson_outline
        with pytest.raises(RuntimeError) as exc_info:
            await get_mcp_tool('generate_lesson_outline')(file_path=temp_python_file)
        
        # Verify error message
        assert "not initialized" in str(exc_info.value).lower()
        
        print(f"✅ Server not initialized error handled correctly: {exc_info.value}")
    finally:
        # Restore app_context
        src.server.app_context = original_context


@pytest.mark.asyncio
async def test_create_exercise_server_not_initialized():
    """Test create_exercise when server not initialized (Req 10.5)."""
    print("\n🧪 Testing create_exercise with uninitialized server...")
    
    # Temporarily set app_context to None
    import src.server
    original_context = src.server.app_context
    src.server.app_context = None
    
    try:
        # Call create_exercise
        with pytest.raises(RuntimeError) as exc_info:
            await get_mcp_tool('create_exercise')(pattern_type="function_implementation")
        
        # Verify error message
        assert "not initialized" in str(exc_info.value).lower()
        
        print(f"✅ Server not initialized error handled correctly: {exc_info.value}")
    finally:
        # Restore app_context
        src.server.app_context = original_context


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
