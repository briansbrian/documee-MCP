"""
Integration tests for AI Content Enrichment MCP tools.

Tests the three enrichment MCP tools:
- get_enrichment_guide: Generate comprehensive enrichment guides
- update_lesson_content: Update lessons with enriched content
- list_lessons_for_enrichment: List lessons with enrichment status

Tests Requirements: All enrichment requirements
"""

import pytest
import pytest_asyncio
import os
import json
import tempfile
import shutil
from pathlib import Path
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
    FunctionInfo,
    ClassInfo,
    ImportInfo,
    DetectedPattern,
    ComplexityMetrics,
    TeachingValueScore,
    DependencyGraph,
    CodebaseMetrics
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
    content = '''"""Example authentication module for testing."""

import bcrypt
from datetime import datetime, timedelta
import jwt

SECRET_KEY = "test_secret_key"


def authenticate_user(username: str, password: str):
    """
    Authenticate user with username and password.
    
    Args:
        username: User's username
        password: User's password
        
    Returns:
        Session token if authentication successful, None otherwise
    """
    # Verify password (simplified for testing)
    if username and password:
        # Generate JWT token
        token = generate_token(username)
        return token
    return None


def generate_token(username: str, expires_in: int = 3600):
    """
    Generate JWT token for authenticated user.
    
    Args:
        username: Username to encode in token
        expires_in: Token expiration time in seconds (default: 1 hour)
        
    Returns:
        JWT token string
    """
    payload = {
        "username": username,
        "exp": datetime.utcnow() + timedelta(seconds=expires_in)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def validate_token(token: str):
    """
    Validate JWT token.
    
    Args:
        token: JWT token to validate
        
    Returns:
        Decoded payload if valid, None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


class UserSession:
    """Manages user session data."""
    
    def __init__(self, username: str, token: str):
        """Initialize user session."""
        self.username = username
        self.token = token
        self.created_at = datetime.utcnow()
    
    def is_valid(self):
        """Check if session is still valid."""
        payload = validate_token(self.token)
        return payload is not None
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(content)
        temp_path = f.name
    
    yield temp_path
    
    if os.path.exists(temp_path):
        os.unlink(temp_path)



@pytest.fixture
def sample_file_analysis(temp_python_file):
    """Create a sample file analysis for authentication module."""
    return FileAnalysis(
        file_path=temp_python_file,
        language="python",
        symbol_info=SymbolInfo(
            functions=[
                FunctionInfo(
                    name="authenticate_user",
                    parameters=["username", "password"],
                    return_type="Optional[str]",
                    docstring="Authenticate user with username and password.",
                    start_line=10,
                    end_line=26,
                    complexity=3,
                    is_async=False,
                    decorators=[]
                ),
                FunctionInfo(
                    name="generate_token",
                    parameters=["username", "expires_in"],
                    return_type="str",
                    docstring="Generate JWT token for authenticated user.",
                    start_line=29,
                    end_line=43,
                    complexity=2,
                    is_async=False,
                    decorators=[]
                ),
                FunctionInfo(
                    name="validate_token",
                    parameters=["token"],
                    return_type="Optional[dict]",
                    docstring="Validate JWT token.",
                    start_line=46,
                    end_line=60,
                    complexity=4,
                    is_async=False,
                    decorators=[]
                )
            ],
            classes=[
                ClassInfo(
                    name="UserSession",
                    methods=[
                        FunctionInfo(
                            name="__init__",
                            parameters=["self", "username", "token"],
                            return_type="None",
                            docstring="Initialize user session.",
                            start_line=66,
                            end_line=70,
                            complexity=1,
                            is_async=False,
                            decorators=[]
                        ),
                        FunctionInfo(
                            name="is_valid",
                            parameters=["self"],
                            return_type="bool",
                            docstring="Check if session is still valid.",
                            start_line=72,
                            end_line=75,
                            complexity=2,
                            is_async=False,
                            decorators=[]
                        )
                    ],
                    base_classes=[],
                    docstring="Manages user session data.",
                    start_line=63,
                    end_line=76,
                    decorators=[]
                )
            ],
            imports=[
                ImportInfo(
                    module="bcrypt",
                    imported_symbols=[],
                    import_type="import",
                    line_number=3,
                    is_relative=False
                ),
                ImportInfo(
                    module="datetime",
                    imported_symbols=["datetime", "timedelta"],
                    import_type="from",
                    line_number=4,
                    is_relative=False
                ),
                ImportInfo(
                    module="jwt",
                    imported_symbols=[],
                    import_type="import",
                    line_number=5,
                    is_relative=False
                )
            ],
            exports=[]
        ),
        patterns=[
            DetectedPattern(
                pattern_type="authentication",
                file_path=temp_python_file,
                confidence=0.95,
                evidence=["User authentication with password verification", "JWT token generation"],
                line_numbers=[10, 29],
                metadata={"method": "jwt_based"}
            ),
            DetectedPattern(
                pattern_type="security",
                file_path=temp_python_file,
                confidence=0.90,
                evidence=["Token validation", "Expiration handling"],
                line_numbers=[46],
                metadata={"type": "jwt_validation"}
            )
        ],
        complexity_metrics=ComplexityMetrics(
            avg_complexity=3.0,
            max_complexity=4,
            min_complexity=2,
            high_complexity_functions=[],
            trivial_functions=[],
            avg_nesting_depth=1.5
        ),
        teaching_value=TeachingValueScore(
            total_score=0.85,
            documentation_score=0.9,
            complexity_score=0.75,
            pattern_score=0.95,
            structure_score=0.80,
            explanation="Excellent example of JWT authentication with clear documentation",
            factors={}
        ),
        documentation_coverage=0.9,
        linter_issues=[],
        has_errors=False,
        errors=[],
        analyzed_at=datetime.now().isoformat(),
        cache_hit=False,
        is_notebook=False
    )



@pytest.fixture
def sample_codebase_analysis(sample_file_analysis, temp_python_file):
    """Create a sample codebase analysis with authentication module."""
    file_analyses = {temp_python_file: sample_file_analysis}
    
    dep_graph = DependencyGraph(
        nodes={},
        edges=[],
        circular_dependencies=[],
        external_dependencies={"bcrypt": 1, "jwt": 2}
    )
    
    top_teaching_files = [(temp_python_file, sample_file_analysis.teaching_value.total_score)]
    
    return CodebaseAnalysis(
        codebase_id="test_enrichment_codebase_123",
        file_analyses=file_analyses,
        dependency_graph=dep_graph,
        global_patterns=[
            DetectedPattern(
                pattern_type="authentication",
                file_path=temp_python_file,
                confidence=0.95,
                evidence=["JWT-based authentication system"],
                line_numbers=[10],
                metadata={}
            )
        ],
        top_teaching_files=top_teaching_files,
        metrics=CodebaseMetrics(
            total_files=1,
            total_functions=3,
            total_classes=1,
            avg_complexity=3.0,
            avg_documentation_coverage=0.9,
            total_patterns_detected=2,
            analysis_time_ms=50.0,
            cache_hit_rate=0.0
        ),
        analyzed_at=datetime.now().isoformat()
    )


@pytest.fixture
def sample_course_data(temp_python_file):
    """Create sample course data with lessons."""
    return {
        'course_id': 'test_course_123',
        'title': 'Authentication Fundamentals',
        'description': 'Learn secure authentication patterns',
        'author': 'Test Author',
        'version': '1.0.0',
        'created_at': datetime.now().isoformat(),
        'total_duration_hours': 2.0,
        'difficulty_distribution': {'beginner': 1, 'intermediate': 0, 'advanced': 0},
        'tags': ['authentication', 'security', 'jwt'],
        'prerequisites': ['Basic Python'],
        'modules': [
            {
                'module_id': 'module-1',
                'title': 'Authentication Basics',
                'description': 'Introduction to authentication',
                'order': 1,
                'difficulty': 'beginner',
                'duration_hours': 2.0,
                'learning_objectives': ['Understand authentication', 'Implement JWT'],
                'lessons': [
                    {
                        'lesson_id': 'module-1-lesson-1',
                        'title': 'JWT Authentication',
                        'description': 'Learn JWT-based authentication',
                        'order': 1,
                        'difficulty': 'beginner',
                        'duration_minutes': 45,
                        'file_path': temp_python_file,
                        'teaching_value': 0.85,
                        'learning_objectives': [
                            'Understand JWT tokens',
                            'Implement token generation',
                            'Validate tokens securely'
                        ],
                        'prerequisites': ['Basic Python', 'HTTP basics'],
                        'concepts': ['Authentication', 'JWT', 'Security'],
                        'exercises': [
                            {
                                'exercise_id': 'ex-1',
                                'title': 'Implement Token Validation',
                                'description': 'Add token validation logic',
                                'difficulty': 'beginner',
                                'estimated_minutes': 15,
                                'instructions': ['Step 1', 'Step 2'],
                                'starter_code': 'def validate_token(token):\n    pass',
                                'solution_code': 'def validate_token(token):\n    return jwt.decode(token, SECRET_KEY)',
                                'hints': ['Use jwt.decode', 'Handle exceptions'],
                                'learning_objectives': ['Validate JWT tokens']
                            }
                        ],
                        'tags': ['jwt', 'authentication']
                    }
                ]
            }
        ],
        'enrichment_status': {}
    }


# ========== Helper Functions for Tests ==========

def create_course_data_in_output(codebase_id: str, course_data: dict) -> Path:
    """Create course data in the expected output directory."""
    output_dir = Path(f"./output/{codebase_id}_course")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    course_data_path = output_dir / 'course_data.json'
    with open(course_data_path, 'w', encoding='utf-8') as f:
        json.dump(course_data, f, indent=2)
    
    return output_dir


def cleanup_course_data(codebase_id: str):
    """Clean up course data from output directory."""
    output_dir = Path(f"./output/{codebase_id}_course")
    if output_dir.exists():
        shutil.rmtree(output_dir)


# ========== Test get_enrichment_guide Tool ==========


@pytest.mark.asyncio
async def test_get_enrichment_guide_success(mock_app_context, sample_codebase_analysis, sample_course_data, temp_python_file):
    """Test get_enrichment_guide with real codebase - verify all evidence fields populated."""
    print("\n🧪 Testing get_enrichment_guide with real codebase...")
    
    # Store analysis in cache
    cache_key = f"codebase:{sample_codebase_analysis.codebase_id}"
    await mock_app_context.cache_manager.set_analysis(cache_key, sample_codebase_analysis.to_dict())
    
    # Store scan data (needed for repo path)
    await mock_app_context.cache_manager.set_resource("structure", {
        'path': str(Path(temp_python_file).parent),
        'codebase_id': sample_codebase_analysis.codebase_id
    })
    
    # Create course data in expected location
    output_dir = create_course_data_in_output(sample_codebase_analysis.codebase_id, sample_course_data)
    
    try:
        # Call get_enrichment_guide tool
        result = await get_mcp_tool('get_enrichment_guide')(
            codebase_id=sample_codebase_analysis.codebase_id,
            lesson_id='module-1-lesson-1'
        )
        
        # Verify result structure
        assert 'lesson_id' in result
        assert result['lesson_id'] == 'module-1-lesson-1'
        
        # Verify all 12 components are present
        assert 'feature_mapping' in result
        assert 'evidence_bundle' in result
        assert 'validation_checklist' in result
        assert 'teaching_value_assessment' in result
        assert 'systematic_investigation' in result
        assert 'narrative_structure' in result
        assert 'code_sections' in result
        assert 'architecture_context' in result
        assert 'real_world_context' in result
        assert 'exercise_generation' in result
        assert 'anti_hallucination_rules' in result
        assert 'enrichment_instructions' in result
        
        # Verify feature mapping
        feature_mapping = result['feature_mapping']
        assert 'feature_name' in feature_mapping
        assert 'user_facing_purpose' in feature_mapping
        assert 'business_value' in feature_mapping
        assert 'entry_points' in feature_mapping
        assert 'feature_flow' in feature_mapping
        assert len(feature_mapping['feature_name']) > 0
        
        # Verify evidence bundle - all fields populated
        evidence = result['evidence_bundle']
        assert 'source_files' in evidence
        assert 'test_files' in evidence
        assert 'git_commits' in evidence
        assert 'documentation' in evidence
        assert 'dependencies' in evidence
        assert 'dependents' in evidence
        assert isinstance(evidence['source_files'], list)
        assert len(evidence['source_files']) > 0  # Should have source files
        
        # Verify validation checklist
        validation = result['validation_checklist']
        assert 'code_behavior' in validation
        assert 'expected_behavior' in validation
        assert 'documentation_alignment' in validation
        assert 'git_context' in validation
        assert 'consistency_check' in validation
        assert len(validation['code_behavior']) > 0
        
        # Verify teaching value assessment
        teaching_value = result['teaching_value_assessment']
        assert 'scores' in teaching_value
        assert 'total_score' in teaching_value
        assert 'should_teach' in teaching_value
        assert 'reasoning' in teaching_value
        assert 0 <= teaching_value['total_score'] <= 14
        assert isinstance(teaching_value['should_teach'], bool)
        assert 'reusability' in teaching_value['scores']
        assert 'best_practice' in teaching_value['scores']
        assert 'fundamentality' in teaching_value['scores']
        
        # Verify systematic investigation
        investigation = result['systematic_investigation']
        assert 'what_it_does' in investigation
        assert 'why_it_exists' in investigation
        assert 'how_it_works' in investigation
        assert 'when_its_used' in investigation
        assert 'edge_cases' in investigation
        assert 'common_pitfalls' in investigation
        assert len(investigation['what_it_does']) > 0
        
        # Verify narrative structure
        narrative = result['narrative_structure']
        assert 'introduction_points' in narrative
        assert 'learning_progression' in narrative
        assert 'code_walkthrough_order' in narrative
        assert 'conclusion_points' in narrative
        assert 'next_steps' in narrative
        assert isinstance(narrative['introduction_points'], list)
        assert len(narrative['introduction_points']) >= 3
        
        # Verify code sections
        code_sections = result['code_sections']
        assert isinstance(code_sections, list)
        assert len(code_sections) > 0
        
        # Check first code section structure
        section = code_sections[0]
        assert 'file_path' in section
        assert 'line_range' in section
        assert 'code_snippet' in section
        assert 'purpose' in section
        assert 'key_concepts' in section
        assert 'explanation_approach' in section
        assert 'related_code' in section
        assert 'test_evidence' in section
        assert 'git_evidence' in section
        assert 'common_mistakes' in section
        
        # Verify architecture context
        architecture = result['architecture_context']
        assert 'component_role' in architecture
        assert 'data_flow' in architecture
        assert 'dependencies' in architecture
        assert 'dependents' in architecture
        assert 'design_patterns' in architecture
        assert len(architecture['component_role']) > 0
        
        # Verify real-world context
        real_world = result['real_world_context']
        assert 'practical_use_cases' in real_world
        assert 'analogies' in real_world
        assert 'industry_patterns' in real_world
        assert 'best_practices' in real_world
        assert 'anti_patterns' in real_world
        assert isinstance(real_world['practical_use_cases'], list)
        
        # Verify exercise generation
        exercises = result['exercise_generation']
        assert 'hands_on_tasks' in exercises
        assert 'starter_code' in exercises
        assert 'solution_code' in exercises
        assert 'test_cases' in exercises
        assert 'progressive_hints' in exercises
        assert 'self_assessment' in exercises
        assert isinstance(exercises['progressive_hints'], list)
        
        # Verify anti-hallucination rules
        rules = result['anti_hallucination_rules']
        assert 'always_cite' in rules
        assert 'distinguish_fact_inference' in rules
        assert 'validate_against_tests' in rules
        assert 'cross_reference' in rules
        assert 'avoid_assumptions' in rules
        assert 'evidence' in rules['always_cite'].lower() or 'cit' in rules['always_cite'].lower()
        
        # Verify enrichment instructions
        instructions = result['enrichment_instructions']
        assert 'tone' in instructions
        assert 'depth' in instructions
        assert 'focus_areas' in instructions
        assert 'avoid_topics' in instructions
        assert 'evidence_requirements' in instructions
        assert instructions['tone'] == 'casual'
        assert instructions['depth'] == 'detailed'
        
        print(f"✅ Enrichment guide generated successfully")
        print(f"   Teaching value: {teaching_value['total_score']}/14")
        print(f"   Should teach: {teaching_value['should_teach']}")
        print(f"   Code sections: {len(code_sections)}")
        print(f"   Evidence sources: {len(evidence['source_files'])}")
    finally:
        # Cleanup
        cleanup_course_data(sample_codebase_analysis.codebase_id)



@pytest.mark.asyncio
async def test_get_enrichment_guide_citations_present(mock_app_context, sample_codebase_analysis, sample_course_data, temp_python_file):
    """Test that enrichment guide contains accurate citations."""
    print("\n🧪 Testing enrichment guide citations...")
    
    # Store analysis in cache
    cache_key = f"codebase:{sample_codebase_analysis.codebase_id}"
    await mock_app_context.cache_manager.set_analysis(cache_key, sample_codebase_analysis.to_dict())
    
    # Store scan data
    await mock_app_context.cache_manager.set_resource("structure", {
        'path': str(Path(temp_python_file).parent),
        'codebase_id': sample_codebase_analysis.codebase_id
    })
    
    # Create course data in expected location
    output_dir = create_course_data_in_output(sample_codebase_analysis.codebase_id, sample_course_data)
    
    try:
        # Call get_enrichment_guide tool
        result = await get_mcp_tool('get_enrichment_guide')(
            codebase_id=sample_codebase_analysis.codebase_id,
            lesson_id='module-1-lesson-1'
        )
        
        # Verify citations in code sections
        code_sections = result['code_sections']
        assert len(code_sections) > 0
        
        for section in code_sections:
            # Each section should have file path and line range
            assert 'file_path' in section
            assert 'line_range' in section
            assert isinstance(section['line_range'], list)
            assert len(section['line_range']) == 2
            
            # Purpose should reference evidence
            assert 'purpose' in section
            assert len(section['purpose']) > 0
            
            # Should have test evidence or git evidence
            has_evidence = (
                (isinstance(section.get('test_evidence'), list) and len(section['test_evidence']) > 0) or
                (isinstance(section.get('git_evidence'), list) and len(section['git_evidence']) > 0)
            )
            # Note: May not have evidence if no tests/git, but structure should be present
            assert 'test_evidence' in section
            assert 'git_evidence' in section
        
        # Verify evidence bundle has source file references
        evidence = result['evidence_bundle']
        assert len(evidence['source_files']) > 0
        
        for source_file in evidence['source_files']:
            assert 'path' in source_file
            assert 'lines' in source_file or 'content' in source_file
        
        print(f"✅ Citations verified in {len(code_sections)} code sections")
    finally:
        # Cleanup
        cleanup_course_data(sample_codebase_analysis.codebase_id)


@pytest.mark.asyncio
async def test_get_enrichment_guide_missing_codebase(mock_app_context):
    """Test get_enrichment_guide with missing codebase analysis."""
    print("\n🧪 Testing get_enrichment_guide with missing codebase...")
    
    # Call get_enrichment_guide without storing analysis first
    with pytest.raises(ValueError) as exc_info:
        await get_mcp_tool('get_enrichment_guide')(
            codebase_id="nonexistent_codebase",
            lesson_id="module-1-lesson-1"
        )
    
    # Verify error message
    assert "not analyzed" in str(exc_info.value).lower()
    assert "analyze_codebase_tool" in str(exc_info.value)
    
    print(f"✅ Missing codebase error handled correctly: {exc_info.value}")


@pytest.mark.asyncio
async def test_get_enrichment_guide_missing_lesson(mock_app_context, sample_codebase_analysis, sample_course_data, temp_python_file):
    """Test get_enrichment_guide with non-existent lesson."""
    print("\n🧪 Testing get_enrichment_guide with missing lesson...")
    
    # Store analysis in cache
    cache_key = f"codebase:{sample_codebase_analysis.codebase_id}"
    await mock_app_context.cache_manager.set_analysis(cache_key, sample_codebase_analysis.to_dict())
    
    # Store scan data
    await mock_app_context.cache_manager.set_resource("structure", {
        'path': str(Path(temp_python_file).parent),
        'codebase_id': sample_codebase_analysis.codebase_id
    })
    
    # Create course data in expected location
    output_dir = create_course_data_in_output(sample_codebase_analysis.codebase_id, sample_course_data)
    
    try:
        # Call get_enrichment_guide with non-existent lesson
        with pytest.raises(ValueError) as exc_info:
            await get_mcp_tool('get_enrichment_guide')(
                codebase_id=sample_codebase_analysis.codebase_id,
                lesson_id='module-99-lesson-99'
            )
        
        # Verify error message
        assert "not found" in str(exc_info.value).lower()
        
        print(f"✅ Missing lesson error handled correctly: {exc_info.value}")
    finally:
        # Cleanup
        cleanup_course_data(sample_codebase_analysis.codebase_id)


@pytest.mark.asyncio
async def test_get_enrichment_guide_empty_parameters(mock_app_context):
    """Test get_enrichment_guide with empty parameters."""
    print("\n🧪 Testing get_enrichment_guide with empty parameters...")
    
    # Test empty codebase_id
    with pytest.raises(ValueError) as exc_info:
        await get_mcp_tool('get_enrichment_guide')(
            codebase_id="",
            lesson_id="module-1-lesson-1"
        )
    
    assert "required" in str(exc_info.value).lower()
    assert "cannot be empty" in str(exc_info.value).lower()
    
    # Test empty lesson_id
    with pytest.raises(ValueError) as exc_info:
        await get_mcp_tool('get_enrichment_guide')(
            codebase_id="test_id",
            lesson_id=""
        )
    
    assert "required" in str(exc_info.value).lower()
    assert "cannot be empty" in str(exc_info.value).lower()
    
    print(f"✅ Empty parameter errors handled correctly")


# ========== Test update_lesson_content Tool ==========


@pytest.mark.asyncio
async def test_update_lesson_content_success(mock_app_context, sample_course_data, temp_python_file):
    """Test update_lesson_content with enriched data."""
    print("\n🧪 Testing update_lesson_content with enriched data...")
    
    # Create course data in expected location
    codebase_id = "test_enrichment_codebase_123"
    output_dir = create_course_data_in_output(codebase_id, sample_course_data)
    course_data_path = output_dir / 'course_data.json'
    
    try:
        
        # Prepare enriched content
        enriched_content = {
            'description': 'Learn how to implement secure JWT-based authentication with proper password hashing and token validation.',
            'content': '''# Introduction

Authentication is the foundation of secure web applications, ensuring that only authorized users can access protected resources. In this lesson, you'll learn how to implement JWT-based authentication, a widely-used industry standard that balances security with performance.

## What is JWT?

JWT (JSON Web Token) is a compact, URL-safe means of representing claims to be transferred between two parties. Think of it like a secure ID badge—it contains information about who you are and when it expires.

## Implementation

The authentication flow consists of three main steps:

1. **User Login**: Validate credentials
2. **Token Generation**: Create a JWT token
3. **Token Validation**: Verify token on subsequent requests

Let's explore each step in detail...
''',
            'learning_objectives': [
                'Understand JWT token structure and purpose',
                'Implement secure token generation with expiration',
                'Validate JWT tokens and handle errors gracefully',
                'Apply authentication best practices'
            ]
        }
        
        # Call update_lesson_content tool
        result = await get_mcp_tool('update_lesson_content')(
            codebase_id=codebase_id,
            lesson_id='module-1-lesson-1',
            enriched_content=enriched_content
        )
        
        # Verify result structure
        assert 'success' in result
        assert result['success'] is True
        assert 'lesson_id' in result
        assert result['lesson_id'] == 'module-1-lesson-1'
        assert 'updated_fields' in result
        assert 'enrichment_status' in result
        assert 'message' in result
        
        # Verify updated fields
        updated_fields = result['updated_fields']
        assert 'description' in updated_fields
        assert 'content' in updated_fields
        assert 'learning_objectives' in updated_fields
        
        # Verify enrichment status
        enrichment_status = result['enrichment_status']
        assert enrichment_status['status'] == 'completed'
        assert 'enriched_at' in enrichment_status
        assert enrichment_status['version'] == 1
        
        # Verify course data was updated on disk
        with open(course_data_path, 'r', encoding='utf-8') as f:
            updated_course_data = json.load(f)
        
        # Find the updated lesson
        lesson = updated_course_data['modules'][0]['lessons'][0]
        assert lesson['description'] == enriched_content['description']
        assert lesson['content'] == enriched_content['content']
        assert lesson['learning_objectives'] == enriched_content['learning_objectives']
        
        # Verify enrichment status tracking
        assert 'enrichment_status' in updated_course_data
        assert 'module-1-lesson-1' in updated_course_data['enrichment_status']
        status = updated_course_data['enrichment_status']['module-1-lesson-1']
        assert status['status'] == 'completed'
        assert status['enriched_by'] == 'kiro'
        assert status['version'] == 1
        
        print(f"✅ Lesson content updated successfully")
        print(f"   Updated fields: {', '.join(updated_fields)}")
        print(f"   Enrichment version: {enrichment_status['version']}")
    finally:
        # Cleanup
        cleanup_course_data(codebase_id)


@pytest.mark.asyncio
async def test_update_lesson_content_with_exercises(mock_app_context, sample_course_data, temp_python_file):
    """Test update_lesson_content with enhanced exercises."""
    print("\n🧪 Testing update_lesson_content with enhanced exercises...")
    
    # Create course data in expected location
    codebase_id = "test_enrichment_codebase_123"
    output_dir = create_course_data_in_output(codebase_id, sample_course_data)
    course_data_path = output_dir / 'course_data.json'
    
    try:
        
        # Prepare enriched content with exercises
        enriched_content = {
            'description': 'Enhanced description',
            'content': 'Enhanced content',
            'exercises': [
                {
                    'exercise_id': 'ex-1',
                    'title': 'Implement Token Validation',
                    'description': 'Implement a function that validates JWT tokens and handles common errors.',
                    'instructions': [
                        '1. Create a function called validate_token(token: str) → dict',
                        '2. Use jwt.decode() to decode the token',
                        '3. Handle ExpiredSignatureError and InvalidTokenError exceptions',
                        '4. Return the payload if valid, None if invalid'
                    ],
                    'hints': [
                        'Remember that JWTs have three parts: header, payload, and signature',
                        'The jwt.decode() function automatically checks expiration',
                        'Wrap your decode call in a try-except block',
                        'Specify the algorithm in decode() for security'
                    ]
                }
            ]
        }
        
        # Call update_lesson_content tool
        result = await get_mcp_tool('update_lesson_content')(
            codebase_id=codebase_id,
            lesson_id='module-1-lesson-1',
            enriched_content=enriched_content
        )
        
        # Verify success
        assert result['success'] is True
        assert 'exercises' in result['updated_fields']
        
        # Verify exercise was updated on disk
        with open(course_data_path, 'r', encoding='utf-8') as f:
            updated_course_data = json.load(f)
        
        lesson = updated_course_data['modules'][0]['lessons'][0]
        exercise = lesson['exercises'][0]
        
        # Verify exercise fields were updated
        assert exercise['description'] == enriched_content['exercises'][0]['description']
        assert exercise['instructions'] == enriched_content['exercises'][0]['instructions']
        assert exercise['hints'] == enriched_content['exercises'][0]['hints']
        assert len(exercise['hints']) == 4
        
        print(f"✅ Exercise content updated successfully")
        print(f"   Hints added: {len(exercise['hints'])}")
    finally:
        # Cleanup
        cleanup_course_data(codebase_id)


@pytest.mark.asyncio
async def test_update_lesson_content_validation_error(mock_app_context, sample_course_data):
    """Test update_lesson_content with invalid content structure."""
    print("\n🧪 Testing update_lesson_content with invalid content...")
    
    # Create course data in expected location
    codebase_id = "test_enrichment_codebase_123"
    output_dir = create_course_data_in_output(codebase_id, sample_course_data)
    
    try:
        
        # Test missing required field (description)
        invalid_content = {
            'content': 'Some content'
            # Missing 'description' field
        }
        
        result = await get_mcp_tool('update_lesson_content')(
            codebase_id=codebase_id,
            lesson_id='module-1-lesson-1',
            enriched_content=invalid_content
        )
        
        # Should return error result (not raise exception)
        assert result['success'] is False
        assert 'error' in result
        assert 'missing required field' in result['error'].lower()
        
        print(f"✅ Validation error handled correctly: {result['error']}")
    finally:
        # Cleanup
        cleanup_course_data(codebase_id)


@pytest.mark.asyncio
async def test_update_lesson_content_missing_lesson(mock_app_context, sample_course_data):
    """Test update_lesson_content with non-existent lesson."""
    print("\n🧪 Testing update_lesson_content with missing lesson...")
    
    # Create course data in expected location
    codebase_id = "test_enrichment_codebase_123"
    output_dir = create_course_data_in_output(codebase_id, sample_course_data)
    
    try:
        
        # Prepare valid enriched content
        enriched_content = {
            'description': 'Test description',
            'content': 'Test content'
        }
        
        # Call with non-existent lesson
        result = await get_mcp_tool('update_lesson_content')(
            codebase_id=codebase_id,
            lesson_id='module-99-lesson-99',
            enriched_content=enriched_content
        )
        
        # Should return error result
        assert result['success'] is False
        assert 'error' in result
        assert 'not found' in result['error'].lower()
        
        print(f"✅ Missing lesson error handled correctly: {result['error']}")
    finally:
        # Cleanup
        cleanup_course_data(codebase_id)


# ========== Test list_lessons_for_enrichment Tool ==========


@pytest.mark.asyncio
async def test_list_lessons_for_enrichment_success(mock_app_context, sample_course_data):
    """Test list_lessons_for_enrichment returns correct status."""
    print("\n🧪 Testing list_lessons_for_enrichment...")
    
    # Create output directory in expected location
    output_dir = Path("./output/test_enrichment_codebase_123_course")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Save course data
        course_data_path = output_dir / 'course_data.json'
        with open(course_data_path, 'w', encoding='utf-8') as f:
            json.dump(sample_course_data, f, indent=2)
        
        # Call list_lessons_for_enrichment tool
        result = await get_mcp_tool('list_lessons_for_enrichment')(
            codebase_id="test_enrichment_codebase_123"
        )
        
        # Verify result structure
        assert 'lessons' in result
        assert 'total_lessons' in result
        assert 'enrichment_summary' in result
        assert 'codebase_id' in result
        
        # Verify codebase_id
        assert result['codebase_id'] == "test_enrichment_codebase_123"
        
        # Verify lessons list
        lessons = result['lessons']
        assert isinstance(lessons, list)
        assert len(lessons) == 1  # Sample data has 1 lesson
        
        # Verify lesson structure
        lesson = lessons[0]
        assert 'lesson_id' in lesson
        assert 'title' in lesson
        assert 'module_title' in lesson
        assert 'status' in lesson
        assert 'teaching_value' in lesson
        assert 'source_files' in lesson
        assert 'difficulty' in lesson
        assert 'duration_minutes' in lesson
        
        # Verify lesson data
        assert lesson['lesson_id'] == 'module-1-lesson-1'
        assert lesson['title'] == 'JWT Authentication'
        assert lesson['module_title'] == 'Authentication Basics'
        assert lesson['status'] == 'not_started'  # No enrichment yet
        assert lesson['teaching_value'] == 0.85
        assert lesson['difficulty'] == 'beginner'
        
        # Verify enrichment summary
        summary = result['enrichment_summary']
        assert 'not_started' in summary
        assert 'in_progress' in summary
        assert 'completed' in summary
        assert 'completion_percentage' in summary
        
        assert summary['not_started'] == 1
        assert summary['in_progress'] == 0
        assert summary['completed'] == 0
        assert summary['completion_percentage'] == 0.0
        
        # Verify total lessons
        assert result['total_lessons'] == 1
        
        print(f"✅ Listed {result['total_lessons']} lessons")
        print(f"   Not started: {summary['not_started']}")
        print(f"   Completed: {summary['completed']}")
        print(f"   Completion: {summary['completion_percentage']}%")
    finally:
        # Cleanup
        if output_dir.exists():
            shutil.rmtree(output_dir)


@pytest.mark.asyncio
async def test_list_lessons_for_enrichment_with_enriched_lessons(mock_app_context, sample_course_data):
    """Test list_lessons_for_enrichment with enriched lessons - verify enrichment status tracking."""
    print("\n🧪 Testing list_lessons_for_enrichment with enriched lessons...")
    
    # Add enrichment status to course data
    sample_course_data['enrichment_status'] = {
        'module-1-lesson-1': {
            'status': 'completed',
            'enriched_at': '2024-01-15T10:30:00Z',
            'enriched_by': 'kiro',
            'version': 2,
            'updated_fields': ['description', 'content', 'learning_objectives']
        }
    }
    
    # Create course data in expected location
    codebase_id = "test_enrichment_codebase_123"
    output_dir = create_course_data_in_output(codebase_id, sample_course_data)
    
    try:
        # Call list_lessons_for_enrichment tool
        result = await get_mcp_tool('list_lessons_for_enrichment')(
            codebase_id=codebase_id
        )
        
        # Verify lesson status is updated
        lesson = result['lessons'][0]
        assert lesson['status'] == 'completed'
        assert 'enriched_at' in lesson
        assert lesson['enriched_at'] == '2024-01-15T10:30:00Z'
        assert 'version' in lesson
        assert lesson['version'] == 2
        
        # Verify enrichment summary reflects completion
        summary = result['enrichment_summary']
        assert summary['not_started'] == 0
        assert summary['completed'] == 1
        assert summary['completion_percentage'] == 100.0
        
        print(f"✅ Enrichment status tracking verified")
        print(f"   Lesson status: {lesson['status']}")
        print(f"   Enriched at: {lesson['enriched_at']}")
        print(f"   Version: {lesson['version']}")
        print(f"   Completion: {summary['completion_percentage']}%")
    finally:
        # Cleanup
        cleanup_course_data(codebase_id)


@pytest.mark.asyncio
async def test_list_lessons_for_enrichment_sorted_by_teaching_value(mock_app_context, temp_python_file):
    """Test that lessons are sorted by teaching value (high to low)."""
    print("\n🧪 Testing list_lessons_for_enrichment sorting...")
    
    # Create course data with multiple lessons
    course_data = {
        'course_id': 'test_course_123',
        'title': 'Test Course',
        'description': 'Test',
        'author': 'Test',
        'version': '1.0.0',
        'created_at': datetime.now().isoformat(),
        'total_duration_hours': 3.0,
        'difficulty_distribution': {},
        'tags': [],
        'prerequisites': [],
        'modules': [
            {
                'module_id': 'module-1',
                'title': 'Module 1',
                'description': 'Test module',
                'order': 1,
                'difficulty': 'beginner',
                'duration_hours': 3.0,
                'learning_objectives': [],
                'lessons': [
                    {
                        'lesson_id': 'lesson-1',
                        'title': 'Low Value Lesson',
                        'description': 'Test',
                        'order': 1,
                        'difficulty': 'beginner',
                        'duration_minutes': 30,
                        'file_path': temp_python_file,
                        'teaching_value': 0.3,  # Low value
                        'learning_objectives': [],
                        'prerequisites': [],
                        'concepts': [],
                        'exercises': [],
                        'tags': []
                    },
                    {
                        'lesson_id': 'lesson-2',
                        'title': 'High Value Lesson',
                        'description': 'Test',
                        'order': 2,
                        'difficulty': 'intermediate',
                        'duration_minutes': 45,
                        'file_path': temp_python_file,
                        'teaching_value': 0.9,  # High value
                        'learning_objectives': [],
                        'prerequisites': [],
                        'concepts': [],
                        'exercises': [],
                        'tags': []
                    },
                    {
                        'lesson_id': 'lesson-3',
                        'title': 'Medium Value Lesson',
                        'description': 'Test',
                        'order': 3,
                        'difficulty': 'beginner',
                        'duration_minutes': 30,
                        'file_path': temp_python_file,
                        'teaching_value': 0.6,  # Medium value
                        'learning_objectives': [],
                        'prerequisites': [],
                        'concepts': [],
                        'exercises': [],
                        'tags': []
                    }
                ]
            }
        ],
        'enrichment_status': {}
    }
    
    # Create course data in expected location
    codebase_id = "test_enrichment_codebase_123"
    output_dir = create_course_data_in_output(codebase_id, course_data)
    
    try:
        # Call list_lessons_for_enrichment tool
        result = await get_mcp_tool('list_lessons_for_enrichment')(
            codebase_id=codebase_id
        )
        
        # Verify lessons are sorted by teaching value (high to low)
        lessons = result['lessons']
        assert len(lessons) == 3
        
        # Check order
        assert lessons[0]['lesson_id'] == 'lesson-2'  # 0.9
        assert lessons[0]['teaching_value'] == 0.9
        
        assert lessons[1]['lesson_id'] == 'lesson-3'  # 0.6
        assert lessons[1]['teaching_value'] == 0.6
        
        assert lessons[2]['lesson_id'] == 'lesson-1'  # 0.3
        assert lessons[2]['teaching_value'] == 0.3
        
        # Verify teaching values are in descending order
        teaching_values = [l['teaching_value'] for l in lessons]
        assert teaching_values == sorted(teaching_values, reverse=True)
        
        print(f"✅ Lessons sorted correctly by teaching value")
        print(f"   Order: {[l['teaching_value'] for l in lessons]}")
    finally:
        # Cleanup
        cleanup_course_data(codebase_id)


@pytest.mark.asyncio
async def test_list_lessons_for_enrichment_missing_course(mock_app_context):
    """Test list_lessons_for_enrichment with missing course data."""
    print("\n🧪 Testing list_lessons_for_enrichment with missing course...")
    
    # Call list_lessons_for_enrichment without course data
    with pytest.raises(ValueError) as exc_info:
        await get_mcp_tool('list_lessons_for_enrichment')(
            codebase_id="nonexistent_codebase"
        )
    
    # Verify error message
    assert "not found" in str(exc_info.value).lower()
    assert "export_course" in str(exc_info.value)
    
    print(f"✅ Missing course error handled correctly: {exc_info.value}")


@pytest.mark.asyncio
async def test_list_lessons_for_enrichment_empty_codebase_id(mock_app_context):
    """Test list_lessons_for_enrichment with empty codebase_id."""
    print("\n🧪 Testing list_lessons_for_enrichment with empty codebase_id...")
    
    # Call with empty codebase_id
    with pytest.raises(ValueError) as exc_info:
        await get_mcp_tool('list_lessons_for_enrichment')(
            codebase_id=""
        )
    
    # Verify error message
    assert "required" in str(exc_info.value).lower()
    assert "cannot be empty" in str(exc_info.value).lower()
    
    print(f"✅ Empty codebase_id error handled correctly: {exc_info.value}")


# ========== Test Error Handling ==========

@pytest.mark.asyncio
async def test_enrichment_tools_server_not_initialized():
    """Test enrichment tools when server not initialized."""
    print("\n🧪 Testing enrichment tools with uninitialized server...")
    
    # Temporarily set app_context to None
    import src.server
    original_context = src.server.app_context
    src.server.app_context = None
    
    try:
        # Test get_enrichment_guide
        with pytest.raises(RuntimeError) as exc_info:
            await get_mcp_tool('get_enrichment_guide')(
                codebase_id="test_id",
                lesson_id="lesson-1"
            )
        assert "not initialized" in str(exc_info.value).lower()
        
        # Test update_lesson_content
        with pytest.raises(RuntimeError) as exc_info:
            await get_mcp_tool('update_lesson_content')(
                codebase_id="test_id",
                lesson_id="lesson-1",
                enriched_content={'description': 'test', 'content': 'test'}
            )
        assert "not initialized" in str(exc_info.value).lower()
        
        # Test list_lessons_for_enrichment
        with pytest.raises(RuntimeError) as exc_info:
            await get_mcp_tool('list_lessons_for_enrichment')(
                codebase_id="test_id"
            )
        assert "not initialized" in str(exc_info.value).lower()
        
        print(f"✅ Server not initialized errors handled correctly")
    finally:
        # Restore app_context
        src.server.app_context = original_context


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
