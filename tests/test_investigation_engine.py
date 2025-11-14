"""
Tests for the systematic investigation engine.
"""

import pytest
from src.course.investigation_engine import InvestigationEngine, create_investigation_engine
from src.course.enrichment_models import (
    EvidenceBundle,
    FeatureMapping,
    ValidationChecklist,
    SystematicInvestigation
)


@pytest.fixture
def investigation_engine():
    """Create investigation engine instance."""
    return create_investigation_engine()


@pytest.fixture
def sample_evidence():
    """Create sample evidence bundle."""
    return EvidenceBundle(
        source_files=[
            {
                'path': 'src/example.py',
                'code': 'def calculate_total(items):\n    return sum(items)',
                'lines': 2,
                'language': 'python',
                'sections': [
                    {
                        'start_line': 1,
                        'end_line': 2,
                        'description': 'Calculate total',
                        'code': 'def calculate_total(items):\n    return sum(items)'
                    }
                ]
            }
        ],
        test_files=[
            {
                'path': 'tests/test_example.py',
                'test_cases': [
                    {
                        'name': 'test_calculate_total',
                        'description': 'should calculate sum of items',
                        'type': 'function'
                    },
                    {
                        'name': 'test_empty_list',
                        'description': 'should handle empty list',
                        'type': 'function'
                    }
                ],
                'framework': 'pytest',
                'coverage': ['Should calculate sum of items', 'Should handle empty list'],
                'total_tests': 2
            }
        ],
        git_commits=[
            {
                'hash': 'abc123def456',
                'author': 'Developer',
                'email': 'dev@example.com',
                'date': '2024-01-15T10:00:00Z',
                'subject': 'Add calculate_total function',
                'message': 'Add calculate_total function\n\nImplements sum calculation for items.',
                'files': ['src/example.py']
            }
        ],
        documentation=[
            {
                'type': 'docstring',
                'content': 'Calculate the total sum of items in a list.',
                'location': 'Function: calculate_total (lines 1-2)',
                'context': "Documents function 'calculate_total'"
            }
        ],
        dependencies=[
            {
                'name': 'typing',
                'symbols': ['List'],
                'reason': 'Type hints',
                'evidence': 'Line 1: import',
                'type': 'standard_library'
            }
        ],
        dependents=[
            {
                'name': 'src/main.py',
                'usage': 'Calculates order totals',
                'evidence': 'Line 45: from example import calculate_total'
            }
        ]
    )


@pytest.fixture
def sample_feature():
    """Create sample feature mapping."""
    return FeatureMapping(
        feature_name='Order Total Calculation',
        user_facing_purpose='Calculate total price of items in cart',
        business_value='Enables accurate pricing for customer orders',
        entry_points=['checkout page', 'cart summary'],
        feature_flow=['User adds items', 'System calculates total', 'Display to user']
    )


@pytest.fixture
def sample_validation():
    """Create sample validation checklist."""
    return ValidationChecklist(
        code_behavior='Sums numeric values in a list',
        expected_behavior='Should calculate sum correctly',
        documentation_alignment='Documentation matches implementation',
        git_context='Added for order processing',
        consistency_check=True
    )


def test_create_investigation_engine():
    """Test factory function creates engine."""
    engine = create_investigation_engine()
    assert isinstance(engine, InvestigationEngine)


def test_investigate_what_it_does(investigation_engine, sample_evidence):
    """Test investigation of what code does."""
    result = investigation_engine.investigate_what_it_does(sample_evidence)
    
    assert isinstance(result, str)
    assert len(result) > 0
    # Should contain citations
    assert '[' in result and ']' in result


def test_investigate_why_it_exists(investigation_engine, sample_evidence):
    """Test investigation of why code exists."""
    result = investigation_engine.investigate_why_it_exists(sample_evidence)
    
    assert isinstance(result, str)
    assert len(result) > 0
    # Should mention commits or documentation
    assert 'commit' in result.lower() or 'function' in result.lower()


def test_investigate_how_it_works(investigation_engine, sample_evidence):
    """Test investigation of how code works."""
    result = investigation_engine.investigate_how_it_works(sample_evidence)
    
    assert isinstance(result, str)
    assert len(result) > 0


def test_investigate_when_used(investigation_engine, sample_evidence):
    """Test investigation of when code is used."""
    result = investigation_engine.investigate_when_used(sample_evidence)
    
    assert isinstance(result, list)
    assert len(result) > 0
    # Should have usage scenarios
    assert all(isinstance(item, str) for item in result)


def test_investigate_edge_cases(investigation_engine, sample_evidence):
    """Test investigation of edge cases."""
    result = investigation_engine.investigate_edge_cases(sample_evidence)
    
    assert isinstance(result, list)
    assert len(result) > 0
    # Should identify empty list edge case
    assert any('empty' in case.lower() for case in result)


def test_investigate_pitfalls(investigation_engine, sample_evidence):
    """Test investigation of common pitfalls."""
    result = investigation_engine.investigate_pitfalls(sample_evidence)
    
    assert isinstance(result, list)
    assert len(result) > 0


def test_full_investigation(
    investigation_engine,
    sample_feature,
    sample_evidence,
    sample_validation
):
    """Test complete systematic investigation."""
    result = investigation_engine.investigate(
        sample_feature,
        sample_evidence,
        sample_validation
    )
    
    assert isinstance(result, SystematicInvestigation)
    assert isinstance(result.what_it_does, str)
    assert isinstance(result.why_it_exists, str)
    assert isinstance(result.how_it_works, str)
    assert isinstance(result.when_its_used, list)
    assert isinstance(result.edge_cases, list)
    assert isinstance(result.common_pitfalls, list)
    
    # All fields should have content
    assert len(result.what_it_does) > 0
    assert len(result.why_it_exists) > 0
    assert len(result.how_it_works) > 0
    assert len(result.when_its_used) > 0
    assert len(result.edge_cases) > 0
    assert len(result.common_pitfalls) > 0


def test_investigate_with_minimal_evidence(investigation_engine):
    """Test investigation with minimal evidence."""
    minimal_evidence = EvidenceBundle(
        source_files=[],
        test_files=[],
        git_commits=[],
        documentation=[],
        dependencies=[],
        dependents=[]
    )
    
    feature = FeatureMapping(
        feature_name='Test Feature',
        user_facing_purpose='Test purpose',
        business_value='Test value',
        entry_points=[],
        feature_flow=[]
    )
    
    validation = ValidationChecklist(
        code_behavior='Test behavior',
        expected_behavior='Test expected',
        documentation_alignment='Test alignment',
        git_context='Test context',
        consistency_check=True
    )
    
    result = investigation_engine.investigate(feature, minimal_evidence, validation)
    
    # Should still return valid investigation even with minimal evidence
    assert isinstance(result, SystematicInvestigation)
    assert len(result.what_it_does) > 0
    assert len(result.why_it_exists) > 0


def test_code_functionality_analysis(investigation_engine):
    """Test code functionality analysis helper."""
    # Python function
    python_code = "def process_data(items):\n    return [x * 2 for x in items]"
    result = investigation_engine._analyze_code_functionality(python_code, 'python')
    assert result is not None
    assert 'function' in result.lower()
    
    # Python class
    class_code = "class DataProcessor:\n    def __init__(self):\n        pass"
    result = investigation_engine._analyze_code_functionality(class_code, 'python')
    assert result is not None
    assert 'class' in result.lower()


def test_purpose_extraction_from_commit(investigation_engine):
    """Test purpose extraction from commit messages."""
    # Add pattern
    result = investigation_engine._extract_purpose_from_commit("Add user authentication")
    assert result is not None
    assert 'add' in result.lower()
    
    # Fix pattern
    result = investigation_engine._extract_purpose_from_commit("Fix validation bug")
    assert result is not None
    assert 'fix' in result.lower()
    
    # Empty message
    result = investigation_engine._extract_purpose_from_commit("")
    assert result is None


def test_edge_case_detection(investigation_engine):
    """Test edge case detection from test descriptions."""
    assert investigation_engine._is_edge_case_test("should handle empty list")
    assert investigation_engine._is_edge_case_test("should handle null value")
    assert investigation_engine._is_edge_case_test("should handle boundary condition")
    assert not investigation_engine._is_edge_case_test("should calculate sum")


def test_pitfall_detection(investigation_engine):
    """Test pitfall detection from test descriptions."""
    assert investigation_engine._is_pitfall_test("should throw error on invalid input")
    assert investigation_engine._is_pitfall_test("should reject bad data")
    assert investigation_engine._is_pitfall_test("should handle failure gracefully")
    assert not investigation_engine._is_pitfall_test("should calculate correctly")


def test_bug_fix_commit_detection(investigation_engine):
    """Test bug fix commit detection."""
    assert investigation_engine._is_bug_fix_commit("fix: resolve memory leak")
    assert investigation_engine._is_bug_fix_commit("bug: correct calculation error")
    assert investigation_engine._is_bug_fix_commit("patch: fix crash on startup")
    assert not investigation_engine._is_bug_fix_commit("add: new feature")
