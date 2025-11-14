"""
Tests for Feature Mapper module.

Tests the feature mapping analyzer that connects code to user-facing features.
"""

import pytest
from pathlib import Path

from src.course.feature_mapper import FeatureMapper, create_feature_mapper
from src.course.models import Lesson
from src.models.analysis_models import (
    FileAnalysis, SymbolInfo, DetectedPattern, TeachingValueScore,
    ComplexityMetrics, FunctionInfo, ClassInfo, ImportInfo
)


@pytest.fixture
def repo_path():
    """Get repository path for testing."""
    return str(Path(__file__).parent.parent)


@pytest.fixture
def feature_mapper(repo_path):
    """Create feature mapper instance."""
    return create_feature_mapper(repo_path)


@pytest.fixture
def sample_lesson():
    """Create a sample lesson for testing."""
    return Lesson(
        lesson_id="test-lesson-1",
        title="User Authentication",
        description="Implement secure user login and session management",
        order=1,
        difficulty="intermediate",
        duration_minutes=45,
        file_path="src/auth/login.py",
        teaching_value=0.85,
        learning_objectives=["Understand authentication", "Implement secure login"],
        prerequisites=["Basic Python"],
        concepts=["Authentication", "Security", "Sessions"]
    )


@pytest.fixture
def sample_file_analysis():
    """Create a sample file analysis for testing."""
    return FileAnalysis(
        file_path="src/auth/login.py",
        language="python",
        symbol_info=SymbolInfo(
            functions=[
                FunctionInfo(
                    name="login",
                    start_line=10,
                    end_line=25,
                    parameters=["username", "password"],
                    return_type="Optional[Session]",
                    docstring="Authenticate user and create session",
                    decorators=[],
                    is_async=False,
                    complexity=5
                ),
                FunctionInfo(
                    name="verify_password",
                    start_line=27,
                    end_line=35,
                    parameters=["password", "hash"],
                    return_type="bool",
                    docstring="Verify password against hash using bcrypt",
                    decorators=[],
                    is_async=False,
                    complexity=2
                )
            ],
            classes=[],
            imports=[
                ImportInfo(
                    module="bcrypt",
                    imported_symbols=["checkpw"],
                    import_type="from",
                    line_number=1,
                    is_relative=False
                )
            ],
            exports=[]
        ),
        patterns=[
            DetectedPattern(
                pattern_type="authentication",
                file_path="src/auth/login.py",
                confidence=0.95,
                evidence=["User authentication with password verification"],
                line_numbers=[10],
                metadata={"method": "password_based"}
            ),
            DetectedPattern(
                pattern_type="validation",
                file_path="src/auth/login.py",
                confidence=0.90,
                evidence=["Password validation using bcrypt"],
                line_numbers=[27],
                metadata={"validation_type": "password"}
            )
        ],
        teaching_value=TeachingValueScore(
            total_score=0.85,
            documentation_score=0.8,
            complexity_score=0.7,
            pattern_score=0.9,
            structure_score=0.85,
            explanation="Good authentication example with security best practices"
        ),
        complexity_metrics=ComplexityMetrics(
            avg_complexity=3.5,
            max_complexity=5,
            min_complexity=2,
            high_complexity_functions=[],
            trivial_functions=[],
            avg_nesting_depth=1.5
        ),
        documentation_coverage=0.8,
        linter_issues=[],
        has_errors=False,
        errors=[],
        analyzed_at="2024-01-01T00:00:00",
        cache_hit=False
    )


def test_create_feature_mapper(repo_path):
    """Test feature mapper creation."""
    mapper = create_feature_mapper(repo_path)
    assert mapper is not None
    assert isinstance(mapper, FeatureMapper)
    assert mapper.repo_path == Path(repo_path).resolve()


def test_identify_feature_from_code(feature_mapper, sample_lesson, sample_file_analysis):
    """Test feature identification from code."""
    feature_mapping = feature_mapper.identify_feature_from_code(
        sample_lesson,
        sample_file_analysis
    )
    
    assert feature_mapping is not None
    assert feature_mapping.feature_name == "User Authentication"
    assert len(feature_mapping.user_facing_purpose) > 0
    assert len(feature_mapping.business_value) > 0
    assert len(feature_mapping.entry_points) > 0
    assert len(feature_mapping.feature_flow) > 0


def test_find_entry_points(feature_mapper, sample_file_analysis):
    """Test entry point detection."""
    entry_points = feature_mapper.find_entry_points(sample_file_analysis)
    
    assert len(entry_points) > 0
    # Should find functions as entry points
    assert any("function" in ep.lower() or "login" in ep.lower() for ep in entry_points)


def test_extract_user_flow(feature_mapper, sample_file_analysis):
    """Test user flow extraction."""
    flow = feature_mapper.extract_user_flow(sample_file_analysis)
    
    assert len(flow) > 0
    # Should have multiple steps
    assert len(flow) >= 3
    # Should mention authentication
    assert any("auth" in step.lower() for step in flow)


def test_humanize_name(feature_mapper):
    """Test name humanization."""
    assert feature_mapper._humanize_name("user_authentication") == "User Authentication"
    assert feature_mapper._humanize_name("UserAuth") == "User Auth"
    assert feature_mapper._humanize_name("api-login-handler") == "Api Login Handler"
    assert feature_mapper._humanize_name("LoginController") == "Login"


def test_extract_resource_from_path(feature_mapper):
    """Test resource extraction from API paths."""
    assert "user" in feature_mapper._extract_resource_from_path("/api/users/:id")
    assert "post" in feature_mapper._extract_resource_from_path("/api/posts")
    assert "data" in feature_mapper._extract_resource_from_path("/api")


def test_feature_mapping_with_api_endpoint():
    """Test feature mapping with API endpoint pattern."""
    mapper = create_feature_mapper(".")
    
    lesson = Lesson(
        lesson_id="api-test",
        title="User API",
        description="User management API",
        order=1,
        difficulty="beginner",
        duration_minutes=30,
        file_path="src/api/users.py",
        teaching_value=0.8,
        learning_objectives=[],
        prerequisites=[],
        concepts=[]
    )
    
    file_analysis = FileAnalysis(
        file_path="src/api/users.py",
        language="python",
        symbol_info=SymbolInfo(
            functions=[],
            classes=[],
            imports=[],
            exports=[]
        ),
        patterns=[
            DetectedPattern(
                pattern_type="api_endpoint",
                file_path="src/api/users.py",
                confidence=0.9,
                evidence=["Get all users"],
                line_numbers=[10],
                metadata={"method": "GET", "path": "/api/users"}
            ),
            DetectedPattern(
                pattern_type="api_endpoint",
                file_path="src/api/users.py",
                confidence=0.9,
                evidence=["Create new user"],
                line_numbers=[20],
                metadata={"method": "POST", "path": "/api/users"}
            )
        ],
        teaching_value=TeachingValueScore(
            total_score=0.8,
            documentation_score=0.7,
            complexity_score=0.6,
            pattern_score=0.9,
            structure_score=0.8,
            explanation="Good API example"
        ),
        complexity_metrics=ComplexityMetrics(
            avg_complexity=2.5,
            max_complexity=3,
            min_complexity=2,
            high_complexity_functions=[],
            trivial_functions=[],
            avg_nesting_depth=1.0
        ),
        documentation_coverage=0.7,
        linter_issues=[],
        has_errors=False,
        errors=[],
        analyzed_at="2024-01-01T00:00:00",
        cache_hit=False
    )
    
    feature_mapping = mapper.identify_feature_from_code(lesson, file_analysis)
    
    assert "User" in feature_mapping.feature_name
    assert len(feature_mapping.entry_points) >= 2
    assert any("GET" in ep for ep in feature_mapping.entry_points)
    assert any("POST" in ep for ep in feature_mapping.entry_points)


def test_extract_business_value_with_evidence(feature_mapper):
    """Test business value extraction with evidence."""
    from src.course.enrichment_models import FeatureMapping
    
    initial_mapping = FeatureMapping(
        feature_name="User Authentication",
        user_facing_purpose="Users can log in securely",
        business_value="Provides secure access",
        entry_points=["API: POST /login"],
        feature_flow=["User submits credentials"]
    )
    
    evidence = {
        "git_commits": [
            {
                "hash": "abc123",
                "message": "Implement user authentication to enable secure access to protected resources",
                "date": "2024-01-01"
            }
        ],
        "documentation": [
            {
                "type": "docstring",
                "content": "Purpose: Authenticate users and manage sessions securely",
                "location": "login.py"
            }
        ]
    }
    
    enhanced_value = feature_mapper.extract_business_value(initial_mapping, evidence)
    
    assert len(enhanced_value) > len(initial_mapping.business_value)
    assert "secure" in enhanced_value.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
