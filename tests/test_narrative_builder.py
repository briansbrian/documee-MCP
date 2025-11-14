"""
Tests for the Narrative Structure Builder.

Tests the narrative builder's ability to create structured learning flows
with introduction, progression, walkthrough order, conclusion, and next steps.
"""

import pytest
from src.course.narrative_builder import NarrativeBuilder, create_narrative_builder
from src.course.enrichment_models import (
    SystematicInvestigation,
    TeachingValueAssessment,
    CodeSectionGuide,
    NarrativeStructure
)


@pytest.fixture
def narrative_builder():
    """Create a narrative builder instance."""
    return create_narrative_builder()


@pytest.fixture
def sample_investigation():
    """Create sample investigation data."""
    return SystematicInvestigation(
        what_it_does="This code defines function 'authenticate_user' [auth.py:10-25]; performs validation [auth.py:15-20]",
        why_it_exists="This code exists to: add user authentication [commit abc123]; implement security measures [docs/security.md]",
        how_it_works="Implementation approach: uses asynchronous programming [auth.py:10-25]; includes error handling [auth.py:20-23]",
        when_its_used=[
            "User login flow [called by api/routes.py]",
            "Session validation [tested in tests/test_auth.py]"
        ],
        edge_cases=[
            "Handles empty password [tests/test_auth.py: test_empty_password]",
            "Handles invalid username [tests/test_auth.py: test_invalid_user]"
        ],
        common_pitfalls=[
            "Avoid: storing passwords in plain text [auth.py:15]",
            "Avoid: timing attacks in password comparison [commit def456]"
        ]
    )


@pytest.fixture
def sample_teaching_value():
    """Create sample teaching value assessment."""
    return TeachingValueAssessment(
        scores={
            'reusability': 3,
            'best_practice': 3,
            'fundamentality': 2,
            'uniqueness': 1,
            'junior_dev': 3
        },
        total_score=12,
        should_teach=True,
        reasoning="High reusability: authentication pattern is used in most applications. Best practice: demonstrates secure password handling. Valuable for junior developers learning security."
    )


@pytest.fixture
def sample_code_sections():
    """Create sample code section guides."""
    return [
        CodeSectionGuide(
            file_path="src/auth/login.py",
            line_range=(10, 25),
            code_snippet="def authenticate_user(username, password):\n    ...",
            purpose="Validates user credentials and creates session",
            key_concepts=["Authentication", "Password hashing", "Session management"],
            explanation_approach=["Start with the authentication flow", "Explain password verification", "Show session creation"],
            related_code=[{"path": "src/auth/session.py", "context": "session creation", "relationship": "calls"}],
            test_evidence=[{"test_name": "test_valid_login", "description": "should authenticate valid user", "file": "tests/test_auth.py"}],
            git_evidence=[{"commit": "abc123", "message": "Add user authentication", "date": "2024-01-15"}],
            common_mistakes=["Using == for password comparison", "Not rate limiting login attempts"]
        ),
        CodeSectionGuide(
            file_path="src/auth/session.py",
            line_range=(8, 20),
            code_snippet="def create_session(user):\n    ...",
            purpose="Creates JWT session token for authenticated user",
            key_concepts=["JWT tokens", "Token-based authentication", "Session storage"],
            explanation_approach=["Explain JWT basics", "Show token generation", "Discuss token storage"],
            related_code=[],
            test_evidence=[{"test_name": "test_session_creation", "description": "should create valid session", "file": "tests/test_session.py"}],
            git_evidence=[{"commit": "def456", "message": "Implement JWT sessions", "date": "2024-01-16"}],
            common_mistakes=["Not setting token expiration", "Storing sensitive data in JWT"]
        ),
        CodeSectionGuide(
            file_path="src/auth/validation.py",
            line_range=(5, 15),
            code_snippet="def validate_password(password):\n    ...",
            purpose="Validates password strength requirements",
            key_concepts=["Input validation", "Password requirements", "Security"],
            explanation_approach=["Define password requirements", "Show validation logic", "Handle edge cases"],
            related_code=[{"path": "src/auth/login.py", "context": "password validation", "relationship": "called by"}],
            test_evidence=[{"test_name": "test_weak_password", "description": "should reject weak passwords", "file": "tests/test_validation.py"}],
            git_evidence=[],
            common_mistakes=["Too strict requirements frustrate users"]
        )
    ]


def test_create_narrative_builder():
    """Test factory function creates builder instance."""
    builder = create_narrative_builder()
    assert isinstance(builder, NarrativeBuilder)


def test_build_introduction_points(narrative_builder, sample_investigation, sample_teaching_value):
    """Test building introduction points."""
    intro_points = narrative_builder.build_introduction_points(
        sample_investigation,
        sample_teaching_value,
        lesson_context={'prerequisites': ['Basic Python', 'HTTP concepts']}
    )
    
    assert isinstance(intro_points, list)
    assert 3 <= len(intro_points) <= 5
    assert all(isinstance(point, str) for point in intro_points)
    assert any('covers' in point.lower() for point in intro_points)


def test_build_learning_progression(narrative_builder):
    """Test building learning progression from concepts."""
    concepts = [
        "Advanced async patterns",
        "Basic function definition",
        "Error handling",
        "Complex architecture",
        "Simple variable assignment"
    ]
    
    progression = narrative_builder.build_learning_progression(concepts)
    
    assert isinstance(progression, list)
    assert len(progression) == len(concepts)
    # Check that foundational concepts come before advanced
    basic_idx = next(i for i, c in enumerate(progression) if 'basic' in c.lower() or 'simple' in c.lower())
    advanced_idx = next(i for i, c in enumerate(progression) if 'advanced' in c.lower() or 'complex' in c.lower())
    assert basic_idx < advanced_idx


def test_build_code_walkthrough_order(narrative_builder, sample_code_sections):
    """Test building code walkthrough order."""
    walkthrough_order = narrative_builder.build_code_walkthrough_order(sample_code_sections)
    
    assert isinstance(walkthrough_order, list)
    assert len(walkthrough_order) == len(sample_code_sections)
    assert all(isinstance(ref, str) for ref in walkthrough_order)
    # Check format includes file name and line range
    assert all(':' in ref and '-' in ref for ref in walkthrough_order)


def test_build_conclusion_points(narrative_builder, sample_investigation, sample_teaching_value):
    """Test building conclusion points."""
    conclusion_points = narrative_builder.build_conclusion_points(
        sample_investigation,
        sample_teaching_value
    )
    
    assert isinstance(conclusion_points, list)
    assert 3 <= len(conclusion_points) <= 5
    assert all(isinstance(point, str) for point in conclusion_points)
    # Should include pitfall warning
    assert any('avoid' in point.lower() for point in conclusion_points)


def test_suggest_next_steps(narrative_builder, sample_teaching_value):
    """Test suggesting next steps."""
    next_steps = narrative_builder.suggest_next_steps(
        lesson_context={'title': 'User Authentication', 'topic': 'security'},
        course_outline=None,
        teaching_value=sample_teaching_value
    )
    
    assert isinstance(next_steps, list)
    assert 3 <= len(next_steps) <= 5
    assert all(isinstance(step, str) for step in next_steps)
    # Should include practice suggestion
    assert any('practice' in step.lower() for step in next_steps)


def test_build_narrative_complete(narrative_builder, sample_investigation, sample_teaching_value, sample_code_sections):
    """Test building complete narrative structure."""
    narrative = narrative_builder.build_narrative(
        investigation=sample_investigation,
        teaching_value=sample_teaching_value,
        code_sections=sample_code_sections,
        lesson_context={'title': 'User Authentication', 'prerequisites': ['Python basics']},
        course_outline=None
    )
    
    assert isinstance(narrative, NarrativeStructure)
    assert len(narrative.introduction_points) >= 3
    assert len(narrative.learning_progression) >= 3
    assert len(narrative.code_walkthrough_order) == len(sample_code_sections)
    assert len(narrative.conclusion_points) >= 3
    assert len(narrative.next_steps) >= 3


def test_empty_concepts_learning_progression(narrative_builder):
    """Test learning progression with empty concepts."""
    progression = narrative_builder.build_learning_progression([])
    
    assert isinstance(progression, list)
    assert len(progression) >= 3  # Should provide default progression


def test_empty_code_sections_walkthrough(narrative_builder):
    """Test walkthrough order with empty code sections."""
    walkthrough_order = narrative_builder.build_code_walkthrough_order([])
    
    assert isinstance(walkthrough_order, list)
    assert len(walkthrough_order) == 0


def test_introduction_without_context(narrative_builder, sample_investigation, sample_teaching_value):
    """Test introduction points without lesson context."""
    intro_points = narrative_builder.build_introduction_points(
        sample_investigation,
        sample_teaching_value,
        lesson_context=None
    )
    
    assert isinstance(intro_points, list)
    assert len(intro_points) >= 3


def test_next_steps_without_outline(narrative_builder, sample_teaching_value):
    """Test next steps without course outline."""
    next_steps = narrative_builder.suggest_next_steps(
        lesson_context=None,
        course_outline=None,
        teaching_value=sample_teaching_value
    )
    
    assert isinstance(next_steps, list)
    assert len(next_steps) >= 3


def test_concept_complexity_assessment(narrative_builder):
    """Test concept complexity assessment."""
    # Foundational concepts
    assert narrative_builder._assess_concept_complexity("Basic function definition") == 'foundational'
    assert narrative_builder._assess_concept_complexity("Simple variable syntax") == 'foundational'
    
    # Advanced concepts
    assert narrative_builder._assess_concept_complexity("Advanced async patterns") == 'advanced'
    assert narrative_builder._assess_concept_complexity("Complex architecture design") == 'advanced'
    
    # Intermediate concepts
    assert narrative_builder._assess_concept_complexity("Error handling") == 'intermediate'


def test_walkthrough_priority_calculation(narrative_builder, sample_code_sections):
    """Test walkthrough priority calculation."""
    # Entry point should have high priority
    entry_section = sample_code_sections[0]
    entry_section.purpose = "Main entry point for authentication"
    priority = narrative_builder._calculate_walkthrough_priority(entry_section)
    assert priority > 50
    
    # Edge case should have lower priority
    edge_section = sample_code_sections[1]
    edge_section.purpose = "Handles edge case for invalid tokens"
    priority = narrative_builder._calculate_walkthrough_priority(edge_section)
    assert priority < 50


def test_serialization(narrative_builder, sample_investigation, sample_teaching_value, sample_code_sections):
    """Test that narrative structure can be serialized."""
    narrative = narrative_builder.build_narrative(
        investigation=sample_investigation,
        teaching_value=sample_teaching_value,
        code_sections=sample_code_sections
    )
    
    # Test to_dict
    narrative_dict = narrative.to_dict()
    assert isinstance(narrative_dict, dict)
    assert 'introduction_points' in narrative_dict
    assert 'learning_progression' in narrative_dict
    assert 'code_walkthrough_order' in narrative_dict
    assert 'conclusion_points' in narrative_dict
    assert 'next_steps' in narrative_dict
    
    # Test from_dict
    restored_narrative = NarrativeStructure.from_dict(narrative_dict)
    assert restored_narrative.introduction_points == narrative.introduction_points
    assert restored_narrative.learning_progression == narrative.learning_progression
